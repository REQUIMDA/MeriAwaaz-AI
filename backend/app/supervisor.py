"""
LangGraph supervisor for MeriAwaaz AI.

Each create_react_agent uses MessagesState internally. This module wraps every
agent in a plain Python function that:
  1. Receives AgentState from the outer graph
  2. Formats it into {"messages": [HumanMessage(...)]} for the sub-agent
  3. Parses the agent's final response back into AgentState fields
"""
import json
import logging
import re

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.schemas.models import (
    AgentState,
    ParsedIssue,
    ClusterResult,
    FusedContext,
    Recommendation,
    ScoreBreakdown,
    Explanation,
)
from app.agents import (
    citizen_intelligence_agent,
    demand_intelligence_agent,
    knowledge_fusion_agent,
    policy_recommendation_agent,
    explainability_agent,
    vision_processing,
    speech_processing,
)
from app.services.trace import traced

logger = logging.getLogger("pipeline")

# The government datasets carry need-ratios but no population figures, which
# made population_impact always 0 and produced "population of 0" in evidence.
# Use a ward-level estimate when no real figure is available.
_DEFAULT_WARD_POPULATION = 5000


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _strip_json(text: str) -> dict:
    """Strip markdown code fences and parse JSON. Falls back to extracting
    the outermost {...} block if the model wrapped the JSON in prose."""
    text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


def _as_int(v, default: int = 0) -> int:
    """Best-effort int from LLM/tool output. Tolerates '1,450', '5000', ' 12 ',
    floats, None and junk like 'unknown' (→ default) so numeric coercion of
    model output can never raise inside a node."""
    try:
        return int(float(str(v).replace(",", "").strip()))
    except (TypeError, ValueError):
        return default


def _as_float(v, default: float = 0.0) -> float:
    """Best-effort float with the same tolerance as _as_int."""
    try:
        return float(str(v).replace(",", "").strip())
    except (TypeError, ValueError):
        return default


def _scale_component(value, cap: float) -> float:
    """Normalise an LLM-returned score component.

    The compute_priority_score tool works on a 0-1 scale, but ScoreBreakdown
    fields are on a 0-100 scale with per-field caps (40/30/20/10). If the model
    forgot to multiply by 100, do it here; then clamp so Pydantic never rejects
    the Recommendation (which previously silently dropped it)."""
    v = float(value)
    if 0.0 <= v <= 1.0:
        v *= 100.0
    return min(max(v, 0.0), cap)


def _last_message_content(result: dict) -> str:
    """Extract text from the last message in an agent result."""
    from app.core.llm import content_to_text
    msgs = result.get("messages", [])
    if not msgs:
        return ""
    last = msgs[-1]
    return content_to_text(last.content) if hasattr(last, "content") else str(last)


# Markers that mean "the LLM itself is unreachable" — once one node hits this,
# downstream nodes skip their LLM calls entirely instead of each burning ~35s
# of retries on the same dead endpoint.
_LLM_FAILURE_MARKERS = ("resource_exhausted", "429", "quota",
                        "permission_denied", "api key", "api_key",
                        "not found for api version", "unauthenticated",
                        "503", "unavailable", "high demand")


def _llm_unavailable(state: AgentState) -> bool:
    err = (state.error or "").lower()
    return any(marker in err for marker in _LLM_FAILURE_MARKERS)


# Marker set by citizen_intelligence_node when a submission has no usable text
# (e.g. failed transcription). Downstream nodes must NOT cluster or score it —
# previously it became a ranked "(no usable content)" card on the dashboard.
_NO_CONTENT_MARKER = "(no usable content in submission)"


def _unusable(pi) -> bool:
    return pi is not None and pi.summary == _NO_CONTENT_MARKER


def _match_plan_project(location: str, category: str):
    """Find an existing *planned* project that this citizen demand validates.

    The problem statement asks the system to 'weigh competing proposals against
    real demand' — when demand matches a plan project, we attach to it instead
    of creating a duplicate. Requires a real location to avoid false matches.
    """
    if not location or location.strip().lower() == "unspecified":
        return None
    from app.tools.knowledge_tools import lookup_plan_projects
    try:
        results = lookup_plan_projects.invoke({"location": location, "category": category})
    except Exception:
        return None
    for r in results:
        if r.get("status") == "planned":
            return r
    return None


def _build_fused_context(pi, cluster, location: str, info: dict,
                         llm_data: dict | None = None) -> FusedContext:
    """Combine deterministic tool numbers (authoritative), optional LLM
    narrative extras, plan-project linkage, and cost estimation.

    Numbers policy (adhisha's V1 principle): infrastructure_gap and
    data_confidence come from lookup_infrastructure directly — never from the
    LLM's transcription of it. The LLM contributes population/proposal_context.
    """
    from app.config import CATEGORY_COST_ESTIMATES
    from app.services.need_scoring import apply_complaint_boost
    llm_data = llm_data or {}
    cluster_size = cluster.cluster_size if cluster else 1

    # LLMs return "gap" as a bare number OR occasionally as prose/"unknown".
    # Coerce defensively so a stray non-numeric value can't crash this node
    # (which used to silently discard ALL of the LLM's contribution).
    gap = _as_float(info.get("infrastructure_gap"),
                    _as_float(llm_data.get("infrastructure_gap"), 0.5))
    conf = info.get("data_confidence") or llm_data.get("data_confidence")
    if conf not in ("real_data", "estimated", "synthetic"):
        conf = "estimated"
    # LLM population may arrive as "1,450", "5000", "unknown" or null — parse
    # safely instead of int() which throws on any of the non-plain-int forms.
    population = (_as_int(llm_data.get("population"))
                  or _as_int(info.get("population"))
                  or _DEFAULT_WARD_POPULATION)
    extras = {k: v for k, v in {**info, **llm_data}.items()
              if isinstance(v, (int, float, str))}

    plan = _match_plan_project(location, pi.category)
    if plan:
        cost = plan.get("estimated_cost") or None
        extras["plan_id"] = plan["project_id"]
        extras["plan_title"] = plan["title"]
    else:
        cost = CATEGORY_COST_ESTIMATES.get(pi.category)
        extras["cost_source"] = "category_estimate"

    return FusedContext(
        category=pi.category, location=location,
        demand_count=cluster_size,
        population_affected=population,
        estimated_cost_inr=cost,
        data_confidence=conf,
        # citizen demand lifts severity by up to +0.15 (capped at 10 clustered)
        severity_score=apply_complaint_boost(gap, cluster_size, 10),
        category_specific_data=extras,
        is_existing_plan_project=bool(plan),
    )


def _deterministic_recommendation(state: AgentState, pi, cluster, ctx) -> Recommendation:
    """LLM-free scoring, relative to all competing projects (adhisha's V1
    design): demand/population normalised against the strongest project in the
    store, so rankings differentiate visibly as complaints cluster.

    Project identity rules:
      - demand that validates an existing plan  → the plan's project_id
      - otherwise one project PER CLUSTER (not per submission — that used to
        create N duplicate dashboard cards for N clustered complaints)
    """
    from app.services.store import STORE
    from app.tools.policy_tools import compute_relative_breakdown

    plan_id = ctx.category_specific_data.get("plan_id") if ctx else None
    if plan_id:
        project_id = str(plan_id)
        existing = STORE.get_recommendation(project_id)
        title = existing.title if existing else pi.summary[:80]
    elif cluster:
        project_id = f"proj_{cluster.cluster_id}"
        title = pi.summary[:80]
    else:
        project_id = f"proj_{state.submission_id[:8]}"
        title = pi.summary[:80]

    result = compute_relative_breakdown(
        demand_count=cluster.cluster_size if cluster else 1,
        severity_score=ctx.severity_score if ctx else 0.5,
        population_affected=ctx.population_affected if ctx else 0,
        estimated_cost_inr=ctx.estimated_cost_inr if ctx else None,
        all_contexts=STORE.all_contexts(),
    )
    return Recommendation(
        project_id=project_id,
        title=title,
        priority_score=result["priority_score"],
        breakdown=ScoreBreakdown(**result["breakdown"]),
        is_existing_plan_project=bool(plan_id),
        reason=None,
        explanation=None,
    )


def _deterministic_explanation(rec: Recommendation, cluster, ctx) -> Explanation:
    """LLM-free explanation built from the pure-Python evidence tools."""
    from app.tools.explainability_tools import build_evidence_bullets, compute_confidence_score
    cluster_size = cluster.cluster_size if cluster else 1
    try:
        facility_count = int(float(ctx.category_specific_data.get("facility_count", 0))) if ctx else 0
    except (TypeError, ValueError):
        facility_count = 0
    evidence = build_evidence_bullets.invoke({
        "cluster_size": cluster_size,
        "infrastructure_gap": ctx.severity_score if ctx else 0.5,
        "population": ctx.population_affected if ctx else 0,
        "facility_count": facility_count,
        "category": ctx.category if ctx else "Other",
    })
    # Confidence reflects data provenance (adhisha's V1 idea): real government
    # data earns more trust than estimates or labeled-synthetic priors.
    completeness = {"real_data": 0.9, "estimated": 0.6, "synthetic": 0.4}.get(
        ctx.data_confidence if ctx else "", 0.5)
    confidence = compute_confidence_score.invoke({
        "priority_score": rec.priority_score,
        "cluster_size": cluster_size,
        "data_completeness": completeness,
    })
    return Explanation(
        evidence=evidence,
        summary=(f"{rec.title} scored {rec.priority_score:.0f}/100 based on "
                 f"citizen demand ({cluster_size} submission(s)) and infrastructure data."),
        confidence_score=confidence,
    )


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------

def route_intake(state: AgentState) -> str:
    """Deterministic — input_type is already known, no LLM call needed."""
    return {
        "voice":             "speech_processing_agent",
        "image":             "vision_processing_agent",
        "video":             "vision_processing_agent",
        "dashboard_refresh": "demand_intelligence_agent",
    }.get(state.input_type, "citizen_intelligence_agent")


# ---------------------------------------------------------------------------
# Node wrappers
# Each wrapper translates AgentState → sub-agent input → AgentState updates
# ---------------------------------------------------------------------------

def citizen_intelligence_node(state: AgentState) -> dict:
    """Run citizen_intelligence_agent; parse category/location/summary/language."""
    text = state.raw_text or ""
    # Guard: nothing usable to analyse (e.g. speech transcription failed and
    # produced an empty transcript). Running the LLM on empty input used to
    # hallucinate a junk issue that polluted clusters and the dashboard.
    if not text.strip():
        reason = state.error or "submission contained no usable text"
        logger.warning("[citizen_intelligence_node] empty input — skipping analysis (%s)", reason)
        return {"parsed_issue": ParsedIssue(
            category="Other", location="unspecified",
            summary=_NO_CONTENT_MARKER,
            confidence=0.1, language="en",
        ), "error": f"no usable input: {reason}"}
    if _llm_unavailable(state):
        logger.warning("[citizen_intelligence_node] LLM unavailable — using fallback")
        return {"parsed_issue": ParsedIssue(
            category="Other", location="unspecified", summary=text[:120],
            confidence=0.3, language="en",
        ), "error": state.error}
    try:
        result = citizen_intelligence_agent.invoke({
            "messages": [HumanMessage(content=text)]
        })
        content = _last_message_content(result)
        data = _strip_json(content)
        return {"parsed_issue": ParsedIssue(
            category=data.get("category", "Other"),
            location=data.get("location", "unspecified"),
            summary=data.get("summary", text[:120]),
            confidence=float(data.get("confidence", 0.5)),
            language=data.get("language", "en"),
        )}
    except Exception as exc:
        logger.warning("[citizen_intelligence_node] fallback: %s", exc)
        return {"parsed_issue": ParsedIssue(
            category="Other",
            location="unspecified",
            summary=text[:120],
            confidence=0.3,
            language="en",
        ), "error": f"citizen_intelligence fallback: {exc}"}


def demand_intelligence_node(state: AgentState) -> dict:
    """Run demand_intelligence_agent; parse cluster info."""
    pi = state.parsed_issue
    if pi is None or _unusable(pi):
        return {}
    if _llm_unavailable(state):
        logger.warning("[demand_intelligence_node] LLM unavailable — using fallback")
        return {"cluster": ClusterResult(
            cluster_id=f"cluster_{state.submission_id[:8]}",
            cluster_name=pi.category, cluster_size=1, center_location=pi.location,
        ), "error": state.error}
    prompt = (
        f"Category: {pi.category}\n"
        f"Location: {pi.location}\n"
        f"Summary: {pi.summary}\n\n"
        "Search for similar submissions and cluster them. "
        "Return ONLY the JSON object produced by the cluster_submissions tool, "
        "with exactly these keys: cluster_id, cluster_name, cluster_size, center_location. "
        "Do not alter the tool's values."
    )
    try:
        result = demand_intelligence_agent.invoke({
            "messages": [HumanMessage(content=prompt)]
        })
        content = _last_message_content(result)
        data = _strip_json(content)
        return {"cluster": ClusterResult(
            cluster_id=data.get("cluster_id", f"cluster_{state.submission_id[:8]}"),
            cluster_name=data.get("cluster_name", pi.category),
            cluster_size=int(data.get("cluster_size", 1)),
            center_location=data.get("center_location", pi.location),
        )}
    except Exception as exc:
        logger.warning("[demand_intelligence_node] fallback: %s", exc)
        return {"cluster": ClusterResult(
            cluster_id=f"cluster_{state.submission_id[:8]}",
            cluster_name=pi.category,
            cluster_size=1,
            center_location=pi.location,
        ), "error": f"demand_intelligence fallback: {exc}"}


def knowledge_fusion_node(state: AgentState) -> dict:
    """Run knowledge_fusion_agent; parse infrastructure gap and context."""
    pi = state.parsed_issue
    if pi is None or _unusable(pi):
        return {}
    cluster = state.cluster
    location = cluster.center_location if cluster else pi.location
    # Deterministic numbers first — pure Python + local JSON, no LLM needed.
    # These are authoritative regardless of what the LLM says below.
    try:
        from app.tools.knowledge_tools import lookup_infrastructure
        info = lookup_infrastructure.invoke({"location": location, "category": pi.category})
    except Exception as exc:
        logger.warning("[knowledge_fusion_node] lookup_infrastructure failed: %s", exc)
        info = {}

    if _llm_unavailable(state):
        logger.warning("[knowledge_fusion_node] LLM unavailable — tool data only")
        return {"knowledge_context": _build_fused_context(pi, cluster, location, info),
                "error": state.error}
    prompt = (
        f"Category: {pi.category}\n"
        f"Location: {location}\n\n"
        "Look up infrastructure data and existing development plans. "
        "Return ONLY valid JSON with keys: population, facility_count, nearest_facility_km, "
        "road_quality, infrastructure_gap (0-1, from lookup_infrastructure), "
        "data_confidence (real_data|estimated|synthetic, from lookup_infrastructure), "
        "proposal_context."
    )
    try:
        result = knowledge_fusion_agent.invoke({
            "messages": [HumanMessage(content=prompt)]
        })
        content = _last_message_content(result)
        data = _strip_json(content)
        # Tool numbers are authoritative; LLM contributes population and
        # narrative extras (proposal_context, road_quality, ...)
        ctx = _build_fused_context(pi, cluster, location, info, data)
        return {"knowledge_context": ctx}
    except Exception as exc:
        logger.warning("[knowledge_fusion_node] LLM failed (%s) — tool data only", exc)
        return {"knowledge_context": _build_fused_context(pi, cluster, location, info),
                "error": f"knowledge_fusion fallback: {exc}"}


def policy_recommendation_node(state: AgentState) -> dict:
    """Run policy_recommendation_agent; parse top project recommendation."""
    pi = state.parsed_issue
    cluster = state.cluster
    ctx = state.knowledge_context
    if pi is None:
        return {}
    if _unusable(pi):
        logger.warning("[policy_recommendation_node] skipping — no usable input")
        return {"error": state.error or "no usable input"}

    if _llm_unavailable(state):
        logger.warning("[policy_recommendation_node] LLM unavailable — deterministic scoring")
        rec = _deterministic_recommendation(state, pi, cluster, ctx)
        from app.services.store import STORE
        if ctx:
            STORE.upsert_context(rec.project_id, ctx)
        STORE.upsert_recommendation(rec)
        return {"recommendation": rec, "error": state.error}

    from app.services.store import STORE

    cluster_size = cluster.cluster_size if cluster else 1
    location = (cluster.center_location if cluster else pi.location)
    infra_gap = ctx.severity_score if ctx else 0.5
    pop = ctx.population_affected if ctx else 0

    # Competitive context: show the agent the current leaderboard so its
    # title/reason reference the actual ranking, not a vacuum.
    top = STORE.all_recommendations_sorted()[:5]
    leaderboard = "\n".join(
        f"  - {r.project_id}: {r.title} (score {r.priority_score})"
        for r in top) or "  (none yet)"
    plan_note = ""
    if ctx and ctx.category_specific_data.get("plan_id"):
        plan_note = (f"\nNOTE: this demand VALIDATES the existing plan project "
                     f"{ctx.category_specific_data['plan_id']} "
                     f"({ctx.category_specific_data.get('plan_title', '')}) — "
                     "your reason should say citizens are confirming this planned work.")

    prompt = (
        f"Category: {pi.category}\n"
        f"Location: {location}\n"
        f"Citizen demand (cluster_size): {cluster_size}\n"
        f"Infrastructure gap (0-1): {infra_gap}\n"
        f"Population affected: {pop}\n"
        f"Current top-ranked projects:\n{leaderboard}\n"
        f"{plan_note}\n\n"
        f"Issue summary: {pi.summary}\n\n"
        "Use compute_priority_score (and rank_projects if multiple candidates) to compute scores. "
        "The tool returns values on a 0-1 scale — multiply priority_score and every breakdown "
        "component by 100 before returning. "
        "Return ONLY valid JSON with keys: project_id, "
        "title (an actionable WORKS title naming the SPECIFIC problem and place, "
        "e.g. 'Pothole Repair and Road Resurfacing - Kesarpur Main Road' — "
        "never generic phrases like 'Address Civic Needs'), "
        "priority_score (0-100), breakdown (citizen_demand 0-40, severity 0-30, "
        "population_impact 0-20, cost_feasibility 0-10), "
        "reason (one sentence comparing this project against the current top-ranked ones)."
    )
    try:
        result = policy_recommendation_agent.invoke({
            "messages": [HumanMessage(content=prompt)]
        })
        content = _last_message_content(result)
        data = _strip_json(content)
        # Scores AND project identity are computed deterministically —
        # identity comes from the plan match or the cluster (one project per
        # cluster; per-submission IDs used to create N duplicate cards).
        # The LLM contributes only the human title and the reason.
        base = _deterministic_recommendation(state, pi, cluster, ctx)
        rec = base.model_copy(update={
            # keep the official plan title when demand validates a plan
            "title": base.title if base.is_existing_plan_project
                     else (data.get("title") or base.title),
            "reason": (str(data.get("reason", "")).strip() or None),
        })
        if ctx:
            STORE.upsert_context(rec.project_id, ctx)
        STORE.upsert_recommendation(rec)
        return {"recommendation": rec}
    except Exception as exc:
        logger.warning("[policy_recommendation_node] LLM failed (%s) — deterministic scoring", exc)
        try:
            rec = _deterministic_recommendation(state, pi, cluster, ctx)
            from app.services.store import STORE
            if ctx:
                STORE.upsert_context(rec.project_id, ctx)
            STORE.upsert_recommendation(rec)
            return {"recommendation": rec, "error": f"policy_recommendation fallback: {exc}"}
        except Exception as exc2:
            logger.error("[policy_recommendation_node] deterministic fallback also failed: %s", exc2)
            return {"error": f"policy_recommendation failed: {exc}"}


def explainability_node(state: AgentState) -> dict:
    """Run explainability_agent; add evidence + summary to recommendation."""
    rec = state.recommendation
    cluster = state.cluster
    ctx = state.knowledge_context
    if rec is None:
        return {}

    if _llm_unavailable(state):
        logger.warning("[explainability_node] LLM unavailable — deterministic explanation")
        explanation = _deterministic_explanation(rec, cluster, ctx)
        updated_rec = rec.model_copy(update={"explanation": explanation})
        from app.services.store import STORE
        STORE.upsert_recommendation(updated_rec)
        return {"recommendation": updated_rec, "error": state.error}

    prompt = (
        f"Project: {rec.title}\n"
        f"Priority score: {rec.priority_score}/100\n"
        f"Citizen demand score: {rec.breakdown.citizen_demand}\n"
        f"Infrastructure severity score: {rec.breakdown.severity}\n"
        f"Population impact score: {rec.breakdown.population_impact}\n"
        f"Cost feasibility score: {rec.breakdown.cost_feasibility}\n"
        f"Cluster size: {cluster.cluster_size if cluster else 'unknown'}\n"
        f"Infrastructure gap: {ctx.severity_score if ctx else 'unknown'}\n"
        f"Data confidence: {ctx.data_confidence if ctx else 'unknown'}\n"
        f"{'This project is part of the existing local development plan, now validated by citizen demand.' if rec.is_existing_plan_project else ''}\n\n"
        "When calling compute_confidence_score, pass data_completeness = 0.9 for "
        "real_data, 0.6 for estimated, 0.4 for synthetic. "
        "Generate evidence bullets and a 2-3 sentence explanation readable by an MP. "
        "Return JSON with keys: evidence (list of 2-3 strings), summary (string), confidence_score (0-1)."
    )
    try:
        result = explainability_agent.invoke({
            "messages": [HumanMessage(content=prompt)]
        })
        content = _last_message_content(result)
        data = _strip_json(content)
        explanation = Explanation(
            evidence=data.get("evidence", []),
            summary=data.get("summary", ""),
            confidence_score=float(data.get("confidence_score", 0.7)),
        )
        updated_rec = rec.model_copy(update={"explanation": explanation})
        from app.services.store import STORE
        STORE.upsert_recommendation(updated_rec)
        return {"recommendation": updated_rec}
    except Exception as exc:
        logger.warning("[explainability_node] LLM failed (%s) — deterministic explanation", exc)
        try:
            explanation = _deterministic_explanation(rec, cluster, ctx)
            updated_rec = rec.model_copy(update={"explanation": explanation})
            from app.services.store import STORE
            STORE.upsert_recommendation(updated_rec)
            return {"recommendation": updated_rec, "error": f"explainability fallback: {exc}"}
        except Exception as exc2:
            logger.error("[explainability_node] deterministic fallback also failed: %s", exc2)
            return {"error": f"explainability failed: {exc}"}


# ---------------------------------------------------------------------------
# Graph assembly
# ---------------------------------------------------------------------------

def build_workflow(checkpointer=None):
    graph = StateGraph(AgentState)

    # Plain wrapper functions — no MessagesState mismatch.
    # Each node is wrapped with traced() so every execution is logged to the
    # console and persisted to the agent_log table (see GET /api/trace/{id}).
    graph.add_node("citizen_intelligence_agent",   traced("citizen_intelligence_agent")(citizen_intelligence_node))
    graph.add_node("demand_intelligence_agent",    traced("demand_intelligence_agent")(demand_intelligence_node))
    graph.add_node("knowledge_fusion_agent",       traced("knowledge_fusion_agent")(knowledge_fusion_node))
    graph.add_node("policy_recommendation_agent",  traced("policy_recommendation_agent")(policy_recommendation_node))
    graph.add_node("explainability_agent",         traced("explainability_agent")(explainability_node))

    # Media pre-processors — vision/speech expose .run() functions
    graph.add_node("vision_processing_agent", traced("vision_processing_agent")(vision_processing.run))
    graph.add_node("speech_processing_agent", traced("speech_processing_agent")(speech_processing.run))

    graph.add_conditional_edges(START, route_intake)

    for intake_node in ["speech_processing_agent", "vision_processing_agent"]:
        graph.add_edge(intake_node, "citizen_intelligence_agent")

    graph.add_edge("citizen_intelligence_agent",  "demand_intelligence_agent")
    graph.add_edge("demand_intelligence_agent",   "knowledge_fusion_agent")
    graph.add_edge("knowledge_fusion_agent",      "policy_recommendation_agent")
    graph.add_edge("policy_recommendation_agent", "explainability_agent")
    graph.add_edge("explainability_agent",        END)

    return graph.compile(checkpointer=checkpointer or MemorySaver())
