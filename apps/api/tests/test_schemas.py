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
    TaskPriority,
    TaskResponse,
    TaskStatus,
    TaskStatusUpdate,
    TaskUpdate,
)
from app.schemas.user import UserResponse, UserUpdate


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

    def test_register_request_long_name(self):
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="test@example.com", name="x" * 256, password="secure123"
            )

    def test_register_request_long_password(self):
        with pytest.raises(ValidationError):
            RegisterRequest(email="test@example.com", name="Test", password="x" * 129)

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
        assert resp.access_token == "abc"
        assert resp.refresh_token == "def"

    def test_token_response_default_type(self):
        resp = TokenResponse(access_token="abc", refresh_token="def")
        assert resp.token_type == "bearer"

    def test_refresh_request(self):
        req = RefreshRequest(refresh_token="some-token")
        assert req.refresh_token == "some-token"


class TestUserSchemas:
    def test_user_response_from_attributes(self):
        now = datetime.now(UTC)
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

    def test_user_response_with_optional_fields(self):
        now = datetime.now(UTC)
        resp = UserResponse(
            id=uuid.uuid4(),
            email="test@example.com",
            name="Test",
            avatar_url="https://example.com/avatar.png",
            role="admin",
            telegram_chat_id="12345",
            is_active=True,
            created_at=now,
        )
        assert resp.avatar_url == "https://example.com/avatar.png"
        assert resp.telegram_chat_id == "12345"
        assert resp.role == "admin"

    def test_user_update_optional_fields(self):
        update = UserUpdate()
        assert update.name is None
        assert update.avatar_url is None

    def test_user_update_with_name(self):
        update = UserUpdate(name="New Name")
        assert update.name == "New Name"

    def test_user_update_with_avatar(self):
        update = UserUpdate(avatar_url="https://example.com/avatar.png")
        assert update.avatar_url == "https://example.com/avatar.png"

    def test_user_update_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            UserUpdate(name="")

    def test_user_update_long_name_rejected(self):
        with pytest.raises(ValidationError):
            UserUpdate(name="x" * 256)

    def test_user_update_long_avatar_url_rejected(self):
        with pytest.raises(ValidationError):
            UserUpdate(avatar_url="x" * 501)


class TestTaskSchemas:
    def test_task_status_values(self):
        assert TaskStatus.TODO == "todo"
        assert TaskStatus.IN_PROGRESS == "in_progress"
        assert TaskStatus.DONE == "done"
        assert TaskStatus.CANCELLED == "cancelled"

    def test_task_priority_values(self):
        assert TaskPriority.LOW == "low"
        assert TaskPriority.MEDIUM == "medium"
        assert TaskPriority.HIGH == "high"
        assert TaskPriority.URGENT == "urgent"

    def test_task_create_minimal(self):
        task = TaskCreate(title="My task")
        assert task.title == "My task"
        assert task.priority == TaskPriority.MEDIUM
        assert task.description is None
        assert task.due_date is None
        assert task.tags is None
        assert task.assigned_to is None

    def test_task_create_empty_title_rejected(self):
        with pytest.raises(ValidationError):
            TaskCreate(title="")

    def test_task_create_long_title_rejected(self):
        with pytest.raises(ValidationError):
            TaskCreate(title="x" * 256)

    def test_task_create_full(self):
        uid = uuid.uuid4()
        now = datetime.now(UTC)
        task = TaskCreate(
            title="Full task",
            description="A description",
            priority=TaskPriority.HIGH,
            due_date=now,
            tags=["frontend", "design"],
            assigned_to=uid,
        )
        assert task.priority == TaskPriority.HIGH
        assert task.tags == ["frontend", "design"]
        assert task.assigned_to == uid
        assert task.description == "A description"
        assert task.due_date == now

    def test_task_update_all_optional(self):
        update = TaskUpdate()
        assert update.title is None
        assert update.priority is None
        assert update.description is None
        assert update.due_date is None
        assert update.tags is None

    def test_task_update_with_values(self):
        update = TaskUpdate(title="Updated", priority=TaskPriority.URGENT)
        assert update.title == "Updated"
        assert update.priority == TaskPriority.URGENT

    def test_task_update_empty_title_rejected(self):
        with pytest.raises(ValidationError):
            TaskUpdate(title="")

    def test_task_update_long_title_rejected(self):
        with pytest.raises(ValidationError):
            TaskUpdate(title="x" * 256)

    def test_task_status_update(self):
        su = TaskStatusUpdate(status=TaskStatus.IN_PROGRESS)
        assert su.status == TaskStatus.IN_PROGRESS

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
        now = datetime.now(UTC)
        uid = uuid.uuid4()
        resp = TaskResponse(
            id=uuid.uuid4(),
            title="Test",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            is_deleted=False,
            created_by=uid,
            created_at=now,
            updated_at=now,
        )
        assert resp.status == TaskStatus.TODO
        assert resp.completed_at is None
        assert resp.description is None
        assert resp.tags is None
        assert resp.assigned_to is None

    def test_task_response_with_all_fields(self):
        now = datetime.now(UTC)
        uid = uuid.uuid4()
        task_id = uuid.uuid4()
        resp = TaskResponse(
            id=task_id,
            title="Full task",
            description="desc",
            status=TaskStatus.DONE,
            priority=TaskPriority.HIGH,
            due_date=now,
            tags=["backend"],
            is_deleted=False,
            created_by=uid,
            assigned_to=uid,
            created_at=now,
            updated_at=now,
            completed_at=now,
        )
        assert resp.id == task_id
        assert resp.completed_at == now
        assert resp.tags == ["backend"]

    def test_paginated_task_response(self):
        paginated = PaginatedTaskResponse(items=[], total=0, page=1, size=50, pages=0)
        assert paginated.total == 0
        assert paginated.items == []
        assert paginated.page == 1
        assert paginated.size == 50
        assert paginated.pages == 0

    def test_paginated_task_response_with_items(self):
        now = datetime.now(UTC)
        uid = uuid.uuid4()
        task = TaskResponse(
            id=uuid.uuid4(),
            title="Test",
            status=TaskStatus.TODO,
            priority=TaskPriority.LOW,
            is_deleted=False,
            created_by=uid,
            created_at=now,
            updated_at=now,
        )
        paginated = PaginatedTaskResponse(
            items=[task], total=1, page=1, size=50, pages=1
        )
        assert len(paginated.items) == 1
        assert paginated.total == 1


class TestCommentSchemas:
    def test_comment_create_valid(self):
        comment = CommentCreate(content="A comment")
        assert comment.content == "A comment"

    def test_comment_create_empty_rejected(self):
        with pytest.raises(ValidationError):
            CommentCreate(content="")

    def test_comment_create_long_content(self):
        comment = CommentCreate(content="x" * 5000)
        assert len(comment.content) == 5000

    def test_comment_response(self):
        now = datetime.now(UTC)
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

    def test_task_count_by_status_with_values(self):
        counts = TaskCountByStatus(todo=5, in_progress=3, done=10, cancelled=1)
        assert counts.todo == 5
        assert counts.in_progress == 3
        assert counts.done == 10
        assert counts.cancelled == 1

    def test_task_count_by_user(self):
        tcu = TaskCountByUser(user_id="123", user_name="Test", count=5)
        assert tcu.count == 5
        assert tcu.user_id == "123"
        assert tcu.user_name == "Test"

    def test_dashboard_stats_defaults(self):
        stats = DashboardStats(
            tasks_by_status=TaskCountByStatus(),
        )
        assert stats.total_tasks == 0
        assert stats.overdue_tasks == 0
        assert stats.tasks_by_user == []

    def test_dashboard_stats_with_values(self):
        stats = DashboardStats(
            total_tasks=20,
            tasks_by_status=TaskCountByStatus(todo=5, in_progress=10, done=5),
            overdue_tasks=3,
            tasks_by_user=[
                TaskCountByUser(user_id="1", user_name="Alice", count=10),
                TaskCountByUser(user_id="2", user_name="Bob", count=10),
            ],
        )
        assert stats.total_tasks == 20
        assert stats.overdue_tasks == 3
        assert len(stats.tasks_by_user) == 2
