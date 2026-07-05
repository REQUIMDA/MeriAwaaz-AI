import json
from pathlib import Path

LOCAL_PLANS = [
    {
        "plan_id": "plan_001",
        "category": "Education",
        "location": {"village": "Rampur", "block": "Sadar", "district": "Nagpur"},
        "title": "Additional classroom block - Rampur Govt Primary School",
        "estimated_cost_inr": 3500000,
        "estimated_beneficiaries": 210,
        "source": "mplads_pattern_handbuilt",
    },
    {
        "plan_id": "plan_002",
        "category": "Healthcare",
        "location": {"village": "Kesarpur", "block": "North", "district": "Nagpur"},
        "title": "Upgrade of Primary Health Sub-Centre - Kesarpur",
        "estimated_cost_inr": 1800000,
        "estimated_beneficiaries": 1450,
        "source": "mplads_pattern_handbuilt",
    },
]


def write_local_plans(output_path: str | Path | None = None) -> Path:
    project_root = Path(__file__).resolve().parent.parent
    output_path = Path(output_path) if output_path is not None else project_root / "app" / "data" / "local_plans.json"
    if not output_path.is_absolute():
        output_path = project_root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(LOCAL_PLANS, fh, indent=2)
    return output_path
