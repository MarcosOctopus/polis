"""Campaign router — CRUD + send, pause, cancel, metrics."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Tenant, User as UserModel
from src.modules.auth.dependencies import get_current_tenant, get_current_user, get_db
from src.modules.campaigns.schemas import (
    CampaignCreate,
    CampaignList,
    CampaignResponse,
    CampaignUpdate,
)
from src.modules.campaigns.service import CampaignService

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    body: CampaignCreate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Create a new campaign."""
    campaign = await CampaignService.create(db, tenant.id, body)
    return CampaignResponse.model_validate(campaign)


@router.get("", response_model=CampaignList)
async def list_campaigns(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: str | None = Query(None),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """List campaigns with optional status filter."""
    campaigns, total = await CampaignService.list_by_tenant(
        db, tenant.id, skip=skip, limit=limit, status=status
    )
    return CampaignList(
        items=[CampaignResponse.model_validate(c) for c in campaigns],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Get a specific campaign by ID."""
    campaign = await CampaignService.get_by_id(db, campaign_id, tenant.id)
    if campaign is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )
    return CampaignResponse.model_validate(campaign)


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    body: CampaignUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Update a campaign."""
    campaign = await CampaignService.update(db, campaign_id, body, tenant.id)
    if campaign is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )
    return CampaignResponse.model_validate(campaign)


@router.delete("/{campaign_id}", status_code=status.HTTP_200_OK)
async def delete_campaign(
    campaign_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Soft-delete a campaign."""
    success = await CampaignService.soft_delete(db, campaign_id, tenant.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )
    return {"detail": "Campaign deleted successfully"}


@router.post("/{campaign_id}/send", response_model=dict)
async def send_campaign(
    campaign_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Send a campaign to all contacts matching its segments."""
    success, message = await CampaignService.send(db, campaign_id, tenant.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )
    return {"detail": message}


@router.post("/{campaign_id}/pause", response_model=CampaignResponse)
async def pause_campaign(
    campaign_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Pause a sending campaign."""
    campaign = await CampaignService.pause(db, campaign_id, tenant.id)
    if campaign is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campaign not found or not in sending status",
        )
    return CampaignResponse.model_validate(campaign)


@router.post("/{campaign_id}/cancel", response_model=CampaignResponse)
async def cancel_campaign(
    campaign_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Cancel a campaign."""
    campaign = await CampaignService.cancel(db, campaign_id, tenant.id)
    if campaign is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campaign not found or already completed/cancelled",
        )
    return CampaignResponse.model_validate(campaign)


@router.get("/{campaign_id}/metrics", response_model=dict)
async def campaign_metrics(
    campaign_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Get campaign delivery metrics."""
    metrics = await CampaignService.get_metrics(db, campaign_id, tenant.id)
    if not metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )
    return metrics
