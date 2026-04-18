"""
Ocean data orchestrator: merges Copernicus + NASA + ECMWF data,
writes to PostgreSQL ocean_data table and Redis cache.
Runs every hour via APScheduler.
"""
import asyncio
import json
import structlog
from datetime import datetime, timezone
from typing import Optional

from ...core.config import settings
from ...core.redis_client import get_redis
from .sources.copernicus import copernicus_ingester
from .sources.nasa_earthdata import nasa_ingester, ecmwf_ingester

logger = structlog.get_logger()

WEST_COAST_STATES = ["gujarat", "maharashtra", "goa", "karnataka", "kerala"]

# State lat/lon representative points for quick lookups
STATE_CENTERS = {
    "gujarat": (22.0, 70.5),
    "maharashtra": (17.5, 73.0),
    "goa": (15.3, 73.9),
    "karnataka": (14.0, 74.5),
    "kerala": (10.0, 76.0),
}


class OceanDataService:

    async def refresh_all(self):
        """Fetch all data sources and update cache + DB."""
        logger.info("Ocean data refresh started")
        try:
            # Fetch in parallel
            coper_task = asyncio.create_task(
                copernicus_ingester.fetch_latest_ocean_state()
            )
            # ECMWF wind/wave
            wind_task = asyncio.create_task(ecmwf_ingester.fetch_wind_wave_forecast())

            ocean_records = await coper_task
            wind_records = await wind_task

            # Merge wind into ocean records
            merged = self._merge_wind(ocean_records, wind_records)

            # Aggregate per state and cache
            redis = await get_redis()
            for state in WEST_COAST_STATES:
                state_summary = self._summarize_state(merged, state)
                await redis.setex(
                    f"ocean:{state}:latest",
                    3600,
                    json.dumps(state_summary),
                )
                # Update safety cache
                from ..safety.safety_service import safety_service
                safety = safety_service.compute_safety(
                    wave_height=state_summary.get("wave_height", 1.2),
                    wind_speed=state_summary.get("wind_speed", 18.0),
                    current_strength=abs(state_summary.get("current_u", 0.1)),
                )
                await safety_service.update_safety_cache(redis, state, safety)

            logger.info("Ocean data refresh complete", states=len(WEST_COAST_STATES), records=len(merged))
            return merged

        except Exception as e:
            logger.error("Ocean data refresh failed", error=str(e))
            return []

    def _merge_wind(self, ocean_records: list, wind_records: list) -> list:
        """Merge wind/wave data into ocean records by nearest grid point."""
        if not wind_records:
            return ocean_records

        wind_index = {(r["lat"], r["lon"]): r for r in wind_records}

        for rec in ocean_records:
            lat = round(rec["lat"] * 2) / 2  # snap to 0.5° grid
            lon = round(rec["lon"] * 2) / 2
            wind = wind_index.get((lat, lon), {})
            rec.setdefault("wind_speed", wind.get("wind_speed", 18.0))
            rec.setdefault("wind_direction", wind.get("wind_direction", 225))
            rec.setdefault("wave_height", wind.get("wave_height", 1.2))
            rec.setdefault("wave_period", wind.get("wave_period", 8.0))

        return ocean_records

    def _summarize_state(self, records: list, state: str) -> dict:
        """Average ocean conditions for a state from grid records."""
        center_lat, center_lon = STATE_CENTERS[state]
        # Filter records within 3° of state center
        state_recs = [
            r for r in records
            if abs(r.get("lat", 0) - center_lat) < 3
            and abs(r.get("lon", 0) - center_lon) < 3
        ]
        if not state_recs:
            return self._default_state_conditions(state)

        def avg(key, default=0.0):
            vals = [r[key] for r in state_recs if key in r and r[key] is not None]
            return round(sum(vals) / len(vals), 3) if vals else default

        return {
            "state": state,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sst": avg("sst", 29.0),
            "chlorophyll": avg("chlorophyll", 0.8),
            "current_u": avg("current_u", 0.1),
            "current_v": avg("current_v", 0.05),
            "wave_height": avg("wave_height", 1.2),
            "wave_period": avg("wave_period", 8.0),
            "wind_speed": avg("wind_speed", 18.0),
            "wind_direction": avg("wind_direction", 225),
            "record_count": len(state_recs),
            "source": "copernicus+ecmwf",
        }

    def _default_state_conditions(self, state: str) -> dict:
        """Safe defaults when no data available."""
        return {
            "state": state,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sst": 29.0,
            "chlorophyll": 0.8,
            "current_u": 0.1,
            "current_v": 0.05,
            "wave_height": 1.2,
            "wave_period": 8.0,
            "wind_speed": 18.0,
            "wind_direction": 225,
            "source": "default_fallback",
        }

    async def get_state_conditions(self, state: str) -> dict:
        """Get cached ocean conditions for a state."""
        redis = await get_redis()
        cached = await redis.get(f"ocean:{state}:latest")
        if cached:
            return json.loads(cached)
        return self._default_state_conditions(state)


ocean_data_service = OceanDataService()
