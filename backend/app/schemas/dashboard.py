from typing import List

from pydantic import BaseModel


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
    confidence: float
    reason: str
    evidence: List[str]


class DashboardData(BaseModel):
    projects: List[ProjectCard]
    heatmap: List[HeatmapPoint]
    total_submissions: int
    last_updated: str
