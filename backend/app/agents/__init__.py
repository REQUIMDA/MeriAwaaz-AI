"""
Agent package exports.

IMPORTANT: supervisor.py does `from app.agents import citizen_intelligence_agent`
and then calls `.invoke()` on it. Without these re-exports, Python resolves that
name to the MODULE (which has no .invoke), so every agent silently fell back.
These imports rebind each package attribute to the create_react_agent object.
"""
from app.agents.citizen_intelligence_agent import citizen_intelligence_agent
from app.agents.demand_intelligence_agent import demand_intelligence_agent
from app.agents.knowledge_fusion_agent import knowledge_fusion_agent
from app.agents.policy_recommendation_agent import policy_recommendation_agent
from app.agents.explainability_agent import explainability_agent

# vision/speech are used as modules (they expose .run functions)
from app.agents import vision_processing, speech_processing

__all__ = [
    "citizen_intelligence_agent",
    "demand_intelligence_agent",
    "knowledge_fusion_agent",
    "policy_recommendation_agent",
    "explainability_agent",
    "vision_processing",
    "speech_processing",
]
