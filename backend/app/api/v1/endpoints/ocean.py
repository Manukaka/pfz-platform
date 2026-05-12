import asyncio

from fastapi import APIRouter, Depends, HTTPException

from ....core.constants import WEST_COAST_STATES
from ....core.auth import AuthenticatedUser, require_admin
from ....services.data_ingestion.ocean_data_service import ocean_data_service

router = APIRouter(prefix="/ocean", tags=["Ocean Data"])


@router.get("/state/{state}")
async def get_state_ocean_data(state: str):
    """Get latest ocean conditions for a state (SST, chlorophyll, currents, wind, waves)."""
    if state not in WEST_COAST_STATES:
        raise HTTPException(status_code=404, detail=f"State '{state}' not on west coast")
    return await ocean_data_service.get_state_conditions(state)


@router.get("/all")
async def get_all_states_ocean_data():
    """Get ocean conditions for all 5 west coast states."""
    result = {}
    for state in WEST_COAST_STATES:
        result[state] = await ocean_data_service.get_state_conditions(state)
    return result


@router.post("/refresh")
async def trigger_ocean_refresh(
    _admin: AuthenticatedUser = Depends(require_admin),
):
    """Manually trigger ocean data refresh (admin use)."""
    asyncio.create_task(ocean_data_service.refresh_all())
    return {"status": "refresh_triggered"}
