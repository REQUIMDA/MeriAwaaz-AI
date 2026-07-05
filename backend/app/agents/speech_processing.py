"""
Speech Processing Agent
-----------------------
Runs when input_type == "voice".

Uploads the audio file to the Gemini File API, transcribes it using
Gemini's native audio understanding, then sets:
  - state.raw_text  → exact transcript (passed to Citizen Intelligence Agent)
  - state.audio_url → /uploads/{filename} (returned to frontend for audio widget)

Supported audio formats: mp3, wav, m4a, ogg, flac, aac, webm
Hard limit: 50 MB
"""

import os
import time
from pathlib import Path

import google.generativeai as genai

from app.schemas.models import AgentState

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_FILE_BYTES = 50 * 1024 * 1024  # 50 MB

AUDIO_MIME = {
    ".mp3":  "audio/mpeg",
    ".wav":  "audio/wav",
    ".m4a":  "audio/mp4",
    ".ogg":  "audio/ogg",
    ".flac": "audio/flac",
    ".aac":  "audio/aac",
    ".webm": "audio/webm",
}

# Deterministic transcription prompt — no summarizing, no paraphrasing
_TRANSCRIBE_PROMPT = (
    "Transcribe every word spoken in this audio recording exactly as said. "
    "Do NOT summarize, paraphrase, or add any commentary. "
    "If the speaker is using Hindi, Marathi, or any other Indian language, "
    "transcribe in that language using its native script. "
    "If the audio is silent or unintelligible, write only: [No speech detected]"
)


# ---------------------------------------------------------------------------
# LangGraph node entry point
# ---------------------------------------------------------------------------

def run(state: AgentState) -> dict:
    file_path = state.media_file_path

    # Guard: no file
    if not file_path or not Path(file_path).exists():
        return {
            "raw_text": "",
            "error": f"Audio file not found: {file_path}",
        }

    # Guard: file too large
    if os.path.getsize(file_path) > MAX_FILE_BYTES:
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        return {
            "raw_text": "",
            "error": f"Audio file rejected: {size_mb:.1f} MB exceeds the 50 MB limit.",
        }

    ext = Path(file_path).suffix.lower()

    # Guard: unsupported format
    if ext not in AUDIO_MIME:
        return {
            "raw_text": "",
            "error": f"Unsupported audio format: {ext}. Supported: {list(AUDIO_MIME)}",
        }

    # Build the audio_url for the frontend widget
    filename = Path(file_path).name
    audio_url = f"/uploads/{filename}"

    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

        # Upload to Gemini File API
        audio_file = genai.upload_file(
            path=file_path,
            mime_type=AUDIO_MIME[ext],
        )

        # Wait for processing (max 60 s)
        max_wait = 60
        waited = 0
        while audio_file.state.name == "PROCESSING" and waited < max_wait:
            time.sleep(2)
            waited += 2
            audio_file = genai.get_file(audio_file.name)

        if audio_file.state.name != "ACTIVE":
            genai.delete_file(audio_file.name)
            return {
                "raw_text": "",
                "audio_url": audio_url,
                "error": f"Gemini audio processing failed with state: {audio_file.state.name}",
            }

        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content([audio_file, _TRANSCRIBE_PROMPT])
        transcript = response.text.strip()

        # Clean up
        genai.delete_file(audio_file.name)

        return {
            "raw_text": transcript,
            "audio_url": audio_url,
        }

    except Exception as e:
        return {
            "raw_text": "",
            "audio_url": audio_url,
            "error": f"Speech processing failed: {str(e)}",
        }
