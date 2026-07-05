from pydantic import BaseModel, Field
from typing import Optional, Literal, List

Category = Literal[
    "Education", "Healthcare", "Roads", "Water",
    "Sanitation", "Electricity", "Vocational", "Other"
]
DataConfidence = Literal["real_data", "estimated", "synthetic"]
# ---------------------------------------------------------------------------
# Citizen Intelligence Agent output
# ---------------------------------------------------------------------------

class ParsedIssue(BaseModel):
    category: Category
    location: str = Field(description="Ward, village, or area name. 'unspecified' if unclear.")
    summary: str = Field(description="One-sentence summary of the citizen's request.")
    confidence: float = Field(ge=0.0, le=1.0, description="How certain the AI is it understood this submission correctly.")
    language: str = Field(description="ISO 639-1 language code, e.g. 'en', 'hi'.")

# ---------------------------------------------------------------------------
# Demand Intelligence Agent output
# ---------------------------------------------------------------------------


class ClusterResult(BaseModel):
    cluster_id: str = Field(description="Unique identifier of the matched demand cluster.")
    cluster_name: str = Field(description="Short human-readable label, e.g. 'School Infrastructure'.")
    cluster_size: int = Field(ge=1, description="Total number of similar citizen submissions in this cluster.")
    center_location: str = Field(description="Most common or representative location for the cluster.")

# ---------------------------------------------------------------------------
# Knowledge Fusion Agent output
# ---------------------------------------------------------------------------
class FusedContext(BaseModel):
    category: Category
    location: str
    demand_count: int                          # 0 for plan-sourced items — no citizens generated them
    population_affected: int
    estimated_cost_inr: Optional[float] = Field(
    default=None,
    ge=0)
    data_confidence: DataConfidence
    severity_score: float = Field(ge=0.0, le=1.0, description="Normalized infrastructure need from public data.")
    category_specific_data: dict[str, int | float | str] = Field(
    default_factory=dict
)
    is_existing_plan_project: bool = Field(
        default=False,
        description="True if sourced from the local development plan's existing project list, not a citizen submission."
    )
# ---------------------------------------------------------------------------
# Policy Recommendation Agent output
# ---------------------------------------------------------------------------

    
class ScoreBreakdown(BaseModel):
    citizen_demand: float = Field(ge=0.0, le=40.0, description="Contribution of citizen demand to the final score.")
    severity: float = Field(ge=0.0, le=30.0, description="Contribution of infrastructure need to the final score.")
    population_impact: float = Field(ge=0.0, le=20.0, description="Contribution of affected population.")
    cost_feasibility: float = Field(ge=0.0, le=10.0, description="Contribution of project cost.")





# ---------------------------------------------------------------------------
# Explainability Agent output
# ---------------------------------------------------------------------------
class Explanation(BaseModel):
    evidence: List[str] = Field(description="2-3 grounded evidence bullets citing the actual numbers behind the score.")
    summary: str = Field(description="2-3 sentence human-readable explanation for the MP.")
    confidence_score: float = Field(
        ge=0.0, le=1.0,
        description="How well-supported this recommendation is by the data — distinct from ParsedIssue.confidence, which is about understanding the raw citizen submission, not the ranking."
    )
class Recommendation(BaseModel):
    project_id: str
    title: str
    priority_score: float = Field(ge=0.0, le=100.0)
    breakdown: ScoreBreakdown
    is_existing_plan_project: bool = False
    explanation: Optional[Explanation] = None   # None right after Policy Agent; filled in by Explainability Agent


# ---------------------------------------------------------------------------
# LangGraph shared state (full pipeline)
# ---------------------------------------------------------------------------

class AgentState(BaseModel):
    submission_id: str
    input_type: Literal["text", "voice", "photo", "dashboard_refresh"]
    raw_text: str = ""
    media_file_path: Optional[str] = None

    parsed_issue: Optional[ParsedIssue] = None
    cluster: Optional[ClusterResult] = None
    knowledge_context: Optional[FusedContext] = None
    recommendation: Optional[Recommendation] = None   # explanation lives inside this now

    error: Optional[str] = None
