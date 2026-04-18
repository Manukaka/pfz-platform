from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from ....core.database import get_db
from ....core.redis_client import get_redis
from ....services.pfz.pfz_service import pfz_service

router = APIRouter(prefix="/pfz", tags=["PFZ Zones"])


@router.get("/nearby")
async def get_nearby_zones(
    lat: Optional[float] = Query(None, description="User latitude"),
    lon: Optional[float] = Query(None, description="User longitude"),
    radius_km: float = Query(100, ge=10, le=500),
    state: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """Get PFZ zones near user location."""
    zones = await pfz_service.get_nearby_zones(
        db, redis, lat=lat, lon=lon, radius_km=radius_km, state=state, limit=limit
    )
    return {"zones": zones, "count": len(zones)}


@router.get("/state/{state}")
async def get_state_zones(
    state: str,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """Get all active PFZ zones for a specific state."""
    zones = await pfz_service.get_state_zones(db, redis, state=state)
    return {"zones": zones, "state": state, "count": len(zones)}


@router.get("/geojson")
async def get_pfz_geojson(
    state: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """Get PFZ zones as GeoJSON FeatureCollection."""
    zones = await pfz_service.get_nearby_zones(db, redis, state=state, limit=200)
    features = []
    for z in zones:
        features.append({
            "type": "Feature",
            "properties": {
                "zone_id": z.get("zone_id"),
                "confidence": z.get("confidence"),
                "state": z.get("state"),
                "top_species": z.get("top_species"),
                "safety_status": z.get("safety_status"),
                "sst": z.get("environmental_factors", {}).get("sst"),
            },
            "geometry": z.get("geometry"),
        })
    return {
        "type": "FeatureCollection",
        "features": features,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }
