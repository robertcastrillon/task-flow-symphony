import uuid
from datetime import datetime
<<<<<<< HEAD

from pydantic import BaseModel, Field

from app.models.task import TaskPriority, TaskStatus
=======
from enum import StrEnum

from pydantic import BaseModel, Field


class TaskStatus(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
>>>>>>> origin/eng-88


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
<<<<<<< HEAD
    priority: TaskPriority = TaskPriority.medium
    due_date: datetime | None = None
    assigned_to: uuid.UUID | None = None
    tags: list[str] = Field(default_factory=list)
=======
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: datetime | None = None
    tags: list[str] | None = None
    assigned_to: uuid.UUID | None = None
>>>>>>> origin/eng-88


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    priority: TaskPriority | None = None
    due_date: datetime | None = None
    tags: list[str] | None = None


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskAssign(BaseModel):
<<<<<<< HEAD
    assigned_to: uuid.UUID | None


class TaskResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    due_date: datetime | None
    created_by: uuid.UUID
    assigned_to: uuid.UUID | None
    tags: list[str] | None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
=======
    assigned_to: uuid.UUID | None = None


class TaskResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None = None
    status: TaskStatus
    priority: TaskPriority
    due_date: datetime | None = None
    tags: list[str] | None = None
    is_deleted: bool
    created_by: uuid.UUID
    assigned_to: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}
>>>>>>> origin/eng-88


class PaginatedTaskResponse(BaseModel):
    items: list[TaskResponse]
    total: int
    page: int
    size: int
<<<<<<< HEAD
=======
    pages: int
>>>>>>> origin/eng-88
