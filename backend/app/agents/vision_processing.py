"""LangGraph node: vision_processing_agent — describes image content, hands off to citizen_intelligence_agent."""

import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from app.schemas.models import AgentState

load_dotenv()

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

_MIME_MAP = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
}

_PROMPT = (
    "Describe the infrastructure issue visible in this image in 2-4 sentences. "
    "Focus on: what the physical problem is, which type of public facility or infrastructure is affected, "
    "and a brief severity impression if visually clear (e.g. 'roof partially collapsed' vs 'minor crack'). "
    "Be factual and specific — do not speculate beyond what is visible. "
    "Do not classify into a category or recommend any action."
)


def run(state: AgentState) -> AgentState:
    """Describe the image at state.media_file_path and append description to state.raw_text."""
    try:
        if not state.media_file_path:
            return state.model_copy(update={
                "error": "vision_processing_agent: media_file_path is empty"
            })

        path = Path(state.media_file_path)
        mime = _MIME_MAP.get(path.suffix.lower(), "image/jpeg")

        with open(path, "rb") as f:
            image_bytes = f.read()

        response = _client.models.generate_content(
            model=_MODEL,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime),
                _PROMPT,
            ],
            config=types.GenerateContentConfig(temperature=0.2),
        )

        description = response.text.strip()

        if state.raw_text:
            combined = f"{state.raw_text}\n\n[Image Description]\n{description}"
        else:
            combined = description

        return state.model_copy(update={"raw_text": combined})

    except Exception as e:
        return state.model_copy(update={"error": f"vision_processing_agent: {e}"})
