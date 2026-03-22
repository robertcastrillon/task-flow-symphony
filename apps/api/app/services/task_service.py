import math
import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.models.user import User
from app.schemas.task import (
    PaginatedTaskResponse,
    TaskAssign,
    TaskCreate,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate,
)


class TaskService:
    @staticmethod
    async def list_tasks(
        db: AsyncSession,
        *,
        status: str | None = None,
        assignee: uuid.UUID | None = None,
        priority: str | None = None,
        tag: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> PaginatedTaskResponse:
        """Build query from filters, apply pagination, execute."""
        query = select(Task).where(Task.is_deleted.is_(False))

        if status is not None:
            query = query.where(Task.status == status)
        if assignee is not None:
            query = query.where(Task.assigned_to == assignee)
        if priority is not None:
            query = query.where(Task.priority == priority)
        if tag is not None:
            query = query.where(Task.tags.any(tag))

        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0

        query = (
            query.offset((page - 1) * size).limit(size).order_by(Task.created_at.desc())
        )
        result = await db.execute(query)
        items = [TaskResponse.model_validate(t) for t in result.scalars().all()]

        return PaginatedTaskResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=math.ceil(total / size) if size > 0 else 0,
        )

    @staticmethod
    async def create_task(
        db: AsyncSession, payload: TaskCreate, current_user: User
    ) -> Task:
        """Set created_by, set defaults, save."""
        task = Task(
            title=payload.title,
            description=payload.description,
            priority=payload.priority,
            due_date=payload.due_date,
            assigned_to=payload.assigned_to,
            tags=payload.tags,
            created_by=current_user.id,
        )
        db.add(task)
        await db.flush()
        await db.refresh(task)
        return task

    @staticmethod
    async def get_task(db: AsyncSession, task_id: uuid.UUID) -> Task:
        """Find task, raise 404 if not found or deleted."""
        result = await db.execute(
            select(Task).where(Task.id == task_id, Task.is_deleted.is_(False))
        )
        task = result.scalar_one_or_none()
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        return task

    @staticmethod
    async def update_task(
        db: AsyncSession,
        task_id: uuid.UUID,
        payload: TaskUpdate,
        current_user: User,
    ) -> Task:
        """Find task, validate ownership/admin, update fields."""
        task = await TaskService.get_task(db, task_id)
        TaskService._check_permission(task, current_user)

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        await db.flush()
        await db.refresh(task)
        return task

    @staticmethod
    async def delete_task(
        db: AsyncSession, task_id: uuid.UUID, current_user: User
    ) -> None:
        """Find task, validate ownership/admin, set soft delete flag."""
        task = await TaskService.get_task(db, task_id)
        TaskService._check_permission(task, current_user)
        task.is_deleted = True
        await db.flush()

    @staticmethod
    async def change_status(
        db: AsyncSession,
        task_id: uuid.UUID,
        payload: TaskStatusUpdate,
        current_user: User,
    ) -> Task:
        """Find task, update status, set completed_at if done."""
        task = await TaskService.get_task(db, task_id)
        task.status = payload.status

        if payload.status == "done":
            task.completed_at = datetime.now(tz=UTC)
        elif task.completed_at is not None:
            task.completed_at = None

        await db.flush()
        await db.refresh(task)
        return task

    @staticmethod
    async def assign_task(
        db: AsyncSession,
        task_id: uuid.UUID,
        payload: TaskAssign,
        current_user: User,
    ) -> Task:
        """Find task, validate permissions and assignee, update assigned_to.

        Members can only assign tasks to themselves. Admins can assign freely.
        """
        task = await TaskService.get_task(db, task_id)

        # Members can only self-assign; admins can assign to anyone
        if (
            payload.assigned_to is not None
            and payload.assigned_to != current_user.id
            and current_user.role != "admin"
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Members can only assign tasks to themselves",
            )

        if payload.assigned_to is not None:
            result = await db.execute(
                select(User).where(User.id == payload.assigned_to)
            )
            if result.scalar_one_or_none() is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Assignee not found",
                )

        task.assigned_to = payload.assigned_to
        await db.flush()
        await db.refresh(task)
        return task

    @staticmethod
    def _check_permission(task: Task, current_user: User) -> None:
        """Validate ownership or admin role."""
        if task.created_by != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this task",
            )
