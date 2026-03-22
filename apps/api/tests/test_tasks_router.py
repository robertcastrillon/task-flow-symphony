"""Integration tests for tasks endpoints."""

import uuid

import pytest

from app.core.security import create_access_token, hash_password
from app.models.task import Task
from app.models.user import User


async def _create_user(
    db_session,
    email="user@example.com",
    name="Test User",
    password="password123",  # noqa: S107
    role="member",
):
    user = User(
        email=email,
        name=name,
        password_hash=hash_password(password),
        role=role,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


async def _create_task(db_session, created_by, title="Test Task", **kwargs):
    task = Task(title=title, created_by=created_by, **kwargs)
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


def _auth_header(user):
    token = create_access_token({"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}


class TestCreateTask:
    @pytest.mark.asyncio
    async def test_create_task_success(self, client, db_session):
        user = await _create_user(db_session)
        response = await client.post(
            "/api/v1/tasks",
            json={"title": "My Task"},
            headers=_auth_header(user),
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "My Task"
        assert data["status"] == "todo"
        assert data["priority"] == "medium"
        assert data["created_by"] == str(user.id)

    @pytest.mark.asyncio
    async def test_create_task_unauthenticated(self, client):
        response = await client.post("/api/v1/tasks", json={"title": "Fail"})
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_task_validation_error(self, client, db_session):
        user = await _create_user(db_session)
        response = await client.post(
            "/api/v1/tasks",
            json={"title": ""},
            headers=_auth_header(user),
        )
        assert response.status_code == 422


class TestListTasks:
    @pytest.mark.asyncio
    async def test_list_tasks_empty(self, client, db_session):
        user = await _create_user(db_session)
        response = await client.get("/api/v1/tasks", headers=_auth_header(user))
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_tasks_with_data(self, client, db_session):
        user = await _create_user(db_session)
        await _create_task(db_session, user.id, title="Task 1")
        await _create_task(db_session, user.id, title="Task 2")
        response = await client.get("/api/v1/tasks", headers=_auth_header(user))
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    @pytest.mark.asyncio
    async def test_list_tasks_excludes_deleted(self, client, db_session):
        user = await _create_user(db_session)
        await _create_task(db_session, user.id, title="Visible")
        await _create_task(db_session, user.id, title="Deleted", is_deleted=True)
        response = await client.get("/api/v1/tasks", headers=_auth_header(user))
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Visible"

    @pytest.mark.asyncio
    async def test_list_tasks_filter_by_status(self, client, db_session):
        user = await _create_user(db_session)
        await _create_task(db_session, user.id, title="Todo", status="todo")
        await _create_task(
            db_session, user.id, title="Done", status="done"
        )
        response = await client.get(
            "/api/v1/tasks?status=todo", headers=_auth_header(user)
        )
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Todo"

    @pytest.mark.asyncio
    async def test_list_tasks_pagination(self, client, db_session):
        user = await _create_user(db_session)
        for i in range(5):
            await _create_task(db_session, user.id, title=f"Task {i}")
        response = await client.get(
            "/api/v1/tasks?page=1&size=2", headers=_auth_header(user)
        )
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["pages"] == 3


class TestGetTask:
    @pytest.mark.asyncio
    async def test_get_task_success(self, client, db_session):
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id)
        response = await client.get(
            f"/api/v1/tasks/{task.id}", headers=_auth_header(user)
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Test Task"

    @pytest.mark.asyncio
    async def test_get_task_not_found(self, client, db_session):
        user = await _create_user(db_session)
        response = await client.get(
            f"/api/v1/tasks/{uuid.uuid4()}", headers=_auth_header(user)
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_deleted_task_returns_404(self, client, db_session):
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id, is_deleted=True)
        response = await client.get(
            f"/api/v1/tasks/{task.id}", headers=_auth_header(user)
        )
        assert response.status_code == 404


class TestUpdateTask:
    @pytest.mark.asyncio
    async def test_update_task_by_owner(self, client, db_session):
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id)
        response = await client.patch(
            f"/api/v1/tasks/{task.id}",
            json={"title": "Updated"},
            headers=_auth_header(user),
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated"

    @pytest.mark.asyncio
    async def test_update_task_forbidden_for_non_owner(self, client, db_session):
        owner = await _create_user(db_session, email="owner@example.com")
        other = await _create_user(db_session, email="other@example.com")
        task = await _create_task(db_session, owner.id)
        response = await client.patch(
            f"/api/v1/tasks/{task.id}",
            json={"title": "Hacked"},
            headers=_auth_header(other),
        )
        assert response.status_code == 403


class TestDeleteTask:
    @pytest.mark.asyncio
    async def test_soft_delete_task(self, client, db_session):
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id)
        response = await client.delete(
            f"/api/v1/tasks/{task.id}", headers=_auth_header(user)
        )
        assert response.status_code == 204

        # Verify it's no longer accessible
        get_response = await client.get(
            f"/api/v1/tasks/{task.id}", headers=_auth_header(user)
        )
        assert get_response.status_code == 404


class TestChangeStatus:
    @pytest.mark.asyncio
    async def test_change_status_to_done(self, client, db_session):
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id)
        response = await client.patch(
            f"/api/v1/tasks/{task.id}/status",
            json={"status": "done"},
            headers=_auth_header(user),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "done"
        assert data["completed_at"] is not None

    @pytest.mark.asyncio
    async def test_change_status_from_done_clears_completed_at(self, client, db_session):
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id)
        # First set to done
        await client.patch(
            f"/api/v1/tasks/{task.id}/status",
            json={"status": "done"},
            headers=_auth_header(user),
        )
        # Then back to in_progress
        response = await client.patch(
            f"/api/v1/tasks/{task.id}/status",
            json={"status": "in_progress"},
            headers=_auth_header(user),
        )
        assert response.status_code == 200
        assert response.json()["completed_at"] is None


class TestAssignTask:
    @pytest.mark.asyncio
    async def test_assign_task_to_user(self, client, db_session):
        user = await _create_user(db_session, email="creator@example.com")
        assignee = await _create_user(db_session, email="assignee@example.com")
        task = await _create_task(db_session, user.id)
        response = await client.patch(
            f"/api/v1/tasks/{task.id}/assign",
            json={"assigned_to": str(assignee.id)},
            headers=_auth_header(user),
        )
        assert response.status_code == 200
        assert response.json()["assigned_to"] == str(assignee.id)

    @pytest.mark.asyncio
    async def test_assign_to_nonexistent_user(self, client, db_session):
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id)
        response = await client.patch(
            f"/api/v1/tasks/{task.id}/assign",
            json={"assigned_to": str(uuid.uuid4())},
            headers=_auth_header(user),
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_unassign_task(self, client, db_session):
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id, assigned_to=user.id)
        response = await client.patch(
            f"/api/v1/tasks/{task.id}/assign",
            json={"assigned_to": None},
            headers=_auth_header(user),
        )
        assert response.status_code == 200
        assert response.json()["assigned_to"] is None
