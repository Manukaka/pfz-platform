import asyncio

import sentry_sdk
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sqlalchemy import text

from .core.config import settings
from .core.database import AsyncSessionLocal
from .core.redis_client import close_redis, get_redis
from .api.v1.endpoints import pfz, ai, safety, catches, alerts, species, ocean
from .api.v1.websocket import pfz_ws

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

    # Start Kafka PFZ zone consumer in background (non-blocking)
    if settings.kafka_bootstrap_servers:
        asyncio.create_task(_run_kafka_consumers())


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
    await close_redis()


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": settings.version,
        "environment": settings.environment,
    }


@app.get("/")
async def root():
    return {
        "app": "DaryaSagar API",
        "version": settings.version,
        "docs": "/docs",
    }
