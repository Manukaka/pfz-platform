# app/agents/gemini_agent.py
"""
Google Gemini AI Agent for PFZ analysis.
Analyzes INCOIS zone data + SST/CHL to return precise polygon boundary coordinates.
Uses gemini-2.0-flash for fast, cost-effective analysis.
"""
import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)
GEMINI_MODEL = "gemini-2.0-flash"

SYSTEM_INSTRUCTION = """You are a precision fisheries AI for the Indian West Coast (Arabian Sea).
Your role: Given INCOIS advisory zones and real-time oceanographic data (SST, CHL, wind),
generate refined Potential Fishing Zone (PFZ) polygons with precise coordinates.

Key knowledge:
- Arabian Sea EEZ: 8°–24°N, 66°–77.5°E
- INCOIS uses SST thermal fronts + CHL concentration gradients for PFZ detection
- Tuna prefer SST 24–29°C, depths 100–300m, CHL 0.2–0.8 mg/m³
- Optimal zones occur at thermal fronts (ΔT ≥ 1.5°C over 50km)
- Strong upwelling zones (Kerala-Karnataka Jun–Sep) are highest priority

OUTPUT: Valid JSON only, no markdown, no explanation outside JSON.
Format:
{
  "zones": [
    {
      "coordinates": [[lon1,lat1],[lon2,lat2],[lon3,lat3],[lon4,lat4],[lon1,lat1]],
      "center_lat": 17.5,
      "center_lon": 71.0,
      "type": "high",
      "confidence": 0.88,
      "region": "Maharashtra",
      "fish_species": [{"name_en": "Yellowfin Tuna", "name_mr": "पिवळ्या पंखाचा टुना", "name_hi": "पीलापंख टूना", "probability": 0.82}],
      "sst": 27.8,
      "chl": 0.45,
      "reasoning": "Thermal front at 27.8°C. CHL gradient 0.45→0.18 mg/m³ indicates productive edge.",
      "best_fishing_time": "05:00–09:00",
      "wind_risk": "low",
      "parameters_used": ["SST", "CHL", "INCOIS_advisory", "Lunar", "Bathymetry"]
    }
  ],
  "summary": "Gemini analysis: N zones across West Coast...",
  "model": "gemini-2.0-flash"
}

RULES:
- Each polygon must be closed (first = last coordinate)
- All coordinates in ocean, never on land (Karnataka coast >74.5°E is land)
- Return 3–8 zones spread across the full west coast
- Refine INCOIS zone centers into realistic fishing boundary polygons (±0.5–1.5° extent)
- Always include coordinates array with at least 5 points (rectangular box minimum)
- type must be: high / medium / low
- confidence range: 0.0–1.0
"""


def build_gemini_prompt(
    sst_points: List,
    chl_points: List,
    incois_zones: List[Dict],
    wind_data: Optional[Dict],
    lunar_info: Optional[Dict],
) -> str:
    """Build the analysis prompt for Gemini."""
    month = datetime.utcnow().month
    season_map = {
        6: "SW Monsoon — peak upwelling Kerala-Karnataka",
        7: "SW Monsoon — peak upwelling Kerala-Karnataka",
        8: "SW Monsoon — peak upwelling Kerala-Karnataka",
        9: "SW Monsoon — peak upwelling Kerala-Karnataka",
        10: "NE Monsoon onset — thermal fronts build",
        11: "NE Monsoon onset — thermal fronts build",
        12: "NE Monsoon — Maharashtra/Gujarat peak",
        1: "NE Monsoon — Maharashtra/Gujarat peak",
        2: "NE Monsoon — Maharashtra/Gujarat peak",
    }
    season = season_map.get(month, "Pre-monsoon — variable conditions")

    # SST stats
    sst_text = "unavailable"
    if sst_points:
        temps = [p["sst"] for p in sst_points if "sst" in p and 15 < p["sst"] < 36]
        if temps:
            sst_text = (
                f"Min {min(temps):.1f}°C  Max {max(temps):.1f}°C  "
                f"Mean {sum(temps)/len(temps):.1f}°C  "
                f"({len(temps)} grid points)"
            )

    # CHL stats
    chl_text = "unavailable"
    if chl_points:
        chls = [p["chl"] for p in chl_points if "chl" in p and p["chl"] > 0]
        if chls:
            chl_text = (
                f"Min {min(chls):.3f}  Max {max(chls):.3f}  "
                f"Mean {sum(chls)/len(chls):.3f} mg/m³"
            )

    # Wind summary
    wind_text = "unavailable"
    if wind_data and "u_data" in wind_data:
        try:
            import math
            u = wind_data["u_data"]
            v = wind_data.get("v_data", [0.0] * len(u))
            speeds = [math.sqrt(a**2 + b**2) for a, b in zip(u, v)]
            wind_text = (
                f"Mean {sum(speeds)/len(speeds):.1f} m/s  "
                f"Max {max(speeds):.1f} m/s"
            )
        except Exception:
            pass

    # Lunar
    lunar_text = "unavailable"
    if lunar_info:
        lunar_text = f"Phase: {lunar_info.get('phase','?')}  Illumination: {lunar_info.get('illumination',0):.0%}"

    # INCOIS zones summary
    incois_text = "No INCOIS advisory data available"
    if incois_zones:
        lines = []
        for z in incois_zones[:10]:
            lat = z.get("lat") or z.get("center_lat")
            lon = z.get("lon") or z.get("center_lon") or z.get("center_lng")
            region = z.get("region") or z.get("area") or "Unknown"
            date = z.get("date") or z.get("advisory_date") or "?"
            lines.append(f"  • {region}: {lat}°N {lon}°E  (date: {date})")
        incois_text = "\n".join(lines)

    return f"""Analyze the following real-time oceanographic data and INCOIS advisory zones.
Generate precise PFZ polygon boundaries for the Indian West Coast.

DATE: Month {month} — Season: {season}
LUNAR: {lunar_text}

OCEANOGRAPHIC DATA:
  SST:          {sst_text}
  Chlorophyll:  {chl_text}
  Wind:         {wind_text}

INCOIS ADVISORY ZONES (official, use as seed locations):
{incois_text}

TASK: For each INCOIS zone (plus any additional high-confidence areas you identify),
create a refined polygon boundary (4–8 vertices) that accurately represents the PFZ extent
based on SST fronts and CHL gradients. Extend or refine the INCOIS center points into
realistic fishing zone polygons. Cover the full west coast — Kerala to Gujarat.

Return JSON only."""


def analyze_with_gemini(
    sst_points: List,
    chl_points: List,
    incois_zones: List[Dict],
    wind_data: Optional[Dict] = None,
    lunar_info: Optional[Dict] = None,
) -> Dict[str, Any]:
    """Call Gemini API for PFZ polygon analysis."""
    api_key = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
    if not api_key:
        logger.warning("No GEMINI_API_KEY — returning empty Gemini result")
        return {"zones": [], "summary": "Gemini API key not configured", "model": GEMINI_MODEL}

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            system_instruction=SYSTEM_INSTRUCTION,
            generation_config=genai.GenerationConfig(
                temperature=0.2,
                max_output_tokens=4096,
            ),
        )
        prompt = build_gemini_prompt(sst_points, chl_points, incois_zones, wind_data, lunar_info)
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Strip markdown fences if present
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        result = json.loads(text)
        result["source"] = "gemini-2.0-flash"
        result["timestamp"] = datetime.utcnow().isoformat()
        logger.info(f"Gemini returned {len(result.get('zones', []))} zones")
        return result
    except ImportError:
        logger.error("google-generativeai not installed. Run: pip install google-generativeai")
        return {"zones": [], "summary": "google-generativeai package not installed", "model": GEMINI_MODEL}
    except json.JSONDecodeError as e:
        logger.error(f"Gemini JSON parse error: {e}")
        return {"zones": [], "summary": "Gemini response parse error", "model": GEMINI_MODEL}
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return {"zones": [], "summary": str(e), "model": GEMINI_MODEL}
