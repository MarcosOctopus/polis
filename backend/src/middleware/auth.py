"""JWT Auth middleware — optional Bearer token extraction for non-FastAPI contexts.

Note: In this project, JWT validation is handled via FastAPI dependencies
(auth/dependencies.py). This middleware is provided as a Starlette-compatible
alternative for use with other ASGI frameworks or as an extra security layer.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.utils.security import decode_token


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware that decodes JWT from the Authorization header
    and attaches the user payload to request.state if valid.
    Does NOT block unauthenticated requests — use FastAPI dependencies
    for protected endpoints.
    """

    async def dispatch(self, request: Request, call_next):
        request.state.user = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.removeprefix("Bearer ")
            payload = decode_token(token)
            if payload is not None and payload.get("type") == "access":
                request.state.user = payload

        response: Response = await call_next(request)
        return response
