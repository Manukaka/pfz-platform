from typing import Optional
import json
import redis.asyncio as redis


class SafetyService:
    """
    Computes safety score based on wave height, wind speed, currents.
    Score 0-100: Green(<30), Yellow(30-60), Red(60-80), Black(>80)
    """

    def compute_safety(
        self,
        wave_height: float = 0.8,
        wind_speed: float = 15.0,
        current_strength: float = 0.5,
        cyclone_distance_km: Optional[float] = None,
    ) -> dict:
        score = 0

        # Wave component (0-40 pts)
        if wave_height > 4.0:
            score += 40
        elif wave_height > 3.0:
            score += 30
        elif wave_height > 2.0:
            score += 20
        elif wave_height > 1.5:
            score += 10
        else:
            score += 0

        # Wind component (0-30 pts)
        if wind_speed > 60:
            score += 30
        elif wind_speed > 45:
            score += 20
        elif wind_speed > 30:
            score += 15
        elif wind_speed > 20:
            score += 8
        else:
            score += 0

        # Current component (0-20 pts)
        if current_strength > 2.0:
            score += 20
        elif current_strength > 1.5:
            score += 12
        elif current_strength > 1.0:
            score += 6
        else:
            score += 0

        # Cyclone proximity (0-10 pts)
        if cyclone_distance_km is not None:
            if cyclone_distance_km < 200:
                score += 10
            elif cyclone_distance_km < 500:
                score += 5

        score = min(100, score)

        if score < 30:
            color = "green"
            message = "Safe conditions for fishing"
        elif score < 60:
            color = "yellow"
            message = "Caution: moderate sea conditions"
        elif score < 80:
            color = "red"
            message = "Danger: rough sea. Avoid deep sea fishing"
        else:
            color = "black"
            message = "EXTREME DANGER: Do not venture out"

        return {
            "score": score,
            "color": color,
            "message": message,
            "wave_height": wave_height,
            "wind_speed": wind_speed,
            "current_strength": current_strength,
        }

    async def get_cached_safety(
        self,
        redis_client: redis.Redis,
        state: str = "maharashtra",
    ) -> dict:
        cached = await redis_client.get(f"safety:{state}")
        if cached:
            return json.loads(cached)
        # Return default safe conditions if no data
        return self.compute_safety()

    async def update_safety_cache(
        self,
        redis_client: redis.Redis,
        state: str,
        safety_data: dict,
        ttl: int = 3600,
    ):
        await redis_client.setex(f"safety:{state}", ttl, json.dumps(safety_data))


safety_service = SafetyService()
