"""Conversation router — CRUD + assign endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Tenant, User as UserModel
from src.modules.auth.dependencies import get_current_tenant, get_current_user, get_db
from src.modules.conversations.schemas import (
    AssignConversationRequest,
    ConversationCreate,
    ConversationList,
    ConversationResponse,
    ConversationUpdate,
)
from src.modules.conversations.service import ConversationService

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    body: ConversationCreate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Start a new conversation."""
    conversation = await ConversationService.create(db, tenant.id, body)
    return ConversationResponse.model_validate(conversation)


@router.get("", response_model=ConversationList)
async def list_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: str | None = Query(None),
    contact_id: str | None = Query(None),
    assigned_to: str | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """List conversations with optional filters."""
    conversations, total = await ConversationService.list_by_tenant(
        db,
        tenant.id,
        skip=skip,
        limit=limit,
        status=status,
        contact_id=contact_id,
        assigned_to=assigned_to,
        date_from=date_from,
        date_to=date_to,
    )
    return ConversationList(
        items=[ConversationResponse.model_validate(c) for c in conversations],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Get a specific conversation by ID."""
    conversation = await ConversationService.get_by_id(db, conversation_id, tenant.id)
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    return ConversationResponse.model_validate(conversation)


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    body: ConversationUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Update a conversation."""
    conversation = await ConversationService.update(db, conversation_id, body, tenant.id)
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    return ConversationResponse.model_validate(conversation)


@router.post("/{conversation_id}/assign", response_model=ConversationResponse)
async def assign_conversation(
    conversation_id: str,
    body: AssignConversationRequest,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Assign a conversation to a user."""
    if body.user_id == "null" or body.user_id == "":
        conversation = await ConversationService.unassign(db, conversation_id, tenant.id)
    else:
        conversation = await ConversationService.assign(
            db, conversation_id, body.user_id, tenant.id
        )
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    return ConversationResponse.model_validate(conversation)
