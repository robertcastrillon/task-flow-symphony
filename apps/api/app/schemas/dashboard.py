from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_tasks: int
    tasks_by_status: dict[str, int]
    tasks_by_priority: dict[str, int]
    overdue_tasks: int
    tasks_completed_today: int
