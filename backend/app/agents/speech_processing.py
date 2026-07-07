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

MAX_FILE_BYTES = 50 * 1024 * 1024      # 50 MB hard reject
INLINE_LIMIT_BYTES = 20 * 1024 * 1024  # ≤20 MB sent inline (no File API needed)

AUDIO_MIME = {
    ".mp3":  "audio/mpeg",
    ".mpeg": "audio/mpeg",
    ".mpga": "audio/mpeg",
    ".wav":  "audio/wav",
    ".m4a":  "audio/mp4",
    ".ogg":  "audio/ogg",
    ".oga":  "audio/ogg",
    ".opus": "audio/opus",
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
        model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-3.5-flash"))
        size = os.path.getsize(file_path)

        if size <= INLINE_LIMIT_BYTES:
            # INLINE path (preferred): sends bytes directly with the request.
            # The File API path below goes through Google's discovery endpoint,
            # which rejects some API key formats with API_KEY_INVALID even when
            # the same key works fine for generate_content.
            audio_blob = {"mime_type": AUDIO_MIME[ext],
                          "data": Path(file_path).read_bytes()}
            response = model.generate_content([audio_blob, _TRANSCRIBE_PROMPT])
            transcript = response.text.strip()
            return {"raw_text": transcript, "audio_url": audio_url}

        # LARGE-FILE path (> 20 MB): requires the Gemini File API.
        audio_file = genai.upload_file(path=file_path, mime_type=AUDIO_MIME[ext])
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

        response = model.generate_content([audio_file, _TRANSCRIBE_PROMPT])
        transcript = response.text.strip()
        genai.delete_file(audio_file.name)
        return {"raw_text": transcript, "audio_url": audio_url}

    except Exception as e:
        return {
            "raw_text": "",
            "audio_url": audio_url,
            "error": f"Speech processing failed: {str(e)}",
        }
