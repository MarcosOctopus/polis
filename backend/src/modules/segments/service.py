"""Segment service — CRUD + contact membership management."""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.database.models_extensions import Segment, SegmentContact
from src.modules.segments.schemas import SegmentCreate, SegmentUpdate

logger = logging.getLogger(__name__)


class SegmentService:
    """Business logic for audience segment management."""

    @staticmethod
    async def create(
        db: AsyncSession, tenant_id: str, user_id: str, data: SegmentCreate
    ) -> Segment:
        segment = Segment(
            tenant_id=tenant_id,
            name=data.name,
            description=data.description,
            segment_type=data.segment_type,
            filters=data.filters,
            territorial_event_id=data.territorial_event_id,
            is_active=True,
            created_by=user_id,
            contact_count=0,
        )
        db.add(segment)
        await db.flush()

        if data.contact_ids:
            count = await SegmentService._bulk_add_contacts(
                db, segment.id, data.contact_ids
            )
            segment.contact_count = count

        await db.refresh(segment)
        logger.info(
            "Segment created: %s (tenant=%s, type=%s)",
            segment.id, tenant_id, data.segment_type,
        )
        return segment

    @staticmethod
    async def get(
        db: AsyncSession, segment_id: str, tenant_id: Optional[str] = None
    ) -> Optional[Segment]:
        query = select(Segment).where(Segment.id == segment_id)
        if tenant_id:
            query = query.where(Segment.tenant_id == tenant_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list(
        db: AsyncSession,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Segment], int]:
        query = select(Segment).where(Segment.tenant_id == tenant_id)
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        query = query.order_by(Segment.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        segments = list(result.scalars().all())
        return segments, total

    @staticmethod
    async def update(
        db: AsyncSession,
        segment_id: str,
        data: SegmentUpdate,
        tenant_id: Optional[str] = None,
    ) -> Optional[Segment]:
        segment = await SegmentService.get(db, segment_id, tenant_id)
        if segment is None:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(segment, key, value)
        await db.flush()
        await db.refresh(segment)
        logger.info("Segment updated: %s", segment_id)
        return segment

    @staticmethod
    async def delete(
        db: AsyncSession, segment_id: str, tenant_id: Optional[str] = None
    ) -> bool:
        segment = await SegmentService.get(db, segment_id, tenant_id)
        if segment is None:
            return False

        # Remove all contact associations
        await db.execute(
            SegmentContact.__table__.delete().where(
                SegmentContact.segment_id == segment_id
            )
        )
        await db.delete(segment)
        await db.flush()
        logger.info("Segment deleted: %s", segment_id)
        return True

    @staticmethod
    async def _bulk_add_contacts(
        db: AsyncSession, segment_id: str, contact_ids: List[str]
    ) -> int:
        """Add multiple contacts to a segment. Returns count of new associations."""
        added = 0
        now = datetime.now(timezone.utc)
        for cid in contact_ids:
            existing = await db.execute(
                select(SegmentContact).where(
                    SegmentContact.segment_id == segment_id,
                    SegmentContact.contact_id == cid,
                )
            )
            if existing.scalar_one_or_none() is None:
                sc = SegmentContact(
                    segment_id=segment_id,
                    contact_id=cid,
                    added_at=now,
                )
                db.add(sc)
                added += 1

        if added > 0:
            await db.flush()
            segment = await SegmentService.get(db, segment_id)
            if segment:
                segment.contact_count = (segment.contact_count or 0) + added
                await db.flush()

        return added

    @staticmethod
    async def add_contacts(
        db: AsyncSession,
        segment_id: str,
        contact_ids: List[str],
        tenant_id: Optional[str] = None,
    ) -> int:
        """Add contacts to a segment. Returns the number added."""
        segment = await SegmentService.get(db, segment_id, tenant_id)
        if segment is None:
            return 0
        return await SegmentService._bulk_add_contacts(db, segment_id, contact_ids)

    @staticmethod
    async def remove_contact(
        db: AsyncSession,
        segment_id: str,
        contact_id: str,
        tenant_id: Optional[str] = None,
    ) -> bool:
        """Remove a single contact from a segment."""
        segment = await SegmentService.get(db, segment_id, tenant_id)
        if segment is None:
            return False

        result = await db.execute(
            select(SegmentContact).where(
                SegmentContact.segment_id == segment_id,
                SegmentContact.contact_id == contact_id,
            )
        )
        sc = result.scalar_one_or_none()
        if sc is None:
            return False

        await db.delete(sc)
        segment.contact_count = max(0, (segment.contact_count or 1) - 1)
        await db.flush()
        return True

    @staticmethod
    async def get_contacts(
        db: AsyncSession,
        segment_id: str,
        skip: int = 0,
        limit: int = 100,
        tenant_id: Optional[str] = None,
    ) -> Tuple[list, int]:
        """List contacts belonging to a segment with their contact data."""
        segment = await SegmentService.get(db, segment_id, tenant_id)
        if segment is None:
            return [], 0

        count_query = select(func.count()).where(
            SegmentContact.segment_id == segment_id
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = (
            select(SegmentContact, Contact)
            .outerjoin(Contact, SegmentContact.contact_id == Contact.id)
            .where(SegmentContact.segment_id == segment_id)
            .order_by(SegmentContact.added_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        rows = list(result.all())
        return rows, total

    @staticmethod
    async def count_by_filters(
        db: AsyncSession, tenant_id: str, filters: Optional[Dict] = None
    ) -> int:
        """Count contacts matching dynamic segment filters."""
        query = select(func.count(Contact.id)).where(
            Contact.tenant_id == tenant_id,
            Contact.deleted_at.is_(None),
        )

        if filters:
            if filters.get("city"):
                query = query.where(Contact.city.ilike(f"%{filters['city']}%"))
            if filters.get("state"):
                query = query.where(Contact.state.ilike(f"%{filters['state']}%"))
            if filters.get("tags"):
                tags = filters["tags"]
                if isinstance(tags, list):
                    for tag in tags:
                        query = query.where(Contact.tags.any(tag))

        result = await db.execute(query)
        return result.scalar() or 0
