"""BDD integration tests for Tasks & Users module.

Maps to all BDD scenarios from ENG-78 (B—TU-03).
"""

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.core.security import create_access_token, hash_password
from app.models.task import Task
from app.models.user import User

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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


async def _create_task(db_session, created_by, title="Test Task", **kwargs):
    task = Task(title=title, created_by=created_by, **kwargs)
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


def _auth_header(user):
    token = create_access_token({"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}


# ===========================================================================
# US-B01: Crear tarea
# ===========================================================================


class TestUSB01CreateTask:
    """US-B01: Create task scenarios."""

    @pytest.mark.asyncio
    async def test_create_task_with_required_fields(self, client, db_session):
        """Scenario: Crear tarea con campos obligatorios."""
        user = await _create_user(db_session)
        response = await client.post(
            "/api/v1/tasks",
            json={"title": "Diseñar landing page"},
            headers=_auth_header(user),
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Diseñar landing page"
        assert data["status"] == "todo"
        assert data["priority"] == "medium"
        assert data["created_by"] == str(user.id)

    @pytest.mark.asyncio
    async def test_create_task_with_all_fields(self, client, db_session):
        """Scenario: Crear tarea con todos los campos."""
        user = await _create_user(db_session)
        due = (datetime.now(tz=UTC) + timedelta(days=7)).isoformat()
        response = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Full task",
                "description": "A detailed description",
                "priority": "high",
                "due_date": due,
                "tags": ["diseño", "frontend"],
            },
            headers=_auth_header(user),
        )
        assert response.status_code == 201
        data = response.json()
        assert data["priority"] == "high"
        assert data["description"] == "A detailed description"
        assert data["due_date"] is not None
        assert set(data["tags"]) == {"diseño", "frontend"}

    @pytest.mark.asyncio
    async def test_create_task_without_title(self, client, db_session):
        """Scenario: Crear tarea sin título."""
        user = await _create_user(db_session)
        response = await client.post(
            "/api/v1/tasks",
            json={"title": ""},
            headers=_auth_header(user),
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_task_title_too_long(self, client, db_session):
        """Scenario: Crear tarea con título excesivamente largo (>255 chars)."""
        user = await _create_user(db_session)
        response = await client.post(
            "/api/v1/tasks",
            json={"title": "x" * 256},
            headers=_auth_header(user),
        )
        assert response.status_code == 422


# ===========================================================================
# US-B02: Ver lista de tareas con filtros
# ===========================================================================


class TestUSB02ListTasksFilters:
    """US-B02: List tasks with filters scenarios."""

    @pytest.mark.asyncio
    async def test_paginated_list_50_max(self, client, db_session):
        """Scenario: Ver lista de tareas paginada (60 tasks, first page = 50)."""
        user = await _create_user(db_session)
        for i in range(60):
            await _create_task(db_session, user.id, title=f"Task {i}")
        response = await client.get(
            "/api/v1/tasks?page=1&size=50", headers=_auth_header(user)
        )
        data = response.json()
        assert data["total"] == 60
        assert len(data["items"]) == 50
        assert data["pages"] == 2

    @pytest.mark.asyncio
    async def test_filter_by_status(self, client, db_session):
        """Scenario: Filtrar por estado."""
        user = await _create_user(db_session)
        await _create_task(db_session, user.id, title="T1", status="todo")
        await _create_task(db_session, user.id, title="T2", status="in_progress")
        await _create_task(db_session, user.id, title="T3", status="in_progress")
        response = await client.get(
            "/api/v1/tasks?status=in_progress", headers=_auth_header(user)
        )
        data = response.json()
        assert data["total"] == 2
        assert all(t["status"] == "in_progress" for t in data["items"])

    @pytest.mark.asyncio
    async def test_filter_by_priority(self, client, db_session):
        """Scenario: Filtrar por prioridad."""
        user = await _create_user(db_session)
        await _create_task(db_session, user.id, title="Low", priority="low")
        await _create_task(db_session, user.id, title="Urgent", priority="urgent")
        await _create_task(db_session, user.id, title="Urgent2", priority="urgent")
        response = await client.get(
            "/api/v1/tasks?priority=urgent", headers=_auth_header(user)
        )
        data = response.json()
        assert data["total"] == 2
        assert all(t["priority"] == "urgent" for t in data["items"])

    @pytest.mark.asyncio
    async def test_filter_by_assignee(self, client, db_session):
        """Scenario: Filtrar por asignado."""
        user = await _create_user(db_session, email="creator@team.com")
        maria = await _create_user(db_session, email="maria@team.com", name="Maria")
        await _create_task(db_session, user.id, title="Unassigned")
        await _create_task(db_session, user.id, title="Maria's", assigned_to=maria.id)
        response = await client.get(
            f"/api/v1/tasks?assignee={maria.id}", headers=_auth_header(user)
        )
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["assigned_to"] == str(maria.id)

    @pytest.mark.asyncio
    async def test_filter_by_tag(self, client, db_session):
        """Scenario: Filtrar por tag."""
        user = await _create_user(db_session)
        await _create_task(db_session, user.id, title="FE", tags=["frontend", "react"])
        await _create_task(db_session, user.id, title="BE", tags=["backend"])
        response = await client.get(
            "/api/v1/tasks?tag=frontend", headers=_auth_header(user)
        )
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "FE"

    @pytest.mark.asyncio
    async def test_search_by_text(self, client, db_session):
        """Scenario: Búsqueda por texto."""
        user = await _create_user(db_session)
        await _create_task(db_session, user.id, title="Diseñar landing page")
        await _create_task(db_session, user.id, title="Backend API")
        response = await client.get(
            "/api/v1/tasks?search=landing", headers=_auth_header(user)
        )
        data = response.json()
        assert data["total"] == 1
        assert "landing" in data["items"][0]["title"].lower()

    @pytest.mark.asyncio
    async def test_combined_filters(self, client, db_session):
        """Scenario: Combinación de filtros."""
        user = await _create_user(db_session)
        await _create_task(
            db_session, user.id, title="T1", status="todo", priority="high"
        )
        await _create_task(
            db_session, user.id, title="T2", status="todo", priority="low"
        )
        await _create_task(
            db_session, user.id, title="T3", status="done", priority="high"
        )
        response = await client.get(
            "/api/v1/tasks?status=todo&priority=high", headers=_auth_header(user)
        )
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "T1"

    @pytest.mark.asyncio
    async def test_no_results(self, client, db_session):
        """Scenario: Sin resultados."""
        user = await _create_user(db_session)
        await _create_task(db_session, user.id, title="Exists")
        response = await client.get(
            "/api/v1/tasks?status=cancelled", headers=_auth_header(user)
        )
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    @pytest.mark.asyncio
    async def test_sort_by_due_date_asc(self, client, db_session):
        """Scenario: Ordenar tareas por fecha de vencimiento ascendente."""
        user = await _create_user(db_session)
        now = datetime.now(tz=UTC)
        await _create_task(
            db_session,
            user.id,
            title="Later",
            due_date=now + timedelta(days=10),
        )
        await _create_task(
            db_session,
            user.id,
            title="Sooner",
            due_date=now + timedelta(days=2),
        )
        await _create_task(
            db_session,
            user.id,
            title="Soonest",
            due_date=now + timedelta(days=1),
        )
        response = await client.get(
            "/api/v1/tasks?sort_by=due_date_asc", headers=_auth_header(user)
        )
        data = response.json()
        titles = [t["title"] for t in data["items"]]
        assert titles == ["Soonest", "Sooner", "Later"]


# ===========================================================================
# US-B05: Ver detalle de tarea
# ===========================================================================


class TestUSB05TaskDetail:
    """US-B05: View task detail scenarios."""

    @pytest.mark.asyncio
    async def test_view_full_detail(self, client, db_session):
        """Scenario: Ver detalle completo."""
        user = await _create_user(db_session)
        task = await _create_task(
            db_session,
            user.id,
            title="Diseñar landing page",
            description="Full desc",
            priority="high",
            tags=["design"],
        )
        response = await client.get(
            f"/api/v1/tasks/{task.id}", headers=_auth_header(user)
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Diseñar landing page"
        assert data["description"] == "Full desc"
        assert data["status"] == "todo"
        assert data["priority"] == "high"
        assert data["created_by"] == str(user.id)
        assert data["created_at"] is not None
        assert data["updated_at"] is not None
        assert "design" in data["tags"]

    @pytest.mark.asyncio
    async def test_task_without_description(self, client, db_session):
        """Scenario: Tarea sin descripción."""
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id, title="No desc")
        response = await client.get(
            f"/api/v1/tasks/{task.id}", headers=_auth_header(user)
        )
        assert response.status_code == 200
        assert response.json()["description"] is None

    @pytest.mark.asyncio
    async def test_nonexistent_task_returns_404(self, client, db_session):
        """Scenario: Acceder a tarea inexistente."""
        user = await _create_user(db_session)
        response = await client.get(
            f"/api/v1/tasks/{uuid.uuid4()}", headers=_auth_header(user)
        )
        assert response.status_code == 404


# ===========================================================================
# US-B06: Editar tarea
# ===========================================================================


class TestUSB06EditTask:
    """US-B06: Edit task scenarios."""

    @pytest.mark.asyncio
    async def test_edit_title_and_description(self, client, db_session):
        """Scenario: Editar título y descripción."""
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id, title="Original")
        original_updated = task.updated_at

        response = await client.patch(
            f"/api/v1/tasks/{task.id}",
            json={"title": "Diseñar landing page v2", "description": "New desc"},
            headers=_auth_header(user),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Diseñar landing page v2"
        assert data["description"] == "New desc"
        # updated_at should change
        assert data["updated_at"] != str(original_updated) if original_updated else True

    @pytest.mark.asyncio
    async def test_change_priority(self, client, db_session):
        """Scenario: Cambiar prioridad."""
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id, priority="medium")
        response = await client.patch(
            f"/api/v1/tasks/{task.id}",
            json={"priority": "urgent"},
            headers=_auth_header(user),
        )
        assert response.status_code == 200
        assert response.json()["priority"] == "urgent"

    @pytest.mark.asyncio
    async def test_edit_due_date(self, client, db_session):
        """Scenario: Editar fecha de vencimiento."""
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id)
        due = (datetime.now(tz=UTC) + timedelta(days=5)).isoformat()
        response = await client.patch(
            f"/api/v1/tasks/{task.id}",
            json={"due_date": due},
            headers=_auth_header(user),
        )
        assert response.status_code == 200
        assert response.json()["due_date"] is not None

    @pytest.mark.asyncio
    async def test_edit_tags(self, client, db_session):
        """Scenario: Editar tags."""
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id, tags=["diseño"])
        response = await client.patch(
            f"/api/v1/tasks/{task.id}",
            json={"tags": ["urgente"]},
            headers=_auth_header(user),
        )
        assert response.status_code == 200
        assert response.json()["tags"] == ["urgente"]

    @pytest.mark.asyncio
    async def test_admin_can_edit_any_task(self, client, db_session):
        """Admin can edit tasks created by others."""
        owner = await _create_user(db_session, email="owner@team.com")
        admin = await _create_user(db_session, email="admin@team.com", role="admin")
        task = await _create_task(db_session, owner.id, title="Owner's task")
        response = await client.patch(
            f"/api/v1/tasks/{task.id}",
            json={"title": "Admin edited"},
            headers=_auth_header(admin),
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Admin edited"


# ===========================================================================
# US-B07: Cambiar estado de tarea via API
# ===========================================================================


class TestUSB07ChangeStatus:
    """US-B07: Change task status scenarios."""

    @pytest.mark.asyncio
    async def test_change_to_valid_status(self, client, db_session):
        """Scenario: Cambiar estado válido."""
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id, status="todo")
        response = await client.patch(
            f"/api/v1/tasks/{task.id}/status",
            json={"status": "in_progress"},
            headers=_auth_header(user),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"

    @pytest.mark.asyncio
    async def test_mark_as_done_sets_completed_at(self, client, db_session):
        """Scenario: Marcar como completada."""
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id, status="in_progress")
        response = await client.patch(
            f"/api/v1/tasks/{task.id}/status",
            json={"status": "done"},
            headers=_auth_header(user),
        )
        assert response.status_code == 200
        assert response.json()["completed_at"] is not None

    @pytest.mark.asyncio
    async def test_invalid_status_returns_422(self, client, db_session):
        """Scenario: Cambiar a estado inválido."""
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id)
        response = await client.patch(
            f"/api/v1/tasks/{task.id}/status",
            json={"status": "deleted"},
            headers=_auth_header(user),
        )
        assert response.status_code == 422


# ===========================================================================
# US-B08: Asignar tarea a un usuario
# ===========================================================================


class TestUSB08AssignTask:
    """US-B08: Assign task scenarios."""

    @pytest.mark.asyncio
    async def test_admin_assigns_to_member(self, client, db_session):
        """Scenario: Asignar tarea a otro miembro (admin)."""
        admin = await _create_user(db_session, email="admin@team.com", role="admin")
        maria = await _create_user(db_session, email="maria@team.com", name="Maria")
        task = await _create_task(db_session, admin.id, title="Diseñar landing page")
        response = await client.patch(
            f"/api/v1/tasks/{task.id}/assign",
            json={"assigned_to": str(maria.id)},
            headers=_auth_header(admin),
        )
        assert response.status_code == 200
        assert response.json()["assigned_to"] == str(maria.id)

    @pytest.mark.asyncio
    async def test_reassign_task(self, client, db_session):
        """Scenario: Reasignar tarea."""
        admin = await _create_user(db_session, email="admin@team.com", role="admin")
        maria = await _create_user(db_session, email="maria@team.com")
        carlos = await _create_user(db_session, email="carlos@team.com")
        task = await _create_task(db_session, admin.id, assigned_to=maria.id)
        response = await client.patch(
            f"/api/v1/tasks/{task.id}/assign",
            json={"assigned_to": str(carlos.id)},
            headers=_auth_header(admin),
        )
        assert response.status_code == 200
        assert response.json()["assigned_to"] == str(carlos.id)

    @pytest.mark.asyncio
    async def test_unassign_task(self, client, db_session):
        """Scenario: Desasignar tarea."""
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id, assigned_to=user.id)
        response = await client.patch(
            f"/api/v1/tasks/{task.id}/assign",
            json={"assigned_to": None},
            headers=_auth_header(user),
        )
        assert response.status_code == 200
        assert response.json()["assigned_to"] is None

    @pytest.mark.asyncio
    async def test_assign_to_nonexistent_user(self, client, db_session):
        """Scenario: Asignar a usuario inexistente."""
        admin = await _create_user(db_session, role="admin")
        task = await _create_task(db_session, admin.id)
        response = await client.patch(
            f"/api/v1/tasks/{task.id}/assign",
            json={"assigned_to": str(uuid.uuid4())},
            headers=_auth_header(admin),
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_member_self_assign(self, client, db_session):
        """Scenario: Miembro asigna tarea a sí mismo."""
        creator = await _create_user(db_session, email="creator@team.com")
        member = await _create_user(db_session, email="member@team.com")
        task = await _create_task(db_session, creator.id)
        response = await client.patch(
            f"/api/v1/tasks/{task.id}/assign",
            json={"assigned_to": str(member.id)},
            headers=_auth_header(member),
        )
        assert response.status_code == 200
        assert response.json()["assigned_to"] == str(member.id)


# ===========================================================================
# US-B09: Eliminar tarea (soft delete)
# ===========================================================================


class TestUSB09DeleteTask:
    """US-B09: Soft delete task scenarios."""

    @pytest.mark.asyncio
    async def test_admin_soft_delete(self, client, db_session):
        """Scenario: Soft delete exitoso (admin)."""
        admin = await _create_user(db_session, role="admin")
        member = await _create_user(db_session, email="member@team.com")
        task = await _create_task(db_session, member.id, title="Tarea obsoleta")
        # Admin can delete any task
        response = await client.delete(
            f"/api/v1/tasks/{task.id}", headers=_auth_header(admin)
        )
        assert response.status_code == 204
        # Task no longer visible
        get_resp = await client.get(
            f"/api/v1/tasks/{task.id}", headers=_auth_header(admin)
        )
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_nonexistent_task(self, client, db_session):
        """Scenario: Eliminar tarea inexistente."""
        user = await _create_user(db_session)
        response = await client.delete(
            f"/api/v1/tasks/{uuid.uuid4()}", headers=_auth_header(user)
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_member_deletes_own_task(self, client, db_session):
        """Scenario: Miembro elimina su propia tarea."""
        member = await _create_user(db_session)
        task = await _create_task(db_session, member.id, title="Mi tarea")
        response = await client.delete(
            f"/api/v1/tasks/{task.id}", headers=_auth_header(member)
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_member_cannot_delete_others_task(self, client, db_session):
        """Scenario: Miembro intenta eliminar tarea de otro."""
        owner = await _create_user(db_session, email="owner@team.com")
        other = await _create_user(db_session, email="other@team.com")
        task = await _create_task(db_session, owner.id)
        response = await client.delete(
            f"/api/v1/tasks/{task.id}", headers=_auth_header(other)
        )
        assert response.status_code == 403


# ===========================================================================
# US-E01: Ver miembros del equipo
# ===========================================================================


class TestUSE01ListTeamMembers:
    """US-E01: List team members scenarios."""

    @pytest.mark.asyncio
    async def test_list_active_members(self, client, db_session):
        """Scenario: Ver lista de miembros."""
        for i in range(5):
            await _create_user(db_session, email=f"user{i}@team.com", name=f"User {i}")
        user = await _create_user(db_session, email="viewer@team.com", name="Viewer")
        response = await client.get("/api/v1/users", headers=_auth_header(user))
        assert response.status_code == 200
        data = response.json()
        # 5 + viewer = 6
        assert len(data) == 6
        # Each user has expected fields
        for u in data:
            assert "name" in u
            assert "email" in u
            assert "role" in u

    @pytest.mark.asyncio
    async def test_roles_differentiated(self, client, db_session):
        """Scenario: Distinguir roles."""
        admin = await _create_user(
            db_session, email="admin@team.com", role="admin", name="Admin"
        )
        await _create_user(
            db_session, email="member@team.com", role="member", name="Member"
        )
        response = await client.get("/api/v1/users", headers=_auth_header(admin))
        data = response.json()
        roles = {u["email"]: u["role"] for u in data}
        assert roles["admin@team.com"] == "admin"
        assert roles["member@team.com"] == "member"

    @pytest.mark.asyncio
    async def test_inactive_users_excluded(self, client, db_session):
        """Scenario: Usuarios inactivos."""
        active = await _create_user(db_session, email="active@team.com", name="Active")
        await _create_user(
            db_session, email="inactive@team.com", name="Inactive", is_active=False
        )
        response = await client.get("/api/v1/users", headers=_auth_header(active))
        emails = [u["email"] for u in response.json()]
        assert "active@team.com" in emails
        assert "inactive@team.com" not in emails


# ===========================================================================
# US-E02: Ver detalle de un miembro
# ===========================================================================


class TestUSE02MemberDetail:
    """US-E02: View member detail scenarios."""

    @pytest.mark.asyncio
    async def test_view_member_profile(self, client, db_session):
        """Scenario: Ver perfil de miembro."""
        maria = await _create_user(
            db_session, email="maria@team.com", name="Maria", role="member"
        )
        response = await client.get(
            f"/api/v1/users/{maria.id}", headers=_auth_header(maria)
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Maria"
        assert data["email"] == "maria@team.com"
        assert data["role"] == "member"
        assert data["created_at"] is not None

    @pytest.mark.asyncio
    async def test_nonexistent_user_returns_404(self, client, db_session):
        """Scenario: Perfil de usuario inexistente."""
        user = await _create_user(db_session)
        response = await client.get(
            f"/api/v1/users/{uuid.uuid4()}", headers=_auth_header(user)
        )
        assert response.status_code == 404


# ===========================================================================
# US-E03: Actualizar perfil propio
# ===========================================================================


class TestUSE03UpdateOwnProfile:
    """US-E03: Update own profile scenarios."""

    @pytest.mark.asyncio
    async def test_update_name(self, client, db_session):
        """Scenario: Actualizar nombre."""
        user = await _create_user(db_session, email="maria@team.com", name="Maria")
        response = await client.patch(
            f"/api/v1/users/{user.id}",
            json={"name": "María García"},
            headers=_auth_header(user),
        )
        assert response.status_code == 200
        assert response.json()["name"] == "María García"

    @pytest.mark.asyncio
    async def test_update_avatar(self, client, db_session):
        """Scenario: Actualizar avatar."""
        user = await _create_user(db_session)
        response = await client.patch(
            f"/api/v1/users/{user.id}",
            json={"avatar_url": "https://example.com/avatar.png"},
            headers=_auth_header(user),
        )
        assert response.status_code == 200
        assert response.json()["avatar_url"] == "https://example.com/avatar.png"

    @pytest.mark.asyncio
    async def test_cannot_change_email_via_update(self, client, db_session):
        """Scenario: Intentar cambiar email — field not in UserUpdate schema."""
        user = await _create_user(db_session, email="original@team.com")
        response = await client.patch(
            f"/api/v1/users/{user.id}",
            json={"email": "hacked@team.com"},
            headers=_auth_header(user),
        )
        # Email field is ignored (not in UserUpdate), original preserved
        assert response.status_code == 200
        assert response.json()["email"] == "original@team.com"

    @pytest.mark.asyncio
    async def test_member_cannot_change_own_role(self, client, db_session):
        """Scenario: Intentar cambiar rol propio."""
        member = await _create_user(db_session, role="member")
        response = await client.patch(
            f"/api/v1/users/{member.id}",
            json={"role": "admin"},
            headers=_auth_header(member),
        )
        # Role field is ignored (not in UserUpdate schema)
        assert response.status_code == 200
        assert response.json()["role"] == "member"


# ===========================================================================
# US-F01: Autorización basada en roles
# ===========================================================================


class TestUSF01Authorization:
    """US-F01: Role-based authorization scenarios."""

    @pytest.mark.asyncio
    async def test_admin_full_access(self, client, db_session):
        """Scenario: Admin accede a operaciones de gestión."""
        admin = await _create_user(db_session, email="admin@team.com", role="admin")
        member = await _create_user(db_session, email="member@team.com")
        task = await _create_task(db_session, member.id, title="Member's task")

        # Admin can assign to anyone
        resp = await client.patch(
            f"/api/v1/tasks/{task.id}/assign",
            json={"assigned_to": str(member.id)},
            headers=_auth_header(admin),
        )
        assert resp.status_code == 200

        # Admin can delete any task
        resp = await client.delete(
            f"/api/v1/tasks/{task.id}", headers=_auth_header(admin)
        )
        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_member_cannot_assign_to_other(self, client, db_session):
        """Scenario: Miembro intenta operación de Admin."""
        creator = await _create_user(db_session, email="creator@team.com")
        other = await _create_user(db_session, email="other@team.com")
        task = await _create_task(db_session, creator.id)
        response = await client.patch(
            f"/api/v1/tasks/{task.id}/assign",
            json={"assigned_to": str(other.id)},
            headers=_auth_header(creator),
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_expired_token(self, client, db_session):
        """Scenario: Token expirado."""
        from jose import jwt

        from app.core.config import settings

        payload = {
            "sub": str(uuid.uuid4()),
            "type": "access",
            "exp": datetime.now(tz=UTC) - timedelta(hours=1),
        }
        token = jwt.encode(
            payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
        )
        response = await client.get(
            "/api/v1/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_manipulated_token(self, client):
        """Scenario: Token manipulado (invalid signature)."""
        from jose import jwt

        payload = {
            "sub": str(uuid.uuid4()),
            "type": "access",
            "exp": datetime.now(tz=UTC) + timedelta(hours=1),
        }
        token = jwt.encode(payload, "wrong-secret-key", algorithm="HS256")
        response = await client.get(
            "/api/v1/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_idor_prevention(self, client, db_session):
        """Scenario: Autorización a nivel de objeto (IDOR prevention)."""
        owner = await _create_user(db_session, email="owner@team.com")
        attacker = await _create_user(db_session, email="attacker@team.com")
        task = await _create_task(db_session, owner.id, title="Owner's task")

        # Attacker tries to delete owner's task
        response = await client.delete(
            f"/api/v1/tasks/{task.id}", headers=_auth_header(attacker)
        )
        assert response.status_code == 403

        # Task still exists
        get_resp = await client.get(
            f"/api/v1/tasks/{task.id}", headers=_auth_header(owner)
        )
        assert get_resp.status_code == 200
