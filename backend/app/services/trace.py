"""
Pipeline tracing for MeriAwaaz AI.

Wraps every LangGraph node so each execution is:
  1. logged to the console (logger name "pipeline"), and
  2. persisted to the agent_log SQLite table.

Per-submission traces are queryable via GET /api/trace/{submission_id},
showing which agent ran, how long it took, what it wrote into the state,
and where errors or fallbacks occurred.

Set PIPELINE_TRACE=1 in backend/.env for full untruncated state payloads
in the console (default truncates to 300 chars per field).
"""
import functools
import json
import logging
import os
import time
import traceback

from app.services import database

logger = logging.getLogger("pipeline")

_VERBOSE = os.getenv("PIPELINE_TRACE", "0") == "1"
_MAX_DETAIL = 2000  # max chars persisted per trace event


def _summarize(update: dict) -> str:
    """Render a node's state-update dict as a compact one-line string."""
    parts = []
    for key, value in (update or {}).items():
        if value is None:
            continue
        if hasattr(value, "model_dump"):
            value = value.model_dump()
        try:
            text = json.dumps(value, default=str, ensure_ascii=False)
        except Exception:
            text = str(value)
        if not _VERBOSE and len(text) > 300:
            text = text[:300] + "..."
        parts.append(f"{key}={text}")
    return "; ".join(parts) or "(no state update)"


def _persist(submission_id: str, node_name: str, status: str,
             duration_ms: int, detail: str) -> None:
    """Write a trace event to agent_log. Tracing must never break the pipeline."""
    try:
        database.log_agent(submission_id, node_name, status, duration_ms,
                           (detail or "")[:_MAX_DETAIL])
    except Exception as exc:
        logger.warning("[trace] could not persist event %s/%s: %s",
                       submission_id, node_name, exc)


def traced(node_name: str):
    """Decorator factory: wrap a pipeline node function for tracing.

    Usage: graph.add_node("x", traced("x")(x_node))
    """
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(state):
            sid = getattr(state, "submission_id", "unknown")
            logger.info("[%s] start (submission=%s)", node_name, sid)
            t0 = time.perf_counter()
            try:
                update = fn(state) or {}
            except Exception:
                duration_ms = int((time.perf_counter() - t0) * 1000)
                tb = traceback.format_exc()
                logger.error("[%s] CRASHED after %d ms\n%s", node_name, duration_ms, tb)
                _persist(sid, node_name, "crashed", duration_ms, tb)
                raise

            duration_ms = int((time.perf_counter() - t0) * 1000)
            err = update.get("error") if isinstance(update, dict) else None
            if err:
                status = "error"
            elif isinstance(update, dict) and not update:
                status = "skipped"  # node had nothing to work with (e.g. no recommendation)
            else:
                status = "ok"
            summary = _summarize(update) if isinstance(update, dict) else str(update)

            log = logger.warning if err else logger.info
            log("[%s] %s in %d ms -> %s", node_name, status, duration_ms,
                err or summary)
            _persist(sid, node_name, status, duration_ms,
                     f"{err} | {summary}" if err else summary)
            return update
        return wrapper
    return decorator
