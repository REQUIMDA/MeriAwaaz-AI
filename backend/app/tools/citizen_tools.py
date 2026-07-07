import json
import re

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

_CATEGORIES = [
    "Education", "Healthcare", "Roads", "Water",
    "Sanitation", "Electricity", "Vocational", "Other",
]


def _parse_json(text: str) -> dict:
    """Strip markdown code fences then parse JSON."""
    text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
    return json.loads(text)


@tool
def extract_issue_details(text: str) -> dict:
    """Extract structured issue details from a citizen's raw text submission.

    Calls Gemini to parse category, location, summary, and confidence from
    whatever the citizen wrote or said (any language).

    Args:
        text: raw citizen submission text

    Returns:
        dict with keys: category, location, summary, confidence
    """
    from app.core.llm import get_model

    prompt = (
        "You are analyzing a citizen complaint submitted to an Indian Member of Parliament.\n\n"
        "Extract the following and return ONLY valid JSON — no markdown, no explanation:\n"
        "{\n"
        f'  "category": one of {_CATEGORIES},\n'
        '  "location": "village or ward name — set to \\"unspecified\\" if unclear",\n'
        '  "summary": "one-sentence summary of what the citizen is asking for",\n'
        '  "confidence": 0.0–1.0 float for how clearly you understood the submission\n'
        "}\n\n"
        f'Citizen submission:\n"""{text}"""'
    )

    model = get_model()
    response = model.invoke([HumanMessage(content=prompt)])
    from app.core.llm import content_to_text
    content = content_to_text(getattr(response, "content", response))

    try:
        result = _parse_json(content)
        if result.get("category") not in _CATEGORIES:
            result["category"] = "Other"
        result["confidence"] = float(result.get("confidence", 0.7))
        result.setdefault("location", "unspecified")
        result.setdefault("summary", text[:120])
        return result
    except Exception:
        # Graceful fallback — never crash the pipeline
        return {
            "category": "Other",
            "location": "unspecified",
            "summary": text[:120],
            "confidence": 0.3,
        }


@tool
def detect_language(text: str) -> str:
    """Detect the language of the citizen's submission.

    Calls Gemini and returns an ISO 639-1 language code.

    Args:
        text: raw input text (first 300 chars are enough)

    Returns:
        ISO 639-1 code, e.g. 'en', 'hi', 'mr', 'ta'
    """
    from app.core.llm import get_model

    prompt = (
        "Detect the language of the text below.\n"
        "Return ONLY the ISO 639-1 two-letter code (e.g. en, hi, mr, ta, te, bn).\n"
        "No punctuation, no explanation — just the code.\n\n"
        f'Text: """{text[:300]}"""'
    )

    model = get_model()
    response = model.invoke([HumanMessage(content=prompt)])
    from app.core.llm import content_to_text
    content = content_to_text(getattr(response, "content", response))

    # Clean up whatever Gemini returned
    parts = content.strip().lower().replace('"', "").replace("'", "").split()
    code = parts[0] if parts else "en"
    # Keep only the first 2–3 chars; fall back to 'en' if nonsensical
    return code[:3] if (2 <= len(code) <= 3 and code.isalpha()) else "en"
