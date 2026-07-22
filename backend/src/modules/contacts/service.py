"""Contact service — CRUD with tenant filtering, search, pagination, soft delete."""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.modules.contacts.schemas import ContactCreate, ContactUpdate


class ContactService:
    """Business logic for contact management."""

    @staticmethod
    async def create(
        db: AsyncSession, tenant_id: str, data: ContactCreate
    ) -> Contact:
        contact = Contact(
            tenant_id=tenant_id,
            name=data.name,
            email=data.email,
            phone=data.phone,
            city=data.city,
            state=data.state,
            neighborhood=data.neighborhood,
            address=data.address,
            latitude=data.latitude,
            longitude=data.longitude,
            tags=data.tags,
            metadata=data.metadata,
            is_active=True,
        )
        db.add(contact)
        await db.flush()
        await db.refresh(contact)
        return contact

    @staticmethod
    async def get_by_id(
        db: AsyncSession, contact_id: str, tenant_id: str | None = None
    ) -> Contact | None:
        query = select(Contact).where(
            Contact.id == contact_id,
            Contact.deleted_at.is_(None),
        )
        if tenant_id:
            query = query.where(Contact.tenant_id == tenant_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_tenant(
        db: AsyncSession,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        tags: list[str] | None = None,
        city: str | None = None,
        state: str | None = None,
    ) -> tuple[list[Contact], int]:
        query = select(Contact).where(
            Contact.tenant_id == tenant_id,
            Contact.deleted_at.is_(None),
        )

        if search:
            query = query.where(
                Contact.name.ilike(f"%{search}%")
                | (Contact.phone.ilike(f"%{search}%") if Contact.phone else False)
                | (Contact.email.ilike(f"%{search}%") if Contact.email else False)
            )

        if tags:
            # Filter contacts that have any of the specified tags
            for tag in tags:
                query = query.where(Contact.tags.any(tag))

        if city:
            query = query.where(Contact.city.ilike(f"%{city}%"))

        if state:
            query = query.where(Contact.state.ilike(f"%{state}%"))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Contact.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        contacts = list(result.scalars().all())
        return contacts, total

    @staticmethod
    async def update(
        db: AsyncSession,
        contact_id: str,
        data: ContactUpdate,
        tenant_id: str | None = None,
    ) -> Contact | None:
        contact = await ContactService.get_by_id(db, contact_id, tenant_id)
        if contact is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(contact, key, value)

        await db.flush()
        await db.refresh(contact)
        return contact

    @staticmethod
    async def soft_delete(
        db: AsyncSession, contact_id: str, tenant_id: str | None = None
    ) -> bool:
        contact = await ContactService.get_by_id(db, contact_id, tenant_id)
        if contact is None:
            return False

        contact.deleted_at = datetime.now(timezone.utc)
        contact.is_active = False
        await db.flush()
        return True

    @staticmethod
    async def add_tags(
        db: AsyncSession,
        contact_id: str,
        tags: list[str],
        tenant_id: str | None = None,
    ) -> Contact | None:
        contact = await ContactService.get_by_id(db, contact_id, tenant_id)
        if contact is None:
            return None

        current_tags = set(contact.tags or [])
        current_tags.update(tags)
        contact.tags = list(current_tags)
        await db.flush()
        await db.refresh(contact)
        return contact

    @staticmethod
    async def remove_tags(
        db: AsyncSession,
        contact_id: str,
        tags: list[str],
        tenant_id: str | None = None,
    ) -> Contact | None:
        contact = await ContactService.get_by_id(db, contact_id, tenant_id)
        if contact is None:
            return None

        current_tags = set(contact.tags or [])
        current_tags.difference_update(tags)
        contact.tags = list(current_tags) if current_tags else None
        await db.flush()
        await db.refresh(contact)
        return contact
