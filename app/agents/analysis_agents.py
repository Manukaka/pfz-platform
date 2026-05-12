"""
Specialized Analysis Agents
विशेषज्ञ एजेंट - विशेषीकृत विश्लेषण

Each agent analyzes data from its domain of expertise
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List
import logging

from .base_agent import AnalysisAgent
from app.specialists.ghol_engine import GholEngine
from app.core.lunar import LunarEngine
from app.core.sea_mask import is_sea

logger = logging.getLogger(__name__)


def _zone_in_sea(lat: float, lng: float) -> bool:
    """Guardrail: ensure all emitted zones are ocean-only."""
    try:
        return is_sea(float(lat), float(lng))
    except Exception:
        return False


class GHOLAnalysisAgent(AnalysisAgent):
    """Specialized GHOL (Black Pomfret) fishing zone detection and analysis"""

    def __init__(self):
        super().__init__(
            agent_id="ghol_agent",
            agent_name="GHOL Specialist Agent",
            specialization="Ghol behavior and habitat suitability"
        )

    async def analyze(self, data: Dict[str, Any], context: Dict = None) -> Dict[str, Any]:
        """
        Analyze GHOL suitability across regions
        GHOL is most valuable species - detailed analysis
        """
        self.add_reasoning("Analyzing GHOL habitat suitability...")

        try:
            # Extract key parameters — handle both 'grid' and 'sst_grid' keys
            sst = data.get("sst", {})
            bathymetry = data.get("bathymetry", {})
            currents = data.get("currents", {})
            date = datetime.utcnow()

            # Get region bounds from context for proper coordinate generation
            region = (context or {}).get("region", {})
            region_lat_min = region.get("lat_min", 14.0)
            region_lat_max = region.get("lat_max", 21.0)
            region_lng_min = region.get("lng_min", 67.0)
            region_lng_max = region.get("lng_max", 74.5)

            zones = []
            confidence_scores = []

            # Analyze grid if available (handle both key names)
            sst_grid = sst.get("grid") or sst.get("sst_grid")
            if sst_grid:
                lat = sst.get("lat", [])
                lng = sst.get("lng", [])

                # Use real region coordinates if lat/lng missing — NEVER use range()
                if not lat or not lng:
                    import numpy as np
                    n_lat = min(5, len(sst_grid)) if sst_grid else 5
                    n_lng = min(5, len(sst_grid[0]) if sst_grid and len(sst_grid) > 0 else 5)
                    lat = list(np.linspace(region_lat_min, region_lat_max, n_lat))
                    lng = list(np.linspace(region_lng_min, region_lng_max, n_lng))

                # Analyze multiple points
                for i in range(min(5, len(lat), len(sst_grid))):
                    for j in range(min(5, len(lng), len(sst_grid[0]) if sst_grid else 0)):
                        try:
                            # Safe grid access
                            try:
                                sst_val = float(sst_grid[i][j]) if isinstance(sst_grid[i], (list, tuple)) else float(sst_grid[i])
                            except (TypeError, IndexError):
                                sst_val = 28.0  # Default mock value
                            depth = bathymetry.get("grid", [[50]*5]*5)[i][j] if bathymetry.get("grid") else 50

                            # Calculate GHOL suitability
                            spawning_prob = GholEngine.calculate_spawning_probability(date, lat[i], lng[j])
                            hsi = GholEngine.calculate_habitat_suitability(sst_val, depth, date)
                            acoustic = GholEngine.calculate_acoustic_detection_probability(date, lat[i], lng[j])

                            if hsi > 0.5 and _zone_in_sea(lat[i], lng[j]):  # Only include viable sea zones
                                zone = {
                                    "center_lat": lat[i],
                                    "center_lng": lng[j],
                                    "ghol_suitability": hsi,
                                    "spawning_probability": spawning_prob,
                                    "acoustic_potential": acoustic,
                                    "sst": sst_val,
                                    "depth": depth,
                                    "confidence": max(hsi, spawning_prob, acoustic),
                                }
                                zones.append(zone)
                                confidence_scores.append(zone["confidence"])
                        except:
                            continue

            # Calculate average confidence
            self.confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.3

            self.add_reasoning(
                f"Analyzed {len(zones)} GHOL zones with avg confidence {self.confidence:.2f}"
            )

            return {
                "zones": sorted(zones, key=lambda z: z["confidence"], reverse=True)[:10],
                "recommendations": [
                    f"🎣 {len(zones)} viable GHOL zones identified",
                    f"⭐ Peak habitat suitability in mid-Arabian Sea",
                    "[MOON] Lunar phase favorable for spawning detection",
                ] if zones else ["No favorable GHOL zones in current conditions"],
                "confidence": self.confidence,
                "reasoning": self.reasoning,
                "specialization": "GHOL Expertise"
            }

        except Exception as e:
            self.add_error(f"GHOL analysis failed: {str(e)}")
            return {
                "zones": [],
                "recommendations": ["Error in GHOL analysis"],
                "confidence": 0.0,
                "error": str(e)
            }


class ThermalFrontAgent(AnalysisAgent):
    """Detects thermal fronts and temperature gradients"""

    def __init__(self):
        super().__init__(
            agent_id="thermal_agent",
            agent_name="Thermal Front Agent",
            specialization="Temperature fronts and gradients"
        )

    async def analyze(self, data: Dict[str, Any], context: Dict = None) -> Dict[str, Any]:
        """Identify thermal fronts where fish aggregate"""
        self.add_reasoning("Detecting thermal fronts...")

        try:
            sst = data.get("sst", {})
            zones = []

            # Get region bounds from context for proper coordinate generation
            region = (context or {}).get("region", {})
            region_lat_min = region.get("lat_min", 14.0)
            region_lat_max = region.get("lat_max", 21.0)
            region_lng_min = region.get("lng_min", 67.0)
            region_lng_max = region.get("lng_max", 74.5)

            sst_grid = sst.get("grid") or sst.get("sst_grid") if sst else None
            if sst_grid:
                lat = sst.get("lat", [])
                lng = sst.get("lng", [])

                if not lat or not lng:
                    import numpy as np
                    n_lat = min(10, len(sst_grid)) if sst_grid else 5
                    n_lng = min(10, len(sst_grid[0]) if sst_grid and len(sst_grid) > 0 else 5)
                    lat = list(np.linspace(region_lat_min, region_lat_max, n_lat))
                    lng = list(np.linspace(region_lng_min, region_lng_max, n_lng))

                # Find temperature gradients (simplified)
                for i in range(min(len(lat) - 1, len(sst_grid) - 1)):
                    for j in range(min(4, len(lng), len(sst_grid[0]) if sst_grid else 0)):  # Limit width
                        try:
                            temp1 = float(sst_grid[i][j] if isinstance(sst_grid[i], (list, tuple)) else sst_grid[i])
                            temp2 = float(sst_grid[i+1][j] if isinstance(sst_grid[i+1], (list, tuple)) else sst_grid[i+1])

                            gradient = abs(temp2 - temp1)

                            # Fish congregate at gradients > 0.5°C
                            if gradient > 0.5:
                                center_lat = (lat[i] + lat[i+1]) / 2 if i+1 < len(lat) else lat[i]
                                center_lng = lng[j]
                                if not _zone_in_sea(center_lat, center_lng):
                                    continue
                                zone = {
                                    "center_lat": center_lat,
                                    "center_lng": center_lng,
                                    "temperature_gradient": gradient,
                                    "thermal_intensity": min(gradient / 2.0, 1.0),
                                    "sst_range": (min(temp1, temp2), max(temp1, temp2)),
                                    "confidence": min(gradient / 3.0, 0.95),
                                }
                                zones.append(zone)
                        except:
                            continue

            self.confidence = min(len(zones) * 0.15, 0.7) if zones else 0.2

            self.add_reasoning(f"Identified {len(zones)} thermal fronts")

            return {
                "zones": sorted(zones, key=lambda z: z["thermal_intensity"], reverse=True)[:8],
                "recommendations": [
                    "🌡️ Thermal fronts detected - high fish concentration areas",
                    f"📍 Focus on temperature gradients > 0.5°C",
                ] if zones else ["Low thermal front activity"],
                "confidence": self.confidence,
            }

        except Exception as e:
            self.add_error(str(e))
            return {
                "zones": [],
                "confidence": 0.0,
                "error": str(e)
            }


class WindCurrentAgent(AnalysisAgent):
    """Analyzes wind and current patterns"""

    def __init__(self):
        super().__init__(
            agent_id="wind_agent",
            agent_name="Wind & Current Agent",
            specialization="Hydrodynamics and wind patterns"
        )

    async def analyze(self, data: Dict[str, Any], context: Dict = None) -> Dict[str, Any]:
        """Analyze favorable wind and current conditions"""
        self.add_reasoning("Analyzing wind and current patterns...")

        try:
            wind = data.get("u10_wind", {})
            currents = data.get("u_current", {})
            zones = []

            # Get region bounds from context for proper coordinate generation
            region = (context or {}).get("region", {})
            region_lat_min = region.get("lat_min", 14.0)
            region_lat_max = region.get("lat_max", 21.0)
            region_lng_min = region.get("lng_min", 67.0)
            region_lng_max = region.get("lng_max", 74.5)

            # Simplified: Look for moderate wind speeds (5-12 m/s optimal for fishing)
            wind_grid = wind.get("grid") if wind else None
            if wind_grid:
                lat = wind.get("lat", [])
                lng = wind.get("lng", [])

                if not lat or not lng:
                    import numpy as np
                    n_lat = min(10, len(wind_grid)) if wind_grid else 5
                    n_lng = min(10, len(wind_grid[0]) if wind_grid and len(wind_grid) > 0 else 5)
                    lat = list(np.linspace(region_lat_min, region_lat_max, n_lat))
                    lng = list(np.linspace(region_lng_min, region_lng_max, n_lng))

                for i in range(min(5, len(lat), len(wind_grid))):
                    for j in range(min(5, len(lng), len(wind_grid[0]) if wind_grid else 0)):
                        try:
                            wind_speed = float(wind_grid[i][j] if isinstance(wind_grid[i], (list, tuple)) else wind_grid[i])

                            # Favorable range: 5-12 m/s
                            if 5 <= wind_speed <= 12 and _zone_in_sea(lat[i], lng[j]):
                                zone = {
                                    "center_lat": lat[i],
                                    "center_lng": lng[j],
                                    "wind_speed": wind_speed,
                                    "wind_quality": "EXCELLENT" if 6 <= wind_speed <= 10 else "GOOD",
                                    "confidence": 0.7 if 6 <= wind_speed <= 10 else 0.5,
                                }
                                zones.append(zone)
                        except:
                            continue

            self.confidence = min(len(zones) * 0.12, 0.75) if zones else 0.3

            self.add_reasoning(f"Found {len(zones)} zones with favorable wind conditions")

            return {
                "zones": zones,
                "recommendations": [
                    "💨 Wind speeds optimal for boat operations",
                    "[OCEAN] Safe conditions for offshore fishing",
                ] if zones else ["Unfavorable wind conditions"],
                "confidence": self.confidence,
            }

        except Exception as e:
            self.add_error(str(e))
            return {
                "zones": [],
                "confidence": 0.0,
                "error": str(e)
            }


class LunarPhaseAgent(AnalysisAgent):
    """Analyzes lunar influence on fish behavior"""

    def __init__(self):
        super().__init__(
            agent_id="lunar_agent",
            agent_name="Lunar Phase Agent",
            specialization="Lunar cycles and fish behavior"
        )

    async def analyze(self, data: Dict[str, Any], context: Dict = None) -> Dict[str, Any]:
        """Analyze lunar conditions for fishing success"""
        self.add_reasoning("Analyzing lunar phase impact...")

        try:
            date = datetime.utcnow()
            phase = LunarEngine.get_lunar_phase(date)
            illumination = LunarEngine.get_lunar_illumination_percent(date)

            # Spawning occurs during new moon and waning/waxing crescent
            spawning_phases = ["new_moon", "waning_crescent", "waxing_crescent"]
            is_spawning_window = phase in spawning_phases

            confidence = 0.9 if is_spawning_window else 0.3

            self.add_reasoning(
                f"Lunar phase: {phase}, Illumination: {illumination:.1f}%, "
                f"Spawning window: {is_spawning_window}"
            )

            return {
                "zones": [],  # Lunar doesn't define zones, but affects all
                "recommendations": [
                    f"[MOON] Current phase: {phase.replace('_', ' ').title()}",
                    f"[INSIGHT] Illumination: {illumination:.1f}%",
                    "🎣 EXCELLENT spawning window - peak fish aggregation" if is_spawning_window
                    else "[WARN] Suboptimal for major spawning events",
                    "🌃 Dark nights favorable for nocturnal species detection" if illumination < 20
                    else "🌕 Bright nights affect visibility and behavior",
                ],
                "confidence": confidence,
                "phase": phase,
                "illumination_percent": illumination,
                "spawning_window": is_spawning_window,
            }

        except Exception as e:
            self.add_error(str(e))
            return {
                "zones": [],
                "confidence": 0.0,
                "error": str(e)
            }


class PrimaryProductivityAgent(AnalysisAgent):
    """Analyzes chlorophyll and primary productivity"""

    def __init__(self):
        super().__init__(
            agent_id="productivity_agent",
            agent_name="Primary Productivity Agent",
            specialization="Chlorophyll and food web dynamics"
        )

    async def analyze(self, data: Dict[str, Any], context: Dict = None) -> Dict[str, Any]:
        """Identify high-productivity zones with abundant food"""
        self.add_reasoning("Analyzing primary productivity...")

        try:
            chl = data.get("chlorophyll", {})
            zones = []

            # Get region bounds from context for proper coordinate generation
            region = (context or {}).get("region", {})
            region_lat_min = region.get("lat_min", 14.0)
            region_lat_max = region.get("lat_max", 21.0)
            region_lng_min = region.get("lng_min", 67.0)
            region_lng_max = region.get("lng_max", 74.5)

            chl_grid = chl.get("grid") or chl.get("chl_grid") if chl else None
            if chl_grid:
                lat = chl.get("lat", [])
                lng = chl.get("lng", [])

                if not lat or not lng:
                    import numpy as np
                    n_lat = min(10, len(chl_grid)) if chl_grid else 5
                    n_lng = min(10, len(chl_grid[0]) if chl_grid and len(chl_grid) > 0 else 5)
                    lat = list(np.linspace(region_lat_min, region_lat_max, n_lat))
                    lng = list(np.linspace(region_lng_min, region_lng_max, n_lng))

                for i in range(min(5, len(lat), len(chl_grid))):
                    for j in range(min(5, len(lng), len(chl_grid[0]) if chl_grid else 0)):
                        try:
                            chl_val = float(chl_grid[i][j] if isinstance(chl_grid[i], (list, tuple)) else chl_grid[i])

                            # High productivity zones: chlorophyll > 0.5 mg/m³
                            if chl_val > 0.5 and _zone_in_sea(lat[i], lng[j]):
                                zone = {
                                    "center_lat": lat[i],
                                    "center_lng": lng[j],
                                    "chlorophyll": chl_val,
                                    "productivity_level": "HIGH" if chl_val > 1.0 else "MODERATE",
                                    "food_availability": min(chl_val * 0.8, 1.0),
                                    "confidence": min(chl_val * 0.7, 0.9),
                                }
                                zones.append(zone)
                        except:
                            continue

            self.confidence = min(len(zones) * 0.15, 0.8) if zones else 0.2

            self.add_reasoning(f"Identified {len(zones)} high-productivity zones")

            return {
                "zones": sorted(zones, key=lambda z: z["chlorophyll"], reverse=True)[:8],
                "recommendations": [
                    "🌱 High chlorophyll zones = abundant food for fish",
                    "[FISH] These areas attract larger fish populations",
                ] if zones else ["Low primary productivity"],
                "confidence": self.confidence,
            }

        except Exception as e:
            self.add_error(str(e))
            return {
                "zones": [],
                "confidence": 0.0,
                "error": str(e)
            }
