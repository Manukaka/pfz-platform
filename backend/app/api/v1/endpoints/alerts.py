import json
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....core.redis_client import get_redis

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("")
async def get_alerts(
    state: Optional[str] = Query(None),
    redis=Depends(get_redis),
    db: AsyncSession = Depends(get_db),
):
    """Get active alerts from DB, optionally filtered by state."""
    cache_key = f"alerts:{state or 'all'}"
    cached = await redis.get(cache_key)
    if cached:
        return {"alerts": json.loads(cached)}

    now = datetime.now(timezone.utc)
    params: dict = {"now": now}
    state_filter = ""
    if state:
        state_filter = "AND (state = :state OR state IS NULL) "
        params["state"] = state

    rows = await db.execute(
        text(
            "SELECT id, type, title, message, state, severity, source, created_at "
            "FROM alerts WHERE is_active = true "
            f"{state_filter}"
            "AND (valid_until IS NULL OR valid_until > :now) "
            "ORDER BY created_at DESC LIMIT 50"
        ),
        params,
    )

    alerts = [
        {
            "id": row.id,
            "type": row.type,
            "title": row.title,
            "message": row.message,
            "state": row.state,
            "severity": row.severity,
            "source": row.source,
            "time": row.created_at.isoformat() if row.created_at else None,
        }
        for row in rows.fetchall()
    ]

    await redis.setex(cache_key, 300, json.dumps(alerts))
    return {"alerts": alerts, "count": len(alerts)}
