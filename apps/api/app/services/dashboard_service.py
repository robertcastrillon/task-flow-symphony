from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.models.user import User
from app.schemas.dashboard import DashboardStats, TaskCountByStatus, TaskCountByUser


class DashboardService:
    @staticmethod
    async def get_stats(db: AsyncSession) -> DashboardStats:
        """Aggregate task statistics."""
        base_query = select(Task).where(Task.is_deleted.is_(False))

        # Total tasks
        total_result = await db.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total_tasks = total_result.scalar() or 0

        # Tasks by status
        status_result = await db.execute(
            select(Task.status, func.count())
            .where(Task.is_deleted.is_(False))
            .group_by(Task.status)
        )
        status_counts = dict(status_result.all())
        tasks_by_status = TaskCountByStatus(
            todo=status_counts.get("todo", 0),
            in_progress=status_counts.get("in_progress", 0),
            done=status_counts.get("done", 0),
            cancelled=status_counts.get("cancelled", 0),
        )

        # Tasks by priority
        priority_result = await db.execute(
            select(Task.priority, func.count())
            .where(Task.is_deleted.is_(False))
            .group_by(Task.priority)
        )
        tasks_by_priority = dict(priority_result.all())

        # Overdue tasks
        now = datetime.now(tz=UTC)
        overdue_result = await db.execute(
            select(func.count())
            .where(
                Task.is_deleted.is_(False),
                Task.due_date < now,
                Task.status.notin_(["done", "cancelled"]),
            )
        )
        overdue_tasks = overdue_result.scalar() or 0

        # Tasks by user
        user_result = await db.execute(
            select(User.id, User.name, func.count(Task.id))
            .join(Task, Task.assigned_to == User.id)
            .where(Task.is_deleted.is_(False))
            .group_by(User.id, User.name)
        )
        tasks_by_user = [
            TaskCountByUser(user_id=str(row[0]), user_name=row[1], count=row[2])
            for row in user_result.all()
        ]

        return DashboardStats(
            total_tasks=total_tasks,
            tasks_by_status=tasks_by_status,
            tasks_by_priority=tasks_by_priority,
            overdue_tasks=overdue_tasks,
            tasks_by_user=tasks_by_user,
        )
