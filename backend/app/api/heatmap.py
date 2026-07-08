"""
GET /api/heatmap
----------------
Constituency heatmap data for the MP Portal map view.

Every town/village is returned as ONE entry whose ``projects`` list holds all
of that town's recommendations — across every category (Healthcare, Roads,
Water, …). The frontend renders one marker per town and lets the MP page
through the clustered projects behind it.

Data is read live from the in-memory STORE (the same source the dashboard
uses), so the map reflects new submissions as they are processed. Coordinates
come from ``data/village_coordinates.json`` (a small gazetteer); towns absent
from it are returned with ``lat``/``lng`` = null and the frontend geocodes them
via the free OSM Nominatim service as a fallback.

Shape (the contract the frontend expects):
    {
      "towns": [
        {
          "name": "Kesarpur", "state": "Maharashtra",
          "lat": 21.232, "lng": 79.001,
          "projects": [
            {
              "id": "plan_002",
              "title": "Upgrade of Primary Health Sub-Centre - Kesarpur",
              "category": "Healthcare",
              "description": "...",          # optional
              "explanation": "...",          # optional (from Explainability agent)
              "priority_score": 41.1,
              "breakdown": {"citizen_demand": 0, "severity": 15,
                            "population_impact": 17.9, "cost_feasibility": 8.2},
              "is_existing_plan_project": true
            }
          ]
        }
      ]
    }
"""
import json
from functools import lru_cache
from pathlib import Path
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.config import CONSTITUENCY
from app.services.store import STORE

router = APIRouter()

_COORDS_PATH = Path(__file__).resolve().parent.parent / "data" / "village_coordinates.json"


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class HeatmapProject(BaseModel):
    id: str
    title: str
    category: str
    description: Optional[str] = None      # what the project is about (summary/details)
    explanation: Optional[str] = None      # reasoning from the Explainability agent
    submission_count: int = 0              # citizen submissions clustered into this project
    population_affected: int = 0           # estimated affected population
    priority_score: float
    breakdown: dict
    is_existing_plan_project: bool = False


class HeatmapTown(BaseModel):
    name: str
    state: str
    lat: Optional[float] = None
    lng: Optional[float] = None
    projects: list[HeatmapProject]


class HeatmapData(BaseModel):
    towns: list[HeatmapTown]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _load_coords() -> dict[str, list[float]]:
    """Gazetteer: lowercased location name -> [lat, lng]. Cached after first read."""
    try:
        with _COORDS_PATH.open(encoding="utf-8") as f:
            raw = json.load(f)
    except Exception:
        return {}
    # Drop the "_comment" key and any non-coordinate entries.
    out: dict[str, list[float]] = {}
    for k, v in raw.items():
        if k.startswith("_"):
            continue
        if isinstance(v, list) and len(v) == 2:
            out[str(k).strip().lower()] = [float(v[0]), float(v[1])]
    return out


def _coords_for(location: str) -> tuple[Optional[float], Optional[float]]:
    coords = _load_coords()
    key = (location or "").strip().lower()
    if key in coords:
        return coords[key][0], coords[key][1]
    return None, None


def _summary(ctx, rec) -> Optional[str]:
    """A short human summary of WHAT the project is (potholes, a health centre,
    etc.) — never fabricated. Prefers the Explainability agent's narrative when
    it is a real description rather than the deterministic 'scored X/100' string.
    """
    expl = rec.explanation.summary if rec.explanation else None
    if expl and "scored" not in expl.lower():
        return expl
    if ctx is not None:
        kind = "Planned" if rec.is_existing_plan_project else "Citizen-raised"
        return f"{kind} {ctx.category} project for {ctx.location}: {rec.title}."
    return rec.title


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------

@router.get("/api/heatmap", response_model=HeatmapData)
def get_heatmap() -> HeatmapData:
    """Group every stored recommendation by its town and return map-ready data.

    Projects are ordered highest-priority-first within each town; towns are
    ordered by their single worst (highest) project priority so the busiest /
    most urgent settlements surface first.
    """
    state_name = CONSTITUENCY.get("state", "India")

    # location key -> {"name", "projects": [...]}
    grouped: dict[str, dict] = {}

    for rec in STORE.all_recommendations_sorted():          # already sorted desc
        ctx = STORE.get_context(rec.project_id)
        category = ctx.category if ctx is not None else "Other"
        location = (ctx.location if ctx is not None else "") or "unspecified"
        key = location.strip().lower()
        if key in ("", "unspecified"):
            # No place to put it on a map — skip rather than pin it wrongly.
            continue

        demand = int(ctx.demand_count) if ctx and ctx.demand_count else 0
        pop = int(ctx.population_affected) if ctx and ctx.population_affected else 0
        expl = rec.explanation.summary if rec.explanation else None

        bucket = grouped.setdefault(key, {"name": location.strip(), "projects": []})
        bucket["projects"].append(HeatmapProject(
            id=rec.project_id,
            title=rec.title,
            category=category,
            description=_summary(ctx, rec),
            # Only surface the explanation callout when it differs from the summary.
            explanation=(expl if (expl and "scored" in expl.lower()) else None),
            submission_count=demand,
            population_affected=pop,
            priority_score=rec.priority_score,
            breakdown=rec.breakdown.model_dump(),
            is_existing_plan_project=rec.is_existing_plan_project,
        ))

    towns: list[HeatmapTown] = []
    for bucket in grouped.values():
        lat, lng = _coords_for(bucket["name"])
        towns.append(HeatmapTown(
            name=bucket["name"],
            state=state_name,
            lat=lat,
            lng=lng,
            projects=bucket["projects"],
        ))

    # Busiest / most urgent towns first (by their top project's score).
    towns.sort(key=lambda t: max((p.priority_score for p in t.projects), default=0),
               reverse=True)
    return HeatmapData(towns=towns)
