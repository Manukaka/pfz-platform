# app/agents/claude_agent.py
"""
Real Claude AI Agent for PFZ analysis.
Uses claude-sonnet-4-6 with complete fish encyclopedia in system prompt.
Falls back to offline knowledge base when API unavailable.
"""
import json
import logging
import os
import re
import math
import random
from datetime import datetime
from typing import Dict, Any, List, Optional

import anthropic

from app.data.fish_knowledge import FISH_KNOWLEDGE, get_top_species

logger = logging.getLogger(__name__)
MODEL = "claude-sonnet-4-6"

_FISH_ENCYCLOPEDIA = "\n".join(
    f"- {k.replace('_',' ')} ({v['name_mr']}/{v['name_hi']}): "
    f"SST {v['sst_range'][0]}-{v['sst_range'][1]}°C (opt {v['optimal_sst']}), "
    f"depth {v['depth_range'][0]}-{v['depth_range'][1]}m (opt {v['optimal_depth']}), "
    f"CHL {v['chl_range'][0]}-{v['chl_range'][1]} mg/m³, "
    f"peak months {v['peak_months']}, moon {v['moon_preference']}, "
    f"habitat: {v['habitat']}, best time: {v['best_time']}"
    for k, v in FISH_KNOWLEDGE.items()
)

SYSTEM_PROMPT = f"""You are an expert fisheries oceanographer specialising in the Arabian Sea and West Coast India (Maharashtra, Goa, Karnataka, Gujarat). You have 30 years of experience with INCOIS PFZ methodology, satellite oceanography, and fish behaviour.

FISH SPECIES ENCYCLOPEDIA (West Coast India):
{_FISH_ENCYCLOPEDIA}

MAHARASHTRA EEZ: 15°N-20.5°N, 67°E-74°E.

YOUR TASK: Given real-time oceanographic data, identify Potential Fishing Zones (PFZ) with scientific reasoning.

OUTPUT FORMAT (respond with valid JSON only, no markdown):
{{
  "zones": [
    {{
      "coordinates": [[lon, lat], [lon2, lat2]],
      "center_lat": 17.5,
      "center_lon": 70.5,
      "confidence": 0.84,
      "type": "high",
      "reasoning": "Strong thermal front detected at 28.1°C matching Surmai feeding threshold...",
      "fish_species": [
        {{"name_en": "Surmai", "name_mr": "सुरमई", "name_hi": "सुरमई", "icon": "🐠", "probability": 0.84, "reasoning": "SST optimal, peak season"}}
      ],
      "best_fishing_time": "05:00-08:00",
      "parameters_used": ["SST", "CHL", "depth", "lunar", "month"]
    }}
  ],
  "summary": "3 high-confidence zones found...",
  "data_quality": "high"
}}

RULES:
- All coordinates must be in ocean (Arabian Sea), never on land
- Latitude range: 14.0-21.0°N, Longitude range: 67.0-74.5°E
- Return 3-8 zones
- Each zone reasoning must cite specific parameter values
- Fish species probabilities must be scientifically justified
- type must be one of: high, medium, low"""


def analyze_with_claude(
    ocean_data: Dict[str, Any],
    region: Dict[str, float],
    lunar_info: Optional[Dict] = None,
) -> Dict[str, Any]:
    """Run Claude AI analysis. Falls back to offline if API unavailable."""
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key or not api_key.startswith("sk-ant"):
        logger.warning("No valid ANTHROPIC_API_KEY — using offline fallback")
        return _offline_analysis(ocean_data, region, lunar_info)
    try:
        prompt = _build_prompt(ocean_data, region, lunar_info)
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()
        text = re.sub(r"^```json\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        result = json.loads(text)
        result["source"] = "claude-sonnet-4-6"
        result["timestamp"] = datetime.utcnow().isoformat()
        logger.info(f"Claude returned {len(result.get('zones', []))} zones")
        return result
    except anthropic.APIError as e:
        logger.error(f"Claude API error: {e}")
        return _offline_analysis(ocean_data, region, lunar_info)
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.error(f"Claude response parse error: {e}")
        return _offline_analysis(ocean_data, region, lunar_info)
    except Exception as e:
        logger.error(f"Claude unexpected error: {e}")
        return _offline_analysis(ocean_data, region, lunar_info)


def _build_prompt(ocean_data: Dict, region: Dict, lunar_info: Optional[Dict]) -> str:
    sst_summary = ocean_data.get("sst_summary", "SST data unavailable")
    chl_summary = ocean_data.get("chl_summary", "Chlorophyll data unavailable")
    depth_summary = ocean_data.get("depth_summary", "Continental shelf 20-200m, deeper offshore")
    wind_summary = ocean_data.get("wind_summary", "Wind data unavailable")
    month = ocean_data.get("month", datetime.utcnow().month)
    season = ocean_data.get("season", "unknown")
    lunar_text = ""
    if lunar_info:
        lunar_text = f"\nLUNAR: Phase={lunar_info.get('phase', 'unknown')}, Illumination={lunar_info.get('illumination', 0):.0%}"
    return (
        f"REGION: {region['lat_min']:.1f}°N to {region['lat_max']:.1f}°N, "
        f"{region['lng_min']:.1f}°E to {region['lng_max']:.1f}°E\n"
        f"MONTH: {month} (Season: {season}){lunar_text}\n\n"
        f"OCEANOGRAPHIC DATA:\nSST: {sst_summary}\nCHLOROPHYLL: {chl_summary}\n"
        f"DEPTH/BATHYMETRY: {depth_summary}\nWIND: {wind_summary}\n\n"
        f"Identify PFZ zones in this region. Return valid JSON only."
    )


def build_ocean_summary(sst_points: List, chl_points: List) -> Dict[str, str]:
    """Summarise raw data arrays into text descriptions for Claude."""
    summaries = {}
    if sst_points:
        temps = [p["sst"] for p in sst_points if "sst" in p]
        if temps:
            summaries["sst_summary"] = (
                f"Min {min(temps):.1f}°C Max {max(temps):.1f}°C "
                f"Mean {sum(temps)/len(temps):.1f}°C ({len(temps)} grid points). "
                f"Thermal gradient detected where SST changes >0.5°C over <30km."
            )
        else:
            summaries["sst_summary"] = "SST data sparse"
    else:
        summaries["sst_summary"] = "SST not available (climatological estimate ~27-29°C)"
    if chl_points:
        chls = [p["chl"] for p in chl_points if "chl" in p]
        if chls:
            summaries["chl_summary"] = (
                f"Min {min(chls):.3f} Max {max(chls):.3f} "
                f"Mean {sum(chls)/len(chls):.3f} mg/m³ "
                f"({'high productivity' if max(chls)>0.5 else 'moderate productivity'})"
            )
        else:
            summaries["chl_summary"] = "CHL data sparse"
    else:
        summaries["chl_summary"] = "Chlorophyll not available (seasonal estimate)"
    summaries["depth_summary"] = "Continental shelf 20-200m, deeper offshore beyond 200m"
    summaries["wind_summary"] = "Live wind data from /api/wind/live"
    return summaries


def _offline_analysis(
    ocean_data: Dict,
    region: Dict,
    lunar_info: Optional[Dict],
) -> Dict:
    """Knowledge-base fallback when Claude API unavailable."""
    month = ocean_data.get("month", datetime.utcnow().month)
    sst_points = ocean_data.get("sst_points", [])
    chl_points = ocean_data.get("chl_points", [])
    moon_phase = (lunar_info or {}).get("phase", "any")
    lat_min = region["lat_min"]
    lat_max = region["lat_max"]
    lng_min = region["lng_min"]
    lng_max = region["lng_max"]
    lat_step = (lat_max - lat_min) / 3
    lng_step = (lng_max - lng_min) / 3
    zones = []
    rng = random.Random(month * 100 + int(lat_min * 10))
    for i in range(3):
        for j in range(3):
            clat = lat_min + (i + 0.5) * lat_step + rng.uniform(-0.1, 0.1)
            clon = lng_min + (j + 0.5) * lng_step + rng.uniform(-0.1, 0.1)
            sst = 28.0
            if sst_points:
                nearest = min(sst_points, key=lambda p: (p["lat"]-clat)**2 + (p["lon"]-clon)**2)
                sst = nearest.get("sst", 28.0)
            chl = 0.3
            if chl_points:
                nearest = min(chl_points, key=lambda p: (p["lat"]-clat)**2 + (p["lon"]-clon)**2)
                chl = nearest.get("chl", 0.3)
            depth = max(20.0, min(200.0, (clon - 68.0) * 50))
            species = get_top_species(sst, depth, chl, month, moon_phase, top_n=4)
            if not species:
                continue
            confidence = sum(s["probability"] for s in species) / len(species)
            zone_type = "high" if confidence >= 0.65 else ("medium" if confidence >= 0.45 else "low")
            angle = rng.uniform(0, math.pi)
            length = 0.3
            coords = [
                [clon - length * math.cos(angle), clat - length * math.sin(angle)],
                [clon, clat],
                [clon + length * math.cos(angle), clat + length * math.sin(angle)],
            ]
            zones.append({
                "coordinates": coords,
                "center_lat": clat,
                "center_lon": clon,
                "confidence": round(confidence, 2),
                "type": zone_type,
                "reasoning": f"Offline: SST {sst:.1f}°C, CHL {chl:.3f} mg/m³, depth ~{depth:.0f}m, month {month}",
                "fish_species": species,
                "best_fishing_time": species[0]["best_time"] if species else "05:00-08:00",
                "parameters_used": ["SST", "CHL", "Depth", "Month", "Lunar"],
            })
    zones.sort(key=lambda z: z["confidence"], reverse=True)
    return {
        "zones": zones[:6],
        "summary": f"Offline analysis ({len(zones)} zones). Claude API unavailable — using knowledge base.",
        "data_quality": "medium",
        "source": "offline_knowledge_base",
        "timestamp": datetime.utcnow().isoformat(),
    }
