import httpx, json

apis = [
    ('PFZ Live',       'https://samudra-ai.onrender.com/api/pfz/live'),
    ('SST JSON',       'https://samudra-ai.onrender.com/sst_data.json'),
    ('CHL JSON',       'https://samudra-ai.onrender.com/chl_data.json'),
    ('CHL Heatmap',    'https://samudra-ai.onrender.com/api/chlorophyll/heatmap'),
    ('Forecast 6day',  'https://samudra-ai.onrender.com/api/forecast/6day'),
    ('INCOIS Live',    'https://samudra-ai.onrender.com/api/incois/live'),
    ('Depth',          'https://samudra-ai.onrender.com/api/depth?lat=17.5&lon=70.5'),
    ('Health',         'https://samudra-ai.onrender.com/health'),
    ('Wind Live',      'https://samudra-ai.onrender.com/api/wind/live'),
    ('Wave Live',      'https://samudra-ai.onrender.com/api/wave/live'),
    ('Current Live',   'https://samudra-ai.onrender.com/api/current/live'),
    ('Wind JSON',      'https://samudra-ai.onrender.com/wind_data.json'),
    ('Wave JSON',      'https://samudra-ai.onrender.com/wave_data.json'),
    ('Current JSON',   'https://samudra-ai.onrender.com/current_data.json'),
    ('PFZ GeoJSON',    'https://samudra-ai.onrender.com/pfz_data.geojson'),
    ('Agents Status',  'https://samudra-ai.onrender.com/api/agents/status'),
]

for name, url in apis:
    try:
        r = httpx.get(url, timeout=20)
        d = r.json() if r.status_code == 200 else {}
        info = ''
        if 'features' in d:
            info = f"{len(d['features'])} features"
        elif 'points' in d:
            info = f"{len(d['points'])} points"
        elif 'available' in d:
            info = f"available={d['available']}"
        elif 'status' in d:
            info = str(d['status'])
        elif 'days' in d:
            info = f"{len(d['days'])} days"
        elif 'zones' in d:
            info = f"{len(d['zones'])} zones"
        else:
            info = str(list(d.keys()))[:80]
        print(f"  {r.status_code} {name:20s} {info}")
    except Exception as e:
        print(f"  ERR {name:20s} {e}")
