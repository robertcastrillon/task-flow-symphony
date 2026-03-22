import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.core.security import hash_password
from app.models.comment import Comment
from app.models.task import Task
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.schemas.comment import CommentCreate
from app.schemas.task import TaskAssign, TaskCreate, TaskStatusUpdate, TaskUpdate
from app.schemas.user import UserUpdate
from app.services.auth_service import AuthService
from app.services.comment_service import CommentService
from app.services.task_service import TaskService
from app.services.user_service import UserService

# --- Helpers ---


def _make_user(role="member", is_active=True, user_id=None):
    return SimpleNamespace(
        id=user_id or uuid.uuid4(),
        email="test@example.com",
        name="Test User",
        password_hash=hash_password("password123"),
        role=role,
        is_active=is_active,
        created_at=datetime.now(tz=UTC),
        updated_at=datetime.now(tz=UTC),
        avatar_url=None,
        telegram_chat_id=None,
    )


def _make_task(created_by=None, task_id=None, status="todo"):
    return SimpleNamespace(
        id=task_id or uuid.uuid4(),
        title="Test Task",
        description=None,
        status=status,
        priority="medium",
        due_date=None,
        created_by=created_by or uuid.uuid4(),
        assigned_to=None,
        tags=[],
        is_deleted=False,
        created_at=datetime.now(tz=UTC),
        updated_at=datetime.now(tz=UTC),
        completed_at=None,
    )


def _make_comment(task_id=None, author_id=None):
    return SimpleNamespace(
        id=uuid.uuid4(),
        task_id=task_id or uuid.uuid4(),
        author_id=author_id or uuid.uuid4(),
        content="Test comment",
        created_at=datetime.now(tz=UTC),
        updated_at=datetime.now(tz=UTC),
    )


def _mock_db(scalar_result=None, scalars_result=None):
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = scalar_result
    result.scalar.return_value = scalar_result
    if scalars_result is not None:
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = scalars_result
        result.scalars.return_value = scalars_mock
    db.execute.return_value = result
    return db


# --- AuthService ---


class TestAuthServiceRegister:
    @pytest.mark.asyncio
    async def test_register_duplicate_email_raises_409(self):
        existing = _make_user()
        db = _mock_db(scalar_result=existing)
        payload = RegisterRequest(
            email="test@example.com", name="New User", password="secure123"
        )
        with pytest.raises(HTTPException) as exc_info:
            await AuthService.register_user(db, payload)
        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_register_new_user_succeeds(self):
        db = _mock_db(scalar_result=None)
        db.add = MagicMock()

        payload = RegisterRequest(
            email="new@example.com", name="New User", password="secure123"
        )
        result = await AuthService.register_user(db, payload)
        assert isinstance(result, User)
        db.add.assert_called_once()
        db.flush.assert_awaited_once()


class TestAuthServiceAuthenticate:
    @pytest.mark.asyncio
    async def test_login_wrong_email_raises_401(self):
        db = _mock_db(scalar_result=None)
        payload = LoginRequest(email="wrong@example.com", password="password123")
        with pytest.raises(HTTPException) as exc_info:
            await AuthService.authenticate(db, payload)
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_login_wrong_password_raises_401(self):
        user = _make_user()
        db = _mock_db(scalar_result=user)
        payload = LoginRequest(email="test@example.com", password="wrong_pass")
        with pytest.raises(HTTPException) as exc_info:
            await AuthService.authenticate(db, payload)
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_login_inactive_user_raises_401(self):
        user = _make_user(is_active=False)
        db = _mock_db(scalar_result=user)
        payload = LoginRequest(email="test@example.com", password="password123")
        with pytest.raises(HTTPException) as exc_info:
            await AuthService.authenticate(db, payload)
        assert exc_info.value.status_code == 401
        assert "disabled" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_login_success(self):
        user = _make_user()
        db = _mock_db(scalar_result=user)
        payload = LoginRequest(email="test@example.com", password="password123")
        result = await AuthService.authenticate(db, payload)
        assert result.access_token
        assert result.refresh_token


class TestAuthServiceRefreshToken:
    @pytest.mark.asyncio
    async def test_refresh_invalid_token_raises_401(self):
        db = AsyncMock()
        with pytest.raises(HTTPException) as exc_info:
            await AuthService.refresh_token(db, "invalid-token")
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_with_access_token_raises_401(self):
        from app.core.security import create_access_token

        db = AsyncMock()
        token = create_access_token({"sub": str(uuid.uuid4())})
        with pytest.raises(HTTPException) as exc_info:
            await AuthService.refresh_token(db, token)
        assert exc_info.value.status_code == 401
        assert "Invalid token type" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_refresh_without_sub_raises_401(self):
        from app.core.security import create_refresh_token

        db = AsyncMock()
        token = create_refresh_token({})  # no sub
        with pytest.raises(HTTPException) as exc_info:
            await AuthService.refresh_token(db, token)
        assert exc_info.value.status_code == 401
        assert "Invalid token payload" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_refresh_user_not_found_raises_401(self):
        from app.core.security import create_refresh_token

        db = _mock_db(scalar_result=None)
        token = create_refresh_token({"sub": str(uuid.uuid4())})
        with pytest.raises(HTTPException) as exc_info:
            await AuthService.refresh_token(db, token)
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_inactive_user_raises_401(self):
        from app.core.security import create_refresh_token

        user = _make_user(is_active=False)
        db = _mock_db(scalar_result=user)
        token = create_refresh_token({"sub": str(user.id)})
        with pytest.raises(HTTPException) as exc_info:
            await AuthService.refresh_token(db, token)
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_success(self):
        from app.core.security import create_refresh_token

        user = _make_user()
        db = _mock_db(scalar_result=user)
        token = create_refresh_token({"sub": str(user.id)})
        result = await AuthService.refresh_token(db, token)
        assert result.access_token
        assert result.refresh_token


# --- UserService ---


class TestUserServiceList:
    @pytest.mark.asyncio
    async def test_list_users(self):
        users = [_make_user(), _make_user()]
        db = _mock_db(scalars_result=users)
        result = await UserService.list_users(db)
        assert len(result) == 2


class TestUserServiceGet:
    @pytest.mark.asyncio
    async def test_get_user_not_found_raises_404(self):
        db = _mock_db(scalar_result=None)
        with pytest.raises(HTTPException) as exc_info:
            await UserService.get_user(db, uuid.uuid4())
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_user_found(self):
        user = _make_user()
        db = _mock_db(scalar_result=user)
        result = await UserService.get_user(db, user.id)
        assert result is user


class TestUserServiceUpdate:
    @pytest.mark.asyncio
    async def test_update_own_profile(self):
        user = _make_user()
        db = _mock_db(scalar_result=user)
        payload = UserUpdate(name="Updated Name")
        result = await UserService.update_user(db, user.id, payload, user)
        assert result.name == "Updated Name"

    @pytest.mark.asyncio
    async def test_update_other_profile_as_member_raises_403(self):
        user = _make_user(role="member")
        other_id = uuid.uuid4()
        db = AsyncMock()
        payload = UserUpdate(name="Hack")
        with pytest.raises(HTTPException) as exc_info:
            await UserService.update_user(db, other_id, payload, user)
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_update_other_profile_as_admin(self):
        admin = _make_user(role="admin")
        other = _make_user()
        db = _mock_db(scalar_result=other)
        payload = UserUpdate(name="Admin Updated")
        result = await UserService.update_user(db, other.id, payload, admin)
        assert result.name == "Admin Updated"


# --- TaskService ---


class TestTaskServiceGet:
    @pytest.mark.asyncio
    async def test_get_task_not_found_raises_404(self):
        db = _mock_db(scalar_result=None)
        with pytest.raises(HTTPException) as exc_info:
            await TaskService.get_task(db, uuid.uuid4())
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_task_found(self):
        task = _make_task()
        db = _mock_db(scalar_result=task)
        result = await TaskService.get_task(db, task.id)
        assert result is task


class TestTaskServiceCreate:
    @pytest.mark.asyncio
    async def test_create_task(self):
        user = _make_user()
        db = AsyncMock()
        db.add = MagicMock()
        payload = TaskCreate(title="New Task")
        result = await TaskService.create_task(db, payload, user)
        assert isinstance(result, Task)
        assert result.created_by == user.id
        db.add.assert_called_once()


class TestTaskServiceUpdate:
    @pytest.mark.asyncio
    async def test_update_task_as_owner(self):
        user = _make_user()
        task = _make_task(created_by=user.id)
        db = _mock_db(scalar_result=task)
        payload = TaskUpdate(title="Updated Title")
        result = await TaskService.update_task(db, task.id, payload, user)
        assert result.title == "Updated Title"

    @pytest.mark.asyncio
    async def test_update_task_not_owner_raises_403(self):
        user = _make_user(role="member")
        task = _make_task(created_by=uuid.uuid4())
        db = _mock_db(scalar_result=task)
        payload = TaskUpdate(title="Hack")
        with pytest.raises(HTTPException) as exc_info:
            await TaskService.update_task(db, task.id, payload, user)
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_update_task_as_admin(self):
        admin = _make_user(role="admin")
        task = _make_task(created_by=uuid.uuid4())
        db = _mock_db(scalar_result=task)
        payload = TaskUpdate(title="Admin Updated")
        result = await TaskService.update_task(db, task.id, payload, admin)
        assert result.title == "Admin Updated"


class TestTaskServiceDelete:
    @pytest.mark.asyncio
    async def test_delete_task_sets_soft_delete(self):
        user = _make_user()
        task = _make_task(created_by=user.id)
        db = _mock_db(scalar_result=task)
        await TaskService.delete_task(db, task.id, user)
        assert task.is_deleted is True

    @pytest.mark.asyncio
    async def test_delete_task_not_owner_raises_403(self):
        user = _make_user(role="member")
        task = _make_task(created_by=uuid.uuid4())
        db = _mock_db(scalar_result=task)
        with pytest.raises(HTTPException) as exc_info:
            await TaskService.delete_task(db, task.id, user)
        assert exc_info.value.status_code == 403


class TestTaskServiceChangeStatus:
    @pytest.mark.asyncio
    async def test_change_status_to_done_sets_completed_at(self):
        user = _make_user()
        task = _make_task(created_by=user.id)
        db = _mock_db(scalar_result=task)
        payload = TaskStatusUpdate(status="done")
        result = await TaskService.change_status(db, task.id, payload, user)
        assert result.status == "done"
        assert result.completed_at is not None

    @pytest.mark.asyncio
    async def test_change_status_from_done_clears_completed_at(self):
        user = _make_user()
        task = _make_task(created_by=user.id, status="done")
        task.completed_at = datetime.now(tz=UTC)
        db = _mock_db(scalar_result=task)
        payload = TaskStatusUpdate(status="todo")
        result = await TaskService.change_status(db, task.id, payload, user)
        assert result.status == "todo"
        assert result.completed_at is None


class TestTaskServiceAssign:
    @pytest.mark.asyncio
    async def test_assign_to_existing_user(self):
        user = _make_user()
        assignee = _make_user()
        task = _make_task(created_by=user.id)

        db = AsyncMock()
        task_result = MagicMock()
        task_result.scalar_one_or_none.return_value = task
        assignee_result = MagicMock()
        assignee_result.scalar_one_or_none.return_value = assignee
        db.execute.side_effect = [task_result, assignee_result]

        payload = TaskAssign(assigned_to=assignee.id)
        result = await TaskService.assign_task(db, task.id, payload, user)
        assert result.assigned_to == assignee.id

    @pytest.mark.asyncio
    async def test_assign_to_nonexistent_user_raises_404(self):
        user = _make_user()
        task = _make_task(created_by=user.id)

        db = AsyncMock()
        task_result = MagicMock()
        task_result.scalar_one_or_none.return_value = task
        assignee_result = MagicMock()
        assignee_result.scalar_one_or_none.return_value = None
        db.execute.side_effect = [task_result, assignee_result]

        payload = TaskAssign(assigned_to=uuid.uuid4())
        with pytest.raises(HTTPException) as exc_info:
            await TaskService.assign_task(db, task.id, payload, user)
        assert exc_info.value.status_code == 404
        assert "Assignee not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_unassign_task(self):
        user = _make_user()
        task = _make_task(created_by=user.id)
        task.assigned_to = uuid.uuid4()
        db = _mock_db(scalar_result=task)
        payload = TaskAssign(assigned_to=None)
        result = await TaskService.assign_task(db, task.id, payload, user)
        assert result.assigned_to is None


class TestTaskServiceListTasks:
    @pytest.mark.asyncio
    async def test_list_tasks_empty(self):
        db = AsyncMock()
        count_result = MagicMock()
        count_result.scalar.return_value = 0
        items_result = MagicMock()
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = []
        items_result.scalars.return_value = scalars_mock
        db.execute.side_effect = [count_result, items_result]

        result = await TaskService.list_tasks(db)
        assert result.total == 0
        assert result.items == []
        assert result.pages == 0


# --- CommentService ---


class TestCommentServiceList:
    @pytest.mark.asyncio
    async def test_list_comments_task_not_found_raises_404(self):
        db = _mock_db(scalar_result=None)
        with pytest.raises(HTTPException) as exc_info:
            await CommentService.list_comments(db, uuid.uuid4())
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_list_comments_success(self):
        task = _make_task()
        comments = [_make_comment(), _make_comment()]

        db = AsyncMock()
        task_result = MagicMock()
        task_result.scalar_one_or_none.return_value = task
        comment_result = MagicMock()
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = comments
        comment_result.scalars.return_value = scalars_mock
        db.execute.side_effect = [task_result, comment_result]

        result = await CommentService.list_comments(db, task.id)
        assert len(result) == 2


class TestCommentServiceCreate:
    @pytest.mark.asyncio
    async def test_create_comment_task_not_found_raises_404(self):
        db = _mock_db(scalar_result=None)
        user = _make_user()
        payload = CommentCreate(content="Hello")
        with pytest.raises(HTTPException) as exc_info:
            await CommentService.create_comment(db, uuid.uuid4(), payload, user)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_create_comment_success(self):
        task = _make_task()
        user = _make_user()

        db = AsyncMock()
        task_result = MagicMock()
        task_result.scalar_one_or_none.return_value = task
        db.execute.return_value = task_result
        db.add = MagicMock()

        payload = CommentCreate(content="Nice work!")
        result = await CommentService.create_comment(db, task.id, payload, user)
        assert isinstance(result, Comment)
        db.add.assert_called_once()


# ---------------------------------------------------------------------------
# DashboardService
# ---------------------------------------------------------------------------
from app.services.dashboard_service import DashboardService


class TestDashboardService:
    @pytest.mark.asyncio
    async def test_get_stats_empty(self):
        db = AsyncMock()

        # total tasks
        total_mock = MagicMock()
        total_mock.scalar.return_value = 0

        # status counts
        status_mock = MagicMock()
        status_mock.all.return_value = []

        # priority counts
        priority_mock = MagicMock()
        priority_mock.all.return_value = []

        # overdue
        overdue_mock = MagicMock()
        overdue_mock.scalar.return_value = 0

        # users
        user_mock = MagicMock()
        user_mock.all.return_value = []

        db.execute.side_effect = [
            total_mock,
            status_mock,
            priority_mock,
            overdue_mock,
            user_mock,
        ]

        result = await DashboardService.get_stats(db)
        assert result.total_tasks == 0
        assert result.overdue_tasks == 0
        assert result.tasks_by_status.todo == 0
        assert result.tasks_by_user == []

    @pytest.mark.asyncio
    async def test_get_stats_with_data(self):
        db = AsyncMock()
        uid = uuid.uuid4()

        total_mock = MagicMock()
        total_mock.scalar.return_value = 5

        status_mock = MagicMock()
        status_mock.all.return_value = [("todo", 2), ("in_progress", 3)]

        priority_mock = MagicMock()
        priority_mock.all.return_value = [("high", 3), ("low", 2)]

        overdue_mock = MagicMock()
        overdue_mock.scalar.return_value = 1

        user_mock = MagicMock()
        user_mock.all.return_value = [(uid, "Alice", 3)]

        db.execute.side_effect = [
            total_mock,
            status_mock,
            priority_mock,
            overdue_mock,
            user_mock,
        ]

        result = await DashboardService.get_stats(db)
        assert result.total_tasks == 5
        assert result.overdue_tasks == 1
        assert result.tasks_by_status.todo == 2
        assert result.tasks_by_status.in_progress == 3
        assert result.tasks_by_priority == {"high": 3, "low": 2}
        assert len(result.tasks_by_user) == 1
        assert result.tasks_by_user[0].user_name == "Alice"
