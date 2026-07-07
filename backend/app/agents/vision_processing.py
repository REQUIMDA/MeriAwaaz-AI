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

MAX_FILE_BYTES = 50 * 1024 * 1024      # 50 MB hard limit
INLINE_LIMIT_BYTES = 20 * 1024 * 1024  # ≤20 MB sent inline (no File API needed)

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

# Deterministic structured prompts — same sections every time. Deep analysis:
# the downstream agents can only be as specific as what we extract here.
_CATEGORIES_HINT = ("Education | Healthcare | Roads | Water | Sanitation | "
                    "Electricity | Vocational | Other")

_IMAGE_PROMPT = (
    "You are analyzing a photo submitted by a citizen to their Member of Parliament in India. "
    "Your analysis is the ONLY thing downstream systems will see of this image, so be thorough "
    "and concrete. Describe only what is actually visible — never invent details.\n\n"
    "Return ONLY the following sections, exactly these labels, no markdown, no extra text:\n\n"
    "PROBLEM: [Name the specific infrastructure problem in a few words, "
    "e.g. 'large water-filled pothole in asphalt road', 'broken handpump', "
    "'overflowing open drain'.]\n\n"
    "VISUAL_DETAILS: [3-5 sentences of thorough description: what objects/damage are visible, "
    "approximate size/extent/count (e.g. 'pothole roughly 1 metre wide', 'cracks radiating 2-3 metres'), "
    "the condition of surrounding infrastructure, and any visible context (traffic, houses, people).]\n\n"
    "SEVERITY_INDICATORS: [Concrete visual evidence of risk or impact: standing water, exposed rebar, "
    "depth, proximity to a school/homes/traffic, signs the damage is old or worsening. "
    "Write 'None visible' if none.]\n\n"
    "LOCATION_CLUES: [Signboards, shop names, landmarks, road markings, vehicle plates, terrain. "
    "Write 'No location clues visible' if none.]\n\n"
    f"SUGGESTED_CATEGORY: [One of: {_CATEGORIES_HINT} — based on what is VISIBLE.]\n\n"
    "COMPLAINT: [1-2 sentences in the citizen's voice, naming the specific problem and its impact, "
    "as a request to the MP.]"
)

_VIDEO_PROMPT = (
    "You are analyzing a video submitted by a citizen to their Member of Parliament in India. "
    "The video may contain both visual footage and spoken audio. Your analysis is the ONLY thing "
    "downstream systems will see of this video, so be thorough and concrete. "
    "Describe only what is actually visible/audible — never invent details.\n\n"
    "Return ONLY the following sections, exactly these labels, no markdown, no extra text:\n\n"
    "PROBLEM: [Name the specific infrastructure problem shown in a few words.]\n\n"
    "VISUAL_DETAILS: [3-5 sentences: what the footage shows across its duration, specific damage/"
    "conditions, approximate extent/count/size, surroundings, people or vehicles affected.]\n\n"
    "AUDIO_TRANSCRIPT: [Exact transcription of everything spoken, in the original language "
    "(native script if Hindi/Marathi/etc.). Write 'No speech detected' if silent. "
    "Do NOT paraphrase — use the speaker's exact words.]\n\n"
    "SEVERITY_INDICATORS: [Concrete evidence of risk or impact seen or spoken: injuries mentioned, "
    "depth of damage, proximity to homes/school/traffic, duration of the problem if stated. "
    "Write 'None' if none.]\n\n"
    "LOCATION_CLUES: [Visible or spoken location references — signboards, landmarks, village/ward names. "
    "Write 'No location clues' if none.]\n\n"
    f"SUGGESTED_CATEGORY: [One of: {_CATEGORIES_HINT} — based on what is shown/said.]\n\n"
    "COMPLAINT: [1-2 sentences combining visual and audio evidence into the citizen's complaint, "
    "in the citizen's voice, naming the specific problem.]"
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
    from app.core.llm import content_to_text
    return content_to_text(getattr(response, "content", response))


def _process_video(file_path: str) -> str:
    """Video → visual + audio analysis → raw complaint text.

    ≤20 MB: bytes sent INLINE with the request (preferred — the File API's
    discovery endpoint rejects some API key formats with API_KEY_INVALID even
    when the same key works for generate_content).
    >20 MB: Gemini File API upload."""
    ext = Path(file_path).suffix.lower()
    mime_type = VIDEO_MIME.get(ext, "video/mp4")

    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-3.5-flash"))

    if os.path.getsize(file_path) <= INLINE_LIMIT_BYTES:
        video_blob = {"mime_type": mime_type, "data": Path(file_path).read_bytes()}
        response = model.generate_content([video_blob, _VIDEO_PROMPT])
        return response.text

    # Large file — File API upload
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

        # CRITICAL: keep the citizen's own words. Previously the image
        # analysis REPLACED raw_text, so a caption like "Kesarpur has too
        # many of these" (the only location clue!) was silently discarded.
        citizen_text = (state.raw_text or "").strip()
        if citizen_text:
            combined = (f"CITIZEN'S OWN MESSAGE: {citizen_text}\n\n"
                        f"ANALYSIS OF ATTACHED {input_type.upper()}:\n{raw.strip()}")
        else:
            combined = raw.strip()
        return {"raw_text": combined}

    except Exception as e:
        citizen_text = (state.raw_text or "").strip()
        fallback = _build_fallback(input_type)
        if citizen_text:
            fallback = f"CITIZEN'S OWN MESSAGE: {citizen_text}\n\n{fallback}"
        return {
            "raw_text": fallback,
            "error": f"Vision processing failed: {str(e)}",
        }
