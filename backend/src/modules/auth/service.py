"""Auth service — business logic for authentication."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import RefreshToken, Tenant, User
from src.modules.auth.schemas import (
    RegisterRequest,
    TokenResponse,
    UserOut,
    TenantOut,
)
from src.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from src.config.settings import settings


class AuthService:
    """Handles authentication and registration logic."""

    @staticmethod
    async def authenticate(
        db: AsyncSession, email: str, password: str
    ) -> User | None:
        """Validate credentials and return the user or None."""
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user is None or not user.is_active:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    async def register(
        db: AsyncSession, data: RegisterRequest
    ) -> tuple[User, Tenant]:
        """Create a new tenant and an admin user."""
        tenant = Tenant(
            name=data.tenant_name,
            is_active=True,
        )
        db.add(tenant)
        await db.flush()

        user = User(
            tenant_id=tenant.id,
            name=data.name,
            email=data.email,
            password_hash=hash_password(data.password),
            is_admin=True,
            is_active=True,
        )
        db.add(user)
        await db.flush()
        return user, tenant

    @staticmethod
    async def refresh_token(
        db: AsyncSession, token: str
    ) -> TokenResponse | None:
        """Validate a refresh token and issue new tokens."""
        payload = decode_token(token)
        if payload is None or payload.get("type") != "refresh":
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        # Check stored refresh token
        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.token == token,
                RefreshToken.is_revoked == False,  # noqa: E712
            )
        )
        stored = result.scalar_one_or_none()
        if stored is None or stored.expires_at < datetime.now(timezone.utc):
            return None

        # Revoke old token
        stored.is_revoked = True
        await db.flush()

        # Fetch user and tenant
        result = await db.execute(
            select(User).where(User.id == user_id, User.is_active == True)  # noqa: E712
        )
        user = result.scalar_one_or_none()
        if user is None:
            return None

        result = await db.execute(
            select(Tenant).where(Tenant.id == user.tenant_id)
        )
        tenant = result.scalar_one_or_none()
        if tenant is None:
            return None

        # Issue new tokens
        access_token = create_access_token({"sub": user.id, "tenant_id": tenant.id})
        new_refresh_token = create_refresh_token({"sub": user.id, "tenant_id": tenant.id})

        # Store new refresh token
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.jwt_refresh_token_expire_days
        )
        rt = RefreshToken(
            user_id=user.id,
            token=new_refresh_token,
            expires_at=expires_at,
        )
        db.add(rt)
        await db.flush()

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            user=UserOut.model_validate(user),
            tenant=TenantOut.model_validate(tenant),
        )

    @staticmethod
    async def change_password(
        db: AsyncSession, user_id: str, old_password: str, new_password: str
    ) -> bool:
        """Change a user's password after verifying the current one."""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            return False

        if not verify_password(old_password, user.password_hash):
            return False

        user.password_hash = hash_password(new_password)
        await db.flush()
        return True

    @staticmethod
    async def store_refresh_token(
        db: AsyncSession, user_id: str, token: str
    ) -> RefreshToken:
        """Persist a refresh token in the database."""
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.jwt_refresh_token_expire_days
        )
        rt = RefreshToken(user_id=user_id, token=token, expires_at=expires_at)
        db.add(rt)
        await db.flush()
        return rt

    @staticmethod
    async def revoke_user_tokens(db: AsyncSession, user_id: str) -> None:
        """Revoke all active refresh tokens for a user."""
        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False,  # noqa: E712
            )
        )
        for token in result.scalars().all():
            token.is_revoked = True
        await db.flush()
