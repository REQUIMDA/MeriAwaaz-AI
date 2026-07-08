"""
POST /api/submissions/video
---------------------------
Separate endpoint for video submissions. Accepts a video file, analyses both
its visual footage AND audio track (vision_processing), splits the result into
distinct topic complaints, and runs the pipeline per topic so each updates or
creates its own demand cluster / project.

Supported formats : mp4, mov, avi, mkv, webm
Hard size limit   : 50 MB
"""

import logging
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.schemas.models import AgentState, ParsedIssue, Recommendation
from app.services import database, chroma_client
from app.services.decompose import decompose_text
from app.agents import vision_processing

UPLOADS_DIR = Path(__file__).resolve().parent.parent / "data" / "uploads"

MAX_FILE_BYTES = 50 * 1024 * 1024
SUPPORTED_VIDEO_EXT = {".mp4", ".mov", ".avi", ".mkv", ".webm"}

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


def _run_pipeline_for_issue(sid: str, idx: int, issue_text: str):
    """Run the single-topic pipeline for one decomposed issue."""
    row_id = sid if idx == 0 else f"{sid}#{idx}"
    state = AgentState(submission_id=row_id, input_type="text", raw_text=issue_text)
    try:
        result = _pipeline.invoke(state, config={"configurable": {"thread_id": row_id}})
    except Exception as exc:
        logger.exception("Pipeline crashed for video issue %s", row_id)
        return row_id, None, None, f"pipeline crashed: {exc}"
    pi = result.get("parsed_issue") if isinstance(result, dict) else None
    rec = result.get("recommendation") if isinstance(result, dict) else None
    err = result.get("error") if isinstance(result, dict) else None
    return (row_id,
            pi if isinstance(pi, ParsedIssue) else None,
            rec if isinstance(rec, Recommendation) else None,
            err)


@router.post("/api/submissions/video")
async def create_video_submission(
    channel: str = Form("video"),
    video: UploadFile = File(...),
    text: str = Form(""),
):
    """Accept a citizen video submission and process it (multi-topic aware)."""
    sid = str(uuid.uuid4())

    ext = Path(video.filename or "").suffix.lower()
    if ext not in SUPPORTED_VIDEO_EXT:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported video format '{ext}'. Accepted: {sorted(SUPPORTED_VIDEO_EXT)}",
        )

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    dest = UPLOADS_DIR / f"{sid}{ext}"
    with dest.open("wb") as f:
        shutil.copyfileobj(video.file, f)

    file_size = dest.stat().st_size
    if file_size > MAX_FILE_BYTES:
        dest.unlink(missing_ok=True)
        raise HTTPException(
            status_code=413,
            detail=f"Video exceeds the 50 MB limit ({file_size / 1024 / 1024:.1f} MB).",
        )

    video_url = f"/uploads/{dest.name}"
    saved_path = str(dest)
    pipeline_error: Optional[str] = None

    # ── Phase 1: analyse the video into plain text ──────────────────────────
    base_text = text or ""
    if _PIPELINE_AVAILABLE:
        pre_state = AgentState(submission_id=sid, input_type="video",
                               raw_text=text or "", media_file_path=saved_path)
        try:
            pre = vision_processing.run(pre_state)
            base_text = (pre.get("raw_text") or "").strip()
            pipeline_error = pre.get("error")
        except Exception as exc:
            logger.exception("Video analysis failed for %s", sid)
            pipeline_error = f"video analysis failed: {exc}"

    # ── Phase 2: split into topics and run the pipeline per topic ───────────
    processed: list[tuple] = []
    recommendations: list[Recommendation] = []
    if _PIPELINE_AVAILABLE and base_text.strip():
        for idx, issue_text in enumerate(decompose_text(base_text)):
            row_id, pi, rec, err = _run_pipeline_for_issue(sid, idx, issue_text)
            pipeline_error = pipeline_error or err
            processed.append((row_id, issue_text, pi, rec))
            if rec is not None:
                recommendations.append(rec)

    # ── Persist one row per topic; index each in ChromaDB ───────────────────
    now = datetime.utcnow().isoformat()
    if processed:
        for i, (row_id, issue_text, pi, rec) in enumerate(processed):
            first = (i == 0)
            searchable = (pi.summary if pi else issue_text) or "video submission"
            database.insert_submission({
                "id": row_id, "created_at": now,
                "input_type": "video" if first else "text",
                "raw_text": issue_text,
                "category": pi.category if pi else None,
                "location": pi.location if pi else None,
                "summary": pi.summary if pi else None,
                "confidence": pi.confidence if pi else None,
                "language": pi.language if pi else None,
                "cluster_id": rec.project_id if rec else None,
                "photo_url": None,
                "video_url": video_url if first else None,
                "audio_url": None,
            })
            try:
                chroma_client.add_submission(
                    submission_id=row_id, text=searchable,
                    metadata={"category": pi.category if pi else "Other",
                              "location": pi.location if pi else "unspecified"},
                )
            except Exception as exc:
                logger.exception("ChromaDB indexing failed for %s", row_id)
                try:
                    database.log_agent(row_id, "chroma_indexing", "error", 0, str(exc)[:2000])
                except Exception:
                    pass
    else:
        database.insert_submission({
            "id": sid, "created_at": now, "input_type": "video",
            "raw_text": base_text or text or "", "category": None, "location": None,
            "summary": None, "confidence": None, "language": None, "cluster_id": None,
            "photo_url": None, "video_url": video_url, "audio_url": None,
        })

    primary = recommendations[0] if recommendations else None
    return {
        "status": ("processed" if (_PIPELINE_AVAILABLE and recommendations and not pipeline_error)
                   else ("degraded" if _PIPELINE_AVAILABLE else "stored")),
        "submission_id": sid,
        "video_url": video_url,
        "error": pipeline_error,
        "topics": len(processed),
        "recommendation": primary.model_dump() if primary else None,
        "recommendations": [r.model_dump() for r in recommendations],
    }
