"""
INCOIS PFZ bulletin scraper.
Runs daily at 5:30 PM IST (INCOIS publishes around 5 PM).
"""
import asyncio
import aiohttp
import json
import re
import structlog
from datetime import date, datetime
from typing import Optional

from ...core.config import settings
from ...core.redis_client import get_redis

logger = structlog.get_logger()

INCOIS_BULLETIN_URLS = {
    "gujarat": f"{settings.incois_base_url}/portal/osf/pfz_bulletins.jsp?state=GJ",
    "maharashtra": f"{settings.incois_base_url}/portal/osf/pfz_bulletins.jsp?state=MH",
    "goa": f"{settings.incois_base_url}/portal/osf/pfz_bulletins.jsp?state=GA",
    "karnataka": f"{settings.incois_base_url}/portal/osf/pfz_bulletins.jsp?state=KA",
    "kerala": f"{settings.incois_base_url}/portal/osf/pfz_bulletins.jsp?state=KL",
}


class IncoisScraper:

    async def fetch_all_bulletins(self) -> dict:
        results = {}
        async with aiohttp.ClientSession() as session:
            for state, url in INCOIS_BULLETIN_URLS.items():
                try:
                    bulletin = await self._fetch_bulletin(session, state, url)
                    results[state] = bulletin
                    logger.info("Fetched INCOIS bulletin", state=state)
                except Exception as e:
                    logger.error("Failed to fetch bulletin", state=state, error=str(e))
        return results

    async def _fetch_bulletin(self, session: aiohttp.ClientSession, state: str, url: str) -> dict:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            resp.raise_for_status()
            html = await resp.text()
            return {
                "state": state,
                "date": date.today().isoformat(),
                "raw_html": html[:5000],  # Store first 5KB
                "fetched_at": datetime.utcnow().isoformat(),
                "zones": self._parse_zones_from_html(html, state),
            }

    def _parse_zones_from_html(self, html: str, state: str) -> list:
        zones = []
        # Basic coordinate extraction (enhance with full parser for production)
        lat_lon_pattern = re.compile(
            r"(\d{1,2}[°\s]?\d{0,2}[N])[^\d]*(\d{1,3}[°\s]?\d{0,2}[E])"
        )
        for match in lat_lon_pattern.finditer(html):
            zones.append({
                "raw_lat": match.group(1),
                "raw_lon": match.group(2),
                "state": state,
                "source": "incois_official",
            })
        return zones[:20]  # Return max 20 per bulletin

    async def cache_bulletin(self, redis_client, state: str, bulletin: dict):
        await redis_client.setex(
            f"incois:bulletin:{state}",
            86400,  # Cache for 24 hours
            json.dumps(bulletin),
        )

    async def run_daily_fetch(self):
        """Called by scheduler at 5:30 PM IST."""
        logger.info("Starting daily INCOIS bulletin fetch")
        redis = await get_redis()
        bulletins = await self.fetch_all_bulletins()
        for state, bulletin in bulletins.items():
            await self.cache_bulletin(redis, state, bulletin)
        logger.info("INCOIS bulletins cached", states=list(bulletins.keys()))
        return bulletins


incois_scraper = IncoisScraper()
