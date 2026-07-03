from langchain_core.tools import tool


@tool
def extract_issue_details(text: str) -> dict:
    """Extract structured issue details from a citizen's raw text submission.

    Use this tool to parse category, location, urgency, and a short summary
    from whatever the citizen wrote or said.

    Args:
        text: raw citizen submission text

    Returns:
        dict with keys: category, location, urgency, summary, confidence
    """
    # Real implementation will call Gemini with a structured prompt.
    # Returning a typed placeholder so the agent graph is testable now.
    return {
        "category": "",
        "location": "",
        "urgency": "",
        "summary": "",
        "confidence": 0.0,
    }


@tool
def detect_language(text: str) -> str:
    """Detect the language of the citizen's submission.

    Args:
        text: raw input text

    Returns:
        ISO 639-1 language code, e.g. 'en', 'hi', 'ta'
    """
    return "en"
