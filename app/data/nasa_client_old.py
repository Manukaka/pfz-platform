"""
SAMUDRA AI — NASA Data Client
नासा उपग्रह डेटा - समुद्र अवलोकन

Fetches satellite data from NASA sources:
- Sea Surface Height Altimetry (SSHA)
- Satellite Sea Surface Temperature
- Ocean Color data
- Wind stress from satellites

Reference: https://oceandata.sci.gsfc.nasa.gov/
"""

from datetime import datetime, timedelta
import math
from typing import Dict, List, Optional
import json


class NASAClient:
    """NASA oceanographic satellite data client"""

    # NASA OceanColor and ASDC API endpoints
    API_ENDPOINTS = {
        "oceancolor": "https://oceandata.sci.gsfc.nasa.gov/cgi/getfile/",
        "nrt": "https://oceandata.sci.gsfc.nasa.gov/cgi/nrt.cgi",
    }

    # Required NASA API key for DAAC access
    API_KEY = None

    # Cache settings
    CACHE_DIR = "data/cache/nasa"
    CACHE_TTL_HOURS = 24

    def __init__(self, api_key: str = None):
        """
        Initialize NASA client with optional API key

        Args:
            api_key: NASA DAAC API key for authenticated access
        """
        if api_key:
            NASAClient.API_KEY = api_key

    @staticmethod
    def fetch_sst(lat_min: float, lat_max: float, lng_min: float, lng_max: float,
                  date: datetime = None) -> Optional[Dict]:
        """
        Fetch Sea Surface Temperature from NASA satellites
        (MODIS-Aqua, MODIS-Terra composite)

        Args:
            lat_min, lat_max, lng_min, lng_max: Bounding box
            date: Date for data (4km resolution, daily)

        Returns:
            Dict with SST grid: {"date": str, "sst": 2D array, "lat": list, "lng": list}
        """
        if date is None:
            date = datetime.utcnow()

        # Mock data for development
        return NASAClient._generate_mock_sst(lat_min, lat_max, lng_min, lng_max, date)

    @staticmethod
    def fetch_ssha(lat_min: float, lat_max: float, lng_min: float, lng_max: float,
                   date: datetime = None) -> Optional[Dict]:
        """
        Fetch Sea Surface Height Anomaly from satellite altimetry
        (Jason-3, Sentinel-6, SARAL/AltiKa combined)

        Args:
            lat_min, lat_max, lng_min, lng_max: Bounding box
            date: Date for data (25km resolution, multi-mission merged)

        Returns:
            Dict with SSHA grid: {"date": str, "ssha": 2D array, ...}
        """
        if date is None:
            date = datetime.utcnow()

        return NASAClient._generate_mock_ssha(lat_min, lat_max, lng_min, lng_max, date)

    @staticmethod
    def fetch_rrs(lat_min: float, lat_max: float, lng_min: float, lng_max: float,
                  wavelength: int = 671,  # Red channel (nm)
                  date: datetime = None) -> Optional[Dict]:
        """
        Fetch Remote Sensing Reflectance (ocean color)
        Useful for estimating chlorophyll and water properties

        Args:
            lat_min, lat_max, lng_min, lng_max: Bounding box
            wavelength: Wavelength in nm (standard: 412, 443, 469, 488, 531, 551, 671)
            date: Date for data

        Returns:
            Dict with reflectance grid: {"date": str, "rrs": 2D array, ...}
        """
        if date is None:
            date = datetime.utcnow()

        return NASAClient._generate_mock_rrs(lat_min, lat_max, lng_min, lng_max, date, wavelength)

    @staticmethod
    def fetch_wind_stress(lat_min: float, lat_max: float, lng_min: float, lng_max: float,
                         date: datetime = None) -> Optional[Dict]:
        """
        Fetch wind stress from satellite data
        (ASCAT scatterometer wind stress)

        Args:
            lat_min, lat_max, lng_min, lng_max: Bounding box
            date: Date for data

        Returns:
            Dict with wind stress components: {"date": str, "tau_x": 2D, "tau_y": 2D, ...}
        """
        if date is None:
            date = datetime.utcnow()

        return NASAClient._generate_mock_wind_stress(lat_min, lat_max, lng_min, lng_max, date)

    @staticmethod
    def _generate_mock_sst(lat_min: float, lat_max: float, lng_min: float, lng_max: float,
                          date: datetime) -> Dict:
        """
        Generate mock MODIS SST data (4km resolution)
        """
        import numpy as np

        resolution = 0.05  # Finer than CMEMS (4km ~ 0.04°)
        lats = np.arange(lat_min, lat_max + resolution, resolution)
        lngs = np.arange(lng_min, lng_max + resolution, resolution)

        sst_grid = np.zeros((len(lats), len(lngs)))

        for i, lat in enumerate(lats):
            for j, lng in enumerate(lngs):
                # Base gradient
                base = 24.0 + (lat - lat_min) * 0.4

                # Monsoon effect
                if 6 <= date.month <= 9:
                    factor = 0.75
                else:
                    factor = 1.0

                # Thermal fronts with sharper gradients than CMEMS
                distance_from_coast = max(0, lng - 72.5)
                if distance_from_coast < 1.5:
                    front = 2.0 * math.exp(-(distance_from_coast ** 2) / 0.3)
                else:
                    front = 0

                # Mesoscale features
                noise = 0.3 * np.sin(lat * 20 + lng * 20 + date.day)

                sst_grid[i, j] = base * factor + front + noise

        return {
            "date": date.strftime("%Y-%m-%d"),
            "sst": sst_grid.tolist(),
            "lat": lats.tolist(),
            "lng": lngs.tolist(),
            "resolution_km": 4,
            "source": "NASA_MODIS_MOCK",
        }

    @staticmethod
    def _generate_mock_ssha(lat_min: float, lat_max: float, lng_min: float, lng_max: float,
                           date: datetime) -> Dict:
        """
        Generate mock satellite altimetry SSHA data
        """
        import numpy as np

        resolution = 0.25  # 25km typical resolution
        lats = np.arange(lat_min, lat_max + resolution, resolution)
        lngs = np.arange(lng_min, lng_max + resolution, resolution)

        ssha_grid = np.zeros((len(lats), len(lngs)))

        for i, lat in enumerate(lats):
            for j, lng in enumerate(lngs):
                # Eddy patterns (cyclonic = negative SSHA)
                # Primary cyclone
                dist1 = math.sqrt((lat - 17.0) ** 2 + (lng - 70.0) ** 2)
                ssha_grid[i, j] = -0.20 * math.exp(-(dist1 ** 2) / 0.4)

                # Secondary anticyclone
                dist2 = math.sqrt((lat - 18.5) ** 2 + (lng - 71.5) ** 2)
                ssha_grid[i, j] += 0.12 * math.exp(-(dist2 ** 2) / 0.3)

                # Large-scale trend
                ssha_grid[i, j] += 0.05 * (lat - lat_min) / (lat_max - lat_min)

                # Noise
                ssha_grid[i, j] += np.random.random() * 0.03 - 0.015

        return {
            "date": date.strftime("%Y-%m-%d"),
            "ssha": ssha_grid.tolist(),
            "lat": lats.tolist(),
            "lng": lngs.tolist(),
            "unit": "meters",
            "resolution_km": 25,
            "source": "NASA_ALTIMETRY_MOCK",
        }

    @staticmethod
    def _generate_mock_rrs(lat_min: float, lat_max: float, lng_min: float, lng_max: float,
                          date: datetime, wavelength: int) -> Dict:
        """
        Generate mock ocean color remote sensing reflectance
        """
        import numpy as np

        resolution = 0.05  # 1km MODIS resolution
        lats = np.arange(lat_min, lat_max + resolution, resolution)
        lngs = np.arange(lng_min, lng_max + resolution, resolution)

        rrs_grid = np.zeros((len(lats), len(lngs)))

        for i, lat in enumerate(lats):
            for j, lng in enumerate(lngs):
                # Wavelength-dependent reflectance
                # Coastal waters typically have higher reflectance
                distance_from_coast = max(0, lng - 72.5)

                base_rrs = 0.005 + 0.005 / (1.0 + distance_from_coast)

                # Red channels (671nm) lower in productive waters (more chlorophyll absorption)
                if wavelength > 600:
                    factor = 0.8 if 6 <= date.month <= 9 else 0.95
                # Blue channels (400-500nm) higher
                else:
                    factor = 1.2 if 6 <= date.month <= 9 else 0.9

                # Chlorophyll correlation
                if 6 <= date.month <= 9:
                    chl_factor = 2.0
                else:
                    chl_factor = 0.6

                rrs_grid[i, j] = base_rrs * factor * chl_factor + np.random.random() * 0.001

        return {
            "date": date.strftime("%Y-%m-%d"),
            "rrs": rrs_grid.tolist(),
            "wavelength_nm": wavelength,
            "lat": lats.tolist(),
            "lng": lngs.tolist(),
            "unit": "sr^-1",
            "source": "NASA_OCEANCOLOR_MOCK",
        }

    @staticmethod
    def _generate_mock_wind_stress(lat_min: float, lat_max: float, lng_min: float, lng_max: float,
                                  date: datetime) -> Dict:
        """
        Generate mock wind stress data from satellite scatterometer
        """
        import numpy as np

        resolution = 0.25  # 25km resolution
        lats = np.arange(lat_min, lat_max + resolution, resolution)
        lngs = np.arange(lng_min, lng_max + resolution, resolution)

        tau_x = np.zeros((len(lats), len(lngs)))  # Zonal (eastward)
        tau_y = np.zeros((len(lats), len(lngs)))  # Meridional (northward)

        for i, lat in enumerate(lats):
            for j, lng in enumerate(lngs):
                # Monsoon wind patterns
                if 6 <= date.month <= 9:  # Southwest monsoon - strong westerlies
                    # Strong southwesterly winds
                    tau_x_base = -0.15  # Westward
                    tau_y_base = -0.08  # Southward
                elif 10 <= date.month <= 5:  # Northeast monsoon
                    # Moderate northeasterly winds
                    tau_x_base = 0.08  # Eastward
                    tau_y_base = 0.12  # Northward
                else:  # Transition months
                    tau_x_base = 0.01
                    tau_y_base = 0.02

                # Latitude-dependent modulation
                lat_factor = 1.0 + 0.2 * (lat - lat_min) / (lat_max - lat_min)

                # Add mesoscale wind variability
                wind_var_x = 0.05 * np.sin(lat * 10 + lng * 10 + date.day)
                wind_var_y = 0.05 * np.cos(lat * 10 + lng * 10 + date.day)

                tau_x[i, j] = tau_x_base * lat_factor + wind_var_x
                tau_y[i, j] = tau_y_base * lat_factor + wind_var_y

        return {
            "date": date.strftime("%Y-%m-%d"),
            "tau_x": tau_x.tolist(),  # Zonal wind stress (N/m²)
            "tau_y": tau_y.tolist(),  # Meridional wind stress (N/m²)
            "lat": lats.tolist(),
            "lng": lngs.tolist(),
            "unit": "N/m²",
            "resolution_km": 25,
            "source": "NASA_SCATTEROMETER_MOCK",
        }

    @staticmethod
    def get_status() -> Dict:
        """Check NASA data service status"""
        return {
            "authenticated": NASAClient.API_KEY is not None,
            "endpoints": NASAClient.API_ENDPOINTS,
            "cache_dir": NASAClient.CACHE_DIR,
            "status": "Ready (mock mode)" if NASAClient.API_KEY is None else "Connected",
        }


if __name__ == "__main__":
    client = NASAClient()

    lat_min, lat_max = 16.0, 20.0
    lng_min, lng_max = 70.0, 73.0

    print("Testing NASA Client (Mock Mode)")
    print("=" * 50)

    sst = NASAClient.fetch_sst(lat_min, lat_max, lng_min, lng_max)
    print(f"[OK] MODIS SST: {len(sst['sst'])} x {len(sst['sst'][0])} grid (4km)")

    ssha = NASAClient.fetch_ssha(lat_min, lat_max, lng_min, lng_max)
    print(f"[OK] Altimetry SSHA: {len(ssha['ssha'])} x {len(ssha['ssha'][0])} grid (25km)")

    rrs = NASAClient.fetch_rrs(lat_min, lat_max, lng_min, lng_max, wavelength=671)
    print(f"[OK] Ocean Color RRS: {len(rrs['rrs'])} x {len(rrs['rrs'][0])} grid")

    wind = NASAClient.fetch_wind_stress(lat_min, lat_max, lng_min, lng_max)
    print(f"[OK] Wind Stress: {len(wind['tau_x'])} x {len(wind['tau_x'][0])} grid")

    print(f"\n[DATA] Status:")
    status = NASAClient.get_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
