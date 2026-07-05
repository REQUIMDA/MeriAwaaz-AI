import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.store import STORE
from app.agents.policy_agent import policy_agent
from app.agents.explainability_agent import explainability_agent_stub
from app.schemas.schema import AgentState


def refresh_all_recommendations():
    for key, context in STORE.fused_contexts.items():
        fake_state = AgentState(
            submission_id=f"refresh_{key}", input_type="dashboard_refresh",
            cluster=STORE.clusters.get(key), knowledge_context=context,
        )
        result = policy_agent(fake_state)  # uses `key` as fallback project_id when cluster is None
        explainability_agent_stub(result)
    return STORE.all_recommendations_sorted()


__all__ = ["refresh_all_recommendations"]
