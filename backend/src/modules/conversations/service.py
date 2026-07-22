"""Conversation service — CRUD with filtering by contact/status/assignee."""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Conversation
from src.modules.conversations.schemas import ConversationCreate, ConversationUpdate


class ConversationService:
    """Business logic for conversation management."""

    @staticmethod
    async def create(
        db: AsyncSession, tenant_id: str, data: ConversationCreate
    ) -> Conversation:
        conversation = Conversation(
            tenant_id=tenant_id,
            contact_id=data.contact_id,
            channel_id=data.channel_id,
            subject=data.subject,
            status=data.status or "active",
            metadata=data.metadata,
        )
        db.add(conversation)
        await db.flush()
        await db.refresh(conversation)
        return conversation

    @staticmethod
    async def get_by_id(
        db: AsyncSession, conversation_id: str, tenant_id: str | None = None
    ) -> Conversation | None:
        query = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.deleted_at.is_(None),
        )
        if tenant_id:
            query = query.where(Conversation.tenant_id == tenant_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_tenant(
        db: AsyncSession,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
        contact_id: str | None = None,
        assigned_to: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> tuple[list[Conversation], int]:
        query = select(Conversation).where(
            Conversation.tenant_id == tenant_id,
            Conversation.deleted_at.is_(None),
        )

        if status:
            query = query.where(Conversation.status == status)
        if contact_id:
            query = query.where(Conversation.contact_id == contact_id)
        if assigned_to:
            query = query.where(Conversation.assigned_to == assigned_to)
        if date_from:
            query = query.where(Conversation.created_at >= date_from)
        if date_to:
            query = query.where(Conversation.created_at <= date_to)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Conversation.updated_at.desc().nulls_last()).offset(skip).limit(limit)
        result = await db.execute(query)
        conversations = list(result.scalars().all())
        return conversations, total

    @staticmethod
    async def update(
        db: AsyncSession,
        conversation_id: str,
        data: ConversationUpdate,
        tenant_id: str | None = None,
    ) -> Conversation | None:
        conversation = await ConversationService.get_by_id(db, conversation_id, tenant_id)
        if conversation is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(conversation, key, value)

        await db.flush()
        await db.refresh(conversation)
        return conversation

    @staticmethod
    async def assign(
        db: AsyncSession,
        conversation_id: str,
        user_id: str,
        tenant_id: str | None = None,
    ) -> Conversation | None:
        conversation = await ConversationService.get_by_id(db, conversation_id, tenant_id)
        if conversation is None:
            return None

        conversation.assigned_to = user_id
        await db.flush()
        await db.refresh(conversation)
        return conversation

    @staticmethod
    async def unassign(
        db: AsyncSession,
        conversation_id: str,
        tenant_id: str | None = None,
    ) -> Conversation | None:
        conversation = await ConversationService.get_by_id(db, conversation_id, tenant_id)
        if conversation is None:
            return None

        conversation.assigned_to = None
        await db.flush()
        await db.refresh(conversation)
        return conversation

    @staticmethod
    async def soft_delete(
        db: AsyncSession, conversation_id: str, tenant_id: str | None = None
    ) -> bool:
        conversation = await ConversationService.get_by_id(db, conversation_id, tenant_id)
        if conversation is None:
            return False

        conversation.deleted_at = datetime.now(timezone.utc)
        await db.flush()
        return True
