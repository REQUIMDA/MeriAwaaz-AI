from datetime import datetime
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.schemas.dashboard import DashboardData, HeatmapPoint, ProjectCard
from app.services import database
from app.services.store import STORE

router = APIRouter()


# ---------------------------------------------------------------------------
# Response model (dashboard-refresh only)
# ---------------------------------------------------------------------------

class DashboardRefreshResponse(BaseModel):
    count: int


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/api/dashboard", response_model=DashboardData)
def get_dashboard() -> DashboardData:
    """
    Return the full dashboard payload: ranked projects, heatmap, and stats.
    explanation is never included here.
    """
    recs = STORE.all_recommendations_sorted()

    projects: list[ProjectCard] = []
    for rec in recs:
        ctx = STORE.get_context(rec.project_id)
        category: str = ctx.category if ctx is not None else "Other"
        projects.append(ProjectCard(
            id=rec.project_id,
            title=rec.title,
            category=category,
            priority_score=rec.priority_score,
            breakdown=rec.breakdown,
            is_existing_plan_project=rec.is_existing_plan_project,
        ))

    # TODO: replace with real heatmap when ward coordinates are available
    heatmap: list[HeatmapPoint] = []

    total_submissions: int = database.count_all_submissions()

    last_updated_raw: Optional[str] = database.get_last_updated()
    last_updated: str = last_updated_raw if last_updated_raw else datetime.utcnow().isoformat()

    return DashboardData(
        projects=projects,
        heatmap=heatmap,
        total_submissions=total_submissions,
        last_updated=last_updated,
    )


@router.post("/api/dashboard-refresh", response_model=DashboardRefreshResponse)
def dashboard_refresh() -> DashboardRefreshResponse:
    """
    Deterministically re-score every stored FusedContext using the same
    weighted formula as compute_priority_score (no LLM call needed).
    """
    from app.schemas.models import ScoreBreakdown
    from app.tools.policy_tools import compute_priority_score

    count = 0
    for project_id, ctx in STORE._contexts.items():
        rec = STORE.get_recommendation(project_id)
        if rec is None:
            continue

        cost = ctx.estimated_cost_inr or 0
        result = compute_priority_score.invoke({
            "citizen_demand": min(ctx.demand_count / 50, 1.0),
            "infrastructure_gap": ctx.severity_score,
            "population_impact": min(ctx.population_affected / 15000, 1.0),
            # unknown cost = neutral 0.5, matching the pipeline's scorer —
            # previously cost=0 scored a perfect 1.0 and inflated refreshed scores
            "cost_feasibility": max(0.0, 1.0 - cost / 10_000_000) if cost else 0.5,
        })
        bd = result["breakdown"]

        updated = rec.model_copy(update={
            "priority_score": round(result["priority_score"] * 100, 2),
            "breakdown": ScoreBreakdown(
                citizen_demand=round(bd["citizen_demand"] * 100, 2),
                severity=round(bd["infrastructure_gap"] * 100, 2),
                population_impact=round(bd["population_impact"] * 100, 2),
                cost_feasibility=round(bd["cost_feasibility"] * 100, 2),
            ),
        })
        STORE.upsert_recommendation(updated)
        count += 1

    return DashboardRefreshResponse(count=count)
