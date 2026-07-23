"""Pydantic schemas for the templates module."""

from datetime import datetime

from pydantic import BaseModel, Field


class TemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    channel: str = Field(..., pattern=r"^(whatsapp|sms|email)$")
    message_type: str = Field("text", pattern=r"^(text|html|template)$")
    subject: str | None = Field(None, max_length=500)
    body: str = Field(..., min_length=1)
    variables: list[str] | None = None
    category: str | None = Field(None, max_length=100)
    tone: str | None = Field(None, max_length=50)


class TemplateUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    channel: str | None = Field(None, pattern=r"^(whatsapp|sms|email)$")
    message_type: str | None = Field(None, pattern=r"^(text|html|template)$")
    subject: str | None = Field(None, max_length=500)
    body: str | None = Field(None, min_length=1)
    variables: list[str] | None = None
    category: str | None = Field(None, max_length=100)
    tone: str | None = Field(None, max_length=50)
    is_active: bool | None = None


class TemplateOut(BaseModel):
    id: str
    tenant_id: str
    name: str
    channel: str
    message_type: str
    subject: str | None = None
    body: str
    variables: list[str] | None = None
    category: str | None = None
    tone: str | None = None
    is_active: bool = True
    created_by: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class TemplateRenderRequest(BaseModel):
    template_id: str | None = None
    variables: dict[str, str] = Field(default_factory=dict)


class TemplateRenderResponse(BaseModel):
    rendered_body: str
    rendered_subject: str | None = None


class PaginatedTemplates(BaseModel):
    items: list[TemplateOut]
    total: int
    skip: int
    limit: int
