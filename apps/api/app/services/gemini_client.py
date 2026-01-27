from functools import lru_cache
from typing import Optional

from google import genai

from app.config import settings


class GeminiUnavailable(Exception):
    """Raised when Gemini API key is missing."""


@lru_cache(maxsize=1)
def get_gemini_client() -> genai.Client:
    api_key: Optional[str] = settings.gemini_api_key
    if not api_key:
        raise GeminiUnavailable("GEMINI_API_KEY no configurada")
    return genai.Client(api_key=api_key)
