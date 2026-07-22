"""Protocol service — CRUD with automatic number generation, search by contact/event."""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, Protocol
from src.modules.protocols.schemas import ProtocolCreate, ProtocolUpdate


class ProtocolService:
    """Business logic for protocol management."""

    @staticmethod
    async def _generate_number(db: AsyncSession, tenant_id: str) -> str:
        """Generate a sequential protocol number in format PRO-YYYY-XXXXX."""
        year = str(datetime.now(timezone.utc).year)
        # Count protocols created this year for this tenant
        result = await db.execute(
            select(func.count()).where(
                Protocol.tenant_id == tenant_id,
                Protocol.number.like(f"PRO-{year}-%"),
            )
        )
        count = result.scalar() or 0
        seq = count + 1
        return f"PRO-{year}-{seq:05d}"

    @staticmethod
    async def create(
        db: AsyncSession, tenant_id: str, data: ProtocolCreate
    ) -> Protocol:
        number = await ProtocolService._generate_number(db, tenant_id)
        protocol = Protocol(
            tenant_id=tenant_id,
            contact_id=data.contact_id,
            title=data.title,
            description=data.description,
            event=data.event,
            number=number,
            status=data.status or "open",
            metadata=data.metadata,
        )
        db.add(protocol)
        await db.flush()
        await db.refresh(protocol)
        return protocol

    @staticmethod
    async def get_by_id(
        db: AsyncSession, protocol_id: str, tenant_id: str | None = None
    ) -> Protocol | None:
        query = select(Protocol).where(
            Protocol.id == protocol_id,
            Protocol.deleted_at.is_(None),
        )
        if tenant_id:
            query = query.where(Protocol.tenant_id == tenant_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_number(
        db: AsyncSession, number: str, tenant_id: str | None = None
    ) -> Protocol | None:
        query = select(Protocol).where(
            Protocol.number == number,
            Protocol.deleted_at.is_(None),
        )
        if tenant_id:
            query = query.where(Protocol.tenant_id == tenant_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_tenant(
        db: AsyncSession,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        contact_id: str | None = None,
        event: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> tuple[list[Protocol], int]:
        query = select(Protocol).where(
            Protocol.tenant_id == tenant_id,
            Protocol.deleted_at.is_(None),
        )
        if contact_id:
            query = query.where(Protocol.contact_id == contact_id)
        if event:
            query = query.where(Protocol.event.ilike(f"%{event}%"))
        if status:
            query = query.where(Protocol.status == status)
        if search:
            query = query.where(
                Protocol.number.ilike(f"%{search}%")
                | Protocol.title.ilike(f"%{search}%")
            )

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Protocol.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        protocols = list(result.scalars().all())
        return protocols, total

    @staticmethod
    async def update(
        db: AsyncSession,
        protocol_id: str,
        data: ProtocolUpdate,
        tenant_id: str | None = None,
    ) -> Protocol | None:
        protocol = await ProtocolService.get_by_id(db, protocol_id, tenant_id)
        if protocol is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(protocol, key, value)

        await db.flush()
        await db.refresh(protocol)
        return protocol

    @staticmethod
    async def soft_delete(
        db: AsyncSession, protocol_id: str, tenant_id: str | None = None
    ) -> bool:
        protocol = await ProtocolService.get_by_id(db, protocol_id, tenant_id)
        if protocol is None:
            return False
        protocol.deleted_at = datetime.now(timezone.utc)
        await db.flush()
        return True
