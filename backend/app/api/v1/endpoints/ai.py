import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from ....core.database import get_db
from ....core.redis_client import get_redis
from ....core.config import settings
from ....core.auth import AuthenticatedUser, get_current_user
from ....models.user import User
from ....services.ai.claude_agent import claude_agent

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


class AiQueryRequest(BaseModel):
    query: str
    language: str = "mr"
    user_id: Optional[str] = None
    user_state: Optional[str] = None
    context: Optional[dict] = None


@router.post("/query")
async def query_ai(
    request: AiQueryRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    redis=Depends(get_redis),
    db: AsyncSession = Depends(get_db),
):
    """Query the Claude AI assistant."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Check subscription tier from DB; default to free if user not in DB yet
    tier_row = await db.execute(
        select(User.subscription_tier).where(User.id == current_user.id)
    )
    row = tier_row.first()
    is_free = row is None or row[0] == "free"

    # Rate limiting for free tier
    today = datetime.date.today().isoformat()
    key = f"ai_queries:{current_user.id}:{today}"
    queries_today = await redis.incr(key)
    await redis.expire(key, 86400)
    if is_free and queries_today > settings.free_tier_ai_queries_per_day:
        raise HTTPException(
            status_code=429,
            detail=f"Free tier limit: {settings.free_tier_ai_queries_per_day} queries/day",
        )

    ai_result = await claude_agent.query(
        user_query=request.query,
        language=request.language,
        context=request.context,
        user_state=request.user_state,
        redis=redis,
    )
    return ai_result


@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages for AI queries."""
    return {
        "languages": [
            {"code": "mr", "name": "मराठी", "region": "Maharashtra"},
            {"code": "gu", "name": "ગુજરાતી", "region": "Gujarat"},
            {"code": "hi", "name": "हिंदी", "region": "All India"},
            {"code": "kok", "name": "कोंकणी", "region": "Goa"},
            {"code": "kn", "name": "ಕನ್ನಡ", "region": "Karnataka"},
            {"code": "ml", "name": "മലയാളം", "region": "Kerala"},
            {"code": "en", "name": "English", "region": "Universal"},
        ]
    }
