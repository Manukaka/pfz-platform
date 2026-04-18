from fastapi import APIRouter, Depends, Query
from typing import Optional

from ....core.redis_client import get_redis
from ....services.safety.safety_service import safety_service

router = APIRouter(prefix="/safety", tags=["Safety"])


@router.get("/current")
async def get_safety_status(
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    state: str = Query("maharashtra"),
    redis=Depends(get_redis),
):
    """Get current safety status for a state/location."""
    return await safety_service.get_cached_safety(redis, state=state)


@router.get("/states")
async def get_all_states_safety(redis=Depends(get_redis)):
    """Get safety status for all west coast states."""
    from ....core.constants import WEST_COAST_STATES
    result = {}
    for state in WEST_COAST_STATES:
        result[state] = await safety_service.get_cached_safety(redis, state=state)
    return result
