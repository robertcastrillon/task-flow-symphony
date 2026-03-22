import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.models.task import Task
from app.models.user import User
from app.schemas.comment import CommentCreate


class CommentService:
    @staticmethod
    async def list_comments(db: AsyncSession, task_id: uuid.UUID) -> list[Comment]:
        """List comments on a task, ordered by creation time."""
        # Verify task exists
        result = await db.execute(
            select(Task).where(Task.id == task_id, Task.is_deleted.is_(False))
        )
        if result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        result = await db.execute(
            select(Comment)
            .where(Comment.task_id == task_id)
            .order_by(Comment.created_at)
        )
        return list(result.scalars().all())

    @staticmethod
    async def create_comment(
        db: AsyncSession,
        task_id: uuid.UUID,
        payload: CommentCreate,
        current_user: User,
    ) -> Comment:
        """Add a comment to a task."""
        # Verify task exists
        result = await db.execute(
            select(Task).where(Task.id == task_id, Task.is_deleted.is_(False))
        )
        if result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        comment = Comment(
            task_id=task_id,
            author_id=current_user.id,
            content=payload.content,
        )
        db.add(comment)
        await db.flush()
        await db.refresh(comment)
        return comment
