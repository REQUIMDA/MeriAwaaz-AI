from pydantic import BaseModel, Field  # type: ignore[import]
from typing import Optional, Literal, List

Category = Literal[
    "Education", "Healthcare", "Roads", "Water",
    "Sanitation", "Electricity", "Vocational", "Other"
]
DataConfidence = Literal["real_data", "estimated", "synthetic"]

class ParsedIssue(BaseModel):
    category: Category
    location: str = Field(description="Ward, village, or area name. 'unspecified' if unclear.")
    summary: str = Field(description="One-sentence summary of the citizen's request.")
    confidence: float = Field(ge=0.0, le=1.0)
    language: str = Field(description="ISO 639-1 language code, e.g. 'en', 'hi'.")

class ClusterResult(BaseModel):
    cluster_id: str
    cluster_name: str
    cluster_size: int = Field(ge=1)
    center_location: str

class FusedContext(BaseModel):
    category: Category
    location: str
    demand_count: int
    population_affected: int
    estimated_cost_inr: Optional[float] = Field(default=None, ge=0)
    data_confidence: DataConfidence
    severity_score: float = Field(ge=0.0, le=1.0)
    category_specific_data: dict[str, int | float | str] = Field(default_factory=dict)
    is_existing_plan_project: bool = Field(default=False)

class ScoreBreakdown(BaseModel):
    citizen_demand: float = Field(ge=0.0, le=40.0)
    severity: float = Field(ge=0.0, le=30.0)
    population_impact: float = Field(ge=0.0, le=20.0)
    cost_feasibility: float = Field(ge=0.0, le=10.0)

class Explanation(BaseModel):
    evidence: List[str]
    summary: str
    confidence_score: float = Field(ge=0.0, le=1.0)

class Recommendation(BaseModel):
    project_id: str
    title: str
    priority_score: float = Field(ge=0.0, le=100.0)
    breakdown: ScoreBreakdown
    is_existing_plan_project: bool = False
    explanation: Optional[Explanation] = None

class AgentState(BaseModel):
    submission_id: str
    input_type: Literal["text", "voice", "photo", "dashboard_refresh"]
    raw_text: str = ""
    media_file_path: Optional[str] = None
    parsed_issue: Optional[ParsedIssue] = None
    cluster: Optional[ClusterResult] = None
    knowledge_context: Optional[FusedContext] = None
    recommendation: Optional[Recommendation] = None
    error: Optional[str] = None