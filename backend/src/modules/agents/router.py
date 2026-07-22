"""Agent router — CRUD endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Tenant, User as UserModel
from src.modules.auth.dependencies import get_current_tenant, get_current_user, get_db
from src.modules.agents.schemas import (
    AgentCreate,
    AgentList,
    AgentResponse,
    AgentUpdate,
)
from src.modules.agents.service import AgentService

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    body: AgentCreate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Create a new AI agent."""
    agent = await AgentService.create(db, tenant.id, body)
    return AgentResponse.model_validate(agent)


@router.get("", response_model=AgentList)
async def list_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: str | None = Query(None),
    model: str | None = Query(None),
    is_active: bool | None = Query(None),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """List agents with optional search and filters."""
    agents, total = await AgentService.list_by_tenant(
        db,
        tenant.id,
        skip=skip,
        limit=limit,
        search=search,
        model=model,
        is_active=is_active,
    )
    return AgentList(
        items=[AgentResponse.model_validate(a) for a in agents],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Get a specific agent by ID."""
    agent = await AgentService.get_by_id(db, agent_id, tenant.id)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    return AgentResponse.model_validate(agent)


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    body: AgentUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Update an agent."""
    agent = await AgentService.update(db, agent_id, body, tenant.id)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    return AgentResponse.model_validate(agent)


@router.delete("/{agent_id}", status_code=status.HTTP_200_OK)
async def delete_agent(
    agent_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Soft-delete an agent."""
    success = await AgentService.soft_delete(db, agent_id, tenant.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    return {"detail": "Agent deleted successfully"}
