import base64
import logging
from functools import lru_cache
from openai import APIError, AsyncOpenAI
from app.core.config import settings
from app.core.errors import ExtractionError, extraction_error_from_openai

logger = logging.getLogger(__name__)

_PROVIDER_LABELS = {"gemini": "Gemini", "huggingface": "Hugging Face"}

_PROMPT = """Extract all content from this image precisely.

Rules:
1. Convert every mathematical expression to LaTeX notation:
   - Inline math: $expression$
   - Display/block equations: $$expression$$
2. If the image contains a diagram, chart, graph, or figure, output exactly "[HAS_DIAGRAM]" on the first line
3. Preserve the logical reading order
4. Return only the extracted content, no explanation or commentary"""

_PROVIDER_CONFIG = {
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "api_key": lambda: settings.gemini_api_key,
        "model": lambda: settings.gemini_model,
        "key_env": "GEMINI_API_KEY",
    },
    "huggingface": {
        "base_url": "https://router.huggingface.co/v1",
        "api_key": lambda: settings.huggingface_api_key,
        "model": lambda: settings.huggingface_model,
        "key_env": "HUGGINGFACE_API_KEY",
    },
}


@lru_cache(maxsize=None)
def _client_for(provider: str) -> AsyncOpenAI:
    config = _PROVIDER_CONFIG[provider]
    return AsyncOpenAI(api_key=config["api_key"](), base_url=config["base_url"])


async def extract_from_image(
    image_bytes: bytes, mime_type: str, provider: str = "gemini"
) -> tuple[str, bool]:
    """Returns (extracted_content, has_diagram)."""
    if provider not in _PROVIDER_CONFIG:
        raise ValueError(f"Unknown extraction provider: {provider}")
    config = _PROVIDER_CONFIG[provider]
    if not config["api_key"]():
        logger.error("Extraction provider %r selected but %s is not set", provider, config["key_env"])
        raise ExtractionError(
            f"The {_PROVIDER_LABELS.get(provider, provider)} extraction provider isn't configured. "
            f"Set {config['key_env']} in .env."
        )
    client = _client_for(provider)
    model = config["model"]()

    b64 = base64.b64encode(image_bytes).decode()
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime_type};base64,{b64}"},
                        },
                        {"type": "text", "text": _PROMPT},
                    ],
                }
            ],
        )
    except APIError as e:
        logger.error("Extraction failed (provider=%s, model=%s): %s", provider, model, e)
        raise extraction_error_from_openai(e, provider) from e
    raw = response.choices[0].message.content or ""
    has_diagram = "[HAS_DIAGRAM]" in raw
    content = raw.replace("[HAS_DIAGRAM]", "").strip()
    return content, has_diagram
