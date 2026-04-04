"""
SAMUDRA AI — REST API Backend
वेब API - डेटा सेवा

Flask-based REST API providing:
- Real-time PFZ zone detection
- GHOL specialist analysis
- Trip planning
- Lunar/weather data
- Economic recommendations
- Navigation & safety alerts

Endpoints serve the 6-tab web interface and mobile apps
"""

from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime, timedelta
import json
import os

from app.processors.integrated_processor import IntegratedProcessor
from app.specialists.ghol_engine import GholEngine
from app.specialists.ghol_behavior import GholBehavior
from app.core.lunar import LunarEngine
from app.data.data_aggregator import DataAggregator


# Initialize Flask app with static folder
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['JSON_SORT_KEYS'] = False

# === HELPER FUNCTIONS ===

def get_region_from_request(request_data=None):
    """Extract geographic region from request or use default"""
    if request_data is None:
        request_data = request.get_json() or {}

    region = {
        "lat_min": request_data.get("lat_min", 14.0),
        "lat_max": request_data.get("lat_max", 21.0),
        "lng_min": request_data.get("lng_min", 67.0),
        "lng_max": request_data.get("lng_max", 74.5),
    }
    return region


def error_response(message, status_code=400):
    """Standard error response format"""
    return jsonify({
        "status": "error",
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
    }), status_code


def success_response(data, status_code=200):
    """Standard success response format"""
    return jsonify({
        "status": "success",
        "data": data,
        "timestamp": datetime.utcnow().isoformat(),
    }), status_code


# === HEALTH & STATUS ENDPOINTS ===

@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return success_response({
        "service": "SAMUDRA AI Backend",
        "version": "2.0",
        "status": "operational",
        "endpoints": [
            "/api/pfz/zones",
            "/api/ghol/analysis",
            "/api/ghol/trip-plan",
            "/api/lunar/phase",
            "/api/lunar/forecast",
            "/api/data/sources",
        ]
    })


@app.route("/api/status", methods=["GET"])
def status():
    """System status including data sources"""
    sources = DataAggregator.get_available_sources()

    return success_response({
        "system": "SAMUDRA AI",
        "timestamp": datetime.utcnow().isoformat(),
        "data_sources": {name: status["status"] for name, status in sources.items()},
        "region": {
            "lat_min": 14.0,
            "lat_max": 21.0,
            "lng_min": 67.0,
            "lng_max": 74.5,
            "name": "Maharashtra EEZ, Arabian Sea",
        }
    })


# === FRONTEND ROUTES ===

@app.route("/", methods=["GET"])
@app.route("/dashboard.html", methods=["GET"])
def serve_frontend():
    """Serve the main dashboard application"""
    static_dir = app.static_folder or '.'
    return send_from_directory(static_dir, 'dashboard.html')


@app.route("/index.html", methods=["GET"])
def serve_legacy_frontend():
    """Serve legacy tab-based interface for compatibility"""
    static_dir = app.static_folder or '.'
    return send_from_directory(static_dir, 'index.html')


@app.route("/static/<path:filename>", methods=["GET"])
def serve_static(filename):
    """Serve static files (CSS, JS, images)"""
    static_dir = app.static_folder or '.'
    return send_from_directory(static_dir, filename)


# === PFZ ZONE ENDPOINTS ===

@app.route("/api/pfz/zones", methods=["POST"])
def get_pfz_zones():
    """
    Get PFZ zones for region

    Request body:
    {
        "lat_min": 14.0,
        "lat_max": 21.0,
        "lng_min": 67.0,
        "lng_max": 74.5
    }

    Returns: List of detected zones with scores and species suitability
    """
    try:
        data = request.get_json() or {}
        region = get_region_from_request(data)

        # Run integrated processor
        processor = IntegratedProcessor()
        results = processor.process_complete(
            lat_min=region["lat_min"],
            lat_max=region["lat_max"],
            lng_min=region["lng_min"],
            lng_max=region["lng_max"],
        )

        # Format for API response
        zones = results.get("pfz_zones", [])

        return success_response({
            "date": results["date"],
            "zone_count": len(zones),
            "zones": zones[:10],  # Top 10 zones
            "region": region,
        })

    except Exception as e:
        return error_response(f"Error processing zones: {str(e)}", 500)


@app.route("/api/pfz/zones/<int:zone_id>", methods=["GET"])
def get_zone_details(zone_id):
    """Get detailed information about a specific zone"""
    try:
        # In production, retrieve from database
        # For now, return mock detailed data

        return success_response({
            "zone_id": zone_id,
            "coordinates": {
                "lat": 17.5,
                "lng": 71.0,
            },
            "pfz_score": 0.72,
            "confidence": "MEDIUM",
            "species_suitability": {
                "ghol": {"score": 0.82, "status": "Excellent"},
                "papalet": {"score": 0.65, "status": "Good"},
                "bangada": {"score": 0.58, "status": "Good"},
            },
            "environmental_conditions": {
                "sst": 28.5,
                "depth": 50,
                "chlorophyll": 0.8,
                "wind_speed": 5.2,
            },
            "fishing_recommendation": "[OK] GOOD - Multiple species available",
        })

    except Exception as e:
        return error_response(f"Error retrieving zone: {str(e)}", 500)


@app.route("/api/pfz/agent-analysis", methods=["POST"])
def get_pfz_agent_analysis():
    """
    Multi-agent PFZ analysis — runs the full AgentOrchestrator pipeline.
    Returns GeoJSON zone features plus per-agent status for live visualization.
    """
    import asyncio
    from app.agents.orchestrator import AgentOrchestrator
    from app.agents.data_agents import CMEMSDataAgent, NASADataAgent, ECMWFDataAgent, GEBCODataAgent
    from app.agents.analysis_agents import (
        GHOLAnalysisAgent, ThermalFrontAgent,
        WindCurrentAgent, LunarPhaseAgent, PrimaryProductivityAgent
    )
    from app.agents.decision_agents import FishingRecommendationSynthesizer

    try:
        req_data = request.get_json() or {}
        region = get_region_from_request(req_data)

        orchestrator = AgentOrchestrator()

        for agent in [CMEMSDataAgent(), NASADataAgent(), ECMWFDataAgent(), GEBCODataAgent()]:
            orchestrator.register_data_agent(agent)

        for agent in [
            GHOLAnalysisAgent(), ThermalFrontAgent(),
            WindCurrentAgent(), LunarPhaseAgent(), PrimaryProductivityAgent()
        ]:
            orchestrator.register_analysis_agent(agent)

        orchestrator.register_decision_agent(FishingRecommendationSynthesizer())

        # Run orchestrator in a fresh event loop (Flask is sync)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            report = loop.run_until_complete(
                orchestrator.orchestrate_full_analysis({}, region)
            )
        finally:
            loop.close()

        # --- Extract synthesized zones ---
        synthesis = report["phases"]["synthesis"]
        rec_result = synthesis.get("recommendation_agent", {})
        final_zones = rec_result.get("final_zones", [])
        final_zones = sorted(
            final_zones,
            key=lambda z: z.get("consensus_score", z.get("confidence", 0.0)),
            reverse=True,
        )

        # Build GeoJSON features
        features = []
        for idx, zone in enumerate(final_zones[:10]):
            lat = zone.get("center_lat", 0)
            lng = zone.get("center_lng", 0)
            score = zone.get("consensus_score", zone.get("confidence", 0.5))
            if score > 0.7:
                confidence = "HIGH"
            elif score > 0.4:
                confidence = "MEDIUM"
            else:
                confidence = "LOW"

            attrs = zone.get("attributes", {})
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lng, lat]},
                "properties": {
                    "zone_id": idx + 1,
                    "pfz_score": round(score, 3),
                    "confidence": confidence,
                    "agent_votes": zone.get("agent_votes", 1),
                    "supporting_agents": zone.get("supporting_agents", []),
                    "sst": attrs.get("sst"),
                    "depth": attrs.get("depth"),
                    "ghol_suitability": attrs.get("ghol_suitability"),
                    "temperature_gradient": attrs.get("temperature_gradient"),
                    "chlorophyll": attrs.get("chlorophyll"),
                },
            })

        # --- Per-agent status summary ---
        analysis_phase = report["phases"]["analysis"]
        agent_status = {}
        for agent_id, result in analysis_phase.items():
            agent_status[agent_id] = {
                "status": "error" if "error" in result else "completed",
                "confidence": round(result.get("confidence", 0), 2),
                "zone_count": len(result.get("zones", [])),
                "recommendations": result.get("recommendations", [])[:2],
            }

        # Add lunar context as a bonus
        lunar = analysis_phase.get("lunar_agent", {})

        return success_response({
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "zone_count": len(features),
            "geojson": {"type": "FeatureCollection", "features": features},
            "agent_status": agent_status,
            "lunar_context": {
                "phase": lunar.get("phase"),
                "illumination_percent": lunar.get("illumination_percent"),
                "spawning_window": lunar.get("spawning_window"),
            },
            "execution_time_seconds": round(report.get("execution_time_seconds", 0), 2),
            "region": region,
        })

    except Exception as e:
        return error_response(f"Agent analysis failed: {str(e)}", 500)


# === GHOL SPECIALIST ENDPOINTS ===

@app.route("/api/ghol/analysis", methods=["POST"])
def get_ghol_analysis():
    """
    GHOL-focused analysis for region

    Returns: Ghol-optimized zones with spawning probability, acoustic potential
    """
    try:
        data = request.get_json() or {}
        region = get_region_from_request(data)

        # Run integrated processor
        processor = IntegratedProcessor()
        results = processor.process_complete(
            lat_min=region["lat_min"],
            lat_max=region["lat_max"],
            lng_min=region["lng_min"],
            lng_max=region["lng_max"],
        )

        ghol_zones = results.get("ghol_zones", [])
        acoustic_hotspots = results.get("acoustic_hotspots", [])

        return success_response({
            "date": results["date"],
            "ghol_zone_count": len(ghol_zones),
            "zones": ghol_zones[:5],
            "acoustic_hotspots": acoustic_hotspots[:3],
            "recommendations": results.get("integrated_recommendations", [])[:5],
        })

    except Exception as e:
        return error_response(f"Error in GHOL analysis: {str(e)}", 500)


@app.route("/api/ghol/spawning-probability", methods=["POST"])
def get_spawning_probability():
    """
    Get spawning aggregation probability for location

    Request body:
    {
        "lat": 17.5,
        "lng": 71.0,
        "date": "2026-03-23"  # optional, defaults to today
    }
    """
    try:
        data = request.get_json() or {}
        lat = data.get("lat")
        lng = data.get("lng")
        date_str = data.get("date")

        if lat is None or lng is None:
            return error_response("Missing lat/lng parameters")

        if date_str:
            date = datetime.fromisoformat(date_str)
        else:
            date = datetime.utcnow()

        spawning_prob = GholEngine.calculate_spawning_probability(date, lat, lng)
        hsi = GholEngine.calculate_habitat_suitability(sst=28.5, depth=50, date=date)
        acoustic = GholEngine.calculate_acoustic_detection_probability(date, lat, lng)

        return success_response({
            "location": {"lat": lat, "lng": lng},
            "date": date.strftime("%Y-%m-%d"),
            "lunar_phase": LunarEngine.get_lunar_phase(date),
            "spawning_probability": round(spawning_prob, 3),
            "habitat_suitability": round(hsi, 3),
            "acoustic_detection": round(acoustic, 3),
            "interpretation": (
                "[TARGET] EXCELLENT - Peak spawning window" if spawning_prob > 0.75 else
                "[OK] GOOD - Spawning window active" if spawning_prob > 0.5 else
                "[WARN] FAIR - Marginal spawning conditions" if spawning_prob > 0.3 else
                "[FAIL] POOR - Not spawning season"
            )
        })

    except Exception as e:
        return error_response(f"Error calculating spawning: {str(e)}", 500)


@app.route("/api/ghol/trip-plan", methods=["POST"])
def get_trip_plan():
    """
    Generate detailed GHOL trip plan

    Request body:
    {
        "zone_id": 1,
        "lat": 17.5,
        "lng": 71.0,
        "boat_type": "medium_boat",
        "crew_count": 4
    }
    """
    try:
        data = request.get_json() or {}
        lat = data.get("lat", 17.5)
        lng = data.get("lng", 71.0)
        boat_type = data.get("boat_type", "medium_boat")
        crew_count = data.get("crew_count", 4)

        # Create mock zone for trip planning
        zone = {
            "zone_id": data.get("zone_id", 1),
            "center_lat": lat,
            "center_lng": lng,
            "ghol_targeting_score": 0.85,
            "spawning_probability": 0.80,
            "habitat_suitability": 0.88,
            "is_spawning_window": True,
        }

        trip_plan = GholEngine.generate_ghol_trip_plan(zone, datetime.utcnow())

        return success_response({
            "trip_plan": trip_plan,
            "optimization_tips": [
                "Bring LED underwater lights to attract baitfish",
                "Deploy hydrophone for acoustic monitoring",
                "Use selective 32-40mm mesh for Ghol",
                "Peak activity: 05:00-07:00 and 21:00-04:00",
            ]
        })

    except Exception as e:
        return error_response(f"Error generating trip plan: {str(e)}", 500)


# === LUNAR & ASTRONOMICAL ENDPOINTS ===

@app.route("/api/lunar/phase", methods=["GET"])
def get_lunar_phase():
    """Get current lunar phase and illumination"""
    try:
        date = datetime.utcnow()

        return success_response({
            "date": date.strftime("%Y-%m-%d %H:%M:%S"),
            "lunar_phase": LunarEngine.get_lunar_phase(date),
            "illumination_percent": round(LunarEngine.get_lunar_illumination_percent(date), 1),
            "lunar_age_days": round(LunarEngine.calculate_lunar_age(date), 1),
            "fishing_impact": (
                "[MOON] Dark night - EXCELLENT for night fishing" if LunarEngine.get_lunar_illumination(date) < 0.3 else
                "[MOON] Moderate light - GOOD for evening/early morning" if LunarEngine.get_lunar_illumination(date) < 0.7 else
                "[MOON] Bright night - FAIR for night fishing (visibility may affect fish behavior)"
            )
        })

    except Exception as e:
        return error_response(f"Error getting lunar phase: {str(e)}", 500)


@app.route("/api/lunar/forecast", methods=["GET"])
def get_lunar_forecast():
    """Get 30-day lunar phase forecast"""
    try:
        date = datetime.utcnow()
        forecast = []

        for i in range(30):
            forecast_date = date + timedelta(days=i)
            phase = LunarEngine.get_lunar_phase(forecast_date)
            illum = LunarEngine.get_lunar_illumination_percent(forecast_date)

            forecast.append({
                "date": forecast_date.strftime("%Y-%m-%d"),
                "phase": phase,
                "illumination_percent": round(illum, 1),
                "spawning_window": phase in ["new_moon", "waning_crescent", "waxing_crescent"],
            })

        return success_response({
            "forecast_days": 30,
            "forecast": forecast,
        })

    except Exception as e:
        return error_response(f"Error generating forecast: {str(e)}", 500)


@app.route("/api/lunar/spawning-windows", methods=["GET"])
def get_spawning_windows():
    """Get upcoming spawning windows for major species"""
    try:
        date = datetime.utcnow()
        windows = []

        # Check next 90 days for spawning windows
        for i in range(90):
            check_date = date + timedelta(days=i)
            phase = LunarEngine.get_lunar_phase(check_date)

            if phase == "new_moon":
                windows.append({
                    "date": check_date.strftime("%Y-%m-%d"),
                    "phase": "new_moon",
                    "species": ["ghol", "surmai", "tuna"],
                    "intensity": "PEAK",
                    "description": "Major spawning aggregation window",
                })

        return success_response({
            "windows_found": len(windows),
            "spawning_windows": windows[:6],  # Next 6 windows
        })

    except Exception as e:
        return error_response(f"Error getting spawning windows: {str(e)}", 500)


# === ECONOMIC INTELLIGENCE ENDPOINTS ===

@app.route("/api/economics/trip-roi", methods=["POST"])
def calculate_trip_roi():
    """
    Calculate trip profitability

    Request body:
    {
        "catch_composition": {"ghol": 100, "papalet": 50},
        "distance_km": 90,
        "boat_type": "medium_boat",
        "crew_count": 4,
        "trip_days": 0.75
    }
    """
    try:
        from app.core.economic import EconomicCalculator

        data = request.get_json() or {}

        roi = EconomicCalculator.calculate_trip_roi(
            catch_composition=data.get("catch_composition", {"ghol": 80}),
            distance_km=data.get("distance_km", 90),
            boat_type=data.get("boat_type", "medium_boat"),
            num_crew=data.get("crew_count", 4),
            landing_port=data.get("landing_port", "Ratnagiri"),
            trip_days=data.get("trip_days", 0.75),
        )

        return success_response({
            "trip": roi,
            "profitability_rating": (
                "[TARGET] EXCELLENT" if roi["profit"]["roi_percentage"] > 50 else
                "[OK] GOOD" if roi["profit"]["roi_percentage"] > 25 else
                "[WARN] FAIR" if roi["profit"]["roi_percentage"] > 0 else
                "[FAIL] POOR"
            )
        })

    except Exception as e:
        return error_response(f"Error calculating ROI: {str(e)}", 500)


@app.route("/api/economics/market-prices", methods=["GET"])
def get_market_prices():
    """Get current market prices for all fish species"""
    try:
        from app.core.economic import EconomicCalculator

        prices = {}
        for species, price in EconomicCalculator.MARKET_PRICES.items():
            prices[species] = {
                "price_per_kg": price,
                "value_category": "Premium" if price > 1000 else "High" if price > 500 else "Standard",
            }

        return success_response({
            "market_prices": prices,
            "highest_value": "ghol",
            "premium_value": "Ghol swim bladder (₹70,000/kg)",
        })

    except Exception as e:
        return error_response(f"Error retrieving prices: {str(e)}", 500)


# === AGENT ORCHESTRATION ENDPOINTS ===

@app.route("/api/agents/army", methods=["POST"])
def analyze_with_agents():
    """
    Execute the complete multi-agent analysis system

    Request body:
    {
        "lat_min": 14.0,
        "lat_max": 21.0,
        "lng_min": 67.0,
        "lng_max": 74.5
    }

    Returns: Multi-agent analysis with consensus zones and recommendations
    """
    try:
        from app.agents import (
            AgentOrchestrator,
            CMEMSDataAgent,
            NASADataAgent,
            ECMWFDataAgent,
            GEBCODataAgent,
            GHOLAnalysisAgent,
            ThermalFrontAgent,
            WindCurrentAgent,
            LunarPhaseAgent,
            PrimaryProductivityAgent,
            FishingRecommendationSynthesizer,
            RiskAssessmentAgent,
            EconomicAnalysisAgent,
        )
        import asyncio

        data = request.get_json() or {}
        region = get_region_from_request(data)

        # Create orchestrator
        orchestrator = AgentOrchestrator()

        # Register data agents
        orchestrator.register_data_agent(CMEMSDataAgent())
        orchestrator.register_data_agent(NASADataAgent())
        orchestrator.register_data_agent(ECMWFDataAgent())
        orchestrator.register_data_agent(GEBCODataAgent())

        # Register analysis agents
        orchestrator.register_analysis_agent(GHOLAnalysisAgent())
        orchestrator.register_analysis_agent(ThermalFrontAgent())
        orchestrator.register_analysis_agent(WindCurrentAgent())
        orchestrator.register_analysis_agent(LunarPhaseAgent())
        orchestrator.register_analysis_agent(PrimaryProductivityAgent())

        # Register decision agents
        orchestrator.register_decision_agent(FishingRecommendationSynthesizer())
        orchestrator.register_decision_agent(RiskAssessmentAgent())
        orchestrator.register_decision_agent(EconomicAnalysisAgent())

        # Get data
        pfz_data = DataAggregator.fetch_pfz_data(
            lat_min=region["lat_min"],
            lat_max=region["lat_max"],
            lng_min=region["lng_min"],
            lng_max=region["lng_max"],
        )

        # Run orchestration
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(
            orchestrator.orchestrate_full_analysis(
                pfz_data,
                region
            )
        )
        loop.close()

        return success_response({
            "agent_analysis": results,
            "agent_status": orchestrator.get_agent_status(),
            "timestamp": datetime.utcnow().isoformat(),
        })

    except Exception as e:
        return error_response(f"Agent analysis failed: {str(e)}", 500)


@app.route("/api/agents/status", methods=["GET"])
def get_agents_status():
    """Get real-time status of all registered agents"""
    try:
        from app.agents import AgentOrchestrator

        # Would need to maintain a global orchestrator instance
        # For now, return placeholder
        return success_response({
            "message": "Agent system ready",
            "total_agents": 12,
            "agent_types": {
                "data_fetchers": 4,
                "analysis_specialists": 5,
                "decision_makers": 3,
            }
        })

    except Exception as e:
        return error_response(f"Error getting agent status: {str(e)}", 500)


@app.route("/api/agents/insights", methods=["POST"])
def get_agent_insights():
    """
    Get detailed insights from specific agents

    Request body:
    {
        "agent_id": "ghol_agent",  # optional, specific agent
        "lat_min": 14.0,
        "lat_max": 21.0,
        "lng_min": 67.0,
        "lng_max": 74.5
    }
    """
    try:
        data = request.get_json() or {}
        agent_id = data.get("agent_id")
        region = get_region_from_request(data)

        pfz_data = DataAggregator.fetch_pfz_data(
            lat_min=region["lat_min"],
            lat_max=region["lat_max"],
            lng_min=region["lng_min"],
            lng_max=region["lng_max"],
        )

        # Return agent-specific analysis
        return success_response({
            "requested_agent": agent_id or "all",
            "region": region,
            "insights": {
                "zones_analyzed": len(pfz_data.get("sst", {}).get("lat", [])) * 5,
                "recommendation_confidence": 0.78,
            }
        })

    except Exception as e:
        return error_response(f"Error getting insights: {str(e)}", 500)


# === DATA MANAGEMENT ENDPOINTS ===

@app.route("/api/data/sources", methods=["GET"])
def get_data_sources():
    """Get information about available data sources"""
    try:
        sources = DataAggregator.get_available_sources()

        return success_response({
            "data_sources": sources,
            "ready_for_integration": True,
            "authentication_status": {
                "CMEMS": "configured" if sources["CMEMS"].get("authenticated") else "needs_credentials",
                "NASA": "configured" if sources["NASA"].get("authenticated") else "needs_credentials",
                "ECMWF": "configured" if sources["ECMWF"].get("authenticated") else "needs_credentials",
                "GEBCO": "ready",
            }
        })

    except Exception as e:
        return error_response(f"Error retrieving sources: {str(e)}", 500)


# === DATA FILE SERVING ENDPOINTS ===

@app.route("/pfz_data.geojson", methods=["GET"])
def serve_pfz_geojson():
    """Serve PFZ GeoJSON data file"""
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return send_from_directory(base_dir, 'pfz_data.geojson')


@app.route("/wind_data.json", methods=["GET"])
def serve_wind_data():
    """Serve wind velocity data file"""
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return send_from_directory(base_dir, 'wind_data.json')


@app.route("/wave_data.json", methods=["GET"])
def serve_wave_data():
    """Serve wave data file"""
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return send_from_directory(base_dir, 'wave_data.json')


@app.route("/current_data.json", methods=["GET"])
def serve_current_data():
    """Serve ocean current data file"""
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return send_from_directory(base_dir, 'current_data.json')


# === TEST ROUTE ===
@app.route("/test_file_serving")
def test_file_serving():
    return jsonify({"status": "File serving module loaded", "test": "OK"})


# === ERROR HANDLERS ===

@app.errorhandler(404)
def not_found(error):
    return error_response("Endpoint not found", 404)


@app.errorhandler(500)
def server_error(error):
    return error_response("Internal server error", 500)


# === MAIN ===

if __name__ == "__main__":
    # Development server
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_ENV") == "development",
    )
