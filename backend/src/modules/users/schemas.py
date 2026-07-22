"""Pydantic schemas for the users module."""

from datetime import datetime

from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: str
    phone: str | None = None
    password: str
    role_id: str | None = None


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    role_id: str | None = None
    is_active: bool | None = None
    avatar_url: str | None = None
    metadata: dict | None = None


class UserResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    email: str
    phone: str | None = None
    is_active: bool = True
    is_admin: bool = False
    role_id: str | None = None
    avatar_url: str | None = None
    metadata: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int
    skip: int
    limit: int
