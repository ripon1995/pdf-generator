import base64
from openai import AsyncOpenAI
from app.core.config import settings

_client = AsyncOpenAI(
    api_key=settings.grok_api_key,
    base_url="https://api.x.ai/v1",
)

_PROMPT = """Extract all content from this image precisely.

Rules:
1. Convert every mathematical expression to LaTeX notation:
   - Inline math: $expression$
   - Display/block equations: $$expression$$
2. If the image contains a diagram, chart, graph, or figure, output exactly "[HAS_DIAGRAM]" on the first line
3. Preserve the logical reading order
4. Return only the extracted content, no explanation or commentary"""


async def extract_from_image(image_bytes: bytes, mime_type: str) -> tuple[str, bool]:
    """Returns (extracted_content, has_diagram)."""
    b64 = base64.b64encode(image_bytes).decode()
    response = await _client.chat.completions.create(
        model=settings.grok_model,
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
    raw = response.choices[0].message.content or ""
    has_diagram = "[HAS_DIAGRAM]" in raw
    content = raw.replace("[HAS_DIAGRAM]", "").strip()
    return content, has_diagram
