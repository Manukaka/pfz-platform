"""
fetch_weather.py — PFZ Platform
Real data fetch:
  - Wind (U/V)     : Open-Meteo API
  - Wave (U/V)     : Open-Meteo Marine → height+direction → U/V convert
  - Current (U/V)  : Open-Meteo Marine → uo/vo
  - Chlorophyll    : NASA ERDDAP CoastWatch (MODIS Aqua, 1-day)
  - SST            : Open-Meteo Marine → sea_surface_temperature
"""

import requests
import json
import math
import numpy as np
from datetime import datetime, timezone
from app.core.sea_mask import is_sea

# ── Arabian Sea grid ──────────────────────────────────────────────────────────
LAT1, LAT2 = 5.0,  25.0   # south → north
LON1, LON2 = 55.0, 78.0   # west  → east
DLAT, DLON = 2.0,  2.0    # grid spacing (degrees)

def make_lats():
    lats = []
    v = LAT2
    while v >= LAT1 - 0.01:
        lats.append(round(v, 2))
        v -= DLAT
    return lats

def make_lons():
    lons = []
    v = LON1
    while v <= LON2 + 0.01:
        lons.append(round(v, 2))
        v += DLON
    return lons

LATS = make_lats()   # top-to-bottom (north → south) for leaflet-velocity
LONS = make_lons()   # left-to-right (west  → east)
NY   = len(LATS)
NX   = len(LONS)

NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ── leaflet-velocity header builder ──────────────────────────────────────────
def make_header(param_cat, param_num, name, units="m/s"):
    return {
        "parameterCategory"  : param_cat,
        "parameterNumber"    : param_num,
        "dx"                 : DLON,
        "dy"                 : DLAT,
        "la1"                : LAT2,   # top-left lat (north)
        "la2"                : LAT1,   # bottom-right lat (south)
        "lo1"                : LON1,   # top-left lon (west)
        "lo2"                : LON2,   # bottom-right lon (east)
        "nx"                 : NX,
        "ny"                 : NY,
        "refTime"            : NOW,
        "units"              : units,
        "name"               : name
    }

def velocity_json(u_grid, v_grid, u_cat, u_num, u_name, v_num, v_name):
    """
    u_grid, v_grid : 2D list [ny][nx] — row 0 = northernmost row
    """
    u_flat = [u_grid[iy][ix] for iy in range(NY) for ix in range(NX)]
    v_flat = [v_grid[iy][ix] for iy in range(NY) for ix in range(NX)]
    return [
        {"header": make_header(u_cat, u_num, u_name), "data": u_flat},
        {"header": make_header(u_cat, v_num, v_name), "data": v_flat},
    ]

# ── fetch one Open-Meteo hourly variable for all grid points ──────────────────
def fetch_om(base_url, lat, lon, params_dict):
    """Returns hourly dict or None on error."""
    try:
        qp = "&".join(f"{k}={v}" for k, v in params_dict.items())
        url = f"{base_url}?latitude={lat}&longitude={lon}&{qp}&timezone=UTC"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json().get("hourly", {})
    except Exception as e:
        print(f"  OM fetch error ({lat},{lon}): {e}")
        return None

def latest_value(hourly, key):
    """Get most-recent non-null value from hourly list."""
    vals = hourly.get(key, []) if hourly else []
    for v in reversed(vals):
        if v is not None:
            return v
    return 0.0


def masked_uv(lat, lon, u, v):
    """Return zero vector for land points so animations render ocean-only."""
    return (u, v) if is_sea(lat, lon) else (0.0, 0.0)

# ══════════════════════════════════════════════════════════════════════════════
# 1. WIND — Open-Meteo (atmosphere)
# ══════════════════════════════════════════════════════════════════════════════
def fetch_wind():
    print("Fetching WIND data …")
    u_grid = [[0.0]*NX for _ in range(NY)]
    v_grid = [[0.0]*NX for _ in range(NY)]

    for iy, lat in enumerate(LATS):
        for ix, lon in enumerate(LONS):
            h = fetch_om(
                "https://api.open-meteo.com/v1/forecast",
                lat, lon,
                {"hourly": "wind_speed_10m,wind_direction_10m", "forecast_days": 1}
            )
            spd = latest_value(h, "wind_speed_10m")      # m/s
            dirn = latest_value(h, "wind_direction_10m")  # degrees (meteorological: FROM)
            rad = math.radians(dirn)
            # Meteorological convention: wind blows FROM direction
            u, v = round(-spd * math.sin(rad), 4), round(-spd * math.cos(rad), 4)
            u, v = masked_uv(lat, lon, u, v)
            u_grid[iy][ix], v_grid[iy][ix] = round(u, 4), round(v, 4)
            print(f"  Wind ({lat},{lon}): spd={spd:.1f} dir={dirn:.0f}°")

    data = velocity_json(u_grid, v_grid, 2, 2, "U-wind", 3, "V-wind")
    with open("wind_data.json", "w") as f:
        json.dump(data, f)
    print(f"[OK] wind_data.json saved ({NX*NY} points)")

# ══════════════════════════════════════════════════════════════════════════════
# 2. WAVE — Open-Meteo Marine → convert height+direction → U/V
#    BUG FIX: leaflet-velocity needs U/V, NOT height+direction directly!
# ══════════════════════════════════════════════════════════════════════════════
def fetch_wave():
    print("Fetching WAVE data …")
    u_grid = [[0.0]*NX for _ in range(NY)]
    v_grid = [[0.0]*NX for _ in range(NY)]

    for iy, lat in enumerate(LATS):
        for ix, lon in enumerate(LONS):
            h = fetch_om(
                "https://marine-api.open-meteo.com/v1/marine",
                lat, lon,
                {"hourly": "wave_height,wave_direction", "forecast_days": 1}
            )
            height = latest_value(h, "wave_height")       # metres
            dirn   = latest_value(h, "wave_direction")    # degrees (oceanographic: going TO)
            rad = math.radians(dirn)
            # Wave GOES towards direction → U/V
            # Scale height to 0–3 m/s range for good animation speed
            spd = min(height * 1.5, 3.0)
            u, v = round(spd * math.sin(rad), 4), round(spd * math.cos(rad), 4)
            u, v = masked_uv(lat, lon, u, v)
            u_grid[iy][ix], v_grid[iy][ix] = round(u, 4), round(v, 4)
            print(f"  Wave ({lat},{lon}): h={height:.2f}m dir={dirn:.0f}deg U={u_grid[iy][ix]:.3f} V={v_grid[iy][ix]:.3f}")

    data = velocity_json(u_grid, v_grid, 0, 0, "U-wave", 1, "V-wave")
    with open("wave_data.json", "w") as f:
        json.dump(data, f)
    print(f"[OK] wave_data.json saved ({NX*NY} points)")

# ══════════════════════════════════════════════════════════════════════════════
# 3. CURRENTS — Open-Meteo Marine (uo/vo already U/V)
# ══════════════════════════════════════════════════════════════════════════════
def fetch_current():
    print("Fetching CURRENT data …")
    u_grid = [[0.0]*NX for _ in range(NY)]
    v_grid = [[0.0]*NX for _ in range(NY)]

    for iy, lat in enumerate(LATS):
        for ix, lon in enumerate(LONS):
            h = fetch_om(
                "https://marine-api.open-meteo.com/v1/marine",
                lat, lon,
                {"hourly": "ocean_current_velocity,ocean_current_direction", "forecast_days": 1}
            )
            vel  = latest_value(h, "ocean_current_velocity")    # m/s
            dirn = latest_value(h, "ocean_current_direction")   # degrees (going TO)
            rad = math.radians(dirn)
            u, v = round(vel * math.sin(rad), 4), round(vel * math.cos(rad), 4)
            u, v = masked_uv(lat, lon, u, v)
            u_grid[iy][ix], v_grid[iy][ix] = round(u, 4), round(v, 4)
            print(f"  Current ({lat},{lon}): vel={vel:.3f} dir={dirn:.0f}°")

    data = velocity_json(u_grid, v_grid, 2, 6, "U-current", 7, "V-current")
    with open("current_data.json", "w") as f:
        json.dump(data, f)
    print(f"[OK] current_data.json saved ({NX*NY} points)")

# ══════════════════════════════════════════════════════════════════════════════
# 4. CHLOROPHYLL — NOAA OceanWatch ERDDAP (MODIS Aqua, monthly composite)
#    Dataset: aqua_chla_monthly_2018_0 on oceanwatch.pifsc.noaa.gov
# ══════════════════════════════════════════════════════════════════════════════
def fetch_chlorophyll():
    print("Fetching CHLOROPHYLL data (NOAA OceanWatch ERDDAP) …")

    # OceanWatch ERDDAP — last available month, Arabian Sea bounding box
    # Dataset columns: [time, latitude, longitude, chlor_a]  (NO altitude column)
    url = (
        "https://oceanwatch.pifsc.noaa.gov/erddap/griddap/aqua_chla_monthly_2018_0.json"
        f"?chlor_a[(last)][({LAT1}):({LAT2})][({LON1}):({LON2})]"
    )

    try:
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        raw = r.json()
        rows = raw["table"]["rows"]

        # rows: [time, latitude, longitude, chlor_a]
        points = []
        for row in rows:
            try:
                chl = float(row[3]) if row[3] is not None else None
                if chl is not None and not math.isnan(chl) and chl > 0:
                    points.append({
                        "lat": float(row[1]),
                        "lon": float(row[2]),
                        "chl": round(chl, 4)
                    })
            except (TypeError, ValueError):
                pass

        result = {
            "source"    : "NOAA OceanWatch ERDDAP - MODIS Aqua Chlorophyll-a (monthly)",
            "updated"   : NOW,
            "grid_size" : len(points),
            "points"    : points
        }
        with open("chl_data.json", "w") as f:
            json.dump(result, f)
        print(f"[OK] chl_data.json saved ({len(points)} valid points)")

    except Exception as e:
        print(f"⚠️  OceanWatch ERDDAP fetch failed: {e}")
        print("    Generating fallback chlorophyll grid …")
        _fallback_chlorophyll()

def _fallback_chlorophyll():
    """Seasonal approximation when ERDDAP is unavailable."""
    month = datetime.now().month
    # Arabian Sea bloom: Nov–Mar (NE monsoon), Jun–Sep (SW monsoon)
    bloom = month in [11, 12, 1, 2, 3, 6, 7, 8, 9]
    points = []
    lat = LAT1
    while lat <= LAT2:
        lon = LON1
        while lon <= LON2:
            # Higher CHL near coast and in bloom season
            coast_dist = min(abs(lon - 72.5), abs(lon - 73.5)) + abs(lat - 17.5)
            base = 0.8 if bloom else 0.3
            noise = math.sin(lat * 3.7) * math.cos(lon * 2.3) * 0.15
            chl = max(0.05, base - coast_dist * 0.03 + noise)
            points.append({"lat": round(lat,2), "lon": round(lon,2), "chl": round(chl,3)})
            lon += 1.0
        lat += 1.0

    result = {
        "source"    : "Fallback — seasonal approximation",
        "updated"   : NOW,
        "grid_size" : len(points),
        "points"    : points
    }
    with open("chl_data.json", "w") as f:
        json.dump(result, f)
    print(f"  Fallback chl_data.json saved ({len(points)} points)")

# ══════════════════════════════════════════════════════════════════════════════
# 5. SST — Open-Meteo Marine
# ══════════════════════════════════════════════════════════════════════════════
def fetch_sst():
    """
    Fetch SST across Indian West Coast at 1° spacing (high-res near-shore) +
    2° spacing for open Arabian Sea (speed balance).
    Total: ~80 points, covers Kerala–Gujarat coast accurately.
    """
    print("Fetching SST data (high-res west coast grid) …")
    points = []
    seen = set()

    # High-resolution west coast strip: 1° spacing, 8–24°N, 66–77°E
    west_coast_lats = [round(8 + i, 1) for i in range(17)]   # 8–24°N (17 pts)
    west_coast_lons = [round(66 + i, 1) for i in range(12)]  # 66–77°E (12 pts)

    # Coarser offshore grid: 2° spacing, covers 5–25°N, 55–66°E (open sea)
    offshore_lats = [v for v in range(5, 26, 2)]
    offshore_lons = [v for v in range(55, 67, 2)]

    all_points = (
        [(lat, lon) for lat in west_coast_lats for lon in west_coast_lons] +
        [(lat, lon) for lat in offshore_lats for lon in offshore_lons]
    )

    for lat, lon in all_points:
        key = (lat, lon)
        if key in seen:
            continue
        seen.add(key)
        h = fetch_om(
            "https://marine-api.open-meteo.com/v1/marine",
            lat, lon,
            {"hourly": "sea_surface_temperature", "forecast_days": 1}
        )
        sst = latest_value(h, "sea_surface_temperature")
        if sst and 15 < sst < 35:
            points.append({"lat": lat, "lon": lon, "sst": round(sst, 2)})
            print(f"  SST ({lat},{lon}): {sst:.1f}°C")
        else:
            print(f"  SST ({lat},{lon}): skip (val={sst})")

    with open("sst_data.json", "w") as f:
        json.dump({"updated": NOW, "source": "Open-Meteo Marine", "points": points}, f)
    print(f"[OK] sst_data.json saved ({len(points)}/{len(all_points)} pts)")

# ══════════════════════════════════════════════════════════════════════════════
# META
# ══════════════════════════════════════════════════════════════════════════════
def save_meta():
    meta = {
        "last_update" : NOW,
        "grid"        : {"lat1":LAT1,"lat2":LAT2,"lon1":LON1,"lon2":LON2,"dlat":DLAT,"dlon":DLON,"nx":NX,"ny":NY},
        "sources"     : {
            "wind"         : "Open-Meteo (10m wind)",
            "wave"         : "Open-Meteo Marine (height+dir → U/V)",
            "current"      : "Open-Meteo Marine (velocity+dir → U/V)",
            "chlorophyll"  : "NOAA OceanWatch ERDDAP MODIS Aqua (monthly)",
            "sst"          : "Open-Meteo Marine"
        }
    }
    with open("weather_meta.js" \
    "on", "w") as f:
        json.dump(meta, f, indent=2)
    print("[OK] weather_meta.json saved")

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print(f"PFZ Platform — Data Fetch  {NOW}")
    print(f"Grid: {NX}×{NY} = {NX*NY} points")
    print("=" * 60)
    fetch_wind()
    fetch_wave()
    fetch_current()
    fetch_chlorophyll()
    fetch_sst()
    save_meta()
    print("=" * 60)
    print("All data updated!")