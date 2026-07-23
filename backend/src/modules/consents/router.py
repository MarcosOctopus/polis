"""Consent router — CRUD endpoints, bulk operations, and verification."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Tenant, User as UserModel
from src.modules.auth.dependencies import get_current_tenant, get_current_user, get_db
from src.modules.consents.schemas import (
    BulkConsentRequest,
    ConsentCheckResponse,
    ConsentCreate,
    ConsentOut,
    ConsentUpdate,
    PaginatedConsents,
)
from src.modules.consents.service import ConsentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/consents", tags=["Consents"])


@router.post("", response_model=ConsentOut, status_code=status.HTTP_201_CREATED)
async def set_consent(
    body: ConsentCreate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Create or update (upsert) a consent for a contact+channel pair."""
    consent = await ConsentService.set(db, tenant.id, body)
    return ConsentOut.model_validate(consent)


@router.get("", response_model=PaginatedConsents)
async def list_consents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    channel: str | None = Query(None, pattern="^(whatsapp|sms|email)$"),
    status: str | None = Query(None, pattern="^(granted|denied|pending)$"),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """List consents for the current tenant, optionally filtered."""
    consents, total = await ConsentService.list(
        db, tenant.id, skip=skip, limit=limit, channel=channel, status=status
    )
    return PaginatedConsents(
        items=[ConsentOut.model_validate(c) for c in consents],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{consent_id}", response_model=ConsentOut)
async def get_consent(
    consent_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Get a specific consent by ID."""
    consent = await ConsentService.get(db, consent_id, tenant.id)
    if consent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consent not found",
        )
    return ConsentOut.model_validate(consent)


@router.post("/bulk", status_code=status.HTTP_200_OK)
async def bulk_set_consent(
    body: BulkConsentRequest,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Set consent for multiple contacts on the same channel."""
    processed = await ConsentService.bulk_set(db, tenant.id, body)
    return {"processed": processed, "detail": f"{processed} consent(s) processed"}


@router.get("/check/{contact_id}/{channel}", response_model=ConsentCheckResponse)
async def check_consent(
    contact_id: str,
    channel: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Check if a contact has granted consent for a channel."""
    consent = await ConsentService.get_by_contact_channel(
        db, tenant.id, contact_id, channel
    )
    has_consent = await ConsentService.check_consent(
        db, tenant.id, contact_id, channel
    )
    return ConsentCheckResponse(
        consent_id=consent.id if consent else None,
        contact_id=contact_id,
        channel=channel,
        has_consent=has_consent,
        status=consent.status if consent else None,
    )
