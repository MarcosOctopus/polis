"""Pydantic schemas for the protocols module."""

from datetime import datetime

from pydantic import BaseModel, Field


class ProtocolCreate(BaseModel):
    contact_id: str | None = None
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    event: str | None = Field(None, max_length=100)
    status: str | None = "open"
    metadata: dict | None = None


class ProtocolUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    event: str | None = None
    status: str | None = None
    contact_id: str | None = None
    metadata: dict | None = None


class ProtocolResponse(BaseModel):
    id: str
    tenant_id: str
    contact_id: str | None = None
    number: str
    title: str
    description: str | None = None
    event: str | None = None
    status: str = "open"
    metadata: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ProtocolList(BaseModel):
    items: list[ProtocolResponse]
    total: int
    skip: int
    limit: int
