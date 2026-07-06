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


def _deterministic_recommendation(state: AgentState, pi, cluster, ctx) -> Recommendation:
    """LLM-free recommendation using the pure-Python scoring tool, so the
    pipeline still produces a ranked project when Gemini is unavailable."""
    from app.tools.policy_tools import compute_priority_score
    cluster_size = cluster.cluster_size if cluster else 1
    pop = ctx.population_affected if ctx else 0
    infra_gap = ctx.severity_score if ctx else 0.5
    cost = (ctx.estimated_cost_inr if ctx else None) or 0
    result = compute_priority_score.invoke({
        "citizen_demand": min(cluster_size / 50, 1.0),
        "infrastructure_gap": infra_gap,
        "population_impact": min(pop / 15000, 1.0),
        "cost_feasibility": max(0.0, 1.0 - cost / 10_000_000) if cost else 0.5,
    })
    bd = result["breakdown"]
    return Recommendation(
        project_id=f"proj_{state.submission_id[:8]}",
        title=pi.summary[:80],
        priority_score=round(result["priority_score"] * 100, 2),
        breakdown=ScoreBreakdown(
            citizen_demand=round(bd["citizen_demand"] * 100, 2),
            severity=round(bd["infrastructure_gap"] * 100, 2),
            population_impact=round(bd["population_impact"] * 100, 2),
            cost_feasibility=round(bd["cost_feasibility"] * 100, 2),
        ),
        is_existing_plan_project=False,
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
    confidence = compute_confidence_score.invoke({
        "priority_score": rec.priority_score,
        "cluster_size": cluster_size,
        "data_completeness": 0.5,
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
    if pi is None:
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
    if pi is None:
        return {}
    cluster = state.cluster
    location = cluster.center_location if cluster else pi.location
    if _llm_unavailable(state):
        logger.warning("[knowledge_fusion_node] LLM unavailable — using lookup tool directly")
        # lookup_infrastructure is pure Python + local JSON — no LLM needed
        try:
            from app.tools.knowledge_tools import lookup_infrastructure
            info = lookup_infrastructure.invoke({"location": location, "category": pi.category})
        except Exception:
            info = {}
        from app.services.need_scoring import apply_complaint_boost
        return {"knowledge_context": FusedContext(
            category=pi.category, location=location,
            demand_count=cluster.cluster_size if cluster else 1,
            population_affected=int(info.get("population", 0) or 0) or _DEFAULT_WARD_POPULATION,
            data_confidence=info.get("data_confidence", "estimated"),
            severity_score=apply_complaint_boost(
                float(info.get("infrastructure_gap", 0.5)),
                cluster.cluster_size if cluster else 1, 10),
            category_specific_data={k: v for k, v in info.items()
                                     if isinstance(v, (int, float, str))},
            is_existing_plan_project=False,
        ), "error": state.error}
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
        raw_conf = data.get("data_confidence")
        # Citizen demand lifts severity by up to +0.15 (capped at 10 clustered
        # submissions) — repeated complaints about the same issue now move the
        # 30-point severity component, not just the 40-point demand component.
        from app.services.need_scoring import apply_complaint_boost
        ctx = FusedContext(
            category=pi.category,
            location=location,
            demand_count=cluster.cluster_size if cluster else 1,
            population_affected=int(data.get("population", 0) or 0) or _DEFAULT_WARD_POPULATION,
            estimated_cost_inr=None,
            data_confidence=raw_conf if raw_conf in ("real_data", "estimated", "synthetic") else "estimated",
            severity_score=apply_complaint_boost(
                float(data.get("infrastructure_gap", 0.5)),
                cluster.cluster_size if cluster else 1, 10),
            category_specific_data={k: v for k, v in data.items()
                                     if isinstance(v, (int, float, str))},
            is_existing_plan_project=False,
        )
        return {"knowledge_context": ctx}
    except Exception as exc:
        logger.warning("[knowledge_fusion_node] fallback: %s", exc)
        if pi:
            return {"knowledge_context": FusedContext(
                category=pi.category,
                location=location,
                demand_count=1,
                population_affected=0,
                data_confidence="estimated",
                severity_score=0.5,
                is_existing_plan_project=False,
            ), "error": f"knowledge_fusion fallback: {exc}"}
        return {}


def policy_recommendation_node(state: AgentState) -> dict:
    """Run policy_recommendation_agent; parse top project recommendation."""
    pi = state.parsed_issue
    cluster = state.cluster
    ctx = state.knowledge_context
    if pi is None:
        return {}

    if _llm_unavailable(state):
        logger.warning("[policy_recommendation_node] LLM unavailable — deterministic scoring")
        rec = _deterministic_recommendation(state, pi, cluster, ctx)
        from app.services.store import STORE
        if ctx:
            STORE.upsert_context(rec.project_id, ctx)
        STORE.upsert_recommendation(rec)
        return {"recommendation": rec, "error": state.error}

    cluster_size = cluster.cluster_size if cluster else 1
    location = (cluster.center_location if cluster else pi.location)
    infra_gap = ctx.severity_score if ctx else 0.5
    pop = ctx.population_affected if ctx else 0

    prompt = (
        f"Category: {pi.category}\n"
        f"Location: {location}\n"
        f"Citizen demand (cluster_size): {cluster_size}\n"
        f"Infrastructure gap (0-1): {infra_gap}\n"
        f"Population affected: {pop}\n\n"
        "Use compute_priority_score (and rank_projects if multiple candidates) to compute scores. "
        "The tool returns values on a 0-1 scale — multiply priority_score and every breakdown "
        "component by 100 before returning. "
        "Return ONLY valid JSON with keys: project_id, title, priority_score (0-100), "
        "breakdown (citizen_demand 0-40, severity 0-30 = tool's infrastructure_gap x 100, "
        "population_impact 0-20, cost_feasibility 0-10), reason."
    )
    try:
        result = policy_recommendation_agent.invoke({
            "messages": [HumanMessage(content=prompt)]
        })
        content = _last_message_content(result)
        data = _strip_json(content)
        project_id = data.get("project_id", f"proj_{state.submission_id[:8]}")
        # Scores are ALWAYS recomputed deterministically from the pipeline
        # inputs — the LLM contributes only project identity and title.
        # (GPT once reported the formula weight 0.40 as the component score,
        # producing citizen_demand=40 alongside priority_score=5.8.)
        rec = _deterministic_recommendation(state, pi, cluster, ctx).model_copy(update={
            "project_id": project_id,
            "title": data.get("title", pi.summary[:80]),
        })
        # Write to in-memory store
        from app.services.store import STORE
        if ctx:
            STORE.upsert_context(project_id, ctx)
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
        f"Infrastructure gap: {ctx.severity_score if ctx else 'unknown'}\n\n"
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
