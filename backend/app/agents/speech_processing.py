"""LangGraph node: speech_processing_agent — transcribes audio, hands off to citizen_intelligence_agent."""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from app.schemas.models import AgentState

load_dotenv()

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

_PROMPT = (
    "Transcribe the audio exactly as spoken. "
    "Do not translate, correct grammar, or add punctuation beyond what is clearly spoken. "
    "Preserve the original language — do not convert to English. "
    "Output only the transcript text, nothing else."
)


def run(state: AgentState) -> AgentState:
    """Transcribe state.media_file_path audio and append transcript to state.raw_text."""
    try:
        if not state.media_file_path:
            return state.model_copy(update={
                "error": "speech_processing_agent: media_file_path is empty"
            })

        uploaded = _client.files.upload(file=state.media_file_path)

        response = _client.models.generate_content(
            model=_MODEL,
            contents=[
                types.Part.from_uri(
                    file_uri=uploaded.uri,
                    mime_type=uploaded.mime_type,
                ),
                _PROMPT,
            ],
            config=types.GenerateContentConfig(temperature=0.1),
        )

        transcript = response.text.strip()

        if state.raw_text:
            combined = f"{state.raw_text}\n\n[Voice Transcript]\n{transcript}"
        else:
            combined = transcript

        return state.model_copy(update={"raw_text": combined})

    except Exception as e:
        return state.model_copy(update={"error": f"speech_processing_agent: {e}"})
