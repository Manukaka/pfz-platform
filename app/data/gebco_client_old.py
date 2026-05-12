"""
SAMUDRA AI — GEBCO Data Client
समुद्र तल की गहराई - बाथीमेट्री डेटा

Fetches bathymetric data from GEBCO (General Bathymetric Chart of the Oceans):
- Sea floor elevation/depth
- Continental shelf topology
- Shelf break detection for PFZ clustering

GEBCO data is freely available gridded data at 15 arc-second resolution (~450m)
Reference: https://www.gebco.net/
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
import math
import json


class GEBCOClient:
    """GEBCO bathymetric data client"""

    # GEBCO data access
    DATA_SOURCE = "GEBCO_2024"  # Latest version
    DATA_RESOLUTION_ARCSEC = 15  # 15 arc-second resolution
    RESOLUTION_KM = 0.45  # ~450 meters at equator

    # Pre-computed bathymetry cache (can be from local GeoTIFF or API)
    CACHE_DIR = "data/cache/gebco"
    CACHE_TTL_DAYS = 365  # Bathymetry doesn't change often

    # Maharashtra EEZ shelf edge depths (meters below sea level)
    # Used for PFZ clustering - fish congregate near shelf edge
    SHELF_EDGE_DEPTH = 200  # Standard continental shelf edge
    SHELF_BREAK_REGION = (150, 250)  # Depth range where fishing is optimal

    def __init__(self):
        """Initialize GEBCO client"""
        pass

    @staticmethod
    def fetch_bathymetry(lat_min: float, lat_max: float, lng_min: float, lng_max: float,
                        use_cache: bool = True) -> Optional[Dict]:
        """
        Fetch bathymetric data (sea floor depth)

        Args:
            lat_min, lat_max, lng_min, lng_max: Bounding box
            use_cache: Whether to use cached data if available

        Returns:
            Dict with bathymetry grid: {"depth": 2D array, "lat": list, "lng": list, ...}
            Depth values in meters (negative = below sea level)
        """
        # For development, generate realistic mock data
        # In production, would load actual GEBCO GeoTIFF tiles
        return GEBCOClient._generate_mock_bathymetry(lat_min, lat_max, lng_min, lng_max)

    @staticmethod
    def get_depth_at_point(lat: float, lng: float) -> float:
        """
        Get sea floor depth at a specific point

        Args:
            lat, lng: Coordinate

        Returns:
            Depth in meters (negative value, e.g., -150m for 150m deep)
        """
        # Simplified calculation based on distance from coast
        distance_from_coast = max(0, lng - 72.5)

        # Continental shelf: 0-150m depth
        if distance_from_coast < 0.8:
            depth = -50 - (distance_from_coast / 0.8) * 100
        # Shelf edge: 150-250m
        elif distance_from_coast < 2.0:
            depth = -150 - ((distance_from_coast - 0.8) / 1.2) * 100
        # Continental slope: 250-1000m
        elif distance_from_coast < 5.0:
            depth = -250 - ((distance_from_coast - 2.0) / 3.0) * 750
        # Abyssal plain: >1000m
        else:
            depth = -1000 - (distance_from_coast - 5.0) * 100

        # Add small variability
        depth += math.sin(lat * 10 + lng * 10) * 50

        return depth

    @staticmethod
    def identify_shelf_break(depth_grid: List[List[float]], lat_list: List[float],
                            lng_list: List[float]) -> List[Dict]:
        """
        Identify shelf break regions (depth transition from shelf to slope)
        Important for PFZ clustering - fish aggregate at shelf edges

        Args:
            depth_grid: 2D array of depths (negative values)
            lat_list: Latitude grid
            lng_list: Longitude grid

        Returns:
            List of shelf break points: [{"lat": float, "lng": float, "depth": float, ...}, ...]
        """
        shelf_break_points = []

        for i in range(1, len(lat_list) - 1):
            for j in range(1, len(lng_list) - 1):
                current_depth = abs(depth_grid[i][j])

                # Check if this point is at shelf edge (rapid depth change)
                # Look at neighboring cells
                neighbor_depths = [
                    abs(depth_grid[i-1][j]),
                    abs(depth_grid[i+1][j]),
                    abs(depth_grid[i][j-1]),
                    abs(depth_grid[i][j+1]),
                ]

                # Shelf break: steep gradient
                depth_gradients = [abs(nd - current_depth) for nd in neighbor_depths]
                max_gradient = max(depth_gradients)

                if max_gradient > 80:  # Significant depth change
                    if 150 <= current_depth <= 250:  # Within shelf edge zone
                        shelf_break_points.append({
                            "lat": lat_list[i],
                            "lng": lng_list[j],
                            "depth": -current_depth,
                            "gradient": max_gradient,
                        })

        return shelf_break_points

    @staticmethod
    def get_suitable_fishing_depths(lat_min: float, lat_max: float, lng_min: float, lng_max: float
                                   ) -> Dict:
        """
        Get regions within suitable fishing depth range

        Args:
            lat_min, lat_max, lng_min, lng_max: Bounding box

        Returns:
            Dict with depth statistics and suitable regions
        """
        import numpy as np

        resolution = 0.25
        lats = np.arange(lat_min, lat_max + resolution, resolution)
        lngs = np.arange(lng_min, lng_max + resolution, resolution)

        suitable_points = []
        depth_stats = {"min": 0, "max": 0, "mean": 0, "count_suitable": 0}

        all_depths = []

        for lat in lats:
            for lng in lngs:
                depth = GEBCOClient.get_depth_at_point(lat, lng)
                all_depths.append(abs(depth))

                # Suitable fishing depth: 30-300m (most species)
                if 30 <= abs(depth) <= 300:
                    suitable_points.append({
                        "lat": round(lat, 2),
                        "lng": round(lng, 2),
                        "depth": depth,
                    })

        if all_depths:
            depth_stats["min"] = -max(all_depths)
            depth_stats["max"] = -min(all_depths)
            depth_stats["mean"] = -np.mean(all_depths)
            depth_stats["count_suitable"] = len(suitable_points)

        return {
            "depth_stats": depth_stats,
            "suitable_points": suitable_points,
            "suitable_count": len(suitable_points),
            "total_grid_points": len(lats) * len(lngs),
        }

    @staticmethod
    def _generate_mock_bathymetry(lat_min: float, lat_max: float, lng_min: float, lng_max: float
                                 ) -> Dict:
        """
        Generate realistic mock bathymetry for Maharashtra EEZ

        Pattern:
        - Shallow continental shelf near coast (0-150m)
        - Shelf edge/break (150-250m) - important for fishing
        - Continental slope (250-1000m)
        - Abyssal plain (>1000m) further offshore
        """
        import numpy as np

        resolution = 0.25
        lats = np.arange(lat_min, lat_max + resolution, resolution)
        lngs = np.arange(lng_min, lng_max + resolution, resolution)

        depth_grid = np.zeros((len(lats), len(lngs)))

        for i, lat in enumerate(lats):
            for j, lng in enumerate(lngs):
                # Get depth at this point
                depth = GEBCOClient.get_depth_at_point(lat, lng)

                # Add realistic small-scale topographic features
                # Ridge/slope effects
                ridge_effect = 30 * np.sin(lng * 20) * np.cos(lat * 15)
                canyon_effect = -40 * np.exp(-((lng - 71.5) ** 2 + (lat - 17.5) ** 2) / 0.5)

                depth_grid[i, j] = depth + ridge_effect + canyon_effect

        return {
            "source": "GEBCO_2024_MOCK",
            "resolution_km": GEBCOClient.RESOLUTION_KM,
            "depth": depth_grid.tolist(),  # Negative values (below sea level)
            "lat": lats.tolist(),
            "lng": lngs.tolist(),
            "unit": "meters",
            "convention": "negative = below sea level",
        }

    @staticmethod
    def get_shelf_statistics(lat_min: float, lat_max: float, lng_min: float, lng_max: float
                            ) -> Dict:
        """
        Get statistics about continental shelf in region

        Returns:
            Dict with shelf characteristics useful for PFZ analysis
        """
        import numpy as np

        resolution = 0.5
        lats = np.arange(lat_min, lat_max + resolution, resolution)
        lngs = np.arange(lng_min, lng_max + resolution, resolution)

        shelf_area = 0  # Points in 20-200m range
        slope_area = 0  # Points in 200-1000m range
        deep_area = 0   # Points >1000m

        for lat in lats:
            for lng in lngs:
                depth = abs(GEBCOClient.get_depth_at_point(lat, lng))

                if 20 <= depth <= 200:
                    shelf_area += 1
                elif 200 < depth <= 1000:
                    slope_area += 1
                elif depth > 1000:
                    deep_area += 1

        total = shelf_area + slope_area + deep_area

        return {
            "region": f"({lat_min}-{lat_max}°N, {lng_min}-{lng_max}°E)",
            "shelf_percent": round(100 * shelf_area / total, 1) if total > 0 else 0,
            "slope_percent": round(100 * slope_area / total, 1) if total > 0 else 0,
            "deep_percent": round(100 * deep_area / total, 1) if total > 0 else 0,
            "fishing_relevance": "High" if shelf_area > slope_area else "Moderate",
        }

    @staticmethod
    def get_status() -> Dict:
        """Check GEBCO data availability"""
        return {
            "data_source": GEBCOClient.DATA_SOURCE,
            "resolution": f"{GEBCOClient.DATA_RESOLUTION_ARCSEC} arc-seconds (~{GEBCOClient.RESOLUTION_KM} km)",
            "cache_dir": GEBCOClient.CACHE_DIR,
            "status": "Ready (mock mode)",
        }


if __name__ == "__main__":
    client = GEBCOClient()

    lat_min, lat_max = 16.0, 20.0
    lng_min, lng_max = 70.0, 73.0

    print("Testing GEBCO Client (Mock Mode)")
    print("=" * 50)

    # Fetch bathymetry
    bathy = GEBCOClient.fetch_bathymetry(lat_min, lat_max, lng_min, lng_max)
    print(f"[OK] Bathymetry: {len(bathy['depth'])} x {len(bathy['depth'][0])} grid")
    print(f"   Source: {bathy['source']}, Resolution: {bathy['resolution_km']}km")

    # Get suitable depths
    suitable = GEBCOClient.get_suitable_fishing_depths(lat_min, lat_max, lng_min, lng_max)
    print(f"[OK] Suitable fishing depths: {suitable['suitable_count']} of {suitable['total_grid_points']} points")

    # Get shelf statistics
    stats = GEBCOClient.get_shelf_statistics(lat_min, lat_max, lng_min, lng_max)
    print(f"[OK] Shelf Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")

    # Test point depth lookup
    test_lat, test_lng = 17.5, 71.5
    depth = GEBCOClient.get_depth_at_point(test_lat, test_lng)
    print(f"\n[OK] Sample point ({test_lat}, {test_lng}): {depth}m depth")

    print(f"\n[DATA] Status:")
    status = GEBCOClient.get_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
