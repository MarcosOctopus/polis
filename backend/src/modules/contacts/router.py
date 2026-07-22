"""Contact router — CRUD endpoints + tag management."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Tenant, User as UserModel
from src.modules.auth.dependencies import get_current_tenant, get_current_user, get_db
from src.modules.contacts.schemas import (
    AddTagsRequest,
    ContactCreate,
    ContactList,
    ContactResponse,
    ContactUpdate,
    RemoveTagsRequest,
)
from src.modules.contacts.service import ContactService

router = APIRouter(prefix="/contacts", tags=["Contacts"])


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactCreate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Create a new contact for the current tenant."""
    contact = await ContactService.create(db, tenant.id, body)
    return ContactResponse.model_validate(contact)


@router.get("", response_model=ContactList)
async def list_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: str | None = Query(None),
    tags: str | None = Query(None, description="Comma-separated tags"),
    city: str | None = Query(None),
    state: str | None = Query(None),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """List contacts for the current tenant with optional filters."""
    tag_list = tags.split(",") if tags else None
    contacts, total = await ContactService.list_by_tenant(
        db,
        tenant.id,
        skip=skip,
        limit=limit,
        search=search,
        tags=tag_list,
        city=city,
        state=state,
    )
    return ContactList(
        items=[ContactResponse.model_validate(c) for c in contacts],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Get a specific contact by ID."""
    contact = await ContactService.get_by_id(db, contact_id, tenant.id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    return ContactResponse.model_validate(contact)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: str,
    body: ContactUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Update a contact."""
    contact = await ContactService.update(db, contact_id, body, tenant.id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    return ContactResponse.model_validate(contact)


@router.delete("/{contact_id}", status_code=status.HTTP_200_OK)
async def delete_contact(
    contact_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Soft-delete a contact."""
    success = await ContactService.soft_delete(db, contact_id, tenant.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    return {"detail": "Contact deleted successfully"}


@router.post("/{contact_id}/tags", response_model=ContactResponse)
async def add_tags(
    contact_id: str,
    body: AddTagsRequest,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Add tags to a contact."""
    contact = await ContactService.add_tags(db, contact_id, body.tags, tenant.id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    return ContactResponse.model_validate(contact)


@router.delete("/{contact_id}/tags", response_model=ContactResponse)
async def remove_tags(
    contact_id: str,
    body: RemoveTagsRequest,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Remove tags from a contact."""
    contact = await ContactService.remove_tags(db, contact_id, body.tags, tenant.id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    return ContactResponse.model_validate(contact)
