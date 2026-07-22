"""FastAPI dependencies for authentication and authorization."""

from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_db as _get_db
from src.database.models import Tenant, User
from src.utils.security import decode_token

security_scheme = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides an async database session."""
    async for session in _get_db():
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Decode the JWT and return the current authenticated user."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(credentials.credentials)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    result = await db.execute(
        select(User).where(User.id == user_id, User.is_active == True)  # noqa: E712
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user


async def get_current_tenant(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Tenant:
    """Return the tenant associated with the current user."""
    result = await db.execute(
        select(Tenant).where(Tenant.id == user.tenant_id, Tenant.is_active == True)  # noqa: E712
    )
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    return tenant


def require_permissions(*required_perms: str):
    """Factory that returns a dependency requiring specific permissions.

    Usage:
        @router.get("/admin", dependencies=[Depends(require_permissions("admin"))])
    """

    async def _permission_checker(user: User = Depends(get_current_user)) -> User:
        if user.is_admin:
            return user

        if user.role and user.role.permissions:
            user_perms = set(user.role.permissions)
            if not user_perms.issuperset(required_perms):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return user

    return _permission_checker
