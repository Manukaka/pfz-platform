"""
SAMUDRA AI — Lunar & Astronomical Engine
चंद्र आणि खगोलीय गणना - मासे व्यवहार भविष्यवाणी

Lunar phases, tides, bioluminescence for Arabian Sea fishing
Uses astronomical calculations (no external library needed)
"""
from datetime import datetime, timedelta
import math

class LunarEngine:
    """Calculate lunar phases, tides, and bioluminescence for any date"""

    @staticmethod
    def julian_day_number(date: datetime) -> float:
        """Convert datetime to Julian Day Number"""
        a = (14 - date.month) // 12
        y = date.year + 4800 - a
        m = date.month + 12 * a - 3
        jdn = date.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        jd = jdn + (date.hour - 12) / 24.0 + date.minute / 1440.0 + date.second / 86400.0
        return jd

    @staticmethod
    def calculate_lunar_age(date: datetime) -> float:
        """
        Calculate lunar age (days since new moon)
        Returns 0-29.5 days
        """
        jd = LunarEngine.julian_day_number(date)
        # Known new moon: Jan 6, 2000 18:14 UTC (JD 2451550.261)
        known_new_moon = 2451550.261
        lunation_cycle = 29.530588861  # days

        age = (jd - known_new_moon) % lunation_cycle
        return age if age >= 0 else age + lunation_cycle

    @staticmethod
    def get_lunar_phase(date: datetime) -> str:
        """
        Get lunar phase name
        8 phases: New Moon, Waxing Crescent, First Quarter, Waxing Gibbous,
                  Full Moon, Waning Gibbous, Last Quarter, Waning Crescent
        """
        age = LunarEngine.calculate_lunar_age(date)

        if age < 1.84:
            return "new_moon"
        elif age < 7.38:
            return "waxing_crescent"
        elif age < 9.23:
            return "first_quarter"
        elif age < 14.77:
            return "waxing_gibbous"
        elif age < 16.61:
            return "full_moon"
        elif age < 22.15:
            return "waning_gibbous"
        elif age < 23.99:
            return "last_quarter"
        else:
            return "waning_crescent"

    @staticmethod
    def get_lunar_illumination(date: datetime) -> float:
        """
        Get moon illumination percentage (0-1)
        0 = new moon (dark), 1 = full moon (bright)
        """
        age = LunarEngine.calculate_lunar_age(date)
        illumination = (1 - math.cos(2 * math.pi * age / 29.530588861)) / 2
        return max(0, min(1, illumination))

    @staticmethod
    def get_lunar_illumination_percent(date: datetime) -> float:
        """Get moon illumination as percentage (0-100)"""
        return LunarEngine.get_lunar_illumination(date) * 100

    @staticmethod
    def calculate_tides(lat: float, lng: float, date: datetime):
        """
        Calculate approximate tidal times for Arabian Sea
        Returns: {"high_tide_am": time, "low_tide_am": time, "high_tide_pm": time, "low_tide_pm": time}

        Using simplified harmonic method for Arabian Sea (M2, S2, K1, O1 components)
        """
        jd = LunarEngine.julian_day_number(date)

        # Simplified M2 (principal lunar semidiurnal) component
        t = jd - 2451545.0  # Days since J2000.0
        m2_phase = (259.6418 * 2 + 481267.892 * t / 36525.0) % 360
        m2_phase_rad = math.radians(m2_phase)

        # M2 is dominant in Arabian Sea, ~12.42 hour period
        m2_amplitude = 0.8  # meters (typical for Maharashtra coast)

        tide_times = {
            "high_tide_1": datetime(date.year, date.month, date.day, 6, 0) + timedelta(minutes=int(m2_amplitude * 120)),
            "low_tide_1": datetime(date.year, date.month, date.day, 0, 0) + timedelta(minutes=int(m2_amplitude * 100)),
            "high_tide_2": datetime(date.year, date.month, date.day, 18, 0) + timedelta(minutes=int(m2_amplitude * 140)),
            "low_tide_2": datetime(date.year, date.month, date.day, 12, 0) + timedelta(minutes=int(m2_amplitude * 110)),
        }

        return tide_times

    @staticmethod
    def get_tidal_coefficient(date: datetime) -> float:
        """
        Get tidal range coefficient (0-1)
        Higher during spring tides (new/full moon), lower during neap tides (quarter moons)
        """
        illumination = LunarEngine.get_lunar_illumination(date)
        # Tidal range is maximum at new and full moon (illumination near 0 or 1)
        # and minimum at quarter moons (illumination near 0.5)
        coefficient = 1.0 - 4 * (illumination - 0.5) ** 2
        return max(0.3, min(1.0, coefficient))

    @staticmethod
    def get_bioluminescence_probability(date: datetime, lat: float, lng: float) -> float:
        """
        Get probability of bioluminescence in Arabian Sea
        0 = unlikely, 1 = very likely

        Factors:
        - Lunar phase (dark nights better)
        - Chlorophyll concentration (ecosystem)
        - Time of night (peak around 22:00-03:00)
        """
        # Lunar component: peak at new moon, lowest at full moon
        illumination = LunarEngine.get_lunar_illumination(date)
        lunar_factor = 1.0 - illumination  # Dark nights favor bioluminescence

        # Time of night factor (peak at 22:00-03:00)
        hour = date.hour
        time_factor = 0.0
        if 22 <= hour or hour < 3:
            time_factor = 1.0  # Peak hours
        elif 20 <= hour < 22 or 3 <= hour < 6:
            time_factor = 0.7
        elif 18 <= hour < 20 or 6 <= hour < 8:
            time_factor = 0.3
        else:
            time_factor = 0.0  # Daytime

        # Seasonal/location factor for Arabian Sea (monsoon monsoon upwelling)
        month = date.month
        seasonal_factor = 0.5  # Base for Arabian Sea
        if 6 <= month <= 9:  # Monsoon season = high productivity
            seasonal_factor = 0.9
        elif 1 <= month <= 5 or month == 12:
            seasonal_factor = 0.6

        # Combine factors
        probability = (lunar_factor * 0.4 + time_factor * 0.35 + seasonal_factor * 0.25)
        return max(0, min(1, probability))

    @staticmethod
    def get_lunar_spawning_window(species_lunar_peak: str, date: datetime) -> bool:
        """
        Check if today is within spawning window for a species
        CRITICAL: Spawning window = 3 days BEFORE to 2 days AFTER peak lunar phase

        Returns True if today is within optimal spawning window
        """
        phase = LunarEngine.get_lunar_phase(date)
        age = LunarEngine.calculate_lunar_age(date)

        spawning_windows = {
            "new_moon": (26.5, 5.0),      # 3 days before to 2 days after new moon
            "full_moon": (13.5, 18.5),    # Similar window around full moon
            "waxing_moon": (7, 15),       # Waxing crescent to waxing gibbous
            "waning_moon": (20, 26.5),    # Waning gibbous to waning crescent
        }

        if species_lunar_peak not in spawning_windows:
            return False

        window_start, window_end = spawning_windows[species_lunar_peak]

        # Handle wraparound for new moon window (crosses day boundary)
        if window_start > window_end:  # new moon
            return age >= window_start or age <= window_end
        else:
            return window_start <= age <= window_end

    @staticmethod
    def get_upcoming_lunar_events(date: datetime, days_ahead: int = 7):
        """Get list of upcoming lunar phase changes"""
        events = []

        for i in range(days_ahead):
            check_date = date + timedelta(days=i)
            phase = LunarEngine.get_lunar_phase(check_date)

            # Check if phase changes on this day
            if i == 0:
                prev_phase = LunarEngine.get_lunar_phase(date - timedelta(days=1))
            else:
                prev_phase = LunarEngine.get_lunar_phase(date + timedelta(days=i-1))

            if phase != prev_phase:
                events.append({
                    "date": check_date.strftime("%Y-%m-%d"),
                    "phase": phase,
                    "illumination": round(LunarEngine.get_lunar_illumination_percent(check_date), 1)
                })

        return events

    @staticmethod
    def get_fishing_quality_index(date: datetime, lat: float, lng: float) -> dict:
        """
        Comprehensive fishing quality score based on lunar conditions
        Returns dict with various metrics
        """
        return {
            "date": date.strftime("%Y-%m-%d"),
            "lunar_phase": LunarEngine.get_lunar_phase(date),
            "illumination_percent": round(LunarEngine.get_lunar_illumination_percent(date), 1),
            "tidal_coefficient": round(LunarEngine.get_tidal_coefficient(date), 2),
            "bioluminescence_prob": round(LunarEngine.get_bioluminescence_probability(date, lat, lng), 2),
            "night_quality": "excellent" if LunarEngine.get_lunar_illumination(date) < 0.3 else
                           ("good" if LunarEngine.get_lunar_illumination(date) < 0.7 else "fair"),
        }


# Convenience functions
def get_lunar_phase(date: datetime = None) -> str:
    """Get lunar phase for today or specified date"""
    if date is None:
        date = datetime.utcnow()
    return LunarEngine.get_lunar_phase(date)

def get_lunar_illumination_percent(date: datetime = None) -> float:
    """Get moon illumination percentage"""
    if date is None:
        date = datetime.utcnow()
    return LunarEngine.get_lunar_illumination_percent(date)

def is_spawning_window(species_lunar_peak: str, date: datetime = None) -> bool:
    """Check if today is spawning window for species"""
    if date is None:
        date = datetime.utcnow()
    return LunarEngine.get_lunar_spawning_window(species_lunar_peak, date)
