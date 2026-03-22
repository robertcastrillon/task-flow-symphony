import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.dashboard import DashboardStats
from app.schemas.task import (
    PaginatedTaskResponse,
    TaskCreate,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate,
)
from app.schemas.user import UserCreate, UserResponse, UserUpdate


class TestUserSchemas:
    def test_user_create_valid(self):
        user = UserCreate(
            email="test@example.com", name="Test User", password="securepass123"
        )
        assert user.email == "test@example.com"
        assert user.name == "Test User"

    def test_user_create_invalid_email(self):
        with pytest.raises(ValidationError):
            UserCreate(email="not-an-email", name="Test", password="securepass123")

    def test_user_create_short_password(self):
        with pytest.raises(ValidationError):
            UserCreate(email="test@example.com", name="Test", password="short")

    def test_user_create_empty_name(self):
        with pytest.raises(ValidationError):
            UserCreate(email="test@example.com", name="", password="securepass123")

    def test_user_update_partial(self):
        update = UserUpdate(name="New Name")
        assert update.name == "New Name"
        assert update.avatar_url is None

    def test_user_response_from_attributes(self):
        now = datetime.now(tz=UTC)
        resp = UserResponse(
            id=uuid.uuid4(),
            email="test@example.com",
            name="Test",
            avatar_url=None,
            role="member",
            is_active=True,
            created_at=now,
        )
        assert resp.email == "test@example.com"


class TestTaskSchemas:
    def test_task_create_minimal(self):
        task = TaskCreate(title="My Task")
        assert task.title == "My Task"
        assert task.priority.value == "medium"
        assert task.tags == []

    def test_task_create_empty_title(self):
        with pytest.raises(ValidationError):
            TaskCreate(title="")

    def test_task_create_full(self):
        uid = uuid.uuid4()
        task = TaskCreate(
            title="Full Task",
            description="A description",
            priority="high",
            assigned_to=uid,
            tags=["backend", "urgent"],
        )
        assert task.assigned_to == uid
        assert len(task.tags) == 2

    def test_task_update_partial(self):
        update = TaskUpdate(title="Updated")
        assert update.title == "Updated"
        assert update.priority is None

    def test_task_status_update(self):
        update = TaskStatusUpdate(status="done")
        assert update.status.value == "done"

    def test_task_status_update_invalid(self):
        with pytest.raises(ValidationError):
            TaskStatusUpdate(status="invalid_status")

    def test_task_response(self):
        now = datetime.now(tz=UTC)
        uid = uuid.uuid4()
        resp = TaskResponse(
            id=uuid.uuid4(),
            title="Task",
            description=None,
            status="todo",
            priority="medium",
            due_date=None,
            created_by=uid,
            assigned_to=None,
            tags=[],
            is_deleted=False,
            created_at=now,
            updated_at=now,
            completed_at=None,
        )
        assert resp.status.value == "todo"

    def test_paginated_response(self):
        paginated = PaginatedTaskResponse(items=[], total=0, page=1, size=20)
        assert paginated.total == 0


class TestCommentSchemas:
    def test_comment_create_valid(self):
        comment = CommentCreate(content="A comment")
        assert comment.content == "A comment"

    def test_comment_create_empty(self):
        with pytest.raises(ValidationError):
            CommentCreate(content="")

    def test_comment_response(self):
        now = datetime.now(tz=UTC)
        resp = CommentResponse(
            id=uuid.uuid4(),
            task_id=uuid.uuid4(),
            author_id=uuid.uuid4(),
            content="Comment",
            created_at=now,
            updated_at=now,
        )
        assert resp.content == "Comment"


class TestAuthSchemas:
    def test_login_request(self):
        login = LoginRequest(email="test@example.com", password="password123")
        assert login.email == "test@example.com"

    def test_login_invalid_email(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="not-email", password="password123")

    def test_token_response(self):
        token = TokenResponse(
            access_token="abc", refresh_token="def", token_type="bearer"
        )
        assert token.token_type == "bearer"


class TestDashboardSchemas:
    def test_dashboard_stats(self):
        stats = DashboardStats(
            total_tasks=10,
            tasks_by_status={"todo": 3, "in_progress": 4, "done": 3},
            tasks_by_priority={"low": 2, "medium": 5, "high": 3},
            overdue_tasks=1,
            tasks_completed_today=2,
        )
        assert stats.total_tasks == 10
        assert stats.overdue_tasks == 1
        assert stats.tasks_by_status["todo"] == 3
