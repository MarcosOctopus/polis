"""Territorial router — CRUD + map + stats endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Tenant, User as UserModel
from src.modules.auth.dependencies import get_current_tenant, get_current_user, get_db
from src.modules.territorial.schemas import (
    TerritorialEventCreate,
    TerritorialEventList,
    TerritorialEventResponse,
    TerritorialEventUpdate,
    TerritorialMapPoint,
    TerritorialStats,
)
from src.modules.territorial.service import TerritorialService

router = APIRouter(prefix="/territorial", tags=["Territorial"])


@router.post("", response_model=TerritorialEventResponse, status_code=status.HTTP_201_CREATED)
async def create_territorial_event(
    body: TerritorialEventCreate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Create a new territorial event."""
    event = await TerritorialService.create(db, tenant.id, body)
    return TerritorialEventResponse.model_validate(event)


@router.get("", response_model=TerritorialEventList)
async def list_territorial_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    event_type: str | None = Query(None),
    severity: str | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    search: str | None = Query(None),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """List territorial events with optional filters."""
    events, total = await TerritorialService.list_by_tenant(
        db,
        tenant.id,
        skip=skip,
        limit=limit,
        event_type=event_type,
        severity=severity,
        date_from=date_from,
        date_to=date_to,
        search=search,
    )
    return TerritorialEventList(
        items=[TerritorialEventResponse.model_validate(e) for e in events],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/map", response_model=list[TerritorialMapPoint])
async def territorial_map(
    event_type: str | None = Query(None),
    severity: str | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Get events with location data for map rendering."""
    events = await TerritorialService.list_for_map(
        db,
        tenant.id,
        event_type=event_type,
        severity=severity,
        date_from=date_from,
        date_to=date_to,
    )
    return [
        TerritorialMapPoint(
            id=e.id,
            event_type=e.event_type,
            title=e.title,
            severity=e.severity,
            location=e.location,
            occurred_at=e.occurred_at,
        )
        for e in events
    ]


@router.get("/stats", response_model=TerritorialStats)
async def territorial_stats(
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Get aggregated territorial event statistics."""
    stats = await TerritorialService.get_stats(
        db, tenant.id, date_from=date_from, date_to=date_to
    )

    # Grab the latest event for the response
    latest_result = await TerritorialService.list_by_tenant(
        db, tenant.id, skip=0, limit=1,
        date_from=date_from, date_to=date_to,
    )
    latest_event = (
        TerritorialEventResponse.model_validate(latest_result[0][0])
        if latest_result[0]
        else None
    )

    return TerritorialStats(
        total_events=stats["total_events"],
        by_type=stats["by_type"],
        by_severity=stats["by_severity"],
        latest_event=latest_event,
    )


@router.get("/{event_id}", response_model=TerritorialEventResponse)
async def get_territorial_event(
    event_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Get a specific territorial event by ID."""
    event = await TerritorialService.get_by_id(db, event_id, tenant.id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Territorial event not found",
        )
    return TerritorialEventResponse.model_validate(event)


@router.put("/{event_id}", response_model=TerritorialEventResponse)
async def update_territorial_event(
    event_id: str,
    body: TerritorialEventUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Update a territorial event."""
    event = await TerritorialService.update(db, event_id, body, tenant.id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Territorial event not found",
        )
    return TerritorialEventResponse.model_validate(event)


@router.delete("/{event_id}", status_code=status.HTTP_200_OK)
async def delete_territorial_event(
    event_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Soft-delete a territorial event."""
    success = await TerritorialService.soft_delete(db, event_id, tenant.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Territorial event not found",
        )
    return {"detail": "Territorial event deleted successfully"}
