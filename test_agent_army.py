#!/usr/bin/env python3
"""
Test Script — Agent Army Execution
एजेंट आर्मी परीक्षण

Run this to test the complete multi-agent system directly from command line
"""

import asyncio
import json
import sys
from datetime import datetime
from pprint import pprint

# Add parent directory to path
sys.path.insert(0, '.')

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
from app.data.data_aggregator import DataAggregator


async def main():
    """Run complete agent army analysis"""

    print("\n" + "="*70)
    print("🤖 SAMUDRA AI — AGENT ARMY TEST")
    print("="*70)

    # Create orchestrator
    print("\n📋 Setting up orchestrator...")
    orchestrator = AgentOrchestrator()

    # Register data agents
    print("   Registering Data Agents...")
    orchestrator.register_data_agent(CMEMSDataAgent())
    orchestrator.register_data_agent(NASADataAgent())
    orchestrator.register_data_agent(ECMWFDataAgent())
    orchestrator.register_data_agent(GEBCODataAgent())

    # Register analysis agents
    print("   Registering Analysis Agents...")
    orchestrator.register_analysis_agent(GHOLAnalysisAgent())
    orchestrator.register_analysis_agent(ThermalFrontAgent())
    orchestrator.register_analysis_agent(WindCurrentAgent())
    orchestrator.register_analysis_agent(LunarPhaseAgent())
    orchestrator.register_analysis_agent(PrimaryProductivityAgent())

    # Register decision agents
    print("   Registering Decision Agents...")
    orchestrator.register_decision_agent(FishingRecommendationSynthesizer())
    orchestrator.register_decision_agent(RiskAssessmentAgent())
    orchestrator.register_decision_agent(EconomicAnalysisAgent())

    # Get data
    print("\n📊 Fetching oceanographic data...")
    region = {
        "lat_min": 14.0,
        "lat_max": 21.0,
        "lng_min": 67.0,
        "lng_max": 74.5,
    }

    pfz_data = DataAggregator.fetch_pfz_data(
        lat_min=region["lat_min"],
        lat_max=region["lat_max"],
        lng_min=region["lng_min"],
        lng_max=region["lng_max"],
    )

    print(f"   ✓ Data fetched for {region['lat_min']}-{region['lat_max']}°N, "
          f"{region['lng_min']}-{region['lng_max']}°E")

    # Run orchestration
    print("\n🚀 STARTING AGENT ARMY EXECUTION...\n")
    start_time = datetime.utcnow()

    results = await orchestrator.orchestrate_full_analysis(pfz_data, region)

    execution_time = (datetime.utcnow() - start_time).total_seconds()

    print("\n" + "="*70)
    print("✅ AGENT ARMY EXECUTION COMPLETE")
    print("="*70)
    print(f"\n⏱️  Execution Time: {execution_time:.2f} seconds\n")

    # Display results
    print("📌 AGENT SUMMARIES:")
    print("-" * 70)

    summaries = results['agent_summaries']
    for phase_name, agents_dict in summaries.items():
        print(f"\n{phase_name.upper()} AGENTS:")
        for agent_id, summary in agents_dict.items():
            status_emoji = "✅" if summary['status'] == 'completed' else "❌" if summary['status'] == 'error' else "⏸️"
            print(f"  {status_emoji} {summary['agent_name']}")
            print(f"     Status: {summary['status']}")
            print(f"     Confidence: {summary['confidence']:.2f}")
            print(f"     Reasoning steps: {summary['reasoning_steps']}")

    # Display synthesis results
    print("\n" + "="*70)
    print("🎯 SYNTHESIS RESULTS:")
    print("-" * 70)

    synthesis = results['phases']['synthesis']

    if 'recommendation_agent' in synthesis:
        rec = synthesis['recommendation_agent']
        print(f"\n🎣 Fishing Recommendations (Confidence: {rec.get('confidence', 0):.2f}):")

        zones = rec.get('zones', [])
        print(f"   Total zones identified: {len(zones)}")

        if zones:
            print("\n   Top 3 Consensus Zones:")
            for i, zone in enumerate(zones[:3], 1):
                votes = zone.get('agent_votes', 0)
                consensus = zone.get('consensus_score', 0)
                print(f"\n   {i}. Zone ({zone['center_lat']:.2f}°N, {zone['center_lng']:.2f}°E)")
                print(f"      Consensus Score: {consensus:.2f} ({votes} agents agree)")
                print(f"      Supporting Agents: {', '.join(zone.get('supporting_agents', []))}")

        recommendations = rec.get('recommendations', [])
        if recommendations:
            print("\n   Recommendations:")
            for rec_text in recommendations[:5]:
                print(f"   • {rec_text}")

    # Risk assessment
    if 'risk_agent' in synthesis:
        risk = synthesis['risk_agent']
        print(f"\n⚠️ Risk Assessment: {risk.get('risk_level', 'UNKNOWN')}")
        print(f"   Confidence: {risk.get('confidence', 0):.2f}")
        warnings = risk.get('warnings', [])
        if warnings:
            for warning in warnings:
                print(f"   • {warning}")

    # Economic analysis
    if 'economic_agent' in synthesis:
        econ = synthesis['economic_agent']
        print(f"\n💰 Economic Viability: {econ.get('profitability_rating', 'UNKNOWN')}")
        print(f"   Confidence: {econ.get('confidence', 0):.2f}")

    # Execution log
    print("\n" + "="*70)
    print("📜 EXECUTION LOG:")
    print("-" * 70)
    log_entries = results['execution_log']
    for entry in log_entries[:10]:  # Show first 10
        print(f"[{entry['timestamp']}] {entry['message']}")

    print("\n" + "="*70)
    print("\n✨ Agent Army ready for production!\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ Agent Army interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Agent Army error: {str(e)}")
        import traceback
        traceback.print_exc()
