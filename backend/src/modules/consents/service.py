"""Consent service — upsert, bulk, verification."""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models_extensions import Consent
from src.modules.consents.schemas import BulkConsentRequest, ConsentCreate

logger = logging.getLogger(__name__)


class ConsentService:
    """Business logic for contact consent management."""

    @staticmethod
    async def _now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    async def set(
        db: AsyncSession, tenant_id: str, data: ConsentCreate
    ) -> Consent:
        """Create or update (upsert) consent for a contact+channel pair."""
        now = await ConsentService._now()

        result = await db.execute(
            select(Consent).where(
                Consent.tenant_id == tenant_id,
                Consent.contact_id == data.contact_id,
                Consent.channel == data.channel,
            )
        )
        consent = result.scalar_one_or_none()

        if consent:
            consent.status = data.status
            if data.source:
                consent.source = data.source
            if data.status == "granted":
                consent.granted_at = now
                consent.denied_at = None
            elif data.status == "denied":
                consent.denied_at = now
                consent.granted_at = None
            consent.updated_at = now
        else:
            consent = Consent(
                tenant_id=tenant_id,
                contact_id=data.contact_id,
                channel=data.channel,
                status=data.status,
                source=data.source,
                granted_at=now if data.status == "granted" else None,
                denied_at=now if data.status == "denied" else None,
            )
            db.add(consent)

        await db.flush()
        await db.refresh(consent)
        logger.info(
            "Consent set: contact=%s channel=%s status=%s",
            data.contact_id, data.channel, data.status,
        )
        return consent

    @staticmethod
    async def get(
        db: AsyncSession, consent_id: str, tenant_id: Optional[str] = None
    ) -> Optional[Consent]:
        query = select(Consent).where(Consent.id == consent_id)
        if tenant_id:
            query = query.where(Consent.tenant_id == tenant_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_contact_channel(
        db: AsyncSession,
        tenant_id: str,
        contact_id: str,
        channel: str,
    ) -> Optional[Consent]:
        result = await db.execute(
            select(Consent).where(
                Consent.tenant_id == tenant_id,
                Consent.contact_id == contact_id,
                Consent.channel == channel,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list(
        db: AsyncSession,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        channel: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Tuple[List[Consent], int]:
        query = select(Consent).where(Consent.tenant_id == tenant_id)
        if channel:
            query = query.where(Consent.channel == channel)
        if status:
            query = query.where(Consent.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Consent.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        consents = list(result.scalars().all())
        return consents, total

    @staticmethod
    async def bulk_set(
        db: AsyncSession, tenant_id: str, data: BulkConsentRequest
    ) -> int:
        """Set consent for multiple contacts on the same channel."""
        count = 0
        for cid in data.contact_ids:
            await ConsentService.set(
                db,
                tenant_id,
                ConsentCreate(
                    contact_id=cid,
                    channel=data.channel,
                    status=data.status,
                    source=data.source,
                ),
            )
            count += 1

        logger.info(
            "Bulk consent set: %d contacts, channel=%s, status=%s",
            count, data.channel, data.status,
        )
        return count

    @staticmethod
    async def check_consent(
        db: AsyncSession,
        tenant_id: str,
        contact_id: str,
        channel: str,
    ) -> bool:
        """Check if a contact has active (granted) consent for a channel."""
        consent = await ConsentService.get_by_contact_channel(
            db, tenant_id, contact_id, channel
        )
        if consent is None:
            return False
        if consent.status != "granted":
            return False
        if consent.expires_at and consent.expires_at < await ConsentService._now():
            return False
        return True
