# app/data/incois_scraper.py
"""
INCOIS PFZ Advisory Scraper — 5:30 PM IST daily fetch.
Tries authenticated login to samudra.incois.gov.in then fetches PFZ advisory.
Falls back to public endpoints. Returns structured data or None.
On failure: only INCOIS panel shows 'not available' — never affects other layers.
"""
import logging
import json
import os
import re
from datetime import datetime
from typing import Optional, Dict, List

import httpx
import pytz

logger = logging.getLogger(__name__)
IST = pytz.timezone("Asia/Kolkata")

INCOIS_BASE = "https://samudra.incois.gov.in/INCOIS"
INCOIS_PUBLIC_ENDPOINTS = [
    f"{INCOIS_BASE}/pfzViewAction.do",
    f"{INCOIS_BASE}/advisoryData.json",
    "https://incois.gov.in/portal/pfz/pfz.jsp",
]
# These require a logged-in session
INCOIS_AUTH_ENDPOINTS = [
    f"{INCOIS_BASE}/pfzViewAction.do",
    f"{INCOIS_BASE}/advisoryData.json",
]


async def _get_authenticated_client() -> Optional[httpx.AsyncClient]:
    """Login to INCOIS Samudra portal and return an authenticated client, or None."""
    user = os.getenv("INCOIS_USER", "")
    pwd  = os.getenv("INCOIS_PASS", "")
    if not user or not pwd:
        return None
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 DaryaSagar/2.0",
        "Referer": f"{INCOIS_BASE}/loginPage.jsp",
        "Origin": "https://samudra.incois.gov.in",
    }
    login_payloads = [
        # Struts / Spring Security variants
        {"j_username": user, "j_password": pwd},
        {"username": user, "password": pwd},
        {"userId": user, "password": pwd},
    ]
    login_urls = [
        f"{INCOIS_BASE}/j_spring_security_check",
        f"{INCOIS_BASE}/loginAction.do",
        f"{INCOIS_BASE}/userLoginAction.do",
    ]
    client = httpx.AsyncClient(timeout=20.0, follow_redirects=True, headers=headers)
    for login_url in login_urls:
        for payload in login_payloads:
            try:
                resp = await client.post(login_url, data=payload)
                # Success: redirected to dashboard (not back to login page)
                if resp.status_code in (200, 302) and "login" not in str(resp.url).lower():
                    logger.info(f"INCOIS login succeeded via {login_url}")
                    return client
            except Exception as e:
                logger.debug(f"INCOIS login attempt {login_url} failed: {e}")
                continue
    await client.aclose()
    return None


async def fetch_incois_advisory() -> Optional[Dict]:
    """Attempt to fetch real INCOIS PFZ advisory. Returns structured dict or None."""
    # Try 1: authenticated session
    auth_client = await _get_authenticated_client()
    if auth_client:
        try:
            for url in INCOIS_AUTH_ENDPOINTS:
                try:
                    resp = await auth_client.get(url)
                    if resp.status_code == 200:
                        parsed = _parse_incois_response(resp.text, resp.headers.get("content-type", ""))
                        if parsed:
                            logger.info(f"INCOIS authenticated fetch OK from {url}: {parsed.get('zones_count',0)} zones")
                            await auth_client.aclose()
                            return parsed
                except Exception as e:
                    logger.warning(f"INCOIS auth fetch failed {url}: {e}")
        finally:
            try:
                await auth_client.aclose()
            except Exception:
                pass

    # Try 2: public endpoints (no auth)
    for url in INCOIS_PUBLIC_ENDPOINTS:
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0 DaryaSagar/2.0"})
                if resp.status_code == 200:
                    parsed = _parse_incois_response(resp.text, resp.headers.get("content-type", ""))
                    if parsed:
                        logger.info(f"INCOIS public fetch OK from {url}")
                        return parsed
        except Exception as e:
            logger.warning(f"INCOIS public fetch failed {url}: {e}")
            continue

    logger.warning("All INCOIS endpoints failed — returning None")
    return None


def _parse_incois_response(text: str, content_type: str) -> Optional[Dict]:
    """Parse INCOIS response — handles JSON and HTML."""
    now = datetime.now(IST)
    if "json" in content_type or text.strip().startswith("{") or text.strip().startswith("["):
        try:
            data = json.loads(text)
            zones = _extract_zones_from_json(data)
            if zones:
                return _build_incois_result(zones, now, "INCOIS API")
        except Exception:
            pass
    zones = _extract_zones_from_html(text)
    if zones:
        return _build_incois_result(zones, now, "INCOIS Web Advisory")
    return None


def _extract_zones_from_json(data) -> List[Dict]:
    zones = []
    items = data if isinstance(data, list) else data.get("zones", data.get("features", []))
    for item in items:
        lat = item.get("latitude") or item.get("lat") or item.get("center_lat")
        lon = item.get("longitude") or item.get("lon") or item.get("center_lon")
        if lat and lon:
            try:
                zones.append({
                    "lat": float(lat), "lon": float(lon),
                    "type": item.get("type", item.get("confidence", "medium")),
                    "description": item.get("description", item.get("advisory", "")),
                })
            except (ValueError, TypeError):
                continue
    return zones


def _extract_zones_from_html(html: str) -> List[Dict]:
    zones = []
    pattern = r'(\d{1,2}\.\d+)\s*[°]?\s*N[,\s]+(\d{2}\.\d+)\s*[°]?\s*E'
    matches = re.findall(pattern, html, re.IGNORECASE)
    for lat_s, lon_s in matches:
        lat, lon = float(lat_s), float(lon_s)
        if 10.0 <= lat <= 24.0 and 65.0 <= lon <= 76.0:
            zones.append({"lat": lat, "lon": lon, "type": "medium", "description": ""})
    return zones


def _build_incois_result(zones: List[Dict], now: datetime, source: str) -> Dict:
    geojson_features = []
    for z in zones:
        lat, lon = z["lat"], z["lon"]
        coords = [
            [lon - 0.3, lat - 0.1], [lon - 0.15, lat],
            [lon, lat + 0.1], [lon + 0.15, lat],
            [lon + 0.3, lat - 0.1],
        ]
        geojson_features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {
                "source": "INCOIS",
                "type": z.get("type", "medium"),
                "center_lat": lat, "center_lon": lon,
                "description": z.get("description", ""),
                "fetched_at": now.isoformat(),
            },
        })
    return {
        "source": source,
        "fetched_at": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "zones_count": len(zones),
        "available": True,
        "geojson": {
            "type": "FeatureCollection",
            "features": geojson_features,
            "metadata": {"source": source, "issued": now.isoformat(), "advisory_type": "PFZ"},
        },
    }


def get_not_available_response(date_str: str) -> Dict:
    """Standard 'not available' response for INCOIS panel."""
    return {
        "available": False,
        "date": date_str,
        "message": f"INCOIS data not available for {date_str}. Fetch may have failed or data not yet released.",
        "geojson": {"type": "FeatureCollection", "features": []},
    }
