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
    """Percentile-rank normalisation.

    Min-max normalisation broke on these datasets: 77% of districts share
    medicine_shortage_ratio=0.0 (so Nagpur always scored exactly 0) and single
    outliers (Mumbai teledensity 210) stretched the scale so everyone else
    compressed into a corner. Percentile rank is robust to both: ties get the
    mid-rank, outliers only count as one rank position.
    """
    vals = sorted(v for v in all_values if v is not None)
    if not vals or vals[0] == vals[-1]:
        return 0.5
    below = sum(1 for v in vals if v < value)
    equal = sum(1 for v in vals if v == value)
    pct = (below + 0.5 * equal) / len(vals)
    return round(pct if direction == "higher_is_more_need" else 1 - pct, 4)


def apply_complaint_boost(base: float, demand: int, max_demand: int) -> float:
    if max_demand == 0:
        return base
    return min(1.0, base + 0.15 * (demand / max_demand))
