"""Pydantic schemas for the conversations module."""

from datetime import datetime

from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    contact_id: str = Field(..., min_length=1)
    channel_id: str | None = None
    subject: str | None = Field(None, max_length=500)
    status: str | None = "active"
    metadata: dict | None = None


class ConversationUpdate(BaseModel):
    subject: str | None = Field(None, max_length=500)
    status: str | None = None
    metadata: dict | None = None


class MessageInConversation(BaseModel):
    id: str
    direction: str
    message_type: str = "text"
    content: dict
    provider_message_id: str | None = None
    provider_status: str | None = None
    is_read: bool = False
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    id: str
    tenant_id: str
    contact_id: str
    channel_id: str | None = None
    assigned_to: str | None = None
    status: str = "active"
    subject: str | None = None
    metadata: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ConversationList(BaseModel):
    items: list[ConversationResponse]
    total: int
    skip: int
    limit: int


class AssignConversationRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
