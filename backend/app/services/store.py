import json
import os
from typing import Optional

from app.schemas.models import FusedContext, Recommendation, ScoreBreakdown


class _Store:
    def __init__(self):
        self._contexts: dict[str, FusedContext] = {}
        self._recommendations: dict[str, Recommendation] = {}

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
            print(f"WARNING: local_plans.json not found at {json_path}, skipping.")
            return

        from app.services.need_scoring import score_plan_project
        from app.tools.policy_tools import compute_priority_score

        with open(json_path) as f:
            plans = json.load(f)

        for plan in plans:
            ctx = score_plan_project(plan)
            self.upsert_context(plan["plan_id"], ctx)

            max_pop = 15000
            result = compute_priority_score.invoke({
                "citizen_demand": 0.0,
                "infrastructure_gap": ctx.severity_score,
                "population_impact": min(ctx.population_affected / max_pop, 1.0),
                "cost_feasibility": max(0.0, 1.0 - (ctx.estimated_cost_inr or 0) / 5_000_000),
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