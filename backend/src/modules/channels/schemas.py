"""Pydantic schemas for the channels module."""

from datetime import datetime

from pydantic import BaseModel, Field


class ChannelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    provider: str = Field(..., description="Provider type: whatsapp, email, sms")
    channel_type: str = Field(..., description="Channel type name")
    credentials: dict = Field(
        ..., description="Provider credentials (will be encrypted at rest)"
    )
    config: dict | None = None


class ChannelUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    credentials: dict | None = None
    config: dict | None = None
    is_active: bool | None = None


class ChannelResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    provider: str
    channel_type: str
    config: dict | None = None
    is_active: bool = True
    webhook_url: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ChannelList(BaseModel):
    items: list[ChannelResponse]
    total: int
    skip: int
    limit: int


class TestConnectionResponse(BaseModel):
    success: bool
    message: str


class WebhookUrlResponse(BaseModel):
    webhook_url: str
    webhook_secret: str | None = None
