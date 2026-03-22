from pydantic import BaseModel


<<<<<<< HEAD
class DashboardStats(BaseModel):
    total_tasks: int
    tasks_by_status: dict[str, int]
    tasks_by_priority: dict[str, int]
    overdue_tasks: int
    tasks_completed_today: int
=======
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
>>>>>>> origin/eng-88
