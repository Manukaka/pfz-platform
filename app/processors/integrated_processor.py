"""
SAMUDRA AI — Integrated Processor
एकीकृत प्रणाली - मुख्य + विशेषज्ञ

Combines main PFZ processor with specialist engines (GHOL, future species)
Provides unified interface for complete intelligent fishing platform

Workflow:
1. Main PFZ detection (all 5 oceanographic methods)
2. Specialist analysis (GHOL acoustic, behavioral, economic optimization)
3. Integrated recommendations (best zones for each target)
4. Economic prioritization (expected profit per species/zone)
5. Trip planning (detailed operations for fishermen)
"""

from datetime import datetime
from typing import Dict, List, Optional

from app.processors.pfz_processor import PFZProcessor
from app.specialists.ghol_engine import GholEngine
from app.specialists.ghol_behavior import GholBehavior


class IntegratedProcessor:
    """
    Unified processor combining general PFZ detection with specialist engines

    Orchestrates complete intelligent fishing platform:
    - Detects fishing zones using oceanographic methods
    - Applies species-specific intelligence (GHOL, etc.)
    - Generates economic recommendations
    - Plans operational trips for fishermen
    """

    def __init__(self, date: datetime = None):
        """
        Initialize integrated processor

        Args:
            date: Processing date (defaults to today UTC)
        """
        self.date = date if date else datetime.utcnow()
        self.pfz_results = None
        self.specialist_results = {}
        self.final_recommendations = None

    def process_complete(self, lat_min: float = 14.0, lat_max: float = 21.0,
                        lng_min: float = 67.0, lng_max: float = 74.5,
                        target_species: List[str] = None) -> Dict:
        """
        Execute complete integrated processing workflow

        Args:
            lat_min, lat_max, lng_min, lng_max: Geographic region
            target_species: List of species to focus on (["ghol"] for GHOL-focused, None for all)

        Returns:
            Dict with complete analysis including general PFZ zones, specialist insights,
            and integrated recommendations
        """
        print("\n" + "="*70)
        print("SAMUDRA AI — Integrated Processor (PFZ + GHOL)")
        print("="*70)

        if target_species is None:
            target_species = ["ghol", "papalet", "bangada"]

        # STEP 1: Run main PFZ processor
        print("\n[STEP 1] Running Main PFZ Processor...")
        pfz_processor = PFZProcessor(self.date)
        self.pfz_results = pfz_processor.process(lat_min, lat_max, lng_min, lng_max)
        print(f"[OK] Detected {len(self.pfz_results['pfz_zones'])} PFZ zones")

        # STEP 2: Apply GHOL specialist analysis
        print("\n[STEP 2] Applying GHOL Specialist Engine...")
        ghol_zones = GholEngine.find_best_ghol_zones(
            self.pfz_results["pfz_zones"],
            self.date
        )
        print(f"[OK] Identified {len(ghol_zones)} zones optimal for GHOL targeting")

        # STEP 3: Generate GHOL behavior forecasts
        print("\n[STEP 3] Generating Behavioral Forecasts...")
        if ghol_zones:
            top_ghol_zone = ghol_zones[0]
            behavior_forecast = GholBehavior.generate_behavior_forecast(
                self.date,
                top_ghol_zone["center_lat"],
                top_ghol_zone["center_lng"],
                days_ahead=7
            )
            print(f"[OK] Generated 7-day behavioral forecast for top GHOL zone")
        else:
            behavior_forecast = []

        # STEP 4: Identify acoustic hotspots
        print("\n[STEP 4] Finding Acoustic Hotspots...")
        acoustic_hotspots = GholBehavior.identify_acoustic_hotspots(
            self.date,
            (lat_min, lat_max),
            (lng_min, lng_max)
        )
        print(f"[OK] Identified {len(acoustic_hotspots)} acoustic detection hotspots")

        # STEP 5: Generate integrated recommendations
        print("\n[STEP 5] Generating Integrated Recommendations...")
        integrated_recs = self._generate_integrated_recommendations(
            ghol_zones,
            behavior_forecast,
            acoustic_hotspots
        )
        print(f"[OK] Generated recommendations for {len(integrated_recs)} top opportunities")

        # Compile final output
        final_output = {
            "date": self.date.strftime("%Y-%m-%d"),
            "region": {
                "lat_min": lat_min,
                "lat_max": lat_max,
                "lng_min": lng_min,
                "lng_max": lng_max,
            },
            "processing_summary": {
                "general_pfz_zones": len(self.pfz_results["pfz_zones"]),
                "ghol_optimized_zones": len(ghol_zones),
                "acoustic_hotspots": len(acoustic_hotspots),
                "forecast_days": 7,
            },
            "pfw_zones": self.pfz_results["pfz_zones"][:5],  # Top 5 general zones
            "ghol_zones": ghol_zones[:5],  # Top 5 GHOL zones
            "acoustic_hotspots": acoustic_hotspots[:5],  # Top 5 acoustic spots
            "behavioral_forecast": behavior_forecast[:3],  # 3-day forecast
            "integrated_recommendations": integrated_recs[:10],  # Top 10 opportunities
            "species_insights": self.pfz_results["species_insights"],
        }

        print("\n[OK] Integrated processing complete!")
        print("="*70 + "\n")

        return final_output

    def generate_trip_plans(self, integrated_results: Dict,
                           num_plans: int = 5) -> List[Dict]:
        """
        Generate detailed trip plans from integrated results

        Args:
            integrated_results: Output from process_complete()
            num_plans: Number of trip plans to generate

        Returns:
            List of detailed trip plans for fishermen
        """
        trip_plans = []

        # Get top GHOL zones
        ghol_zones = integrated_results.get("ghol_zones", [])

        for i, zone in enumerate(ghol_zones[:num_plans]):
            trip_plan = GholEngine.generate_ghol_trip_plan(zone, self.date)
            trip_plans.append(trip_plan)

        return trip_plans

    def _generate_integrated_recommendations(self, ghol_zones: List[Dict],
                                            forecast: List[Dict],
                                            hotspots: List[Dict]) -> List[Dict]:
        """
        Generate integrated recommendations combining all analyses

        Args:
            ghol_zones: GHOL-optimized zones
            forecast: Behavioral forecast
            hotspots: Acoustic hotspots

        Returns:
            List of integrated recommendations with priority ranking
        """
        recommendations = []

        for zone in ghol_zones[:5]:  # Top 5 zones
            zone_id = zone.get("zone_id", 0)
            lat = zone["center_lat"]
            lng = zone["center_lng"]

            # Find matching forecast for this zone
            zone_forecast = None
            for f in forecast:
                if f.get("behavior_state") in ["spawning", "feeding"]:
                    zone_forecast = f
                    break

            # Calculate priority score
            priority_score = (
                zone["ghol_targeting_score"] * 0.4 +
                (zone["spawning_probability"] * 0.3) +
                zone["habitat_suitability"] * 0.3
            )

            recommendation = {
                "priority_rank": len(recommendations) + 1,
                "zone_id": zone_id,
                "coordinates": {"lat": lat, "lng": lng},
                "ghol_targeting_score": zone["ghol_targeting_score"],
                "spawning_window_active": zone["is_spawning_window"],
                "expected_behavior": zone_forecast.get("fishing_quality", "Unknown") if zone_forecast else "Unknown",
                "recommended_gear": ["Gill net (32-40mm)", "Handlines", "Hydrophone if available"],
                "best_fishing_hours": "05:00-07:00, 17:00-19:00, 21:00-04:00",
                "priority_score": priority_score,
                "action": self._priority_action(priority_score),
            }

            recommendations.append(recommendation)

        # Sort by priority
        recommendations.sort(key=lambda x: x["priority_score"], reverse=True)

        return recommendations

    def _priority_action(self, score: float) -> str:
        """Determine action level based on priority score"""
        if score > 0.75:
            return "[TARGET] GO NOW - Optimal conditions, immediate departure recommended"
        elif score > 0.6:
            return "[OK] GO - Excellent opportunity, plan departure today"
        elif score > 0.45:
            return "[WARN] MONITOR - Good opportunity, wait for tide/weather confirmation"
        else:
            return "[FAIL] WAIT - Marginal conditions, check again tomorrow"


def run_integrated_analysis(date: datetime = None,
                           region: Dict = None) -> Dict:
    """
    Quick function to run integrated PFZ + GHOL analysis

    Args:
        date: Processing date (defaults to today)
        region: Dict with lat_min, lat_max, lng_min, lng_max (defaults to Maharashtra EEZ)

    Returns:
        Complete integrated analysis
    """
    processor = IntegratedProcessor(date)

    if region is None:
        region = {
            "lat_min": 14.0,
            "lat_max": 21.0,
            "lng_min": 67.0,
            "lng_max": 74.5,
        }

    return processor.process_complete(
        lat_min=region.get("lat_min", 14.0),
        lat_max=region.get("lat_max", 21.0),
        lng_min=region.get("lng_min", 67.0),
        lng_max=region.get("lng_max", 74.5),
    )


if __name__ == "__main__":
    print("\n[DEPLOY] SAMUDRA AI — Integrated Processor Demo")
    print("Combining PFZ Detection + GHOL Specialist Engine\n")

    # Run integrated analysis
    results = run_integrated_analysis()

    # Display summary
    print("\n[SUMMARY] INTEGRATED ANALYSIS SUMMARY")
    print("=" * 70)
    print(f"\nDate: {results['date']}")
    print(f"Region: {results['region']['lat_min']}-{results['region']['lat_max']}°N, "
          f"{results['region']['lng_min']}-{results['region']['lng_max']}°E")

    print(f"\n[DATA] Zone Detection:")
    print(f"   General PFZ zones: {results['processing_summary']['general_pfz_zones']}")
    print(f"   GHOL-optimized zones: {results['processing_summary']['ghol_optimized_zones']}")
    print(f"   Acoustic hotspots: {results['processing_summary']['acoustic_hotspots']}")

    print(f"\n[FISH] Top GHOL Opportunities:")
    for i, zone in enumerate(results['ghol_zones'][:3], 1):
        print(f"   {i}. Zone {zone['zone_id']}: {zone['center_lat']:.2f}°N, {zone['center_lng']:.2f}°E")
        print(f"      GHOL score: {zone['ghol_targeting_score']:.3f}, "
              f"Spawning: {zone['is_spawning_window']}")

    print(f"\n[INSIGHT] Top Recommendations:")
    for i, rec in enumerate(results['integrated_recommendations'][:3], 1):
        print(f"   {i}. {rec['action']}")

    print("\n" + "=" * 70)
    print("[OK] Integrated analysis complete!")
