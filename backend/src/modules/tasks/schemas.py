"""Pydantic schemas for the tasks module."""

from datetime import datetime

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    assignee_id: str | None = None
    status: str | None = "todo"
    priority: str | None = "medium"
    deadline: datetime | None = None
    event_id: str | None = None
    protocol_id: str | None = None
    order: int | None = 0
    metadata: dict | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    assignee_id: str | None = None
    status: str | None = None
    priority: str | None = None
    deadline: datetime | None = None
    event_id: str | None = None
    protocol_id: str | None = None
    order: int | None = None
    metadata: dict | None = None


class TaskResponse(BaseModel):
    id: str
    tenant_id: str
    title: str
    description: str | None = None
    assignee_id: str | None = None
    status: str = "todo"
    priority: str = "medium"
    deadline: datetime | None = None
    event_id: str | None = None
    protocol_id: str | None = None
    order: int = 0
    metadata: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class TaskList(BaseModel):
    items: list[TaskResponse]
    total: int
    skip: int
    limit: int


class KanbanColumn(BaseModel):
    status: str
    items: list[TaskResponse]
    count: int


class KanbanBoard(BaseModel):
    columns: list[KanbanColumn]
