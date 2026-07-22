"""Knowledge service — CRUD with search and soft delete."""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import KnowledgeBase
from src.modules.knowledge.schemas import KnowledgeBaseCreate, KnowledgeBaseUpdate


class KnowledgeService:
    """Business logic for knowledge base management."""

    @staticmethod
    async def create(
        db: AsyncSession, tenant_id: str, data: KnowledgeBaseCreate
    ) -> KnowledgeBase:
        kb = KnowledgeBase(
            tenant_id=tenant_id,
            name=data.name,
            description=data.description,
            content=data.content,
        )
        db.add(kb)
        await db.flush()
        await db.refresh(kb)
        return kb

    @staticmethod
    async def get_by_id(
        db: AsyncSession, kb_id: str, tenant_id: str | None = None
    ) -> KnowledgeBase | None:
        query = select(KnowledgeBase).where(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.deleted_at.is_(None),
        )
        if tenant_id:
            query = query.where(KnowledgeBase.tenant_id == tenant_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_tenant(
        db: AsyncSession,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> tuple[list[KnowledgeBase], int]:
        query = select(KnowledgeBase).where(
            KnowledgeBase.tenant_id == tenant_id,
            KnowledgeBase.deleted_at.is_(None),
        )
        if search:
            query = query.where(
                KnowledgeBase.name.ilike(f"%{search}%")
                | KnowledgeBase.description.ilike(f"%{search}%")
            )

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(KnowledgeBase.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        items = list(result.scalars().all())
        return items, total

    @staticmethod
    async def update(
        db: AsyncSession,
        kb_id: str,
        data: KnowledgeBaseUpdate,
        tenant_id: str | None = None,
    ) -> KnowledgeBase | None:
        kb = await KnowledgeService.get_by_id(db, kb_id, tenant_id)
        if kb is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(kb, key, value)

        await db.flush()
        await db.refresh(kb)
        return kb

    @staticmethod
    async def soft_delete(
        db: AsyncSession, kb_id: str, tenant_id: str | None = None
    ) -> bool:
        kb = await KnowledgeService.get_by_id(db, kb_id, tenant_id)
        if kb is None:
            return False
        kb.deleted_at = datetime.now(timezone.utc)
        await db.flush()
        return True
