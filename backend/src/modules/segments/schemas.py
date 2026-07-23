"""Pydantic schemas for the segments module."""

from datetime import datetime

from pydantic import BaseModel, Field


class SegmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    segment_type: str = Field(
        "manual", pattern=r"^(manual|dynamic|imported|ai_generated|territorial)$"
    )
    filters: dict | None = None
    territorial_event_id: str | None = None
    contact_ids: list[str] | None = None


class SegmentUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    segment_type: str | None = Field(
        None, pattern=r"^(manual|dynamic|imported|ai_generated|territorial)$"
    )
    filters: dict | None = None
    territorial_event_id: str | None = None
    is_active: bool | None = None


class SegmentOut(BaseModel):
    id: str
    tenant_id: str
    name: str
    description: str | None = None
    segment_type: str
    filters: dict | None = None
    territorial_event_id: str | None = None
    is_active: bool = True
    contact_count: int = 0
    created_by: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class SegmentContactOut(BaseModel):
    segment_id: str
    contact_id: str
    added_at: datetime | None = None

    model_config = {"from_attributes": True}


class ContactBasics(BaseModel):
    id: str
    name: str
    email: str | None = None
    phone: str | None = None
    city: str | None = None
    state: str | None = None

    model_config = {"from_attributes": True}


class SegmentContactWithContact(BaseModel):
    segment_id: str
    contact_id: str
    added_at: datetime | None = None
    contact: ContactBasics | None = None


class PaginatedSegments(BaseModel):
    items: list[SegmentOut]
    total: int
    skip: int
    limit: int


class AddContactsRequest(BaseModel):
    contact_ids: list[str] = Field(..., min_length=1)


class PaginatedSegmentContacts(BaseModel):
    items: list[SegmentContactWithContact]
    total: int
    skip: int
    limit: int
