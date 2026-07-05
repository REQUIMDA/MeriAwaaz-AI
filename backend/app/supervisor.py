from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.schemas.models import AgentState
from app.agents import (
    citizen_intelligence_agent,
    demand_intelligence_agent,
    knowledge_fusion_agent,
    policy_recommendation_agent,
    explainability_agent,
    vision_processing,
    speech_processing,
)


def route_intake(state: AgentState) -> str:
    """Deterministic — input_type is already known, no LLM call needed."""
    return {
        "voice": "speech_processing_agent",
        "image": "vision_processing_agent",
        "dashboard_refresh": "demand_intelligence_agent",
    }.get(state.input_type, "citizen_intelligence_agent")  # default: text


def build_workflow(checkpointer=None):
    graph = StateGraph(AgentState)

    graph.add_node("citizen_intelligence_agent", citizen_intelligence_agent.run)
    graph.add_node("demand_intelligence_agent", demand_intelligence_agent.run)
    graph.add_node("knowledge_fusion_agent", knowledge_fusion_agent.run)
    graph.add_node("policy_recommendation_agent", policy_recommendation_agent.run)
    graph.add_node("explainability_agent", explainability_agent.run)
    graph.add_node("vision_processing_agent", vision_processing.run)
    graph.add_node("speech_processing_agent", speech_processing.run)

    graph.add_conditional_edges(START, route_intake)
    for intake_node in ["speech_processing_agent", "vision_processing_agent"]:
        graph.add_edge(intake_node, "citizen_intelligence_agent")
    graph.add_edge("citizen_intelligence_agent", "demand_intelligence_agent")
    graph.add_edge("demand_intelligence_agent", "knowledge_fusion_agent")
    graph.add_edge("knowledge_fusion_agent", "policy_recommendation_agent")
    graph.add_edge("policy_recommendation_agent", "explainability_agent")
    graph.add_edge("explainability_agent", END)

    return graph.compile(checkpointer=checkpointer or MemorySaver())
