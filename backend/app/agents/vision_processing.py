"""
Vision Processing Agent
-----------------------
Runs when input_type == "image" or "video".

IMAGE path: base64-encode → Gemini Vision → structured complaint text
VIDEO path: Gemini File API upload → analyze BOTH visual frames AND audio
            track → structured complaint text

In both cases the result is written into state.raw_text so the rest of
the pipeline (Citizen Intelligence → ... → Explainability) runs unchanged.

Hard constraints
----------------
- Files > 50 MB are hard-rejected before any API call.
- Supported image formats : jpg, jpeg, png, webp
- Supported video formats : mp4, mov, avi, mkv, webm
- The output prompt is fully deterministic — fixed sections, no freeform.
- Gemini File API uploads are always deleted after use.
"""

import base64
import os
import time
from pathlib import Path

import google.generativeai as genai
from langchain_core.messages import HumanMessage

from app.schemas.models import AgentState

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_FILE_BYTES = 50 * 1024 * 1024  # 50 MB hard limit

IMAGE_MIME = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}

VIDEO_MIME = {
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".avi": "video/x-msvideo",
    ".mkv": "video/x-matroska",
    ".webm": "video/webm",
}

# Deterministic structured prompt — same sections every time
_IMAGE_PROMPT = (
    "Analyze this photo submitted by a citizen to their Member of Parliament in India.\n\n"
    "Return ONLY the following three lines — no markdown, no headers, no extra text:\n\n"
    "VISUAL: [2-3 sentences describing exactly what infrastructure problem is visible. "
    "Reference specific objects, damage, or conditions you can see. "
    "Do NOT speculate about anything not visible in the image.]\n\n"
    "LOCATION: [Any visible location clues — signboards, landmarks, road names. "
    "Write 'No location clues visible' if none.]\n\n"
    "COMPLAINT: [One sentence written as the citizen's own words describing their request to the MP.]"
)

_VIDEO_PROMPT = (
    "Analyze this video submitted by a citizen to their Member of Parliament in India. "
    "The video may contain both visual footage and spoken audio.\n\n"
    "Return ONLY the following four lines — no markdown, no headers, no extra text:\n\n"
    "VISUAL: [2-3 sentences describing exactly what infrastructure problem is visible in the footage. "
    "Reference specific objects, damage, or conditions. "
    "Do NOT speculate about anything not visible.]\n\n"
    "AUDIO: [Exact transcription of everything spoken in the video. "
    "If no speech is audible write: No speech detected. "
    "Do NOT paraphrase — use the speaker's exact words.]\n\n"
    "LOCATION: [Any visible or spoken location clues — signboards, landmarks, road names, area names. "
    "Write 'No location clues' if none.]\n\n"
    "COMPLAINT: [One sentence combining visual evidence and spoken audio into the citizen's complaint, "
    "written as if the citizen themselves wrote it to the MP.]"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _file_size_ok(path: str) -> bool:
    return os.path.getsize(path) <= MAX_FILE_BYTES


def _process_image(file_path: str) -> str:
    """Inline base64 → Gemini Vision → raw complaint text."""
    ext = Path(file_path).suffix.lower()
    mime_type = IMAGE_MIME.get(ext, "image/jpeg")

    image_bytes = Path(file_path).read_bytes()
    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")

    from app.core.llm import get_model
    model = get_model()

    message = HumanMessage(content=[
        {"type": "text", "text": _IMAGE_PROMPT},
        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64}"}},
    ])
    response = model.invoke([message])
    return response.content if hasattr(response, "content") else str(response)


def _process_video(file_path: str) -> str:
    """Gemini File API upload → visual + audio analysis → raw complaint text."""
    ext = Path(file_path).suffix.lower()
    mime_type = VIDEO_MIME.get(ext, "video/mp4")

    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    # Upload
    video_file = genai.upload_file(path=file_path, mime_type=mime_type)

    # Wait for Gemini to finish processing (max 90 s)
    max_wait = 90
    waited = 0
    while video_file.state.name == "PROCESSING" and waited < max_wait:
        time.sleep(3)
        waited += 3
        video_file = genai.get_file(video_file.name)

    if video_file.state.name != "ACTIVE":
        genai.delete_file(video_file.name)
        raise RuntimeError(f"Gemini file processing ended in state: {video_file.state.name}")

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content([video_file, _VIDEO_PROMPT])
        return response.text
    finally:
        # Always clean up uploaded file — no stale data left in Gemini
        genai.delete_file(video_file.name)


def _build_fallback(input_type: str) -> str:
    kind = "video" if input_type == "video" else "photo"
    return f"A citizen submitted a {kind} showing a civic infrastructure problem."


# ---------------------------------------------------------------------------
# LangGraph node entry point
# ---------------------------------------------------------------------------

def run(state: AgentState) -> dict:
    file_path = state.media_file_path
    input_type = state.input_type  # "image" or "video"

    # Guard: no file provided
    if not file_path or not Path(file_path).exists():
        return {
            "raw_text": _build_fallback(input_type),
            "error": f"Media file not found: {file_path}",
        }

    # Guard: file too large (hard reject)
    if not _file_size_ok(file_path):
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        return {
            "raw_text": _build_fallback(input_type),
            "error": f"File rejected: {size_mb:.1f} MB exceeds the 50 MB limit.",
        }

    ext = Path(file_path).suffix.lower()

    # Guard: unsupported format
    if input_type == "image" and ext not in IMAGE_MIME:
        return {
            "raw_text": _build_fallback(input_type),
            "error": f"Unsupported image format: {ext}. Supported: {list(IMAGE_MIME)}",
        }
    if input_type == "video" and ext not in VIDEO_MIME:
        return {
            "raw_text": _build_fallback(input_type),
            "error": f"Unsupported video format: {ext}. Supported: {list(VIDEO_MIME)}",
        }

    try:
        if input_type == "video":
            raw = _process_video(file_path)
        else:
            raw = _process_image(file_path)

        return {"raw_text": raw.strip()}

    except Exception as e:
        return {
            "raw_text": _build_fallback(input_type),
            "error": f"Vision processing failed: {str(e)}",
        }
