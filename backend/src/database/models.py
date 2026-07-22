"""SQLAlchemy models for the Polis backend."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=utcnow
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), default=None
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )


class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    document: Mapped[str | None] = mapped_column(String(20), nullable=True)
    type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    domain: Mapped[str | None] = mapped_column(String(255), nullable=True)
    logo: Mapped[str | None] = mapped_column(String(500), nullable=True)
    colors: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    settings: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    users = relationship("User", back_populates="tenant", lazy="selectin")
    roles = relationship("Role", back_populates="tenant", lazy="selectin")


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("roles.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    metadata_: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    tenant = relationship("Tenant", back_populates="users", lazy="selectin")
    role = relationship("Role", back_populates="users", lazy="selectin")


class Role(Base, TimestampMixin):
    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    permissions: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)

    tenant = relationship("Tenant", back_populates="roles", lazy="selectin")
    users = relationship("User", back_populates="role", lazy="selectin")


class RefreshToken(Base, TimestampMixin):
    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    token: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=True
    )
    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity: Mapped[str | None] = mapped_column(String(100), nullable=True)
    entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)


# ── BATCH 3 Models ──────────────────────────────────────────────────────


class Contact(Base, TimestampMixin):
    __tablename__ = "contacts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    neighborhood: Mapped[str | None] = mapped_column(String(100), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    tenant = relationship("Tenant", lazy="selectin")


class Channel(Base, TimestampMixin):
    __tablename__ = "channels"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # whatsapp, email, sms
    channel_type: Mapped[str] = mapped_column(String(50), nullable=False)  # type alias
    credentials: Mapped[dict] = mapped_column(JSON, nullable=False)  # encrypted
    config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    webhook_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    webhook_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)

    tenant = relationship("Tenant", lazy="selectin")


class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=False, index=True
    )
    contact_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("contacts.id"), nullable=False, index=True
    )
    channel_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("channels.id"), nullable=True
    )
    assigned_to: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default="active", index=True
    )  # active, waiting, closed
    subject: Mapped[str | None] = mapped_column(String(500), nullable=True)
    metadata_: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    tenant = relationship("Tenant", lazy="selectin")
    contact = relationship("Contact", lazy="selectin")
    channel = relationship("Channel", lazy="selectin")
    assignee = relationship("User", lazy="selectin", foreign_keys=[assigned_to])


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=False, index=True
    )
    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversations.id"), nullable=False, index=True
    )
    channel_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("channels.id"), nullable=True
    )
    direction: Mapped[str] = mapped_column(
        String(10), nullable=False
    )  # inbound, outbound
    message_type: Mapped[str] = mapped_column(
        String(20), default="text"
    )  # text, media, template
    content: Mapped[dict] = mapped_column(JSON, nullable=False)
    provider_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    provider_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    metadata_: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    tenant = relationship("Tenant", lazy="selectin")
    conversation = relationship("Conversation", lazy="selectin")
    channel = relationship("Channel", lazy="selectin")


class Campaign(Base, TimestampMixin):
    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    channel_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("channels.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default="draft", index=True
    )  # draft, scheduled, sending, paused, completed, cancelled
    segments: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )  # filter criteria for contacts
    message_template: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )  # message content template
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    total_contacts: Mapped[int] = mapped_column(Integer, default=0)
    sent_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    metadata_: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    tenant = relationship("Tenant", lazy="selectin")
    channel = relationship("Channel", lazy="selectin")


class Protocol(Base, TimestampMixin):
    __tablename__ = "protocols"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=False, index=True
    )
    contact_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("contacts.id"), nullable=True
    )
    number: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    event: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default="open", index=True
    )  # open, in_progress, closed, cancelled
    metadata_: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    tenant = relationship("Tenant", lazy="selectin")
    contact = relationship("Contact", lazy="selectin")


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    assignee_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default="todo", index=True
    )  # todo, in_progress, done, blocked
    priority: Mapped[str] = mapped_column(
        String(10), default="medium"
    )  # low, medium, high, urgent
    deadline: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    event_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    protocol_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("protocols.id"), nullable=True
    )
    order: Mapped[int] = mapped_column(Integer, default=0)
    metadata_: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    tenant = relationship("Tenant", lazy="selectin")
    assignee = relationship("User", lazy="selectin", foreign_keys=[assignee_id])
    protocol = relationship("Protocol", lazy="selectin")


# ── BATCH 4: Agents, Knowledge, Territorial ──────────────────────────────


class Agent(Base, TimestampMixin):
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    tenant = relationship("Tenant", lazy="selectin")


class KnowledgeBase(Base, TimestampMixin):
    __tablename__ = "knowledge_bases"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    embedding: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    tenant = relationship("Tenant", lazy="selectin")


class TerritorialEvent(Base, TimestampMixin):
    __tablename__ = "territorial_events"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    severity: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    occurred_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    metadata_: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    tenant = relationship("Tenant", lazy="selectin")
