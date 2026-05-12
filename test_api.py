#!/usr/bin/env python3
"""
SAMUDRA AI — Complete API Test Suite

Tests all 13+ endpoints to verify system functionality
Useful for validating setup, debugging issues, and demonstrating capabilities
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any
import sys

# Test configuration
BASE_URL = "http://localhost:5000"
TIMEOUT = 30

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(title: str):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{title:^70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}\n")

def print_test(name: str):
    """Print test name"""
    print(f"{Colors.CYAN}▶ {name}{Colors.ENDC}")

def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}  ✅ {message}{Colors.ENDC}")

def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}  ❌ {message}{Colors.ENDC}")

def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}  ⚠️  {message}{Colors.ENDC}")

def print_info(message: str):
    """Print info message"""
    print(f"{Colors.BLUE}  ℹ️  {message}{Colors.ENDC}")

def test_endpoint(method: str, endpoint: str, data: Dict[str, Any] = None,
                 expected_status: int = 200) -> Dict[str, Any]:
    """Test a single API endpoint"""
    url = f"{BASE_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, timeout=TIMEOUT)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=TIMEOUT)
        else:
            print_error(f"Unknown HTTP method: {method}")
            return None

        if response.status_code == expected_status:
            print_success(f"{method} {endpoint} → {response.status_code}")
            try:
                return response.json()
            except:
                return {"status": "ok", "raw": response.text[:100]}
        else:
            print_error(f"{method} {endpoint} → {response.status_code} (expected {expected_status})")
            print_warning(f"Response: {response.text[:200]}")
            return None

    except requests.exceptions.ConnectionError:
        print_error(f"Connection failed to {BASE_URL}")
        return None
    except requests.exceptions.Timeout:
        print_error(f"Request timeout (>{TIMEOUT}s)")
        return None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None

def run_tests():
    """Run complete test suite"""

    print_header("SAMUDRA AI — API Test Suite")
    print(f"{Colors.BOLD}Testing at: {BASE_URL}{Colors.ENDC}\n")

    # Test 1: Health Check
    print_test("Health & Status Endpoints")
    health = test_endpoint("GET", "/api/health")
    status = test_endpoint("GET", "/api/status")

    if health and status:
        print_info(f"System status: Operational")
        if status.get("data", {}).get("data_sources"):
            for source, state in status["data"]["data_sources"].items():
                print_info(f"  {source}: {state}")

    # Test 2: Data Sources
    print_test("Data Sources Endpoint")
    sources = test_endpoint("GET", "/api/data/sources")
    if sources:
        print_info(f"Available sources: {len(sources)} providers")
        for provider_name, provider_info in sources.items():
            status_str = provider_info.get("status", "unknown")
            print_info(f"  {provider_name}: {status_str}")

    # Test 3: PFZ (Productive Fishing Zone) Endpoints
    print_test("PFZ Zone Detection")
    pfz_payload = {
        "lat_min": 14.0,
        "lat_max": 21.0,
        "lng_min": 67.0,
        "lng_max": 74.5
    }
    pfz_zones = test_endpoint("POST", "/api/pfz/zones", pfz_payload)

    if pfz_zones and pfz_zones.get("zones"):
        num_zones = len(pfz_zones.get("zones", []))
        print_info(f"Found {num_zones} productive fishing zones")
        if num_zones > 0:
            zone = pfz_zones["zones"][0]
            print_info(f"  Zone 1: Lat {zone.get('center_lat', 'N/A')}, Lng {zone.get('center_lng', 'N/A')}")

        # Test zone detail endpoint
        if num_zones > 0:
            zone_id = pfz_zones["zones"][0].get("id", "zone_1")
            print_test("PFZ Zone Detail")
            zone_detail = test_endpoint("GET", f"/api/pfz/zones/{zone_id}")
            if zone_detail:
                print_info(f"Zone {zone_id} details retrieved")

    # Test 4: Lunar Endpoints (always real data)
    print_test("Lunar Phase & Astronomical Data")
    lunar_phase = test_endpoint("GET", "/api/lunar/phase")
    if lunar_phase:
        phase = lunar_phase.get("data", {}).get("phase", "unknown")
        illumination = lunar_phase.get("data", {}).get("illumination", "N/A")
        print_info(f"Current lunar phase: {phase} ({illumination}% illuminated)")

    lunar_forecast = test_endpoint("GET", "/api/lunar/forecast")
    if lunar_forecast:
        forecast_days = len(lunar_forecast.get("data", {}).get("forecast", []))
        print_info(f"Lunar forecast: {forecast_days} days")

    # Test 5: GHOL Spawning Endpoints
    print_test("GHOL Spawning Probability")
    ghol_payload = {
        "lat": 17.5,
        "lng": 71.0,
        "date": datetime.utcnow().strftime("%Y-%m-%d")
    }
    spawning_prob = test_endpoint("POST", "/api/ghol/spawning-probability", ghol_payload)
    if spawning_prob and spawning_prob.get("data"):
        prob = spawning_prob["data"].get("probability", 0)
        print_info(f"GHOL spawning probability: {prob:.1%}")

    # Test 6: GHOL Analysis
    print_test("GHOL Full Analysis")
    ghol_analysis = test_endpoint("POST", "/api/ghol/analysis", {
        "lat_min": 14.0,
        "lat_max": 21.0,
        "lng_min": 67.0,
        "lng_max": 74.5
    })
    if ghol_analysis:
        print_info(f"GHOL analysis complete")

    # Test 7: Trip Planning
    print_test("GHOL Trip Plan")
    trip_plan = test_endpoint("POST", "/api/ghol/trip-plan", {
        "departure_port": "Ratnagiri",
        "trip_days": 4,
        "crew_size": 8,
        "target_species": "GHOL"
    })
    if trip_plan and trip_plan.get("data"):
        roi = trip_plan["data"].get("estimated_roi", 0)
        profit = trip_plan["data"].get("estimated_profit", 0)
        print_info(f"Estimated ROI: {roi:.1%}, Profit: ₹{profit:,.0f}")

    # Test 8: Economics Endpoints
    print_test("Market Prices")
    prices = test_endpoint("GET", "/api/economics/market-prices")
    if prices and prices.get("data"):
        for species, price in list(prices["data"].items())[:3]:
            print_info(f"  {species}: ₹{price:,.0f}/kg")

    print_test("Trip ROI Calculator")
    roi_payload = {
        "catch_kg": 500,
        "species": "GHOL",
        "fuel_liters": 200,
        "crew_size": 8,
        "trip_days": 4
    }
    roi = test_endpoint("POST", "/api/economics/trip-roi", roi_payload)
    if roi and roi.get("data"):
        roi_pct = roi["data"].get("roi_percent", 0)
        total_profit = roi["data"].get("total_profit", 0)
        print_info(f"Trip ROI: {roi_pct:.1f}%, Profit: ₹{total_profit:,.0f}")

    # Test 9: Frontend serving
    print_test("Frontend HTML")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
        if response.status_code == 200 and "SAMUDRA" in response.text:
            print_success(f"GET / → 200 (HTML frontend)")
            print_info(f"Frontend size: {len(response.text):,} bytes")
        else:
            print_error(f"Frontend not serving correctly")
    except Exception as e:
        print_error(f"Frontend error: {e}")

    # Summary
    print_header("Test Summary")
    print(f"{Colors.GREEN}{Colors.BOLD}✅ API Test Complete{Colors.ENDC}\n")
    print(f"{Colors.BOLD}Next Steps:{Colors.ENDC}")
    print(f"  1. Verify all endpoints are responding")
    print(f"  2. Open http://localhost:5000 in browser")
    print(f"  3. For real data: register with providers and update .env")
    print(f"  4. See API_SETUP_GUIDE.md for detailed instructions\n")

if __name__ == "__main__":
    try:
        run_tests()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.ENDC}")
        sys.exit(1)
