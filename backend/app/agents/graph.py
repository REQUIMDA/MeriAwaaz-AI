import os
import sys
from pathlib import Path

try:
    from langgraph.graph import StateGraph, END  # type: ignore[import-not-found]
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from langgraph.graph import StateGraph, END  # type: ignore[import-not-found]

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.schemas.schema import AgentState

try:
    from app.agents.intake_agent import intake_agent_stub
except Exception:
    import intake_agent as intake_agent_module
    intake_agent_stub = getattr(
        intake_agent_module,
        "intake_agent_stub",
        getattr(intake_agent_module, "intake_agent", None),
    )
    if intake_agent_stub is None:
        def intake_agent_stub(state):
            return state

from app.agents.clustering_agent import clustering_agent
from app.agents.fusion_agent import fusion_agent
from app.agents.policy_agent import policy_agent
from app.agents.explainability_agent import explainability_agent_stub

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("intake", intake_agent_stub)
    graph.add_node("clustering", clustering_agent)
    graph.add_node("fusion", fusion_agent)
    graph.add_node("policy", policy_agent)
    graph.add_node("explainability", explainability_agent_stub)

    graph.set_entry_point("intake")
    graph.add_edge("intake", "clustering")
    graph.add_edge("clustering", "fusion")
    graph.add_edge("fusion", "policy")
    graph.add_edge("policy", "explainability")
    graph.add_edge("explainability", END)
    return graph.compile()

pipeline = build_graph()
