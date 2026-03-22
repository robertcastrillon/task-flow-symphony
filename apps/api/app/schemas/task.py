import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.task import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    priority: TaskPriority = TaskPriority.medium
    due_date: datetime | None = None
    assigned_to: uuid.UUID | None = None
    tags: list[str] = Field(default_factory=list)


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    priority: TaskPriority | None = None
    due_date: datetime | None = None
    tags: list[str] | None = None


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskAssign(BaseModel):
    assigned_to: uuid.UUID | None = None


class TaskResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    title: str
    description: str | None = None
    status: TaskStatus
    priority: TaskPriority
    due_date: datetime | None = None
    created_by: uuid.UUID
    assigned_to: uuid.UUID | None = None
    tags: list[str] | None = None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None


class PaginatedTaskResponse(BaseModel):
    items: list[TaskResponse]
    total: int
    page: int
    size: int
    pages: int
