"""User router — CRUD endpoints for users."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User as UserModel
from src.modules.auth.dependencies import get_current_user, get_current_tenant, get_db
from src.database.models import Tenant
from src.modules.users.schemas import UserCreate, UserResponse, UserUpdate
from src.modules.users.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Create a new user in the current tenant."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create users",
        )

    # Check duplicate email within tenant
    existing = await UserService.get_by_email(db, body.email, tenant.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists in this tenant",
        )

    user = await UserService.create(db, tenant.id, body)
    return UserResponse.model_validate(user)


@router.get("", response_model=dict)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: str | None = Query(None),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """List users for the current tenant."""
    users, total = await UserService.list_by_tenant(
        db, tenant.id, skip=skip, limit=limit, search=search
    )
    return {
        "items": [UserResponse.model_validate(u) for u in users],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: UserModel = Depends(get_current_user),
):
    """Get the current user's own profile."""
    return UserResponse.model_validate(current_user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Get a specific user by ID."""
    user = await UserService.get_by_id(db, user_id, tenant.id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    body: UserUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Update a user."""
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile",
        )

    user = await UserService.update(db, user_id, body, tenant.id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Soft-delete a user."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete users",
        )

    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete yourself",
        )

    success = await UserService.soft_delete(db, user_id, tenant.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return {"detail": "User deleted successfully"}
