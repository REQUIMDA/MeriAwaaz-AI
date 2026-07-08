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
    resolved = database.resolved_cluster_ids()
    recs = [r for r in STORE.all_recommendations_sorted() if r.project_id not in resolved]

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
    Re-score every stored FusedContext with compute_relative_breakdown — the
    SAME scorer the pipeline uses, so refreshed scores never drift from
    pipeline scores (they previously used different normalisations).
    """
    from app.schemas.models import ScoreBreakdown
    from app.tools.policy_tools import compute_relative_breakdown

    count = 0
    all_contexts = STORE.all_contexts()
    for project_id, ctx in STORE._contexts.items():
        rec = STORE.get_recommendation(project_id)
        if rec is None:
            continue

        result = compute_relative_breakdown(
            demand_count=ctx.demand_count,
            severity_score=ctx.severity_score,
            population_affected=ctx.population_affected,
            estimated_cost_inr=ctx.estimated_cost_inr,
            all_contexts=all_contexts,
        )
        updated = rec.model_copy(update={
            "priority_score": result["priority_score"],
            "breakdown": ScoreBreakdown(**result["breakdown"]),
        })
        STORE.upsert_recommendation(updated)
        count += 1

    return DashboardRefreshResponse(count=count)
