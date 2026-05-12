import asyncio
import json
from typing import Optional, Set

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt

from ....core.config import settings
from ....core.redis_client import get_redis

router = APIRouter()

# Map of state → connected WebSockets for targeted broadcasts
_connections: dict[Optional[str], Set[WebSocket]] = {}


def _get_user_state(token: Optional[str]) -> Optional[str]:
    """Decode JWT and extract the user's registered state, if present."""
    if not token:
        return None
    try:
        claims = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"verify_aud": False},
        )
        return claims.get("state") or claims.get("user_metadata", {}).get("state")
    except JWTError:
        return None


@router.websocket("/ws/pfz")
async def pfz_websocket(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
):
    """Real-time PFZ zone updates via WebSocket.

    Pass ?token=<jwt> for auth. ?state=<state> overrides the state from the token
    (useful for unauthenticated map viewers in debug mode).
    """
    # In production, require a valid token
    if settings.environment == "production" and not token:
        await websocket.close(code=1008)
        return

    user_state = _get_user_state(token) or state

    await websocket.accept()

    # Register by state bucket (None = receives all states)
    bucket = user_state
    _connections.setdefault(bucket, set()).add(websocket)

    try:
        # Send current cached zones on connect
        redis_client = await get_redis()
        cache_key = f"pfz:latest:{user_state}" if user_state else "pfz:latest"
        cached_zones = await redis_client.get(cache_key)
        if cached_zones:
            await websocket.send_text(json.dumps({
                "type": "pfz_update",
                "zones": json.loads(cached_zones),
            }))

        # Keep alive with ping/pong
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                if data == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                await websocket.send_text(json.dumps({"type": "heartbeat"}))
    except WebSocketDisconnect:
        _connections.get(bucket, set()).discard(websocket)
    except Exception:
        _connections.get(bucket, set()).discard(websocket)
        await websocket.close()


async def broadcast_pfz_update(zones: list, state: Optional[str] = None):
    """Called by Kafka consumer when ML inference produces new PFZ zones.

    Sends to connections registered for the same state, plus the catch-all bucket.
    """
    message = json.dumps({"type": "pfz_update", "zones": zones})
    buckets_to_notify: list[Optional[str]] = [None]  # always notify catch-all
    if state:
        buckets_to_notify.append(state)

    for bucket in buckets_to_notify:
        disconnected: Set[WebSocket] = set()
        for ws in _connections.get(bucket, set()).copy():
            try:
                await ws.send_text(message)
            except Exception:
                disconnected.add(ws)
        _connections.get(bucket, set()).difference_update(disconnected)
