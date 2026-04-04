# app/data/history_manager.py
"""
File-based JSON snapshot storage for PFZ history (10-day rolling window).
Stores: pfz_YYYY-MM-DD_HH.json | incois_YYYY-MM-DD.json | agent_YYYY-MM-DD_HH.json
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List

import pytz

DATA_DIR = Path("data/history")
IST = pytz.timezone("Asia/Kolkata")
KEEP_DAYS = 10


def _ensure_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _ist_now() -> datetime:
    return datetime.now(IST)


def save_pfz(date_str: str, slot: str, geojson: Dict) -> None:
    """Save PFZ GeoJSON. slot = '09' or '16'."""
    _ensure_dir()
    path = DATA_DIR / f"pfz_{date_str}_{slot}.json"
    with open(path, "w") as f:
        json.dump(geojson, f)


def get_pfz(date_str: str, slot: str) -> Optional[Dict]:
    path = DATA_DIR / f"pfz_{date_str}_{slot}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def save_incois(date_str: str, data: Dict) -> None:
    _ensure_dir()
    path = DATA_DIR / f"incois_{date_str}.json"
    with open(path, "w") as f:
        json.dump(data, f)


def get_incois(date_str: str) -> Optional[Dict]:
    path = DATA_DIR / f"incois_{date_str}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def save_agent(date_str: str, slot: str, data: Dict) -> None:
    _ensure_dir()
    path = DATA_DIR / f"agent_{date_str}_{slot}.json"
    with open(path, "w") as f:
        json.dump(data, f)


def get_agent(date_str: str, slot: str) -> Optional[Dict]:
    path = DATA_DIR / f"agent_{date_str}_{slot}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def list_available() -> List[Dict]:
    """Return list of available dates (last 10 days) with slot availability."""
    _ensure_dir()
    now = _ist_now()
    result = []
    for i in range(KEEP_DAYS):
        d = now - timedelta(days=i)
        date_str = d.strftime("%Y-%m-%d")
        slots = []
        for slot in ["09", "16"]:
            if (DATA_DIR / f"pfz_{date_str}_{slot}.json").exists():
                slots.append(slot)
        entry = {
            "date": date_str,
            "slots": slots,
            "has_incois": (DATA_DIR / f"incois_{date_str}.json").exists(),
            "has_agent_09": (DATA_DIR / f"agent_{date_str}_09.json").exists(),
            "has_agent_16": (DATA_DIR / f"agent_{date_str}_16.json").exists(),
            "is_today": i == 0,
        }
        result.append(entry)
    return result


def prune_old() -> int:
    """Delete files older than KEEP_DAYS. Returns count deleted."""
    _ensure_dir()
    cutoff = (_ist_now() - timedelta(days=KEEP_DAYS)).timestamp()
    deleted = 0
    for f in DATA_DIR.glob("*.json"):
        if f.name == ".gitkeep":
            continue
        if f.stat().st_mtime < cutoff:
            f.unlink()
            deleted += 1
    return deleted
