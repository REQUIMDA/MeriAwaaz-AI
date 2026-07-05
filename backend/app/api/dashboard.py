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
    Re-score all existing FusedContext entries.
    Policy Agent integration is a TODO — skeleton is ready.
    """
    contexts = STORE.all_contexts()

    for ctx in contexts:
        # TODO: replace with real Policy Recommendation Agent call
        pass

    return DashboardRefreshResponse(count=len(contexts))
