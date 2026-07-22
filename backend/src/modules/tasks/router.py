"""Task router — CRUD + kanban board endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Tenant, User as UserModel
from src.modules.auth.dependencies import get_current_tenant, get_current_user, get_db
from src.modules.tasks.schemas import (
    KanbanBoard,
    KanbanColumn,
    TaskCreate,
    TaskList,
    TaskResponse,
    TaskUpdate,
)
from src.modules.tasks.service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    body: TaskCreate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Create a new task."""
    task = await TaskService.create(db, tenant.id, body)
    return TaskResponse.model_validate(task)


@router.get("", response_model=TaskList)
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: str | None = Query(None),
    assignee_id: str | None = Query(None),
    priority: str | None = Query(None),
    protocol_id: str | None = Query(None),
    search: str | None = Query(None),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """List tasks with optional filters."""
    tasks, total = await TaskService.list_by_tenant(
        db,
        tenant.id,
        skip=skip,
        limit=limit,
        status=status,
        assignee_id=assignee_id,
        priority=priority,
        protocol_id=protocol_id,
        search=search,
    )
    return TaskList(
        items=[TaskResponse.model_validate(t) for t in tasks],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/kanban", response_model=KanbanBoard)
async def kanban_board(
    assignee_id: str | None = Query(None),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Get tasks grouped by status for kanban board view."""
    columns_data = await TaskService.get_kanban(db, tenant.id, assignee_id=assignee_id)
    columns = [
        KanbanColumn(
            status=status,
            items=[TaskResponse.model_validate(t) for t in tasks],
            count=len(tasks),
        )
        for status, tasks in columns_data
    ]
    return KanbanBoard(columns=columns)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Get a specific task by ID."""
    task = await TaskService.get_by_id(db, task_id, tenant.id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return TaskResponse.model_validate(task)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    body: TaskUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Update a task."""
    task = await TaskService.update(db, task_id, body, tenant.id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(
    task_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Soft-delete a task."""
    success = await TaskService.soft_delete(db, task_id, tenant.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return {"detail": "Task deleted successfully"}


@router.put("/{task_id}/reorder", response_model=TaskResponse)
async def reorder_task(
    task_id: str,
    body: dict,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    _current_user: UserModel = Depends(get_current_user),
):
    """Reorder a task and optionally move it to a different status."""
    new_order = body.get("order", 0)
    new_status = body.get("status")
    task = await TaskService.reorder(db, task_id, new_order, new_status, tenant.id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return TaskResponse.model_validate(task)
