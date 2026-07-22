"""Task service — CRUD with filters and kanban-style grouping."""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Task
from src.modules.tasks.schemas import TaskCreate, TaskUpdate


class TaskService:
    """Business logic for task management."""

    STATUS_ORDER = {"todo": 0, "in_progress": 1, "blocked": 2, "done": 3}

    @staticmethod
    async def create(
        db: AsyncSession, tenant_id: str, data: TaskCreate
    ) -> Task:
        task = Task(
            tenant_id=tenant_id,
            title=data.title,
            description=data.description,
            assignee_id=data.assignee_id,
            status=data.status or "todo",
            priority=data.priority or "medium",
            deadline=data.deadline,
            event_id=data.event_id,
            protocol_id=data.protocol_id,
            order=data.order or 0,
            metadata=data.metadata,
        )
        db.add(task)
        await db.flush()
        await db.refresh(task)
        return task

    @staticmethod
    async def get_by_id(
        db: AsyncSession, task_id: str, tenant_id: str | None = None
    ) -> Task | None:
        query = select(Task).where(
            Task.id == task_id,
            Task.deleted_at.is_(None),
        )
        if tenant_id:
            query = query.where(Task.tenant_id == tenant_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_tenant(
        db: AsyncSession,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
        assignee_id: str | None = None,
        priority: str | None = None,
        protocol_id: str | None = None,
        search: str | None = None,
    ) -> tuple[list[Task], int]:
        query = select(Task).where(
            Task.tenant_id == tenant_id,
            Task.deleted_at.is_(None),
        )
        if status:
            query = query.where(Task.status == status)
        if assignee_id:
            query = query.where(Task.assignee_id == assignee_id)
        if priority:
            query = query.where(Task.priority == priority)
        if protocol_id:
            query = query.where(Task.protocol_id == protocol_id)
        if search:
            query = query.where(Task.title.ilike(f"%{search}%"))

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Task.order.asc(), Task.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        tasks = list(result.scalars().all())
        return tasks, total

    @staticmethod
    async def get_kanban(
        db: AsyncSession,
        tenant_id: str,
        assignee_id: str | None = None,
    ) -> list[tuple[str, list[Task]]]:
        """Get tasks grouped by status for kanban board view."""
        columns = {}
        for status_val in ("todo", "in_progress", "blocked", "done"):
            query = select(Task).where(
                Task.tenant_id == tenant_id,
                Task.status == status_val,
                Task.deleted_at.is_(None),
            )
            if assignee_id:
                query = query.where(Task.assignee_id == assignee_id)
            query = query.order_by(Task.order.asc(), Task.created_at.desc())
            result = await db.execute(query)
            columns[status_val] = list(result.scalars().all())
        return list(columns.items())

    @staticmethod
    async def update(
        db: AsyncSession,
        task_id: str,
        data: TaskUpdate,
        tenant_id: str | None = None,
    ) -> Task | None:
        task = await TaskService.get_by_id(db, task_id, tenant_id)
        if task is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(task, key, value)

        await db.flush()
        await db.refresh(task)
        return task

    @staticmethod
    async def soft_delete(
        db: AsyncSession, task_id: str, tenant_id: str | None = None
    ) -> bool:
        task = await TaskService.get_by_id(db, task_id, tenant_id)
        if task is None:
            return False
        task.deleted_at = datetime.now(timezone.utc)
        await db.flush()
        return True

    @staticmethod
    async def reorder(
        db: AsyncSession,
        task_id: str,
        new_order: int,
        new_status: str | None = None,
        tenant_id: str | None = None,
    ) -> Task | None:
        """Reorder a task and optionally move it to a different status column."""
        task = await TaskService.get_by_id(db, task_id, tenant_id)
        if task is None:
            return None

        task.order = new_order
        if new_status:
            task.status = new_status
        await db.flush()
        await db.refresh(task)
        return task
