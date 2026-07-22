"""Pydantic schemas for the auth module."""

from datetime import datetime

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    tenant_name: str


class RefreshRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class UserOut(BaseModel):
    id: str
    tenant_id: str
    name: str
    email: str
    phone: str | None = None
    is_active: bool = True
    is_admin: bool = False
    role_id: str | None = None
    avatar_url: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class TenantOut(BaseModel):
    id: str
    name: str
    document: str | None = None
    type: str | None = None
    city: str | None = None
    state: str | None = None
    domain: str | None = None
    logo: str | None = None
    colors: dict | None = None
    settings: dict | None = None
    is_active: bool = True
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut
    tenant: TenantOut
