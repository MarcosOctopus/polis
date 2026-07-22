"""Message router — send, list by conversation, get by ID."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Tenant, User as UserModel
from src.modules.auth.dependencies import get_current_tenant, get_current_user, get_db
from src.modules.messages.schemas import (
    MessageCreate,
    MessageList,
    MessageResponse,
)
from src.modules.messages.service import MessageService

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    body: MessageCreate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Send a message. If channel_id is provided, the message is sent via the provider."""
    message = await MessageService.send_and_create(db, tenant.id, body)
    return MessageResponse.model_validate(message)


@router.get("", response_model=MessageList)
async def list_messages(
    conversation_id: str = Query(..., description="Filter by conversation ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """List messages for a conversation."""
    messages, total = await MessageService.list_by_conversation(
        db, conversation_id, tenant_id=tenant.id, skip=skip, limit=limit
    )
    return MessageList(
        items=[MessageResponse.model_validate(m) for m in messages],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Get a specific message by ID."""
    message = await MessageService.get_by_id(db, message_id, tenant.id)
    if message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )
    return MessageResponse.model_validate(message)


@router.post("/{message_id}/read", response_model=MessageResponse)
async def mark_as_read(
    message_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Mark a message as read."""
    message = await MessageService.mark_as_read(db, message_id, tenant.id)
    if message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )
    return MessageResponse.model_validate(message)
