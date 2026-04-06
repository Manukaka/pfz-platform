import time
import subprocess
import schedule
from datetime import datetime
from urllib import request as urlrequest

def run_with_retry(cmd, label, retries=2, delay_seconds=8):
    last_result = None
    for attempt in range(1, retries + 2):
        print(f"  → {label} (attempt {attempt}/{retries + 1})...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        last_result = result
        if result.returncode == 0:
            print(f"  ✅ {label} updated")
            return True
        print(f"  ⚠️  {label} error: {result.stderr[:220]}")
        if attempt <= retries:
            print(f"  ↻ Retrying {label} in {delay_seconds}s...")
            time.sleep(delay_seconds)
    return False


def warm_backend_endpoints():
    endpoints = [
        "http://localhost:8000/api/health",
        "http://localhost:8000/api/pfz/live",
        "http://localhost:8000/api/wind/live",
        "http://localhost:8000/api/current/live",
        "http://localhost:8000/api/wave/live",
        "http://localhost:8000/api/incois/advisory",
    ]
    failures = 0
    for ep in endpoints:
        try:
            with urlrequest.urlopen(ep, timeout=15) as resp:
                code = getattr(resp, 'status', 200)
                if code >= 400:
                    failures += 1
        except Exception as e:
            failures += 1
            print(f"  ⚠️  Endpoint recall failed: {ep} ({str(e)[:120]})")
    if failures == 0:
        print("  ✅ Backend endpoint recall successful")
    else:
        print(f"  ⚠️  Endpoint recall partial failures: {failures}")


def update_system():
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"\n[{ts}] ३-तास रिफ्रेश सुरू होत आहे...")

    # १. हवामान + समुद्र डेटा (Open-Meteo + NASA ERDDAP + related inputs)
    ok_weather = run_with_retry(["python", "fetch_weather.py"], "fetch_weather.py", retries=2)

    # २. PFZ झोन्स तयार करणे
    ok_pfz = run_with_retry(["python", "process_pfz.py"], "process_pfz.py", retries=2)

    # ३. API/backend recall warm-up (self-heal path after refresh failures)
    if (not ok_weather) or (not ok_pfz):
        print("  ↻ Refresh had failures; recalling backend APIs...")
    warm_backend_endpoints()

    print(f"[{datetime.now().strftime('%H:%M:%S')}] सिस्टीम रिफ्रेश झाली! ✅")

# दर ३ तासांनी अपडेट
schedule.every(3).hours.do(update_system)

print("=" * 50)
print("PFZ Platform — ३-तास ऑटो-रिफ्रेश शेड्युलर")
print("Data sources: Open-Meteo + NASA ERDDAP + backend recall")
print("टर्मिनल बंद करू नका!")
print("=" * 50)

update_system()   # पहिल्यांदा लगेच रन

while True:
    schedule.run_pending()
    time.sleep(60)
