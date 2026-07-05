# backend/clustering_agent.py
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.schemas.schema import AgentState, ClusterResult
from app.services.store import STORE
import uuid


def clustering_agent(state: AgentState) -> AgentState:
    issue = state.parsed_issue
    match_key = f"{issue.category}::{issue.location}".lower()

    existing_id = None
    for cid, cluster in STORE.clusters.items():
        if f"{cluster.cluster_name}::{cluster.center_location}".lower() == match_key:
            existing_id = cid
            break

    if existing_id:
        cluster = STORE.clusters[existing_id]
        cluster.cluster_size += 1
        STORE.cluster_submissions[existing_id].append(
            {"submission_id": state.submission_id, "summary": issue.summary})
    else:
        existing_id = f"cluster_{uuid.uuid4().hex[:8]}"
        cluster = ClusterResult(cluster_id=existing_id, cluster_name=issue.category,
                                 cluster_size=1, center_location=issue.location)
        STORE.clusters[existing_id] = cluster
        STORE.cluster_submissions[existing_id] = [
            {"submission_id": state.submission_id, "summary": issue.summary}]

    state.cluster = cluster
    return state


__all__ = ["clustering_agent"]
