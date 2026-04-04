"""
SAMUDRA AI — Agent Framework
एजेंट प्रणाली - बुद्धिमान विश्लेषण

Base class for all specialized agents in the multi-agent system
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


class BaseAgent(ABC):
    """
    Abstract base class for all SAMUDRA AI agents

    Agents are specialized intelligence modules that:
    - Analyze specific aspects of fishing data
    - Provide domain-specific recommendations
    - Contribute to collective decision-making
    - Report confidence levels and reasoning
    """

    def __init__(self, agent_id: str, agent_name: str, specialization: str):
        """
        Initialize an agent

        Args:
            agent_id: Unique identifier (e.g., 'ghol_agent', 'wind_agent')
            agent_name: Human-readable name
            specialization: Domain of expertise
        """
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.specialization = specialization
        self.status = AgentStatus.IDLE
        self.confidence = 0.0
        self.last_update = None
        self.results = {}
        self.reasoning = []
        self.errors = []

    @abstractmethod
    async def analyze(self, data: Dict[str, Any], context: Dict = None) -> Dict[str, Any]:
        """
        Analyze data and return insights

        Args:
            data: Input data dict (oceanographic, meteorological, etc.)
            context: Additional context (date, region, previous agent results)

        Returns:
            Dict with:
            {
                "recommendations": [...],
                "zones": [...],
                "confidence": 0.0-1.0,
                "reasoning": [...],
                "metadata": {...}
            }
        """
        pass

    def set_status(self, status: AgentStatus):
        """Update agent status"""
        self.status = status
        self.last_update = datetime.utcnow().isoformat()

    def add_reasoning(self, reasoning: str):
        """Add reasoning step to explain analysis"""
        self.reasoning.append({
            "timestamp": datetime.utcnow().isoformat(),
            "step": reasoning
        })

    def add_error(self, error: str):
        """Log an error during analysis"""
        self.errors.append({
            "timestamp": datetime.utcnow().isoformat(),
            "error": error
        })

    def get_summary(self) -> Dict:
        """Get agent status summary"""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "specialization": self.specialization,
            "status": self.status.value if hasattr(self.status, 'value') else str(self.status),
            "confidence": self.confidence,
            "last_update": self.last_update,
            "reasoning_steps": len(self.reasoning),
            "errors": len(self.errors)
        }


class DataFetchAgent(BaseAgent):
    """Base class for agents that fetch data from external sources"""

    async def analyze(self, data: Dict[str, Any], context: Dict = None) -> Dict[str, Any]:
        """
        Data fetch agents don't analyze - they just fetch
        Override this to fetch from your data source
        """
        return {
            "raw_data": {},
            "confidence": 0.5,
            "source": self.specialization,
            "timestamp": datetime.utcnow().isoformat(),
        }


class AnalysisAgent(BaseAgent):
    """Base class for agents that perform specialized analysis"""

    async def analyze(self, data: Dict[str, Any], context: Dict = None) -> Dict[str, Any]:
        """
        Analyze data from a specialized perspective
        Must be implemented by subclasses
        """
        pass


class DecisionAgent(BaseAgent):
    """Base class for agents that synthesize recommendations"""

    async def synthesize(self, agent_results: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Synthesize recommendations from multiple agents

        Args:
            agent_results: Results from all other agents

        Returns:
            Synthesized recommendations and final confidence
        """
        pass

    async def analyze(self, data: Dict[str, Any], context: Dict = None) -> Dict[str, Any]:
        """Decision agents typically work with other agents' output"""
        raise NotImplementedError("Use synthesize() instead")
