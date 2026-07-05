from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.schemas.models import ParsedIssue, Recommendation, ScoreBreakdown
from app.services import database
from app.services.store import STORE

router = APIRouter()


# ---------------------------------------------------------------------------
# Response model
# ---------------------------------------------------------------------------

class SubmissionResponse(BaseModel):
    id: str
    created_at: str
    input_type: str
    raw_text: str
    category: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    confidence: Optional[float] = None
    language: Optional[str] = None
    cluster_id: Optional[str] = None
    parsed_issue: Optional[ParsedIssue] = None
    recommendation: Optional[Recommendation] = None


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_parsed_issue(sub: dict) -> Optional[ParsedIssue]:
    try:
        return ParsedIssue(
            category=sub["category"],
            location=sub["location"],
            summary=sub["summary"],
            confidence=sub["confidence"],
            language=sub["language"],
        )
    except Exception:
        return None


def _build_recommendation(cluster_id: str) -> Optional[Recommendation]:
    # Attempt 1: in-memory store
    rec = STORE.get_recommendation(cluster_id)
    if rec is not None:
        return rec.model_copy(update={"explanation": None})

    # Attempt 2: SQLite fallback
    row = database.get_recommendation(cluster_id)
    if row is None:
        return None

    try:
        return Recommendation(
            project_id=row["project_id"],
            title=row["title"],
            priority_score=row["priority_score"],
            breakdown=ScoreBreakdown(
                citizen_demand=row["citizen_demand"],
                severity=row["severity"],
                population_impact=row["population_impact"],
                cost_feasibility=row["cost_feasibility"],
            ),
            is_existing_plan_project=bool(row["is_existing_plan_project"]),
            explanation=None,
        )
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------

@router.get("/api/submissions/{submission_id}", response_model=SubmissionResponse)
def get_submission(submission_id: str) -> SubmissionResponse:
    """
    Return the stored record for a submission, including the parsed issue
    and the associated recommendation. explanation is always null here.
    """
    sub = database.get_submission(submission_id)
    if sub is None:
        raise HTTPException(
            status_code=404,
            detail=f"Submission '{submission_id}' not found.",
        )

    cluster_id = sub.get("cluster_id")
    recommendation = _build_recommendation(cluster_id) if cluster_id else None
    parsed_issue = _build_parsed_issue(sub)

    return SubmissionResponse(
        id=sub["id"],
        created_at=sub["created_at"],
        input_type=sub["input_type"],
        raw_text=sub["raw_text"],
        category=sub.get("category"),
        location=sub.get("location"),
        summary=sub.get("summary"),
        confidence=sub.get("confidence"),
        language=sub.get("language"),
        cluster_id=cluster_id,
        parsed_issue=parsed_issue,
        recommendation=recommendation,
    )
