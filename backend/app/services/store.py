import json
import os
from typing import Optional

from app.schemas.models import FusedContext, Recommendation, ScoreBreakdown, ClusterResult


class _Store:
    def __init__(self):
        self._contexts: dict[str, FusedContext] = {}
        self._recommendations: dict[str, Recommendation] = {}
        self.clusters: dict[str, ClusterResult] = {}
        self.cluster_submissions: dict[str, list[dict]] = {}

    def upsert_context(self, project_id: str, ctx: FusedContext) -> None:
        self._contexts[project_id] = ctx

    def get_context(self, project_id: str) -> Optional[FusedContext]:
        return self._contexts.get(project_id)

    def all_contexts(self) -> list[FusedContext]:
        return list(self._contexts.values())

    def upsert_recommendation(self, rec: Recommendation) -> None:
        self._recommendations[rec.project_id] = rec

    def get_recommendation(self, project_id: str) -> Optional[Recommendation]:
        return self._recommendations.get(project_id)

    def all_recommendations_sorted(self) -> list[Recommendation]:
        return sorted(
            self._recommendations.values(),
            key=lambda r: r.priority_score,
            reverse=True,
        )

    def load_local_plans(self, json_path: str) -> None:
        if not os.path.exists(json_path):
            print(f"WARNING: {json_path} not found, skipping.")
            return
        with open(json_path) as f:
            plans = json.load(f)
        for plan in plans:
            pop = plan.get("estimated_beneficiaries", 0)
            cost = plan.get("estimated_cost_inr") or 0
            location = plan["location"]["village"] if isinstance(plan["location"], dict) else plan["location"]
            ctx = FusedContext(
                category=plan["category"],
                location=location,
                demand_count=0,
                population_affected=pop,
                estimated_cost_inr=cost,
                data_confidence="synthetic",
                severity_score=0.5,
                category_specific_data={"title": plan["title"], "source": plan.get("source", "handbuilt")},
                is_existing_plan_project=True,
            )
            self.upsert_context(plan["plan_id"], ctx)
            from app.tools.policy_tools import compute_priority_score
            result = compute_priority_score.invoke({
                "citizen_demand": 0.0,
                "infrastructure_gap": 0.5,
                "population_impact": min(pop / 15000, 1.0),
                "cost_feasibility": max(0.0, 1.0 - cost / 10_000_000),
            })
            rec = Recommendation(
                project_id=plan["plan_id"],
                title=plan["title"],
                priority_score=result["priority_score"],
                breakdown=ScoreBreakdown(**result["breakdown"]),
                is_existing_plan_project=True,
                explanation=None,
            )
            self.upsert_recommendation(rec)
        print(f"Store: loaded {len(plans)} local plan projects.")


STORE = _Store()