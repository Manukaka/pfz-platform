from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

from .core.config import settings
from .core.redis_client import close_redis
from .api.v1.endpoints import pfz, ai, safety, catches, alerts, species, ocean
from .api.v1.websocket import pfz_ws

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
    pass


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
