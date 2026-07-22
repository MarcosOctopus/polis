"""Pydantic schemas for the knowledge module."""

from datetime import datetime

from pydantic import BaseModel, Field


class KnowledgeBaseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    content: str | None = None


class KnowledgeBaseUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    content: str | None = None


class KnowledgeBaseResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    description: str | None = None
    content: str | None = None
    metadata: dict | None = None
    embedding: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class KnowledgeBaseList(BaseModel):
    items: list[KnowledgeBaseResponse]
    total: int
    skip: int
    limit: int
