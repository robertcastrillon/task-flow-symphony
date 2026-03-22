"""BDD integration tests for Comments & Dashboard module.

Maps to all BDD scenarios from ENG-82 (B—CD-03).
"""

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.core.security import create_access_token, hash_password
from app.models.comment import Comment
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
    avatar_url=None,
):
    user = User(
        email=email,
        name=name,
        password_hash=hash_password(password),
        role=role,
        avatar_url=avatar_url,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


async def _create_task(
    db_session,
    created_by,
    title="Diseñar landing page",
    status="todo",
    due_date=None,
    assigned_to=None,
    is_deleted=False,
):
    task = Task(
        title=title,
        created_by=created_by,
        status=status,
        due_date=due_date,
        assigned_to=assigned_to,
        is_deleted=is_deleted,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


async def _create_comment(db_session, task_id, author_id, content="A comment"):
    comment = Comment(task_id=task_id, author_id=author_id, content=content)
    db_session.add(comment)
    await db_session.commit()
    await db_session.refresh(comment)
    return comment


def _auth_header(user):
    token = create_access_token({"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}


# ===========================================================================
# US-C01: Ver comentarios de una tarea
# ===========================================================================


class TestUSC01ViewComments:
    """US-C01: As a member, I want to see comments on a task
    to understand the team's discussions and decisions."""

    @pytest.mark.asyncio
    async def test_list_comments_ordered_chronologically(self, client, db_session):
        """Scenario: Ver lista de comentarios
        Given the task 'Diseñar landing page' has 3 comments
        When I open the task detail
        Then I see the 3 comments ordered chronologically
        And each comment shows author_id, content, created_at.
        """
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id)

        # Create 3 comments in order
        await _create_comment(db_session, task.id, user.id, "First comment")
        await _create_comment(db_session, task.id, user.id, "Second comment")
        await _create_comment(db_session, task.id, user.id, "Third comment")

        response = await client.get(
            f"/api/v1/tasks/{task.id}/comments", headers=_auth_header(user)
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

        # Chronological order
        assert data[0]["content"] == "First comment"
        assert data[1]["content"] == "Second comment"
        assert data[2]["content"] == "Third comment"

        # Each comment has author, content, date
        for item in data:
            assert "author_id" in item
            assert "content" in item
            assert "created_at" in item
            assert item["author_id"] == str(user.id)

    @pytest.mark.asyncio
    async def test_task_without_comments_returns_empty_list(self, client, db_session):
        """Scenario: Tarea sin comentarios
        Given the task has no comments
        When I open the detail
        Then I see an empty list (frontend handles 'No hay comentarios aún' message).
        """
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id)

        response = await client.get(
            f"/api/v1/tasks/{task.id}/comments", headers=_auth_header(user)
        )
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_member_can_view_comments(self, client, db_session):
        """Persona: Member can view comments."""
        member = await _create_user(db_session, role="member")
        task = await _create_task(db_session, member.id)
        await _create_comment(db_session, task.id, member.id, "Member comment")

        response = await client.get(
            f"/api/v1/tasks/{task.id}/comments", headers=_auth_header(member)
        )
        assert response.status_code == 200
        assert len(response.json()) == 1

    @pytest.mark.asyncio
    async def test_admin_can_view_comments(self, client, db_session):
        """Persona: Admin can view comments."""
        admin = await _create_user(db_session, role="admin")
        task = await _create_task(db_session, admin.id)
        await _create_comment(db_session, task.id, admin.id, "Admin comment")

        response = await client.get(
            f"/api/v1/tasks/{task.id}/comments", headers=_auth_header(admin)
        )
        assert response.status_code == 200
        assert len(response.json()) == 1

    @pytest.mark.asyncio
    async def test_unauthenticated_cannot_view_comments(self, client, db_session):
        """Unauthenticated user cannot view comments."""
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id)

        response = await client.get(f"/api/v1/tasks/{task.id}/comments")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_view_comments_nonexistent_task_404(self, client, db_session):
        """Viewing comments on a nonexistent task returns 404."""
        user = await _create_user(db_session)
        fake_task_id = uuid.uuid4()

        response = await client.get(
            f"/api/v1/tasks/{fake_task_id}/comments", headers=_auth_header(user)
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_comments_from_multiple_authors(self, client, db_session):
        """Comments from different authors display correct author_id."""
        user_a = await _create_user(db_session, email="a@example.com", name="Alice")
        user_b = await _create_user(db_session, email="b@example.com", name="Bob")
        task = await _create_task(db_session, user_a.id)

        await _create_comment(db_session, task.id, user_a.id, "Alice's comment")
        await _create_comment(db_session, task.id, user_b.id, "Bob's comment")

        response = await client.get(
            f"/api/v1/tasks/{task.id}/comments", headers=_auth_header(user_a)
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        authors = {item["author_id"] for item in data}
        assert str(user_a.id) in authors
        assert str(user_b.id) in authors


# ===========================================================================
# US-C02: Agregar comentario a una tarea
# ===========================================================================


class TestUSC02AddComment:
    """US-C02: As a member, I want to add a comment to a task
    to communicate updates or ask questions to the team."""

    @pytest.mark.asyncio
    async def test_add_comment_success(self, client, db_session):
        """Scenario: Agregar comentario exitoso
        Given I'm viewing the detail of 'Diseñar landing page'
        When I write '¿Usamos los colores de la marca?' and submit
        Then the comment appears with my name, avatar, and current date
        And the form is cleared (client-side concern).
        """
        user = await _create_user(
            db_session, name="María García", avatar_url="https://example.com/avatar.png"
        )
        task = await _create_task(db_session, user.id, title="Diseñar landing page")

        response = await client.post(
            f"/api/v1/tasks/{task.id}/comments",
            json={"content": "¿Usamos los colores de la marca?"},
            headers=_auth_header(user),
        )
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "¿Usamos los colores de la marca?"
        assert data["author_id"] == str(user.id)
        assert data["task_id"] == str(task.id)
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_empty_comment_rejected(self, client, db_session):
        """Scenario: Comentario vacío
        Given I'm on the comment form
        When I try to submit an empty comment
        Then I see a validation error
        And the comment is not sent.
        """
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id)

        response = await client.post(
            f"/api/v1/tasks/{task.id}/comments",
            json={"content": ""},
            headers=_auth_header(user),
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_comment_on_nonexistent_task_returns_404(self, client, db_session):
        """Scenario: Comentar en tarea inexistente
        Given I try to comment on a task with a non-existent ID
        When I submit the comment
        Then I receive a 404 error 'Tarea no encontrada'.
        """
        user = await _create_user(db_session)
        fake_task_id = uuid.uuid4()

        response = await client.post(
            f"/api/v1/tasks/{fake_task_id}/comments",
            json={"content": "This should fail"},
            headers=_auth_header(user),
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_member_can_add_comment(self, client, db_session):
        """Persona: Member can add comments."""
        member = await _create_user(db_session, role="member")
        task = await _create_task(db_session, member.id)

        response = await client.post(
            f"/api/v1/tasks/{task.id}/comments",
            json={"content": "Member comment"},
            headers=_auth_header(member),
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_admin_can_add_comment(self, client, db_session):
        """Persona: Admin can add comments."""
        admin = await _create_user(db_session, role="admin")
        task = await _create_task(db_session, admin.id)

        response = await client.post(
            f"/api/v1/tasks/{task.id}/comments",
            json={"content": "Admin comment"},
            headers=_auth_header(admin),
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_unauthenticated_cannot_add_comment(self, client, db_session):
        """Unauthenticated user cannot add comments."""
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id)

        response = await client.post(
            f"/api/v1/tasks/{task.id}/comments",
            json={"content": "No auth"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_comment_on_deleted_task_returns_404(self, client, db_session):
        """Commenting on a soft-deleted task returns 404."""
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id, is_deleted=True)

        response = await client.post(
            f"/api/v1/tasks/{task.id}/comments",
            json={"content": "Should fail"},
            headers=_auth_header(user),
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_whitespace_only_comment_accepted(self, client, db_session):
        """Whitespace-only content passes min_length=1 validation (len > 0).

        Note: The schema uses min_length=1 which counts whitespace characters.
        Future improvement could add a strip-then-validate pattern.
        """
        user = await _create_user(db_session)
        task = await _create_task(db_session, user.id)

        response = await client.post(
            f"/api/v1/tasks/{task.id}/comments",
            json={"content": "   "},
            headers=_auth_header(user),
        )
        assert response.status_code == 201


# ===========================================================================
# US-D01: Ver estadísticas del dashboard
# ===========================================================================


class TestUSD01DashboardStats:
    """US-D01: As a member, I want to see a visual summary of tasks
    to understand the general state of the team's work."""

    @pytest.mark.asyncio
    async def test_dashboard_shows_correct_metrics(self, client, db_session):
        """Scenario: Dashboard muestra métricas correctas
        Given there are 10 tasks: 3 todo, 5 in_progress, 2 done
        When I access the dashboard
        Then I see StatCards with: Total (10), Todo (3), In Progress (5), Done (2).
        """
        user = await _create_user(db_session)

        statuses = ["todo"] * 3 + ["in_progress"] * 5 + ["done"] * 2
        for i, status in enumerate(statuses):
            await _create_task(db_session, user.id, title=f"Task {i}", status=status)

        response = await client.get(
            "/api/v1/dashboard/stats", headers=_auth_header(user)
        )
        assert response.status_code == 200
        data = response.json()

        assert data["total_tasks"] == 10
        assert data["tasks_by_status"]["todo"] == 3
        assert data["tasks_by_status"]["in_progress"] == 5
        assert data["tasks_by_status"]["done"] == 2

    @pytest.mark.asyncio
    async def test_dashboard_shows_overdue_tasks(self, client, db_session):
        """Scenario: Dashboard muestra tareas vencidas
        Given there are 2 tasks with due_date in the past and status != 'done'
        When I access the dashboard
        Then I see an indicator of '2 overdue tasks'.
        """
        user = await _create_user(db_session)
        past_date = datetime.now(tz=UTC) - timedelta(days=7)
        future_date = datetime.now(tz=UTC) + timedelta(days=7)

        # 2 overdue tasks (past due, not done)
        await _create_task(
            db_session,
            user.id,
            title="Overdue 1",
            status="todo",
            due_date=past_date,
        )
        await _create_task(
            db_session,
            user.id,
            title="Overdue 2",
            status="in_progress",
            due_date=past_date,
        )
        # Task past due but done — NOT overdue
        await _create_task(
            db_session,
            user.id,
            title="Done past",
            status="done",
            due_date=past_date,
        )
        # Task past due but cancelled — NOT overdue
        await _create_task(
            db_session,
            user.id,
            title="Cancelled past",
            status="cancelled",
            due_date=past_date,
        )
        # Task due in future — NOT overdue
        await _create_task(
            db_session,
            user.id,
            title="Future",
            status="todo",
            due_date=future_date,
        )
        # Task with no due date — NOT overdue
        await _create_task(
            db_session,
            user.id,
            title="No due date",
            status="todo",
        )

        response = await client.get(
            "/api/v1/dashboard/stats", headers=_auth_header(user)
        )
        assert response.status_code == 200
        data = response.json()
        assert data["overdue_tasks"] == 2

    @pytest.mark.asyncio
    async def test_dashboard_shows_tasks_by_user(self, client, db_session):
        """Scenario: Dashboard muestra tareas por usuario
        Given there are tasks assigned to different users
        When I access the dashboard
        Then I see a summary of tasks per assigned user.
        """
        alice = await _create_user(db_session, email="alice@example.com", name="Alice")
        bob = await _create_user(db_session, email="bob@example.com", name="Bob")

        # Alice: 3 tasks assigned
        for i in range(3):
            await _create_task(
                db_session,
                alice.id,
                title=f"Alice task {i}",
                assigned_to=alice.id,
            )
        # Bob: 2 tasks assigned
        for i in range(2):
            await _create_task(
                db_session,
                bob.id,
                title=f"Bob task {i}",
                assigned_to=bob.id,
            )
        # Unassigned task — should not appear in tasks_by_user
        await _create_task(db_session, alice.id, title="Unassigned")

        response = await client.get(
            "/api/v1/dashboard/stats", headers=_auth_header(alice)
        )
        assert response.status_code == 200
        data = response.json()

        by_user = {u["user_name"]: u["count"] for u in data["tasks_by_user"]}
        assert by_user["Alice"] == 3
        assert by_user["Bob"] == 2
        assert data["total_tasks"] == 6

    @pytest.mark.asyncio
    async def test_dashboard_no_tasks_all_zeros(self, client, db_session):
        """Scenario: Dashboard sin tareas
        Given there are no tasks in the system
        When I access the dashboard
        Then I see all metrics at 0.
        """
        user = await _create_user(db_session)

        response = await client.get(
            "/api/v1/dashboard/stats", headers=_auth_header(user)
        )
        assert response.status_code == 200
        data = response.json()

        assert data["total_tasks"] == 0
        assert data["overdue_tasks"] == 0
        assert data["tasks_by_status"]["todo"] == 0
        assert data["tasks_by_status"]["in_progress"] == 0
        assert data["tasks_by_status"]["done"] == 0
        assert data["tasks_by_status"]["cancelled"] == 0
        assert data["tasks_by_user"] == []
        assert data["tasks_by_priority"] == {}

    @pytest.mark.asyncio
    async def test_dashboard_excludes_deleted_tasks(self, client, db_session):
        """Deleted tasks should not appear in any dashboard metric."""
        user = await _create_user(db_session)
        await _create_task(db_session, user.id, title="Active", status="todo")
        await _create_task(
            db_session, user.id, title="Deleted", status="todo", is_deleted=True
        )

        response = await client.get(
            "/api/v1/dashboard/stats", headers=_auth_header(user)
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_tasks"] == 1
        assert data["tasks_by_status"]["todo"] == 1

    @pytest.mark.asyncio
    async def test_dashboard_tasks_by_priority(self, client, db_session):
        """Dashboard shows correct counts by priority."""
        user = await _create_user(db_session)
        for priority in ["high", "high", "low", "medium"]:
            task = Task(
                title=f"Task {priority}",
                created_by=user.id,
                priority=priority,
            )
            db_session.add(task)
        await db_session.commit()

        response = await client.get(
            "/api/v1/dashboard/stats", headers=_auth_header(user)
        )
        assert response.status_code == 200
        data = response.json()
        assert data["tasks_by_priority"]["high"] == 2
        assert data["tasks_by_priority"]["low"] == 1
        assert data["tasks_by_priority"]["medium"] == 1

    @pytest.mark.asyncio
    async def test_dashboard_member_can_access(self, client, db_session):
        """Persona: Member can access dashboard."""
        member = await _create_user(db_session, role="member")
        response = await client.get(
            "/api/v1/dashboard/stats", headers=_auth_header(member)
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_dashboard_admin_can_access(self, client, db_session):
        """Persona: Admin can access dashboard."""
        admin = await _create_user(db_session, role="admin")
        response = await client.get(
            "/api/v1/dashboard/stats", headers=_auth_header(admin)
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_dashboard_unauthenticated_rejected(self, client):
        """Unauthenticated user cannot access dashboard."""
        response = await client.get("/api/v1/dashboard/stats")
        assert response.status_code == 401
