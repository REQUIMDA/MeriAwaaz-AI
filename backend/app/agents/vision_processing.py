"""
Vision Processing Agent
-----------------------
Runs when input_type == "image".
Reads the image from state.media_file_path, sends it to Gemini Vision,
and writes a plain-text description into state.raw_text so the rest of
the pipeline (Citizen Intelligence -> ... -> Explainability) runs unchanged.
"""

import base64
from pathlib import Path

from langchain_core.messages import HumanMessage

from app.schemas.models import AgentState


def run(state: AgentState) -> dict:
    """LangGraph node entry point. Returns AgentState fields to update."""
    file_path = state.media_file_path

    if not file_path or not Path(file_path).exists():
        return {
            "raw_text": "A citizen submitted a photo but the image could not be read.",
            "error": f"Image file not found: {file_path}",
        }

    image_bytes = Path(file_path).read_bytes()
    b64_image = base64.standard_b64encode(image_bytes).decode("utf-8")

    ext = Path(file_path).suffix.lower()
    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }
    mime_type = mime_map.get(ext, "image/jpeg")

    prompt_text = (
        "You are analyzing a photo submitted by a citizen to their Member of Parliament in India.\n\n"
        "Describe what you see in 2-4 sentences, focusing on:\n"
        "- What infrastructure problem or civic issue is visible\n"
        "- How severe it looks\n"
        "- Any visible location clues (signboards, landmarks, road names)\n\n"
        "Write as if you are the citizen describing their complaint. "
        "Be specific and factual — do not guess what is not visible."
    )

    try:
        from app.core.llm import get_model
        model = get_model()

        message = HumanMessage(content=[
            {"type": "text", "text": prompt_text},
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{b64_image}"},
            },
        ])

        response = model.invoke([message])
        description = response.content if hasattr(response, "content") else str(response)
        return {"raw_text": description.strip()}

    except Exception as e:
        return {
            "raw_text": "A citizen submitted a photo showing a civic infrastructure problem.",
            "error": f"Vision processing failed: {str(e)}",
        }
