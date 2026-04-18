"""
NASA Earthdata MODIS/VIIRS data ingestion.
Fetches chlorophyll-a, SST L3 mapped products for west coast.

Products:
  - MODIS Aqua: MYD09A1 (chlorophyll proxy), MYD11A2 (LST)
  - VIIRS SNPP: VNP09H1
  - Direct OPeNDAP access via Earthdata OPeNDAP endpoint

Auth: Set NASA_EARTHDATA_USERNAME + NASA_EARTHDATA_PASSWORD in .env
      Register at https://urs.earthdata.nasa.gov
"""
import asyncio
import os
import json
import aiohttp
import numpy as np
import structlog
from datetime import datetime, timezone, timedelta, date
from typing import Optional

logger = structlog.get_logger()

NASA_EARTHDATA_BASE = "https://opendap.earthdata.nasa.gov"
NASA_CMR_BASE = "https://cmr.earthdata.nasa.gov"

# West coast bounding box
BBOX = "68.0,8.0,78.0,24.5"  # lon_min,lat_min,lon_max,lat_max

MODIS_COLLECTIONS = {
    "chlorophyll_daily": {
        "short_name": "MODIS_TERRA_CHL_MONTHLY",
        "concept_id": "C2036882064-OBPG",
        "resolution": "4km",
    },
    "sst_daily": {
        "short_name": "MODIS_TERRA_SSTA_MONTHLY",
        "concept_id": "C2036882095-OBPG",
        "resolution": "4km",
    },
}


class NasaEarthdataIngester:
    """Fetches NASA MODIS/VIIRS ocean color and SST data."""

    def __init__(self):
        self.username = os.getenv("NASA_EARTHDATA_USERNAME", "")
        self.password = os.getenv("NASA_EARTHDATA_PASSWORD", "")
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            auth = aiohttp.BasicAuth(self.username, self.password) if self.username else None
            self._session = aiohttp.ClientSession(auth=auth)
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def fetch_latest_chlorophyll(self) -> list:
        """Fetch latest MODIS chlorophyll-a L3 mapped data for west coast."""
        if not self.username:
            logger.debug("NASA Earthdata credentials not set, using mock chlorophyll")
            return self._mock_chlorophyll_grid()

        target_date = date.today() - timedelta(days=3)  # 3-day lag for processing
        granule_url = await self._find_granule(
            "MODIS_TERRA_CHL_MONTHLY",
            target_date,
        )
        if not granule_url:
            return self._mock_chlorophyll_grid()

        try:
            session = await self._get_session()
            # OPeNDAP subset request
            opendap_url = (
                f"{granule_url}?chlor_a[0:1:4319][0:1:8639]"  # full global, then crop
            )
            async with session.get(opendap_url, timeout=aiohttp.ClientTimeout(total=300)) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    return self._parse_hdf_chlorophyll(data)
                else:
                    logger.warning("NASA fetch failed", status=resp.status)
                    return self._mock_chlorophyll_grid()
        except Exception as e:
            logger.error("NASA Earthdata fetch error", error=str(e))
            return self._mock_chlorophyll_grid()

    async def _find_granule(self, short_name: str, target_date: date) -> Optional[str]:
        """Find the latest available granule URL from CMR."""
        try:
            session = await self._get_session()
            params = {
                "short_name": short_name,
                "bounding_box": BBOX,
                "temporal": f"{target_date.isoformat()},{(target_date + timedelta(days=1)).isoformat()}",
                "page_size": 1,
                "sort_key": "-start_date",
            }
            async with session.get(
                f"{NASA_CMR_BASE}/search/granules.json",
                params=params,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    entries = data.get("feed", {}).get("entry", [])
                    if entries:
                        links = entries[0].get("links", [])
                        for link in links:
                            if "opendap" in link.get("href", "").lower():
                                return link["href"]
        except Exception as e:
            logger.warning("CMR granule search failed", error=str(e))
        return None

    def _parse_hdf_chlorophyll(self, data: bytes) -> list:
        """Parse HDF4/NetCDF binary chlorophyll data → records."""
        try:
            import netCDF4 as nc
            import io
            dataset = nc.Dataset("in_memory", memory=data)
            chl = dataset.variables.get("chlor_a") or dataset.variables.get("CHL")
            if chl is None:
                return self._mock_chlorophyll_grid()
            lats = dataset.variables["lat"][:]
            lons = dataset.variables["lon"][:]
            # Crop to west coast bbox
            lat_mask = (lats >= 8.0) & (lats <= 24.5)
            lon_mask = (lons >= 68.0) & (lons <= 78.0)
            chl_crop = chl[np.ix_(lat_mask, lon_mask)]
            lat_crop = lats[lat_mask]
            lon_crop = lons[lon_mask]
            records = []
            for i, lat in enumerate(lat_crop):
                for j, lon in enumerate(lon_crop):
                    val = float(chl_crop[i, j])
                    if val > 0 and val < 100:  # valid range mg/m³
                        records.append({
                            "lat": round(float(lat), 3),
                            "lon": round(float(lon), 3),
                            "chlorophyll": round(val, 4),
                            "source": "MODIS_TERRA",
                        })
            return records
        except ImportError:
            return self._mock_chlorophyll_grid()

    def _mock_chlorophyll_grid(self) -> list:
        """
        Realistic mock chlorophyll grid for west coast.
        Higher values in upwelling zones (Kerala, Karnataka coasts).
        """
        records = []
        for lat in np.arange(8.0, 24.5, 0.25):
            for lon in np.arange(68.0, 78.0, 0.25):
                # Upwelling signal: higher chlorophyll near shore and in southern states
                shore_distance = lon - 68.0
                upwelling_boost = max(0, 1.5 - shore_distance * 0.2) if lat < 14 else 0
                base = 0.8 + upwelling_boost
                chl = max(0.1, base + np.random.normal(0, 0.2))
                records.append({
                    "lat": round(float(lat), 2),
                    "lon": round(float(lon), 2),
                    "chlorophyll": round(float(chl), 3),
                    "source": "MODIS_mock",
                })
        return records

    async def fetch_viirs_sst(self) -> list:
        """Fetch VIIRS SNPP SST for west coast (better cloud penetration than MODIS)."""
        if not self.username:
            return []  # Copernicus already provides SST mock
        # Same pattern as chlorophyll but for VIIRS SST product
        logger.info("VIIRS SST fetch not implemented — using Copernicus SST")
        return []


class EcmwfIngester:
    """
    ECMWF ERA5 / IFS forecast data ingestion.
    Uses Copernicus Climate Data Store (CDS) API.

    Install: pip install cdsapi
    Register: https://cds.climate.copernicus.eu
    Configure: ~/.cdsapirc with API key
    """

    async def fetch_wind_wave_forecast(self) -> list:
        """Fetch wind speed, wave height, direction for west coast."""
        try:
            import cdsapi
            c = cdsapi.Client()
            now = datetime.now(timezone.utc)
            result = c.retrieve(
                "reanalysis-era5-single-levels",
                {
                    "product_type": "reanalysis",
                    "variable": [
                        "10m_u_component_of_wind",
                        "10m_v_component_of_wind",
                        "significant_height_of_combined_wind_waves_and_swell",
                        "mean_wave_period",
                    ],
                    "year": now.strftime("%Y"),
                    "month": now.strftime("%m"),
                    "day": now.strftime("%d"),
                    "time": ["00:00", "06:00", "12:00", "18:00"],
                    "area": [24.5, 68.0, 8.0, 78.0],  # N, W, S, E
                    "format": "netcdf",
                },
            )
            return self._parse_era5_netcdf(result)
        except ImportError:
            logger.warning("cdsapi not installed, using mock wind/wave data")
            return self._mock_wind_wave()
        except Exception as e:
            logger.error("ECMWF fetch error", error=str(e))
            return self._mock_wind_wave()

    def _mock_wind_wave(self) -> list:
        records = []
        for lat in np.arange(8.0, 24.5, 0.5):
            for lon in np.arange(68.0, 78.0, 0.5):
                records.append({
                    "lat": round(float(lat), 1),
                    "lon": round(float(lon), 1),
                    "wind_speed": round(float(np.random.normal(18, 5)), 1),
                    "wind_direction": round(float(np.random.uniform(180, 270)), 0),
                    "wave_height": round(float(np.random.gamma(2, 0.5)), 2),
                    "wave_period": round(float(np.random.normal(8, 1.5)), 1),
                    "source": "ECMWF_mock",
                })
        return records

    def _parse_era5_netcdf(self, filepath: str) -> list:
        try:
            import netCDF4 as nc
            dataset = nc.Dataset(filepath)
            # Parse u10, v10, swh, mwp
            lats = dataset.variables["latitude"][:]
            lons = dataset.variables["longitude"][:]
            u10 = dataset.variables["u10"][0]
            v10 = dataset.variables["v10"][0]
            swh = dataset.variables["swh"][0]
            records = []
            for i, lat in enumerate(lats):
                for j, lon in enumerate(lons):
                    wind_speed = np.sqrt(float(u10[i, j]) ** 2 + float(v10[i, j]) ** 2) * 3.6  # m/s → km/h
                    records.append({
                        "lat": float(lat),
                        "lon": float(lon),
                        "wind_speed": round(wind_speed, 1),
                        "wave_height": round(float(swh[i, j]), 2),
                        "source": "ECMWF_ERA5",
                    })
            return records
        except Exception as e:
            logger.error("ERA5 parse error", error=str(e))
            return self._mock_wind_wave()


nasa_ingester = NasaEarthdataIngester()
ecmwf_ingester = EcmwfIngester()
