from pathlib import Path
from typing import Tuple

from google.genai import types as genai_types
from google.genai import errors as genai_errors

from app.services.gemini_client import get_gemini_client, GeminiUnavailable
from app.models import MeetingAudio, MeetingStatus
from app import crud

GEMINI_MODEL = "gemini-3.0-flash"


async def transcribe_and_summarize(session, meeting: MeetingAudio) -> Tuple[str, str, list[str]]:
    """
    Transcribe audio and return (transcript, summary, action_items).
    Raises GeminiUnavailable or genai_errors on failure.
    """
    client = get_gemini_client()
    path = Path(meeting.file_path)
    if not path.exists():
        raise FileNotFoundError("Audio file not found")

    audio_bytes = path.read_bytes()
    prompt = (
        "Transcribe el audio en español (o detecta idioma). "
        "Incluye timestamps en formato [MM:SS]. Luego genera un resumen breve (3-5 bullets) "
        "y una lista de action items concretos (viñetas)."
    )

    result = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[
            genai_types.Part.from_bytes(
                data=audio_bytes,
                mime_type=_guess_mime(path.suffix),
            ),
            prompt,
        ],
    )
    transcript = result.text or ""
    summary = ""
    action_items: list[str] = []

    # Simple parsing: split by sections if model returns markdown
    if "Resumen" in transcript:
        summary = transcript
    else:
        summary = transcript[:500]  # fallback

    # Action items heuristic: lines starting with "-" or "•"
    for line in transcript.splitlines():
        line_stripped = line.strip()
        if line_stripped.startswith(("-", "•", "*")):
            action_items.append(line_stripped.lstrip("-•* ").strip())

    return transcript, summary, action_items


def _guess_mime(ext: str) -> str:
    ext = ext.lower()
    if ext in {".wav"}:
        return "audio/wav"
    if ext in {".mp3"}:
        return "audio/mpeg"
    if ext in {".m4a"}:
        return "audio/mp4"
    if ext in {".webm"}:
        return "audio/webm"
    return "application/octet-stream"
