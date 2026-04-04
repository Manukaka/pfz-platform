"""
SAMUDRA AI — Economic Intelligence Module
आर्थिक विश्लेषण - मासे पकडून व्यावसायिक लाभ मोजणे

Profit calculator, fuel cost analysis, market price tracking
Trip ROI (Return on Investment) estimation
"""
from typing import Dict, List
from datetime import datetime

class EconomicCalculator:
    """Calculate fishing trip profitability and ROI"""

    # Default cost parameters (Maharashtra fishing context)
    DIESEL_PRICE_PER_LITER = 100.0  # INR
    CREW_COST_PER_DAY = 800.0  # INR per person
    ICE_COST_PER_KG = 10.0  # INR
    FUEL_CONSUMPTION_RATES = {
        "small_boat": 5,      # Liters per hour
        "medium_boat": 15,
        "large_boat": 35,
        "mechanized": 25,
    }

    # Port fees and landing center charges
    PORT_FEES = {
        "Mumbai": 500,
        "Ratnagiri": 300,
        "Sindhudurg": 350,
        "Malvan": 300,
    }

    LANDING_COMMISSION = 0.06  # 6% of catch value

    # Market prices (INR/kg) - Live market data can override these
    MARKET_PRICES = {
        "ghol": 8500,
        "papalet": 600,
        "bangada": 400,
        "mandeli": 250,
        "tuna": 800,
        "surmai": 500,
        "bombil": 150,
        "khamane": 100,
        "awali": 450,
        "waghal": 300,
        "shingala": 200,
        "rawas": 350,
        "karandi": 500,
        "kolimbi": 400,
        "khekda": 250,
        "papada": 280,
        "ghol_sher": 200,
        "shet_bangda": 350,
        "kalava": 600,
        "chirpa": 120,
    }

    # Premium values for special products
    SWIM_BLADDER_PRICES = {
        "ghol": 70000,  # INR/kg - very high value
    }

    @staticmethod
    def calculate_fuel_cost(distance_km: float, boat_type: str = "medium_boat",
                           hours_at_sea: float = None) -> float:
        """
        Calculate fuel cost for a fishing trip

        Args:
            distance_km: Total distance from port to fishing area (round trip)
            boat_type: small_boat, medium_boat, large_boat, mechanized
            hours_at_sea: Optional - if provided, overrides distance-based calculation

        Returns:
            Fuel cost in INR
        """
        consumption_rate = EconomicCalculator.FUEL_CONSUMPTION_RATES.get(boat_type, 15)

        if hours_at_sea:
            fuel_liters = consumption_rate * hours_at_sea
        else:
            # Rough estimate: 1 km ~ 4 minutes at 15 km/hr average speed
            hours_travel = distance_km / 15.0
            fuel_liters = consumption_rate * hours_travel

        fuel_cost = fuel_liters * EconomicCalculator.DIESEL_PRICE_PER_LITER
        return fuel_cost

    @staticmethod
    def calculate_crew_cost(num_crew: int, trip_days: float = 1) -> float:
        """Calculate crew costs"""
        return num_crew * EconomicCalculator.CREW_COST_PER_DAY * trip_days

    @staticmethod
    def calculate_catch_value(catch_composition: Dict[str, float],
                            market_prices: Dict[str, float] = None) -> Dict:
        """
        Calculate total catch value

        Args:
            catch_composition: {"species_key": kg_caught, ...}
            market_prices: Override default prices if provided

        Returns:
            Dict with breakdown and total
        """
        if market_prices is None:
            market_prices = EconomicCalculator.MARKET_PRICES

        breakdown = {}
        total_value = 0.0

        for species, kg_caught in catch_composition.items():
            price = market_prices.get(species, 300)  # Default to 300 if not found
            value = kg_caught * price
            breakdown[species] = {
                "kg": kg_caught,
                "price_per_kg": price,
                "total_value": value,
            }
            total_value += value

        # Add special premiums (e.g., swim bladder from Ghol)
        swim_bladder_bonus = 0.0
        if "ghol" in catch_composition:
            ghol_kg = catch_composition["ghol"]
            # Assume 1% of catch weight is swim bladder (rough estimate)
            bladder_kg = ghol_kg * 0.01
            bladder_value = bladder_kg * EconomicCalculator.SWIM_BLADDER_PRICES.get("ghol", 50000)
            swim_bladder_bonus += bladder_value
            breakdown["ghol_swim_bladder"] = {
                "kg": bladder_kg,
                "price_per_kg": EconomicCalculator.SWIM_BLADDER_PRICES.get("ghol", 50000),
                "total_value": bladder_value,
            }

        total_value += swim_bladder_bonus

        return {
            "breakdown": breakdown,
            "total_catch_value_gross": total_value,
            "total_kg": sum(catch_composition.values()),
        }

    @staticmethod
    def calculate_trip_roi(catch_composition: Dict[str, float],
                          distance_km: float,
                          boat_type: str = "medium_boat",
                          num_crew: int = 4,
                          landing_port: str = "Ratnagiri",
                          trip_days: float = 1,
                          market_prices: Dict[str, float] = None,
                          other_costs: float = 0.0) -> Dict:
        """
        Complete trip profitability analysis

        Returns comprehensive ROI breakdown
        """
        # Calculate revenues
        catch_value = EconomicCalculator.calculate_catch_value(catch_composition, market_prices)
        gross_value = catch_value["total_catch_value_gross"]

        # Calculate costs
        fuel_cost = EconomicCalculator.calculate_fuel_cost(distance_km, boat_type)
        crew_cost = EconomicCalculator.calculate_crew_cost(num_crew, trip_days)
        port_fee = EconomicCalculator.PORT_FEES.get(landing_port, 300)
        landing_commission = gross_value * EconomicCalculator.LANDING_COMMISSION

        total_costs = fuel_cost + crew_cost + port_fee + landing_commission + other_costs

        # Net profit
        net_profit = gross_value - total_costs

        # Calculate ROI
        roi_percentage = (net_profit / total_costs * 100) if total_costs > 0 else 0

        return {
            "catch_details": catch_value,
            "revenue": {
                "gross_catch_value": gross_value,
            },
            "costs": {
                "fuel": round(fuel_cost, 2),
                "crew": round(crew_cost, 2),
                "port_fee": round(port_fee, 2),
                "landing_commission": round(landing_commission, 2),
                "other": round(other_costs, 2),
                "total_costs": round(total_costs, 2),
            },
            "profit": {
                "net_profit": round(net_profit, 2),
                "roi_percentage": round(roi_percentage, 2),
                "profit_per_day": round(net_profit / trip_days, 2),
            },
            "recommendation": EconomicCalculator._get_trip_recommendation(net_profit, total_costs),
        }

    @staticmethod
    def _get_trip_recommendation(net_profit: float, total_costs: float) -> str:
        """Get trip recommendation based on ROI"""
        if net_profit < 0:
            return "[FAIL] NOT RECOMMENDED - Net loss"
        elif net_profit < total_costs * 0.25:
            return "[WARN] RISKY - Low profit margin"
        elif net_profit < total_costs * 0.75:
            return "[OK] ACCEPTABLE - Reasonable profit"
        else:
            return "[TARGET] EXCELLENT - Strong profit potential"

    @staticmethod
    def calculate_breakeven_catch(fuel_cost: float, crew_cost: float,
                                 port_fee: float, avg_price_per_kg: float = 400) -> float:
        """
        Calculate breakeven catch (minimum kg needed to make profit)
        """
        fixed_costs = fuel_cost + crew_cost + port_fee
        # Need to account for 6% landing commission
        effective_price = avg_price_per_kg * 0.94

        if effective_price <= 0:
            return float('inf')

        breakeven_kg = fixed_costs / effective_price
        return breakeven_kg

    @staticmethod
    def get_profitability_by_species(species_key: str, kg_caught: float,
                                    market_price: float = None) -> Dict:
        """Get profitability metrics for a single species"""
        if market_price is None:
            market_price = EconomicCalculator.MARKET_PRICES.get(species_key, 300)

        gross_value = kg_caught * market_price
        commission = gross_value * EconomicCalculator.LANDING_COMMISSION
        net_value = gross_value - commission

        return {
            "species": species_key,
            "kg_caught": kg_caught,
            "market_price_per_kg": market_price,
            "gross_value": round(gross_value, 2),
            "landing_commission_6pct": round(commission, 2),
            "net_value_after_commission": round(net_value, 2),
            "value_per_kg_net": round(net_value / kg_caught, 2) if kg_caught > 0 else 0,
        }


# Sample trip analysis function
def analyze_sample_trip():
    """
    Example: Ratnagiri fisherman's trip
    Distance: 45km offshore
    Catch: Mixed (Bangada, Papalet, Bombil)
    Boat: Medium (mechanized)
    Duration: 18 hours (overnight)
    """
    catch = {
        "bangada": 120,      # 120 kg
        "papalet": 80,       # 80 kg
        "bombil": 200,       # 200 kg (lower value, higher volume)
    }

    roi = EconomicCalculator.calculate_trip_roi(
        catch_composition=catch,
        distance_km=90,      # Round trip
        boat_type="medium_boat",
        num_crew=4,
        landing_port="Ratnagiri",
        trip_days=0.75,      # 18 hours
        other_costs=500,     # Ice, packaging, etc.
    )

    return roi


if __name__ == "__main__":
    result = analyze_sample_trip()
    print("\n[DATA] SAMPLE TRIP ANALYSIS:")
    print(f"Catch: {result['catch_details']['total_kg']} kg")
    print(f"Gross Value: ₹{result['revenue']['gross_catch_value']}")
    print(f"Total Costs: ₹{result['costs']['total_costs']}")
    print(f"Net Profit: ₹{result['profit']['net_profit']}")
    print(f"ROI: {result['profit']['roi_percentage']}%")
    print(f"📌 {result['recommendation']}")
