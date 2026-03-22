from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.comment import Comment
    from app.models.task import Task


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="member")
    telegram_chat_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True, unique=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    created_tasks: Mapped[list[Task]] = relationship(
        "Task",
        back_populates="creator",
        foreign_keys="Task.created_by",
    )
    assigned_tasks: Mapped[list[Task]] = relationship(
        "Task",
        back_populates="assignee",
        foreign_keys="Task.assigned_to",
    )
    comments: Mapped[list[Comment]] = relationship("Comment", back_populates="author")

    def __repr__(self) -> str:
        email = self.__dict__.get("email", "?")
        return f"<User {email}>"
