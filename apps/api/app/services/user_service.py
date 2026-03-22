import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserUpdate


class UserService:
    @staticmethod
    async def list_users(db: AsyncSession) -> list[User]:
        """Query active users."""
        result = await db.execute(
            select(User).where(User.is_active.is_(True)).order_by(User.name)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_user(db: AsyncSession, user_id: uuid.UUID) -> User:
        """Find by ID, raise 404 if not found."""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user

    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id: uuid.UUID,
        payload: UserUpdate,
        current_user: User,
    ) -> User:
        """Validate permissions (own profile or admin), update fields."""
        if current_user.id != user_id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only update own profile or require admin",
            )

        user = await UserService.get_user(db, user_id)
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await db.flush()
        await db.refresh(user)
        return user
