import asyncio

import sentry_sdk
import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sqlalchemy import text

from .core.config import settings
from .core.database import AsyncSessionLocal
from .core.redis_client import close_redis, get_redis
from .api.v1.endpoints import pfz, ai, safety, catches, alerts, species, ocean
from .api.v1.websocket import pfz_ws

scheduler = AsyncIOScheduler(timezone="UTC")

logger = structlog.get_logger()

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,
        environment=settings.environment,
    )

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="DaryaSagar - Real-time PFZ platform for Indian West Coast fishermen",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(pfz.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(safety.router, prefix="/api/v1")
app.include_router(catches.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")
app.include_router(species.router, prefix="/api/v1")
app.include_router(ocean.router, prefix="/api/v1")

# WebSocket routes
app.include_router(pfz_ws.router)


@app.on_event("startup")
async def startup():
    # Verify Redis is reachable
    try:
        redis = await get_redis()
        await redis.ping()
        logger.info("startup.redis", status="ok")
    except Exception as e:
        logger.warning("startup.redis", status="failed", error=str(e))

    # Verify database is reachable
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        logger.info("startup.db", status="ok")
    except Exception as e:
        logger.warning("startup.db", status="failed", error=str(e))

    # Start hourly ocean data refresh via APScheduler
    from .services.data_ingestion.ocean_data_service import ocean_data_service
    scheduler.add_job(ocean_data_service.refresh_all, "interval", hours=1, id="ocean_refresh")
    scheduler.start()
    logger.info("scheduler.started", job="ocean_refresh", interval="1h")
    # Trigger first fetch immediately (non-blocking)
    asyncio.create_task(_initial_data_fetch())

    # Start Kafka PFZ zone consumer only if explicitly configured (not default localhost)
    kafka = settings.kafka_bootstrap_servers
    if kafka and kafka != "localhost:9092":
        asyncio.create_task(_run_kafka_consumers())


async def _initial_data_fetch():
    """Fetch ocean data once at startup so Redis cache is populated immediately."""
    try:
        from .services.data_ingestion.ocean_data_service import ocean_data_service
        logger.info("startup.ocean_fetch", status="starting")
        await ocean_data_service.refresh_all()
        logger.info("startup.ocean_fetch", status="complete")
    except Exception as e:
        logger.warning("startup.ocean_fetch", status="failed", error=str(e))


async def _run_kafka_consumers():
    """Background task: consume ML-inferred PFZ zones from Kafka and broadcast via WebSocket."""
    try:
        from .services.data_ingestion.kafka_consumer import PfzZoneConsumer
        consumer = PfzZoneConsumer()
        await consumer.start()
        logger.info("kafka.pfz_consumer", status="started")
        await consumer.process()
    except Exception as e:
        logger.warning("kafka.pfz_consumer", status="failed", error=str(e))


@app.on_event("shutdown")
async def shutdown():
    scheduler.shutdown(wait=False)
    await close_redis()


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": settings.version,
        "environment": settings.environment,
    }


@app.post("/api/v1/admin/refresh-ocean-data")
async def manual_refresh():
    """Manually trigger ocean data refresh (for debugging/admin)."""
    asyncio.create_task(_initial_data_fetch())
    return {"status": "refresh_triggered", "message": "Ocean data refresh started in background"}


@app.get("/")
async def root():
    return {
        "app": "DaryaSagar API",
        "version": settings.version,
        "docs": "/docs",
    }
