import json
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
import redis.asyncio as redis
from datetime import datetime, timezone
from geoalchemy2.elements import WKBElement, WKTElement
from geoalchemy2.shape import to_shape
from shapely import wkt

from ...core.config import settings
from ...models.pfz_zone import PfzZone


class PfzService:

    async def get_nearby_zones(
        self,
        db: AsyncSession,
        redis_client: redis.Redis,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius_km: float = 100,
        state: Optional[str] = None,
        limit: int = 20,
    ) -> list[dict]:
        cache_key = (
            f"pfz:nearby:{lat:.2f}:{lon:.2f}:{radius_km}"
            if lat is not None and lon is not None
            else f"pfz:state:{state}"
        )

        # Try cache first
        cached = await redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

        now = datetime.now(timezone.utc)
        query = select(PfzZone).where(PfzZone.valid_until > now)

        if lat is not None and lon is not None:
            query = query.where(
                text(
                    "ST_DWithin("
                    "center::geography, "
                    "ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography, "
                    ":radius_m"
                    ")"
                ).bindparams(lon=lon, lat=lat, radius_m=radius_km * 1000)
            )
        elif state:
            query = query.where(PfzZone.state == state)

        query = query.order_by(PfzZone.confidence.desc()).limit(limit)
        result = await db.execute(query)
        zones = result.scalars().all()

        data = [self._zone_to_dict(z, lat, lon) for z in zones]

        await redis_client.setex(cache_key, settings.redis_pfz_ttl, json.dumps(data))
        return data

    def _zone_to_dict(self, zone: PfzZone, user_lat=None, user_lon=None) -> dict:
        polygon = self._geometry_to_geojson(zone.polygon)
        center = self._geometry_to_geojson(zone.center)
        environmental_factors = zone.environmental_factors or {}

        d = {
            "zone_id": zone.zone_id,
            "state": zone.state,
            "confidence": zone.confidence,
            "source": zone.source,
            "polygon": polygon.get("coordinates", [[]])[0],
            "center": center.get("coordinates", [None, None]),
            "geometry": polygon,
            "species_probability": zone.species_probability or {},
            "environmental_factors": {
                "sst": environmental_factors.get("sst", 0.0),
                "chlorophyll": environmental_factors.get("chlorophyll", 0.0),
                **environmental_factors,
            },
            "valid_from": zone.valid_from.isoformat() if zone.valid_from else None,
            "valid_until": zone.valid_until.isoformat() if zone.valid_until else None,
            "distance_from_shore_km": zone.distance_from_shore_km or 0.0,
            "safety_status": zone.safety_status,
        }
        # Add top species
        probs = zone.species_probability or {}
        if probs:
            d["top_species"] = max(probs, key=probs.get)
        return d

    def _geometry_to_geojson(self, geometry) -> dict:
        if geometry is None:
            return {"type": "GeometryCollection", "geometries": []}
        if isinstance(geometry, dict):
            return geometry
        if isinstance(geometry, WKTElement):
            shape = wkt.loads(geometry.data)
        elif isinstance(geometry, WKBElement):
            shape = to_shape(geometry)
        else:
            shape = geometry
        return json.loads(json.dumps(shape.__geo_interface__))

    async def get_state_zones(
        self,
        db: AsyncSession,
        redis_client: redis.Redis,
        state: str,
    ) -> list[dict]:
        return await self.get_nearby_zones(db, redis_client, state=state, limit=50)

    async def invalidate_cache(self, redis_client: redis.Redis, pattern: str = "pfz:*"):
        keys = await redis_client.keys(pattern)
        if keys:
            await redis_client.delete(*keys)


pfz_service = PfzService()
