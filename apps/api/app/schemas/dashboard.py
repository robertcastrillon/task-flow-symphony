from pydantic import BaseModel


class TaskCountByStatus(BaseModel):
    todo: int = 0
    in_progress: int = 0
    done: int = 0
    cancelled: int = 0


class TaskCountByUser(BaseModel):
    user_id: str
    user_name: str
    count: int


class DashboardStats(BaseModel):
    total_tasks: int = 0
    tasks_by_status: TaskCountByStatus
    overdue_tasks: int = 0
    tasks_by_user: list[TaskCountByUser] = []
