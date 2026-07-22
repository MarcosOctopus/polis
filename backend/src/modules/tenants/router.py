"""Tenant router — CRUD endpoints for tenants."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.dependencies import get_current_user, get_db
from src.database.models import Tenant as TenantModel, User
from src.modules.tenants.schemas import TenantCreate, TenantResponse, TenantUpdate
from src.modules.tenants.service import TenantService

router = APIRouter(prefix="/tenants", tags=["Tenants"])


@router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    body: TenantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new tenant (admin only)."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create tenants",
        )
    tenant = await TenantService.create(db, body)
    return TenantResponse.model_validate(tenant)


@router.get("", response_model=dict)
async def list_tenants(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all active tenants."""
    if not current_user.is_admin:
        tenants, total = await TenantService.list_all(
            db, skip=skip, limit=limit, search=search
        )
    else:
        tenants, total = await TenantService.list_all(
            db, skip=skip, limit=limit, search=search
        )
    return {
        "items": [TenantResponse.model_validate(t) for t in tenants],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get tenant details."""
    tenant = await TenantService.get_by_id(db, tenant_id)
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    return TenantResponse.model_validate(tenant)


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: str,
    body: TenantUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a tenant."""
    if not current_user.is_admin and current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own tenant",
        )
    tenant = await TenantService.update(db, tenant_id, body)
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    return TenantResponse.model_validate(tenant)


@router.delete("/{tenant_id}", status_code=status.HTTP_200_OK)
async def delete_tenant(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft-delete a tenant (admin only)."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete tenants",
        )
    success = await TenantService.soft_delete(db, tenant_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    return {"detail": "Tenant deleted successfully"}
