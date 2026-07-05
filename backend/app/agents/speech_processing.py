"""
Speech Processing Agent — P2 stub
----------------------------------
Voice transcription is not implemented for this hackathon submission.
If input_type == "voice", the pipeline routes here first, then continues
to Citizen Intelligence with the raw_text unchanged.
"""

from app.schemas.models import AgentState


def run(state: AgentState) -> dict:
    """LangGraph node entry point. Returns AgentState fields to update."""
    # Voice transcription (Whisper / Gemini Audio) would go here.
    # For now, pass raw_text through unchanged so the pipeline doesn't crash.
    return {}
