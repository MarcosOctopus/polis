"""Polis API — FastAPI application entry point."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import settings
from src.middleware.auth import AuthMiddleware
from src.middleware.logging import LoggingMiddleware
from src.middleware.tenant import TenantMiddleware
from src.modules.auth.router import router as auth_router
from src.modules.tenants.router import router as tenants_router
from src.modules.users.router import router as users_router
from src.modules.audit.router import router as audit_router
from src.modules.contacts.router import router as contacts_router
from src.modules.conversations.router import router as conversations_router
from src.modules.messages.router import router as messages_router
from src.modules.channels.router import router as channels_router
from src.modules.campaigns.router import router as campaigns_router
from src.modules.agents.router import router as agents_router
from src.modules.knowledge.router import router as knowledge_router
from src.modules.territorial.router import router as territorial_router
from src.modules.protocols.router import router as protocols_router
from src.modules.tasks.router import router as tasks_router
from src.modules.dashboard.router import router as dashboard_router

# ── Logging ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# ── Application ──────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

# ── Middleware (order matters: last added = first executed) ──────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TenantMiddleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(LoggingMiddleware)

# ── Routers ──────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(tenants_router)
app.include_router(users_router)
app.include_router(audit_router)
app.include_router(contacts_router)
app.include_router(conversations_router)
app.include_router(messages_router)
app.include_router(channels_router)
app.include_router(campaigns_router)
app.include_router(agents_router)
app.include_router(knowledge_router)
app.include_router(territorial_router)
app.include_router(protocols_router)
app.include_router(tasks_router)
app.include_router(dashboard_router)


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "version": settings.app_version}
