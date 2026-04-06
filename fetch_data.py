import copernicusmarine
import numpy as np
import json
from datetime import datetime, timedelta

print("Arabian Sea SST fetch kartoy...")

today = datetime.utcnow()
yesterday = today - timedelta(days=1)

ds = copernicusmarine.open_dataset(
    dataset_id="cmems_mod_glo_phy_anfc_0.083deg_P1D-m",
    variables=["tob"],
    minimum_latitude=5.0,
    maximum_latitude=28.0,
    minimum_longitude=51.0,
    maximum_longitude=78.0,
    start_datetime=yesterday.strftime("%Y-%m-%dT00:00:00"),
    end_datetime=today.strftime("%Y-%m-%dT00:00:00"),
)

sst = ds['tob'].isel(time=0).values
lats = ds['latitude'].values
lons = ds['longitude'].values

print(f"Data milala! Shape: {sst.shape}")
print(f"Temp range: {np.nanmin(sst):.1f} to {np.nanmax(sst):.1f} C")

data = {
    "timestamp": today.isoformat(),
    "lats": lats.tolist(),
    "lons": lons.tolist(),
    "sst": sst.tolist()
}

with open("sst_data.json", "w") as f:
    json.dump(data, f)

print("sst_data.json save zala!")