import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # points to backend/app/


def load_json(path: str) -> list:
    resolved = BASE_DIR / path
    with resolved.open("r", encoding="utf-8") as f:
        return json.load(f)


def match_by_location(location: str, records: list, key_field: str) -> dict | None:
    target = location.strip().lower()
    for record in records:
        if str(record.get(key_field, "")).strip().lower() == target:
            return record
    return None


def normalize(value: float, all_values: list, direction: str) -> float:
    vals = [v for v in all_values if v is not None]
    if not vals or max(vals) == min(vals):
        return 0.5
    norm = (value - min(vals)) / (max(vals) - min(vals))
    return norm if direction == "higher_is_more_need" else 1 - norm


def apply_complaint_boost(base: float, demand: int, max_demand: int) -> float:
    if max_demand == 0:
        return base
    return min(1.0, base + 0.15 * (demand / max_demand))
