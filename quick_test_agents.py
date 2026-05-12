#!/usr/bin/env python3
"""
Quick Test — Verify Agent System Imports and Basic Functionality
एजेंट प्रणाली परीक्षण

This tests basic imports and instantiation without running the full async pipeline
"""

import sys
sys.path.insert(0, '.')

print("🧪 Testing Agent System Imports...\n")

# Test 1: Base Agent imports
try:
    from app.agents.base_agent import BaseAgent, AgentStatus, DataFetchAgent, AnalysisAgent, DecisionAgent
    print("✅ Base agent classes imported successfully")
except ImportError as e:
    print(f"❌ Failed to import base agents: {e}")
    sys.exit(1)

# Test 2: Orchestrator import
try:
    from app.agents.orchestrator import AgentOrchestrator
    print("✅ AgentOrchestrator imported successfully")
except ImportError as e:
    print(f"❌ Failed to import orchestrator: {e}")
    sys.exit(1)

# Test 3: Data agents import
try:
    from app.agents.data_agents import CMEMSDataAgent, NASADataAgent, ECMWFDataAgent, GEBCODataAgent
    print("✅ Data agents imported successfully")
except ImportError as e:
    print(f"❌ Failed to import data agents: {e}")
    sys.exit(1)

# Test 4: Analysis agents import
try:
    from app.agents.analysis_agents import (
        GHOLAnalysisAgent,
        ThermalFrontAgent,
        WindCurrentAgent,
        LunarPhaseAgent,
        PrimaryProductivityAgent,
    )
    print("✅ Analysis agents imported successfully")
except ImportError as e:
    print(f"❌ Failed to import analysis agents: {e}")
    sys.exit(1)

# Test 5: Decision agents import
try:
    from app.agents.decision_agents import (
        FishingRecommendationSynthesizer,
        RiskAssessmentAgent,
        EconomicAnalysisAgent,
    )
    print("✅ Decision agents imported successfully")
except ImportError as e:
    print(f"❌ Failed to import decision agents: {e}")
    sys.exit(1)

# Test 6: Instantiate orchestrator
try:
    orch = AgentOrchestrator()
    print("✅ AgentOrchestrator instantiated successfully")
except Exception as e:
    print(f"❌ Failed to instantiate orchestrator: {e}")
    sys.exit(1)

# Test 7: Register agents
try:
    orch.register_data_agent(CMEMSDataAgent())
    orch.register_data_agent(NASADataAgent())
    orch.register_data_agent(ECMWFDataAgent())
    orch.register_data_agent(GEBCODataAgent())
    print("✅ Data agents registered (4/4)")

    orch.register_analysis_agent(GHOLAnalysisAgent())
    orch.register_analysis_agent(ThermalFrontAgent())
    orch.register_analysis_agent(WindCurrentAgent())
    orch.register_analysis_agent(LunarPhaseAgent())
    orch.register_analysis_agent(PrimaryProductivityAgent())
    print("✅ Analysis agents registered (5/5)")

    orch.register_decision_agent(FishingRecommendationSynthesizer())
    orch.register_decision_agent(RiskAssessmentAgent())
    orch.register_decision_agent(EconomicAnalysisAgent())
    print("✅ Decision agents registered (3/3)")

except Exception as e:
    print(f"❌ Failed to register agents: {e}")
    sys.exit(1)

# Test 8: Check agent status
try:
    status = orch.get_agent_status()
    print(f"✅ Agent status retrieved:")
    print(f"   Total agents: {status['total_agents']}")
    print(f"   Data agents: {len(status['data_agents'])}")
    print(f"   Analysis agents: {len(status['analysis_agents'])}")
    print(f"   Decision agents: {len(status['decision_agents'])}")
except Exception as e:
    print(f"❌ Failed to get agent status: {e}")
    sys.exit(1)

# Test 9: Test agent instantiation without async
try:
    test_agent = GHOLAnalysisAgent()
    test_agent.add_reasoning("Test reasoning step")
    test_agent.set_status("completed")
    summary = test_agent.get_summary()
    print(f"✅ Agent methods working:")
    print(f"   Agent ID: {summary['agent_id']}")
    print(f"   Status: {summary['status']}")
    print(f"   Reasoning steps: {summary['reasoning_steps']}")
except Exception as e:
    print(f"❌ Failed to test agent methods: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("✅ ALL TESTS PASSED!")
print("="*60)
print("\nAgent system is ready for deployment.")
print("Run: python app/api.py")
print("Then visit: http://localhost:5000")
