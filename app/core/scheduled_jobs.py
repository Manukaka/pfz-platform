# app/core/scheduled_jobs.py
"""
APScheduler jobs:
  Every 30 min : SST + CHL data refresh (fast, critical for PFZ accuracy)
  Every 60 min : Wind + Wave + Current refresh (Open-Meteo Marine)
  9AM / 4PM IST: PFZ zone calculation using fresh data
  5:30PM IST   : INCOIS advisory fetch
  Midnight     : History prune
"""
import asyncio
import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytz

from app.data import history_manager
from app.data.incois_scraper import fetch_incois_advisory, get_not_available_response

logger = logging.getLogger(__name__)
IST = pytz.timezone("Asia/Kolkata")

# ── Fetch timestamp helpers ───────────────────────────────────────────────────
def _file_age_minutes(path: str) -> float:
    """Return age of file in minutes, or 9999 if missing."""
    try:
        mtime = os.path.getmtime(path)
        return (datetime.now(timezone.utc).timestamp() - mtime) / 60
    except OSError:
        return 9999.0

def _mark_fetch_start(source: str):
    """Write a fetch-in-progress marker so UI can show pulsing indicator."""
    try:
        p = Path(f"data/cache/.fetching_{source}")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(datetime.now(timezone.utc).isoformat())
    except Exception:
        pass

def _mark_fetch_done(source: str):
    try:
        Path(f"data/cache/.fetching_{source}").unlink(missing_ok=True)
    except Exception:
        pass

# ── SST refresh (every 30 min) ────────────────────────────────────────────────
async def job_sst_refresh() -> None:
    """Fetch fresh SST data from Open-Meteo Marine. ~15-20s, non-blocking."""
    age = _file_age_minutes("sst_data.json")
    if age < 25:
        logger.debug(f"SST fresh ({age:.0f}min) — skipping")
        return
    logger.info("SST refresh starting…")
    _mark_fetch_start("sst")
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _run_sst_fetch)
        logger.info("SST refresh complete")
    except Exception as e:
        logger.error(f"SST refresh failed: {e}")
    finally:
        _mark_fetch_done("sst")

def _run_sst_fetch():
    import importlib.util, sys as _sys
    try:
        # Import fetch_weather functions directly
        spec = importlib.util.spec_from_file_location("fetch_weather", "fetch_weather.py")
        fw = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fw)
        fw.fetch_sst()
        fw.save_meta()
    except Exception as e:
        logger.error(f"SST fetch inner error: {e}")

# ── CHL refresh (every 30 min) ────────────────────────────────────────────────
async def job_chl_refresh() -> None:
    """Fetch fresh chlorophyll data from NOAA OceanWatch ERDDAP."""
    age = _file_age_minutes("chl_data.json")
    if age < 25:
        logger.debug(f"CHL fresh ({age:.0f}min) — skipping")
        return
    logger.info("CHL refresh starting…")
    _mark_fetch_start("chl")
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _run_chl_fetch)
        logger.info("CHL refresh complete")
    except Exception as e:
        logger.error(f"CHL refresh failed: {e}")
    finally:
        _mark_fetch_done("chl")

def _run_chl_fetch():
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("fetch_weather", "fetch_weather.py")
        fw = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fw)
        fw.fetch_chlorophyll()
    except Exception as e:
        logger.error(f"CHL fetch inner error: {e}")

# ── Wind/Wave/Current refresh (every 60 min) ──────────────────────────────────
async def job_wind_wave_current_refresh() -> None:
    """Fetch wind, wave, current from Open-Meteo Marine. ~30-45s."""
    age = _file_age_minutes("wind_data.json")
    if age < 55:
        logger.debug(f"Wind fresh ({age:.0f}min) — skipping")
        return
    logger.info("Wind/Wave/Current refresh starting…")
    _mark_fetch_start("wind")
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _run_wind_fetch)
        logger.info("Wind/Wave/Current refresh complete")
    except Exception as e:
        logger.error(f"Wind/Wave/Current refresh failed: {e}")
    finally:
        _mark_fetch_done("wind")

def _run_wind_fetch():
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("fetch_weather", "fetch_weather.py")
        fw = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fw)
        fw.fetch_wind()
        fw.fetch_wave()
        fw.fetch_current()
        fw.save_meta()
    except Exception as e:
        logger.error(f"Wind fetch inner error: {e}")


async def job_pfz_cache(slot: str) -> None:
    """Compute and cache PFZ for given slot ('09' or '16')."""
    logger.info(f"Scheduled PFZ job starting — slot {slot}")
    try:
        from main import get_live_pfz
        resp = get_live_pfz()
        geojson = json.loads(resp.body)
        date_str = datetime.now(IST).strftime("%Y-%m-%d")
        history_manager.save_pfz(date_str, slot, geojson)
        count = len(geojson.get("features", []))
        logger.info(f"PFZ cached — slot {slot}, {count} zones, date {date_str}")
    except Exception as e:
        logger.error(f"PFZ cache job failed (slot {slot}): {e}")


async def job_pfz_morning() -> None:
    await job_pfz_cache("09")


async def job_pfz_afternoon() -> None:
    await job_pfz_cache("16")


async def job_incois_evening() -> None:
    logger.info("Scheduled INCOIS fetch starting")
    date_str = datetime.now(IST).strftime("%Y-%m-%d")
    max_retries = 3
    retry_delay = 300  # 5 minutes
    for attempt in range(1, max_retries + 1):
        try:
            result = await fetch_incois_advisory()
            if result and result.get("zones_count", 0) > 0:
                history_manager.save_incois(date_str, {"available": True, **result})
                logger.info(f"INCOIS cached — {result.get('zones_count', 0)} zones (attempt {attempt})")
                return
            elif attempt < max_retries:
                logger.warning(f"INCOIS returned empty/None (attempt {attempt}/{max_retries}), retrying in {retry_delay}s")
                await asyncio.sleep(retry_delay)
                continue
            else:
                logger.warning(f"INCOIS empty after {max_retries} attempts — caching not-available")
                history_manager.save_incois(date_str, get_not_available_response(date_str))
        except Exception as e:
            if attempt < max_retries:
                logger.warning(f"INCOIS attempt {attempt} failed: {e}, retrying in {retry_delay}s")
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"INCOIS job failed after {max_retries} attempts: {e}")
                history_manager.save_incois(date_str, get_not_available_response(date_str))


async def job_prune_history() -> None:
    deleted = history_manager.prune_old()
    logger.info(f"History pruned — {deleted} old files removed")
