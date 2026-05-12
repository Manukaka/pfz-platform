"""
SAMUDRA AI Specialists Module
विशेषज्ञ प्रणाली - प्रजाति-केंद्रित इंजन

Specialized engines for high-value fish species
Extends core PFZ detection with species-specific intelligence

Currently includes:
- GHOL Engine: Premium fish targeting, acoustic detection, spawning prediction
- Behavioral Modeling: Feeding, migration, social patterns

Future additions:
- SURMAI (King Mackerel) engine
- RAWAS (Indian Salmon) engine
- Tuna school detection
"""

from .ghol_engine import GholEngine, analyze_ghol_potential, plan_ghol_trip
from .ghol_behavior import GholBehavior

__all__ = [
    "GholEngine",
    "GholBehavior",
    "analyze_ghol_potential",
    "plan_ghol_trip",
]
