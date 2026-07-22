"""Pydantic schemas for the contacts module."""

from datetime import datetime

from pydantic import BaseModel, Field


class ContactCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=20)
    city: str | None = Field(None, max_length=100)
    state: str | None = Field(None, max_length=50)
    neighborhood: str | None = Field(None, max_length=100)
    address: str | None = Field(None, max_length=500)
    latitude: float | None = None
    longitude: float | None = None
    tags: list[str] | None = None
    metadata: dict | None = None


class ContactUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    email: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=20)
    city: str | None = None
    state: str | None = None
    neighborhood: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    tags: list[str] | None = None
    metadata: dict | None = None
    is_active: bool | None = None


class ContactResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    email: str | None = None
    phone: str | None = None
    city: str | None = None
    state: str | None = None
    neighborhood: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    tags: list[str] | None = None
    metadata: dict | None = None
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ContactList(BaseModel):
    items: list[ContactResponse]
    total: int
    skip: int
    limit: int


class AddTagsRequest(BaseModel):
    tags: list[str] = Field(..., min_length=1)


class RemoveTagsRequest(BaseModel):
    tags: list[str] = Field(..., min_length=1)
