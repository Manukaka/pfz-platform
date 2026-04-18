"""
PFZ Inference Service.
Loads ONNX model and performs batch inference on 5km x 5km grid cells.
Runs every 15 minutes, publishes results to Kafka.
"""
import asyncio
import json
import numpy as np
import structlog
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional
import uuid

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False

from aiokafka import AIOKafkaProducer

logger = structlog.get_logger()

# West coast bounding box (rough)
WEST_COAST_BBOX = {
    "gujarat": {"lat_min": 20.0, "lat_max": 24.5, "lon_min": 68.0, "lon_max": 73.5},
    "maharashtra": {"lat_min": 15.6, "lat_max": 20.4, "lon_min": 72.0, "lon_max": 73.5},
    "goa": {"lat_min": 14.8, "lat_max": 15.8, "lon_min": 73.6, "lon_max": 74.3},
    "karnataka": {"lat_min": 12.4, "lat_max": 15.0, "lon_min": 74.0, "lon_max": 75.0},
    "kerala": {"lat_min": 8.0, "lat_max": 12.8, "lon_min": 74.8, "lon_max": 77.5},
}

GRID_SIZE_DEG = 0.05  # ~5km at equator


class PfzInferenceEngine:
    """
    ONNX-based PFZ prediction engine.
    Input: Ocean features (SST, chlorophyll, currents, wind, bathymetry, time encoding)
    Output: PFZ probability per grid cell
    """

    def __init__(self, model_path: str = "models/pfz_model.onnx"):
        self.model_path = model_path
        self.session: Optional[ort.InferenceSession] = None
        self._load_model()

    def _load_model(self):
        if not ONNX_AVAILABLE:
            logger.warning("ONNX Runtime not available, using mock inference")
            return
        if not Path(self.model_path).exists():
            logger.warning("Model not found, using mock inference", path=self.model_path)
            return
        opts = ort.SessionOptions()
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        self.session = ort.InferenceSession(
            self.model_path,
            sess_options=opts,
            providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
        )
        logger.info("ONNX PFZ model loaded", path=self.model_path)

    def predict_batch(self, features: np.ndarray) -> np.ndarray:
        """Predict PFZ probability for a batch of grid cells."""
        if self.session is None:
            return self._mock_predict(features)

        input_name = self.session.get_inputs()[0].name
        outputs = self.session.run(None, {input_name: features.astype(np.float32)})
        return outputs[0][:, 1]  # Probability of PFZ=True

    def _mock_predict(self, features: np.ndarray) -> np.ndarray:
        """Mock predictions for development without real model."""
        np.random.seed(int(datetime.now(timezone.utc).timestamp()) % 1000)
        n = features.shape[0]
        # Simulate ~15% of cells as PFZ
        probs = np.random.beta(0.5, 3.0, n)
        return probs

    def build_features(
        self,
        lats: np.ndarray,
        lons: np.ndarray,
        ocean_data: dict,
    ) -> np.ndarray:
        """
        Build feature matrix for grid cells.
        Features: [lat, lon, sst, chlorophyll, current_u, current_v, wind_speed,
                   wave_height, bathymetry, day_of_year_sin, day_of_year_cos,
                   hour_sin, hour_cos, state_encoded]
        """
        n = len(lats)
        now = datetime.now(timezone.utc)
        doy = now.timetuple().tm_yday
        hour = now.hour

        features = np.zeros((n, 14), dtype=np.float32)
        features[:, 0] = lats
        features[:, 1] = lons
        features[:, 2] = ocean_data.get("sst", 28.0)
        features[:, 3] = ocean_data.get("chlorophyll", 0.8)
        features[:, 4] = ocean_data.get("current_u", 0.2)
        features[:, 5] = ocean_data.get("current_v", 0.1)
        features[:, 6] = ocean_data.get("wind_speed", 15.0)
        features[:, 7] = ocean_data.get("wave_height", 1.2)
        features[:, 8] = ocean_data.get("bathymetry", -100.0)
        features[:, 9] = np.sin(2 * np.pi * doy / 365)
        features[:, 10] = np.cos(2 * np.pi * doy / 365)
        features[:, 11] = np.sin(2 * np.pi * hour / 24)
        features[:, 12] = np.cos(2 * np.pi * hour / 24)
        features[:, 13] = 0  # state encoding (set per state)
        return features

    def generate_grid(self, state: str) -> tuple[np.ndarray, np.ndarray]:
        """Generate lat/lon grid for a state."""
        bbox = WEST_COAST_BBOX.get(state, WEST_COAST_BBOX["maharashtra"])
        lats = np.arange(bbox["lat_min"], bbox["lat_max"], GRID_SIZE_DEG)
        lons = np.arange(bbox["lon_min"], bbox["lon_max"], GRID_SIZE_DEG)
        grid_lats, grid_lons = np.meshgrid(lats, lons)
        return grid_lats.flatten(), grid_lons.flatten()

    def probabilities_to_zones(
        self,
        lats: np.ndarray,
        lons: np.ndarray,
        probs: np.ndarray,
        state: str,
        threshold: float = 0.65,
        ocean_data: dict = None,
    ) -> list[dict]:
        """Convert probability grid to PFZ zone polygons."""
        high_prob_mask = probs >= threshold
        if not np.any(high_prob_mask):
            return []

        zones = []
        high_lats = lats[high_prob_mask]
        high_lons = lons[high_prob_mask]
        high_probs = probs[high_prob_mask]

        # Group nearby cells (simple clustering)
        for lat, lon, prob in zip(high_lats, high_lons, high_probs):
            half = GRID_SIZE_DEG / 2
            polygon = [
                [lon - half, lat - half],
                [lon + half, lat - half],
                [lon + half, lat + half],
                [lon - half, lat + half],
                [lon - half, lat - half],
            ]
            now = datetime.now(timezone.utc)
            zone = {
                "zone_id": f"wc_{state}_{now.strftime('%Y%m%d%H%M')}_{lat:.2f}_{lon:.2f}",
                "state": state,
                "confidence": float(prob),
                "source": "ml_model_v3.0",
                "polygon": polygon,
                "center": [float(lon), float(lat)],
                "top_species": self._get_top_species(state, prob),
                "species_probability": self._get_species_probs(state),
                "environmental_factors": ocean_data or {},
                "valid_from": now.isoformat(),
                "valid_until": (now + timedelta(hours=3)).isoformat(),
                "safety_status": "green",
            }
            zones.append(zone)

        return zones[:500]  # Cap at 500 zones per state per run

    def _get_top_species(self, state: str, confidence: float) -> str:
        species_map = {
            "gujarat": "Bombay Duck",
            "maharashtra": "Bangda",
            "goa": "Kingfish",
            "karnataka": "Mackerel",
            "kerala": "Sardine",
        }
        return species_map.get(state, "Mackerel")

    def _get_species_probs(self, state: str) -> dict:
        probs_map = {
            "gujarat": {"bombay_duck": 0.45, "ribbon_fish": 0.25, "pomfret": 0.18},
            "maharashtra": {"bangda": 0.42, "surmai": 0.28, "pomfret": 0.15},
            "goa": {"kingfish": 0.35, "mackerel": 0.30, "sardine": 0.20},
            "karnataka": {"mackerel": 0.40, "sardine": 0.30, "anchovy": 0.20},
            "kerala": {"sardine": 0.45, "mackerel": 0.30, "tuna": 0.15},
        }
        return probs_map.get(state, {"mackerel": 0.40})


class PfzScheduler:
    """Runs inference every 15 minutes and publishes to Kafka."""

    def __init__(self):
        self.engine = PfzInferenceEngine()
        self.producer: Optional[AIOKafkaProducer] = None

    async def start(self, kafka_servers: str):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=kafka_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await self.producer.start()
        logger.info("PFZ Scheduler started")

    async def run_inference_all_states(self, ocean_data: dict = None):
        """Run inference for all west coast states."""
        states = list(WEST_COAST_BBOX.keys())
        all_zones = []

        for state in states:
            try:
                zones = await self.run_inference_state(state, ocean_data or {})
                all_zones.extend(zones)
                logger.info("Inference complete", state=state, zones=len(zones))
            except Exception as e:
                logger.error("Inference failed", state=state, error=str(e))

        # Publish to Kafka
        if self.producer:
            await self.producer.send(
                "pfz-zones",
                {"zones": all_zones, "timestamp": datetime.now(timezone.utc).isoformat()},
            )

        return all_zones

    async def run_inference_state(self, state: str, ocean_data: dict) -> list:
        lats, lons = self.engine.generate_grid(state)
        features = self.engine.build_features(lats, lons, ocean_data)
        probs = self.engine.predict_batch(features)
        return self.engine.probabilities_to_zones(lats, lons, probs, state, ocean_data=ocean_data)

    async def run_loop(self, interval_minutes: int = 15):
        """Main inference loop."""
        while True:
            try:
                logger.info("Starting PFZ inference cycle")
                await self.run_inference_all_states()
                logger.info("PFZ inference cycle complete")
            except Exception as e:
                logger.error("Inference cycle failed", error=str(e))
            await asyncio.sleep(interval_minutes * 60)


if __name__ == "__main__":
    import asyncio
    from app.core.config import settings

    async def main():
        scheduler = PfzScheduler()
        await scheduler.start(settings.kafka_bootstrap_servers)
        await scheduler.run_loop()

    asyncio.run(main())
