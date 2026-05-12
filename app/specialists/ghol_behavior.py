"""
SAMUDRA AI — GHOL Behavioral Modeling
घोल व्यवहार विज्ञान - जीव पद्धति

Detailed behavioral patterns and ecological interactions for Ghol
Enables prediction of feeding, spawning, and movement behaviors

Behavioral components:
1. Spawning aggregations (lunar-driven mass gatherings)
2. Feeding behavior (diurnal/nocturnal, tidal-influenced)
3. Migration patterns (depth changes with season/monsoon)
4. Social structure (schooling, predator response)
5. Acoustic communication (drumming during reproduction)
6. Predator-prey interactions
"""

from datetime import datetime, timedelta
import math
from typing import Dict, List, Tuple, Optional

from app.core.lunar import LunarEngine
from app.specialists.ghol_engine import GholEngine


class GholBehavior:
    """
    Detailed behavioral modeling for Ghol (Protonibea diacanthus)

    Models feeding, spawning, movement, and social behaviors
    that influence fish distribution and catchability
    """

    # === SPAWNING BEHAVIOR ===
    # Ghol spawning is highly synchronized and lunar-driven

    # Peak spawning: New moon, April-June
    SPAWNING_PEAK_MONTHS = (4, 5, 6)  # April, May, June
    SPAWNING_EXTENDED_MONTHS = (3, 4, 5, 6, 7)  # Extended window

    # Spawning aggregation characteristics
    SPAWNING_SCHOOL_LOCATION = "shelf_edge"  # 40-65m depth zone
    SPAWNING_SCHOOL_DURATION_DAYS = 7  # Lasts ~7 days around new moon
    SPAWNING_INTENSITY_PEAK = "new_moon_peak"  # Peak day of new moon

    # === FEEDING BEHAVIOR ===
    # Ghol feeds primarily at dawn/dusk and night

    FEEDING_HOURS_DAWN = (5, 7)  # 05:00-07:00
    FEEDING_HOURS_DUSK = (17, 19)  # 17:00-19:00
    FEEDING_HOURS_NIGHT = (21, 4)  # 21:00-04:00
    FEEDING_ACTIVITY_LEVEL_NIGHT = 1.5  # 50% more active at night

    # Prey preference
    PREFERRED_PREY = ["small_fish", "squid", "crustaceans"]
    FEEDING_DEPTH = (30, 75)  # m, matches habitat

    # === TIDAL BEHAVIOR ===
    PEAK_ACTIVITY_TIDE = "high_tide"  # More active during high tide
    ACTIVITY_HIGH_TIDE = 1.3  # 30% more active
    ACTIVITY_LOW_TIDE = 0.7  # 30% less active
    SLACK_WATER_EFFECT = 0.85  # Reduced activity at slack water

    # === SEASONAL MIGRATION ===
    # Ghol moves deeper during hot season, shallower during monsoon

    DEPTH_HOT_SEASON = (55, 75)  # May-June (deep to escape heat)
    DEPTH_MONSOON = (40, 55)  # Jun-Sep (upwelling brings cool water)
    DEPTH_POST_MONSOON = (45, 65)  # Oct-Nov (returning to normal)
    DEPTH_WINTER = (40, 60)  # Dec-Mar (moderate)

    # === SCHOOLING BEHAVIOR ===
    SCHOOL_SIZE_RANGE = (50, 5000)  # Fish per school
    SCHOOL_DENSITY_SPAWNING = 1000  # Fish per 1000 m³ during spawning
    SCHOOL_DENSITY_FEEDING = 100  # Fish per 1000 m³ normal

    # === ACOUSTIC BEHAVIOR ===
    # Ghol produces distinctive drumming sounds during spawning
    ACOUSTIC_CALL_FREQUENCY = (100, 200)  # Hz range
    ACOUSTIC_PEAK_FREQUENCY = 140  # Hz
    ACOUSTIC_INTENSITY_SPAWNING = 1.0  # Relative to baseline
    ACOUSTIC_INTENSITY_FEEDING = 0.2  # Mostly silent while feeding
    ACOUSTIC_CALLING_HOURS = (20, 6)  # 20:00-06:00 peak calling

    # === BEHAVIOR STATE MACHINE ===
    BEHAVIOR_STATES = {
        "spawning": {
            "triggers": ["new_moon", "april_to_june", "shelf_edge"],
            "depth": (40, 65),
            "catchability": 0.9,  # Very catchable (dense schools)
            "acoustic_activity": 0.9,  # High acoustic activity
        },
        "pre_spawning_migration": {
            "triggers": ["waning_crescent", "april"],
            "depth": (30, 50),
            "catchability": 0.6,
            "acoustic_activity": 0.5,
        },
        "feeding": {
            "triggers": ["not_spawning", "dawn_dusk_night"],
            "depth": (40, 75),
            "catchability": 0.7,
            "acoustic_activity": 0.2,
        },
        "resting": {
            "triggers": ["day_hours", "slack_tide"],
            "depth": (50, 70),  # Deeper during day
            "catchability": 0.3,
            "acoustic_activity": 0.05,
        },
        "predator_avoidance": {
            "triggers": ["danger_detected"],
            "depth": (45, 80),  # Moves away from surface
            "catchability": 0.1,
            "acoustic_activity": 0.0,
        },
    }

    @staticmethod
    def predict_behavior_state(date: datetime, lat: float, lng: float, sst: float,
                              tidal_phase: str = "flood") -> Dict:
        """
        Predict current behavioral state of Ghol population

        Args:
            date: Current date/time
            lat, lng: Location
            sst: Sea surface temperature
            tidal_phase: "flood", "ebb", or "slack"

        Returns:
            Dict with predicted behavior state and characteristics
        """
        # Evaluate trigger conditions
        lunar_phase = LunarEngine.get_lunar_phase(date)
        lunar_age = LunarEngine.calculate_lunar_age(date)
        month = date.month
        hour = date.hour

        # Scoring for each behavior state
        state_scores = {}

        # === SPAWNING STATE ===
        # Conditions: new moon + april-june + shelf edge
        spawning_score = 0.0
        if lunar_phase == "new_moon":
            spawning_score += 0.4
        elif lunar_phase in ["waning_crescent", "waxing_crescent"]:
            spawning_score += 0.2

        if month in GholBehavior.SPAWNING_PEAK_MONTHS:
            spawning_score += 0.3
        elif month in GholBehavior.SPAWNING_EXTENDED_MONTHS:
            spawning_score += 0.15

        if GholEngine._is_near_shelf_edge(lat, lng):
            spawning_score += 0.3

        state_scores["spawning"] = min(1.0, spawning_score)

        # === PRE-SPAWNING MIGRATION ===
        pre_spawn_score = 0.0
        if lunar_phase == "waning_crescent":
            pre_spawn_score += 0.4
        if month == 4:  # April
            pre_spawn_score += 0.3
        if 30 <= GholEngine._estimate_depth(lat, lng) <= 50:
            pre_spawn_score += 0.3

        state_scores["pre_spawning_migration"] = min(1.0, pre_spawn_score)

        # === FEEDING STATE ===
        feeding_score = 0.0
        if state_scores["spawning"] < 0.6:  # Not in spawning
            feeding_score += 0.4

        # Active during dawn/dusk/night
        if (GholBehavior.FEEDING_HOURS_DAWN[0] <= hour <= GholBehavior.FEEDING_HOURS_DAWN[1] or
            GholBehavior.FEEDING_HOURS_DUSK[0] <= hour <= GholBehavior.FEEDING_HOURS_DUSK[1] or
            hour >= GholBehavior.FEEDING_HOURS_NIGHT[0] or hour <= GholBehavior.FEEDING_HOURS_NIGHT[1]):
            feeding_score += 0.3

        if tidal_phase == "flood":
            feeding_score += 0.2

        state_scores["feeding"] = min(1.0, feeding_score)

        # === RESTING STATE ===
        resting_score = 0.0
        if 9 <= hour <= 16:  # Daytime
            resting_score += 0.3
        if tidal_phase == "slack":
            resting_score += 0.2
        if 50 <= GholEngine._estimate_depth(lat, lng) <= 70:
            resting_score += 0.3

        state_scores["resting"] = min(1.0, resting_score)

        # === PREDATOR AVOIDANCE ===
        # Low probability unless other factors suggest danger
        state_scores["predator_avoidance"] = 0.0

        # Select dominant behavior state
        dominant_state = max(state_scores, key=state_scores.get)
        state_config = GholBehavior.BEHAVIOR_STATES[dominant_state]

        return {
            "primary_state": dominant_state,
            "state_scores": state_scores,
            "catchability": state_config["catchability"],
            "expected_depth_range": state_config["depth"],
            "acoustic_activity": state_config["acoustic_activity"],
            "feeding_active": dominant_state in ["feeding", "pre_spawning_migration"],
        }

    @staticmethod
    def calculate_catchability(date: datetime, lat: float, lng: float,
                              catch_method: str = "gill_net") -> float:
        """
        Calculate relative catchability of Ghol at location/date

        0.0 = very difficult to catch
        1.0 = maximum catchability (spawning aggregation)

        Args:
            date: Date/time
            lat, lng: Location
            catch_method: "gill_net", "handline", "trawl", "dynamite" (last is illegal)

        Returns:
            0-1 catchability score
        """
        # Get behavior state
        behavior = GholBehavior.predict_behavior_state(date, lat, lng, sst=28.0)
        base_catchability = behavior["catchability"]

        # Adjust for catch method
        if catch_method == "gill_net":
            method_factor = 1.0  # Standard
        elif catch_method == "handline":
            method_factor = 0.8  # Less efficient, but more selective
        elif catch_method == "trawl":
            method_factor = 1.3  # Higher volume capture
        else:
            method_factor = 0.5

        # Environmental factors
        lunar_illum = LunarEngine.get_lunar_illumination(date)
        darkness_factor = 1.0 - lunar_illum * 0.2  # Slightly higher at night

        tidal_coef = LunarEngine.get_tidal_coefficient(date)
        tidal_factor = 0.8 + tidal_coef * 0.4  # Spring tides better

        final_catchability = base_catchability * method_factor * darkness_factor * tidal_factor

        return max(0, min(1.0, final_catchability))

    @staticmethod
    def estimate_school_size(date: datetime, lat: float, lng: float,
                            sst: float, depth: float) -> Dict:
        """
        Estimate size of Ghol schools at location

        Args:
            date: Date/time
            lat, lng: Location
            sst: Sea surface temperature
            depth: Water depth

        Returns:
            Dict with school size estimates
        """
        behavior = GholBehavior.predict_behavior_state(date, lat, lng, sst)

        if behavior["primary_state"] == "spawning":
            # Massive spawning aggregations
            school_size = 2000 + int(3000 * GholEngine.calculate_spawning_probability(date, lat, lng))
            school_density = GholBehavior.SCHOOL_DENSITY_SPAWNING
            confidence = "Very High"
        elif behavior["primary_state"] == "pre_spawning_migration":
            # Large pre-spawning schools
            school_size = 400 + int(600 * GholEngine.calculate_spawning_probability(date, lat, lng))
            school_density = 500
            confidence = "High"
        elif behavior["primary_state"] == "feeding":
            # Moderate feeding schools
            school_size = 150 + int(250 * (0.5 if 5 <= date.hour <= 7 else 1.0))
            school_density = GholBehavior.SCHOOL_DENSITY_FEEDING
            confidence = "Medium"
        else:
            # Scattered during resting
            school_size = 30 + int(50 * depth / 100)  # Deeper = slightly larger
            school_density = 30
            confidence = "Low"

        return {
            "estimated_school_size": school_size,
            "school_density_fish_per_1000m3": school_density,
            "confidence": confidence,
            "behavior_state": behavior["primary_state"],
            "catching_opportunity": "Excellent" if school_size > 1000 else
                                   "Good" if school_size > 300 else
                                   "Fair" if school_size > 100 else "Poor",
        }

    @staticmethod
    def generate_behavior_forecast(date: datetime, lat: float, lng: float,
                                  days_ahead: int = 7) -> List[Dict]:
        """
        Generate 7-day behavioral forecast for location

        Useful for trip planning: predict when Ghol will be most catchable

        Args:
            date: Starting date
            lat, lng: Location
            days_ahead: Number of days to forecast

        Returns:
            List of daily forecasts
        """
        forecasts = []

        for i in range(days_ahead):
            forecast_date = date + timedelta(days=i)

            behavior = GholBehavior.predict_behavior_state(forecast_date, lat, lng, sst=28.0)
            school = GholBehavior.estimate_school_size(forecast_date, lat, lng, sst=28.0, depth=50)
            catchability = GholBehavior.calculate_catchability(forecast_date, lat, lng)

            spawning_prob = GholEngine.calculate_spawning_probability(forecast_date, lat, lng)
            lunar_phase = LunarEngine.get_lunar_phase(forecast_date)

            forecasts.append({
                "date": forecast_date.strftime("%Y-%m-%d"),
                "day_of_week": forecast_date.strftime("%A"),
                "lunar_phase": lunar_phase,
                "primary_behavior": behavior["primary_state"],
                "spawning_probability": round(spawning_prob, 2),
                "estimated_school_size": school["estimated_school_size"],
                "catchability": round(catchability, 2),
                "fishing_quality": "Excellent" if catchability > 0.8 else
                                 "Good" if catchability > 0.6 else
                                 "Fair" if catchability > 0.4 else "Poor",
                "recommendation": GholBehavior._forecast_recommendation(
                    behavior["primary_state"], spawning_prob, catchability
                ),
            })

        return forecasts

    @staticmethod
    def _forecast_recommendation(behavior_state: str, spawning_prob: float,
                                catchability: float) -> str:
        """Generate recommendation text for forecast day"""
        if spawning_prob > 0.7 and catchability > 0.8:
            return "[TARGET] PRIME - Go Ghol fishing!"
        elif behavior_state == "spawning" or catchability > 0.75:
            return "[OK] EXCELLENT - High probability success"
        elif catchability > 0.6:
            return "[OK] GOOD - Worth fishing"
        elif catchability > 0.4:
            return "[WARN] FAIR - Mixed conditions"
        else:
            return "[FAIL] POOR - Consider different location"

    @staticmethod
    def identify_acoustic_hotspots(date: datetime, region_lats: Tuple[float, float],
                                  region_lngs: Tuple[float, float]) -> List[Dict]:
        """
        Identify potential acoustic detection hotspots in region

        Places where Ghol acoustic signals are most likely

        Args:
            date: Date for analysis
            region_lats: (lat_min, lat_max)
            region_lngs: (lng_min, lng_max)

        Returns:
            List of acoustic hotspot locations
        """
        hotspots = []

        # Grid search for likely spawning/acoustic locations
        step = 0.5  # 0.5 degree grid (~55 km)
        lat = region_lats[0]

        while lat <= region_lats[1]:
            lng = region_lngs[0]
            while lng <= region_lngs[1]:
                acoustic_prob = GholEngine.calculate_acoustic_detection_probability(date, lat, lng)

                if acoustic_prob > 0.5:  # Only report significant acoustic probability
                    hotspots.append({
                        "lat": lat,
                        "lng": lng,
                        "acoustic_probability": round(acoustic_prob, 2),
                        "spawning_probability": round(
                            GholEngine.calculate_spawning_probability(date, lat, lng), 2
                        ),
                        "recommended_listening_hours": "20:00-06:00 (peak calling hours)",
                        "hydrophone_range_km": 2,
                    })

                lng += step
            lat += step

        # Sort by acoustic probability
        hotspots.sort(key=lambda x: x["acoustic_probability"], reverse=True)

        return hotspots[:10]  # Return top 10


if __name__ == "__main__":
    print("SAMUDRA AI — GHOL Behavioral Modeling")
    print("=" * 70)

    date = datetime.utcnow()
    test_lat, test_lng = 17.5, 71.0

    # Test 1: Behavior prediction
    print("\n1️⃣ Predicting Ghol Behavior State...")
    behavior = GholBehavior.predict_behavior_state(date, test_lat, test_lng, sst=28.5)
    print(f"   Primary state: {behavior['primary_state']}")
    print(f"   Catchability: {behavior['catchability']:.1%}")

    # Test 2: Catchability
    print("\n2️⃣ Calculating Catchability...")
    catchability = GholBehavior.calculate_catchability(date, test_lat, test_lng, catch_method="gill_net")
    print(f"   Gill net catchability: {catchability:.1%}")

    # Test 3: School size estimation
    print("\n3️⃣ Estimating School Size...")
    school = GholBehavior.estimate_school_size(date, test_lat, test_lng, sst=28.5, depth=50)
    print(f"   Estimated school size: {school['estimated_school_size']} fish")
    print(f"   Catching opportunity: {school['catching_opportunity']}")

    # Test 4: 7-day forecast
    print("\n4️⃣ Generating 7-Day Forecast...")
    forecast = GholBehavior.generate_behavior_forecast(date, test_lat, test_lng, days_ahead=3)
    for day in forecast:
        print(f"   {day['date']}: {day['fishing_quality']} - {day['recommendation']}")

    # Test 5: Acoustic hotspots
    print("\n5️⃣ Finding Acoustic Hotspots...")
    hotspots = GholBehavior.identify_acoustic_hotspots(date, (16, 19), (70, 72))
    if hotspots:
        print(f"   Found {len(hotspots)} acoustic hotspots")
        print(f"   Best: {hotspots[0]['lat']}°N, {hotspots[0]['lng']}°E")
        print(f"   Acoustic probability: {hotspots[0]['acoustic_probability']:.1%}")

    print("\n" + "=" * 70)
    print("[OK] GHOL Behavioral modeling operational")
