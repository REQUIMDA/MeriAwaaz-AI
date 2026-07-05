# backend/prepare_context_stats.py
import json
import pandas as pd  # type: ignore[import]
from clean_utils import ensure_output_path, normalize_col, resolve_path


def clean_pfms_expenditure(path: str) -> pd.DataFrame:
    df = pd.read_csv(resolve_path(path), encoding="latin-1")
    df.columns = [normalize_col(c) for c in df.columns]
    amt_col = [c for c in df.columns if "amount" in c][0]
    df[amt_col] = df[amt_col].astype(str).str.replace(",", "", regex=False).astype(float)
    return df.rename(columns={amt_col: "amount_inr"})

def clean_forest_training(path: str) -> pd.DataFrame:
    df = pd.read_csv(resolve_path(path), encoding="latin-1")
    df.columns = [normalize_col(c) for c in df.columns]
    return df

if __name__ == "__main__":
    pfms = clean_pfms_expenditure("data/raw/PFMS_CS_EXPENDITURE.csv")
    forest = clean_forest_training("data/raw/Percentage_Participation_Report_2022_23_0_FOREST.csv")
    output_path = ensure_output_path("data/processed/context_stats.json")
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(
            {
                "pfms_scheme_expenditure": pfms.to_dict(orient="records"),
                "forest_officer_training": forest.to_dict(orient="records"),
            },
            fh,
            indent=2,
        )