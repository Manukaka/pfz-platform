from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

from ....core.redis_client import get_redis
from ....core.config import settings
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
    redis=Depends(get_redis),
):
    """Query the Claude AI assistant."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Rate limiting for free tier
    if request.user_id:
        key = f"ai_queries:{request.user_id}:{__import__('datetime').date.today()}"
        queries_today = await redis.incr(key)
        await redis.expire(key, 86400)
        # Pro users: check subscription (simplified)
        is_free = True  # TODO: check subscription from DB
        if is_free and queries_today > settings.free_tier_ai_queries_per_day:
            raise HTTPException(
                status_code=429,
                detail=f"Free tier limit: {settings.free_tier_ai_queries_per_day} queries/day",
            )

    result = await claude_agent.query(
        user_query=request.query,
        language=request.language,
        context=request.context,
        user_state=request.user_state,
        redis=redis,
    )
    return result


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
