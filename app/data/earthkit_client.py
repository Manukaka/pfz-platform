"""
SAMUDRA AI — EarthKit Data Client
ECMWF earthkit-data integration for accurate SST and ocean data

Uses ECMWF open data (free, no API key) for:
- Sea Surface Temperature (SST) from IFS forecast
- 10m wind components (u, v)

Falls back gracefully if earthkit is unavailable or data fetch fails.
"""
import os
import math
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Cache for fetched data (avoid re-fetching within same hour)
_sst_cache: Dict = {"timestamp": None, "data": None}
_CACHE_TTL_SECONDS = 3600  # 1 hour


def _is_cache_valid() -> bool:
    if _sst_cache["timestamp"] is None or _sst_cache["data"] is None:
        return False
    age = (datetime.now(timezone.utc) - _sst_cache["timestamp"]).total_seconds()
    return age < _CACHE_TTL_SECONDS


def fetch_sst_ecmwf_opendata(
    lat_min: float = 5.0,
    lat_max: float = 25.0,
    lon_min: float = 55.0,
    lon_max: float = 78.0,
    grid_step: float = 0.5,
) -> Optional[List[Dict]]:
    """
    Fetch real SST data from ECMWF Open Data (free, no API key needed).
    Uses the latest IFS forecast skin temperature over ocean as SST proxy.

    Returns list of {"lat": float, "lon": float, "sst": float} points,
    or None if fetch fails.
    """
    if _is_cache_valid():
        return _sst_cache["data"]

    try:
        import earthkit.data as ekd

        logger.info("Fetching SST from ECMWF Open Data (IFS latest)...")

        # Fetch skin temperature (skt) from latest IFS forecast
        # skt over ocean = SST. step 0 = analysis time = most accurate
        ds: Any = ekd.from_source(
            "ecmwf-open-data",
            model="ifs",
            param=["skt"],  # Skin temperature (= SST over ocean)
            levtype="sfc",
            step=[0],
        )

        if ds is None or len(ds) == 0:
            logger.warning("ECMWF open data returned no fields")
            return None

        # Extract data from GRIB field
        field = ds[0]
        ll = field.to_latlon()  # dict with 'lat', 'lon' 2D arrays
        values = field.to_numpy()  # 2D array (nlat x nlon)

        import numpy as np
        lats = np.array(ll['lat'])
        lons = np.array(ll['lon'])
        vals = np.array(values)

        # All arrays are 2D (721x1440 for 0.25° global grid)
        # Apply mask for Arabian Sea region
        mask = (lats >= lat_min) & (lats <= lat_max) & (lons >= lon_min) & (lons <= lon_max)

        arab_lats = lats[mask]
        arab_lons = lons[mask]
        arab_vals = vals[mask]

        # Convert Kelvin to Celsius
        arab_sst = arab_vals - 273.15 if arab_vals.mean() > 100 else arab_vals

        # Build point list (subsample for performance — take every Nth point)
        n_points = len(arab_lats)
        step = max(1, n_points // 500)  # Limit to ~500 points

        sst_points = []
        for i in range(0, n_points, step):
            sst_c = float(arab_sst[i])
            if 15 <= sst_c <= 38:
                sst_points.append({
                    "lat": round(float(arab_lats[i]), 3),
                    "lon": round(float(arab_lons[i]), 3),
                    "sst": round(sst_c, 2),
                })

        if sst_points:
            logger.info(f"ECMWF SST: {len(sst_points)} points for Arabian Sea region")
            _sst_cache["timestamp"] = datetime.now(timezone.utc)
            _sst_cache["data"] = sst_points

            # Also save to sst_data.json for other components
            try:
                with open("sst_data.json", "w") as f:
                    json.dump({
                        "source": "ECMWF-IFS-OpenData",
                        "fetched": datetime.now(timezone.utc).isoformat(),
                        "points": sst_points,
                    }, f)
            except Exception:
                pass

            return sst_points
        else:
            logger.warning("No valid SST points in Arabian Sea region from ECMWF")
            return None

    except ImportError:
        logger.warning("earthkit-data not installed, skipping ECMWF SST fetch")
        return None
    except Exception as e:
        logger.warning(f"ECMWF open data SST fetch failed: {e}")
        return None


def fetch_sst_from_cds(
    lat_min: float = 5.0,
    lat_max: float = 25.0,
    lon_min: float = 55.0,
    lon_max: float = 78.0,
) -> Optional[List[Dict]]:
    """
    Fetch SST from Copernicus Climate Data Store (CDS) using ERA5 reanalysis.
    Requires CDS API key configured (~/.cdsapirc or CDSAPI_URL/CDSAPI_KEY env vars).

    Returns list of {"lat", "lon", "sst"} dicts or None.
    """
    if _is_cache_valid():
        return _sst_cache["data"]

    try:
        import earthkit.data as ekd

        # Check if CDS credentials are available
        cds_key = os.environ.get("CDSAPI_KEY") or os.environ.get("CDS_API_KEY")
        if not cds_key and not os.path.exists(os.path.expanduser("~/.cdsapirc")):
            logger.info("No CDS API credentials found, skipping ERA5 SST")
            return None

        logger.info("Fetching SST from CDS ERA5 reanalysis...")

        # Yesterday's date (ERA5 has ~5 day lag, but recent dates work on CDS)
        yesterday = (datetime.now(timezone.utc) - timedelta(days=2)).strftime("%Y-%m-%d")

        ds: Any = ekd.from_source(
            "cds",
            "reanalysis-era5-single-levels",
            request=dict(
                product_type="reanalysis",
                variable=["sea_surface_temperature"],
                area=[lat_max, lon_min, lat_min, lon_max],  # N, W, S, E
                grid=[0.25, 0.25],
                date=yesterday,
                time="12:00",
            ),
        )

        if ds is None or len(ds) == 0:
            return None

        field = ds[0]
        ll = field.to_latlon()
        values = field.to_numpy()

        import numpy as np
        lats = np.array(ll['lat'])
        lons = np.array(ll['lon'])
        vals = np.array(values)

        mask = (lats >= lat_min) & (lats <= lat_max) & (lons >= lon_min) & (lons <= lon_max)
        arab_lats = lats[mask]
        arab_lons = lons[mask]
        arab_vals = vals[mask]
        arab_sst = arab_vals - 273.15 if arab_vals.mean() > 100 else arab_vals

        sst_points = []
        n_points = len(arab_lats)
        step = max(1, n_points // 500)
        for i in range(0, n_points, step):
            sst_c = float(arab_sst[i])
            if 15 <= sst_c <= 38:
                sst_points.append({
                    "lat": round(float(arab_lats[i]), 3),
                    "lon": round(float(arab_lons[i]), 3),
                    "sst": round(sst_c, 2),
                })

        if sst_points:
            logger.info(f"ERA5 SST: {len(sst_points)} points")
            _sst_cache["timestamp"] = datetime.now(timezone.utc)
            _sst_cache["data"] = sst_points

            try:
                with open("sst_data.json", "w") as f:
                    json.dump({
                        "source": "ERA5-CDS",
                        "fetched": datetime.now(timezone.utc).isoformat(),
                        "points": sst_points,
                    }, f)
            except Exception:
                pass

            return sst_points

        return None

    except ImportError:
        return None
    except Exception as e:
        logger.warning(f"CDS ERA5 SST fetch failed: {e}")
        return None


def get_accurate_sst(
    lat_min: float = 5.0,
    lat_max: float = 25.0,
    lon_min: float = 55.0,
    lon_max: float = 78.0,
) -> Tuple[Optional[List[Dict]], str]:
    """
    Get the most accurate SST data available, trying sources in order:
    1. ECMWF Open Data (free, no key)
    2. CDS ERA5 (needs API key)
    3. Existing sst_data.json fallback

    Returns (sst_points, source_name)
    """
    # Try ECMWF open data first (free)
    points = fetch_sst_ecmwf_opendata(lat_min, lat_max, lon_min, lon_max)
    if points:
        return points, "ECMWF-IFS"

    # Try CDS ERA5
    points = fetch_sst_from_cds(lat_min, lat_max, lon_min, lon_max)
    if points:
        return points, "ERA5-CDS"

    # Fallback to existing file
    try:
        if os.path.exists("sst_data.json"):
            with open("sst_data.json", "r") as f:
                data = json.load(f)
                pts = data.get("points", [])
                if pts:
                    src = data.get("source", "cached-file")
                    return pts, src
    except Exception:
        pass

    return None, "estimated"


def fetch_sst_grid_ecmwf(
    lat_min: float = 14.0,
    lat_max: float = 21.0,
    lon_min: float = 67.0,
    lon_max: float = 74.5,
) -> Optional[Dict]:
    """
    Fetch real SST from ECMWF and return in grid format compatible with the agent pipeline.
    Returns {"sst_grid": 2D list, "lat": list, "lng": list, "source": str}
    or None if fetch fails.
    """
    try:
        import numpy as np

        # Get point-based SST (uses cache)
        points, source = get_accurate_sst(lat_min, lat_max, lon_min, lon_max)
        if not points:
            return None

        # Build a regular grid from the scattered points
        resolution = 0.25
        lats = np.arange(lat_min, lat_max + resolution, resolution)
        lngs = np.arange(lon_min, lon_max + resolution, resolution)
        sst_grid = np.full((len(lats), len(lngs)), np.nan)

        # Place each point into the nearest grid cell
        for p in points:
            lat_idx = int(round((p["lat"] - lat_min) / resolution))
            lon_idx = int(round((p["lon"] - lon_min) / resolution))
            if 0 <= lat_idx < len(lats) and 0 <= lon_idx < len(lngs):
                sst_grid[lat_idx, lon_idx] = p["sst"]

        # Fill NaN gaps with nearest-neighbour interpolation
        from scipy.ndimage import distance_transform_edt
        nan_mask = np.isnan(sst_grid)
        if nan_mask.any() and not nan_mask.all():
            indices = distance_transform_edt(nan_mask, return_distances=False, return_indices=True)
            if indices is not None:
                sst_grid = sst_grid[tuple(indices)]

        # If scipy isn't available or all NaN, fill with mean
        if np.isnan(sst_grid).any():
            mean_sst = np.nanmean(sst_grid) if not np.isnan(sst_grid).all() else 28.0
            sst_grid = np.where(np.isnan(sst_grid), mean_sst, sst_grid)

        return {
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "sst_grid": sst_grid.tolist(),
            "lat": lats.tolist(),
            "lng": lngs.tolist(),
            "source": source,
        }

    except Exception as e:
        logger.warning(f"Failed to build SST grid from earthkit: {e}")
        return None


def fetch_wind_grid_ecmwf(
    lat_min: float = 14.0,
    lat_max: float = 21.0,
    lon_min: float = 67.0,
    lon_max: float = 74.5,
) -> Optional[Dict]:
    """
    Fetch real 10m wind (u10, v10) from ECMWF Open Data.
    Returns {"u10": 2D list, "v10": 2D list, "lat": list, "lng": list, "source": str}
    or None if fetch fails.
    """
    try:
        import earthkit.data as ekd
        import numpy as np

        logger.info("Fetching 10m wind from ECMWF Open Data...")

        ds: Any = ekd.from_source(
            "ecmwf-open-data",
            model="ifs",
            param=["10u", "10v"],
            levtype="sfc",
            step=[0],
        )

        if ds is None or len(ds) < 2:
            return None

        resolution = 0.25
        out_lats = np.arange(lat_min, lat_max + resolution, resolution)
        out_lngs = np.arange(lon_min, lon_max + resolution, resolution)

        grids = {}
        for field in ds:
            meta = field.metadata()
            param = meta.get("shortName", meta.get("param", ""))
            ll = field.to_latlon()
            vals = field.to_numpy()
            lats = np.array(ll['lat'])
            lons = np.array(ll['lon'])
            v = np.array(vals)

            mask = (lats >= lat_min) & (lats <= lat_max) & (lons >= lon_min) & (lons <= lon_max)
            grid = np.full((len(out_lats), len(out_lngs)), 0.0)
            for idx in np.argwhere(mask):
                i, j = idx
                lat_i = int(round((float(lats[i, j]) - lat_min) / resolution))
                lon_j = int(round((float(lons[i, j]) - lon_min) / resolution))
                if 0 <= lat_i < len(out_lats) and 0 <= lon_j < len(out_lngs):
                    grid[lat_i, lon_j] = float(v[i, j])
            grids[param] = grid

        u10 = grids.get("10u", grids.get("u10", np.zeros((len(out_lats), len(out_lngs)))))
        v10 = grids.get("10v", grids.get("v10", np.zeros((len(out_lats), len(out_lngs)))))

        return {
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "u10": u10.tolist() if hasattr(u10, 'tolist') else u10,
            "v10": v10.tolist() if hasattr(v10, 'tolist') else v10,
            "lat": out_lats.tolist(),
            "lng": out_lngs.tolist(),
            "source": "ECMWF-IFS",
        }
    except Exception as e:
        logger.warning(f"ECMWF wind fetch failed: {e}")
        return None


def get_accurate_depth_at_point(lat: float, lon: float) -> Optional[float]:
    """
    Try to get accurate bathymetry depth from GEBCO NetCDF file via earthkit.
    Returns depth in meters (positive) or None if not available.
    """
    try:
        # Check for local GEBCO grid file
        gebco_paths = [
            "data/gebco/GEBCO_2024.nc",
            "data/gebco/gebco_2024_n25_s5_w55_e78.nc",
            "data/GEBCO_2024.nc",
            "GEBCO_2024.nc",
        ]

        gebco_path = None
        for p in gebco_paths:
            if os.path.exists(p):
                gebco_path = p
                break

        if not gebco_path:
            return None

        import earthkit.data as ekd

        ds = ekd.from_source("file", gebco_path)
        # GEBCO NetCDF has elevation (negative = depth)
        xr_ds = ds.to_xarray()

        # Find nearest grid point
        if "elevation" in xr_ds:
            elev = xr_ds["elevation"].sel(lat=lat, lon=lon, method="nearest").values
            depth = -float(elev) if elev < 0 else 0  # positive depth
            return depth

        return None

    except Exception:
        return None
