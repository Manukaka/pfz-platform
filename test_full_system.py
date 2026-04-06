#!/usr/bin/env python3
"""
SAMUDRA AI — Complete System Test Suite
Tests all components, endpoints, and data sources
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
TEST_REGION = {
    "lat_min": 14.0,
    "lat_max": 21.0,
    "lng_min": 67.0,
    "lng_max": 74.5
}

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Test results tracking
results = {
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "errors": []
}

def print_header(text):
    print(f"\n{BLUE}{BOLD}{'='*70}{RESET}")
    print(f"{BLUE}{BOLD}{text:^70}{RESET}")
    print(f"{BLUE}{BOLD}{'='*70}{RESET}\n")

def print_test(name, status, details=""):
    if status == "PASS":
        print(f"{GREEN}[PASS]{RESET} {name}")
        if details:
            print(f"       {details}")
        results["passed"] += 1
    elif status == "FAIL":
        print(f"{RED}[FAIL]{RESET} {name}")
        if details:
            print(f"       {details}")
        results["failed"] += 1
        results["errors"].append((name, details))
    elif status == "SKIP":
        print(f"{YELLOW}[SKIP]{RESET} {name}")
        if details:
            print(f"       {details}")
        results["skipped"] += 1

def test_endpoint(method, endpoint, data=None, expected_status=200, name=None):
    """Test a single API endpoint"""
    test_name = name or f"{method} {endpoint}"
    url = f"{BASE_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            print_test(test_name, "FAIL", f"Unknown method: {method}")
            return False

        if response.status_code == expected_status:
            print_test(test_name, "PASS", f"Status: {response.status_code}")
            return True
        else:
            print_test(test_name, "FAIL", f"Expected {expected_status}, got {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_test(test_name, "FAIL", "Connection refused - is Flask running?")
        return False
    except Exception as e:
        print_test(test_name, "FAIL", str(e))
        return False

def test_response_structure(method, endpoint, data=None, required_keys=None):
    """Test that response contains expected JSON structure"""
    url = f"{BASE_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        else:
            response = requests.post(url, json=data, timeout=10)

        if response.status_code != 200:
            return False

        json_data = response.json()

        if required_keys:
            for key in required_keys:
                if key not in json_data:
                    return False

        return True
    except:
        return False

def main():
    print(f"\n{BOLD}SAMUDRA AI - Full System Test Suite{RESET}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {BASE_URL}\n")

    # ====================================================================================
    print_header("1. HEALTH & STATUS ENDPOINTS")
    # ====================================================================================

    test_endpoint("GET", "/api/health", name="API Health Check")
    test_endpoint("GET", "/api/status", name="System Status")
    test_endpoint("GET", "/api/data/sources", name="Data Sources Status")

    # ====================================================================================
    print_header("2. FRONTEND & STATIC FILES")
    # ====================================================================================

    test_endpoint("GET", "/", expected_status=200, name="Root Index")
    test_endpoint("GET", "/index.html", expected_status=200, name="Index HTML")

    # ====================================================================================
    print_header("3. PFZ ZONE ENDPOINTS")
    # ====================================================================================

    test_endpoint("POST", "/api/pfz/zones", data=TEST_REGION, name="Get PFZ Zones (Regional)")
    test_endpoint("GET", "/api/pfz/zones/0", name="Get Single PFZ Zone")

    # ====================================================================================
    print_header("4. GHOL SPECIALIST ENDPOINTS")
    # ====================================================================================

    test_endpoint("POST", "/api/ghol/analysis", data=TEST_REGION, name="GHOL Analysis (Regional)")
    test_endpoint("POST", "/api/ghol/spawning-probability",
                  data={"lat": 17.5, "lng": 71.0},
                  name="GHOL Spawning Probability")
    test_endpoint("POST", "/api/ghol/trip-plan", data=TEST_REGION, name="GHOL Trip Plan")

    # ====================================================================================
    print_header("5. LUNAR & ASTRONOMICAL ENDPOINTS")
    # ====================================================================================

    test_endpoint("GET", "/api/lunar/phase", name="Current Lunar Phase")
    test_endpoint("GET", "/api/lunar/forecast", name="Lunar Forecast (30 days)")
    test_endpoint("GET", "/api/lunar/spawning-windows", name="Spawning Windows")

    # ====================================================================================
    print_header("6. ECONOMIC ANALYSIS ENDPOINTS")
    # ====================================================================================

    test_endpoint("POST", "/api/economics/trip-roi", data=TEST_REGION, name="Trip ROI Calculation")
    test_endpoint("GET", "/api/economics/market-prices", name="Market Prices")

    # ====================================================================================
    print_header("7. AGENT SYSTEM ENDPOINTS")
    # ====================================================================================

    test_endpoint("POST", "/api/agents/army", data=TEST_REGION, name="Agent Army Analysis")
    test_endpoint("GET", "/api/agents/status", name="Agent System Status")
    test_endpoint("POST", "/api/agents/insights", data=TEST_REGION, name="Agent Insights")

    # ====================================================================================
    print_header("8. DATA FILE ENDPOINTS")
    # ====================================================================================

    test_endpoint("GET", "/pfz_data.geojson", name="PFZ GeoJSON")
    test_endpoint("GET", "/wind_data.json", name="Wind Data")
    test_endpoint("GET", "/wave_data.json", name="Wave Data")
    test_endpoint("GET", "/current_data.json", name="Current Data")

    # ====================================================================================
    print_header("FINAL RESULTS")
    # ====================================================================================

    total = results["passed"] + results["failed"] + results["skipped"]
    pass_pct = (results["passed"] / total * 100) if total > 0 else 0

    print(f"\nTotal Tests:   {total}")
    print(f"{GREEN}Passed:       {results['passed']}{RESET}")
    print(f"{RED}Failed:       {results['failed']}{RESET}")
    print(f"{YELLOW}Skipped:      {results['skipped']}{RESET}")
    print(f"\nSuccess Rate:  {pass_pct:.1f}%")

    if results["failed"] > 0:
        print(f"\n{RED}Failed Tests:{RESET}")
        for test_name, error in results["errors"]:
            print(f"  - {test_name}")
            print(f"    {error}")

    if results["failed"] == 0:
        print(f"\n{GREEN}{BOLD}ALL TESTS PASSED! System is operational.{RESET}")
        return 0
    else:
        print(f"\n{RED}{BOLD}Some tests failed. See above for details.{RESET}")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Test interrupted by user.{RESET}")
        sys.exit(1)
