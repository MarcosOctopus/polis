"""Knowledge router — CRUD endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Tenant, User as UserModel
from src.modules.auth.dependencies import get_current_tenant, get_current_user, get_db
from src.modules.knowledge.schemas import (
    KnowledgeBaseCreate,
    KnowledgeBaseList,
    KnowledgeBaseResponse,
    KnowledgeBaseUpdate,
)
from src.modules.knowledge.service import KnowledgeService

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])


@router.post("", response_model=KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(
    body: KnowledgeBaseCreate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Create a new knowledge base entry."""
    kb = await KnowledgeService.create(db, tenant.id, body)
    return KnowledgeBaseResponse.model_validate(kb)


@router.get("", response_model=KnowledgeBaseList)
async def list_knowledge_bases(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: str | None = Query(None),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """List knowledge base entries with optional search."""
    items, total = await KnowledgeService.list_by_tenant(
        db,
        tenant.id,
        skip=skip,
        limit=limit,
        search=search,
    )
    return KnowledgeBaseList(
        items=[KnowledgeBaseResponse.model_validate(k) for k in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    kb_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Get a specific knowledge base entry by ID."""
    kb = await KnowledgeService.get_by_id(db, kb_id, tenant.id)
    if kb is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base entry not found",
        )
    return KnowledgeBaseResponse.model_validate(kb)


@router.put("/{kb_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_base(
    kb_id: str,
    body: KnowledgeBaseUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Update a knowledge base entry."""
    kb = await KnowledgeService.update(db, kb_id, body, tenant.id)
    if kb is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base entry not found",
        )
    return KnowledgeBaseResponse.model_validate(kb)


@router.delete("/{kb_id}", status_code=status.HTTP_200_OK)
async def delete_knowledge_base(
    kb_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Soft-delete a knowledge base entry."""
    success = await KnowledgeService.soft_delete(db, kb_id, tenant.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base entry not found",
        )
    return {"detail": "Knowledge base entry deleted successfully"}
