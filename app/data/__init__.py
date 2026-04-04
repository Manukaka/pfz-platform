"""
SAMUDRA AI Data Module
डेटा संग्रह - समुद्र अवलोकन

Unified data collection from multiple oceanographic and meteorological sources:
- CMEMS (Copernicus): SST, currents, chlorophyll, SSH
- NASA: Satellite SST, altimetry, ocean color, wind stress
- ECMWF: Wind, pressure, temperature, wave height
- GEBCO: Bathymetry, shelf topology

All clients support mock data generation for development
"""

from .cmems_client import CMEMSClient
from .nasa_client import NASAClient
from .ecmwf_client import ECMWFClient
from .gebco_client import GEBCOClient

__all__ = [
    "CMEMSClient",
    "NASAClient",
    "ECMWFClient",
    "GEBCOClient",
]
