from typing import List

from pydantic import BaseModel

from app.schemas.models import ScoreBreakdown


class HeatmapPoint(BaseModel):
    ward: str
    lat: float
    lon: float
    intensity: int


class ProjectCard(BaseModel):
    id: str
    title: str
    category: str
    priority_score: float
    breakdown: ScoreBreakdown
    is_existing_plan_project: bool


class DashboardData(BaseModel):
    projects: List[ProjectCard]
    heatmap: List[HeatmapPoint]
    total_submissions: int
    last_updated: str
