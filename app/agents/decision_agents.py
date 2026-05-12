"""
Decision & Synthesis Agents
निर्णय एजेंट - सिंथेसिस और सिफारिशें

Agents that synthesize insights from specialized agents into actionable recommendations
"""

from datetime import datetime
from typing import Dict, Any, List
import logging

from .base_agent import DecisionAgent

logger = logging.getLogger(__name__)


class FishingRecommendationSynthesizer(DecisionAgent):
    """Synthesizes all agent insights into final fishing recommendations"""

    def __init__(self):
        super().__init__(
            agent_id="recommendation_agent",
            agent_name="Fishing Recommendation Synthesizer",
            specialization="Multi-agent synthesis and recommendations"
        )

    async def synthesize(self, agent_results: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Combine all agent analyses into prioritized fishing zones and recommendations
        """
        self.add_reasoning("Beginning multi-agent synthesis...")

        try:
            # Collect zones from all analysis agents
            all_zones = {}  # key: (lat, lng) -> zone data

            for agent_id, result in agent_results.items():
                zones = result.get("zones", [])
                confidence = result.get("confidence", 0.5)

                self.add_reasoning(f"Processing {agent_id}: {len(zones)} zones, confidence {confidence:.2f}")

                for zone in zones:
                    key = (round(zone.get("center_lat", 0), 2), round(zone.get("center_lng", 0), 2))

                    if key not in all_zones:
                        all_zones[key] = {
                            "lat": zone.get("center_lat", 0),
                            "lng": zone.get("center_lng", 0),
                            "votes": 0,
                            "supporting_agents": [],
                            "agent_confidences": [],
                            "attributes": {}
                        }

                    all_zones[key]["votes"] += 1
                    all_zones[key]["supporting_agents"].append(agent_id)
                    all_zones[key]["agent_confidences"].append(confidence)

                    # Merge zone attributes
                    for key_attr, val in zone.items():
                        if key_attr not in ["center_lat", "center_lng"]:
                            all_zones[key]["attributes"][key_attr] = val

            # Score zones by consensus and confidence
            final_zones = []
            total_agents = len(agent_results)

            for (lat, lng), zone_data in all_zones.items():
                # Consensus score: how many agents mentioned it
                consensus_score = zone_data["votes"] / total_agents

                # Confidence score: average confidence of supporting agents
                avg_confidence = sum(zone_data["agent_confidences"]) / len(zone_data["agent_confidences"]) if zone_data["agent_confidences"] else 0.3

                # Combined score (60% consensus, 40% confidence)
                combined_score = consensus_score * 0.6 + avg_confidence * 0.4

                final_zone = {
                    "center_lat": zone_data["lat"],
                    "center_lng": zone_data["lng"],
                    "consensus_score": combined_score,
                    "agent_votes": zone_data["votes"],
                    "supporting_agents": zone_data["supporting_agents"],
                    "confidence": avg_confidence,
                    "attributes": zone_data["attributes"],
                }

                final_zones.append(final_zone)

            # Sort by consensus
            final_zones.sort(key=lambda z: z["consensus_score"], reverse=True)
            top_zones = final_zones[:10]

            self.add_reasoning(f"Identified {len(top_zones)} consensus fishing zones")

            # Generate recommendations
            recommendations = self._generate_recommendations(
                top_zones, agent_results, total_agents
            )

            self.confidence = (
                sum(z["consensus_score"] for z in top_zones) / len(top_zones)
                if top_zones else 0.3
            )

            return {
                "zones": top_zones,
                "recommendations": recommendations,
                "confidence": self.confidence,
                "summary": {
                    "total_zones_analyzed": len(all_zones),
                    "consensus_zones": len(top_zones),
                    "average_agent_agreement": sum(z["agent_votes"] for z in top_zones) / len(top_zones) / total_agents if top_zones else 0,
                    "reasoning": self.reasoning,
                }
            }

        except Exception as e:
            self.add_error(f"Synthesis failed: {str(e)}")
            return {
                "zones": [],
                "recommendations": ["Error in synthesis"],
                "confidence": 0.0,
                "error": str(e)
            }

    def _generate_recommendations(self, zones: List[Dict], agent_results: Dict, total_agents: int) -> List[str]:
        """Generate human-readable recommendations"""
        recommendations = []

        if not zones:
            return ["[FAIL] No favorable fishing zones in current conditions"]

        top_zone = zones[0]
        agreements = top_zone["agent_votes"]
        agreement_pct = (agreements / total_agents) * 100

        # Zone quality assessment
        if agreement_pct >= 80:
            recommendations.append(f"[TARGET] EXCELLENT CONSENSUS - {agreements}/{total_agents} agents agree")
        elif agreement_pct >= 60:
            recommendations.append(f"[OK] STRONG CONSENSUS - {agreements}/{total_agents} agents agree")
        else:
            recommendations.append(f"ℹ️ MODERATE AGREEMENT - {agreements}/{total_agents} agents agree")

        # Location recommendation
        recommendations.append(
            f"📍 Priority Zone: {top_zone['center_lat']:.2f}°N, {top_zone['center_lng']:.2f}°E"
        )

        # Condition summary
        cond_summary = self._summarize_conditions(top_zone, agent_results)
        recommendations.extend(cond_summary)

        # Specialist insights
        insights = self._extract_specialist_insights(zones, agent_results)
        recommendations.extend(insights)

        return recommendations

    def _summarize_conditions(self, zone: Dict, agent_results: Dict) -> List[str]:
        """Summarize environmental conditions"""
        conditions = []

        attrs = zone.get("attributes", {})

        if "sst" in attrs:
            sst = attrs["sst"]
            conditions.append(f"🌡️ Sea Temp: {sst:.1f}°C")

        if "ghol_suitability" in attrs:
            ghol_suit = attrs["ghol_suitability"]
            if ghol_suit > 0.7:
                conditions.append("[FISH] GHOL HABITAT EXCELLENT")
            elif ghol_suit > 0.5:
                conditions.append("[FISH] GHOL HABITAT GOOD")

        if "wind_speed" in attrs:
            wind = attrs["wind_speed"]
            conditions.append(f"💨 Wind: {wind:.1f} m/s")

        if "chlorophyll" in attrs:
            chl = attrs["chlorophyll"]
            if chl > 0.8:
                conditions.append("🌱 HIGH FOOD AVAILABILITY")

        return conditions

    def _extract_specialist_insights(self, zones: List[Dict], agent_results: Dict) -> List[str]:
        """Extract insights from specialized agents"""
        insights = []

        # GHOL agent insights
        if "ghol_agent" in agent_results:
            ghol = agent_results["ghol_agent"]
            if ghol.get("confidence", 0) > 0.6:
                insights.append(f"⭐ GHOL specialist: {len(ghol.get('zones', []))} viable zones detected")

        # Lunar agent insights
        if "lunar_agent" in agent_results:
            lunar = agent_results["lunar_agent"]
            if lunar.get("spawning_window"):
                insights.append("[MOON] SPAWNING WINDOW ACTIVE - Peak fishing period")

        # Thermal agent insights
        if "thermal_agent" in agent_results:
            thermal = agent_results["thermal_agent"]
            if thermal.get("confidence", 0) > 0.5:
                insights.append(f"🌡️ Thermal fronts detected - {len(thermal.get('zones', []))} areas")

        # Wind agent insights
        if "wind_agent" in agent_results:
            wind = agent_results["wind_agent"]
            if wind.get("confidence", 0) > 0.5:
                insights.append("💨 Wind conditions FAVORABLE for operations")

        return insights


class RiskAssessmentAgent(DecisionAgent):
    """Assesses safety and risks for fishing operations"""

    def __init__(self):
        super().__init__(
            agent_id="risk_agent",
            agent_name="Risk Assessment Agent",
            specialization="Safety and operational risk evaluation"
        )

    async def synthesize(self, agent_results: Dict[str, Dict]) -> Dict[str, Any]:
        """Assess risks and safety conditions"""
        self.add_reasoning("Performing risk assessment...")

        try:
            risks = []
            warnings = []

            # Check wind conditions
            if "wind_agent" in agent_results:
                wind = agent_results["wind_agent"]
                zones = wind.get("zones", [])

                if not zones:
                    warnings.append("[WARN] High wind speeds - unsafe for small boats")
                    risks.append({"type": "weather", "severity": "high"})

            # Check thermal conditions
            if "thermal_agent" in agent_results:
                thermal = agent_results["thermal_agent"]
                if thermal.get("confidence", 0) < 0.3:
                    warnings.append("[WARN] Unstable thermal patterns - unpredictable conditions")

            # Overall safety assessment
            risk_level = "LOW" if len(risks) == 0 else "MEDIUM" if len(risks) == 1 else "HIGH"

            self.confidence = 0.85 if risk_level == "LOW" else 0.70 if risk_level == "MEDIUM" else 0.60

            self.add_reasoning(f"Risk level: {risk_level}, Warnings: {len(warnings)}")

            return {
                "risk_level": risk_level,
                "warnings": warnings,
                "recommendations": [
                    "[OK] All systems clear for fishing operations" if risk_level == "LOW"
                    else "[WARN] Proceed with caution - some operational constraints" if risk_level == "MEDIUM"
                    else "[ERROR] High-risk conditions - consider postponing operations"
                ],
                "confidence": self.confidence,
                "details": {
                    "identified_risks": risks,
                    "safety_warnings": warnings,
                }
            }

        except Exception as e:
            self.add_error(str(e))
            return {
                "risk_level": "UNKNOWN",
                "confidence": 0.0,
                "error": str(e)
            }


class EconomicAnalysisAgent(DecisionAgent):
    """Analyzes economic viability of fishing trips"""

    def __init__(self):
        super().__init__(
            agent_id="economic_agent",
            agent_name="Economic Analysis Agent",
            specialization="Trip profitability and resource optimization"
        )

    async def synthesize(self, agent_results: Dict[str, Dict]) -> Dict[str, Any]:
        """Assess economic viability"""
        self.add_reasoning("Analyzing economic feasibility...")

        try:
            # Extract zone quality
            ghol_zones = agent_results.get("ghol_agent", {}).get("zones", [])
            zone_quality = "EXCELLENT" if ghol_zones else "GOOD"

            # Estimate catch potential
            expected_catch = len(ghol_zones) * 50  # Mock calculation

            # Estimate profitability
            from app.core.economic import EconomicCalculator

            roi = EconomicCalculator.calculate_trip_roi(
                catch_composition={"ghol": expected_catch},
                distance_km=90,
                boat_type="medium_boat",
                num_crew=4,
                landing_port="Ratnagiri",
                trip_days=0.75
            )

            roi_percent = roi.get("profit", {}).get("roi_percentage", 0)
            profitability = "EXCELLENT" if roi_percent > 50 else "GOOD" if roi_percent > 25 else "FAIR"

            self.confidence = min(roi_percent / 100, 1.0)

            self.add_reasoning(f"Estimated ROI: {roi_percent:.1f}%, Profitability: {profitability}")

            return {
                "trip_roi": roi,
                "profitability_rating": profitability,
                "confidence": self.confidence,
                "recommendations": [
                    f"💰 Expected ROI: {roi_percent:.1f}%",
                    f"[TARGET] Zone quality: {zone_quality}",
                    "[OK] Trip is economically viable" if profitability != "FAIR" else "[WARN] Marginal profitability",
                ]
            }

        except Exception as e:
            self.add_error(str(e))
            logger.warning(f"Economic analysis failed: {str(e)}")
            return {
                "profitability_rating": "UNKNOWN",
                "confidence": 0.0,
                "recommendations": ["Unable to calculate economic viability"],
                "error": str(e)
            }
