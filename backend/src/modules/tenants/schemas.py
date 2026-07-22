"""Pydantic schemas for the tenants module."""

from datetime import datetime

from pydantic import BaseModel


class TenantCreate(BaseModel):
    name: str
    document: str | None = None
    type: str | None = None
    city: str | None = None
    state: str | None = None
    domain: str | None = None


class TenantUpdate(BaseModel):
    name: str | None = None
    logo: str | None = None
    colors: dict | None = None
    settings: dict | None = None
    document: str | None = None
    type: str | None = None
    city: str | None = None
    state: str | None = None
    domain: str | None = None


class TenantResponse(BaseModel):
    id: str
    name: str
    document: str | None = None
    type: str | None = None
    city: str | None = None
    state: str | None = None
    domain: str | None = None
    logo: str | None = None
    colors: dict | None = None
    settings: dict | None = None
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
