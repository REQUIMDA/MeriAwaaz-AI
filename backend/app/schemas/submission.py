from typing import Optional

from pydantic import BaseModel


class SubmissionRequest(BaseModel):
    text: str
    location_hint: Optional[str] = None


class ParsedIssue(BaseModel):
    category: str
    urgency: str
    location: str
    summary: str
    confidence: float
