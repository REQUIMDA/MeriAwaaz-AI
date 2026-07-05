# backend/policy_agent.py
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.schemas.schema import AgentState, Recommendation, ScoreBreakdown
from app.services.store import STORE


def score_citizen_demand(demand_count, all_contexts):
    counts = [c.demand_count for c in all_contexts]
    return 0.0 if not counts or max(counts) == 0 else 40.0 * (demand_count / max(counts))


def score_severity(severity_score):
    return 30.0 * severity_score


def score_population_impact(population_affected, all_contexts):
    pops = [c.population_affected for c in all_contexts]
    return 0.0 if not pops or max(pops) == 0 else 20.0 * (population_affected / max(pops))


def score_cost_feasibility(estimated_cost_inr):
    if estimated_cost_inr is None:
        return 5.0
    reference_cost = 5_000_000
    return max(0.0, 10.0 * (1 - min(1.0, estimated_cost_inr / (reference_cost * 2))))


def policy_agent(state: AgentState) -> AgentState:
    context = state.knowledge_context
    all_contexts = list(STORE.fused_contexts.values())

    breakdown = ScoreBreakdown(
        citizen_demand=round(score_citizen_demand(context.demand_count, all_contexts), 1),
        severity=round(score_severity(context.severity_score), 1),
        population_impact=round(score_population_impact(context.population_affected, all_contexts), 1),
        cost_feasibility=round(score_cost_feasibility(context.estimated_cost_inr), 1),
    )
    priority_score = round(breakdown.citizen_demand + breakdown.severity +
                            breakdown.population_impact + breakdown.cost_feasibility, 1)

    project_id = state.cluster.cluster_id if state.cluster else f"plan_{state.submission_id}"
    recommendation = Recommendation(
        project_id=project_id,
        title=f"{context.category} — {context.location}",
        priority_score=priority_score,
        breakdown=breakdown,
        is_existing_plan_project=context.is_existing_plan_project,
        explanation=None,
    )
    STORE.recommendations[project_id] = recommendation
    state.recommendation = recommendation
    return state


__all__ = ["policy_agent"]
