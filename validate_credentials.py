#!/usr/bin/env python3
"""
SAMUDRA AI — Credential Validator

Validates that API credentials work before deploying
Useful for troubleshooting authentication issues
"""

import os
import sys
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ANSI colors
class C:
    H = '\033[95m'
    B = '\033[94m'
    C = '\033[96m'
    G = '\033[92m'
    Y = '\033[93m'
    R = '\033[91m'
    E = '\033[0m'
    BOLD = '\033[1m'

def print_header(title):
    print(f"\n{C.BOLD}{C.H}{'='*70}{C.E}")
    print(f"{C.BOLD}{C.H}{title:^70}{C.E}")
    print(f"{C.BOLD}{C.H}{'='*70}{C.E}\n")

def test_cmems():
    """Test CMEMS credentials"""
    print(f"{C.C}Testing CMEMS...{C.E}")

    username = os.environ.get('CMEMS_USERNAME')
    password = os.environ.get('CMEMS_PASSWORD')

    if not username or not password:
        print(f"{C.Y}⚠️  CMEMS credentials not found in environment{C.E}")
        print(f"   Set: CMEMS_USERNAME and CMEMS_PASSWORD")
        return False

    try:
        from app.data.cmems_client import CMEMSClient

        # Initialize client
        client = CMEMSClient(username, password)
        print(f"{C.G}✅ CMEMS client initialized{C.E}")

        # Test a fetch
        test_date = datetime.utcnow() - timedelta(days=1)  # Yesterday (data available)
        sst = CMEMSClient.fetch_sst(14, 21, 67, 74.5, test_date)

        if sst and "grid" in sst:
            print(f"{C.G}✅ CMEMS SST data retrieved successfully{C.E}")
            print(f"   Source: {sst.get('source', 'unknown')}")
            print(f"   Date: {sst.get('date', 'unknown')}")
            return True
        else:
            print(f"{C.R}❌ Failed to fetch SST data{C.E}")
            return False

    except Exception as e:
        print(f"{C.R}❌ CMEMS test failed: {str(e)}{C.E}")
        logger.exception("CMEMS error")
        return False

def test_nasa():
    """Test NASA credentials"""
    print(f"{C.C}Testing NASA...{C.E}")

    api_key = os.environ.get('NASA_API_KEY')

    if not api_key:
        print(f"{C.Y}⚠️  NASA_API_KEY not found in environment{C.E}")
        print(f"   Set: NASA_API_KEY")
        return False

    try:
        from app.data.nasa_client import NASAClient

        # Initialize client
        client = NASAClient(api_key)
        print(f"{C.G}✅ NASA client initialized{C.E}")

        # Test a fetch
        test_date = datetime.utcnow() - timedelta(days=1)
        wind = NASAClient.fetch_wind_stress(14, 21, 67, 74.5, test_date)

        if wind and ("tau_x" in wind or "grid" in wind):
            print(f"{C.G}✅ NASA wind stress data retrieved successfully{C.E}")
            print(f"   Source: {wind.get('source', 'unknown')}")
            print(f"   Date: {wind.get('date', 'unknown')}")
            return True
        else:
            print(f"{C.R}❌ Failed to fetch wind stress data{C.E}")
            return False

    except Exception as e:
        print(f"{C.R}❌ NASA test failed: {str(e)}{C.E}")
        logger.exception("NASA error")
        return False

def test_ecmwf():
    """Test ECMWF credentials"""
    print(f"{C.C}Testing ECMWF...{C.E}")

    api_key = os.environ.get('ECMWF_API_KEY')

    if not api_key:
        print(f"{C.Y}⚠️  ECMWF_API_KEY not found in environment{C.E}")
        print(f"   Set: ECMWF_API_KEY (format: uid:key)")
        return False

    try:
        from app.data.ecmwf_client import ECMWFClient

        # Initialize client
        client = ECMWFClient()
        print(f"{C.G}✅ ECMWF client initialized{C.E}")

        # Test a fetch
        test_date = datetime.utcnow() - timedelta(days=1)
        wind = ECMWFClient.fetch_wind_10m(14, 21, 67, 74.5, test_date)

        if wind and ("u10" in wind or "grid" in wind):
            print(f"{C.G}✅ ECMWF wind data retrieved successfully{C.E}")
            print(f"   Source: {wind.get('source', 'unknown')}")
            print(f"   Date: {wind.get('date', 'unknown')}")
            return True
        else:
            print(f"{C.R}❌ Failed to fetch wind data{C.E}")
            return False

    except Exception as e:
        print(f"{C.R}❌ ECMWF test failed: {str(e)}{C.E}")
        logger.exception("ECMWF error")
        return False

def test_gebco():
    """Test GEBCO (always free)"""
    print(f"{C.C}Testing GEBCO...{C.E}")

    try:
        from app.data.gebco_client import GEBCOClient

        # Test a fetch
        bath = GEBCOClient.fetch_bathymetry(14, 21, 67, 74.5)

        if bath and "grid" in bath:
            print(f"{C.G}✅ GEBCO bathymetry data retrieved successfully{C.E}")
            print(f"   Source: {bath.get('source', 'unknown')}")
            return True
        else:
            print(f"{C.R}❌ Failed to fetch bathymetry data{C.E}")
            return False

    except Exception as e:
        print(f"{C.R}❌ GEBCO test failed: {str(e)}{C.E}")
        logger.exception("GEBCO error")
        return False

def test_aggregator():
    """Test DataAggregator with current credentials"""
    print(f"{C.C}Testing DataAggregator...{C.E}")

    try:
        from app.data.data_aggregator import DataAggregator

        # Initialize
        agg = DataAggregator()
        print(f"{C.G}✅ DataAggregator initialized{C.E}")

        # Fetch complete dataset
        data = DataAggregator.fetch_pfz_data(
            lat_min=14, lat_max=21, lng_min=67, lng_max=74.5
        )

        # Check completeness
        completeness = data["metadata"]["data_quality"]["completeness_percent"]
        print(f"{C.G}✅ Complete dataset fetched{C.E}")
        print(f"   Completeness: {completeness:.1f}%")

        # Show sources
        if data["metadata"]["sources"]:
            print(f"   Sources used:")
            for field, source in data["metadata"]["sources"].items():
                indicator = "✅" if "REAL" in source else "🟡"
                print(f"     {indicator} {field}: {source}")

        return completeness >= 70  # 70% completeness is acceptable

    except Exception as e:
        print(f"{C.R}❌ DataAggregator test failed: {str(e)}{C.E}")
        logger.exception("DataAggregator error")
        return False

def main():
    print_header("SAMUDRA AI — Credential Validator")

    print(f"{C.BOLD}Environment variables loaded:{C.E}")
    print(f"  CMEMS_USERNAME: {'✓' if os.environ.get('CMEMS_USERNAME') else '✗'}")
    print(f"  CMEMS_PASSWORD: {'✓' if os.environ.get('CMEMS_PASSWORD') else '✗'}")
    print(f"  NASA_API_KEY: {'✓' if os.environ.get('NASA_API_KEY') else '✗'}")
    print(f"  ECMWF_API_KEY: {'✓' if os.environ.get('ECMWF_API_KEY') else '✗'}")
    print(f"  GEBCO_ENABLED: {'✓' if os.environ.get('GEBCO_ENABLED') else '✗'}\n")

    results = {}

    # Test each provider
    results['CMEMS'] = test_cmems()
    print()
    results['NASA'] = test_nasa()
    print()
    results['ECMWF'] = test_ecmwf()
    print()
    results['GEBCO'] = test_gebco()
    print()
    results['Aggregator'] = test_aggregator()

    # Summary
    print_header("Validation Summary")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"{C.BOLD}Results: {passed}/{total} tests passed{C.E}\n")

    for provider, success in results.items():
        status = f"{C.G}✅ PASS{C.E}" if success else f"{C.R}❌ FAIL{C.E}"
        print(f"  {provider}: {status}")

    print()

    if passed == total:
        print(f"{C.BOLD}{C.G}🎉 All credentials validated! Ready for deployment.{C.E}")
        return 0
    elif passed >= 3:
        print(f"{C.BOLD}{C.Y}⚠️  Some credentials missing or invalid.{C.E}")
        print(f"   System will use mock data for missing providers.")
        print(f"   See API_SETUP_GUIDE.md for setup instructions.\n")
        return 1
    else:
        print(f"{C.BOLD}{C.R}❌ Multiple credential issues. See above for details.{C.E}\n")
        return 2

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{C.Y}Validation interrupted{C.E}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{C.R}Unexpected error: {e}{C.E}")
        import traceback
        traceback.print_exc()
        sys.exit(2)
