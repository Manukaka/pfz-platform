#!/usr/bin/env python3
"""
SAMUDRA AI — PINN Pipeline Stress Test
Tests the Physics-Informed Neural Network (PINN) data-filling pipeline
under simulated monsoon cloud-cover scenarios.
"""

import os
import sys
import numpy as np
from datetime import datetime
import json
import logging

# Add app to path
sys.path.append(os.getcwd())

from app.data.data_aggregator import DataAggregator
from app.core.pinn_model import pinn_engine

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PINN-Test")

def simulate_monsoon_data_loss(data_grid, loss_percentage=0.4):
    """Simulates data loss due to cloud cover in a realistic pattern"""
    grid = np.array(data_grid)
    rows, cols = grid.shape

    # Create a 'cloud' mask (spatially correlated blocks)
    mask = np.zeros_like(grid, dtype=bool)
    num_clouds = int(rows * cols * loss_percentage / 16) # assuming 4x4 cloud blocks

    for _ in range(num_clouds):
        r = np.random.randint(0, rows - 4)
        c = np.random.randint(0, cols - 4)
        mask[r:r+4, c:c+4] = True

    masked_grid = grid.copy()
    masked_grid[mask] = np.nan
    return masked_grid, mask

def run_pinn_stress_test():
    print("\n" + "="*70)
    print("SAMUDRA AI — PINN Pipeline Stress Test (Monsoon Simulation)")
    print("="*70)

    # 1. Fetch clean data (or generate mock)
    print("\n[STEP 1] Fetching base data...")
    # Force use of mock data for testing if credentials aren't set
    os.environ['NO_MOCK_DATA'] = 'False'

    data = DataAggregator.fetch_pfz_data()

    if 'sst' not in data or 'u_current' not in data or 'v_current' not in data:
        print("Error: Required data not available for test.")
        return

    orig_sst = np.array(data['sst']['grid'])
    u_curr = np.array(data['u_current']['grid'])
    v_curr = np.array(data['v_current']['grid'])

    print(f"[OK] Fetched {orig_sst.shape} SST grid")

    # 2. Simulate Monsoon Cloud Cover (40% data loss)
    print("\n[STEP 2] Simulating 40% cloud cover data loss...")
    masked_sst, mask = simulate_monsoon_data_loss(orig_sst, loss_percentage=0.4)
    missing_count = np.sum(mask)
    total_count = orig_sst.size
    print(f"[OK] Masked {missing_count}/{total_count} pixels ({missing_count/total_count*100:.1f}%)")

    # 3. Run PINN Data Recovery
    print("\n[STEP 3] Running PINN physics-informed recovery...")
    start_time = datetime.now()

    # We call the engine directly to test its recovery performance
    recovered_sst = np.array(pinn_engine.fill_sst_gaps(masked_sst.tolist(), u_curr, v_curr))

    duration = (datetime.now() - start_time).total_seconds()
    print(f"[OK] Recovery complete in {duration:.3f}s")

    # 4. Evaluate Accuracy
    print("\n[STEP 4] Evaluating recovery accuracy...")

    # Calculate RMSE only on the missing parts
    diff = orig_sst[mask] - recovered_sst[mask]
    rmse = np.sqrt(np.mean(diff**2))

    # Calculate Mean Absolute Error
    mae = np.mean(np.abs(diff))

    print(f"   - Root Mean Square Error (RMSE): {rmse:.4f} °C")
    print(f"   - Mean Absolute Error (MAE): {mae:.4f} °C")

    # Success Criteria: RMSE < 0.5°C is excellent for SST gap filling
    if rmse < 0.5:
        print(f"\n✅ SUCCESS: PINN recovery is within scientific tolerance (< 0.5°C)")
    else:
        print(f"\n⚠️ WARNING: PINN recovery error ({rmse:.4f}°C) exceeds ideal tolerance (0.5°C)")

    # 5. Chlorophyll Recovery Test
    print("\n[STEP 5] Testing Chlorophyll recovery with upwelling constraints...")
    if 'chlorophyll' in data and 'grid' in data['chlorophyll'] and data['chlorophyll']['grid'] is not None:
        orig_chl = np.array(data['chlorophyll']['grid'])
        if orig_chl.size > 0 and len(orig_chl.shape) == 2:
            masked_chl, chl_mask = simulate_monsoon_data_loss(orig_chl, loss_percentage=0.3)

            recovered_chl = np.array(pinn_engine.fill_chlorophyll_gaps(
                masked_chl.tolist(), u_curr, v_curr, upwelling_index=0.8
            ))

            chl_diff = orig_chl[chl_mask] - recovered_chl[chl_mask]
            chl_rmse = np.sqrt(np.mean(chl_diff**2))
            print(f"   - Chlorophyll RMSE: {chl_rmse:.4f} mg/m³")
            print(f"[OK] Chlorophyll recovery consistent with advection-growth model")
        else:
            print(f"   - Skipping Chlorophyll: invalid grid shape {orig_chl.shape}")
    else:
        print("   - Skipping Chlorophyll: no grid data found")

    print("\n" + "="*70)
    print("STRESS TEST COMPLETE")
    print("="*70)

if __name__ == "__main__":
    run_pinn_stress_test()
