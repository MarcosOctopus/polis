"""Auth router — login, register, refresh, change password, me."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Tenant, User
from src.modules.auth.dependencies import get_current_user, get_db
from src.modules.auth.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserOut,
    TenantOut,
)
from src.modules.auth.service import AuthService
from src.utils.security import create_access_token, create_refresh_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return JWT tokens."""
    user = await AuthService.authenticate(db, email=body.email, password=body.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    result = await db.execute(select(Tenant).where(Tenant.id == user.tenant_id))
    tenant = result.scalar_one_or_none()
    if tenant is None or not tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tenant inactive or not found",
        )

    access_token = create_access_token({"sub": user.id, "tenant_id": tenant.id})
    refresh_token = create_refresh_token({"sub": user.id, "tenant_id": tenant.id})

    await AuthService.store_refresh_token(db, user.id, refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserOut.model_validate(user),
        tenant=TenantOut.model_validate(tenant),
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Create a new tenant and admin user."""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user, tenant = await AuthService.register(db, body)

    access_token = create_access_token({"sub": user.id, "tenant_id": tenant.id})
    refresh_token = create_refresh_token({"sub": user.id, "tenant_id": tenant.id})

    await AuthService.store_refresh_token(db, user.id, refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserOut.model_validate(user),
        tenant=TenantOut.model_validate(tenant),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Refresh an expired access token using a refresh token."""
    result = await AuthService.refresh_token(db, body.refresh_token)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    return result


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    body: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change the authenticated user's password."""
    success = await AuthService.change_password(
        db, current_user.id, body.old_password, body.new_password
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect",
        )
    await AuthService.revoke_user_tokens(db, current_user.id)
    return {"detail": "Password changed successfully. Please log in again."}


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the current authenticated user's profile."""
    return UserOut.model_validate(current_user)
