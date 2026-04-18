from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime
import uuid

from ....core.database import get_db
from ....models.user import CatchLog

router = APIRouter(prefix="/catch", tags=["Catch Logger"])


class CatchRequest(BaseModel):
    id: Optional[str] = None
    species: str
    quantity_kg: float
    lat: Optional[float] = None
    lon: Optional[float] = None
    timestamp: Optional[str] = None
    notes: Optional[str] = None
    is_shared: bool = False
    user_id: Optional[str] = None


@router.post("")
async def log_catch(
    request: CatchRequest,
    db: AsyncSession = Depends(get_db),
):
    """Log a fish catch."""
    from geoalchemy2.elements import WKTElement

    catch = CatchLog(
        id=request.id or str(uuid.uuid4()),
        user_id=request.user_id or "anonymous",
        species=request.species,
        quantity_kg=request.quantity_kg,
        location=WKTElement(f"POINT({request.lon} {request.lat})", srid=4326)
        if request.lat and request.lon
        else None,
        timestamp=datetime.fromisoformat(request.timestamp) if request.timestamp else datetime.utcnow(),
        notes=request.notes,
        is_shared=request.is_shared,
    )
    db.add(catch)
    await db.flush()
    return {"id": catch.id, "status": "logged"}


@router.get("/history")
async def get_catch_history(
    user_id: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Get catch history for a user."""
    result = await db.execute(
        select(CatchLog)
        .where(CatchLog.user_id == user_id)
        .order_by(CatchLog.timestamp.desc())
        .limit(limit)
    )
    catches = result.scalars().all()
    return {
        "catches": [
            {
                "id": c.id,
                "species": c.species,
                "quantity_kg": c.quantity_kg,
                "timestamp": c.timestamp.isoformat() if c.timestamp else None,
                "notes": c.notes,
            }
            for c in catches
        ]
    }
