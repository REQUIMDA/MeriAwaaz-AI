from langchain_core.tools import tool


@tool
def compute_priority_score(
    citizen_demand: float,
    infrastructure_gap: float,
    population_impact: float,
    cost_feasibility: float,
) -> dict:
    """Compute the deterministic priority score for a development project.

    Formula (fixed weights — LLM never changes these):
        score = 40 * citizen_demand
              + 30 * infrastructure_gap
              + 20 * population_impact
              + 10 * cost_feasibility

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
        40 * citizen_demand
        + 30 * infrastructure_gap
        + 20 * population_impact
        + 10 * cost_feasibility
    )
    return {
        "priority_score": round(score, 4),
        "breakdown": {
            "citizen_demand": round(40 * citizen_demand, 4),
            "infrastructure_gap": round(30 * infrastructure_gap, 4),
            "population_impact": round(20 * population_impact, 4),
            "cost_feasibility": round(10 * cost_feasibility, 4),
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
