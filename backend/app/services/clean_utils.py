# backend/clean_utils.py
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def normalize_col(col: str) -> str:
    col = col.strip().lower()
    col = re.sub(r"[^0-9a-z]+", "_", col)
    return re.sub(r"_+", "_", col).strip("_")


def resolve_path(path: str | Path) -> Path:
    path_obj = Path(path)
    if path_obj.is_absolute():
        return path_obj
    return BASE_DIR / path_obj


def ensure_output_path(path: str | Path) -> Path:
    output_path = resolve_path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path