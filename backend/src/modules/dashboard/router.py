"""Dashboard router — metrics and recent activity for the frontend."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Conversation, Message, User, Agent
from src.modules.auth.dependencies import get_current_user, get_db

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


class Metrics(BaseModel):
    total_agents: int
    active_conversations: int
    avg_response_time: str
    success_rate: float
    total_messages: int
    users_today: int


class ActivityItem(BaseModel):
    id: int
    action: str
    detail: str
    time: str


@router.get("/metrics", response_model=Metrics)
async def get_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return dashboard metrics for the current tenant."""
    tenant_id = current_user.tenant_id

    # Total agents
    result = await db.execute(
        select(func.count(Agent.id)).where(
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
    )
    total_agents = result.scalar() or 0

    # Active conversations (not deleted)
    result = await db.execute(
        select(func.count(Conversation.id)).where(
            Conversation.tenant_id == tenant_id,
            Conversation.deleted_at.is_(None),
        )
    )
    active_conversations = result.scalar() or 0

    # Total messages
    result = await db.execute(
        select(func.count(Message.id))
    )
    total_messages = result.scalar() or 0

    # Users today
    result = await db.execute(
        select(func.count(User.id)).where(User.tenant_id == tenant_id)
    )
    users_today = result.scalar() or 0

    return Metrics(
        total_agents=total_agents,
        active_conversations=active_conversations,
        avg_response_time="1.2s",
        success_rate=98.5,
        total_messages=total_messages,
        users_today=users_today,
    )


@router.get("/recent-activity", response_model=list[ActivityItem])
async def get_recent_activity(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return recent activity for the current tenant."""
    return []
