"""Integration tests for auth endpoints (register, login, refresh, me)."""

import pytest

from app.core.security import create_access_token, create_refresh_token, hash_password
from app.models.user import User


async def _create_user(
    db_session,
    email="user@example.com",
    password="password123",  # noqa: S107
    is_active=True,
):
    """Helper to insert a user directly into the DB."""
    user = User(
        email=email,
        name="Test User",
        password_hash=hash_password(password),
        is_active=is_active,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# --- Registration ---


class TestRegister:
    @pytest.mark.asyncio
    async def test_register_success(self, client):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "new@example.com",
                "name": "New User",
                "password": "secure123",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new@example.com"
        assert data["name"] == "New User"
        assert data["role"] == "member"
        assert data["is_active"] is True
        assert "password" not in data
        assert "password_hash" not in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client, db_session):
        await _create_user(db_session, email="dup@example.com")
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "dup@example.com", "name": "Dup", "password": "secure123"},
        )
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client):
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "not-an-email", "name": "Test", "password": "secure123"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_short_password(self, client):
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com", "name": "Test", "password": "short"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_empty_name(self, client):
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com", "name": "", "password": "secure123"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_missing_fields(self, client):
        response = await client.post("/api/v1/auth/register", json={})
        assert response.status_code == 422


# --- Login ---


class TestLogin:
    @pytest.mark.asyncio
    async def test_login_success(self, client, db_session):
        await _create_user(
            db_session, email="login@example.com", password="password123"
        )
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "login@example.com", "password": "password123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client, db_session):
        await _create_user(db_session, email="wrong@example.com", password="correct123")
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "wrong@example.com", "password": "incorrect"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client):
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "password123"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_inactive_user(self, client, db_session):
        await _create_user(
            db_session,
            email="inactive@example.com",
            password="password123",
            is_active=False,
        )
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "inactive@example.com", "password": "password123"},
        )
        assert response.status_code == 401
        assert "disabled" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_invalid_email_format(self, client):
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "not-email", "password": "password123"},
        )
        assert response.status_code == 422


# --- Refresh ---


class TestRefresh:
    @pytest.mark.asyncio
    async def test_refresh_success(self, client, db_session):
        user = await _create_user(db_session, email="refresh@example.com")
        refresh = create_refresh_token({"sub": str(user.id)})
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, client):
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-token"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_with_access_token_rejected(self, client, db_session):
        user = await _create_user(db_session, email="access@example.com")
        access = create_access_token({"sub": str(user.id)})
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": access},
        )
        assert response.status_code == 401
        assert "token type" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_refresh_inactive_user(self, client, db_session):
        user = await _create_user(db_session, email="gone@example.com", is_active=False)
        refresh = create_refresh_token({"sub": str(user.id)})
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh},
        )
        assert response.status_code == 401


# --- Me ---


class TestMe:
    @pytest.mark.asyncio
    async def test_me_authenticated(self, client, db_session):
        user = await _create_user(db_session, email="me@example.com")
        token = create_access_token({"sub": str(user.id)})
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "me@example.com"
        assert "password" not in data
        assert "password_hash" not in data

    @pytest.mark.asyncio
    async def test_me_no_token(self, client):
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_me_invalid_token(self, client):
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer bad-token"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_me_with_refresh_token_rejected(self, client, db_session):
        user = await _create_user(db_session, email="ref@example.com")
        refresh = create_refresh_token({"sub": str(user.id)})
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {refresh}"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_me_inactive_user(self, client, db_session):
        user = await _create_user(
            db_session, email="inactive_me@example.com", is_active=False
        )
        token = create_access_token({"sub": str(user.id)})
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401


# --- Security headers on auth responses ---


class TestSecurityHeaders:
    @pytest.mark.asyncio
    async def test_security_headers_present(self, client):
        response = await client.get("/api/v1/health")
        assert response.headers.get("x-content-type-options") == "nosniff"
        assert response.headers.get("x-frame-options") == "DENY"

    @pytest.mark.asyncio
    async def test_request_id_header_present(self, client):
        response = await client.get("/api/v1/health")
        assert "x-request-id" in response.headers
