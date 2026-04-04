"""
SAMUDRA AI Agent Framework
एजेंट प्रणाली - बुद्धिमान बहु-एजेंट विश्लेषण

Multi-agent system for intelligent fishing zone detection and analysis
"""

from .base_agent import BaseAgent, AgentStatus, DataFetchAgent, AnalysisAgent, DecisionAgent
from .orchestrator import AgentOrchestrator
from .data_agents import (
    CMEMSDataAgent,
    NASADataAgent,
    ECMWFDataAgent,
    GEBCODataAgent,
)
from .analysis_agents import (
    GHOLAnalysisAgent,
    ThermalFrontAgent,
    WindCurrentAgent,
    LunarPhaseAgent,
    PrimaryProductivityAgent,
)
from .decision_agents import (
    FishingRecommendationSynthesizer,
    RiskAssessmentAgent,
    EconomicAnalysisAgent,
)

__all__ = [
    "BaseAgent",
    "AgentStatus",
    "DataFetchAgent",
    "AnalysisAgent",
    "DecisionAgent",
    "AgentOrchestrator",
    "CMEMSDataAgent",
    "NASADataAgent",
    "ECMWFDataAgent",
    "GEBCODataAgent",
    "GHOLAnalysisAgent",
    "ThermalFrontAgent",
    "WindCurrentAgent",
    "LunarPhaseAgent",
    "PrimaryProductivityAgent",
    "FishingRecommendationSynthesizer",
    "RiskAssessmentAgent",
    "EconomicAnalysisAgent",
]
