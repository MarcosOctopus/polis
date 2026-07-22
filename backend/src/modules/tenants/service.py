"""Tenant service — CRUD for tenants."""

from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Tenant
from src.modules.tenants.schemas import TenantCreate, TenantUpdate


class TenantService:
    """Business logic for tenant management."""

    @staticmethod
    async def create(db: AsyncSession, data: TenantCreate) -> Tenant:
        tenant = Tenant(
            name=data.name,
            document=data.document,
            type=data.type,
            city=data.city,
            state=data.state,
            domain=data.domain,
            is_active=True,
        )
        db.add(tenant)
        await db.flush()
        await db.refresh(tenant)
        return tenant

    @staticmethod
    async def get_by_id(db: AsyncSession, tenant_id: str) -> Tenant | None:
        result = await db.execute(
            select(Tenant).where(
                Tenant.id == tenant_id,
                Tenant.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> tuple[list[Tenant], int]:
        query = select(Tenant).where(Tenant.deleted_at.is_(None))

        if search:
            query = query.where(Tenant.name.ilike(f"%{search}%"))

        # Total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Tenant.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        tenants = list(result.scalars().all())
        return tenants, total

    @staticmethod
    async def update(db: AsyncSession, tenant_id: str, data: TenantUpdate) -> Tenant | None:
        tenant = await TenantService.get_by_id(db, tenant_id)
        if tenant is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(tenant, key, value)

        await db.flush()
        await db.refresh(tenant)
        return tenant

    @staticmethod
    async def soft_delete(db: AsyncSession, tenant_id: str) -> bool:
        tenant = await TenantService.get_by_id(db, tenant_id)
        if tenant is None:
            return False

        tenant.deleted_at = datetime.now(timezone.utc)
        tenant.is_active = False
        await db.flush()
        return True
