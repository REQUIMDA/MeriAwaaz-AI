# backend/prepare_udise.py
import pandas as pd  # type: ignore
from clean_utils import ensure_output_path, resolve_path


def clean_udise_school_size(path: str) -> pd.DataFrame:
    df = pd.read_csv(resolve_path(path), encoding="latin-1")
    cols = df.columns.tolist()
    bracket_labels = [
        "total_schools", "pct_lt_10", "pct_11_20", "pct_21_30", "pct_31_40", "pct_41_50",
        "pct_51_60", "pct_61_70", "pct_71_80", "pct_81_90", "pct_91_100", "pct_101_200",
        "pct_201_300", "pct_301_400", "pct_401_500", "pct_gt_500",
    ]
    rename_map = {cols[0]: "sl_no", cols[1]: "state"}
    for orig_col, label in zip(cols[2:], bracket_labels):
        rename_map[orig_col] = label
    df = df.rename(columns=rename_map)
    df = df[df["state"] != "India"]
    for label in bracket_labels:
        df[label] = pd.to_numeric(df[label], errors="coerce")

    df["large_school_pct"] = df["pct_401_500"] + df["pct_gt_500"]
    df["small_school_pct"] = df["pct_lt_10"] + df["pct_11_20"]
    return df[["state", "total_schools", "large_school_pct", "small_school_pct"]]

if __name__ == "__main__":
    clean_udise_school_size("data/raw/UDISE_2022_23_Table_2.3_0_EDUCATION.csv") \
        .to_json(ensure_output_path("data/processed/education_need.json"), orient="records")