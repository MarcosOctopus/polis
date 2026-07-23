"""Classification service — business logic for IA classification."""

import json
import logging
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import TerritorialEvent
from src.database.models_extensions import MessageClassification
from src.modules.classification.classifier import MessageClassifier
from src.modules.classification.schemas import ReclassifyRequest

logger = logging.getLogger(__name__)


class ClassificationService:
    """Business logic for message classification."""

    def __init__(self, classifier: MessageClassifier) -> None:
        self.classifier = classifier

    # ------------------------------------------------------------------
    # Classify a single message
    # ------------------------------------------------------------------
    async def classify_message(
        self,
        session: AsyncSession,
        tenant_id: str,
        msg_text: str,
        msg_id: str,
        contact_id: str | None = None,
    ) -> MessageClassification:
        """Run the classifier on a message, persist the result, and return it.

        If an existing classification exists for this message_id it will
        be replaced (soft update by deleting + re-inserting).
        """
        # Build optional contact info
        contact_info = None
        if contact_id:
            from src.database.models import Contact

            result = await session.execute(
                select(Contact).where(Contact.id == contact_id, Contact.tenant_id == tenant_id)
            )
            contact = result.scalar_one_or_none()
            if contact:
                contact_info = {
                    "city": contact.city,
                    "neighborhood": contact.neighborhood,
                    "state": contact.state,
                }

        # Run the LLM classifier
        raw = await self.classifier.classify(
            text=msg_text,
            message_id=msg_id,
            contact_info=contact_info,
        )

        # Remove existing classification for this message (if any)
        existing = await session.execute(
            select(MessageClassification).where(
                MessageClassification.message_id == msg_id,
                MessageClassification.tenant_id == tenant_id,
            )
        )
        existing_row = existing.scalar_one_or_none()
        if existing_row:
            await session.delete(existing_row)
            await session.flush()

        # Resolve territorial event if location data was extracted
        territorial_event_id = None
        if raw.get("extracted_neighborhood") or raw.get("extracted_city"):
            territorial_event_id = await self._resolve_territorial_event(
                session, tenant_id, raw
            )

        # Persist
        classification = MessageClassification(
            tenant_id=tenant_id,
            message_id=msg_id,
            classification_type=raw.get("classification_type", "general"),
            category=raw.get("category"),
            subcategory=raw.get("subcategory"),
            sentiment=raw.get("sentiment"),
            sentiment_score=raw.get("sentiment_score"),
            urgency=raw.get("urgency"),
            risk=raw.get("risk"),
            extracted_address=raw.get("extracted_address"),
            extracted_neighborhood=raw.get("extracted_neighborhood"),
            extracted_city=raw.get("extracted_city"),
            extracted_state=raw.get("extracted_state"),
            reference_point=raw.get("reference_point"),
            latitude=raw.get("latitude"),
            longitude=raw.get("longitude"),
            geocode_source=raw.get("geocode_source"),
            suggested_department=raw.get("suggested_department"),
            summary=raw.get("summary"),
            keywords=raw.get("keywords"),
            confidence=raw.get("confidence"),
            model="gpt-4o-mini",
            raw_classification=raw,
            territorial_event_id=territorial_event_id,
            processed_at=datetime.now(timezone.utc),
        )
        session.add(classification)
        await session.flush()
        await session.refresh(classification)
        return classification

    # ------------------------------------------------------------------
    # Get classification for a message
    # ------------------------------------------------------------------
    async def get_message_classification(
        self,
        session: AsyncSession,
        msg_id: str,
        tenant_id: str | None = None,
    ) -> MessageClassification | None:
        """Retrieve the classification for a given message."""
        stmt = select(MessageClassification).where(
            MessageClassification.message_id == msg_id,
        )
        if tenant_id:
            stmt = stmt.where(MessageClassification.tenant_id == tenant_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    # ------------------------------------------------------------------
    # Paginated listing
    # ------------------------------------------------------------------
    async def get_classifications(
        self,
        session: AsyncSession,
        tenant_id: str,
        limit: int = 50,
        offset: int = 0,
        filter_by: dict | None = None,
    ) -> tuple[list[MessageClassification], int]:
        """List classifications for a tenant with optional filters."""
        stmt = select(MessageClassification).where(
            MessageClassification.tenant_id == tenant_id,
        )

        # Apply optional filters
        filters = filter_by or {}
        if filters.get("classification_type"):
            stmt = stmt.where(
                MessageClassification.classification_type == filters["classification_type"]
            )
        if filters.get("sentiment"):
            stmt = stmt.where(MessageClassification.sentiment == filters["sentiment"])
        if filters.get("urgency"):
            stmt = stmt.where(MessageClassification.urgency == filters["urgency"])
        if filters.get("risk"):
            stmt = stmt.where(MessageClassification.risk == filters["risk"])
        if filters.get("category"):
            stmt = stmt.where(MessageClassification.category == filters["category"])

        # Count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await session.execute(count_stmt)
        total = total_result.scalar() or 0

        # Paginate
        stmt = stmt.order_by(MessageClassification.created_at.desc()).offset(offset).limit(limit)
        result = await session.execute(stmt)
        rows = list(result.scalars().all())
        return rows, total

    # ------------------------------------------------------------------
    # Manual reclassification
    # ------------------------------------------------------------------
    async def reclassify(
        self,
        session: AsyncSession,
        classification_id: str,
        override_data: ReclassifyRequest,
        tenant_id: str | None = None,
    ) -> MessageClassification | None:
        """Override classification fields manually."""
        stmt = select(MessageClassification).where(
            MessageClassification.id == classification_id,
        )
        if tenant_id:
            stmt = stmt.where(MessageClassification.tenant_id == tenant_id)
        result = await session.execute(stmt)
        classification = result.scalar_one_or_none()
        if classification is None:
            return None

        update_data = override_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(classification, key, value)

        await session.flush()
        await session.refresh(classification)
        return classification

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    @staticmethod
    async def _resolve_territorial_event(
        session: AsyncSession,
        tenant_id: str,
        classification_data: dict,
    ) -> str | None:
        """Try to match extracted location to a known TerritorialEvent.

        Currently matches by bairro/cidade. Returns the event id or None.
        """
        neighborhood = classification_data.get("extracted_neighborhood")
        city = classification_data.get("extracted_city")

        if not neighborhood and not city:
            return None

        # Try to find an active event in the same neighbourhood
        conditions = [TerritorialEvent.tenant_id == tenant_id]
        if neighborhood:
            # JSON location field contains neighborhood
            from sqlalchemy import text

            conditions.append(
                TerritorialEvent.location["neighborhood"].as_string() == neighborhood
            )
        if city:
            conditions.append(
                TerritorialEvent.location["city"].as_string() == city
            )

        stmt = select(TerritorialEvent).where(*conditions).limit(1)
        result = await session.execute(stmt)
        event = result.scalar_one_or_none()
        return event.id if event else None
