"""
Claude Opus 4.7 Agentic Orchestrator for DaryaSagar.
Uses tool_use to invoke 8 specialized sub-agents, then synthesizes
a multi-lingual response for west coast fishermen.
"""
import anthropic
import json
from typing import Optional
from datetime import datetime

import structlog

from ...core.config import settings
from .tools import AGENT_TOOLS, execute_tool

logger = structlog.get_logger()

# System prompt — cached via cache_control (>1024 tokens → ephemeral cache)
_SYSTEM_BASE = """You are DaryaSagar AI — India's most advanced ocean intelligence assistant for west coast fishermen. You serve fishermen across Gujarat, Maharashtra, Goa, Karnataka, and Kerala.

YOUR ROLE:
- Orchestrate specialized ocean data, ML inference, safety, and compliance tools to give fishermen the best possible guidance
- ALWAYS check safety before recommending any fishing location
- ALWAYS check MPA compliance before recommending a specific lat/lon
- Synthesize multi-source information into clear, actionable advice

TOOLS AVAILABLE (use them):
1. get_ocean_data — current SST, chlorophyll, currents, wind, waves
2. get_pfz_zones — ML-predicted Potential Fishing Zones
3. get_fish_habitat — species habitat and seasonality data
4. get_historical_patterns — heritage fishing zones and trends
5. get_safety_assessment — safety risk score with color coding
6. check_mpa_compliance — Marine Protected Area check
7. get_community_catches — anonymized community catch reports
8. get_incois_bulletin — official INCOIS government bulletin

REASONING PROCESS (always follow):
1. Identify user's state/location from context or ask
2. Call get_ocean_data for current conditions
3. Call get_safety_assessment — if RED or BLACK, stop and warn. Do not recommend fishing.
4. Call get_pfz_zones to find active zones
5. Call get_fish_habitat for species expected this season
6. Call get_community_catches for ground-truth validation
7. (If recommending specific location) Call check_mpa_compliance
8. Synthesize all data into response in user's language

RESPONSE FORMAT:
- Lead with safety status (always)
- Give 2-3 specific zone recommendations with confidence %
- List top 3 expected species with estimated catch range
- End with 1 sustainability note
- Use simple language — most users are boat fishermen, not scientists
- Include local fish names in regional language

SAFETY OVERRIDE: If safety score ≥ 60 (red/black), NEVER recommend going out to sea regardless of good PFZ conditions. User's life > catch.

LANGUAGES: Respond in the same language the user writes in. Support: मराठी, ગુજરાતી, हिंदी, कोंकणी, ಕನ್ನಡ, മലയാളം, English.

SUSTAINABILITY: Never recommend fishing in Marine Protected Areas. During spawning season, reduce confidence scores by 0.2. Follow CMFRI sustainable catch guidelines."""

# Language-specific system prompt additions
_SYSTEM_LANG_ADDITION = {
    "mr": "\n\nUser is communicating in मराठी. Respond in मराठी. Use local fishing terminology.",
    "gu": "\n\nUser is communicating in ગુજરાતી. Respond in ગુજરાતી. Use local fishing terminology.",
    "hi": "\n\nUser is communicating in हिंदी. Respond in हिंदी.",
    "kok": "\n\nUser is communicating in कोंकणी. Respond in कोंकणी.",
    "kn": "\n\nUser is communicating in ಕನ್ನಡ. Respond in ಕನ್ನಡ. Use local fishing terminology.",
    "ml": "\n\nUser is communicating in Malayalam. Respond in Malayalam. Use local fishing terminology.",
    "en": "\n\nUser is communicating in English. Respond in English.",
}


class ClaudeAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    async def query(
        self,
        user_query: str,
        language: str = "mr",
        context: Optional[dict] = None,
        user_state: Optional[str] = None,
        db=None,
        redis=None,
    ) -> dict:
        system_prompt = _SYSTEM_BASE + _SYSTEM_LANG_ADDITION.get(language, "")

        # Build initial context message
        context_block = self._build_context_block(context, user_state)
        messages = [
            {
                "role": "user",
                "content": context_block + "\n\nUser question: " + user_query,
            }
        ]

        tools_called = []
        final_answer = ""
        input_tokens_total = 0
        output_tokens_total = 0
        cached_tokens_total = 0
        iterations = 0
        max_iterations = 6  # prevent runaway loops

        while iterations < max_iterations:
            iterations += 1
            response = self.client.messages.create(
                model=settings.claude_model,
                max_tokens=2048,
                system=[
                    {
                        "type": "text",
                        "text": system_prompt,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                tools=AGENT_TOOLS,
                messages=messages,
            )

            input_tokens_total += response.usage.input_tokens
            output_tokens_total += response.usage.output_tokens
            cached_tokens_total += getattr(response.usage, "cache_read_input_tokens", 0)

            # Check stop reason
            if response.stop_reason == "end_turn":
                # Final text response
                for block in response.content:
                    if hasattr(block, "text"):
                        final_answer = block.text
                break

            if response.stop_reason == "tool_use":
                # Execute all tool calls in this turn
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input
                        logger.info("Agent calling tool", tool=tool_name, state=tool_input.get("state"))

                        result = await execute_tool(tool_name, tool_input, db=db, redis=redis)
                        tools_called.append({"tool": tool_name, "input": tool_input})

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result),
                        })

                # Append assistant turn + tool results to messages
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})
            else:
                # Unexpected stop reason
                break

        logger.info(
            "Agent query complete",
            iterations=iterations,
            tools_called=len(tools_called),
            input_tokens=input_tokens_total,
            cached_tokens=cached_tokens_total,
        )

        return {
            "answer": final_answer,
            "model": response.model,
            "input_tokens": input_tokens_total,
            "output_tokens": output_tokens_total,
            "cached_tokens": cached_tokens_total,
            "tools_used": [t["tool"] for t in tools_called],
            "iterations": iterations,
        }

    def _build_context_block(self, context: Optional[dict], user_state: Optional[str]) -> str:
        if not context and not user_state:
            return ""
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        lines = [f"Current time: {now}"]
        if user_state:
            lines.append(f"User's state: {user_state.title()}")
        if context:
            pfz_count = context.get("nearby_pfz_count", 0)
            if pfz_count:
                lines.append(f"Nearby PFZ zones: {pfz_count}")
            safety = context.get("safety_status")
            if safety:
                lines.append(f"Last safety status: {safety}")
            weather = context.get("weather", {})
            if weather:
                lines.append(
                    f"Local conditions: waves {weather.get('wave_height', '?')}m, "
                    f"wind {weather.get('wind_speed', '?')} km/h, "
                    f"SST {weather.get('sst', '?')}°C"
                )
        return "[Context]\n" + "\n".join(lines) + "\n"


claude_agent = ClaudeAgent()
