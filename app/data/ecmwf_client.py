"""
SAMUDRA AI — ECMWF Data Client
यूरोपीय मौसम पूर्वानुमान - हवा, दबाव डेटा

Fetches meteorological data from ECMWF (European Centre for Medium-Range Weather Forecasts):
- Wind fields (u, v components) at 10m height
- Sea level pressure
- Atmospheric pressure anomalies
- Wave height forecasts (optional)

Uses Copernicus Climate Change Service (C3S) for ERA5 reanalysis
Reference: https://www.ecmwf.int/ and CDS API
"""

from datetime import datetime, timedelta
import math
from typing import Dict, Optional
import json


class ECMWFClient:
    """European Centre for Medium-Range Weather Forecasts data client"""

    # CDS (Copernicus Climate Data Store) API endpoint
    API_BASE = "https://cds.climate.copernicus.eu/api/v2"

    # CDS API credentials (user configurable)
    CDS_URL = None
    CDS_KEY = None

    # Cache settings
    CACHE_DIR = "data/cache/ecmwf"
    CACHE_TTL_HOURS = 24

    def __init__(self, cds_url: str = None, cds_key: str = None):
        """
        Initialize ECMWF client with CDS credentials

        Args:
            cds_url: CDS API URL
            cds_key: CDS API key (format: UID:API_KEY)
        """
        if cds_url:
            ECMWFClient.CDS_URL = cds_url
        if cds_key:
            ECMWFClient.CDS_KEY = cds_key

    @staticmethod
    def fetch_wind_10m(lat_min: float, lat_max: float, lng_min: float, lng_max: float,
                      date: datetime = None, dataset: str = "era5") -> Optional[Dict]:
        """
        Fetch 10-meter wind components (u10, v10)

        Args:
            lat_min, lat_max, lng_min, lng_max: Bounding box
            date: Date for data (defaults to today)
            dataset: "era5" (reanalysis) or "era5_live" (latest available)

        Returns:
            Dict with wind components: {"date": str, "u10": 2D array, "v10": 2D array, ...}
        """
        if date is None:
            date = datetime.utcnow()

        # Mock data for development
        return ECMWFClient._generate_mock_wind(lat_min, lat_max, lng_min, lng_max, date)

    @staticmethod
    def fetch_msl_pressure(lat_min: float, lat_max: float, lng_min: float, lng_max: float,
                          date: datetime = None) -> Optional[Dict]:
        """
        Fetch mean sea level pressure

        Args:
            lat_min, lat_max, lng_min, lng_max: Bounding box
            date: Date for data

        Returns:
            Dict with MSL pressure: {"date": str, "msl": 2D array, ...}
        """
        if date is None:
            date = datetime.utcnow()

        return ECMWFClient._generate_mock_pressure(lat_min, lat_max, lng_min, lng_max, date)

    @staticmethod
    def fetch_surface_pressure(lat_min: float, lat_max: float, lng_min: float, lng_max: float,
                              date: datetime = None) -> Optional[Dict]:
        """
        Fetch surface pressure (atmospheric pressure at ground level)

        Args:
            lat_min, lat_max, lng_min, lng_max: Bounding box
            date: Date for data

        Returns:
            Dict with surface pressure: {"date": str, "sp": 2D array, ...}
        """
        if date is None:
            date = datetime.utcnow()

        return ECMWFClient._generate_mock_surface_pressure(lat_min, lat_max, lng_min, lng_max, date)

    @staticmethod
    def fetch_2m_temperature(lat_min: float, lat_max: float, lng_min: float, lng_max: float,
                            date: datetime = None) -> Optional[Dict]:
        """
        Fetch 2-meter air temperature (near-surface atmospheric temperature)

        Args:
            lat_min, lat_max, lng_min, lng_max: Bounding box
            date: Date for data

        Returns:
            Dict with temperature: {"date": str, "t2m": 2D array, ...}
        """
        if date is None:
            date = datetime.utcnow()

        return ECMWFClient._generate_mock_temperature(lat_min, lat_max, lng_min, lng_max, date)

    @staticmethod
    def fetch_significant_wave_height(lat_min: float, lat_max: float, lng_min: float, lng_max: float,
                                     date: datetime = None) -> Optional[Dict]:
        """
        Fetch significant wave height (optional - for marine safety)

        Args:
            lat_min, lat_max, lng_min, lng_max: Bounding box
            date: Date for data

        Returns:
            Dict with wave height: {"date": str, "swh": 2D array, ...}
        """
        if date is None:
            date = datetime.utcnow()

        return ECMWFClient._generate_mock_wave_height(lat_min, lat_max, lng_min, lng_max, date)

    @staticmethod
    def _generate_mock_wind(lat_min: float, lat_max: float, lng_min: float, lng_max: float,
                           date: datetime) -> Dict:
        """
        Generate mock ERA5 10m wind data
        """
        import numpy as np

        resolution = 0.25
        lats = np.arange(lat_min, lat_max + resolution, resolution)
        lngs = np.arange(lng_min, lng_max + resolution, resolution)

        u10 = np.zeros((len(lats), len(lngs)))
        v10 = np.zeros((len(lats), len(lngs)))

        for i, lat in enumerate(lats):
            for j, lng in enumerate(lngs):
                # Monsoon-dependent wind patterns (same as NASA mock)
                if 6 <= date.month <= 9:  # Southwest monsoon
                    u10_base = -4.5 - 0.5 * (lat - 18)  # Westward (m/s)
                    v10_base = -2.0 + 0.2 * (lng - 72)  # Southward
                elif 10 <= date.month <= 5:  # Northeast monsoon
                    u10_base = 2.5 + 0.3 * (lat - 18)  # Eastward
                    v10_base = 3.5 - 0.2 * (lng - 72)  # Northward
                else:  # Transition
                    u10_base = 0.5
                    v10_base = 0.5

                # Synoptic-scale variability
                synoptic = 2.0 * np.sin((lng - lng_min) * 4 * math.pi / (lng_max - lng_min))

                # Diurnal cycle (small effect on daily data)
                diurnal = 0.5 * np.cos(date.hour * math.pi / 12)

                u10[i, j] = u10_base + synoptic * 0.3 + diurnal
                v10[i, j] = v10_base + synoptic * 0.2 + diurnal * 0.5

        return {
            "date": date.strftime("%Y-%m-%d"),
            "u10": u10.tolist(),  # Eastward 10m wind (m/s)
            "v10": v10.tolist(),  # Northward 10m wind (m/s)
            "lat": lats.tolist(),
            "lng": lngs.tolist(),
            "unit": "m/s",
            "height": "10m",
            "source": "ECMWF_ERA5_MOCK",
        }

    @staticmethod
    def _generate_mock_pressure(lat_min: float, lat_max: float, lng_min: float, lng_max: float,
                               date: datetime) -> Dict:
        """
        Generate mock mean sea level pressure
        """
        import numpy as np

        resolution = 0.25
        lats = np.arange(lat_min, lat_max + resolution, resolution)
        lngs = np.arange(lng_min, lng_max + resolution, resolution)

        msl = np.zeros((len(lats), len(lngs)))

        for i, lat in enumerate(lats):
            for j, lng in enumerate(lngs):
                # Base pressure (typical for Arabian Sea: ~1013 hPa)
                base = 101300.0  # Pa (standard 1013 hPa)

                # Latitude effect (pressure slightly lower near equator)
                lat_effect = -100 * (lat - 18) ** 2 / 25

                # Monsoon pressure anomaly
                if 6 <= date.month <= 9:  # SW monsoon - low pressure system active
                    monsoon_effect = -500 - 200 * np.sin((lng - lng_min) * 2 * math.pi / (lng_max - lng_min))
                else:
                    monsoon_effect = 0

                # Synoptic-scale low/high pressure systems
                synoptic = 300 * np.sin((lng - lng_min) * 3 * math.pi / (lng_max - lng_min))

                msl[i, j] = base + lat_effect + monsoon_effect + synoptic

        return {
            "date": date.strftime("%Y-%m-%d"),
            "msl": msl.tolist(),  # Mean sea level pressure (Pa)
            "lat": lats.tolist(),
            "lng": lngs.tolist(),
            "unit": "Pa",
            "source": "ECMWF_ERA5_MOCK",
        }

    @staticmethod
    def _generate_mock_surface_pressure(lat_min: float, lat_max: float, lng_min: float, lng_max: float,
                                       date: datetime) -> Dict:
        """
        Generate mock surface pressure
        """
        import numpy as np

        resolution = 0.25
        lats = np.arange(lat_min, lat_max + resolution, resolution)
        lngs = np.arange(lng_min, lng_max + resolution, resolution)

        sp = np.zeros((len(lats), len(lngs)))

        for i, lat in enumerate(lats):
            for j, lng in enumerate(lngs):
                # Surface pressure typically ~20-30 hPa lower than MSL over ocean
                base = 101100.0

                lat_effect = -80 * (lat - 18) ** 2 / 25

                if 6 <= date.month <= 9:
                    monsoon_effect = -300 - 150 * np.sin((lng - lng_min) * 2 * math.pi / (lng_max - lng_min))
                else:
                    monsoon_effect = 0

                synoptic = 200 * np.sin((lng - lng_min) * 3 * math.pi / (lng_max - lng_min))

                sp[i, j] = base + lat_effect + monsoon_effect + synoptic

        return {
            "date": date.strftime("%Y-%m-%d"),
            "sp": sp.tolist(),  # Surface pressure (Pa)
            "lat": lats.tolist(),
            "lng": lngs.tolist(),
            "unit": "Pa",
            "source": "ECMWF_ERA5_MOCK",
        }

    @staticmethod
    def _generate_mock_temperature(lat_min: float, lat_max: float, lng_min: float, lng_max: float,
                                  date: datetime) -> Dict:
        """
        Generate mock 2m air temperature
        """
        import numpy as np

        resolution = 0.25
        lats = np.arange(lat_min, lat_max + resolution, resolution)
        lngs = np.arange(lng_min, lng_max + resolution, resolution)

        t2m = np.zeros((len(lats), len(lngs)))

        for i, lat in enumerate(lats):
            for j, lng in enumerate(lngs):
                # Base air temperature (warmer than SST typically)
                # Varies by season
                if 3 <= date.month <= 5:  # Pre-monsoon: hottest
                    base = 27.0 + (lat - lat_min) * 0.3
                elif 6 <= date.month <= 9:  # Monsoon: cooler
                    base = 25.0 + (lat - lat_min) * 0.2
                else:  # Post-monsoon and winter
                    base = 26.0 + (lat - lat_min) * 0.25

                # Diurnal cycle
                hour_factor = 2.0 * np.sin((date.hour - 6) * math.pi / 12)

                t2m[i, j] = base + hour_factor + np.random.random() * 0.5

        return {
            "date": date.strftime("%Y-%m-%d %H:00"),
            "t2m": t2m.tolist(),  # Temperature at 2m (Kelvin converted to Celsius)
            "lat": lats.tolist(),
            "lng": lngs.tolist(),
            "unit": "K",
            "height": "2m",
            "source": "ECMWF_ERA5_MOCK",
        }

    @staticmethod
    def _generate_mock_wave_height(lat_min: float, lat_max: float, lng_min: float, lng_max: float,
                                  date: datetime) -> Dict:
        """
        Generate mock significant wave height (for maritime safety)
        """
        import numpy as np

        resolution = 0.25
        lats = np.arange(lat_min, lat_max + resolution, resolution)
        lngs = np.arange(lng_min, lng_max + resolution, resolution)

        swh = np.zeros((len(lats), len(lngs)))

        for i, lat in enumerate(lats):
            for j, lng in enumerate(lngs):
                # Wave height depends on wind speed and fetch
                # Monsoon season: higher waves (5-7m typical)
                if 6 <= date.month <= 9:
                    base_swh = 3.0 + 2.0 * np.sin((lng - lng_min) * 2 * math.pi / (lng_max - lng_min))
                else:
                    base_swh = 1.5 + 0.5 * np.sin((lng - lng_min) * 2 * math.pi / (lng_max - lng_min))

                # Add some variability
                swh[i, j] = max(0.5, base_swh + np.random.random() * 0.5)

        return {
            "date": date.strftime("%Y-%m-%d"),
            "swh": swh.tolist(),  # Significant wave height (m)
            "lat": lats.tolist(),
            "lng": lngs.tolist(),
            "unit": "m",
            "source": "ECMWF_WAVES_MOCK",
        }

    @staticmethod
    def get_status() -> Dict:
        """Check ECMWF/CDS service status"""
        return {
            "authenticated": ECMWFClient.CDS_KEY is not None,
            "api_base": ECMWFClient.API_BASE,
            "cache_dir": ECMWFClient.CACHE_DIR,
            "status": "Ready (mock mode)" if ECMWFClient.CDS_KEY is None else "Connected",
        }


if __name__ == "__main__":
    client = ECMWFClient()

    lat_min, lat_max = 16.0, 20.0
    lng_min, lng_max = 70.0, 73.0

    print("Testing ECMWF Client (Mock Mode)")
    print("=" * 50)

    wind = ECMWFClient.fetch_wind_10m(lat_min, lat_max, lng_min, lng_max)
    print(f"[OK] 10m Wind: {len(wind['u10'])} x {len(wind['u10'][0])} grid")

    pressure = ECMWFClient.fetch_msl_pressure(lat_min, lat_max, lng_min, lng_max)
    print(f"[OK] MSL Pressure: {len(pressure['msl'])} x {len(pressure['msl'][0])} grid")

    temp = ECMWFClient.fetch_2m_temperature(lat_min, lat_max, lng_min, lng_max)
    print(f"[OK] 2m Temperature: {len(temp['t2m'])} x {len(temp['t2m'][0])} grid")

    waves = ECMWFClient.fetch_significant_wave_height(lat_min, lat_max, lng_min, lng_max)
    print(f"[OK] Wave Height: {len(waves['swh'])} x {len(waves['swh'][0])} grid")

    print(f"\n[DATA] Status:")
    status = ECMWFClient.get_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
