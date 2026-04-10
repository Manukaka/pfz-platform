"""
process_pfz.py - PFZ with Real SST + Real Chlorophyll in GeoJSON
Bug Fix: Now loads chl_data.json from NASA ERDDAP instead of simulating CHL
"""
import numpy as np
import json
from datetime import datetime
import os

print("PFZ Processing Started:", datetime.now().strftime('%Y-%m-%d %H:%M'))

# ── Load SST (Open-Meteo Marine points) ──────────────────────────────────────
sst_points = []
if os.path.exists("sst_data.json"):
    try:
        with open("sst_data.json") as f:
            raw = json.load(f)
        sst_points = raw.get("points", [])
        print(f"SST loaded: {len(sst_points)} points")
    except Exception as e:
        print(f"SST load failed: {e}")

# ── Load real Chlorophyll (NASA ERDDAP via fetch_weather.py) ─────────────────
chl_points = []
if os.path.exists("chl_data.json"):
    try:
        with open("chl_data.json") as f:
            raw = json.load(f)
        chl_points = raw.get("points", [])
        print(f"CHL loaded: {len(chl_points)} points (source: {raw.get('source','unknown')})")
    except Exception as e:
        print(f"CHL load failed: {e}")
else:
    print("WARNING: chl_data.json not found — run fetch_weather.py first")

# ── Ocean mask (accurate Maharashtra coastline from sea_mask.py) ──────────────
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.core.sea_mask import is_sea, COAST_MAPPING, get_coast_lng_for_lat

def point_in_eez(lat, lon):
    """Check if point is in the sea within Maharashtra EEZ using accurate coastline."""
    return is_sea(lat, lon)

# ── Processing grid (Full Indian West Coast — Kerala to Gujarat) ──────────────
# Lat 8°-24°N, Lon 66°-77.5°E — covers Kerala, Karnataka, Goa, Maharashtra, Gujarat
lats = np.arange(8.0, 24.25, 0.25)
lons = np.arange(66.0, 77.75, 0.25)
print(f"Grid: {len(lats)} x {len(lons)} = {len(lats)*len(lons)} points")

# ── Build SST lookup from points ──────────────────────────────────────────────
def get_sst_at(lat, lon):
    if not sst_points:
        return None
    best, best_d = None, 999.0
    for p in sst_points:
        d = abs(p["lat"] - lat) + abs(p["lon"] - lon)
        if d < best_d:
            best_d = d
            best = p.get("sst")
    if best is not None and best_d < 3.0 and 0 < best < 40:
        return round(float(best), 1)
    return None

# ── Build CHL lookup from real data points ────────────────────────────────────
def get_chl_at(lat, lon):
    """Return nearest chlorophyll value from chl_data.json points."""
    if not chl_points:
        return None
    best, best_d = None, 999.0
    for p in chl_points:
        d = abs(p["lat"] - lat) + abs(p["lon"] - lon)
        if d < best_d:
            best_d = d
            best = p.get("chl")
    if best is not None and best_d < 2.5:
        return float(best)
    return None

# ── Build grids ───────────────────────────────────────────────────────────────
print("Building SST grid...")
sst_interp = np.zeros((len(lats), len(lons)))
for i, lat in enumerate(lats):
    for j, lon in enumerate(lons):
        v = get_sst_at(lat, lon)
        sst_interp[i, j] = v if v else (28.0 - 0.05*(lat-15)**2)

print("Building CHL grid (real data if available, seasonal fallback otherwise)...")
month = datetime.now().month
chl_grid = np.zeros((len(lats), len(lons)))
for i, lat in enumerate(lats):
    for j, lon in enumerate(lons):
        real_chl = get_chl_at(lat, lon)
        if real_chl is not None:
            chl_grid[i, j] = max(0.05, real_chl)
        else:
            # Seasonal fallback only when NASA ERDDAP data missing for this point
            c = 0.15
            bloom = month in [11, 12, 1, 2, 3, 6, 7, 8, 9]
            if 20<=lat<=23 and 68<=lon<=73: c += 1.8*np.exp(-((lat-21)**2)/2)*np.exp(-((lon-70)**2)/3)
            if month in [6,7,8,9] and 8<=lat<=14 and 74<=lon<=77: c += 2.5*np.exp(-((lat-11)**2)/4)*np.exp(-((lon-75)**2)/2)
            if 15<=lat<=19 and 70<=lon<=73: c += 0.8*np.exp(-((lat-17)**2)/3)*np.exp(-((lon-71.5)**2)/2)
            if 8<=lat<=12 and 71<=lon<=74: c += 1.2*np.exp(-((lat-10)**2)/3)*np.exp(-((lon-72.5)**2)/2)
            if month in [6,7,8] and 5<=lat<=12 and 55<=lon<=62: c += 3.0*np.exp(-((lat-8)**2)/5)*np.exp(-((lon-58)**2)/4)
            if 16<=lat<=23 and 55<=lon<=62: c += 1.5*np.exp(-((lat-20)**2)/4)*np.exp(-((lon-57)**2)/3)
            chl_grid[i, j] = max(0.05, c + np.random.normal(0, 0.05))

real_chl_count = sum(1 for p in chl_points if p.get("chl"))
print(f"CHL grid built: {real_chl_count} real points used, rest from seasonal model")

# ── PFZ Score calculation ─────────────────────────────────────────────────────
grad_lat = np.gradient(sst_interp, axis=0)
grad_lon = np.gradient(sst_interp, axis=1)
sst_gradient = np.sqrt(grad_lat**2 + grad_lon**2)

def norm(a):
    mn, mx = a.min(), a.max()
    return (a - mn) / (mx - mn) if mx != mn else np.zeros_like(a)

score = 0.55*norm(chl_grid) + 0.30*norm(sst_gradient) + 0.15*norm(np.exp(-((sst_interp-28)**2)/8))

# ── Find local maxima ─────────────────────────────────────────────────────────
try:
    from scipy.ndimage import maximum_filter
    local_max = maximum_filter(score, size=12) == score
except ImportError:
    local_max = np.zeros_like(score, dtype=bool)
    for i in range(6, len(lats)-6):
        for j in range(6, len(lons)-6):
            if score[i, j] == score[i-6:i+6, j-6:j+6].max():
                local_max[i, j] = True

# ── Fish species labels ───────────────────────────────────────────────────────
fish = {
    'high':   {'mr': 'बांगडा, सुरमई, रावस, टुना',    'hi': 'बांगड़ा, सुरमई, रावस',   'en': 'Mackerel, Seerfish, Tuna'},
    'medium': {'mr': 'पापलेट, हलवा, झिंगे, बांगडा',  'hi': 'पापलेट, हलवा, झींगे',    'en': 'Pomfret, Halwa, Prawns'},
    'low':    {'mr': 'बोंबील, मांदेली, करली',         'hi': 'बोंबिल, मांदेली',         'en': 'Bombay Duck, Herring'}
}

# ── Build GeoJSON features ────────────────────────────────────────────────────
features = []
used = set()
counts = {'high': 0, 'medium': 0, 'low': 0}

for i in range(len(lats)):
    for j in range(len(lons)):
        if len(features) >= 40: break
        if not local_max[i, j]: continue
        lat, lon = float(lats[i]), float(lons[j])
        if not point_in_eez(lat, lon): continue
        s = float(score[i, j])
        if s < 0.38: continue
        if any(abs(i-pi) < 8 and abs(j-pj) < 8 for pi, pj in used): continue
        used.add((i, j))

        ztype = 'high' if s >= 0.72 else ('medium' if s >= 0.52 else 'low')
        counts[ztype] += 1

        sst_val = get_sst_at(lat, lon)
        chl_val = round(float(chl_grid[i, j]), 2)
        chl_source = "real" if get_chl_at(lat, lon) is not None else "model"

        angle = float(np.arctan2(grad_lat[i, j], grad_lon[i, j]))
        coords = []
        for k in range(7):
            t = (k/6 - 0.5) * 0.35
            curve = 0.12 * np.sin(np.pi * k/6)
            pt_lat = lat + t*np.sin(angle) + curve*np.cos(angle)
            pt_lon = lon + t*np.cos(angle) - curve*np.sin(angle)
            if point_in_eez(pt_lat, pt_lon):
                coords.append([round(pt_lon, 5), round(pt_lat, 5)])

        if len(coords) < 3: continue

        features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {
                "type":        ztype,
                "score":       round(s, 3),
                "fish_mr":     fish[ztype]['mr'],
                "fish_hi":     fish[ztype]['hi'],
                "fish_en":     fish[ztype]['en'],
                "sst":         sst_val,
                "chl":         chl_val,
                "chl_source":  chl_source,
                "center_lat":  round(lat, 4),
                "center_lon":  round(lon, 4),
                "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M")
            }
        })
    if len(features) >= 40: break

# ── Save GeoJSON ──────────────────────────────────────────────────────────────
geojson = {"type": "FeatureCollection", "features": features}
with open("pfz_data.geojson", "w") as f:
    json.dump(geojson, f, indent=2)

print(f"\nDone! {len(features)} zones — High:{counts['high']} Med:{counts['medium']} Low:{counts['low']}")
print(f"SST source: {'Real (Open-Meteo)' if sst_points else 'Simulated'}")
print(f"CHL source: {'Real (NASA ERDDAP)' if chl_points else 'Seasonal model'}")
print(f"Output: pfz_data.geojson saved [OK]")
