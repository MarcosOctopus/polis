"""Template router — CRUD endpoints + variable rendering."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Tenant, User as UserModel
from src.modules.auth.dependencies import get_current_tenant, get_current_user, get_db
from src.modules.templates.schemas import (
    PaginatedTemplates,
    TemplateCreate,
    TemplateOut,
    TemplateRenderRequest,
    TemplateRenderResponse,
    TemplateUpdate,
)
from src.modules.templates.service import TemplateService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/templates", tags=["Templates"])


@router.post("", response_model=TemplateOut, status_code=status.HTTP_201_CREATED)
async def create_template(
    body: TemplateCreate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Create a new message template."""
    template = await TemplateService.create(db, tenant.id, current_user.id, body)
    return TemplateOut.model_validate(template)


@router.get("", response_model=PaginatedTemplates)
async def list_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    channel: str | None = Query(None, pattern="^(whatsapp|sms|email)$"),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """List templates for the current tenant, optionally filtered by channel."""
    templates, total = await TemplateService.list(
        db, tenant.id, skip=skip, limit=limit, channel=channel
    )
    return PaginatedTemplates(
        items=[TemplateOut.model_validate(t) for t in templates],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{template_id}", response_model=TemplateOut)
async def get_template(
    template_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Get a specific template by ID."""
    template = await TemplateService.get(db, template_id, tenant.id)
    if template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    return TemplateOut.model_validate(template)


@router.put("/{template_id}", response_model=TemplateOut)
async def update_template(
    template_id: str,
    body: TemplateUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Update a template."""
    template = await TemplateService.update(db, template_id, body, tenant.id)
    if template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    return TemplateOut.model_validate(template)


@router.delete("/{template_id}", status_code=status.HTTP_200_OK)
async def delete_template(
    template_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Delete a template."""
    success = await TemplateService.delete(db, template_id, tenant.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    return {"detail": "Template deleted successfully"}


@router.post("/{template_id}/render", response_model=TemplateRenderResponse)
async def render_template(
    template_id: str,
    body: TemplateRenderRequest,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Render a template with variable substitution."""
    result = await TemplateService.render(
        db, template_id, body.variables or {}, tenant.id
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    return result
