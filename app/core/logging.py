import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings

request_logger = logging.getLogger("request")


def configure_logging() -> None:
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, env_name: str) -> None:
        super().__init__(app)
        self.env_name = env_name.upper()

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_logger.info("START | %s | %s | %s", self.env_name, request.method, request.url.path)

        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        request_logger.info(
            "FINISHED | %s | %s | Status: %s | Duration: %.2fms",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response
