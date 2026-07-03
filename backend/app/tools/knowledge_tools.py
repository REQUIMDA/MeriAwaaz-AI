from langchain_core.tools import tool


@tool
def lookup_infrastructure(location: str, category: str) -> dict:
    """Look up infrastructure data for a given ward/location and issue category.

    Use this to find out what facilities already exist in the area
    (schools, hospitals, roads, ITI centres, etc.) and the population served.

    Args:
        location: ward name or area (e.g. 'Ward 3', 'Village A')
        category: issue category to focus on (e.g. 'Education', 'Healthcare')

    Returns:
        dict with keys: population, facility_count, nearest_facility_km,
                        road_quality, infrastructure_gap (0.0–1.0)
    """
    # Real implementation will do a dict lookup on datasets/demo/infrastructure.json.
    return {
        "population": 0,
        "facility_count": 0,
        "nearest_facility_km": 0.0,
        "road_quality": "",
        "infrastructure_gap": 0.0,
    }


@tool
def lookup_plan_projects(location: str, category: str) -> list[dict]:
    """Look up existing development plan proposals for a location and category.

    Use this to check what projects are already planned so recommendations
    are grounded in the local development plan.

    Args:
        location: ward name or area
        category: issue category

    Returns:
        list of dicts, each with keys: project_id, title, estimated_cost, status
    """
    # Real implementation will load datasets/demo/projects.json.
    return []
