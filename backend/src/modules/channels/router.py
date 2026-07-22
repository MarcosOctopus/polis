"""Channel router — CRUD + connection test + webhook registration."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Tenant, User as UserModel
from src.modules.auth.dependencies import get_current_tenant, get_current_user, get_db
from src.modules.channels.schemas import (
    ChannelCreate,
    ChannelList,
    ChannelResponse,
    ChannelUpdate,
    TestConnectionResponse,
    WebhookUrlResponse,
)
from src.modules.channels.service import ChannelService

router = APIRouter(prefix="/channels", tags=["Channels"])


@router.post("", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED)
async def create_channel(
    body: ChannelCreate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Create a new communication channel."""
    channel = await ChannelService.create(db, tenant.id, body)
    return ChannelResponse.model_validate(channel)


@router.get("", response_model=ChannelList)
async def list_channels(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    provider: str | None = Query(None),
    is_active: bool | None = Query(None),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """List channels for the current tenant."""
    channels, total = await ChannelService.list_by_tenant(
        db,
        tenant.id,
        skip=skip,
        limit=limit,
        provider=provider,
        is_active=is_active,
    )
    return ChannelList(
        items=[ChannelResponse.model_validate(c) for c in channels],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{channel_id}", response_model=ChannelResponse)
async def get_channel(
    channel_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Get a specific channel by ID. Credentials are never returned."""
    channel = await ChannelService.get_by_id(db, channel_id, tenant.id)
    if channel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found",
        )
    return ChannelResponse.model_validate(channel)


@router.put("/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    channel_id: str,
    body: ChannelUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Update a channel."""
    channel = await ChannelService.update(db, channel_id, body, tenant.id)
    if channel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found",
        )
    return ChannelResponse.model_validate(channel)


@router.delete("/{channel_id}", status_code=status.HTTP_200_OK)
async def delete_channel(
    channel_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Soft-delete a channel."""
    success = await ChannelService.soft_delete(db, channel_id, tenant.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found",
        )
    return {"detail": "Channel deleted successfully"}


@router.post("/{channel_id}/test", response_model=TestConnectionResponse)
async def test_channel_connection(
    channel_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Test the connection to a channel's provider."""
    success, message = await ChannelService.test_connection(db, channel_id, tenant.id)
    return TestConnectionResponse(success=success, message=message)


@router.post("/{channel_id}/webhook", response_model=WebhookUrlResponse)
async def register_webhook(
    channel_id: str,
    body: dict,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Register a webhook URL for a channel."""
    webhook_url = body.get("webhook_url")
    if not webhook_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="webhook_url is required",
        )
    try:
        channel, webhook_secret = await ChannelService.register_webhook(
            db, channel_id, webhook_url, tenant.id
        )
        return WebhookUrlResponse(
            webhook_url=channel.webhook_url or "",
            webhook_secret=webhook_secret,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
