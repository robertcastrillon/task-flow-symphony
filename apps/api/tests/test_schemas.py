import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.dashboard import DashboardStats, TaskCountByStatus, TaskCountByUser
from app.schemas.task import (
    PaginatedTaskResponse,
    TaskAssign,
    TaskCreate,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate,
)
from app.schemas.user import UserCreate, UserResponse, UserUpdate


class TestAuthSchemas:
    def test_register_request_valid(self):
        req = RegisterRequest(
            email="test@example.com", name="Test User", password="secure123"
        )
        assert req.email == "test@example.com"
        assert req.name == "Test User"

    def test_register_request_invalid_email(self):
        with pytest.raises(ValidationError):
            RegisterRequest(email="not-an-email", name="Test", password="secure123")

    def test_register_request_short_password(self):
        with pytest.raises(ValidationError):
            RegisterRequest(email="test@example.com", name="Test", password="short")

    def test_register_request_empty_name(self):
        with pytest.raises(ValidationError):
            RegisterRequest(email="test@example.com", name="", password="secure123")

    def test_login_request_valid(self):
        req = LoginRequest(email="test@example.com", password="mypassword")
        assert req.email == "test@example.com"

    def test_login_request_invalid_email(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="not-email", password="password123")

    def test_token_response(self):
        resp = TokenResponse(
            access_token="abc", refresh_token="def", token_type="bearer"
        )
        assert resp.token_type == "bearer"

    def test_refresh_request(self):
        req = RefreshRequest(refresh_token="some-token")
        assert req.refresh_token == "some-token"


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

    def test_user_update_optional_fields(self):
        update = UserUpdate()
        assert update.name is None
        assert update.avatar_url is None

    def test_user_update_with_name(self):
        update = UserUpdate(name="New Name")
        assert update.name == "New Name"

    def test_user_update_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            UserUpdate(name="")

    def test_user_response_from_attributes(self):
        now = datetime.now(tz=UTC)
        uid = uuid.uuid4()
        resp = UserResponse(
            id=uid,
            email="test@example.com",
            name="Test",
            role="member",
            is_active=True,
            created_at=now,
        )
        assert resp.id == uid
        assert resp.email == "test@example.com"
        assert resp.avatar_url is None
        assert resp.telegram_chat_id is None


class TestTaskSchemas:
    def test_task_create_minimal(self):
        task = TaskCreate(title="My Task")
        assert task.title == "My Task"
        assert task.priority.value == "medium"
        assert task.tags == []

    def test_task_create_empty_title(self):
        with pytest.raises(ValidationError):
            TaskCreate(title="")

    def test_task_create_long_title_rejected(self):
        with pytest.raises(ValidationError):
            TaskCreate(title="x" * 256)

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

    def test_task_assign(self):
        uid = uuid.uuid4()
        assign = TaskAssign(assigned_to=uid)
        assert assign.assigned_to == uid

    def test_task_assign_unassign(self):
        assign = TaskAssign(assigned_to=None)
        assert assign.assigned_to is None

    def test_task_response(self):
        now = datetime.now(tz=UTC)
        uid = uuid.uuid4()
        resp = TaskResponse(
            id=uuid.uuid4(),
            title="Task",
            status="todo",
            priority="medium",
            created_by=uid,
            is_deleted=False,
            created_at=now,
            updated_at=now,
        )
        assert resp.status.value == "todo"
        assert resp.completed_at is None

    def test_paginated_response(self):
        paginated = PaginatedTaskResponse(
            items=[], total=0, page=1, size=20, pages=0
        )
        assert paginated.total == 0
        assert paginated.items == []


class TestCommentSchemas:
    def test_comment_create_valid(self):
        comment = CommentCreate(content="A comment")
        assert comment.content == "A comment"

    def test_comment_create_empty_rejected(self):
        with pytest.raises(ValidationError):
            CommentCreate(content="")

    def test_comment_response(self):
        now = datetime.now(tz=UTC)
        resp = CommentResponse(
            id=uuid.uuid4(),
            content="Test comment",
            task_id=uuid.uuid4(),
            author_id=uuid.uuid4(),
            created_at=now,
            updated_at=now,
        )
        assert resp.content == "Test comment"


class TestDashboardSchemas:
    def test_task_count_by_status_defaults(self):
        counts = TaskCountByStatus()
        assert counts.todo == 0
        assert counts.in_progress == 0
        assert counts.done == 0
        assert counts.cancelled == 0

    def test_task_count_by_user(self):
        tcu = TaskCountByUser(user_id="123", user_name="Test", count=5)
        assert tcu.count == 5

    def test_dashboard_stats_defaults(self):
        stats = DashboardStats(
            tasks_by_status=TaskCountByStatus(),
        )
        assert stats.total_tasks == 0
        assert stats.overdue_tasks == 0
        assert stats.tasks_by_user == []
