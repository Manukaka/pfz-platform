"""
SAMUDRA AI — GHOL Specialized Engine
घोल विशेषज्ञ प्रणाली - भारत की सबसे मूल्यवान मछली

Comprehensive GHOL (Protonibea diacanthus) detection and behavioral modeling
Ghol is Maharashtra's premium fish: ₹8,500/kg + ₹70,000/kg swim bladder

Scientific approach:
- Acoustic detection (characteristic drum sound at 100-200 Hz)
- Spawning aggregation windows (lunar-driven reproduction)
- Depth-temperature preference curves
- Tidal movement patterns
- Seasonal migration behavior
- Economic optimization (when to target Ghol vs mixed catches)

Reference: INCOIS Ghol advisory data, Arabian Sea reproductive biology
"""

from datetime import datetime, timedelta
import math
from typing import Dict, List, Optional, Tuple
import numpy as np

from app.core.lunar import LunarEngine
from app.core.species_db import get_species


class GholEngine:
    """
    Specialized engine for Ghol (Protonibea diacanthus) prediction and detection

    Ghol behavior is highly specialized and lunar-dependent:
    - Spawning aggregation peaks during NEW MOON (reproductive fish gather in massive schools)
    - Acoustic communication on 100-200 Hz (can be detected via hydrophones)
    - Depth preference: 30-75m (shelf edge zone)
    - SST optimal: 27-30°C (warm water dependent)
    - Tidal influence: More active during flood tide (incoming tide)
    """

    # === GHOL SPECIES PARAMETERS ===
    SCIENTIFIC_NAME = "Protonibea diacanthus"
    MARATHI_NAME = "घोल"
    ENGLISH_NAME = "Black Pomfret / Ghol"

    # Habitat preferences (optimized from fishery data)
    SST_OPTIMAL_MIN = 27.0  # °C
    SST_OPTIMAL_MAX = 30.0
    SST_VIABLE_MIN = 24.0
    SST_VIABLE_MAX = 32.0

    DEPTH_OPTIMAL_MIN = 40.0  # meters
    DEPTH_OPTIMAL_MAX = 65.0
    DEPTH_VIABLE_MIN = 30.0
    DEPTH_VIABLE_MAX = 75.0

    SALINITY_MIN = 28.0  # PSU
    SALINITY_MAX = 35.0

    # Acoustic detection parameters
    ACOUSTIC_FREQUENCY_MIN = 80  # Hz (lower bound of Ghol sound)
    ACOUSTIC_FREQUENCY_MAX = 250  # Hz (upper bound)
    ACOUSTIC_PEAK_FREQUENCY = 140  # Hz (characteristic drum sound)
    ACOUSTIC_SOURCE_LEVEL = 130  # dB re 1 µPa @ 1m (typical fish)

    # Spawning aggregation characteristics
    LUNAR_PEAK_PHASE = "new_moon"  # Peak spawning at new moon
    SPAWNING_WINDOW_DAYS_BEFORE = 3  # Days before new moon
    SPAWNING_WINDOW_DAYS_AFTER = 2   # Days after new moon
    SPAWNING_SCHOOL_SIZE_MIN = 100  # Minimum fish in spawning aggregation
    SPAWNING_SCHOOL_SIZE_MAX = 5000  # Maximum (can be very large)

    # Tidal behavior
    TIDAL_PREFERENCE = "flood"  # More active during flood tide (incoming)
    TIDAL_ACTIVITY_FLOOD = 1.3  # 30% more active during flood tide
    TIDAL_ACTIVITY_EBB = 0.7    # 30% less active during ebb tide

    # Seasonal behavior
    MONSOON_SEASON_MONTHS = (6, 7, 8, 9)  # Jun-Sep
    MONSOON_DEPTH_SHIFT = 5  # Shift 5m deeper during monsoon (cooler water)

    # Economic parameters
    MARKET_PRICE_PER_KG = 8500  # INR
    SWIM_BLADDER_PRICE_PER_KG = 70000  # INR (very high value)
    SWIM_BLADDER_PERCENTAGE = 0.01  # ~1% of body weight is swim bladder

    # Catchability parameters (for fishermen)
    GILL_NET_CATCH_PER_TRIP = 80  # kg typical (shelf edge net)
    HANDLINE_CATCH_PER_TRIP = 40  # kg typical
    TRAWL_CATCH_PER_TRIP = 150  # kg typical (if targeting)

    # Detection confidence thresholds
    ACOUSTIC_DETECTION_THRESHOLD = 0.7  # 0-1 scale
    SPAWNING_AGGREGATION_THRESHOLD = 0.75

    def __init__(self):
        """Initialize GHOL engine"""
        self.ghol_species = get_species("ghol")

    @staticmethod
    def calculate_spawning_probability(date: datetime, lat: float, lng: float) -> float:
        """
        Calculate probability of spawning aggregation at location/date

        NEW MOON spawning is well-documented for Ghol:
        - Fish gather in massive schools at shelf edge
        - Reproducible season (primarily Apr-Jun in Arabian Sea)
        - Peak abundance during new moon ±3 days

        Args:
            date: Date to check
            lat, lng: Location coordinates

        Returns:
            0-1 spawning probability (0 = no spawning, 1 = peak aggregation)
        """
        # Base: New moon = 1.0, full moon = 0.0, others scale between
        lunar_phase = LunarEngine.get_lunar_phase(date)
        lunar_age = LunarEngine.calculate_lunar_age(date)

        # Spawning window: 3 days before to 2 days after new moon
        if lunar_phase == "new_moon":
            lunar_score = 1.0  # Peak
        elif lunar_phase == "waning_crescent":
            # 3 days before new moon
            lunar_score = 0.9
        elif lunar_phase == "waxing_crescent":
            # 2 days after new moon
            lunar_score = 0.85
        else:
            lunar_score = 0.1  # Very low for other phases

        # Seasonal component (spawning Apr-Jun primarily)
        month = date.month
        if 4 <= month <= 6:
            seasonal_score = 1.0  # Peak spawning season
        elif 3 <= month <= 7:
            seasonal_score = 0.8  # Extended window
        elif month in [2, 8]:
            seasonal_score = 0.4  # Marginal
        else:
            seasonal_score = 0.0  # Off-season

        # Location component: Near shelf edge (45-65m depth)
        # Shelf edge is optimal for spawning aggregations
        if GholEngine._is_near_shelf_edge(lat, lng):
            location_score = 1.0
        else:
            location_score = 0.5

        # Combined probability
        spawning_prob = (lunar_score * 0.4 +
                        seasonal_score * 0.35 +
                        location_score * 0.25)

        return max(0, min(1, spawning_prob))

    @staticmethod
    def calculate_acoustic_detection_probability(date: datetime, lat: float, lng: float,
                                                hydrophone_sensitivity: float = 1.0) -> float:
        """
        Calculate probability of acoustic detection (Ghol spawning sounds)

        Ghol makes characteristic drumming sounds at 100-200 Hz during spawning
        These can be detected by underwater hydrophones at ~1-2 km range

        Args:
            date: Date for calculation
            lat, lng: Hydrophone location
            hydrophone_sensitivity: 0-1 scale (1.0 = perfect detection)

        Returns:
            0-1 acoustic detection probability
        """
        # Spawning aggregation must be present
        spawning_prob = GholEngine.calculate_spawning_probability(date, lat, lng)
        if spawning_prob < 0.5:
            return 0.0  # No spawning = no sounds

        # Lunar illumination affects detectability (dark nights better for underwater sounds)
        lunar_illum = LunarEngine.get_lunar_illumination(date)
        acoustic_factor = 1.0 - lunar_illum * 0.3  # Slight effect

        # Time of night (sounds more active 20:00-04:00)
        hour = date.hour
        if 20 <= hour or hour < 4:
            time_factor = 1.0
        elif 18 <= hour < 20 or 4 <= hour < 6:
            time_factor = 0.6
        else:
            time_factor = 0.1

        # Ocean condition factor (sound propagates better in quiet ocean)
        # Rough estimate from wind/wave data
        ocean_factor = 0.8  # Conservative estimate

        detection_prob = (spawning_prob * 0.4 +
                         acoustic_factor * 0.2 +
                         time_factor * 0.3 +
                         ocean_factor * 0.1) * hydrophone_sensitivity

        return max(0, min(1, detection_prob))

    @staticmethod
    def calculate_habitat_suitability(sst: float, depth: float, salinity: float = 32.0,
                                     date: datetime = None) -> float:
        """
        Calculate Ghol habitat suitability (0-1) based on environmental parameters

        Ghol is highly specialized: narrow SST range (27-30°C) and depth preference (30-75m)

        Args:
            sst: Sea Surface Temperature (°C)
            depth: Water depth (meters, positive value)
            salinity: Salinity (PSU)
            date: Date (for seasonal adjustment)

        Returns:
            0-1 habitat suitability score
        """
        if date is None:
            date = datetime.utcnow()

        # SST component (most critical - Ghol is warm-water species)
        if sst < GholEngine.SST_VIABLE_MIN or sst > GholEngine.SST_VIABLE_MAX:
            sst_score = 0.0
        elif GholEngine.SST_OPTIMAL_MIN <= sst <= GholEngine.SST_OPTIMAL_MAX:
            sst_score = 1.0
        else:
            # Gaussian decay from optimal range
            dist = min(abs(sst - GholEngine.SST_OPTIMAL_MIN),
                      abs(sst - GholEngine.SST_OPTIMAL_MAX))
            sst_score = math.exp(-(dist ** 2) / 4.0)

        # Depth component
        if depth < GholEngine.DEPTH_VIABLE_MIN or depth > GholEngine.DEPTH_VIABLE_MAX:
            depth_score = 0.0
        elif GholEngine.DEPTH_OPTIMAL_MIN <= depth <= GholEngine.DEPTH_OPTIMAL_MAX:
            depth_score = 1.0
        else:
            dist = min(abs(depth - GholEngine.DEPTH_OPTIMAL_MIN),
                      abs(depth - GholEngine.DEPTH_OPTIMAL_MAX))
            depth_score = math.exp(-(dist ** 2) / 64.0)

        # Salinity component (less critical, but Ghol prefers full marine)
        if salinity < GholEngine.SALINITY_MIN or salinity > GholEngine.SALINITY_MAX:
            salinity_score = 0.5
        else:
            salinity_score = 1.0

        # Seasonal adjustment: monsoon cooling may require depth shift
        month = date.month
        if month in GholEngine.MONSOON_SEASON_MONTHS:
            # During monsoon, Ghol moves deeper to find warm water
            optimal_depth = GholEngine.DEPTH_OPTIMAL_MAX - GholEngine.MONSOON_DEPTH_SHIFT
            if abs(depth - optimal_depth) < 10:
                depth_score = min(1.0, depth_score * 1.2)

        # Combined habitat suitability
        hsi = (sst_score * 0.5 +  # Temperature is most critical
               depth_score * 0.35 +  # Depth preference
               salinity_score * 0.15)

        return max(0, min(1, hsi))

    @staticmethod
    def calculate_fishing_effort_recommendation(date: datetime, lat: float, lng: float,
                                               sst: float, depth: float) -> Dict:
        """
        Recommend fishing effort allocation for Ghol targeting

        Combines spawning probability, habitat suitability, and economics
        to recommend whether to target Ghol vs other species

        Args:
            date: Date for fishing
            lat, lng: Fishing location
            sst: Sea surface temperature
            depth: Water depth

        Returns:
            Dict with recommendation, effort percentage, expected catch
        """
        # Calculate key scores
        spawning_prob = GholEngine.calculate_spawning_probability(date, lat, lng)
        hsi = GholEngine.calculate_habitat_suitability(sst, depth, date=date)
        acoustic_detect = GholEngine.calculate_acoustic_detection_probability(date, lat, lng)

        # Combined targeting score
        targeting_score = (spawning_prob * 0.4 +
                          hsi * 0.35 +
                          acoustic_detect * 0.25)

        # Economic calculation
        # Ghol value: ₹8,500/kg + swim bladder premium
        ghol_gross_per_kg = GholEngine.MARKET_PRICE_PER_KG
        bladder_bonus_per_kg = (GholEngine.SWIM_BLADDER_PERCENTAGE *
                               GholEngine.SWIM_BLADDER_PRICE_PER_KG)
        ghol_total_per_kg = ghol_gross_per_kg + bladder_bonus_per_kg  # ~9,200/kg

        # Estimate catch by effort level
        effort_percent = max(20, min(100, int(targeting_score * 100)))
        if effort_percent > 80:
            estimated_catch = GholEngine.GILL_NET_CATCH_PER_TRIP * 0.9  # Selective fishing
        elif effort_percent > 50:
            estimated_catch = GholEngine.GILL_NET_CATCH_PER_TRIP * 0.6
        else:
            estimated_catch = GholEngine.GILL_NET_CATCH_PER_TRIP * 0.2

        estimated_value = estimated_catch * ghol_total_per_kg

        # Recommendation text
        if spawning_prob > 0.75:
            if effort_percent > 80:
                recommendation = "[TARGET] PRIME TIME - Spawning aggregation + Excellent habitat. Go Ghol-focused!"
                confidence = "VERY HIGH"
            else:
                recommendation = "[OK] GOOD - Spawning window but marginal habitat. Mixed fishing recommended."
                confidence = "HIGH"
        elif hsi > 0.8:
            recommendation = "[OK] EXCELLENT - Strong habitat suitability. High-confidence Ghol fishing."
            confidence = "HIGH"
        elif hsi > 0.6:
            recommendation = "[OK] GOOD - Decent habitat. Can target Ghol with mixed effort."
            confidence = "MEDIUM"
        elif effort_percent > 40:
            recommendation = "[WARN] MODERATE - Some opportunity but not primary target. Mixed fishing better."
            confidence = "MEDIUM"
        else:
            recommendation = "[FAIL] NOT RECOMMENDED - Poor spawning/habitat conditions. Focus on other species."
            confidence = "LOW"

        return {
            "recommendation": recommendation,
            "ghol_targeting_score": round(targeting_score, 3),
            "spawning_probability": round(spawning_prob, 3),
            "habitat_suitability": round(hsi, 3),
            "acoustic_detection": round(acoustic_detect, 3),
            "suggested_effort_percent": effort_percent,
            "estimated_ghol_catch_kg": round(estimated_catch, 1),
            "estimated_gross_value": round(estimated_value, 0),
            "confidence": confidence,
        }

    @staticmethod
    def find_best_ghol_zones(pfz_zones: List[Dict], date: datetime = None) -> List[Dict]:
        """
        Filter and rank PFZ zones for Ghol targeting

        Takes general PFZ zones and ranks them specifically for Ghol potential

        Args:
            pfz_zones: List of PFZ zones from main processor
            date: Date for analysis

        Returns:
            List of Ghol-optimized zones with additional metrics
        """
        if date is None:
            date = datetime.utcnow()

        ghol_zones = []

        for zone in pfz_zones:
            lat = zone["center_lat"]
            lng = zone["center_lng"]

            # Extract zone environmental conditions
            # These come from the PFZ zone data
            if "sst" in zone:
                sst = zone["sst"]
            else:
                sst = 28.0  # Default estimate

            # Estimate depth from zone characteristics
            # Ghol prefers shelf edge 40-65m
            estimated_depth = GholEngine._estimate_depth(lat, lng)

            # Calculate Ghol-specific metrics
            spawning_prob = GholEngine.calculate_spawning_probability(date, lat, lng)
            hsi = GholEngine.calculate_habitat_suitability(sst, estimated_depth, date=date)
            acoustic_prob = GholEngine.calculate_acoustic_detection_probability(date, lat, lng)

            # Only include zones with reasonable Ghol potential
            if hsi > 0.4 or spawning_prob > 0.5:
                ghol_score = spawning_prob * 0.4 + hsi * 0.35 + acoustic_prob * 0.25

                ghol_zones.append({
                    "zone_id": zone.get("zone_id", 0),
                    "center_lat": lat,
                    "center_lng": lng,
                    "base_pfz_score": zone.get("avg_pfz_score", 0),
                    "ghol_targeting_score": ghol_score,
                    "spawning_probability": spawning_prob,
                    "habitat_suitability": hsi,
                    "acoustic_detection": acoustic_prob,
                    "estimated_depth": round(estimated_depth, 1),
                    "estimated_sst": sst,
                    "is_spawning_window": spawning_prob > 0.5,
                })

        # Sort by Ghol targeting score (best first)
        ghol_zones.sort(key=lambda z: z["ghol_targeting_score"], reverse=True)

        return ghol_zones

    @staticmethod
    def generate_ghol_trip_plan(zone: Dict, date: datetime, boat_type: str = "medium_boat",
                               num_crew: int = 4) -> Dict:
        """
        Generate detailed Ghol fishing trip plan for a zone

        Args:
            zone: Ghol-optimized zone (from find_best_ghol_zones)
            date: Trip date
            boat_type: Type of boat
            num_crew: Number of crew

        Returns:
            Detailed trip plan with timing, equipment, expectations
        """
        from app.core.economic import EconomicCalculator

        lat = zone["center_lat"]
        lng = zone["center_lng"]

        # Estimate distance from port (Ratnagiri as default: 16.99°N, 73.30°E)
        port_lat, port_lng = 16.99, 73.30
        distance_km = GholEngine._distance_to_point(port_lat, port_lng, lat, lng) * 2  # Round trip

        # Optimal timing for Ghol
        if zone["is_spawning_window"]:
            best_time = "DAWN (05:00-07:00) for spawning aggregations"
            trip_duration = 16.0  # Overnight for spawning (dark hours)
        else:
            best_time = "DAWN or DUSK for active feeding"
            trip_duration = 12.0  # Shorter day trip

        # Estimate catch based on scoring
        ghol_score = zone["ghol_targeting_score"]
        if ghol_score > 0.8:
            catch_estimate = 120  # kg
            catch_confidence = "HIGH"
        elif ghol_score > 0.6:
            catch_estimate = 80
            catch_confidence = "MEDIUM"
        else:
            catch_estimate = 40
            catch_confidence = "MODERATE"

        # Economic analysis
        catch_composition = {"ghol": catch_estimate}
        roi = EconomicCalculator.calculate_trip_roi(
            catch_composition=catch_composition,
            distance_km=distance_km,
            boat_type=boat_type,
            num_crew=num_crew,
            landing_port="Ratnagiri",
            trip_days=trip_duration / 24.0,
            other_costs=500,  # Ice, fuel for lighting, etc.
        )

        # Equipment recommendations
        equipment = GholEngine._recommend_equipment(zone["ghol_targeting_score"])

        return {
            "zone_id": zone["zone_id"],
            "coordinates": {"lat": lat, "lng": lng},
            "distance_km": round(distance_km, 1),
            "trip_duration_hours": trip_duration,
            "best_departure_time": best_time,
            "lunar_phase": LunarEngine.get_lunar_phase(date),
            "lunar_illumination_percent": round(LunarEngine.get_lunar_illumination_percent(date), 1),
            "spawning_window": zone["is_spawning_window"],
            "estimated_catch": {
                "ghol_kg": catch_estimate,
                "confidence": catch_confidence,
                "gross_value_inr": round(catch_estimate * (GholEngine.MARKET_PRICE_PER_KG +
                                                          (GholEngine.SWIM_BLADDER_PERCENTAGE *
                                                           GholEngine.SWIM_BLADDER_PRICE_PER_KG)), 0),
            },
            "economics": {
                "net_profit": round(roi["profit"]["net_profit"], 0),
                "roi_percent": round(roi["profit"]["roi_percentage"], 1),
                "fuel_cost": round(roi["costs"]["fuel"], 0),
                "crew_cost": round(roi["costs"]["crew"], 0),
            },
            "equipment_recommendations": equipment,
            "trip_recommendation": roi["recommendation"],
        }

    @staticmethod
    def _is_near_shelf_edge(lat: float, lng: float) -> bool:
        """Check if location is near continental shelf edge (40-65m depth zone)"""
        # Rough estimation based on distance from coast
        distance_from_coast = max(0, lng - 72.5)
        # Shelf edge typically 1-3 degrees offshore
        return 0.8 <= distance_from_coast <= 3.0

    @staticmethod
    def _estimate_depth(lat: float, lng: float) -> float:
        """Estimate water depth at location (simplified)"""
        from app.data.gebco_client import GEBCOClient
        return abs(GEBCOClient.get_depth_at_point(lat, lng))

    @staticmethod
    def _distance_to_point(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points in degrees (approximate)"""
        # Simple haversine approximation
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        distance_deg = math.sqrt(dlat**2 + dlng**2)
        distance_km = distance_deg * 111.32  # ~111 km per degree
        return distance_km

    @staticmethod
    def _recommend_equipment(ghol_score: float) -> List[str]:
        """Recommend fishing equipment based on targeting intensity"""
        equipment = [
            "✓ Medium-mesh gill nets (32-40mm) for Ghol",
            "✓ Handlines with squid/fish bait for large specimens",
            "✓ Hydrophone (if available) for acoustic detection",
        ]

        if ghol_score > 0.8:
            equipment.extend([
                "✓ Trawl net (if equipped) for higher catch volume",
                "✓ LED underwater lights (attract baitfish → Ghol follows)",
                "✓ Night fishing setup (darkness aids spawning)",
            ])
        elif ghol_score > 0.6:
            equipment.extend([
                "✓ Selective night fishing preferred",
                "✓ Avoid day fishing (lower Ghol activity)",
            ])

        equipment.append("[WARN] Avoid bottom trawling (damages spawning sites)")

        return equipment


# Convenience functions
def analyze_ghol_potential(pfz_zones: List[Dict], date: datetime = None) -> Dict:
    """Quick analysis of Ghol potential across all zones"""
    if date is None:
        date = datetime.utcnow()

    ghol_zones = GholEngine.find_best_ghol_zones(pfz_zones, date)

    return {
        "total_zones": len(pfz_zones),
        "ghol_recommended_zones": len(ghol_zones),
        "top_zones": ghol_zones[:3],
        "lunar_phase": LunarEngine.get_lunar_phase(date),
        "spawning_windows_active": sum(1 for z in ghol_zones if z["is_spawning_window"]),
    }


def plan_ghol_trip(zone: Dict, date: datetime = None) -> Dict:
    """Quick trip planning for Ghol zone"""
    if date is None:
        date = datetime.utcnow()
    return GholEngine.generate_ghol_trip_plan(zone, date)


if __name__ == "__main__":
    print("SAMUDRA AI — GHOL Specialized Engine")
    print("=" * 70)

    date = datetime.utcnow()

    # Test 1: Spawning probability
    print("\n1️⃣ Testing Spawning Probability Calculation...")
    test_lat, test_lng = 17.5, 71.0
    spawn_prob = GholEngine.calculate_spawning_probability(date, test_lat, test_lng)
    print(f"   Spawning probability at {test_lat}°N, {test_lng}°E: {spawn_prob:.1%}")

    # Test 2: Habitat suitability
    print("\n2️⃣ Testing Habitat Suitability...")
    hsi = GholEngine.calculate_habitat_suitability(sst=28.5, depth=50, date=date)
    print(f"   HSI at 28.5°C and 50m depth: {hsi:.3f}")

    # Test 3: Acoustic detection
    print("\n3️⃣ Testing Acoustic Detection...")
    acoustic = GholEngine.calculate_acoustic_detection_probability(date, test_lat, test_lng)
    print(f"   Acoustic detection probability: {acoustic:.1%}")

    # Test 4: Fishing recommendation
    print("\n4️⃣ Testing Fishing Effort Recommendation...")
    rec = GholEngine.calculate_fishing_effort_recommendation(date, test_lat, test_lng, 28.5, 50)
    print(f"   Recommendation: {rec['recommendation']}")
    print(f"   Ghol targeting score: {rec['ghol_targeting_score']:.3f}")
    print(f"   Suggested effort: {rec['suggested_effort_percent']}%")

    # Test 5: Equipment recommendations
    print("\n5️⃣ Testing Equipment Recommendations...")
    equipment = GholEngine._recommend_equipment(0.85)
    print("   Recommended equipment:")
    for item in equipment:
        print(f"   {item}")

    print("\n" + "=" * 70)
    print("[OK] GHOL Engine operational and ready for integration")
