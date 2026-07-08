from fastapi import APIRouter
from pydantic import BaseModel

from app.schemas.models import Recommendation
from app.services.store import STORE
from app.services import database

router = APIRouter()


# ---------------------------------------------------------------------------
# Response model
# ---------------------------------------------------------------------------

class RecommendationsResponse(BaseModel):
    items: list[Recommendation]


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------

@router.get("/api/recommendations", response_model=RecommendationsResponse)
def get_recommendations() -> RecommendationsResponse:
    """
    Return all recommendations from the in-memory store, sorted by
    priority_score descending. explanation is always null here.
    """
    resolved = database.resolved_cluster_ids()
    recs = [r for r in STORE.all_recommendations_sorted() if r.project_id not in resolved]
    return RecommendationsResponse(items=recs)
