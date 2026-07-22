"""Territorial service — CRUD with filters, map data, and stats."""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import TerritorialEvent
from src.modules.territorial.schemas import (
    TerritorialEventCreate,
    TerritorialEventUpdate,
)


class TerritorialService:
    """Business logic for territorial event management."""

    @staticmethod
    async def create(
        db: AsyncSession, tenant_id: str, data: TerritorialEventCreate
    ) -> TerritorialEvent:
        event = TerritorialEvent(
            tenant_id=tenant_id,
            event_type=data.event_type,
            title=data.title,
            description=data.description,
            location=data.location,
            severity=data.severity,
            occurred_at=data.occurred_at,
            metadata=data.metadata,
        )
        db.add(event)
        await db.flush()
        await db.refresh(event)
        return event

    @staticmethod
    async def get_by_id(
        db: AsyncSession, event_id: str, tenant_id: str | None = None
    ) -> TerritorialEvent | None:
        query = select(TerritorialEvent).where(
            TerritorialEvent.id == event_id,
            TerritorialEvent.deleted_at.is_(None),
        )
        if tenant_id:
            query = query.where(TerritorialEvent.tenant_id == tenant_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_tenant(
        db: AsyncSession,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        event_type: str | None = None,
        severity: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        search: str | None = None,
    ) -> tuple[list[TerritorialEvent], int]:
        query = select(TerritorialEvent).where(
            TerritorialEvent.tenant_id == tenant_id,
            TerritorialEvent.deleted_at.is_(None),
        )
        if event_type:
            query = query.where(TerritorialEvent.event_type == event_type)
        if severity:
            query = query.where(TerritorialEvent.severity == severity)
        if date_from:
            query = query.where(TerritorialEvent.occurred_at >= date_from)
        if date_to:
            query = query.where(TerritorialEvent.occurred_at <= date_to)
        if search:
            query = query.where(
                TerritorialEvent.title.ilike(f"%{search}%")
                | TerritorialEvent.description.ilike(f"%{search}%")
            )

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = (
            query.order_by(TerritorialEvent.occurred_at.desc().nullslast())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        events = list(result.scalars().all())
        return events, total

    @staticmethod
    async def update(
        db: AsyncSession,
        event_id: str,
        data: TerritorialEventUpdate,
        tenant_id: str | None = None,
    ) -> TerritorialEvent | None:
        event = await TerritorialService.get_by_id(db, event_id, tenant_id)
        if event is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(event, key, value)

        await db.flush()
        await db.refresh(event)
        return event

    @staticmethod
    async def soft_delete(
        db: AsyncSession, event_id: str, tenant_id: str | None = None
    ) -> bool:
        event = await TerritorialService.get_by_id(db, event_id, tenant_id)
        if event is None:
            return False
        event.deleted_at = datetime.now(timezone.utc)
        await db.flush()
        return True

    @staticmethod
    async def list_for_map(
        db: AsyncSession,
        tenant_id: str,
        event_type: str | None = None,
        severity: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[TerritorialEvent]:
        """Return events with location data for map rendering."""
        query = select(TerritorialEvent).where(
            TerritorialEvent.tenant_id == tenant_id,
            TerritorialEvent.deleted_at.is_(None),
            TerritorialEvent.location.isnot(None),
        )
        if event_type:
            query = query.where(TerritorialEvent.event_type == event_type)
        if severity:
            query = query.where(TerritorialEvent.severity == severity)
        if date_from:
            query = query.where(TerritorialEvent.occurred_at >= date_from)
        if date_to:
            query = query.where(TerritorialEvent.occurred_at <= date_to)

        query = query.order_by(
            TerritorialEvent.occurred_at.desc().nullslast()
        ).limit(500)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_stats(
        db: AsyncSession,
        tenant_id: str,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> dict:
        """Return aggregated statistics for territorial events."""
        base_query = select(TerritorialEvent).where(
            TerritorialEvent.tenant_id == tenant_id,
            TerritorialEvent.deleted_at.is_(None),
        )
        if date_from:
            base_query = base_query.where(TerritorialEvent.occurred_at >= date_from)
        if date_to:
            base_query = base_query.where(TerritorialEvent.occurred_at <= date_to)

        # Total count
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Count by event_type
        type_query = (
            select(TerritorialEvent.event_type, func.count())
            .where(
                TerritorialEvent.tenant_id == tenant_id,
                TerritorialEvent.deleted_at.is_(None),
            )
            .group_by(TerritorialEvent.event_type)
        )
        if date_from:
            type_query = type_query.where(TerritorialEvent.occurred_at >= date_from)
        if date_to:
            type_query = type_query.where(TerritorialEvent.occurred_at <= date_to)
        type_result = await db.execute(type_query)
        by_type = dict(type_result.all())

        # Count by severity
        sev_query = (
            select(TerritorialEvent.severity, func.count())
            .where(
                TerritorialEvent.tenant_id == tenant_id,
                TerritorialEvent.deleted_at.is_(None),
            )
            .group_by(TerritorialEvent.severity)
        )
        if date_from:
            sev_query = sev_query.where(TerritorialEvent.occurred_at >= date_from)
        if date_to:
            sev_query = sev_query.where(TerritorialEvent.occurred_at <= date_to)
        sev_result = await db.execute(sev_query)
        by_severity = dict(sev_result.all())

        return {
            "total_events": total,
            "by_type": by_type,
            "by_severity": by_severity,
        }
