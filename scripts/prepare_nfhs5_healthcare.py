"""
Convert the NFHS-5 Maharashtra district CSV into healthcare_need_nfhs5.json.

Source (CC-BY-4.0, converted from official rchiips.org NFHS-5 factsheets,
DOI 10.7910/DVN/42WNZF):
  https://github.com/pratapvardhan/NFHS-5/blob/master/district-level/NFHS-5-MH-Maharashtra.csv

Steps:
  1. Open the link above in your browser and click "Download raw file".
  2. Save it as NFHS-5-MH-Maharashtra.csv next to this script (or pass a path).
  3. Run:  python scripts/prepare_nfhs5_healthcare.py
  4. Update the Healthcare entry in backend/app/config.py (snippet printed below).

The health_need_index (0-100, higher = more need) averages five real NFHS-5
indicators: institutional-birth deficit, vaccination deficit, health-insurance
deficit, child stunting, and child underweight.
"""
import csv
import json
import re
import sys
from pathlib import Path

CSV_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else \
    Path(__file__).parent / "NFHS-5-MH-Maharashtra.csv"
OUT_PATH = (Path(__file__).resolve().parents[1]
            / "backend" / "app" / "data" / "healthcare_need_nfhs5.json")

# indicator text pattern -> how it maps to "need"
#   deficit: need = 100 - value   (good things that are missing)
#   burden : need = value         (bad things that are present)
INDICATORS = {
    r"institutional births \(%\)": "deficit",
    r"fully vaccinated": "deficit",
    r"health insurance": "deficit",
    r"under 5 years who are stunted": "burden",
    r"under 5 years who are underweight": "burden",
}


def to_float(s):
    try:
        return float(str(s).strip().replace(",", ""))
    except (TypeError, ValueError):
        return None


def main():
    if not CSV_PATH.exists():
        sys.exit(f"CSV not found: {CSV_PATH}\n"
                 "Download it from https://github.com/pratapvardhan/NFHS-5/"
                 "blob/master/district-level/NFHS-5-MH-Maharashtra.csv")

    per_district: dict[str, list[float]] = {}
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.reader(f):
            if len(row) < 5:
                continue
            district, question = row[2].strip(), row[3].lower()
            # first numeric cell after the question column is the total value
            value = next((v for v in (to_float(c) for c in row[4:])
                          if v is not None), None)
            if value is None or not district:
                continue
            for pattern, direction in INDICATORS.items():
                if re.search(pattern, question):
                    need = (100 - value) if direction == "deficit" else value
                    per_district.setdefault(district, []).append(
                        max(0.0, min(100.0, need)))

    records = [
        {"state": "Maharashtra", "district": d,
         "health_need_index": round(sum(vals) / len(vals), 2)}
        for d, vals in sorted(per_district.items()) if vals
    ]
    if not records:
        sys.exit("No indicators matched — check the CSV format "
                 "(expected columns: state, code, district, question, value, ...)")

    OUT_PATH.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"Wrote {len(records)} districts to {OUT_PATH}\n")
    for r in records:
        marker = "  <-- constituency" if r["district"].lower() == "nagpur" else ""
        print(f"  {r['district']:<24} {r['health_need_index']}{marker}")

    print("\nNow replace the Healthcare entry in backend/app/config.py with:\n")
    print('''    "Healthcare": {
        "dataset": "data/healthcare_need_nfhs5.json",
        "location_level": "district",
        "location_field": "district",
        "need_field": "health_need_index",
        "direction": "higher_is_more_need",
    },''')


if __name__ == "__main__":
    main()
