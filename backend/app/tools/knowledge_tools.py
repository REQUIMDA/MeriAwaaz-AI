from langchain_core.tools import tool

from app.config import CATEGORY_CONFIG, CONSTITUENCY
from app.services import need_scoring


@tool
def lookup_infrastructure(location: str, category: str) -> dict:
    """Look up infrastructure data for a given category using government datasets.

    Matches the constituency's state/district against Adhisha's preprocessed
    JSON files to produce a normalised infrastructure_gap score (0.0 = good,
    1.0 = severe need).

    Args:
        location: ward or village name from the citizen submission (used for
                  context only; actual lookup uses constituency state/district)
        category: issue category, e.g. 'Education', 'Healthcare'

    Returns:
        dict with keys: population, facility_count, nearest_facility_km,
                        road_quality, infrastructure_gap (0.0–1.0),
                        data_confidence ('real_data' | 'estimated')
    """
    config = CATEGORY_CONFIG.get(category)

    if config is None:
        # No public dataset for Roads / Water / Sanitation / Electricity /
        # Vocational yet — use clearly-labelled synthetic priors instead of a
        # flat 0.5, reported with data_confidence='synthetic'.
        try:
            priors = need_scoring.load_json("data/synthetic_category_priors.json")
            prior = priors.get(category, {})
        except Exception:
            prior = {}
        return {
            "population": 0,
            "facility_count": int(prior.get("facility_count", 0)),
            "nearest_facility_km": 0.0,
            "road_quality": "unknown",
            "infrastructure_gap": float(prior.get("infrastructure_gap", 0.5)),
            "data_confidence": "synthetic",
        }

    records = need_scoring.load_json(config["dataset"])

    # Drop city/aggregate rows from the normalisation pool where configured
    # (e.g. Mumbai's teledensity of 210 is not a state and skewed the scale)
    exclude = {v.strip().lower() for v in config.get("exclude_locations", [])}
    if exclude:
        records = [r for r in records
                   if str(r.get(config["location_field"], "")).strip().lower() not in exclude]

    # Dataset is at state level or district level — use constituency defaults
    if config["location_level"] == "state":
        lookup_value = CONSTITUENCY["state"]
    else:
        lookup_value = CONSTITUENCY["district"]

    record = need_scoring.match_by_location(
        lookup_value, records, config["location_field"]
    )

    if record is None:
        return {
            "population": 0,
            "facility_count": 0,
            "nearest_facility_km": 0.0,
            "road_quality": "unknown",
            "infrastructure_gap": 0.5,
            "data_confidence": "estimated",
        }

    # Normalise the need field relative to all records in the dataset
    all_values = [r.get(config["need_field"]) for r in records]
    raw_value = float(record.get(config["need_field"]) or 0.0)
    gap = need_scoring.normalize(raw_value, all_values, config["direction"])

    # Healthcare: medicine_shortage_ratio alone is zero for 77% of districts.
    # Blend it with OPD utilisation pressure (patients per dispensary) — a real
    # signal the dataset already carries (Nagpur: 656 OPD/day per 1 dispensary).
    if category == "Healthcare" and any((r.get("total_opd") or 0) for r in records):
        pressures = [
            (r.get("total_opd") or 0) / max(r.get("dispensary_count") or 1, 1)
            for r in records
        ]
        own_pressure = ((record.get("total_opd") or 0)
                        / max(record.get("dispensary_count") or 1, 1))
        opd_gap = need_scoring.normalize(own_pressure, pressures, "higher_is_more_need")
        gap = 0.5 * gap + 0.5 * opd_gap

    # Pull a facility count if the record has one
    facility_count = int(
        record.get("dispensary_count")
        or record.get("total_schools")
        or 0
    )

    return {
        "population": 0,              # not present in current datasets
        "facility_count": facility_count,
        "nearest_facility_km": 0.0,   # not present in current datasets
        "road_quality": "unknown",
        "infrastructure_gap": round(gap, 4),
        "data_confidence": "real_data",
    }


@tool
def lookup_plan_projects(location: str, category: str) -> list[dict]:
    """Look up existing development plan proposals for a location and category.

    Reads the in-memory Store (loaded from local_plans.json at startup) to find
    projects that match the given category and are relevant to the location.

    Args:
        location: ward or village name from the citizen submission
        category: issue category, e.g. 'Education', 'Healthcare'

    Returns:
        list of dicts, each with keys: project_id, title, estimated_cost,
        status, priority_score
    """
    from app.services.store import STORE

    results = []
    location_lower = location.strip().lower()

    for project_id, ctx in STORE._contexts.items():
        if ctx.category != category:
            continue

        # Match if location is unspecified (return all in category) or overlaps
        ctx_loc = ctx.location.strip().lower()
        location_matches = (
            location_lower == "unspecified"
            or location_lower in ctx_loc
            or ctx_loc in location_lower
        )
        if not location_matches:
            continue

        rec = STORE.get_recommendation(project_id)
        results.append({
            "project_id": project_id,
            "title": ctx.category_specific_data.get("title", project_id),
            "estimated_cost": ctx.estimated_cost_inr or 0,
            "status": "planned" if ctx.is_existing_plan_project else "proposed",
            "priority_score": rec.priority_score if rec else 0.0,
        })

    return results
