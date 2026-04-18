"""
Kafka consumers for satellite + ocean data ingestion.
Runs as a background worker.
"""
import asyncio
import json
import structlog
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from datetime import datetime, timezone

from ...core.config import settings
from ...core.redis_client import get_redis
from ..pfz.pfz_service import pfz_service
from ..safety.safety_service import safety_service

logger = structlog.get_logger()


class SatelliteDataConsumer:
    """Consumes satellite data updates and triggers PFZ ML inference."""

    def __init__(self):
        self.consumer: AIOKafkaConsumer | None = None
        self.producer: AIOKafkaProducer | None = None

    async def start(self):
        self.consumer = AIOKafkaConsumer(
            settings.kafka_satellite_topic,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id="satellite-processor",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="latest",
        )
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await self.consumer.start()
        await self.producer.start()
        logger.info("Satellite data consumer started")

    async def stop(self):
        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()

    async def process(self):
        async for msg in self.consumer:
            try:
                data = msg.value
                await self._process_satellite_update(data)
            except Exception as e:
                logger.error("Error processing satellite update", error=str(e))

    async def _process_satellite_update(self, data: dict):
        source = data.get("source")
        state = data.get("state")
        logger.info("Processing satellite update", source=source, state=state)

        # Trigger ML inference for affected region
        await self.producer.send(
            "ml-inference-requests",
            {
                "type": "pfz_inference",
                "state": state,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "features": data.get("features", {}),
            },
        )


class PfzZoneConsumer:
    """Consumes ML-inferred PFZ zones and stores + broadcasts them."""

    def __init__(self):
        self.consumer: AIOKafkaConsumer | None = None

    async def start(self):
        self.consumer = AIOKafkaConsumer(
            settings.kafka_pfz_topic,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id="pfz-zone-processor",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="latest",
        )
        await self.consumer.start()
        logger.info("PFZ zone consumer started")

    async def stop(self):
        if self.consumer:
            await self.consumer.stop()

    async def process(self):
        from ...api.v1.websocket.pfz_ws import broadcast_pfz_update
        redis = await get_redis()

        async for msg in self.consumer:
            try:
                zones = msg.value.get("zones", [])
                state = msg.value.get("state")

                # Update cache
                await redis.setex(
                    f"pfz:latest:{state}" if state else "pfz:latest",
                    settings.redis_pfz_ttl,
                    json.dumps(zones),
                )
                await pfz_service.invalidate_cache(redis, f"pfz:nearby:*")

                # Broadcast to WebSocket clients
                await broadcast_pfz_update(zones)
                logger.info("PFZ zones updated", count=len(zones), state=state)

                # FCM: send silent refresh push to background users for this state
                try:
                    from ...services.alerts.fcm_service import fcm_service
                    fcm_tokens_raw = await redis.get(f"fcm_tokens:{state}")
                    if fcm_tokens_raw:
                        tokens = json.loads(fcm_tokens_raw)
                        await fcm_service.send_silent_pfz_refresh(tokens, state or "all")
                except Exception as fcm_err:
                    logger.warning("FCM push failed", error=str(fcm_err))

            except Exception as e:
                logger.error("Error processing PFZ zones", error=str(e))


async def run_consumers():
    """Run all Kafka consumers concurrently."""
    satellite_consumer = SatelliteDataConsumer()
    pfz_consumer = PfzZoneConsumer()

    await asyncio.gather(
        satellite_consumer.start(),
        pfz_consumer.start(),
    )

    await asyncio.gather(
        satellite_consumer.process(),
        pfz_consumer.process(),
    )
