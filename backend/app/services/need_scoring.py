# backend/need_scoring.py
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.clean_utils import resolve_path


def load_json(path):
    resolved = resolve_path(path)
    with resolved.open("r", encoding="utf-8") as f:
        return json.load(f)

def match_by_location(location: str, need_records: list, key_field: str) -> dict | None:
    target = location.strip().lower()
    for record in need_records:
        if str(record.get(key_field, "")).strip().lower() == target:
            return record
    return None

def normalize(value: float, all_values: list, direction: str) -> float:
    if not all_values or max(all_values) == min(all_values):
        return 0.5
    norm = (value - min(all_values)) / (max(all_values) - min(all_values))
    return norm if direction == "higher_is_more_need" else 1 - norm

def apply_complaint_boost(base_severity: float, demand_count: int, max_demand_count: int) -> float:
    if max_demand_count == 0:
        return base_severity
    boost = 0.15 * (demand_count / max_demand_count)
    return min(1.0, base_severity + boost)