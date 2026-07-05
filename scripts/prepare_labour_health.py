# backend/prepare_labour_health.py
import pandas as pd  # type: ignore
from clean_utils import ensure_output_path, normalize_col, resolve_path


def clean_labour_health(path: str) -> pd.DataFrame:
    df = pd.read_csv(resolve_path(path), encoding="latin-1")
    df.columns = [normalize_col(c) for c in df.columns]

    numeric_cols = [
        "no_of_opd_total_static", "no_of_opd_total_mobile", "no_ipd",
        "total_no_of_male_opd", "total_no_of_female_opd", "total_no_of_children_opd",
        "approx_no_of_patient_reffered_outside_due_to_lack_of_medicines",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["total_opd"] = df[["total_no_of_male_opd", "total_no_of_female_opd",
                           "total_no_of_children_opd"]].sum(axis=1, skipna=True)

    agg = df.groupby(["state", "district"], as_index=False).agg(
        total_opd=("total_opd", "sum"),
        total_referred_for_lack_of_medicine=(
            "approx_no_of_patient_reffered_outside_due_to_lack_of_medicines", "sum"),
        dispensary_count=("name_of_the_dispensary", "count"),
    )
    agg["medicine_shortage_ratio"] = (
        agg["total_referred_for_lack_of_medicine"] / agg["total_opd"].replace(0, pd.NA)
    ).fillna(0)

    return agg[["state", "district", "total_opd", "dispensary_count", "medicine_shortage_ratio"]]

if __name__ == "__main__":
    clean_labour_health("data/raw/Labour_Health_Scheme_LABOUR.csv") \
        .to_json(ensure_output_path("data/processed/healthcare_need.json"), orient="records")