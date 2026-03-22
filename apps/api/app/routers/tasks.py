import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.task import (
    PaginatedTaskResponse,
    TaskAssign,
    TaskCreate,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate,
)
from app.services.task_service import TaskService

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.get("", response_model=PaginatedTaskResponse)
async def list_tasks(
    status: str | None = None,
    assignee: uuid.UUID | None = None,
    priority: str | None = None,
    tag: str | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedTaskResponse:
    """List tasks with filters and pagination."""
    return await TaskService.list_tasks(
        db,
        status=status,
        assignee=assignee,
        priority=priority,
        tag=tag,
        page=page,
        size=size,
    )


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    payload: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    """Create a new task."""
    task = await TaskService.create_task(db, payload, current_user)
    return TaskResponse.model_validate(task)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    """Get task detail."""
    task = await TaskService.get_task(db, task_id)
    return TaskResponse.model_validate(task)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    payload: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    """Update task fields."""
    task = await TaskService.update_task(db, task_id, payload, current_user)
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Soft delete a task."""
    await TaskService.delete_task(db, task_id, current_user)


@router.patch("/{task_id}/status", response_model=TaskResponse)
async def change_status(
    task_id: uuid.UUID,
    payload: TaskStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    """Change task status."""
    task = await TaskService.change_status(db, task_id, payload, current_user)
    return TaskResponse.model_validate(task)


@router.patch("/{task_id}/assign", response_model=TaskResponse)
async def assign_task(
    task_id: uuid.UUID,
    payload: TaskAssign,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    """Assign or reassign a task."""
    task = await TaskService.assign_task(db, task_id, payload, current_user)
    return TaskResponse.model_validate(task)
