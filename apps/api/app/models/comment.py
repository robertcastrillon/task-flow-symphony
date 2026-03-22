<<<<<<< HEAD
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
=======
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.user import User
>>>>>>> origin/eng-88


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
<<<<<<< HEAD
=======
    content: Mapped[str] = mapped_column(Text, nullable=False)
>>>>>>> origin/eng-88
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False, index=True
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
<<<<<<< HEAD
    content: Mapped[str] = mapped_column(String, nullable=False)
=======
>>>>>>> origin/eng-88
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

<<<<<<< HEAD
    task: Mapped["Task"] = relationship(back_populates="comments")  # noqa: F821
    author: Mapped["User"] = relationship(back_populates="comments")  # noqa: F821
=======
    task: Mapped[Task] = relationship("Task", back_populates="comments")
    author: Mapped[User] = relationship("User", back_populates="comments")

    def __repr__(self) -> str:
        id_ = self.__dict__.get("id", "?")
        return f"<Comment {id_}>"
>>>>>>> origin/eng-88
