# backend/intake_agent.py
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.schemas.schema import AgentState, ParsedIssue

KEYWORD_MAP = {
    "Education": ["school", "classroom", "teacher", "student"],
    "Healthcare": ["hospital", "doctor", "medicine", "health", "clinic"],
    "Electricity": ["power cut", "electricity", "transformer", "voltage"],
    "Water": ["water", "tap", "borewell", "handpump"],
    "Roads": ["road", "pothole", "bridge", "highway"],
    "Sanitation": ["toilet", "drainage", "garbage", "sewage"],
    "Vocational": ["training", "iti", "skill", "employment"],
}
KNOWN_LOCATIONS = ["Rampur", "Kesarpur", "Sultanpur", "Bhelupur"]   # extend with your real village list

def intake_agent_stub(state: AgentState) -> AgentState:
    text_lower = state.raw_text.lower()

    category = "Other"
    for cat, keywords in KEYWORD_MAP.items():
        if any(kw in text_lower for kw in keywords):
            category = cat
            break

    location = "unspecified"
    for loc in KNOWN_LOCATIONS:
        if loc.lower() in text_lower:
            location = loc
            break

    state.parsed_issue = ParsedIssue(
        category=category, location=location,
        summary=state.raw_text[:100], confidence=0.6, language="en",
    )
    return state
