"""
POST /api/submissions/video
---------------------------
Separate endpoint for video submissions.
Accepts a video file upload, saves it to disk, runs the full 5-agent
pipeline (vision_processing handles both visual + audio analysis), and
returns the result including a video_url the frontend can display.

Supported formats : mp4, mov, avi, mkv, webm
Hard size limit   : 50 MB (enforced again here before hitting the agent)
"""

import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.schemas.models import AgentState, ParsedIssue, Recommendation
from app.services import database, chroma_client
from app.services.store import STORE

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


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------

@router.post("/api/submissions/video")
async def create_video_submission(
    channel: str = Form("video"),
    video: UploadFile = File(...),
):
    """
    Accept a citizen video submission.

    Send as multipart/form-data:
      - channel : "video"  (fixed)
      - video   : the video file (required)

    The vision_processing agent analyzes both the visual footage AND the
    audio track and writes a structured complaint into raw_text, which
    then flows through all 5 agents as normal.
    """
    sid = str(uuid.uuid4())

    # Validate extension
    ext = Path(video.filename or "").suffix.lower()
    if ext not in SUPPORTED_VIDEO_EXT:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported video format '{ext}'. Accepted: {sorted(SUPPORTED_VIDEO_EXT)}",
        )

    # Save to disk first so we can check the size
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{sid}{ext}"
    dest = UPLOADS_DIR / filename

    with dest.open("wb") as f:
        shutil.copyfileobj(video.file, f)

    # Hard-reject oversized files — capture size before deleting
    file_size = dest.stat().st_size
    if file_size > MAX_FILE_BYTES:
        dest.unlink(missing_ok=True)
        raise HTTPException(
            status_code=413,
            detail=f"Video exceeds the 50 MB limit ({file_size / 1024 / 1024:.1f} MB).",
        )

    video_url = f"/uploads/{filename}"
    saved_path = str(dest)

    recommendation: Optional[Recommendation] = None
    parsed_issue: Optional[ParsedIssue] = None

    if _PIPELINE_AVAILABLE:
        state = AgentState(
            submission_id=sid,
            input_type="video",
            raw_text="",                  # vision_processing fills this in
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

    effective_text = parsed_issue.summary if parsed_issue else "video submission"

    # Persist to SQLite
    database.insert_submission({
        "id": sid,
        "created_at": datetime.utcnow().isoformat(),
        "input_type": "video",
        "raw_text": effective_text,
        "category": parsed_issue.category if parsed_issue else None,
        "location": parsed_issue.location if parsed_issue else None,
        "summary": parsed_issue.summary if parsed_issue else None,
        "confidence": parsed_issue.confidence if parsed_issue else None,
        "language": parsed_issue.language if parsed_issue else None,
        "cluster_id": recommendation.project_id if recommendation else None,
        "photo_url": None,
        "video_url": video_url,
        "audio_url": None,
    })

    # Index in ChromaDB
    chroma_client.add_submission(
        submission_id=sid,
        text=effective_text,
        metadata={
            "category": parsed_issue.category if parsed_issue else "Other",
            "location": parsed_issue.location if parsed_issue else "unspecified",
        },
    )

    return {
        "status": "processed" if _PIPELINE_AVAILABLE else "stored",
        "submission_id": sid,
        "video_url": video_url,
        "recommendation": recommendation.model_dump() if recommendation else None,
    }
