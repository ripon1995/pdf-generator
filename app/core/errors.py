import re


class ExtractionError(Exception):
    """Raised when the Gemini vision API call fails, with a user-facing message."""

    def __init__(self, message: str, *, retry_after_seconds: float | None = None):
        super().__init__(message)
        self.message = message
        self.retry_after_seconds = retry_after_seconds


def _parse_retry_after_seconds(exc: Exception) -> float | None:
    match = re.search(r"retryDelay['\"]?\s*:\s*['\"]?(\d+(?:\.\d+)?)s", str(exc))
    return float(match.group(1)) if match else None


def extraction_error_from_openai(exc: Exception) -> ExtractionError:
    """Maps an openai SDK exception (raised by the Gemini-compatible endpoint) to an ExtractionError."""
    from openai import AuthenticationError, RateLimitError

    if isinstance(exc, RateLimitError):
        retry_after = _parse_retry_after_seconds(exc)
        wait_hint = f" Please wait about {int(retry_after)}s and try again." if retry_after else " Please wait a moment and try again."
        return ExtractionError(
            "The AI extraction service has hit its usage quota (Gemini free tier limit)." + wait_hint,
            retry_after_seconds=retry_after,
        )
    if isinstance(exc, AuthenticationError):
        return ExtractionError(
            "The AI extraction service rejected our API key. Check the GEMINI_API_KEY configuration."
        )
    return ExtractionError(
        "The AI extraction service failed unexpectedly. Please try again in a moment."
    )
