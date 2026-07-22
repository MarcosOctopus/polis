"""Audit service — log and query audit entries."""

from datetime import datetime

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import AuditLog
from src.modules.audit.schemas import AuditLogCreate, AuditLogFilter


class AuditService:
    """Business logic for audit logging."""

    @staticmethod
    async def log(db: AsyncSession, data: AuditLogCreate) -> AuditLog:
        """Create a new audit log entry."""
        entry = AuditLog(
            tenant_id=data.tenant_id,
            user_id=data.user_id,
            action=data.action,
            entity=data.entity,
            entity_id=data.entity_id,
            description=data.description,
            metadata=data.metadata,
            ip_address=data.ip_address,
            user_agent=data.user_agent,
        )
        db.add(entry)
        await db.flush()
        await db.refresh(entry)
        return entry

    @staticmethod
    async def list_logs(
        db: AsyncSession,
        filters: AuditLogFilter | None = None,
    ) -> tuple[list[AuditLog], int]:
        """List audit logs with optional filters."""
        query = select(AuditLog)

        conditions = []
        if filters:
            if filters.tenant_id:
                conditions.append(AuditLog.tenant_id == filters.tenant_id)
            if filters.user_id:
                conditions.append(AuditLog.user_id == filters.user_id)
            if filters.action:
                conditions.append(AuditLog.action == filters.action)
            if filters.entity:
                conditions.append(AuditLog.entity == filters.entity)
            if filters.date_from:
                conditions.append(AuditLog.created_at >= filters.date_from)
            if filters.date_to:
                conditions.append(AuditLog.created_at <= filters.date_to)

        if conditions:
            query = query.where(and_(*conditions))

        # Total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        skip = filters.skip if filters else 0
        limit = filters.limit if filters else 100

        query = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        logs = list(result.scalars().all())
        return logs, total
