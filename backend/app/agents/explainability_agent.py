# backend/explainability_agent.py
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.schemas.schema import AgentState, Explanation


def explainability_agent_stub(state: AgentState) -> AgentState:
    ctx = state.knowledge_context
    rec = state.recommendation
    b = rec.breakdown
    explanation = Explanation(
        evidence=[
            f"{ctx.demand_count} citizen submission(s) recorded for this issue in {ctx.location}.",
            f"Severity score of {ctx.severity_score:.2f} based on {ctx.data_confidence} data for {ctx.category}.",
            f"Estimated {ctx.population_affected} people affected.",
        ],
        summary=(
            f"This {ctx.category.lower()} issue in {ctx.location} scores {rec.priority_score:.0f}/100, "
            f"driven mainly by {'citizen demand' if b.citizen_demand >= b.severity else 'infrastructure severity'}."
        ),
        confidence_score=0.9 if ctx.data_confidence == "real_data" else 0.6,
    )
    state.recommendation.explanation = explanation
    return state


__all__ = ["explainability_agent_stub"]
