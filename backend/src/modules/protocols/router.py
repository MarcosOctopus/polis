"""Protocol router — CRUD + search by contact."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Tenant, User as UserModel
from src.modules.auth.dependencies import get_current_tenant, get_current_user, get_db
from src.modules.protocols.schemas import (
    ProtocolCreate,
    ProtocolList,
    ProtocolResponse,
    ProtocolUpdate,
)
from src.modules.protocols.service import ProtocolService

router = APIRouter(prefix="/protocols", tags=["Protocols"])


@router.post("", response_model=ProtocolResponse, status_code=status.HTTP_201_CREATED)
async def create_protocol(
    body: ProtocolCreate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Create a new protocol with an auto-generated number."""
    protocol = await ProtocolService.create(db, tenant.id, body)
    return ProtocolResponse.model_validate(protocol)


@router.get("", response_model=ProtocolList)
async def list_protocols(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    contact_id: str | None = Query(None),
    event: str | None = Query(None),
    status: str | None = Query(None),
    search: str | None = Query(None),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """List protocols with optional filters."""
    protocols, total = await ProtocolService.list_by_tenant(
        db,
        tenant.id,
        skip=skip,
        limit=limit,
        contact_id=contact_id,
        event=event,
        status=status,
        search=search,
    )
    return ProtocolList(
        items=[ProtocolResponse.model_validate(p) for p in protocols],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{protocol_id}", response_model=ProtocolResponse)
async def get_protocol(
    protocol_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Get a specific protocol by ID."""
    protocol = await ProtocolService.get_by_id(db, protocol_id, tenant.id)
    if protocol is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Protocol not found",
        )
    return ProtocolResponse.model_validate(protocol)


@router.put("/{protocol_id}", response_model=ProtocolResponse)
async def update_protocol(
    protocol_id: str,
    body: ProtocolUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Update a protocol."""
    protocol = await ProtocolService.update(db, protocol_id, body, tenant.id)
    if protocol is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Protocol not found",
        )
    return ProtocolResponse.model_validate(protocol)


@router.delete("/{protocol_id}", status_code=status.HTTP_200_OK)
async def delete_protocol(
    protocol_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Soft-delete a protocol."""
    success = await ProtocolService.soft_delete(db, protocol_id, tenant.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Protocol not found",
        )
    return {"detail": "Protocol deleted successfully"}
