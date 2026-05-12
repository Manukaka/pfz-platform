"""Quick API test script for CHL and currents data sources."""
import requests
import json

# Test 1: ERDDAP erdMH1chla1day (daily MODIS Aqua CHL)
print("=== Test 1: erdMH1chla1day ===")
try:
    r = requests.get(
        "https://coastwatch.pfeg.noaa.gov/erddap/griddap/erdMH1chla1day.json"
        "?chlorophyll[(last)][(15):(16)][(72):(73)]",
        timeout=30
    )
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        rows = data["table"]["rows"]
        print(f"Rows: {len(rows)}")
        print(f"Sample: {rows[:3]}")
    else:
        print(f"Error: {r.text[:300]}")
except Exception as e:
    print(f"Failed: {e}")

# Test 2: ERDDAP erdMH1chla8day (8-day composite)
print("\n=== Test 2: erdMH1chla8day ===")
try:
    r = requests.get(
        "https://coastwatch.pfeg.noaa.gov/erddap/griddap/erdMH1chla8day.json"
        "?chlorophyll[(last)][(15):(16)][(72):(73)]",
        timeout=30
    )
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        rows = data["table"]["rows"]
        print(f"Rows: {len(rows)}")
        print(f"Sample: {rows[:3]}")
    else:
        print(f"Error: {r.text[:300]}")
except Exception as e:
    print(f"Failed: {e}")

# Test 3: VIIRS CHL (nesdisVHNSQchlaDaily)
print("\n=== Test 3: nesdisVHNSQchlaDaily ===")
try:
    r = requests.get(
        "https://coastwatch.pfeg.noaa.gov/erddap/griddap/nesdisVHNSQchlaDaily.json"
        "?chlor_a[(last)][(15):(16)][(72):(73)]",
        timeout=30
    )
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        rows = data["table"]["rows"]
        print(f"Rows: {len(rows)}")
        print(f"Sample: {rows[:3]}")
    else:
        print(f"Error: {r.text[:300]}")
except Exception as e:
    print(f"Failed: {e}")

# Test 4: VIIRS monthly (nesdisVHNSQchlaMonthly)
print("\n=== Test 4: nesdisVHNSQchlaMonthly ===")
try:
    r = requests.get(
        "https://coastwatch.pfeg.noaa.gov/erddap/griddap/nesdisVHNSQchlaMonthly.json"
        "?chlor_a[(last)][(15):(16)][(72):(73)]",
        timeout=30
    )
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        rows = data["table"]["rows"]
        print(f"Rows: {len(rows)}")
        print(f"Sample: {rows[:3]}")
    else:
        print(f"Error: {r.text[:300]}")
except Exception as e:
    print(f"Failed: {e}")

# Test 5: OC-CCI chlorophyll (Copernicus-hosted ERDDAP)
print("\n=== Test 5: Copernicus OC-CCI ===")
try:
    r = requests.get(
        "https://oceandata.sci.gsfc.nasa.gov/api/file_search"
        "?sensor=aqua&dtype=L3m&sdate=2026-04-01&edate=2026-04-06&prod=CHL",
        timeout=30
    )
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:300]}")
except Exception as e:
    print(f"Failed: {e}")

# Test 6: Open-Meteo Marine Currents
print("\n=== Test 6: Open-Meteo Marine Currents ===")
try:
    r = requests.get(
        "https://marine-api.open-meteo.com/v1/marine"
        "?latitude=15&longitude=72&hourly=ocean_current_velocity,ocean_current_direction&forecast_days=1",
        timeout=15
    )
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        hourly = data.get("hourly", {})
        vel = hourly.get("ocean_current_velocity", [])
        dirn = hourly.get("ocean_current_direction", [])
        non_null_vel = [v for v in vel if v is not None]
        print(f"Velocity points: {len(vel)}, non-null: {len(non_null_vel)}")
        if non_null_vel:
            print(f"Sample vel: {non_null_vel[:5]} km/h")
            print(f"Units: {data.get('hourly_units', {})}")
    else:
        print(f"Error: {r.text[:300]}")
except Exception as e:
    print(f"Failed: {e}")

# Test 7: Open-Meteo Marine Currents - deep ocean point
print("\n=== Test 7: Open-Meteo Marine Currents (deep ocean 10N, 65E) ===")
try:
    r = requests.get(
        "https://marine-api.open-meteo.com/v1/marine"
        "?latitude=10&longitude=65&hourly=ocean_current_velocity,ocean_current_direction&forecast_days=1",
        timeout=15
    )
    if r.status_code == 200:
        data = r.json()
        hourly = data.get("hourly", {})
        vel = hourly.get("ocean_current_velocity", [])
        non_null_vel = [v for v in vel if v is not None]
        print(f"Velocity points: {len(vel)}, non-null: {len(non_null_vel)}")
        if non_null_vel:
            print(f"Sample vel: {non_null_vel[:5]} km/h")
    else:
        print(f"Error: {r.text[:300]}")
except Exception as e:
    print(f"Failed: {e}")

# Test 8: GlobColour / CMEMS free chlorophyll
print("\n=== Test 8: NOAA ERDDAP search for chlorophyll datasets ===")
try:
    r = requests.get(
        "https://coastwatch.pfeg.noaa.gov/erddap/search/index.json"
        "?page=1&itemsPerPage=10&searchFor=chlorophyll+global+daily",
        timeout=30
    )
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        rows = data["table"]["rows"]
        for row in rows[:10]:
            # griddap URL is column index 2, title is index 4
            print(f"  Dataset: {row[2] if len(row) > 2 else 'N/A'} | {row[4] if len(row) > 4 else 'N/A'}")
except Exception as e:
    print(f"Failed: {e}")
