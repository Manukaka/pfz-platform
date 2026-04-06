#!/usr/bin/env python3
"""
Quick GEBCO Download - Starts download immediately
Downloads SRTM15+ (6GB) which has excellent Arabian Sea coverage
"""

import os
import requests
from tqdm import tqdm
import sys

DATA_DIR = "data/gebco"
os.makedirs(DATA_DIR, exist_ok=True)

# SRTM15+ is better for Arabian Sea and slightly smaller
DOWNLOAD_URL = "https://topex.ucsd.edu/pub/srtm15_plus/SRTM15_V2.5.5.nc"
OUTPUT_FILE = os.path.join(DATA_DIR, "srtm15_plus.nc")

print("="*70)
print("GEBCO/SRTM15+ Bathymetry Download")
print("="*70)
print()
print(f"Source: SRTM15+ V2.5.5")
print(f"Coverage: 80°S to 80°N (includes Arabian Sea)")
print(f"Resolution: 15 arc-seconds (~450m)")
print(f"File size: ~6 GB")
print(f"Output: {OUTPUT_FILE}")
print()
print("This will take 20-60 minutes depending on your internet speed.")
print()

response = input("Start download now? (y/n): ")

if response.lower() != 'y':
    print("Download cancelled.")
    sys.exit(0)

print()
print("Starting download...")
print("You can minimize this window - download will continue in background")
print()

try:
    response = requests.get(DOWNLOAD_URL, stream=True, timeout=60)
    response.raise_for_status()

    total_size = int(response.headers.get('content-length', 0))

    print(f"File size: {total_size / (1024**3):.2f} GB")
    print()

    with open(OUTPUT_FILE, 'wb') as f, tqdm(
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
        desc="Downloading",
        bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
    ) as pbar:
        for chunk in response.iter_content(chunk_size=1024*1024):  # 1MB chunks
            size = f.write(chunk)
            pbar.update(size)

    print()
    print("="*70)
    print("DOWNLOAD COMPLETE!")
    print("="*70)
    print()
    print(f"Grid saved to: {OUTPUT_FILE}")
    print(f"File size: {os.path.getsize(OUTPUT_FILE) / (1024**3):.2f} GB")
    print()
    print("✓ GEBCO bathymetry is now available!")
    print()
    print("Next steps:")
    print("1. Server will automatically use local grid")
    print("2. Much faster depth queries")
    print("3. Exact depths (not estimates)")
    print()
    print("Test it:")
    print(f"  python -c \"from app.data.gebco_client import GEBCOClient; d=GEBCOClient.fetch_bathymetry(17,18,70,71); print(d['source'])\"")
    print()

except KeyboardInterrupt:
    print()
    print()
    print("Download cancelled by user.")
    if os.path.exists(OUTPUT_FILE):
        print(f"Partial file will be deleted: {OUTPUT_FILE}")
        os.remove(OUTPUT_FILE)
    sys.exit(1)

except Exception as e:
    print()
    print(f"Error: {e}")
    print()
    print("Download failed. You can:")
    print("1. Try again later")
    print("2. Download manually from: https://topex.ucsd.edu/WWW_html/srtm15_plus.html")
    print(f"3. Save to: {OUTPUT_FILE}")
    sys.exit(1)
