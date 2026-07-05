import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.schemas.models import AgentState, ParsedIssue, Recommendation, ScoreBreakdown
from app.services import database, chroma_client
from app.services.store import STORE

UPLOADS_DIR = Path(__file__).resolve().parent.parent / "data" / "uploads"

# ---------------------------------------------------------------------------
# Pipeline — defensive import
# ---------------------------------------------------------------------------
try:
    from app.supervisor import build_workflow
    _pipeline = build_workflow()
    _PIPELINE_AVAILABLE = True
except Exception:
    _PIPELINE_AVAILABLE = False

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
    photo_url: Optional[str] = None
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
    rec = STORE.get_recommendation(cluster_id)
    if rec is not None:
        return rec.model_copy(update={"explanation": None})

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
# Routes
# ---------------------------------------------------------------------------

@router.post("/api/submissions")
async def create_submission(
    channel: str = Form("text"),
    text: str = Form(""),
    photo: Optional[UploadFile] = File(None),
):
    """
    Accept a citizen submission (text, voice, or photo), run the pipeline,
    persist to SQLite and ChromaDB, and return the result.

    Send as multipart/form-data:
      - channel: "text" | "voice" | "image"
      - text: the citizen's message (empty for photo-only submissions)
      - photo: image file (optional)
    """
    sid = str(uuid.uuid4())

    # Normalise channel → input_type understood by AgentState
    channel_map = {"text": "text", "voice": "voice", "photo": "image", "image": "image"}
    input_type = channel_map.get(channel, "text")

    # Save uploaded photo to disk
    photo_url: Optional[str] = None
    saved_path: Optional[str] = None
    if photo and photo.filename:
        ext = Path(photo.filename).suffix.lower() or ".jpg"
        filename = f"{sid}{ext}"
        dest = UPLOADS_DIR / filename
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        with dest.open("wb") as f:
            shutil.copyfileobj(photo.file, f)
        photo_url = f"/uploads/{filename}"
        saved_path = str(dest)

    recommendation = None
    parsed_issue = None

    if _PIPELINE_AVAILABLE:
        state = AgentState(
            submission_id=sid,
            input_type=input_type,
            raw_text=text,
            media_file_path=saved_path,
        )
        result = _pipeline.invoke(state, config={"configurable": {"thread_id": sid}})

        if isinstance(result, dict):
            pi = result.get("parsed_issue")
            parsed_issue = pi if isinstance(pi, ParsedIssue) else None
            rec = result.get("recommendation")
            recommendation = rec if isinstance(rec, Recommendation) else None
        else:
            parsed_issue = getattr(result, "parsed_issue", None)
            recommendation = getattr(result, "recommendation", None)

    # Use the text that actually ran through the pipeline (vision agent may have
    # replaced it with a description)
    effective_text = text or (parsed_issue.summary if parsed_issue else "")

    # Persist to SQLite
    database.insert_submission({
        "id": sid,
        "created_at": datetime.utcnow().isoformat(),
        "input_type": input_type,
        "raw_text": effective_text,
        "category": parsed_issue.category if parsed_issue else None,
        "location": parsed_issue.location if parsed_issue else None,
        "summary": parsed_issue.summary if parsed_issue else None,
        "confidence": parsed_issue.confidence if parsed_issue else None,
        "language": parsed_issue.language if parsed_issue else None,
        "cluster_id": recommendation.project_id if recommendation else None,
        "photo_url": photo_url,
    })

    # Add to ChromaDB for future similarity search
    searchable_text = effective_text or "photo submission"
    chroma_client.add_submission(
        submission_id=sid,
        text=searchable_text,
        metadata={
            "category": parsed_issue.category if parsed_issue else "Other",
            "location": parsed_issue.location if parsed_issue else "unspecified",
        },
    )

    return {
        "status": "processed" if _PIPELINE_AVAILABLE else "stored",
        "submission_id": sid,
        "photo_url": photo_url,
        "recommendation": recommendation.model_dump() if recommendation else None,
    }


@router.get("/api/submissions/{submission_id}", response_model=SubmissionResponse)
def get_submission(submission_id: str) -> SubmissionResponse:
    """
    Return the stored record for a submission, including parsed issue,
    recommendation, and photo URL if a photo was submitted.
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
        photo_url=sub.get("photo_url"),
        parsed_issue=parsed_issue,
        recommendation=recommendation,
    )
