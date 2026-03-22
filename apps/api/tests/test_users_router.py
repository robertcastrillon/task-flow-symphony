"""Integration tests for users endpoints."""

import pytest

from app.core.security import create_access_token, hash_password
from app.models.user import User


async def _create_user(
    db_session,
    email="user@example.com",
    name="Test User",
    password="password123",  # noqa: S107
    role="member",
    is_active=True,
):
    user = User(
        email=email,
        name=name,
        password_hash=hash_password(password),
        role=role,
        is_active=is_active,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


def _auth_header(user):
    token = create_access_token({"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}


class TestListUsers:
    @pytest.mark.asyncio
    async def test_list_users_authenticated(self, client, db_session):
        user = await _create_user(db_session)
        response = await client.get("/api/v1/users", headers=_auth_header(user))
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["email"] == "user@example.com"

    @pytest.mark.asyncio
    async def test_list_users_excludes_inactive(self, client, db_session):
        active = await _create_user(db_session, email="active@example.com")
        await _create_user(db_session, email="inactive@example.com", is_active=False)
        response = await client.get("/api/v1/users", headers=_auth_header(active))
        assert response.status_code == 200
        emails = [u["email"] for u in response.json()]
        assert "active@example.com" in emails
        assert "inactive@example.com" not in emails

    @pytest.mark.asyncio
    async def test_list_users_unauthenticated(self, client):
        response = await client.get("/api/v1/users")
        assert response.status_code == 401


class TestGetUser:
    @pytest.mark.asyncio
    async def test_get_user_success(self, client, db_session):
        user = await _create_user(db_session)
        response = await client.get(
            f"/api/v1/users/{user.id}", headers=_auth_header(user)
        )
        assert response.status_code == 200
        assert response.json()["email"] == "user@example.com"

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, client, db_session):
        user = await _create_user(db_session)
        import uuid

        fake_id = uuid.uuid4()
        response = await client.get(
            f"/api/v1/users/{fake_id}", headers=_auth_header(user)
        )
        assert response.status_code == 404


class TestUpdateUser:
    @pytest.mark.asyncio
    async def test_update_own_profile(self, client, db_session):
        user = await _create_user(db_session)
        response = await client.patch(
            f"/api/v1/users/{user.id}",
            json={"name": "Updated Name"},
            headers=_auth_header(user),
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    @pytest.mark.asyncio
    async def test_update_other_profile_forbidden(self, client, db_session):
        user1 = await _create_user(db_session, email="user1@example.com")
        user2 = await _create_user(db_session, email="user2@example.com")
        response = await client.patch(
            f"/api/v1/users/{user2.id}",
            json={"name": "Hacked"},
            headers=_auth_header(user1),
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_admin_can_update_other_profile(self, client, db_session):
        admin = await _create_user(db_session, email="admin@example.com", role="admin")
        member = await _create_user(db_session, email="member@example.com")
        response = await client.patch(
            f"/api/v1/users/{member.id}",
            json={"name": "Admin Updated"},
            headers=_auth_header(admin),
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Admin Updated"
