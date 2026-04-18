import asyncio
import json
from typing import Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import redis.asyncio as redis

from ....core.redis_client import get_redis
from ....core.config import settings

router = APIRouter()

# Active WebSocket connections
_connections: Set[WebSocket] = set()


@router.websocket("/ws/pfz")
async def pfz_websocket(websocket: WebSocket):
    """Real-time PFZ zone updates via WebSocket."""
    await websocket.accept()
    _connections.add(websocket)
    try:
        # Send current zones on connect
        redis_client = await get_redis()
        cached_zones = await redis_client.get("pfz:latest")
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
        _connections.discard(websocket)
    except Exception:
        _connections.discard(websocket)
        await websocket.close()


async def broadcast_pfz_update(zones: list):
    """Called by ML inference pipeline when PFZ zones update."""
    message = json.dumps({"type": "pfz_update", "zones": zones})
    disconnected = set()
    for ws in _connections.copy():
        try:
            await ws.send_text(message)
        except Exception:
            disconnected.add(ws)
    _connections.difference_update(disconnected)
