"""User service — CRUD for users with password hashing."""

from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.modules.users.schemas import UserCreate, UserUpdate
from src.utils.security import hash_password


class UserService:
    """Business logic for user management."""

    @staticmethod
    async def create(db: AsyncSession, tenant_id: str, data: UserCreate) -> User:
        user = User(
            tenant_id=tenant_id,
            name=data.name,
            email=data.email,
            phone=data.phone,
            password_hash=hash_password(data.password),
            role_id=data.role_id,
            is_active=True,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_by_id(
        db: AsyncSession, user_id: str, tenant_id: str | None = None
    ) -> User | None:
        query = select(User).where(
            User.id == user_id,
            User.deleted_at.is_(None),
        )
        if tenant_id:
            query = query.where(User.tenant_id == tenant_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(
        db: AsyncSession, email: str, tenant_id: str | None = None
    ) -> User | None:
        query = select(User).where(User.email == email, User.deleted_at.is_(None))
        if tenant_id:
            query = query.where(User.tenant_id == tenant_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_tenant(
        db: AsyncSession,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> tuple[list[User], int]:
        query = select(User).where(
            User.tenant_id == tenant_id,
            User.deleted_at.is_(None),
        )

        if search:
            query = query.where(
                User.name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%")
            )

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(User.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        users = list(result.scalars().all())
        return users, total

    @staticmethod
    async def update(
        db: AsyncSession, user_id: str, data: UserUpdate, tenant_id: str | None = None
    ) -> User | None:
        user = await UserService.get_by_id(db, user_id, tenant_id)
        if user is None:
            return None

        update_data = data.model_dump(exclude_unset=True, exclude={"password"})
        for key, value in update_data.items():
            setattr(user, key, value)

        await db.flush()
        await db.refresh(user)
        return user

    @staticmethod
    async def soft_delete(
        db: AsyncSession, user_id: str, tenant_id: str | None = None
    ) -> bool:
        user = await UserService.get_by_id(db, user_id, tenant_id)
        if user is None:
            return False

        user.deleted_at = datetime.now(timezone.utc)
        user.is_active = False
        await db.flush()
        return True

    @staticmethod
    async def set_password(
        db: AsyncSession, user_id: str, new_password: str
    ) -> bool:
        user = await UserService.get_by_id(db, user_id)
        if user is None:
            return False
        user.password_hash = hash_password(new_password)
        await db.flush()
        return True
