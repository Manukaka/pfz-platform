from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from geoalchemy2.elements import WKTElement
from jose import jwt
from sqlalchemy.sql.elements import TextClause

from app.core.config import settings
from app.services.pfz.pfz_service import pfz_service


def _token(sub: str = "user-123", role: str | None = None) -> str:
    claims = {
        "sub": sub,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
    }
    if role:
        claims["role"] = role
    return jwt.encode(claims, settings.jwt_secret, algorithm=settings.jwt_algorithm)


@pytest.mark.asyncio
async def test_current_user_rejects_missing_bearer_token():
    from app.core.auth import get_current_user

    with pytest.raises(HTTPException) as exc:
        await get_current_user(None)

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_current_user_uses_subject_from_verified_token():
    from app.core.auth import get_current_user

    user = await get_current_user(
        HTTPAuthorizationCredentials(scheme="Bearer", credentials=_token("fisher-42"))
    )

    assert user.id == "fisher-42"


@pytest.mark.asyncio
async def test_admin_dependency_rejects_non_admin_token():
    from app.core.auth import get_current_user, require_admin

    user = await get_current_user(
        HTTPAuthorizationCredentials(scheme="Bearer", credentials=_token("fisher-42"))
    )

    with pytest.raises(HTTPException) as exc:
        await require_admin(user)

    assert exc.value.status_code == 403


def test_protected_routes_require_backend_auth_dependencies():
    from app.api.v1.endpoints import ai, catches, ocean
    from app.core.auth import get_current_user, require_admin

    protected_routes = {
        ("POST", "/catch"): get_current_user,
        ("GET", "/catch/history"): get_current_user,
        ("POST", "/ai/query"): get_current_user,
        ("POST", "/ocean/refresh"): require_admin,
    }

    for route in [*catches.router.routes, *ai.router.routes, *ocean.router.routes]:
        key = (next(iter(route.methods)), route.path)
        if key in protected_routes:
            dependencies = {dependency.call for dependency in route.dependant.dependencies}
            assert protected_routes[key] in dependencies


@pytest.mark.asyncio
async def test_pfz_geospatial_filter_uses_bound_parameters():
    captured = {}

    class FakeResult:
        def scalars(self):
            return self

        def all(self):
            return []

    class FakeDb:
        async def execute(self, query):
            captured["query"] = query
            return FakeResult()

    class FakeRedis:
        async def get(self, _key):
            return None

        async def setex(self, *_args):
            return None

    await pfz_service.get_nearby_zones(
        FakeDb(),
        FakeRedis(),
        lat=15.5,
        lon=73.7,
        radius_km=100,
    )

    where_criteria = captured["query"].whereclause.get_children()
    spatial_clause = next(
        criterion for criterion in where_criteria if isinstance(criterion, TextClause)
    )

    assert ":lon" in spatial_clause.text
    assert ":lat" in spatial_clause.text
    assert ":radius_m" in spatial_clause.text
    assert "73.7" not in spatial_clause.text
    assert spatial_clause._bindparams["lon"].value == 73.7
    assert spatial_clause._bindparams["lat"].value == 15.5
    assert spatial_clause._bindparams["radius_m"].value == 100000


def test_pfz_zone_payload_includes_flutter_and_map_geometry_fields():
    now = datetime.now(timezone.utc)
    zone = SimpleNamespace(
        zone_id="zone-1",
        state="maharashtra",
        confidence=0.88,
        source="ml_model_v3.0",
        polygon=WKTElement(
            "POLYGON((73.0 16.8, 73.2 16.8, 73.2 17.0, 73.0 17.0, 73.0 16.8))",
            srid=4326,
        ),
        center=WKTElement("POINT(73.1 16.9)", srid=4326),
        species_probability={"bangda": 0.42, "surmai": 0.28},
        environmental_factors={"sst": 29.2, "chlorophyll": 1.1},
        valid_from=now,
        valid_until=now + timedelta(hours=3),
        distance_from_shore_km=24.5,
        safety_status="green",
    )

    payload = pfz_service._zone_to_dict(zone)

    assert payload["polygon"] == [
        [73.0, 16.8],
        [73.2, 16.8],
        [73.2, 17.0],
        [73.0, 17.0],
        [73.0, 16.8],
    ]
    assert payload["center"] == [73.1, 16.9]
    assert payload["geometry"]["type"] == "Polygon"
    assert payload["top_species"] == "bangda"


@pytest.mark.asyncio
async def test_ai_pfz_tool_uses_global_live_cache_when_state_cache_missing():
    from app.services.ai.tools import _handle_pfz_zones

    class FakeRedis:
        async def get(self, key):
            if key == "pfz:latest":
                return '[{"state": "maharashtra", "name": "Live Zone", "center": [73.1, 16.9], "confidence": 0.9}]'
            return None

    result = await _handle_pfz_zones({"state": "maharashtra"}, redis=FakeRedis())

    assert result["source"] == "live_cache"
    assert result["count"] == 1
    assert result["zones"][0]["name"] == "Live Zone"
