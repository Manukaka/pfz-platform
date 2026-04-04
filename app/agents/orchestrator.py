"""
Agent Orchestrator — Coordinates multi-agent analysis
एजेंट समन्वयक - बहु-एजेंट विश्लेषण

Manages parallel execution of data, analysis, and decision agents
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import json

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Central coordinator for all SAMUDRA AI agents

    Responsibilities:
    - Execute data agents in parallel
    - Run analysis agents on fetched data
    - Synthesize recommendations via decision agents
    - Track agent progress and confidence
    - Provide real-time feedback to frontend
    """

    def __init__(self):
        """Initialize the orchestrator"""
        self.data_agents = {}
        self.analysis_agents = {}
        self.decision_agents = {}
        self.agent_results = {}
        self.execution_log = []
        self.start_time = None
        self.region = {}

    def register_data_agent(self, agent):
        """Register a data fetching agent"""
        self.data_agents[agent.agent_id] = agent
        logger.info(f"[DATA] Registered data agent: {agent.agent_name}")

    def register_analysis_agent(self, agent):
        """Register a specialized analysis agent"""
        self.analysis_agents[agent.agent_id] = agent
        logger.info(f"🔍 Registered analysis agent: {agent.agent_name}")

    def register_decision_agent(self, agent):
        """Register a decision/synthesis agent"""
        self.decision_agents[agent.agent_id] = agent
        logger.info(f"🤖 Registered decision agent: {agent.agent_name}")

    async def execute_phase(self, agents: Dict, data: Dict, phase_name: str) -> Dict[str, Any]:
        """
        Execute a group of agents in parallel

        Args:
            agents: Dict of agents to execute
            data: Input data for agents
            phase_name: Name of execution phase (for logging)

        Returns:
            Dict with results from all agents
        """
        if not agents:
            return {}

        logger.info(f"\n[DEPLOY] Starting {phase_name} ({len(agents)} agents)...")
        self._log_execution(f"Starting {phase_name}")

        results = {}
        tasks = []

        # Create async tasks for all agents
        for agent_id, agent in agents.items():
            agent.set_status("running")
            # Create a wrapper to capture exceptions
            task = asyncio.create_task(
                self._safe_agent_execution(agent, data)
            )
            tasks.append((agent_id, task))

        # Execute all tasks in parallel
        for agent_id, task in tasks:
            try:
                result = await task
                results[agent_id] = result
                self.agent_results[agent_id] = result
                agents[agent_id].set_status("completed")
                logger.info(f"[OK] {agents[agent_id].agent_name} completed (confidence: {result.get('confidence', 0):.2f})")
            except Exception as e:
                logger.error(f"[FAIL] {agents[agent_id].agent_name} failed: {str(e)}")
                agents[agent_id].set_status("error")
                agents[agent_id].add_error(str(e))
                results[agent_id] = {"error": str(e), "confidence": 0.0}

        self._log_execution(f"Completed {phase_name}")
        return results

    async def _safe_agent_execution(self, agent, data: Dict) -> Dict[str, Any]:
        """Safely execute an agent with error handling"""
        try:
            result = await agent.analyze(data, context=self._get_context())
            return result
        except Exception as e:
            agent.add_error(str(e))
            raise

    async def orchestrate_full_analysis(self, oceanographic_data: Dict, region: Dict) -> Dict[str, Any]:
        """
        Execute complete multi-agent analysis pipeline

        Args:
            oceanographic_data: Data from various sources
            region: Geographic region info

        Returns:
            Comprehensive analysis with all agent insights
        """
        self.start_time = datetime.utcnow()
        self.execution_log = []
        self.agent_results = {}
        self.region = region or {}

        logger.info("\n" + "="*60)
        logger.info("[OCEAN] SAMUDRA AI — Multi-Agent Analysis Starting")
        logger.info("="*60)

        # Phase 1: Parallel Data Fetching (if needed)
        logger.info("\n[DATA] PHASE 1: Data Fetching Agents")
        data_results = await self.execute_phase(
            self.data_agents,
            oceanographic_data,
            "Data Fetching Phase"
        )

        # Merge data results (handle errors gracefully)
        enhanced_data = {**oceanographic_data}
        for agent_id, result in data_results.items():
            try:
                if "raw_data" in result and result["raw_data"]:
                    enhanced_data.update(result["raw_data"])
            except Exception as e:
                logger.warning(f"Could not merge data from {agent_id}: {e}")
                pass

        # Phase 2: Parallel Specialized Analysis
        logger.info("\n🔍 PHASE 2: Analysis Agents")
        analysis_context = {
            "region": region,
            "date": datetime.utcnow().isoformat(),
            "data_sources": data_results
        }
        analysis_results = await self.execute_phase(
            self.analysis_agents,
            enhanced_data,
            "Analysis Phase"
        )

        # Phase 3: Decision/Synthesis Agents
        logger.info("\n🤖 PHASE 3: Decision Agents")
        synthesis_results = {}
        for agent_id, agent in self.decision_agents.items():
            agent.set_status("running")
            try:
                result = await agent.synthesize(analysis_results)
                synthesis_results[agent_id] = result
                self.agent_results[agent_id] = result
                agent.set_status("completed")
                logger.info(f"[OK] {agent.agent_name} synthesized recommendations")
            except Exception as e:
                logger.error(f"[FAIL] {agent.agent_name} failed: {str(e)}")
                agent.set_status("error")
                agent.add_error(str(e))
                synthesis_results[agent_id] = {"error": str(e)}

        # Compile final report
        execution_time = (datetime.utcnow() - self.start_time).total_seconds()
        final_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "execution_time_seconds": execution_time,
            "region": region,
            "phases": {
                "data_fetching": data_results,
                "analysis": analysis_results,
                "synthesis": synthesis_results,
            },
            "agent_summaries": self._get_all_agent_summaries(),
            "execution_log": self.execution_log,
        }

        logger.info("\n" + "="*60)
        logger.info(f"[OK] Analysis complete in {execution_time:.2f}s")
        logger.info("="*60 + "\n")

        return final_report

    def _get_context(self) -> Dict:
        """Get current execution context"""
        return {
            "start_time": self.start_time,
            "region": self.region,
            "agents_completed": len([a for a in self.agent_results if a]),
            "execution_log": self.execution_log
        }

    def _get_all_agent_summaries(self) -> Dict:
        """Get summaries of all agents"""
        summaries = {}

        for phase_name, agents_dict in [
            ("data", self.data_agents),
            ("analysis", self.analysis_agents),
            ("decision", self.decision_agents)
        ]:
            summaries[phase_name] = {}
            for agent_id, agent in agents_dict.items():
                summaries[phase_name][agent_id] = agent.get_summary()

        return summaries

    def _log_execution(self, message: str):
        """Log execution event with timestamp"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message
        }
        self.execution_log.append(entry)

    def get_agent_status(self) -> Dict[str, Any]:
        """Get real-time status of all agents (for frontend)"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "data_agents": {
                agent_id: agent.get_summary()
                for agent_id, agent in self.data_agents.items()
            },
            "analysis_agents": {
                agent_id: agent.get_summary()
                for agent_id, agent in self.analysis_agents.items()
            },
            "decision_agents": {
                agent_id: agent.get_summary()
                for agent_id, agent in self.decision_agents.items()
            },
            "total_agents": len(self.data_agents) + len(self.analysis_agents) + len(self.decision_agents),
            "agents_completed": len([r for r in self.agent_results if self.agent_results.get(r, {}).get('confidence', 0) > 0]),
        }

    def get_consensus_zones(self, analysis_results: Dict) -> List[Dict]:
        """
        Extract zones where multiple agents agree
        Higher consensus = better recommendations
        """
        zone_votes = {}

        # Collect all zones mentioned by agents
        for agent_id, result in analysis_results.items():
            if not result or "zones" not in result:
                continue

            zones = result.get("zones", [])
            if not zones:
                continue

            for zone in zones:
                key = (zone.get("center_lat"), zone.get("center_lng"))
                if key not in zone_votes:
                    zone_votes[key] = {
                        "zone": zone,
                        "votes": 0,
                        "agents": [],
                        "confidence_sum": 0
                    }
                zone_votes[key]["votes"] += 1
                zone_votes[key]["agents"].append(agent_id)
                zone_votes[key]["confidence_sum"] += result.get("confidence", 0.5)

        # Rank by consensus
        consensus_zones = []
        total_agents = len(self.analysis_agents) if self.analysis_agents else 1

        for (lat, lng), vote_data in zone_votes.items():
            # Safe division
            agent_count = len(vote_data["agents"]) if vote_data["agents"] else 1
            consensus_score = (
                (vote_data["votes"] / total_agents) * 0.5 +
                (vote_data["confidence_sum"] / agent_count) * 0.5
            )
            zone = vote_data["zone"].copy()
            zone["consensus_score"] = consensus_score
            zone["agent_votes"] = vote_data["votes"]
            zone["supporting_agents"] = vote_data["agents"]
            consensus_zones.append(zone)

        # Sort by consensus
        consensus_zones.sort(key=lambda z: z["consensus_score"], reverse=True)
        return consensus_zones
