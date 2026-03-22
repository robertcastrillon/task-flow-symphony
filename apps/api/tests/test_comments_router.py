"""Integration tests for comments endpoints."""

import uuid

import pytest

from app.core.security import create_access_token, hash_password
from app.models.comment import Comment
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


async def _create_task(db_session, created_by):
    task = Task(title="Test Task", created_by=created_by)
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


def _auth_header(user):
    token = create_access_token({"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}


class TestListComments:
    @pytest.mark.asyncio
    async def test_list_comments_empty(self, client, db_session):
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id)
        response = await client.get(
            f"/api/v1/tasks/{task.id}/comments", headers=_auth_header(user)
        )
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_list_comments_with_data(self, client, db_session):
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id)
        comment = Comment(task_id=task.id, author_id=user.id, content="Hello")
        db_session.add(comment)
        await db_session.commit()

        response = await client.get(
            f"/api/v1/tasks/{task.id}/comments", headers=_auth_header(user)
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["content"] == "Hello"

    @pytest.mark.asyncio
    async def test_list_comments_task_not_found(self, client, db_session):
        user = await _create_user(db_session)
        response = await client.get(
            f"/api/v1/tasks/{uuid.uuid4()}/comments", headers=_auth_header(user)
        )
        assert response.status_code == 404


class TestCreateComment:
    @pytest.mark.asyncio
    async def test_create_comment_success(self, client, db_session):
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id)
        response = await client.post(
            f"/api/v1/tasks/{task.id}/comments",
            json={"content": "Nice work!"},
            headers=_auth_header(user),
        )
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Nice work!"
        assert data["task_id"] == str(task.id)
        assert data["author_id"] == str(user.id)

    @pytest.mark.asyncio
    async def test_create_comment_on_deleted_task(self, client, db_session):
        user = await _create_user(db_session)
        task = Task(title="Deleted", created_by=user.id, is_deleted=True)
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        response = await client.post(
            f"/api/v1/tasks/{task.id}/comments",
            json={"content": "Should fail"},
            headers=_auth_header(user),
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_comment_empty_content(self, client, db_session):
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id)
        response = await client.post(
            f"/api/v1/tasks/{task.id}/comments",
            json={"content": ""},
            headers=_auth_header(user),
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_comment_unauthenticated(self, client, db_session):
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id)
        response = await client.post(
            f"/api/v1/tasks/{task.id}/comments",
            json={"content": "No auth"},
        )
        assert response.status_code == 401
