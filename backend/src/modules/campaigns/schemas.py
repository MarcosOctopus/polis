"""Pydantic schemas for the campaigns module."""

from datetime import datetime

from pydantic import BaseModel, Field


class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    channel_id: str | None = None
    segments: dict | None = Field(
        None, description="Contact filter criteria: {'tags': ['tag1'], 'city': 'SP'}"
    )
    message_template: dict | None = Field(
        None,
        description="Message content template: {'type': 'text', 'text': '...'} or {'type': 'template', 'template_name': '...', 'params': {...}}",
    )
    scheduled_at: datetime | None = None
    metadata: dict | None = None


class CampaignUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    channel_id: str | None = None
    segments: dict | None = None
    message_template: dict | None = None
    scheduled_at: datetime | None = None
    metadata: dict | None = None


class CampaignResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    description: str | None = None
    channel_id: str | None = None
    status: str = "draft"
    segments: dict | None = None
    message_template: dict | None = None
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    total_contacts: int = 0
    sent_count: int = 0
    failed_count: int = 0
    metadata: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class CampaignList(BaseModel):
    items: list[CampaignResponse]
    total: int
    skip: int
    limit: int
