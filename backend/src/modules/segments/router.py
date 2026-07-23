"""Segment router — CRUD endpoints + contact membership management."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Tenant, User as UserModel
from src.modules.auth.dependencies import get_current_tenant, get_current_user, get_db
from src.modules.segments.schemas import (
    AddContactsRequest,
    ContactBasics,
    PaginatedSegmentContacts,
    PaginatedSegments,
    SegmentContactOut,
    SegmentContactWithContact,
    SegmentCreate,
    SegmentOut,
    SegmentUpdate,
)
from src.modules.segments.service import SegmentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/segments", tags=["Segments"])


@router.post("", response_model=SegmentOut, status_code=status.HTTP_201_CREATED)
async def create_segment(
    body: SegmentCreate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Create a new audience segment."""
    segment = await SegmentService.create(db, tenant.id, current_user.id, body)
    return SegmentOut.model_validate(segment)


@router.get("", response_model=PaginatedSegments)
async def list_segments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """List segments for the current tenant."""
    segments, total = await SegmentService.list(db, tenant.id, skip=skip, limit=limit)
    return PaginatedSegments(
        items=[SegmentOut.model_validate(s) for s in segments],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{segment_id}", response_model=SegmentOut)
async def get_segment(
    segment_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Get a specific segment by ID."""
    segment = await SegmentService.get(db, segment_id, tenant.id)
    if segment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Segment not found",
        )
    return SegmentOut.model_validate(segment)


@router.put("/{segment_id}", response_model=SegmentOut)
async def update_segment(
    segment_id: str,
    body: SegmentUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Update a segment."""
    segment = await SegmentService.update(db, segment_id, body, tenant.id)
    if segment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Segment not found",
        )
    return SegmentOut.model_validate(segment)


@router.delete("/{segment_id}", status_code=status.HTTP_200_OK)
async def delete_segment(
    segment_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Delete a segment and its contact associations."""
    success = await SegmentService.delete(db, segment_id, tenant.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Segment not found",
        )
    return {"detail": "Segment deleted successfully"}


@router.post("/{segment_id}/contacts", status_code=status.HTTP_200_OK)
async def add_contacts(
    segment_id: str,
    body: AddContactsRequest,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Add contacts to a segment."""
    added = await SegmentService.add_contacts(db, segment_id, body.contact_ids, tenant.id)
    return {"added": added, "detail": f"{added} contact(s) added to segment"}


@router.delete("/{segment_id}/contacts/{contact_id}", status_code=status.HTTP_200_OK)
async def remove_contact(
    segment_id: str,
    contact_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Remove a contact from a segment."""
    success = await SegmentService.remove_contact(db, segment_id, contact_id, tenant.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found in segment",
        )
    return {"detail": "Contact removed from segment"}


@router.get("/{segment_id}/contacts", response_model=PaginatedSegmentContacts)
async def list_segment_contacts(
    segment_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """List contacts belonging to a segment."""
    rows, total = await SegmentService.get_contacts(
        db, segment_id, skip=skip, limit=limit, tenant_id=tenant.id
    )
    items: list[SegmentContactWithContact] = []
    for sc, contact in rows:
        contact_basics = ContactBasics.model_validate(contact) if contact else None
        items.append(
            SegmentContactWithContact(
                segment_id=sc.segment_id,
                contact_id=sc.contact_id,
                added_at=sc.added_at,
                contact=contact_basics,
            )
        )
    return PaginatedSegmentContacts(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
    )
