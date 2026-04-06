#!/usr/bin/env python3
"""
GEBCO Grid Downloader - Downloads high-resolution global bathymetry grid
Downloads the GEBCO 2023 grid (~7GB) for precise depth queries
"""

import os
import requests
from tqdm import tqdm
import sys

# GEBCO 2023 Grid URLs
GEBCO_URLS = {
    'full': 'https://www.bodc.ac.uk/data/open_download/gebco/gebco_2023/zip/',  # Full global grid ~7GB
    'geotiff': 'https://www.bodc.ac.uk/data/open_download/gebco/gebco_2023/geotiff/',  # GeoTIFF format
    'netcdf': 'https://www.bodc.ac.uk/data/open_download/gebco/gebco_2023/netcdf/'  # NetCDF format (recommended)
}

# Direct download link for GEBCO 2023 NetCDF
GEBCO_NETCDF_URL = "https://www.bodc.ac.uk/data/open_download/gebco/gebco_2023/zip/GEBCO_2023.nc.zip"

# Alternative: Sub-grid for Arabian Sea only (much smaller!)
ARABIAN_SEA_BOUNDS = {
    'lat_min': 10.0,
    'lat_max': 25.0,
    'lng_min': 50.0,
    'lng_max': 80.0
}

DATA_DIR = "data/gebco"
GRID_FILE = os.path.join(DATA_DIR, "gebco_2023.nc")


def download_file(url: str, output_path: str, description: str = "Downloading"):
    """Download file with progress bar"""
    print(f"\n{description}...")
    print(f"URL: {url}")
    print(f"Output: {output_path}")

    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'wb') as f, tqdm(
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                size = f.write(chunk)
                pbar.update(size)

        print(f"✓ Downloaded: {output_path}")
        return True

    except Exception as e:
        print(f"✗ Download failed: {e}")
        return False


def download_arabian_sea_subgrid():
    """
    Download only Arabian Sea region from GEBCO using OPeNDAP
    Much smaller and faster than full global grid!
    """
    print("\n" + "="*70)
    print("GEBCO Arabian Sea Sub-Grid Download")
    print("="*70)

    try:
        import netCDF4 as nc
        from datetime import datetime

        print("\nAttempting to download Arabian Sea region only...")
        print(f"Bounds: {ARABIAN_SEA_BOUNDS}")

        # GEBCO OPeNDAP endpoint (if available)
        # Alternative: Use NCEI's ETOPO or similar

        # For now, create a script that will extract region from full grid
        print("\n⚠ OPeNDAP subset not available for GEBCO")
        print("Options:")
        print("1. Download full grid (~7GB) - most accurate")
        print("2. Use WMS/estimation (current method)")
        print("3. Use alternative service (ETOPO, SRTM15+)")

        return False

    except ImportError:
        print("\n✗ netCDF4 not installed. Install with: pip install netCDF4")
        return False


def download_srtm15_plus():
    """
    Alternative: Download SRTM15+ which has good coverage
    Smaller file, focuses on <80° latitude
    """
    print("\n" + "="*70)
    print("SRTM15+ Bathymetry Download (Alternative to GEBCO)")
    print("="*70)

    # SRTM15+ is available via Scripps Institution
    # URL: https://topex.ucsd.edu/WWW_html/srtm15_plus.html

    srtm_url = "https://topex.ucsd.edu/pub/srtm15_plus/SRTM15_V2.5.5.nc"
    output = os.path.join(DATA_DIR, "srtm15_plus.nc")

    print(f"\nSRTM15+ covers: 80°S to 80°N")
    print(f"Resolution: 15 arc-seconds (~450m)")
    print(f"File size: ~6-7 GB")
    print(f"Good coverage for Arabian Sea!")

    choice = input("\nDownload SRTM15+ instead of GEBCO? (y/n): ")

    if choice.lower() == 'y':
        return download_file(srtm_url, output, "Downloading SRTM15+ global grid")

    return False


def extract_region_from_grid(input_file: str, output_file: str, bounds: dict):
    """
    Extract Arabian Sea region from full GEBCO grid to reduce file size
    """
    try:
        import netCDF4 as nc
        import numpy as np

        print(f"\nExtracting region from {input_file}...")

        # Open full grid
        dataset = nc.Dataset(input_file, 'r')

        # Get full coordinate arrays
        lats = dataset.variables['lat'][:]
        lons = dataset.variables['lon'][:]

        # Find indices for Arabian Sea region
        lat_idx = np.where((lats >= bounds['lat_min']) & (lats <= bounds['lat_max']))[0]
        lon_idx = np.where((lons >= bounds['lng_min']) & (lons <= bounds['lng_max']))[0]

        # Extract elevation data for region
        elevation = dataset.variables['elevation'][lat_idx[0]:lat_idx[-1]+1, lon_idx[0]:lon_idx[-1]+1]

        # Create new NetCDF file with just the region
        output_ds = nc.Dataset(output_file, 'w', format='NETCDF4')

        # Create dimensions
        output_ds.createDimension('lat', len(lat_idx))
        output_ds.createDimension('lon', len(lon_idx))

        # Create variables
        lat_var = output_ds.createVariable('lat', 'f4', ('lat',))
        lon_var = output_ds.createVariable('lon', 'f4', ('lon',))
        elev_var = output_ds.createVariable('elevation', 'i2', ('lat', 'lon'))

        # Write data
        lat_var[:] = lats[lat_idx]
        lon_var[:] = lons[lon_idx]
        elev_var[:] = elevation

        # Add attributes
        output_ds.title = "GEBCO 2023 - Arabian Sea Region"
        output_ds.source = "Extracted from GEBCO_2023.nc"

        output_ds.close()
        dataset.close()

        print(f"✓ Region extracted: {output_file}")
        print(f"  Lat range: {bounds['lat_min']} to {bounds['lat_max']}")
        print(f"  Lon range: {bounds['lng_min']} to {bounds['lng_max']}")

        return True

    except Exception as e:
        print(f"✗ Extraction failed: {e}")
        return False


def main():
    print("="*70)
    print("GEBCO Bathymetry Grid Setup")
    print("="*70)

    print("\nOptions:")
    print("1. Download GEBCO 2023 full grid (~7 GB) - Most accurate")
    print("2. Download SRTM15+ (alternative, ~6 GB) - Good for Arabian Sea")
    print("3. Skip download - Use existing WMS/estimation method")

    choice = input("\nSelect option (1/2/3): ").strip()

    if choice == '1':
        print("\n⚠ Full GEBCO download is ~7 GB and may take 30-60 minutes")
        confirm = input("Continue? (y/n): ")

        if confirm.lower() == 'y':
            # Download full grid
            zip_file = os.path.join(DATA_DIR, "GEBCO_2023.nc.zip")

            if download_file(GEBCO_NETCDF_URL, zip_file, "Downloading GEBCO 2023"):
                print("\n✓ Download complete!")
                print(f"\nNext steps:")
                print(f"1. Unzip: {zip_file}")
                print(f"2. Extract to: {GRID_FILE}")
                print(f"3. Optional: Extract Arabian Sea region to reduce size")

                # Ask if user wants to extract region
                extract = input("\nExtract Arabian Sea region only? (y/n): ")
                if extract.lower() == 'y':
                    import zipfile
                    print("\nExtracting zip file...")
                    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                        zip_ref.extractall(DATA_DIR)

                    # Find the .nc file
                    full_grid = os.path.join(DATA_DIR, "GEBCO_2023.nc")
                    if os.path.exists(full_grid):
                        region_grid = os.path.join(DATA_DIR, "arabian_sea_gebco.nc")
                        extract_region_from_grid(full_grid, region_grid, ARABIAN_SEA_BOUNDS)
                        print(f"\n✓ Setup complete! Region file ready: {region_grid}")

    elif choice == '2':
        download_srtm15_plus()

    elif choice == '3':
        print("\nSkipping download. Current method will continue using:")
        print("- GEBCO WMS (when available)")
        print("- Geographic depth estimation (fallback)")

    else:
        print("\nInvalid choice. Exiting.")
        return

    print("\n" + "="*70)
    print("Setup Complete!")
    print("="*70)


if __name__ == "__main__":
    main()
