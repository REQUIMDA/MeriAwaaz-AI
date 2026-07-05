# backend/fusion_agent.py
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.schemas.schema import AgentState, FusedContext
from app.config import CATEGORY_CONFIG
from app.services.need_scoring import load_json, match_by_location, normalize, apply_complaint_boost
from app.config import CONSTITUENCY
from app.services.store import STORE


def get_location_value(cfg: dict) -> str:
    """Village-level configs (if you add one later) would instead read
    from the submission's own location — for now all configured datasets
    are district/state, so they read from the fixed constituency context."""
    return CONSTITUENCY[cfg["location_level"]]


def fusion_agent(state: AgentState) -> AgentState:
    issue = state.parsed_issue
    cluster = state.cluster
    cfg = CATEGORY_CONFIG.get(issue.category)

    category_specific_data = {}
    if not cfg:
        # Roads, Water, Sanitation, Electricity, Vocational — no data sourced yet
        severity = 0.5
        data_confidence = "estimated"
    else:
        records = load_json(cfg["dataset"])
        location_value = get_location_value(cfg)
        match = match_by_location(location_value, records, cfg["location_field"])
        if match:
            values = [r.get(cfg["need_field"], 0) for r in records]
            severity = normalize(match.get(cfg["need_field"], 0), values, cfg["direction"])
            category_specific_data = {cfg["need_field"]: match.get(cfg["need_field"])}
            data_confidence = "real_data"
        else:
            severity = 0.5
            data_confidence = "estimated"

    max_cluster_size = max((c.cluster_size for c in STORE.clusters.values()), default=1)
    severity = apply_complaint_boost(severity, cluster.cluster_size, max_cluster_size)

    context = FusedContext(
        category=issue.category,
        location=issue.location,
        demand_count=cluster.cluster_size,
        population_affected=cluster.cluster_size * 5,   # rough proxy — refine if time allows
        estimated_cost_inr=None,
        data_confidence=data_confidence,
        severity_score=severity,
        category_specific_data=category_specific_data,
        is_existing_plan_project=False,
    )

    STORE.fused_contexts[cluster.cluster_id] = context
    state.knowledge_context = context
    return state


__all__ = ["fusion_agent"]
