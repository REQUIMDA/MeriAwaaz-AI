"""
Pipeline observability endpoints.

GET /api/trace/{submission_id} — step-by-step trace of one submission's run
    through the agent pipeline: which node ran, status (ok | error | crashed),
    duration, and what it wrote into the state (or the error/traceback).

GET /api/trace — the most recent trace events across all submissions,
    useful for spotting where the pipeline is failing without knowing an id.
"""
from fastapi import APIRouter, HTTPException, Query

from app.services import database

router = APIRouter()


@router.get("/api/trace/{submission_id}")
def get_trace(submission_id: str):
    events = database.get_agent_logs(submission_id)
    if not events:
        raise HTTPException(
            status_code=404,
            detail=f"No trace events for submission '{submission_id}'.",
        )
    return {
        "submission_id": submission_id,
        "total_duration_ms": sum(e.get("duration_ms") or 0 for e in events),
        "has_errors": any(e["status"] != "ok" for e in events),
        "events": events,
    }


@router.get("/api/trace")
def get_recent_traces(limit: int = Query(default=50, ge=1, le=500)):
    return {"events": database.get_recent_agent_logs(limit)}
