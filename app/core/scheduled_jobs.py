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
    try:
        result = await fetch_incois_advisory()
        if result:
            history_manager.save_incois(date_str, {"available": True, **result})
            logger.info(f"INCOIS cached — {result.get('zones_count', 0)} zones")
        else:
            history_manager.save_incois(date_str, get_not_available_response(date_str))
            logger.warning("INCOIS not available — cached not-available marker")
    except Exception as e:
        logger.error(f"INCOIS job failed: {e}")
        history_manager.save_incois(date_str, get_not_available_response(date_str))


async def job_prune_history() -> None:
    deleted = history_manager.prune_old()
    logger.info(f"History pruned — {deleted} old files removed")
