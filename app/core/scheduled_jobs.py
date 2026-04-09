# app/core/scheduled_jobs.py
"""
APScheduler jobs: PFZ at 9AM/4PM IST, INCOIS at 5:30PM IST, prune at midnight.
"""
import asyncio
import json
import logging
from datetime import datetime

import pytz

from app.data import history_manager
from app.data.incois_scraper import fetch_incois_advisory, get_not_available_response

logger = logging.getLogger(__name__)
IST = pytz.timezone("Asia/Kolkata")


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
