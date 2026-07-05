from fastapi import APIRouter
from pydantic import BaseModel

from app.schemas.models import Recommendation
from app.services.store import STORE

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
    recs = STORE.all_recommendations_sorted()
    return RecommendationsResponse(items=recs)
