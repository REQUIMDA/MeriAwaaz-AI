import json
import sys
from pathlib import Path

from app.schemas.schema import ClusterResult, FusedContext, Recommendation


class Store:
    def __init__(self):
        self.clusters: dict[str, ClusterResult] = {}
        self.cluster_submissions: dict[str, list[dict]] = {}
        self.fused_contexts: dict[str, FusedContext] = {}
        self.recommendations: dict[str, Recommendation] = {}

    def load_local_plans_as_contexts(self, path: str | Path):
        path_obj = Path(path)
        if not path_obj.is_absolute():
            path_obj = Path(__file__).resolve().parent.parent / path_obj
        if not path_obj.exists():
            # scripts/ lives outside the app package (repo_root/scripts), so it
            # isn't a normal importable module — add it to sys.path only here,
            # right before we actually need it (this branch rarely runs since
            # local_plans.json is normally already present).
            scripts_dir = Path(__file__).resolve().parent.parent.parent.parent / "scripts"
            if str(scripts_dir) not in sys.path:
                sys.path.insert(0, str(scripts_dir))
            from build_local_plans import write_local_plans
            path_obj = write_local_plans(path_obj)
        with path_obj.open("r", encoding="utf-8") as fh:
            plans = json.load(fh)
        for plan in plans:
            ctx = FusedContext(
                category=plan["category"],
                location=plan["location"]["village"],
                demand_count=0,
                population_affected=plan.get("estimated_beneficiaries", 0),
                estimated_cost_inr=plan.get("estimated_cost_inr"),
                data_confidence="synthetic",
                severity_score=0.5,
                category_specific_data={"title": plan["title"], "source": plan["source"]},
                is_existing_plan_project=True,
            )
            self.fused_contexts[plan["plan_id"]] = ctx

    def all_recommendations_sorted(self) -> list[Recommendation]:
        return sorted(self.recommendations.values(), key=lambda r: -r.priority_score)


STORE = Store()
__all__ = ["Store", "STORE"]