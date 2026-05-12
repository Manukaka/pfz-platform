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

SYSTEM_PROMPT = f"""You are an expert fisheries oceanographer specialising in the Arabian Sea and West Coast India (Kerala, Karnataka, Goa, Maharashtra, Gujarat). You have 30 years of experience with INCOIS PFZ methodology, satellite oceanography, Indian monsoon dynamics, and fish behaviour.

FISH SPECIES ENCYCLOPEDIA (West Coast India):
{_FISH_ENCYCLOPEDIA}

FULL WEST COAST EEZ COVERAGE:
- Kerala (8°-12°N): Thiruvananthapuram, Kollam, Alappuzha, Kozhikode — upwelling-rich, Kerala mackerel, oil sardine, tuna
- Karnataka (12°-14.5°N): Mangalore, Karwar — mixed demersal-pelagic, Ghol, Pomfret
- Goa (14.5°-15.7°N): Panaji — Kingfish, Pomfret, Mackerel
- Maharashtra (15.7°-21°N): Ratnagiri, Mumbai, Thane — Surmai, Paplet, Ghol, Bombil
- Gujarat (21°-24°N): Saurashtra, Veraval, Kutch — Kati, Shrimp, Hilsa

REGION-SPECIFIC UPWELLING KNOWLEDGE:
- Kerala/Karnataka coast (Jun-Sep SW Monsoon): Strongest upwelling on entire west coast. SST drops 3-5°C, CHL spikes to 2-5 mg/m³. Peak zone for oil sardine, mackerel.
- Maharashtra (Oct-Mar NE Monsoon): Thermal fronts at 50-100km offshore. Surmai, Pomfret peak.
- Gujarat (Nov-Feb): Shallow shelf, Saurashtra Bank productive. Kati/Dhoma target species.

YOUR TASK: Given real-time oceanographic data, identify Potential Fishing Zones (PFZ) with scientific reasoning. Cover the FULL west coast — do not restrict to Maharashtra only.

OUTPUT FORMAT (respond with valid JSON only, no markdown):
{{
  "zones": [
    {{
      "coordinates": [[lon, lat], [lon2, lat2]],
      "center_lat": 17.5,
      "center_lon": 70.5,
      "confidence": 0.84,
      "type": "high",
      "region": "Maharashtra",
      "reasoning": "Strong thermal front at 28.1°C matching Surmai feeding threshold. CHL 0.45 mg/m³ indicates moderate productivity. SW wind 6 m/s driving coastal upwelling.",
      "fish_species": [
        {{"name_en": "Surmai", "name_mr": "सुरमई", "name_hi": "सुरमई", "name_kok": "सुरमयो", "icon": "🐠", "probability": 0.84, "reasoning": "SST 28.1°C optimal, peak Oct-Mar season, new moon favourable"}}
      ],
      "best_fishing_time": "05:00-08:00",
      "wind_risk": "low",
      "parameters_used": ["SST", "CHL", "Wind", "Depth", "Lunar", "Month"]
    }}
  ],
  "summary": "5 zones across Kerala-Maharashtra coast...",
  "data_quality": "high"
}}

RULES:
- All coordinates must be in ocean (Arabian Sea/Lakshadweep Sea), never on land
- Full latitude range: 8.0-24.0°N, Longitude range: 66.0-77.5°E
- Return 4-10 zones spread across the full west coast, not clustered in one area
- Each zone must include region field (Kerala/Karnataka/Goa/Maharashtra/Gujarat)
- Each zone reasoning must cite specific SST, CHL, wind values given in the prompt
- Include wind_risk: low/moderate/high based on wind speed (>7m/s = moderate, >12m/s = high)
- Fish species must include name_kok (Konkani) where known
- Fish species probabilities must be scientifically justified with season + SST + CHL
- type must be one of: high, medium, low
- Do NOT place zones on land: Karnataka coast >74.5°E is land, Kerala coast >77°E is land"""


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
    wave_summary = ocean_data.get("wave_summary", "Wave data unavailable")
    current_summary = ocean_data.get("current_summary", "Current data unavailable")
    upwelling_summary = ocean_data.get("upwelling_summary", "")
    tidal_summary = ocean_data.get("tidal_summary", "")
    month = ocean_data.get("month", datetime.utcnow().month)
    season = _get_season(month)
    lunar_text = ""
    if lunar_info:
        phase = lunar_info.get("phase", "unknown")
        illum = lunar_info.get("illumination", 0)
        tide_note = "Spring tides (strong currents)" if illum > 0.85 or illum < 0.1 else (
                    "Neap tides (calm)" if 0.4 < illum < 0.6 else "Moderate tides")
        lunar_text = f"\nLUNAR: Phase={phase}, Illumination={illum:.0%} — {tide_note}"

    lines = [
        f"REGION: {region['lat_min']:.1f}°N–{region['lat_max']:.1f}°N, "
        f"{region['lng_min']:.1f}°E–{region['lng_max']:.1f}°E",
        f"DATE: Month {month} (Season: {season}){lunar_text}",
        "",
        "OCEANOGRAPHIC DATA:",
        f"SST: {sst_summary}",
        f"CHLOROPHYLL: {chl_summary}",
        f"WIND: {wind_summary}",
        f"WAVE HEIGHT: {wave_summary}",
        f"CURRENT: {current_summary}",
        f"DEPTH/BATHYMETRY: {depth_summary}",
    ]
    if upwelling_summary:
        lines.append(f"UPWELLING INDEX: {upwelling_summary}")
    if tidal_summary:
        lines.append(f"TIDAL STATE: {tidal_summary}")

    lines += [
        "",
        "FISHING SAFETY GUIDANCE:",
        "- Wind >12 m/s: HIGH RISK — mark zone wind_risk=high, recommend postponing",
        "- Wind 7-12 m/s: MODERATE RISK — mark wind_risk=moderate, experienced boats only",
        "- Wave >2.5m: Dangerous for small vessels (<10m)",
        "- Current >1.5 knots with onshore wind: Rip current risk near coast",
        "",
        "Identify 4-10 PFZ zones spread across the full west coast (Kerala to Gujarat). "
        "Prioritise zones with thermal fronts, upwelling edges, CHL gradients, and depth contour transitions. "
        "Return valid JSON only.",
    ]
    return "\n".join(lines)


def _get_season(month: int) -> str:
    if month in (6, 7, 8, 9):    return "SW Monsoon (Jun-Sep) — peak upwelling, Kerala-Karnataka"
    if month in (10, 11):         return "NE Monsoon onset (Oct-Nov) — thermal fronts build"
    if month in (12, 1, 2):       return "NE Monsoon (Dec-Feb) — Maharashtra/Gujarat peak"
    if month in (3, 4, 5):        return "Pre-monsoon (Mar-May) — variable, Rawas/Ghol season"
    return "unknown"


def build_ocean_summary(
    sst_points: List,
    chl_points: List,
    wind_data: Optional[Dict] = None,
    wave_data: Optional[Dict] = None,
    current_data: Optional[Dict] = None,
) -> Dict[str, str]:
    """Summarise raw data arrays into text descriptions for Claude."""
    summaries = {}

    # SST summary + thermal front detection
    if sst_points:
        temps = [p["sst"] for p in sst_points if "sst" in p and 15 < p["sst"] < 36]
        if temps:
            mean_t = sum(temps) / len(temps)
            range_t = max(temps) - min(temps)
            front_note = "Strong thermal fronts present (ΔT>3°C)" if range_t > 3 else (
                         "Moderate thermal gradient (ΔT 1-3°C)" if range_t > 1 else "Weak gradient")
            summaries["sst_summary"] = (
                f"Min {min(temps):.1f}°C Max {max(temps):.1f}°C "
                f"Mean {mean_t:.1f}°C ({len(temps)} pts). {front_note}."
            )
        else:
            summaries["sst_summary"] = "SST data sparse"
    else:
        summaries["sst_summary"] = "SST unavailable (climatological estimate ~27-29°C)"

    # CHL summary + productivity classification
    if chl_points:
        chls = [p["chl"] for p in chl_points if "chl" in p and p["chl"] > 0]
        if chls:
            mean_c = sum(chls) / len(chls)
            productivity = "very high (upwelling)" if mean_c > 1.5 else (
                           "high" if mean_c > 0.5 else (
                           "moderate" if mean_c > 0.2 else "low (oligotrophic)"))
            summaries["chl_summary"] = (
                f"Min {min(chls):.3f} Max {max(chls):.3f} "
                f"Mean {mean_c:.3f} mg/m³ — {productivity}."
            )
        else:
            summaries["chl_summary"] = "CHL data sparse"
    else:
        summaries["chl_summary"] = "Chlorophyll unavailable (seasonal estimate)"

    # Wind summary + safety assessment
    if wind_data and "u_data" in wind_data and "v_data" in wind_data:
        try:
            u_vals = wind_data["u_data"]
            v_vals = wind_data["v_data"]
            speeds = [math.sqrt(u**2 + v**2) for u, v in zip(u_vals, v_vals)]
            mean_spd = sum(speeds) / len(speeds)
            max_spd = max(speeds)
            safety = "HIGH RISK" if max_spd > 12 else ("MODERATE" if max_spd > 7 else "LOW RISK")
            summaries["wind_summary"] = (
                f"Mean {mean_spd:.1f} m/s Max {max_spd:.1f} m/s — Safety: {safety}."
            )
            # Upwelling index: offshore wind (positive U = eastward) reduces upwelling
            # Onshore SW wind drives Kerala-Karnataka upwelling
            mean_u = sum(u_vals) / len(u_vals)
            mean_v = sum(v_vals) / len(v_vals)
            upwelling_strength = "STRONG" if mean_u < -3 else ("MODERATE" if mean_u < -1 else "WEAK")
            summaries["upwelling_summary"] = (
                f"SW wind component {abs(mean_u):.1f} m/s westerly — upwelling {upwelling_strength}. "
                f"Kerala-Karnataka upwelling {'active' if mean_u < -2 else 'suppressed'}."
            )
        except Exception:
            summaries["wind_summary"] = "Wind data format error"
    else:
        summaries["wind_summary"] = "Wind data unavailable — use seasonal estimate"

    # Wave summary
    if wave_data and "wave_height" in wave_data:
        try:
            wh = wave_data["wave_height"]
            if isinstance(wh, list):
                mean_wh = sum(wh) / len(wh)
                max_wh = max(wh)
            else:
                mean_wh = max_wh = float(wh)
            safety = "DANGEROUS for small boats" if max_wh > 2.5 else (
                     "Caution advised" if max_wh > 1.5 else "Favourable")
            summaries["wave_summary"] = f"Sig. wave height {mean_wh:.1f}m (max {max_wh:.1f}m) — {safety}."
        except Exception:
            summaries["wave_summary"] = "Wave data unavailable"
    else:
        summaries["wave_summary"] = "Wave data unavailable — check Open-Meteo Marine"

    # Current summary
    if current_data and "u_data" in current_data:
        try:
            cu = current_data["u_data"]
            cv = current_data.get("v_data", [0.0] * len(cu))
            speeds = [math.sqrt(u**2 + v**2) for u, v in zip(cu, cv)]
            mean_spd = sum(speeds) / len(speeds)
            summaries["current_summary"] = (
                f"Mean current {mean_spd:.2f} m/s ({mean_spd*1.94:.1f} knots). "
                f"{'Strong — convergence zones likely' if mean_spd > 0.5 else 'Moderate — check shelf edge'}."
            )
        except Exception:
            summaries["current_summary"] = "Current data format error"
    else:
        summaries["current_summary"] = "Current data unavailable — seasonal estimate: 0.3-0.8 knots"

    summaries["depth_summary"] = (
        "Kerala/Karnataka: shelf narrows 10-30km. "
        "Maharashtra: 50-80km wide shelf, 100m contour at ~70.5°E. "
        "Gujarat: Saurashtra Bank 40-60m, productive."
    )
    return summaries


def _offline_analysis(
    ocean_data: Dict,
    region: Dict,
    lunar_info: Optional[Dict],
) -> Dict:
    """Knowledge-base fallback when Claude API unavailable. Covers full west coast."""
    from app.core.sea_mask import is_sea
    month = ocean_data.get("month", datetime.utcnow().month)
    sst_points = ocean_data.get("sst_points", [])
    chl_points = ocean_data.get("chl_points", [])
    moon_phase = (lunar_info or {}).get("phase", "any")

    # Fixed candidate centres across full west coast — pre-validated as sea points
    # (lat, lon, region_name, coast_lon_offset)
    WEST_COAST_CANDIDATES = [
        # Kerala
        (8.5,  75.5,  "Kerala"),
        (9.5,  75.0,  "Kerala"),
        (10.5, 74.5,  "Kerala"),
        (11.5, 74.0,  "Kerala"),
        # Karnataka
        (12.5, 73.5,  "Karnataka"),
        (13.5, 73.0,  "Karnataka"),
        # Goa
        (15.0, 72.8,  "Goa"),
        # Maharashtra
        (16.0, 72.5,  "Maharashtra"),
        (17.0, 71.5,  "Maharashtra"),
        (17.5, 70.5,  "Maharashtra"),
        (18.5, 70.0,  "Maharashtra"),
        (19.5, 69.5,  "Maharashtra"),
        # Gujarat
        (21.5, 69.0,  "Gujarat"),
        (22.5, 67.5,  "Gujarat"),
    ]

    rng = random.Random(month * 100 + int(region["lat_min"] * 10))
    zones = []

    for clat, clon, region_name in WEST_COAST_CANDIDATES:
        # Filter to requested region bounds
        if not (region["lat_min"] <= clat <= region["lat_max"]):
            continue
        if not (region["lng_min"] <= clon <= region["lng_max"]):
            continue
        # Sea mask validation
        if not is_sea(clat, clon):
            continue

        # Add small jitter (seeded so reproducible per day)
        clat += rng.uniform(-0.2, 0.2)
        clon += rng.uniform(-0.2, 0.2)

        # Nearest SST/CHL
        sst = 28.0
        if sst_points:
            nearest = min(sst_points, key=lambda p: (p["lat"]-clat)**2 + (p["lon"]-clon)**2)
            sst = nearest.get("sst", 28.0)
        chl = 0.3
        if chl_points:
            nearest = min(chl_points, key=lambda p: (p["lat"]-clat)**2 + (p["lon"]-clon)**2)
            chl = nearest.get("chl", 0.3)

        # Depth estimate from coast distance
        coast_lons = {8: 77.0, 10: 76.1, 12: 74.7, 14: 74.2, 16: 73.4, 18: 73.0, 20: 72.7, 22: 70.5}
        coast_lon = min(coast_lons.values(), key=lambda cl: abs(cl - clon))
        depth = max(20.0, min(300.0, abs(clon - coast_lon) * 80))

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
            "center_lat": round(clat, 4),
            "center_lon": round(clon, 4),
            "confidence": round(confidence, 2),
            "type": zone_type,
            "region": region_name,
            "wind_risk": "low",
            "reasoning": (
                f"Offline knowledge base: SST {sst:.1f}°C, CHL {chl:.3f} mg/m³, "
                f"depth ~{depth:.0f}m, month {month}, {region_name} coast."
            ),
            "fish_species": species,
            "best_fishing_time": species[0].get("best_time", "05:00-08:00") if species else "05:00-08:00",
            "parameters_used": ["SST", "CHL", "Depth", "Month", "Lunar"],
        })

    zones.sort(key=lambda z: z["confidence"], reverse=True)
    return {
        "zones": zones[:8],
        "summary": (
            f"Offline analysis: {len(zones[:8])} zones across Kerala–Gujarat. "
            "Claude API unavailable — using knowledge base."
        ),
        "data_quality": "medium",
        "source": "offline_knowledge_base",
        "timestamp": datetime.utcnow().isoformat(),
    }
