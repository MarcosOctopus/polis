"""Pydantic schemas for the audit module."""

from datetime import datetime

from pydantic import BaseModel


class AuditLogCreate(BaseModel):
    tenant_id: str | None = None
    user_id: str | None = None
    action: str
    entity: str | None = None
    entity_id: str | None = None
    description: str | None = None
    metadata: dict | None = None
    ip_address: str | None = None
    user_agent: str | None = None


class AuditLogResponse(BaseModel):
    id: str
    tenant_id: str | None = None
    user_id: str | None = None
    action: str
    entity: str | None = None
    entity_id: str | None = None
    description: str | None = None
    metadata: dict | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class AuditLogFilter(BaseModel):
    tenant_id: str | None = None
    user_id: str | None = None
    action: str | None = None
    entity: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    skip: int = 0
    limit: int = 100
