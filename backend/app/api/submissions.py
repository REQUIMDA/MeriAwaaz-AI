import logging
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
from app.services.decompose import decompose_text
from app.agents import speech_processing, vision_processing

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
logger = logging.getLogger("pipeline")


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
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
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


def _preprocess_media(input_type: str, sid: str, text: str,
                      saved_path: Optional[str]) -> tuple[str, Optional[str], Optional[str]]:
    """Turn a voice/image submission into plain text BEFORE decomposition.

    Runs the speech/vision node functions directly (they are plain functions),
    so we get the transcript / image analysis without running the rest of the
    pipeline. Returns (base_text, audio_url, error).
    """
    pre_state = AgentState(submission_id=sid, input_type=input_type,
                           raw_text=text or "", media_file_path=saved_path)
    try:
        pre = (speech_processing.run(pre_state) if input_type == "voice"
               else vision_processing.run(pre_state))
    except Exception as exc:
        logger.exception("Media preprocessing failed for %s", sid)
        return (text or ""), None, f"media preprocessing failed: {exc}"
    return (pre.get("raw_text") or "").strip(), pre.get("audio_url"), pre.get("error")


def _run_pipeline_for_issue(sid: str, idx: int, issue_text: str):
    """Run the (single-topic) pipeline for one decomposed issue.

    Returns (row_id, parsed_issue, recommendation, error).
    """
    row_id = sid if idx == 0 else f"{sid}#{idx}"
    state = AgentState(submission_id=row_id, input_type="text", raw_text=issue_text)
    try:
        result = _pipeline.invoke(state, config={"configurable": {"thread_id": row_id}})
    except Exception as exc:
        logger.exception("Pipeline crashed for issue %s", row_id)
        return row_id, None, None, f"pipeline crashed: {exc}"

    pi = result.get("parsed_issue") if isinstance(result, dict) else None
    rec = result.get("recommendation") if isinstance(result, dict) else None
    err = result.get("error") if isinstance(result, dict) else None
    return (row_id,
            pi if isinstance(pi, ParsedIssue) else None,
            rec if isinstance(rec, Recommendation) else None,
            err)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

def _as_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


@router.post("/api/submissions")
async def create_submission(
    channel: str = Form("text"),
    text: str = Form(""),
    lat: Optional[str] = Form(None),
    lng: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None),
):
    """
    Accept a citizen submission (text, voice, or photo).

    A submission that raises MULTIPLE problems (e.g. "potholes AND a clinic
    medicine shortage") is split into one complaint per problem; each is run
    through the pipeline and updates or creates its OWN demand cluster /
    project. All resulting recommendations are returned.
    """
    sid = str(uuid.uuid4())

    channel_map = {"text": "text", "voice": "voice", "photo": "image", "image": "image"}
    input_type = channel_map.get(channel, "text")

    # Infer type from what was actually attached (users often leave channel=text)
    if audio and audio.filename and input_type != "voice":
        input_type = "voice"
    elif photo and photo.filename and input_type == "text":
        input_type = "image"

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    # Save uploaded photo
    photo_url: Optional[str] = None
    saved_path: Optional[str] = None
    if photo and photo.filename:
        ext = Path(photo.filename).suffix.lower() or ".jpg"
        dest = UPLOADS_DIR / f"{sid}{ext}"
        with dest.open("wb") as f:
            shutil.copyfileobj(photo.file, f)
        photo_url = f"/uploads/{dest.name}"
        saved_path = str(dest)

    # Save uploaded audio
    audio_url: Optional[str] = None
    if audio and audio.filename and input_type == "voice":
        ext = Path(audio.filename).suffix.lower() or ".mp3"
        dest = UPLOADS_DIR / f"{sid}_audio{ext}"
        with dest.open("wb") as f:
            shutil.copyfileobj(audio.file, f)
        audio_url = f"/uploads/{dest.name}"
        saved_path = str(dest)

    pipeline_error: Optional[str] = None

    # ── Phase 1: obtain plain text (transcribe / describe media) ────────────
    base_text = text or ""
    if _PIPELINE_AVAILABLE and input_type in ("voice", "image"):
        base_text, pre_audio_url, pre_err = _preprocess_media(input_type, sid, text, saved_path)
        audio_url = audio_url or pre_audio_url
        pipeline_error = pipeline_error or pre_err

    # ── Phase 2: split into topics, run the pipeline per topic ──────────────
    processed: list[tuple] = []          # (row_id, issue_text, parsed_issue, recommendation)
    recommendations: list[Recommendation] = []

    if _PIPELINE_AVAILABLE and base_text.strip():
        for idx, issue_text in enumerate(decompose_text(base_text)):
            row_id, pi, rec, err = _run_pipeline_for_issue(sid, idx, issue_text)
            pipeline_error = pipeline_error or err
            processed.append((row_id, issue_text, pi, rec))
            if rec is not None:
                recommendations.append(rec)

    # ── Persist: one submissions row per topic; index each in ChromaDB ──────
    now = datetime.utcnow().isoformat()
    lat_val = _as_float(lat)
    lng_val = _as_float(lng)
    if processed:
        for i, (row_id, issue_text, pi, rec) in enumerate(processed):
            first = (i == 0)
            searchable = (pi.summary if pi else issue_text) or "submission"
            database.insert_submission({
                "id": row_id,
                "created_at": now,
                "input_type": input_type if first else "text",
                "raw_text": issue_text,
                "category": pi.category if pi else None,
                "location": pi.location if pi else None,
                "summary": pi.summary if pi else None,
                "confidence": pi.confidence if pi else None,
                "language": pi.language if pi else None,
                "cluster_id": rec.project_id if rec else None,
                "photo_url": photo_url if first else None,
                "video_url": None,
                "audio_url": audio_url if first else None,
                "lat": lat_val,
                "lng": lng_val,
            })
            # Index each topic separately so future submissions cluster per-topic.
            try:
                chroma_client.add_submission(
                    submission_id=row_id,
                    text=searchable,
                    metadata={
                        "category": pi.category if pi else "Other",
                        "location": pi.location if pi else "unspecified",
                    },
                )
            except Exception as exc:
                logger.exception("ChromaDB indexing failed for %s", row_id)
                try:
                    database.log_agent(row_id, "chroma_indexing", "error", 0, str(exc)[:2000])
                except Exception:
                    pass
    else:
        # Nothing ran (no usable text or pipeline unavailable) — still record it.
        database.insert_submission({
            "id": sid, "created_at": now, "input_type": input_type,
            "raw_text": base_text or text or "", "category": None, "location": None,
            "summary": None, "confidence": None, "language": None, "cluster_id": None,
            "photo_url": photo_url, "video_url": None, "audio_url": audio_url,
            "lat": lat_val, "lng": lng_val,
        })

    primary = recommendations[0] if recommendations else None
    return {
        "status": ("processed" if (_PIPELINE_AVAILABLE and recommendations and not pipeline_error)
                   else ("degraded" if _PIPELINE_AVAILABLE else "stored")),
        "submission_id": sid,
        "photo_url": photo_url,
        "audio_url": audio_url,
        "error": pipeline_error,
        "topics": len(processed),
        "recommendation": primary.model_dump() if primary else None,
        "recommendations": [r.model_dump() for r in recommendations],
    }


@router.get("/api/submissions")
def list_submissions(limit: int = 100, offset: int = 0):
    """Recent citizen submissions (newest first) for the MP 'Citizen Issues' view.

    Each row is enriched with the priority_score of the project/cluster it fed
    (looked up from STORE), so the frontend can show a real priority band.
    """
    rows = database.list_submissions(limit=limit, offset=offset)
    items = []
    for r in rows:
        score = None
        cid = r.get("cluster_id")
        if cid:
            rec = STORE.get_recommendation(cid)
            if rec is None:
                dbrec = database.get_recommendation(cid)
                score = dbrec["priority_score"] if dbrec else None
            else:
                score = rec.priority_score
        items.append({
            "id": r["id"],
            "created_at": r["created_at"],
            "input_type": r["input_type"],
            "category": r.get("category"),
            "location": r.get("location"),
            "summary": r.get("summary"),
            "raw_text": r.get("raw_text"),
            "cluster_id": cid,
            "priority_score": score,
            "photo_url": r.get("photo_url"),
            "audio_url": r.get("audio_url"),
            "video_url": r.get("video_url"),
            "lat": r.get("lat"),
            "lng": r.get("lng"),
            "resolved": bool(r.get("resolved")),
        })
    return {"items": items, "total": database.count_all_submissions()}


class ResolveRequest(BaseModel):
    ids: list[str]


@router.post("/api/submissions/resolve")
def resolve_submissions(req: ResolveRequest):
    """Mark submissions resolved. When every submission feeding a project is
    resolved, that project/cluster drops out of the dashboard, recommendations
    and heatmap automatically."""
    n = database.mark_submissions_resolved(req.ids)
    return {"resolved": n}


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
        video_url=sub.get("video_url"),
        audio_url=sub.get("audio_url"),
        parsed_issue=parsed_issue,
        recommendation=recommendation,
    )
