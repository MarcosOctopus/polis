"""Pydantic schemas for the agents module."""

from datetime import datetime

from pydantic import BaseModel, Field


class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    model: str = Field(..., min_length=1, max_length=100)
    system_prompt: str | None = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    config: dict | None = None


class AgentUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    model: str | None = Field(None, min_length=1, max_length=100)
    system_prompt: str | None = None
    temperature: float | None = Field(None, ge=0.0, le=2.0)
    config: dict | None = None
    is_active: bool | None = None


class AgentResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    description: str | None = None
    model: str
    system_prompt: str | None = None
    temperature: float = 0.7
    config: dict | None = None
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class AgentList(BaseModel):
    items: list[AgentResponse]
    total: int
    skip: int
    limit: int
