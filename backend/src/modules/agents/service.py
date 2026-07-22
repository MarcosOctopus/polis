"""Agent service — CRUD with search and soft delete."""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Agent
from src.modules.agents.schemas import AgentCreate, AgentUpdate


class AgentService:
    """Business logic for AI agent management."""

    @staticmethod
    async def create(
        db: AsyncSession, tenant_id: str, data: AgentCreate
    ) -> Agent:
        agent = Agent(
            tenant_id=tenant_id,
            name=data.name,
            description=data.description,
            model=data.model,
            system_prompt=data.system_prompt,
            temperature=data.temperature or 0.7,
            config=data.config,
        )
        db.add(agent)
        await db.flush()
        await db.refresh(agent)
        return agent

    @staticmethod
    async def get_by_id(
        db: AsyncSession, agent_id: str, tenant_id: str | None = None
    ) -> Agent | None:
        query = select(Agent).where(
            Agent.id == agent_id,
            Agent.deleted_at.is_(None),
        )
        if tenant_id:
            query = query.where(Agent.tenant_id == tenant_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_tenant(
        db: AsyncSession,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        model: str | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[Agent], int]:
        query = select(Agent).where(
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        if search:
            query = query.where(
                Agent.name.ilike(f"%{search}%")
                | Agent.description.ilike(f"%{search}%")
            )
        if model:
            query = query.where(Agent.model == model)
        if is_active is not None:
            query = query.where(Agent.is_active == is_active)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Agent.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        agents = list(result.scalars().all())
        return agents, total

    @staticmethod
    async def update(
        db: AsyncSession,
        agent_id: str,
        data: AgentUpdate,
        tenant_id: str | None = None,
    ) -> Agent | None:
        agent = await AgentService.get_by_id(db, agent_id, tenant_id)
        if agent is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(agent, key, value)

        await db.flush()
        await db.refresh(agent)
        return agent

    @staticmethod
    async def soft_delete(
        db: AsyncSession, agent_id: str, tenant_id: str | None = None
    ) -> bool:
        agent = await AgentService.get_by_id(db, agent_id, tenant_id)
        if agent is None:
            return False
        agent.deleted_at = datetime.now(timezone.utc)
        await db.flush()
        return True
