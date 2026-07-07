CONSTITUENCY = {
    "state": "Maharashtra",     # ← change this to your real state
    "district": "Nagpur",        # ← change this to your real district
}
__all__ = ["CONSTITUENCY"]

CATEGORY_CONFIG = {
    "Healthcare": {
        "dataset": "data/healthcare_need.json",
        "location_level": "district",
        "location_field": "district",
        "need_field": "medicine_shortage_ratio",
        "direction": "higher_is_more_need",
    },
    "Education": {
        "dataset": "data/education_need.json",
        "location_level": "state",
        "location_field": "state",
        "need_field": "large_school_pct",
        "direction": "higher_is_more_need",
    },
    "Other": {
        "dataset": "data/digital_connectivity_need.json",
        "location_level": "state",
        "location_field": "state",
        "need_field": "rural_teledensity",
        "direction": "lower_is_more_need",
        # City and aggregate rows are not states — including them in the
        # normalisation pool (Mumbai teledensity 210) inflated everyone's need
        "exclude_locations": ["Delhi", "Mumbai", "Chennai", "Kolkata", "North-East"],
    },
    # Roads, Water, Sanitation, Electricity, Vocational: add entries here the
    # moment you source real data for them.
}

# Synthetic per-category cost anchors (₹) for citizen-originated projects with
# no matched plan cost. Estimates modelled on local_plans.json — NOT quotes.
# Without these, cost_feasibility was a dead constant for every new project.
CATEGORY_COST_ESTIMATES = {
    "Education": 3_500_000,
    "Healthcare": 1_800_000,
    "Roads": 6_000_000,
    "Water": 2_500_000,
    "Sanitation": 1_200_000,
    "Electricity": 2_000_000,
    "Vocational": 4_500_000,
    "Other": 1_500_000,
}

__all__ = ["CATEGORY_CONFIG", "CATEGORY_COST_ESTIMATES", "CONSTITUENCY"]