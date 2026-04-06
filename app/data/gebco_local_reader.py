"""
GEBCO Local Grid Reader
Reads bathymetry data from locally stored GEBCO NetCDF grid
Much faster than WMS and provides exact depths
"""

import os
import numpy as np
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Possible grid file locations
GRID_PATHS = [
    "data/gebco/arabian_sea_gebco.nc",  # Regional subset (preferred)
    "data/gebco/gebco_2023.nc",          # Full global grid
    "data/gebco/srtm15_plus.nc",         # Alternative dataset
    "data/gebco/GEBCO_2023.nc",          # Alternative naming
]


class GEBCOLocalReader:
    """Read bathymetry from local GEBCO NetCDF file"""

    _dataset = None
    _grid_path = None
    _cache = {}

    @classmethod
    def initialize(cls):
        """Find and open GEBCO grid file"""
        if cls._dataset is not None:
            return True

        # Find available grid file
        for path in GRID_PATHS:
            if os.path.exists(path):
                try:
                    import netCDF4 as nc
                    cls._dataset = nc.Dataset(path, 'r')
                    cls._grid_path = path
                    logger.info(f"[OK] Loaded GEBCO grid: {path}")

                    # Log grid info
                    if 'lat' in cls._dataset.variables:
                        lats = cls._dataset.variables['lat'][:]
                        lons = cls._dataset.variables['lon'][:]
                        logger.info(f"  Grid coverage: {lats.min():.1f}°N to {lats.max():.1f}°N, "
                                  f"{lons.min():.1f}°E to {lons.max():.1f}°E")

                    return True

                except Exception as e:
                    logger.warning(f"Failed to load {path}: {e}")
                    continue

        logger.warning("No local GEBCO grid found. Install with: python download_gebco_grid.py")
        return False

    @classmethod
    def is_available(cls) -> bool:
        """Check if local grid is available"""
        return cls.initialize()

    @classmethod
    def get_depth_at_point(cls, lat: float, lon: float) -> float:
        """
        Get exact depth at a single point

        Args:
            lat: Latitude in degrees
            lon: Longitude in degrees

        Returns:
            Depth in meters (negative = below sea level)
        """
        if not cls.initialize():
            raise Exception("GEBCO grid not available")

        try:
            # Get grid coordinates
            lats = cls._dataset.variables['lat'][:]
            lons = cls._dataset.variables['lon'][:]

            # Find nearest indices
            lat_idx = np.argmin(np.abs(lats - lat))
            lon_idx = np.argmin(np.abs(lons - lon))

            # Get elevation (GEBCO uses elevation, negative = depth)
            elevation = cls._dataset.variables['elevation'][lat_idx, lon_idx]

            depth = float(elevation)  # Already negative for ocean

            logger.debug(f"Depth at ({lat:.4f}, {lon:.4f}): {depth:.1f}m")
            return depth

        except Exception as e:
            logger.error(f"Error reading point depth: {e}")
            raise

    @classmethod
    def get_depth_grid(cls, lat_min: float, lat_max: float,
                       lon_min: float, lon_max: float,
                       resolution: int = 100) -> Dict:
        """
        Get depth grid for a region

        Args:
            lat_min, lat_max, lon_min, lon_max: Bounding box
            resolution: Target grid resolution (will use GEBCO's native resolution if lower)

        Returns:
            Dict with depth grid and coordinates
        """
        if not cls.initialize():
            raise Exception("GEBCO grid not available")

        try:
            # Get full coordinate arrays
            lats = cls._dataset.variables['lat'][:]
            lons = cls._dataset.variables['lon'][:]

            # Find indices for bounding box
            lat_mask = (lats >= lat_min) & (lats <= lat_max)
            lon_mask = (lons >= lon_min) & (lons <= lon_max)

            lat_indices = np.where(lat_mask)[0]
            lon_indices = np.where(lon_mask)[0]

            if len(lat_indices) == 0 or len(lon_indices) == 0:
                raise Exception(f"Bounding box outside grid coverage")

            # Extract elevation data
            lat_start, lat_end = lat_indices[0], lat_indices[-1] + 1
            lon_start, lon_end = lon_indices[0], lon_indices[-1] + 1

            elevation = cls._dataset.variables['elevation'][lat_start:lat_end, lon_start:lon_end]

            # Get actual lat/lon for extracted region
            region_lats = lats[lat_start:lat_end]
            region_lons = lons[lon_start:lon_end]

            # Optionally downsample if grid is too fine
            native_res = len(region_lats)
            if native_res > resolution * 2:
                # Downsample to requested resolution
                from scipy.ndimage import zoom
                scale_lat = resolution / len(region_lats)
                scale_lon = resolution / len(region_lons)

                elevation_resampled = zoom(elevation, (scale_lat, scale_lon), order=1)
                region_lats_resampled = np.linspace(region_lats[0], region_lats[-1], resolution)
                region_lons_resampled = np.linspace(region_lons[0], region_lons[-1], resolution)

                elevation = elevation_resampled
                region_lats = region_lats_resampled
                region_lons = region_lons_resampled

            logger.info(f"Extracted GEBCO grid: {elevation.shape}, depth range: {np.nanmin(elevation):.1f}m to {np.nanmax(elevation):.1f}m")

            return {
                'bathymetry_grid': elevation.tolist(),
                'lat': region_lats.tolist(),
                'lon': region_lons.tolist(),
                'source': 'GEBCO_LOCAL_GRID',
                'grid_file': cls._grid_path,
                'resolution': f'{elevation.shape[0]}x{elevation.shape[1]}',
                'min_depth': float(np.nanmin(elevation)),
                'max_depth': float(np.nanmax(elevation)),
                'units': 'meters (negative = below sea level)',
                'note': 'Exact depths from GEBCO 2023 grid'
            }

        except Exception as e:
            logger.error(f"Error reading depth grid: {e}")
            raise

    @classmethod
    def close(cls):
        """Close the dataset"""
        if cls._dataset is not None:
            cls._dataset.close()
            cls._dataset = None
            logger.info("Closed GEBCO grid")
