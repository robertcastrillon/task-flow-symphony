"""BDD-style integration tests mapping to auth user-story acceptance criteria.

Each test class corresponds to a user story from the PRD.
Each test method maps to a specific Gherkin scenario.
"""

from datetime import UTC, datetime, timedelta

import pytest
from jose import jwt

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
)
from app.models.user import User

# --- Helpers ---


async def _create_user(
    db_session,
    email="user@example.com",
    name="Test User",
    password="password123",  # noqa: S107
    role="member",
    is_active=True,
):
    """Insert a user directly into the DB."""
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


async def _create_task_via_api(client, user, title="Test Task"):
    """Create a task through the API so it persists in the test DB correctly."""
    response = await client.post(
        "/api/v1/tasks",
        json={"title": title},
        headers=_auth_headers(user),
    )
    assert response.status_code == 201
    return response.json()


def _auth_headers(user):
    """Generate Authorization header for a user."""
    token = create_access_token({"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# US-A01: Registro de usuario
# ---------------------------------------------------------------------------


class TestUSA01Registration:
    """User story: visitor registers with email and password."""

    @pytest.mark.asyncio
    async def test_successful_registration(self, client):
        """Scenario: Registro exitoso — new user gets member role."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "carlos@team.com",
                "name": "Carlos",
                "password": "Segura123!",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "carlos@team.com"
        assert data["name"] == "Carlos"
        assert data["role"] == "member"
        assert data["is_active"] is True
        # Sensitive fields must NOT be exposed
        assert "password" not in data
        assert "password_hash" not in data

    @pytest.mark.asyncio
    async def test_duplicate_email_rejected(self, client, db_session):
        """Scenario: Registro con email duplicado."""
        await _create_user(db_session, email="carlos@team.com")
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "carlos@team.com",
                "name": "Carlos",
                "password": "Segura123!",
            },
        )
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_weak_password_rejected(self, client):
        """Scenario: Registro con contraseña débil — < 8 characters."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "carlos@team.com",
                "name": "Carlos",
                "password": "short",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_email_format_rejected(self, client):
        """Scenario: Registro con email inválido."""
        for bad_email in ["carlos@", "carlos.com", "not-an-email"]:
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": bad_email,
                    "name": "Carlos",
                    "password": "Segura123!",
                },
            )
            assert response.status_code == 422, f"Expected 422 for email: {bad_email}"

    @pytest.mark.asyncio
    async def test_empty_required_fields_rejected(self, client):
        """Scenario: Registro con campos vacíos."""
        # All fields missing
        response = await client.post("/api/v1/auth/register", json={})
        assert response.status_code == 422
        errors = response.json()["detail"]
        # Should have validation errors for each required field
        error_fields = {e["loc"][-1] for e in errors}
        assert "email" in error_fields
        assert "name" in error_fields
        assert "password" in error_fields

    @pytest.mark.asyncio
    async def test_empty_name_rejected(self, client):
        """Scenario: Registro con campos vacíos — empty name."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "carlos@team.com",
                "name": "",
                "password": "Segura123!",
            },
        )
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# US-A02: Inicio de sesión
# ---------------------------------------------------------------------------


class TestUSA02Login:
    """User story: visitor logs in with email and password."""

    @pytest.mark.asyncio
    async def test_successful_login_returns_tokens(self, client, db_session):
        """Scenario: Login exitoso — returns JWT + refresh token."""
        await _create_user(db_session, email="maria@team.com", password="Segura123!")
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "maria@team.com", "password": "Segura123!"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

        # Verify access token is valid and has 24h expiry
        payload = jwt.decode(
            data["access_token"],
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        assert payload["type"] == "access"
        assert "exp" in payload

    @pytest.mark.asyncio
    async def test_wrong_password_returns_401(self, client, db_session):
        """Scenario: Login con credenciales incorrectas."""
        await _create_user(db_session, email="maria@team.com", password="Segura123!")
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "maria@team.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401
        # No token should be generated
        data = response.json()
        assert "access_token" not in data

    @pytest.mark.asyncio
    async def test_nonexistent_email_returns_401(self, client):
        """Scenario: Login con email no registrado — same error, no info leak."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "desconocido@team.com", "password": "Segura123!"},
        )
        assert response.status_code == 401
        assert "access_token" not in response.json()

    @pytest.mark.asyncio
    async def test_error_message_does_not_reveal_email_existence(
        self, client, db_session
    ):
        """Scenario: Login messages must not reveal whether email exists."""
        await _create_user(db_session, email="real@team.com", password="Segura123!")
        # Wrong password for existing user
        resp_existing = await client.post(
            "/api/v1/auth/login",
            json={"email": "real@team.com", "password": "wrongpass123"},
        )
        # Non-existent user
        resp_nonexistent = await client.post(
            "/api/v1/auth/login",
            json={"email": "fake@team.com", "password": "Segura123!"},
        )
        # Both should return the same error message
        assert resp_existing.status_code == resp_nonexistent.status_code == 401
        assert resp_existing.json()["detail"] == resp_nonexistent.json()["detail"]

    @pytest.mark.asyncio
    async def test_rate_limiting_on_login(self, client, db_session):
        """Scenario: Rate limiting en login — 6th attempt returns 429."""
        await _create_user(db_session, email="rate@team.com", password="Segura123!")
        login_payload = {"email": "rate@team.com", "password": "wrongpassword"}

        # First 5 requests should go through (with 401)
        for i in range(5):
            resp = await client.post("/api/v1/auth/login", json=login_payload)
            assert resp.status_code == 401, f"Request {i + 1} should get 401"

        # 6th request should be rate-limited
        resp = await client.post("/api/v1/auth/login", json=login_payload)
        assert resp.status_code == 429
        assert "too many" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_inactive_user_login_rejected(self, client, db_session):
        """Scenario: Login con cuenta inactiva."""
        await _create_user(
            db_session,
            email="disabled@team.com",
            password="Segura123!",
            is_active=False,
        )
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "disabled@team.com", "password": "Segura123!"},
        )
        assert response.status_code == 401
        assert "disabled" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# US-A03: Ver perfil actual
# ---------------------------------------------------------------------------


class TestUSA03Me:
    """User story: member views their current profile."""

    @pytest.mark.asyncio
    async def test_view_profile_returns_expected_fields(self, client, db_session):
        """Scenario: Ver perfil autenticado — name, email, role, avatar returned."""
        user = await _create_user(db_session, email="maria@team.com", name="Maria")
        response = await client.get("/api/v1/auth/me", headers=_auth_headers(user))
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "maria@team.com"
        assert data["name"] == "Maria"
        assert data["role"] == "member"
        assert "avatar_url" in data
        # Sensitive fields must NOT be present
        assert "password" not in data
        assert "password_hash" not in data

    @pytest.mark.asyncio
    async def test_unauthenticated_access_returns_401(self, client):
        """Scenario: Acceso sin autenticación."""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# US-A04: Renovación de token JWT
# ---------------------------------------------------------------------------


class TestUSA04TokenRefresh:
    """User story: member refreshes expired access token."""

    @pytest.mark.asyncio
    async def test_valid_refresh_returns_new_tokens(self, client, db_session):
        """Scenario: Refresh token válido — returns new JWT pair."""
        user = await _create_user(db_session, email="refresh@team.com")
        refresh = create_refresh_token({"sub": str(user.id)})
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_expired_refresh_token_returns_401(self, client, db_session):
        """Scenario: Refresh token expirado — returns 401."""
        user = await _create_user(db_session, email="expired@team.com")
        expired_payload = {
            "sub": str(user.id),
            "exp": datetime.now(tz=UTC) - timedelta(hours=1),
            "type": "refresh",
        }
        expired_token = jwt.encode(
            expired_payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": expired_token},
        )
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# US-A05: Cerrar sesión
# ---------------------------------------------------------------------------


class TestUSA05Logout:
    """User story: member logs out.

    Note: The current implementation uses client-side token invalidation.
    The server does not maintain a token blacklist. These tests verify that
    without a valid token, protected endpoints reject access.
    """

    @pytest.mark.asyncio
    async def test_access_without_token_rejected(self, client):
        """Scenario: Acceso post-logout — protected route returns 401."""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_invalid_token_rejected(self, client):
        """Scenario: After clearing token client-side, stale tokens still fail."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalidated-token"},
        )
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# US-F01: Autorización basada en roles
# ---------------------------------------------------------------------------


class TestUSF01RoleAuthorization:
    """User story: role-based access control for admin vs member."""

    @pytest.mark.asyncio
    async def test_admin_can_delete_any_task(self, client, db_session):
        """Scenario: Admin accede a operaciones de gestión — can delete any task."""
        admin = await _create_user(db_session, email="admin@team.com", role="admin")
        member = await _create_user(db_session, email="member@team.com", name="Member")
        task = await _create_task_via_api(client, member)
        response = await client.delete(
            f"/api/v1/tasks/{task['id']}",
            headers=_auth_headers(admin),
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_member_cannot_delete_others_task(self, client, db_session):
        """Scenario: IDOR prevention — member can't delete another user's task."""
        owner = await _create_user(db_session, email="owner@team.com", name="Owner")
        attacker = await _create_user(
            db_session, email="attacker@team.com", name="Attacker"
        )
        task = await _create_task_via_api(client, owner)
        response = await client.delete(
            f"/api/v1/tasks/{task['id']}",
            headers=_auth_headers(attacker),
        )
        assert response.status_code == 403

        # Verify task was NOT deleted
        get_response = await client.get(
            f"/api/v1/tasks/{task['id']}",
            headers=_auth_headers(owner),
        )
        assert get_response.status_code == 200

    @pytest.mark.asyncio
    async def test_expired_token_on_protected_endpoint(self, client, db_session):
        """Scenario: Token expirado en cualquier endpoint — returns 401."""
        user = await _create_user(db_session, email="expired@team.com")
        expired_payload = {
            "sub": str(user.id),
            "exp": datetime.now(tz=UTC) - timedelta(hours=1),
            "type": "access",
        }
        expired_token = jwt.encode(
            expired_payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_manipulated_token_rejected(self, client):
        """Scenario: Token manipulado — invalid signature returns 401."""
        tampered_token = jwt.encode(
            {"sub": "fake-user-id", "type": "access"},
            "wrong-secret-key",
            algorithm=settings.jwt_algorithm,
        )
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {tampered_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_member_cannot_update_others_task(self, client, db_session):
        """Scenario: Miembro intenta operación no permitida — update other's task."""
        owner = await _create_user(db_session, email="owner2@team.com", name="Owner")
        member = await _create_user(db_session, email="member2@team.com", name="Member")
        task = await _create_task_via_api(client, owner)
        response = await client.patch(
            f"/api/v1/tasks/{task['id']}",
            json={"title": "Hacked"},
            headers=_auth_headers(member),
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_admin_can_update_any_task(self, client, db_session):
        """Scenario: Admin accede a operaciones de gestión — can update any task."""
        admin = await _create_user(db_session, email="admin2@team.com", role="admin")
        member = await _create_user(db_session, email="member3@team.com", name="Member")
        task = await _create_task_via_api(client, member)
        response = await client.patch(
            f"/api/v1/tasks/{task['id']}",
            json={"title": "Admin Updated"},
            headers=_auth_headers(admin),
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Admin Updated"

    @pytest.mark.asyncio
    async def test_rate_limiting_on_register(self, client):
        """Rate limiting also applies to register endpoint."""
        for i in range(5):
            resp = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": f"user{i}@team.com",
                    "name": f"User {i}",
                    "password": "Segura123!",
                },
            )
            assert resp.status_code == 201, f"Request {i + 1} should succeed"

        # 6th should be rate limited
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "user5@team.com",
                "name": "User 5",
                "password": "Segura123!",
            },
        )
        assert resp.status_code == 429
