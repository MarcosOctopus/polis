"""Pydantic schemas for the messages module."""

from datetime import datetime

from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    conversation_id: str = Field(..., min_length=1)
    channel_id: str | None = None
    direction: str = "outbound"
    message_type: str = "text"
    content: dict = Field(..., description="Message content, e.g. {'text': 'Hello'}")
    provider_message_id: str | None = None


class MessageResponse(BaseModel):
    id: str
    tenant_id: str
    conversation_id: str
    channel_id: str | None = None
    direction: str
    message_type: str = "text"
    content: dict
    provider_message_id: str | None = None
    provider_status: str | None = None
    is_read: bool = False
    read_at: datetime | None = None
    metadata: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class MessageList(BaseModel):
    items: list[MessageResponse]
    total: int
    skip: int
    limit: int
