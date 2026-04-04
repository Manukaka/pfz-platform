"""
SAMUDRA AI — Data Aggregator
डेटा एकत्रीकरण - एक जगह से सब कुछ

Unified interface for fetching and aggregating data from all sources
Coordinates between CMEMS, NASA, ECMWF, and GEBCO clients
Provides clean API for PFZ algorithm processing

Purpose:
- Single interface for all data collection
- Automatic coordination between multiple data sources
- Consistency checks and data quality assurance
- Easy integration with PFZ algorithm
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json
import os
import logging
import numpy as np

from .cmems_client import CMEMSClient
from .nasa_client import NASAClient
from .ecmwf_client import ECMWFClient
from .gebco_client import GEBCOClient
from .earthkit_client import fetch_sst_grid_ecmwf, fetch_wind_grid_ecmwf
from app.core.pinn_model import pinn_engine

logger = logging.getLogger(__name__)


class DataAggregator:
    """
    Unified data aggregator for PFZ algorithm inputs

    Fetches all required oceanographic and meteorological data
    for a given geographic region and date
    """

    # Default Maharashtra EEZ bounds
    DEFAULT_LAT_MIN = 14.0
    DEFAULT_LAT_MAX = 21.0
    DEFAULT_LNG_MIN = 67.0
    DEFAULT_LNG_MAX = 74.5

    # Data source preferences (order of preference)
    SST_SOURCES = ["CMEMS", "NASA", "ECMWF"]
    CURRENT_SOURCES = ["CMEMS", "NASA"]
    WIND_SOURCES = ["ECMWF", "CMEMS"]
    CHLOROPHYLL_SOURCES = ["CMEMS", "NASA"]

    def __init__(self, cmems_credentials: Optional[Tuple[str, str]] = None,
                 nasa_api_key: Optional[str] = None,
                 ecmwf_credentials: Optional[Tuple[str, str]] = None):
        """
        Initialize DataAggregator with optional credentials

        Credentials can be provided as arguments OR loaded from environment variables:
        - CMEMS_USERNAME, CMEMS_PASSWORD
        - NASA_API_KEY
        - ECMWF_API_KEY (format: uid:key)
        - ECMWF_URL

        Args:
            cmems_credentials: (username, password) tuple for CMEMS
            nasa_api_key: API key for NASA
            ecmwf_credentials: (url, key) tuple for ECMWF CDS
        """
        # Load from environment if not provided as arguments
        if not cmems_credentials:
            cmems_user = os.environ.get('CMEMS_USERNAME')
            cmems_pass = os.environ.get('CMEMS_PASSWORD')
            if cmems_user and cmems_pass:
                cmems_credentials = (cmems_user, cmems_pass)

        if not nasa_api_key:
            nasa_api_key = os.environ.get('NASA_API_KEY')

        if not ecmwf_credentials:
            ecmwf_key = os.environ.get('ECMWF_API_KEY')
            ecmwf_url = os.environ.get('ECMWF_URL', 'https://cds.climate.copernicus.eu/api/v2')
            if ecmwf_key:
                ecmwf_credentials = (ecmwf_url, ecmwf_key)

        # Initialize clients with credentials
        if cmems_credentials:
            try:
                CMEMSClient(*cmems_credentials)
                logger.info("[OK] CMEMS client initialized")
            except Exception as e:
                logger.warning(f"[WARN] CMEMS initialization failed: {e}")

        if nasa_api_key:
            try:
                NASAClient(nasa_api_key)
                logger.info("[OK] NASA client initialized")
            except Exception as e:
                logger.warning(f"[WARN] NASA initialization failed: {e}")

        if ecmwf_credentials:
            try:
                ECMWFClient(*ecmwf_credentials)
                logger.info("[OK] ECMWF client initialized")
            except Exception as e:
                logger.warning(f"[WARN] ECMWF initialization failed: {e}")

        logger.info("[OCEAN] DataAggregator initialized")

    @staticmethod
    def fetch_pfz_data(lat_min: float = DEFAULT_LAT_MIN,
                      lat_max: float = DEFAULT_LAT_MAX,
                      lng_min: float = DEFAULT_LNG_MIN,
                      lng_max: float = DEFAULT_LNG_MAX,
                      date: datetime = None) -> Dict:
        """
        Fetch all data required for PFZ algorithm

        This is the main method called by the PFZ processor.
        Returns complete oceanographic dataset for the given region and date.

        Args:
            lat_min, lat_max, lng_min, lng_max: Geographic bounds
            date: Date for data (defaults to today UTC)

        Returns:
            Dict containing:
            {
                "date": "YYYY-MM-DD",
                "region": {"lat_min": float, "lat_max": float, "lng_min": float, "lng_max": float},
                "sst": {"grid": 2D array, "lat": list, "lng": list, "source": str},
                "u_current": {...},  # Eastward current
                "v_current": {...},  # Northward current
                "u10_wind": {...},   # 10m eastward wind
                "v10_wind": {...},   # 10m northward wind
                "chlorophyll": {...},
                "ssh_anomaly": {...},
                "wind_stress_x": {...},
                "wind_stress_y": {...},
                "bathymetry": {...},
                "metadata": {
                    "sources": {...},
                    "timestamps": {...},
                    "data_quality": {...},
                }
            }
        """
        if date is None:
            date = datetime.utcnow()

        # Start building the complete dataset
        complete_data = {
            "date": date.strftime("%Y-%m-%d"),
            "region": {
                "lat_min": lat_min,
                "lat_max": lat_max,
                "lng_min": lng_min,
                "lng_max": lng_max,
            },
            "metadata": {
                "fetch_time": datetime.utcnow().isoformat(),
                "sources": {},
                "status": {},
            }
        }

        # Fetch oceanographic data — try earthkit (real ECMWF) first, then CMEMS
        try:
            sst_data = fetch_sst_grid_ecmwf(lat_min, lat_max, lng_min, lng_max)
            if sst_data:
                normalized_sst = {
                    "grid": sst_data.get("sst_grid"),
                    "lat": sst_data.get("lat"),
                    "lng": sst_data.get("lng"),
                    "source": sst_data.get("source", "ECMWF-IFS"),
                }
                complete_data["sst"] = normalized_sst
                complete_data["metadata"]["sources"]["sst"] = sst_data.get("source", "ECMWF-IFS")
            else:
                raise Exception("earthkit SST unavailable, falling back to CMEMS")
        except Exception as e:
            logger.info(f"Earthkit SST: {e}")
            try:
                sst_data = CMEMSClient.fetch_sst(lat_min, lat_max, lng_min, lng_max, date)
                normalized_sst = {
                    "grid": sst_data.get("sst_grid") or sst_data.get("grid"),
                    "lat": sst_data.get("lat"),
                    "lng": sst_data.get("lng"),
                    "source": sst_data.get("source", "CMEMS"),
                }
                complete_data["sst"] = normalized_sst
                complete_data["metadata"]["sources"]["sst"] = sst_data.get("source", "CMEMS")
            except Exception as e2:
                complete_data["metadata"]["status"]["sst_error"] = str(e2)

        try:
            currents = CMEMSClient.fetch_currents(lat_min, lat_max, lng_min, lng_max, date)
            if currents:
                complete_data["u_current"] = {
                    "grid": currents["u"],
                    "lat": currents["lat"],
                    "lng": currents["lng"],
                    "source": currents.get("source", "CMEMS"),
                }
                complete_data["v_current"] = {
                    "grid": currents["v"],
                    "lat": currents["lat"],
                    "lng": currents["lng"],
                    "source": currents.get("source", "CMEMS"),
                }
                complete_data["metadata"]["sources"]["currents"] = currents.get("source", "CMEMS")
        except Exception as e:
            complete_data["metadata"]["status"]["currents_error"] = str(e)

        try:
            chlorophyll = CMEMSClient.fetch_chlorophyll(lat_min, lat_max, lng_min, lng_max, date)
            normalized_chl = {
                "grid": chlorophyll.get("chl_grid") or chlorophyll.get("grid"),
                "lat": chlorophyll.get("lat"),
                "lng": chlorophyll.get("lng"),
                "source": chlorophyll.get("source", "CMEMS"),
            }
            complete_data["chlorophyll"] = normalized_chl
            complete_data["metadata"]["sources"]["chlorophyll"] = chlorophyll.get("source", "CMEMS")
        except Exception as e:
            complete_data["metadata"]["status"]["chlorophyll_error"] = str(e)

        try:
            ssh = CMEMSClient.fetch_ssh_anomaly(lat_min, lat_max, lng_min, lng_max, date)
            normalized_ssh = {
                "grid": ssh.get("ssh_grid") or ssh.get("grid"),
                "lat": ssh.get("lat"),
                "lng": ssh.get("lng"),
                "source": ssh.get("source", "CMEMS"),
            }
            complete_data["ssh_anomaly"] = normalized_ssh
            complete_data["metadata"]["sources"]["ssh_anomaly"] = ssh.get("source", "CMEMS")
        except Exception as e:
            complete_data["metadata"]["status"]["ssh_anomaly_error"] = str(e)

        # Fetch meteorological data — try earthkit (real ECMWF) first, then mock
        try:
            wind = fetch_wind_grid_ecmwf(lat_min, lat_max, lng_min, lng_max)
            if wind:
                complete_data["u10_wind"] = {
                    "grid": wind["u10"],
                    "lat": wind["lat"],
                    "lng": wind["lng"],
                    "source": wind.get("source", "ECMWF-IFS"),
                }
                complete_data["v10_wind"] = {
                    "grid": wind["v10"],
                    "lat": wind["lat"],
                    "lng": wind["lng"],
                    "source": wind.get("source", "ECMWF-IFS"),
                }
                complete_data["metadata"]["sources"]["wind"] = wind.get("source", "ECMWF-IFS")
            else:
                raise Exception("earthkit wind unavailable, falling back to old ECMWF client")
        except Exception as e:
            logger.info(f"Earthkit wind: {e}")
            try:
                wind = ECMWFClient.fetch_wind_10m(lat_min, lat_max, lng_min, lng_max, date)
                complete_data["u10_wind"] = {
                    "grid": wind["u10"],
                    "lat": wind["lat"],
                    "lng": wind["lng"],
                    "source": wind.get("source", "ECMWF"),
                }
                complete_data["v10_wind"] = {
                    "grid": wind["v10"],
                    "lat": wind["lat"],
                    "lng": wind["lng"],
                    "source": wind.get("source", "ECMWF"),
                }
                complete_data["metadata"]["sources"]["wind"] = wind.get("source", "ECMWF")
            except Exception as e2:
                complete_data["metadata"]["status"]["wind_error"] = str(e2)

        try:
            wind_stress = NASAClient.fetch_wind_stress(lat_min, lat_max, lng_min, lng_max, date)
            if wind_stress:
                complete_data["wind_stress_x"] = {
                    "grid": wind_stress["tau_x"],
                    "lat": wind_stress["lat"],
                    "lng": wind_stress["lng"],
                    "source": wind_stress.get("source", "NASA"),
                }
                complete_data["wind_stress_y"] = {
                    "grid": wind_stress["tau_y"],
                    "lat": wind_stress["lat"],
                    "lng": wind_stress["lng"],
                    "source": wind_stress.get("source", "NASA"),
                }
                complete_data["metadata"]["sources"]["wind_stress"] = wind_stress.get("source", "NASA")
        except Exception as e:
            complete_data["metadata"]["status"]["wind_stress_error"] = str(e)

        # Fetch bathymetry (doesn't change with date)
        try:
            bathymetry = GEBCOClient.fetch_bathymetry(lat_min, lat_max, lng_min, lng_max)
            complete_data["bathymetry"] = bathymetry
            complete_data["metadata"]["sources"]["bathymetry"] = bathymetry.get("source", "GEBCO")
        except Exception as e:
            complete_data["metadata"]["status"]["bathymetry_error"] = str(e)

        # Add PINN Physics-Informed Data Filling (Fill gaps from cloud cover)
        try:
            if "sst" in complete_data and "u_current" in complete_data and "v_current" in complete_data:
                sst_grid = complete_data["sst"]["grid"]
                u_curr = np.array(complete_data["u_current"]["grid"])
                v_curr = np.array(complete_data["v_current"]["grid"])

                # Run PINN-inspired filler for SST gaps (e.g. from cloud cover in monsoon)
                filled_sst = pinn_engine.fill_sst_gaps(sst_grid, u_curr, v_curr)
                complete_data["sst"]["grid"] = filled_sst
                complete_data["metadata"]["pinn_enhanced_sst"] = True

            if "chlorophyll" in complete_data and "u_current" in complete_data and "v_current" in complete_data:
                chl_grid = complete_data["chlorophyll"]["grid"]
                u_curr = np.array(complete_data["u_current"]["grid"])
                v_curr = np.array(complete_data["v_current"]["grid"])

                # Chlorophyll gap filling with physics constraints
                upwelling_idx = 0.5 # Default heuristic
                filled_chl = pinn_engine.fill_chlorophyll_gaps(chl_grid, u_curr, v_curr, upwelling_idx)
                complete_data["chlorophyll"]["grid"] = filled_chl
                complete_data["metadata"]["pinn_enhanced_chl"] = True

        except Exception as e:
            logger.warning(f"[PINN] Gap filling failed: {e}")

        # Add data quality summary
        complete_data["metadata"]["data_quality"] = DataAggregator._assess_data_quality(complete_data)

        return complete_data

    @staticmethod
    def _assess_data_quality(data: Dict) -> Dict:
        """
        Assess quality of fetched data

        Returns dict with quality metrics
        """
        quality = {
            "complete": True,
            "missing_fields": [],
            "required_fields": [
                "sst",
                "u_current",
                "v_current",
                "chlorophyll",
                "u10_wind",
                "v10_wind",
                "bathymetry",
            ],
        }

        for field in quality["required_fields"]:
            if field not in data or data[field] is None:
                quality["missing_fields"].append(field)
                quality["complete"] = False

        quality["completeness_percent"] = (
            100 * (len(quality["required_fields"]) - len(quality["missing_fields"])) /
            len(quality["required_fields"])
        )

        return quality

    @staticmethod
    def fetch_coastal_region(port_name: str = "Ratnagiri",
                            radius_km: float = 100,
                            date: datetime = None) -> Dict:
        """
        Fetch data for a region around a specific port

        Args:
            port_name: Port name (Ratnagiri, Mumbai, Sindhudurg, Malvan)
            radius_km: Search radius around port in km
            date: Date for data

        Returns:
            Complete dataset for region around port
        """
        # Port coordinates (latitude, longitude)
        ports = {
            "Ratnagiri": (16.99, 73.30),
            "Mumbai": (19.02, 72.82),
            "Sindhudurg": (15.65, 73.78),
            "Malvan": (15.96, 73.78),
        }

        if port_name not in ports:
            return {"error": f"Unknown port: {port_name}"}

        lat, lng = ports[port_name]

        # Convert km to degrees (~111 km per degree)
        radius_deg = radius_km / 111.0

        lat_min = max(DataAggregator.DEFAULT_LAT_MIN, lat - radius_deg)
        lat_max = min(DataAggregator.DEFAULT_LAT_MAX, lat + radius_deg)
        lng_min = max(DataAggregator.DEFAULT_LNG_MIN, lng - radius_deg)
        lng_max = min(DataAggregator.DEFAULT_LNG_MAX, lng + radius_deg)

        data = DataAggregator.fetch_pfz_data(lat_min, lat_max, lng_min, lng_max, date)
        data["region"]["port"] = port_name
        data["region"]["port_coords"] = {"lat": lat, "lng": lng}
        data["region"]["search_radius_km"] = radius_km

        return data

    @staticmethod
    def get_available_sources() -> Dict:
        """Get information about available data sources and their status"""
        return {
            "CMEMS": CMEMSClient.get_status(),
            "NASA": NASAClient.get_status(),
            "ECMWF": ECMWFClient.get_status(),
            "GEBCO": GEBCOClient.get_status(),
        }

    @staticmethod
    def save_to_file(data: Dict, filename: str) -> bool:
        """
        Save fetched data to JSON file for later processing

        Args:
            data: Data dict from fetch_pfz_data
            filename: Output filename

        Returns:
            True if successful
        """
        try:
            with open(filename, "w") as f:
                # Convert numpy arrays to lists if present
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving data to {filename}: {e}")
            return False

    @staticmethod
    def load_from_file(filename: str) -> Optional[Dict]:
        """
        Load previously saved data from JSON file

        Args:
            filename: Input filename

        Returns:
            Data dict or None if error
        """
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading data from {filename}: {e}")
            return None


# Convenience function
def get_pfz_data(date: datetime = None) -> Dict:
    """
    Quick fetch of PFZ data for default Maharashtra EEZ region

    Args:
        date: Date for data (defaults to today)

    Returns:
        Complete oceanographic dataset
    """
    return DataAggregator.fetch_pfz_data(date=date)


if __name__ == "__main__":
    print("Testing Data Aggregator (Mock Mode)")
    print("=" * 60)

    # Test 1: Fetch for default region
    print("\n1️⃣ Fetching data for Maharashtra EEZ...")
    data = DataAggregator.fetch_pfz_data()

    print(f"[OK] Date: {data['date']}")
    print(f"[OK] Region: {data['region']['lat_min']}-{data['region']['lat_max']}°N, "
          f"{data['region']['lng_min']}-{data['region']['lng_max']}°E")
    print(f"[OK] Data sources: {list(data['metadata']['sources'].keys())}")
    print(f"[OK] Data completeness: {data['metadata']['data_quality']['completeness_percent']:.1f}%")

    # Test 2: Fetch for specific port
    print("\n2️⃣ Fetching data for Ratnagiri region...")
    port_data = DataAggregator.fetch_coastal_region("Ratnagiri", radius_km=100)

    print(f"[OK] Port: {port_data['region']['port']}")
    print(f"[OK] Search radius: {port_data['region']['search_radius_km']} km")

    # Test 3: Check data sources
    print("\n3️⃣ Checking data source status...")
    sources = DataAggregator.get_available_sources()

    for source_name, status in sources.items():
        print(f"   {source_name}: {status['status']}")

    # Test 4: Save data to file
    print("\n4️⃣ Saving data to file...")
    if DataAggregator.save_to_file(data, "test_pfz_data.json"):
        print("[OK] Data saved to test_pfz_data.json")

        # Load it back
        loaded = DataAggregator.load_from_file("test_pfz_data.json")
        if loaded:
            print(f"[OK] Data loaded back successfully (date: {loaded['date']})")

    print("\n" + "=" * 60)
    print("[OK] Data Aggregator ready for PFZ algorithm processing")
