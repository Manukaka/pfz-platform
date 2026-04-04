"""
Data Fetching Agents
डेटा एजेंट - समानांतर डेटा संग्रह

Agents that fetch data from various sources in parallel
"""

import asyncio
import sys
from datetime import datetime
from typing import Dict, Any
import logging
from concurrent.futures import ThreadPoolExecutor

from .base_agent import DataFetchAgent

# Create thread pool for compatibility with Python < 3.9
_executor = ThreadPoolExecutor(max_workers=4)

async def async_call(func, *args, **kwargs):
    """Call sync function asynchronously (compatible with Python 3.8+)"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, func, *args)
from app.data.cmems_client import CMEMSClient
from app.data.nasa_client import NASAClient
from app.data.ecmwf_client import ECMWFClient
from app.data.gebco_client import GEBCOClient
from app.data.earthkit_client import fetch_sst_grid_ecmwf, fetch_wind_grid_ecmwf

logger = logging.getLogger(__name__)


class CMEMSDataAgent(DataFetchAgent):
    """Fetches oceanographic data from CMEMS"""

    def __init__(self):
        super().__init__(
            agent_id="cmems_agent",
            agent_name="CMEMS Oceanographic Agent",
            specialization="CMEMS API"
        )

    async def analyze(self, data: Dict[str, Any], context: Dict = None) -> Dict[str, Any]:
        """Fetch CMEMS data — enhanced with earthkit SST when available"""
        self.add_reasoning("Fetching CMEMS oceanographic data...")

        try:
            region = context.get("region", {}) if context else {}
            date = context.get("date") if context else None

            lat_min = region.get("lat_min", 14.0)
            lat_max = region.get("lat_max", 21.0)
            lng_min = region.get("lng_min", 67.0)
            lng_max = region.get("lng_max", 74.5)

            loop = asyncio.get_event_loop()

            # Try earthkit for real SST first, fall back to CMEMS
            sst = await loop.run_in_executor(
                _executor,
                lambda: fetch_sst_grid_ecmwf(lat_min, lat_max, lng_min, lng_max)
            )
            sst_source = "ECMWF-IFS"
            if not sst:
                sst = await loop.run_in_executor(
                    _executor,
                    lambda: CMEMSClient.fetch_sst(lat_min, lat_max, lng_min, lng_max, date)
                )
                sst_source = "CMEMS"

            currents = await loop.run_in_executor(
                _executor,
                lambda: CMEMSClient.fetch_currents(lat_min, lat_max, lng_min, lng_max, date)
            )
            chlorophyll = await loop.run_in_executor(
                _executor,
                lambda: CMEMSClient.fetch_chlorophyll(lat_min, lat_max, lng_min, lng_max, date)
            )

            self.confidence = 0.90 if sst_source == "ECMWF-IFS" else 0.85
            self.add_reasoning(f"SST from {sst_source}, currents and chlorophyll from CMEMS")

            return {
                "raw_data": {
                    "sst": sst,
                    "currents": currents,
                    "chlorophyll": chlorophyll,
                },
                "confidence": self.confidence,
                "source": f"CMEMS+{sst_source}",
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self.add_error(f"CMEMS fetch failed: {str(e)}")
            self.confidence = 0.0
            return {
                "raw_data": {},
                "confidence": 0.0,
                "error": str(e),
                "source": "CMEMS"
            }


class NASADataAgent(DataFetchAgent):
    """Fetches atmospheric data from NASA"""

    def __init__(self):
        super().__init__(
            agent_id="nasa_agent",
            agent_name="NASA Atmospheric Agent",
            specialization="NASA API"
        )

    async def analyze(self, data: Dict[str, Any], context: Dict = None) -> Dict[str, Any]:
        """Fetch NASA data"""
        self.add_reasoning("Fetching NASA atmospheric data...")

        try:
            region = context.get("region", {}) if context else {}
            date = context.get("date") if context else None

            lat_min = region.get("lat_min", 14.0)
            lat_max = region.get("lat_max", 21.0)
            lng_min = region.get("lng_min", 67.0)
            lng_max = region.get("lng_max", 74.5)

            loop = asyncio.get_event_loop()
            wind_stress = await loop.run_in_executor(
                _executor,
                lambda: NASAClient.fetch_wind_stress(lat_min, lat_max, lng_min, lng_max, date)
            )

            self.confidence = 0.8
            self.add_reasoning("Successfully fetched wind stress data")

            return {
                "raw_data": {
                    "wind_stress": wind_stress,
                },
                "confidence": self.confidence,
                "source": "NASA",
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self.add_error(f"NASA fetch failed: {str(e)}")
            self.confidence = 0.0
            return {
                "raw_data": {},
                "confidence": 0.0,
                "error": str(e),
                "source": "NASA"
            }


class ECMWFDataAgent(DataFetchAgent):
    """Fetches meteorological data from ECMWF"""

    def __init__(self):
        super().__init__(
            agent_id="ecmwf_agent",
            agent_name="ECMWF Meteorological Agent",
            specialization="ECMWF CDS"
        )

    async def analyze(self, data: Dict[str, Any], context: Dict = None) -> Dict[str, Any]:
        """Fetch ECMWF data — uses earthkit for real SST and wind"""
        self.add_reasoning("Fetching ECMWF data via earthkit (real IFS data)...")

        try:
            region = context.get("region", {}) if context else {}
            date = context.get("date") if context else None

            lat_min = region.get("lat_min", 14.0)
            lat_max = region.get("lat_max", 21.0)
            lng_min = region.get("lng_min", 67.0)
            lng_max = region.get("lng_max", 74.5)

            raw_data = {}

            # Fetch real SST via earthkit
            loop = asyncio.get_event_loop()
            sst_grid = await loop.run_in_executor(
                _executor,
                lambda: fetch_sst_grid_ecmwf(lat_min, lat_max, lng_min, lng_max)
            )
            if sst_grid:
                raw_data["sst"] = {
                    "grid": sst_grid.get("sst_grid"),
                    "lat": sst_grid.get("lat"),
                    "lng": sst_grid.get("lng"),
                    "source": sst_grid.get("source", "ECMWF-IFS"),
                }
                self.add_reasoning(f"Real SST from {sst_grid.get('source', 'ECMWF-IFS')}")

            # Fetch real wind via earthkit (fallback to old mock)
            wind_grid = await loop.run_in_executor(
                _executor,
                lambda: fetch_wind_grid_ecmwf(lat_min, lat_max, lng_min, lng_max)
            )
            if wind_grid:
                raw_data["wind_10m"] = wind_grid
                self.add_reasoning(f"Real wind from {wind_grid.get('source', 'ECMWF-IFS')}")
            else:
                wind = await loop.run_in_executor(
                    _executor,
                    lambda: ECMWFClient.fetch_wind_10m(lat_min, lat_max, lng_min, lng_max, date)
                )
                raw_data["wind_10m"] = wind

            self.confidence = 0.92 if sst_grid else 0.82
            self.add_reasoning("ECMWF data fetch complete")

            return {
                "raw_data": raw_data,
                "confidence": self.confidence,
                "source": "ECMWF-earthkit",
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self.add_error(f"ECMWF fetch failed: {str(e)}")
            self.confidence = 0.0
            return {
                "raw_data": {},
                "confidence": 0.0,
                "error": str(e),
                "source": "ECMWF"
            }


class GEBCODataAgent(DataFetchAgent):
    """Fetches bathymetry data from GEBCO"""

    def __init__(self):
        super().__init__(
            agent_id="gebco_agent",
            agent_name="GEBCO Bathymetry Agent",
            specialization="GEBCO"
        )

    async def analyze(self, data: Dict[str, Any], context: Dict = None) -> Dict[str, Any]:
        """Fetch GEBCO data"""
        self.add_reasoning("Fetching bathymetry data...")

        try:
            region = context.get("region", {}) if context else {}

            lat_min = region.get("lat_min", 14.0)
            lat_max = region.get("lat_max", 21.0)
            lng_min = region.get("lng_min", 67.0)
            lng_max = region.get("lng_max", 74.5)

            loop = asyncio.get_event_loop()
            bathymetry = await loop.run_in_executor(
                _executor,
                lambda: GEBCOClient.fetch_bathymetry(lat_min, lat_max, lng_min, lng_max)
            )

            self.confidence = 0.95
            self.add_reasoning("Successfully fetched bathymetry data")

            return {
                "raw_data": {
                    "bathymetry": bathymetry,
                },
                "confidence": self.confidence,
                "source": "GEBCO",
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self.add_error(f"GEBCO fetch failed: {str(e)}")
            self.confidence = 0.0
            return {
                "raw_data": {},
                "confidence": 0.0,
                "error": str(e),
                "source": "GEBCO"
            }
