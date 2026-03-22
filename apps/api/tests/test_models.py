import uuid

from app.db.base import Base
from app.models import Comment, Task, User


class TestUserModel:
    def test_user_table_name(self):
        assert User.__tablename__ == "users"

    def test_user_has_required_columns(self):
        columns = {c.name for c in User.__table__.columns}
        expected = {
            "id",
            "email",
            "name",
            "hashed_password",
            "avatar_url",
            "role",
            "telegram_chat_id",
            "is_active",
            "created_at",
            "updated_at",
        }
        assert expected == columns

    def test_user_email_unique(self):
        email_col = User.__table__.columns["email"]
        assert email_col.unique is True

    def test_user_email_indexed(self):
        email_col = User.__table__.columns["email"]
        assert email_col.index is True

    def test_user_id_is_uuid_primary_key(self):
        id_col = User.__table__.columns["id"]
        assert id_col.primary_key is True

    def test_user_defaults(self):
        is_active_col = User.__table__.columns["is_active"]
        assert is_active_col.default.arg is True

    def test_user_role_default(self):
        role_col = User.__table__.columns["role"]
        assert role_col.default.arg == "member"

    def test_user_repr(self):
        user = User.__new__(User)
        user.__dict__["email"] = "test@example.com"
        assert repr(user) == "<User test@example.com>"


class TestTaskModel:
    def test_task_table_name(self):
        assert Task.__tablename__ == "tasks"

    def test_task_has_required_columns(self):
        columns = {c.name for c in Task.__table__.columns}
        expected = {
            "id",
            "title",
            "description",
            "status",
            "priority",
            "due_date",
            "tags",
            "is_deleted",
            "created_by",
            "assigned_to",
            "created_at",
            "updated_at",
            "completed_at",
        }
        assert expected == columns

    def test_task_status_indexed(self):
        col = Task.__table__.columns["status"]
        assert col.index is True

    def test_task_priority_indexed(self):
        col = Task.__table__.columns["priority"]
        assert col.index is True

    def test_task_is_deleted_indexed(self):
        col = Task.__table__.columns["is_deleted"]
        assert col.index is True

    def test_task_soft_delete_default(self):
        is_deleted_col = Task.__table__.columns["is_deleted"]
        assert is_deleted_col.default.arg is False

    def test_task_status_default(self):
        status_col = Task.__table__.columns["status"]
        assert status_col.default.arg == "todo"

    def test_task_priority_default(self):
        priority_col = Task.__table__.columns["priority"]
        assert priority_col.default.arg == "medium"

    def test_task_foreign_keys(self):
        created_by = Task.__table__.columns["created_by"]
        assigned_to = Task.__table__.columns["assigned_to"]
        assert len(created_by.foreign_keys) == 1
        assert len(assigned_to.foreign_keys) == 1
        fk_created = list(created_by.foreign_keys)[0]
        fk_assigned = list(assigned_to.foreign_keys)[0]
        assert str(fk_created.target_fullname) == "users.id"
        assert str(fk_assigned.target_fullname) == "users.id"

    def test_task_created_by_not_nullable(self):
        created_by = Task.__table__.columns["created_by"]
        assert created_by.nullable is False

    def test_task_assigned_to_nullable(self):
        assigned_to = Task.__table__.columns["assigned_to"]
        assert assigned_to.nullable is True

    def test_task_repr(self):
        task = Task.__new__(Task)
        task.__dict__["title"] = "Test task"
        assert repr(task) == "<Task Test task>"


class TestCommentModel:
    def test_comment_table_name(self):
        assert Comment.__tablename__ == "comments"

    def test_comment_has_required_columns(self):
        columns = {c.name for c in Comment.__table__.columns}
        expected = {
            "id",
            "content",
            "task_id",
            "author_id",
            "created_at",
            "updated_at",
        }
        assert expected == columns

    def test_comment_foreign_keys(self):
        task_id_col = Comment.__table__.columns["task_id"]
        author_id_col = Comment.__table__.columns["author_id"]
        assert len(task_id_col.foreign_keys) == 1
        assert len(author_id_col.foreign_keys) == 1
        fk_task = list(task_id_col.foreign_keys)[0]
        fk_author = list(author_id_col.foreign_keys)[0]
        assert str(fk_task.target_fullname) == "tasks.id"
        assert str(fk_author.target_fullname) == "users.id"

    def test_comment_task_id_indexed(self):
        col = Comment.__table__.columns["task_id"]
        assert col.index is True

    def test_comment_content_not_nullable(self):
        content = Comment.__table__.columns["content"]
        assert content.nullable is False

    def test_comment_repr(self):
        comment = Comment.__new__(Comment)
        test_id = uuid.uuid4()
        comment.__dict__["id"] = test_id
        assert repr(comment) == f"<Comment {test_id}>"


class TestBaseMetadata:
    def test_all_models_registered_in_base(self):
        table_names = set(Base.metadata.tables.keys())
        assert "users" in table_names
        assert "tasks" in table_names
        assert "comments" in table_names
