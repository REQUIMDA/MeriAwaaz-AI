from langchain_core.tools import tool

REFERENCE_COST_INR = 5_000_000  # ₹50L — typical MPLADS-scale project


def compute_relative_breakdown(demand_count: int, severity_score: float,
                               population_affected: int, estimated_cost_inr,
                               all_contexts: list) -> dict:
    """Relative scoring (adhisha's V1 design, hardened). Pure Python — no LLM.

    Demand and population are normalised against the strongest competing
    project instead of fixed caps (cluster_size/50 made one complaint worth
    0.8/40 — invisible on the dashboard). A floor of 5 on the demand
    denominator stops a single lone complaint from maxing out the component.
    Returns {"priority_score": 0-100, "breakdown": {...0-100 scale...}}.
    """
    demands = [c.demand_count for c in all_contexts]
    pops = [c.population_affected for c in all_contexts]
    max_demand = max(demands + [demand_count, 5])
    max_pop = max(pops + [population_affected, 1])

    citizen_demand = 40.0 * min(demand_count / max_demand, 1.0)
    severity = 30.0 * min(max(severity_score, 0.0), 1.0)
    population_impact = 20.0 * min(population_affected / max_pop, 1.0)
    if estimated_cost_inr:
        cost_feasibility = max(0.0, 10.0 * (1.0 - min(1.0, estimated_cost_inr / (2 * REFERENCE_COST_INR))))
    else:
        cost_feasibility = 5.0  # unknown cost = neutral

    breakdown = {
        "citizen_demand": round(citizen_demand, 2),
        "severity": round(severity, 2),
        "population_impact": round(population_impact, 2),
        "cost_feasibility": round(cost_feasibility, 2),
    }
    return {"priority_score": round(sum(breakdown.values()), 2), "breakdown": breakdown}


@tool
def compute_priority_score(
    citizen_demand: float,
    infrastructure_gap: float,
    population_impact: float,
    cost_feasibility: float,
) -> dict:
    """Compute the deterministic priority score for a development project.

    Formula (fixed weights — LLM never changes these):
        score = 0.40 * citizen_demand
              + 0.30 * infrastructure_gap
              + 0.20 * population_impact
              + 0.10 * cost_feasibility

    All inputs must be normalised floats between 0.0 and 1.0.

    Args:
        citizen_demand: proportion of submissions requesting this type of project
        infrastructure_gap: how underserved the area is (from knowledge_fusion)
        population_impact: normalised population of affected area
        cost_feasibility: inverse of estimated cost (higher = cheaper = more feasible)

    Returns:
        dict with keys: priority_score (float), breakdown (dict of weighted components)
    """
    score = (
        0.40 * citizen_demand
        + 0.30 * infrastructure_gap
        + 0.20 * population_impact
        + 0.10 * cost_feasibility
    )
    return {
        "priority_score": round(score, 4),
        "breakdown": {
            "citizen_demand": round(0.40 * citizen_demand, 4),
            "infrastructure_gap": round(0.30 * infrastructure_gap, 4),
            "population_impact": round(0.20 * population_impact, 4),
            "cost_feasibility": round(0.10 * cost_feasibility, 4),
        },
    }


@tool
def rank_projects(projects: list[dict]) -> list[dict]:
    """Sort a list of projects by their priority_score in descending order.

    Args:
        projects: list of dicts, each must have a 'priority_score' key

    Returns:
        same list sorted highest score first
    """
    return sorted(projects, key=lambda p: p.get("priority_score", 0), reverse=True)
