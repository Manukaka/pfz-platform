from fastapi import APIRouter, Depends, Query
from typing import Optional
import json

from ....core.redis_client import get_redis

router = APIRouter(prefix="/alerts", tags=["Alerts"])

MOCK_ALERTS = [
    {
        "id": "alert-001",
        "type": "cyclone",
        "title": "Cyclone Watch - Arabian Sea",
        "message": "Low pressure system developing. Monitor IMD for updates.",
        "state": "gujarat",
        "severity": "yellow",
        "time": "2 hours ago",
        "source": "IMD",
    },
    {
        "id": "alert-002",
        "type": "pfz",
        "title": "New PFZ Zone - Ratnagiri Bank",
        "message": "New high-confidence PFZ zone detected. Estimated 80-120 kg Bangda.",
        "state": "maharashtra",
        "severity": "green",
        "time": "15 min ago",
        "source": "DaryaSagar ML",
    },
]


@router.get("")
async def get_alerts(
    state: Optional[str] = Query(None),
    redis=Depends(get_redis),
):
    """Get active alerts, optionally filtered by state."""
    # Try cache
    cache_key = f"alerts:{state or 'all'}"
    cached = await redis.get(cache_key)
    if cached:
        return {"alerts": json.loads(cached)}

    alerts = MOCK_ALERTS
    if state:
        alerts = [a for a in alerts if a.get("state") == state or a.get("state") is None]

    await redis.setex(cache_key, 300, json.dumps(alerts))
    return {"alerts": alerts, "count": len(alerts)}
