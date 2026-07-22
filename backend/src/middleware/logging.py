"""Logging middleware — logs method, path, status code, and duration."""

import logging
import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("polis.api")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs every request: method, path, status, and duration."""

    async def dispatch(self, request: Request, call_next):
        start = time.monotonic()

        response: Response = await call_next(request)

        duration = time.monotonic() - start
        logger.info(
            "%s %s %d %.4fms",
            request.method,
            request.url.path,
            response.status_code,
            duration * 1000,
        )
        return response
