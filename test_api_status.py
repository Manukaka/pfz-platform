#!/usr/bin/env python3
"""
API Status Checker - Test if external APIs are actually working
Tests real API connectivity and returns honest status
"""

import os
from dotenv import load_dotenv
import requests
from datetime import datetime

load_dotenv()

def check_cmems_api():
    """Test CMEMS API connectivity"""
    username = os.getenv('CMEMS_USERNAME')
    password = os.getenv('CMEMS_PASSWORD')
    enabled = os.getenv('CMEMS_ENABLED', 'False').lower() == 'true'

    if not enabled:
        return {"status": "disabled", "message": "CMEMS disabled in config"}

    if not username or not password:
        return {"status": "error", "message": "CMEMS credentials not configured"}

    if username == "CHANGE_THIS" or "change" in username.lower():
        return {"status": "error", "message": "CMEMS credentials are placeholder values"}

    # Try to authenticate
    try:
        # Test with CMEMS API
        test_url = "https://data.marine.copernicus.eu/api/datasets"
        response = requests.get(test_url, auth=(username, password), timeout=10)

        if response.status_code == 200:
            return {"status": "ok", "message": "CMEMS API authenticated successfully"}
        elif response.status_code == 401:
            return {"status": "error", "message": "CMEMS authentication failed - invalid credentials"}
        elif response.status_code == 402:
            return {"status": "error", "message": "CMEMS account expired or out of quota"}
        else:
            return {"status": "error", "message": f"CMEMS API returned status {response.status_code}"}
    except requests.Timeout:
        return {"status": "error", "message": "CMEMS API timeout - service may be down"}
    except Exception as e:
        return {"status": "error", "message": f"CMEMS API error: {str(e)}"}

def check_nasa_api():
    """Test NASA API connectivity"""
    api_key = os.getenv('NASA_API_KEY')
    enabled = os.getenv('NASA_ENABLED', 'False').lower() == 'true'

    if not enabled:
        return {"status": "disabled", "message": "NASA API disabled in config"}

    if not api_key or "CHANGE_THIS" in api_key:
        return {"status": "error", "message": "NASA API key not configured"}

    try:
        test_url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}"
        response = requests.get(test_url, timeout=10)

        if response.status_code == 200:
            return {"status": "ok", "message": "NASA API authenticated successfully"}
        elif response.status_code == 403:
            return {"status": "error", "message": "NASA API key invalid or expired"}
        elif response.status_code == 429:
            return {"status": "error", "message": "NASA API rate limit exceeded"}
        else:
            return {"status": "error", "message": f"NASA API returned status {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": f"NASA API error: {str(e)}"}

def check_ecmwf_api():
    """Test ECMWF API connectivity"""
    api_key = os.getenv('ECMWF_API_KEY')
    enabled = os.getenv('ECMWF_ENABLED', 'False').lower() == 'true'

    if not enabled:
        return {"status": "disabled", "message": "ECMWF API disabled in config"}

    if not api_key or "CHANGE_THIS" in api_key:
        return {"status": "error", "message": "ECMWF API key not configured"}

    # ECMWF uses UID:API_KEY format
    if ':' not in api_key:
        return {"status": "error", "message": "ECMWF API key format invalid (needs UID:KEY)"}

    return {"status": "warning", "message": "ECMWF API not fully tested (requires CDS client)"}

def check_gebco_api():
    """Test GEBCO API (always free, no auth needed)"""
    enabled = os.getenv('GEBCO_ENABLED', 'True').lower() == 'true'

    if not enabled:
        return {"status": "disabled", "message": "GEBCO disabled in config"}

    try:
        # GEBCO has a test WMS endpoint
        test_url = "https://www.gebco.net/data_and_products/gebco_web_services/web_map_service/mapserv"
        response = requests.get(test_url, timeout=10, params={"request": "GetCapabilities"})

        if response.status_code == 200:
            return {"status": "ok", "message": "GEBCO API accessible"}
        else:
            return {"status": "warning", "message": f"GEBCO returned status {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": f"GEBCO error: {str(e)}"}

def main():
    print("="*70)
    print("API STATUS CHECK - Testing External Data Sources")
    print("="*70)
    print()

    apis = {
        "CMEMS (Copernicus Marine)": check_cmems_api(),
        "NASA Earth Data": check_nasa_api(),
        "ECMWF (Climate Data Store)": check_ecmwf_api(),
        "GEBCO (Bathymetry)": check_gebco_api()
    }

    working_count = 0
    for name, status in apis.items():
        emoji = "[OK]" if status["status"] == "ok" else "[WARN]" if status["status"] == "warning" else "[FAIL]"
        print(f"{emoji} {name}: {status['message']}")
        if status["status"] == "ok":
            working_count += 1

    print()
    print("="*70)
    print(f"SUMMARY: {working_count}/4 APIs working")
    print()

    if working_count == 0:
        print("WARNING: No external APIs are working!")
        print("The system will NOT be able to provide real PFZ data.")
        print("Please configure API credentials in .env file.")
        print()
        print("To fix:")
        print("1. Register for CMEMS: https://data.marine.copernicus.eu/")
        print("2. Get NASA API key: https://api.nasa.gov/")
        print("3. Get ECMWF key: https://cds.climate.copernicus.eu/")
        return 1
    elif working_count < 2:
        print(f"LIMITED: Only {working_count} API(s) working")
        print("Results will be partial and may not be accurate.")
        return 2
    else:
        print(f"OPERATIONAL: {working_count} APIs are working")
        return 0

if __name__ == "__main__":
    exit(main())
