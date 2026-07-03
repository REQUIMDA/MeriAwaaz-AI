from typing import List

from pydantic import BaseModel


class Recommendation(BaseModel):
    project_id: str
    priority_score: float
    confidence: float
    reason: str
    evidence: List[str]
