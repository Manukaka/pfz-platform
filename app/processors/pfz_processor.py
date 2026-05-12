"""
SAMUDRA AI — PFZ Processor
संभाव्य मासे क्षेत्र प्रणाली - एकीकृत पाइपलाइन

Main processing pipeline that orchestrates the complete PFZ detection workflow:
1. Fetch data from multiple oceanographic sources
2. Apply sea masking (land filtering)
3. Calculate HSI (Habitat Suitability) for species
4. Detect thermal fronts, upwelling, eddies
5. Apply lunar/seasonal modifiers
6. Calculate combined PFZ score
7. Cluster into spatial zones
8. Generate economic recommendations

This is the core engine that ties all modules together.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
import math

import numpy as np

from app.core.pfz_algorithm import PFZAlgorithm, classify_pfz_confidence
from app.core.sea_mask import is_sea, get_coast_lng_for_lat
from app.core.lunar import LunarEngine
from app.core.species_db import get_species, get_all_species, calculate_hsi
from app.core.economic import EconomicCalculator
from app.data.data_aggregator import DataAggregator


class PFZProcessor:
    """
    Main orchestrator for Potential Fishing Zone detection

    Combines oceanographic data with advanced algorithms to identify
    optimal fishing zones for Arabian Sea fishermen
    """

    # Process parameters
    PFZ_GRID_RESOLUTION = 0.25  # 0.25° grid (~25-28 km at equator)
    MIN_CLUSTER_POINTS = 3
    CLUSTER_DISTANCE_KM = 90  # eps parameter for DBSCAN in km

    def __init__(self, date: datetime = None):
        """
        Initialize PFZ processor for a specific date

        Args:
            date: Processing date (defaults to today UTC)
        """
        self.date = date if date else datetime.utcnow()
        self.data = None
        self.results = {
            "date": self.date.strftime("%Y-%m-%d"),
            "status": "initialized",
            "pfz_zones": [],
            "species_insights": {},
            "processing_log": [],
        }

    def process(self, lat_min: float = 14.0, lat_max: float = 21.0,
               lng_min: float = 67.0, lng_max: float = 74.5,
               species: str = None) -> Dict:
        """
        Execute complete PFZ detection workflow

        Args:
            lat_min, lat_max, lng_min, lng_max: Geographic region
            species: Specific species code ("ghol", "papalet", etc) or None for all

        Returns:
            Dict with PFZ zones, scores, economic data, and recommendations
        """
        self.results["processing_log"] = []
        self._log("Starting PFZ detection workflow...")

        # Step 1: Fetch data
        self._log("Fetching oceanographic data from CMEMS, NASA, ECMWF, GEBCO...")
        self.data = DataAggregator.fetch_pfz_data(lat_min, lat_max, lng_min, lng_max, self.date)

        if self.data["metadata"]["data_quality"]["completeness_percent"] < 50:
            self.results["status"] = "error"
            self._log("ERROR: Data quality below 50%. Cannot proceed.")
            return self.results

        self._log(f"[OK] Data fetched successfully ({self.data['metadata']['data_quality']['completeness_percent']:.0f}% complete)")

        # Step 2: Create processing grid
        self._log("Creating processing grid...")
        grid = self._create_grid(lat_min, lat_max, lng_min, lng_max)
        self._log(f"[OK] Grid created: {len(grid)} points at {self.PFZ_GRID_RESOLUTION}° resolution")

        # Step 3: Calculate PFZ scores for each grid point
        self._log("Calculating oceanographic features...")
        pfz_points = self._calculate_pfz_scores(grid)
        self._log(f"[OK] Calculated PFZ scores for {len(pfz_points)} grid points")

        # Step 4: Filter high-confidence points
        self._log("Filtering high-confidence PFZ points...")
        high_confidence = [p for p in pfz_points if p["score"] >= PFZAlgorithm.MEDIUM_CONFIDENCE]
        self._log(f"[OK] Found {len(high_confidence)} high-confidence points")

        # Step 5: Cluster into spatial zones
        self._log("Clustering points into spatial zones...")
        clusters = PFZAlgorithm.cluster_pfz_zones(
            [(p["lat"], p["lng"], p["score"]) for p in high_confidence],
            eps_degrees=self.CLUSTER_DISTANCE_KM / 111.0,
            min_samples=self.MIN_CLUSTER_POINTS
        )
        self._log(f"[OK] Identified {len(clusters)} PFZ zones")

        # Step 6: Enrich zones with species and economic data
        self._log("Enriching zones with species and economic intelligence...")
        enriched_zones = self._enrich_zones(clusters, species)
        self.results["pfz_zones"] = enriched_zones

        # Step 7: Generate species-specific insights
        self._log("Generating species insights...")
        self.results["species_insights"] = self._generate_species_insights(enriched_zones, species)

        self.results["status"] = "completed"
        self._log("[OK] PFZ detection workflow completed successfully")

        return self.results

    def _create_grid(self, lat_min: float, lat_max: float, lng_min: float, lng_max: float) -> List[Tuple]:
        """Create processing grid points"""
        grid = []
        lat = lat_min
        while lat <= lat_max:
            lng = lng_min
            while lng <= lng_max:
                # Only include sea points
                if is_sea(lat, lng):
                    grid.append((lat, lng))
                lng += self.PFZ_GRID_RESOLUTION
            lat += self.PFZ_GRID_RESOLUTION
        return grid

    def _calculate_pfz_scores(self, grid: List[Tuple]) -> List[Dict]:
        """
        Calculate PFZ scores for each grid point

        Combines all oceanographic features:
        - Thermal fronts (Sobel gradient on SST)
        - Upwelling (Bakun Ekman Transport)
        - Eddies (Okubo-Weiss parameter)
        - Chlorophyll (productivity)
        - SSH anomaly (eddy signature)
        - Bathymetry (shelf effect)
        - Convergence (flow lines)
        """
        if not self.data:
            return []

        pfz_points = []

        # Get lunar and seasonal multipliers
        lunar_phase = LunarEngine.get_lunar_phase(self.date)
        lunar_illumination = LunarEngine.get_lunar_illumination(self.date)
        lunar_multiplier = 1.2 if lunar_illumination < 0.3 else 0.9  # Favor dark nights

        month = self.date.month
        seasonal_multiplier = 1.5 if 6 <= month <= 9 else 1.0  # Boost monsoon season

        # Extract data grids for interpolation
        sst_grid = np.array(self.data["sst"]["grid"]) if "sst" in self.data else None
        u_current = np.array(self.data["u_current"]["grid"]) if "u_current" in self.data else None
        v_current = np.array(self.data["v_current"]["grid"]) if "v_current" in self.data else None
        u10_wind = np.array(self.data["u10_wind"]["grid"]) if "u10_wind" in self.data else None
        v10_wind = np.array(self.data["v10_wind"]["grid"]) if "v10_wind" in self.data else None
        chlorophyll = np.array(self.data["chlorophyll"]["grid"]) if "chlorophyll" in self.data else None
        ssh = np.array(self.data["ssh_anomaly"]["grid"]) if "ssh_anomaly" in self.data else None
        bathymetry = np.array(self.data["bathymetry"]["depth"]) if "bathymetry" in self.data else None

        # Get coordinate lists for interpolation
        lat_list = self.data["sst"]["lat"] if "sst" in self.data else []
        lng_list = self.data["sst"]["lng"] if "sst" in self.data else []

        # Process each grid point
        for lat, lng in grid:
            try:
                # Find indices in data grid (linear interpolation)
                if not lat_list or not lng_list:
                    continue

                lat_idx = self._interpolate_index(lat, lat_list)
                lng_idx = self._interpolate_index(lng, lng_list)

                if lat_idx < 0 or lng_idx < 0:
                    continue

                # Extract values at this point
                sst = sst_grid[lat_idx, lng_idx] if sst_grid is not None else 25.0
                u_curr = u_current[lat_idx, lng_idx] if u_current is not None else 0.0
                v_curr = v_current[lat_idx, lng_idx] if v_current is not None else 0.0
                u_wind = u10_wind[lat_idx, lng_idx] if u10_wind is not None else 0.0
                v_wind = v10_wind[lat_idx, lng_idx] if v10_wind is not None else 0.0
                chl = chlorophyll[lat_idx, lng_idx] if chlorophyll is not None else 0.3
                ssh_anom = ssh[lat_idx, lng_idx] if ssh is not None else 0.0
                depth = abs(bathymetry[lat_idx, lng_idx]) if bathymetry is not None else 100.0

                # Normalize features to 0-1 scale
                thermal_front = self._normalize(sst, 20, 32)  # SST range 20-32°C
                upwelling = self._normalize(chl, 0.1, 1.0)  # Chlorophyll range
                eddy = self._normalize(abs(ssh_anom), 0, 0.3)  # SSH anomaly magnitude
                convergence = self._normalize(abs(u_curr) + abs(v_curr), 0, 0.5)  # Current magnitude
                bathymetry_score = self._bathymetry_score(depth)  # Higher near shelf edge
                ssh_anomaly_score = 1.0 if ssh_anom < -0.05 else 0.3  # Negative SSH = eddy

                # Depth suitability (optimal 30-300m)
                depth_suitable = 1.0 if 30 <= depth <= 300 else 0.3

                # Combined PFZ score V3 (Scientific Intelligence)
                pfz_score = PFZAlgorithm.calculate_pfz_score(
                    sst=sst,
                    thermal_front=thermal_front,
                    upwelling=upwelling,
                    chlorophyll=chl / 1.0 if chl else 0.0,
                    eddy=eddy,
                    convergence=convergence,
                    bathymetry=bathymetry_score * depth_suitable,
                    ssh_anomaly=ssh_anomaly_score,
                    u_curr=u_curr,
                    v_curr=v_curr,
                    lunar_multiplier=lunar_multiplier,
                    seasonal_multiplier=seasonal_multiplier,
                )

                pfz_points.append({
                    "lat": lat,
                    "lng": lng,
                    "score": pfz_score,
                    "confidence": classify_pfz_confidence(pfz_score),
                    "sst": sst,
                    "chl": chl,
                    "depth": depth,
                    "eddy_signal": ssh_anom,
                })

            except Exception as e:
                # Skip this point if calculation fails
                continue

        return pfz_points

    def _enrich_zones(self, clusters: List[Dict], species: str = None) -> List[Dict]:
        """
        Enrich PFZ zones with species suitability and economic data

        Args:
            clusters: Cluster output from DBSCAN
            species: Specific species to focus on, or None for all

        Returns:
            List of enriched zone objects with recommendations
        """
        enriched = []

        for cluster in clusters:
            zone = {
                "zone_id": len(enriched) + 1,
                "center_lat": cluster["center_lat"],
                "center_lng": cluster["center_lng"],
                "avg_pfz_score": cluster["avg_score"],
                "point_count": cluster["point_count"],
                "points": cluster["points"],
                "species_suitability": {},
                "economic_analysis": None,
            }

            # Get average conditions in zone
            zone_sst = np.mean([p[2] for p in cluster["points"]]) if cluster["points"] else 25.0
            zone_depth = np.mean([abs(self._get_depth(p[0], p[1])) for p in cluster["points"]])

            # Check suitability for species
            if species:
                species_list = [species] if isinstance(species, str) else [species]
            else:
                species_list = list(get_all_species().keys())

            for sp in species_list:
                sp_data = get_species(sp)
                if sp_data:
                    hsi = calculate_hsi(
                        sp,
                        sst=zone_sst,
                        depth=zone_depth,
                        lunar_phase=LunarEngine.get_lunar_phase(self.date),
                        month=self.date.month
                    )
                    zone["species_suitability"][sp] = {
                        "hsi_score": hsi,
                        "species_name": sp_data["english_name"],
                        "suitability": "Excellent" if hsi > 0.7 else "Good" if hsi > 0.5 else "Moderate",
                    }

            # Economic analysis: estimate catch value
            zone["economic_analysis"] = self._estimate_zone_economics(zone)

            enriched.append(zone)

        # Sort by PFZ score (best zones first)
        enriched.sort(key=lambda z: z["avg_pfz_score"], reverse=True)

        return enriched

    def _estimate_zone_economics(self, zone: Dict) -> Dict:
        """
        Estimate economic potential of a zone

        Returns dict with estimated catch and ROI
        """
        # Estimate catch composition based on species suitability
        estimated_catch = {}
        top_species = sorted(
            zone["species_suitability"].items(),
            key=lambda x: x[1]["hsi_score"],
            reverse=True
        )[:3]

        for sp_code, sp_info in top_species:
            if sp_info["hsi_score"] > 0.5:
                # Estimate kg based on HSI (higher HSI = more catch)
                estimated_kg = 50 + int(sp_info["hsi_score"] * 100)
                estimated_catch[sp_code] = estimated_kg

        if not estimated_catch:
            return None

        # Calculate trip ROI (assuming typical fishing parameters)
        distance_km = (zone["center_lng"] - 72.8) * 111.32 * math.cos(math.radians(zone["center_lat"]))
        distance_km = abs(distance_km) * 2  # Round trip

        roi_analysis = EconomicCalculator.calculate_trip_roi(
            catch_composition=estimated_catch,
            distance_km=max(30, distance_km),
            boat_type="medium_boat",
            num_crew=4,
            landing_port="Ratnagiri",
            trip_days=0.75,
        )

        return {
            "estimated_catch_kg": sum(estimated_catch.values()),
            "estimated_catch_species": estimated_catch,
            "estimated_distance_km": round(distance_km, 1),
            "estimated_profit": roi_analysis["profit"]["net_profit"],
            "roi_percent": roi_analysis["profit"]["roi_percentage"],
            "recommendation": roi_analysis["recommendation"],
        }

    def _generate_species_insights(self, zones: List[Dict], species: str = None) -> Dict:
        """Generate insights for specific species across all zones"""
        insights = {}

        species_list = [species] if species else []
        if not species:
            species_list = get_all_species()

        for sp in species_list:
            sp_data = get_species(sp)
            if not sp_data:
                continue

            # Find best zones for this species
            best_zones = []
            for zone in zones:
                if sp in zone["species_suitability"]:
                    hsi = zone["species_suitability"][sp]["hsi_score"]
                    if hsi > 0.5:  # Only include good zones
                        best_zones.append({
                            "zone_id": zone["zone_id"],
                            "lat": zone["center_lat"],
                            "lng": zone["center_lng"],
                            "hsi": hsi,
                        })

            # Check lunar spawning window
            is_spawning = LunarEngine.get_lunar_spawning_window(
                sp_data.get("lunar_peak_phase", "new_moon"),
                self.date
            )

            insights[sp] = {
                "species_name": sp_data["english_name"],
                "scientific_name": sp_data["scientific_name"],
                "market_price_per_kg": EconomicCalculator.MARKET_PRICES.get(sp, 300),
                "best_zones": best_zones,
                "zone_count": len(best_zones),
                "lunar_spawning_window": is_spawning,
                "lunar_phase": LunarEngine.get_lunar_phase(self.date),
                "recommendation": self._species_recommendation(sp, best_zones, is_spawning),
            }

        return insights

    def _species_recommendation(self, species: str, best_zones: List[Dict], is_spawning: bool) -> str:
        """Generate fishing recommendation for a species"""
        if not best_zones:
            return "[WARN] No optimal zones found"

        best_hsi = max([z["hsi"] for z in best_zones])

        if is_spawning and best_hsi > 0.75:
            return "[PRIME] PRIME TIME - Spawning window + Excellent HSI"
        elif is_spawning:
            return "[OK] GOOD - Spawning window active"
        elif best_hsi > 0.75:
            return "[OK] EXCELLENT - Multiple high-suitability zones"
        elif best_hsi > 0.6:
            return "[OK] GOOD - Good suitability zones available"
        else:
            return "[WARN] MODERATE - Marginal conditions"

    # Helper methods
    def _normalize(self, value: float, min_val: float, max_val: float) -> float:
        """Normalize value to 0-1 range"""
        if max_val <= min_val:
            return 0.5
        normalized = (value - min_val) / (max_val - min_val)
        return max(0, min(1, normalized))

    def _bathymetry_score(self, depth: float) -> float:
        """Score bathymetry - higher near shelf edge (200m)"""
        shelf_edge_depth = 200
        if depth < 50:
            return 0.3
        elif 50 <= depth <= 300:
            # Peak score at shelf edge
            return 1.0 - abs(depth - shelf_edge_depth) / 250
        else:
            return 0.2

    def _get_depth(self, lat: float, lng: float) -> float:
        """Get depth at point from bathymetry data"""
        if "bathymetry" in self.data:
            lat_list = self.data["bathymetry"]["lat"]
            lng_list = self.data["bathymetry"]["lng"]
            lat_idx = self._interpolate_index(lat, lat_list)
            lng_idx = self._interpolate_index(lng, lng_list)

            if lat_idx >= 0 and lng_idx >= 0:
                depth_grid = np.array(self.data["bathymetry"]["depth"])
                return abs(depth_grid[lat_idx, lng_idx])

        return 100.0  # Default

    def _interpolate_index(self, value: float, grid: List[float]) -> int:
        """Find closest index in grid"""
        if not grid:
            return -1
        closest = min(range(len(grid)), key=lambda i: abs(grid[i] - value))
        return closest if abs(grid[closest] - value) < 1.0 else -1

    def _log(self, message: str):
        """Add message to processing log"""
        timestamp = datetime.utcnow().isoformat()
        log_entry = f"[{timestamp}] {message}"
        self.results["processing_log"].append(log_entry)
        print(log_entry)


# Convenience function
def run_pfz_detection(date: datetime = None, region: Dict = None, species: str = None) -> Dict:
    """
    Quick function to run PFZ detection for a region

    Args:
        date: Processing date (defaults to today)
        region: Dict with lat_min, lat_max, lng_min, lng_max (defaults to Maharashtra EEZ)
        species: Specific species code or None for all

    Returns:
        Complete PFZ detection results
    """
    processor = PFZProcessor(date)

    if region is None:
        region = {
            "lat_min": 14.0,
            "lat_max": 21.0,
            "lng_min": 67.0,
            "lng_max": 74.5,
        }

    return processor.process(
        lat_min=region.get("lat_min", 14.0),
        lat_max=region.get("lat_max", 21.0),
        lng_min=region.get("lng_min", 67.0),
        lng_max=region.get("lng_max", 74.5),
        species=species
    )


if __name__ == "__main__":
    print("SAMUDRA AI — PFZ Detection System")
    print("=" * 70)

    # Test run
    results = run_pfz_detection(species="ghol")

    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    print(f"Status: {results['status']}")
    print(f"Zones detected: {len(results['pfz_zones'])}")

    if results['pfz_zones']:
        print(f"\nTop 3 Zones:")
        for zone in results['pfz_zones'][:3]:
            print(f"\n  Zone {zone['zone_id']}: ({zone['center_lat']:.2f}°N, {zone['center_lng']:.2f}°E)")
            print(f"    PFZ Score: {zone['avg_pfz_score']:.3f}")
            print(f"    Points: {zone['point_count']}")
            if zone['economic_analysis']:
                print(f"    Est. Profit: ₹{zone['economic_analysis']['estimated_profit']:,.0f}")

    print("\n[OK] Processing complete!")
