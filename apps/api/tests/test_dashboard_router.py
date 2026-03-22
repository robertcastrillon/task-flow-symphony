"""Integration tests for dashboard endpoints."""

import pytest

from app.core.security import create_access_token, hash_password
from app.models.task import Task
from app.models.user import User


async def _create_user(db_session, email="user@example.com"):
    user = User(
        email=email,
        name="Test User",
        password_hash=hash_password("password123"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


def _auth_header(user):
    token = create_access_token({"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}


class TestDashboardStats:
    @pytest.mark.asyncio
    async def test_stats_empty(self, client, db_session):
        user = await _create_user(db_session)
        response = await client.get(
            "/api/v1/dashboard/stats", headers=_auth_header(user)
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_tasks"] == 0
        assert data["overdue_tasks"] == 0
        assert data["tasks_by_status"]["todo"] == 0

    @pytest.mark.asyncio
    async def test_stats_with_tasks(self, client, db_session):
        user = await _create_user(db_session)
        for status in ["todo", "todo", "in_progress", "done"]:
            task = Task(title=f"Task {status}", created_by=user.id, status=status)
            db_session.add(task)
        await db_session.commit()

        response = await client.get(
            "/api/v1/dashboard/stats", headers=_auth_header(user)
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_tasks"] == 4
        assert data["tasks_by_status"]["todo"] == 2
        assert data["tasks_by_status"]["in_progress"] == 1
        assert data["tasks_by_status"]["done"] == 1

    @pytest.mark.asyncio
    async def test_stats_excludes_deleted(self, client, db_session):
        user = await _create_user(db_session)
        db_session.add(Task(title="Active", created_by=user.id))
        db_session.add(Task(title="Deleted", created_by=user.id, is_deleted=True))
        await db_session.commit()

        response = await client.get(
            "/api/v1/dashboard/stats", headers=_auth_header(user)
        )
        assert response.json()["total_tasks"] == 1

    @pytest.mark.asyncio
    async def test_stats_unauthenticated(self, client):
        response = await client.get("/api/v1/dashboard/stats")
        assert response.status_code == 401
