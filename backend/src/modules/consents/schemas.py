"""Pydantic schemas for the consents module."""

from datetime import datetime

from pydantic import BaseModel, Field


class ConsentCreate(BaseModel):
    contact_id: str = Field(..., min_length=1)
    channel: str = Field(..., pattern=r"^(whatsapp|sms|email)$")
    status: str = Field("granted", pattern=r"^(granted|denied|pending)$")
    source: str | None = Field(None, max_length=50)


class ConsentUpdate(BaseModel):
    status: str = Field(..., pattern=r"^(granted|denied|pending)$")
    source: str | None = Field(None, max_length=50)


class ConsentOut(BaseModel):
    id: str
    tenant_id: str
    contact_id: str
    channel: str
    status: str
    source: str | None = None
    granted_at: datetime | None = None
    denied_at: datetime | None = None
    expires_at: datetime | None = None
    metadata_: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class BulkConsentRequest(BaseModel):
    contact_ids: list[str] = Field(..., min_length=1)
    channel: str = Field(..., pattern=r"^(whatsapp|sms|email)$")
    status: str = Field("granted", pattern=r"^(granted|denied|pending)$")
    source: str | None = Field(None, max_length=50)


class ConsentCheckResponse(BaseModel):
    consent_id: str | None = None
    contact_id: str
    channel: str
    has_consent: bool = False
    status: str | None = None


class PaginatedConsents(BaseModel):
    items: list[ConsentOut]
    total: int
    skip: int
    limit: int
