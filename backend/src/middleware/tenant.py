"""Tenant middleware — extracts X-Tenant-ID header and injects into request.state."""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class TenantMiddleware(BaseHTTPMiddleware):
    """Middleware that reads the X-Tenant-ID header and sets
    request.state.tenant_id for downstream use.
    Does NOT block requests without the header — use FastAPI dependencies
    when a tenant is required.
    """

    async def dispatch(self, request: Request, call_next):
        request.state.tenant_id = request.headers.get("X-Tenant-ID")
        response: Response = await call_next(request)
        return response
