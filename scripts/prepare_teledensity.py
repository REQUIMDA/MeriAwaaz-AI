# backend/prepare_teledensity.py
import pandas as pd  # type: ignore
import csv
import json
from typing import Any, Dict, List
from clean_utils import ensure_output_path, normalize_col, resolve_path


def clean_teledensity(path: str) -> pd.DataFrame:
    df = pd.read_csv(resolve_path(path), encoding="latin-1")
    df.columns = [normalize_col(c) for c in df.columns]
    df = df.rename(columns={"at_the_end_of_march": "year"})
    for col in ["total", "wireline", "wireless", "rural", "urban", "public", "private"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    latest_year = df["year"].max()
    latest = df[df["year"] == latest_year].copy()
    return latest[["state", "year", "rural", "total"]].rename(columns={"rural": "rural_teledensity"})

if __name__ == "__main__":
    clean_teledensity("data/raw/Table_3.3_IT.csv") \
        .to_json(ensure_output_path("data/processed/digital_connectivity_need.json"), orient="records")