"""
Background worker entry point.
Runs Kafka consumers + scheduled INCOIS scraper + hourly ocean data refresh.
"""
import asyncio
import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ...core.config import settings
from .kafka_consumer import PfzZoneConsumer, SatelliteDataConsumer
from .incois_scraper import incois_scraper
from .ocean_data_service import ocean_data_service

logger = structlog.get_logger()


async def run():
    scheduler = AsyncIOScheduler()

    # Daily INCOIS bulletin fetch at 17:30 IST (12:00 UTC)
    scheduler.add_job(
        incois_scraper.run_daily_fetch,
        "cron",
        hour=12,
        minute=0,
        id="incois_daily",
    )

    # Hourly ocean data refresh (Copernicus + ECMWF)
    scheduler.add_job(
        ocean_data_service.refresh_all,
        "interval",
        hours=1,
        id="ocean_data_refresh",
        max_instances=1,
    )

    # Start Kafka consumers
    satellite_consumer = SatelliteDataConsumer()
    pfz_consumer = PfzZoneConsumer()

    scheduler.start()
    logger.info("Data worker started")

    # Initial ocean data load on startup
    asyncio.create_task(ocean_data_service.refresh_all())

    try:
        await asyncio.gather(
            satellite_consumer.start(),
            pfz_consumer.start(),
        )
        await asyncio.gather(
            satellite_consumer.process(),
            pfz_consumer.process(),
        )
    except Exception as e:
        logger.error("Worker crashed", error=str(e))
        raise
    finally:
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(run())
