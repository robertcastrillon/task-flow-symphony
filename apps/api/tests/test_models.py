import uuid

from app.db.session import Base
from app.models import Comment, Task, User


def test_user_model_table_name():
    assert User.__tablename__ == "users"


def test_user_model_columns():
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
    }
    assert expected == columns


def test_user_model_email_unique():
    email_col = User.__table__.columns["email"]
    assert email_col.unique is True


def test_user_model_email_indexed():
    email_col = User.__table__.columns["email"]
    assert email_col.index is True


def test_user_model_id_is_uuid():
    id_col = User.__table__.columns["id"]
    assert id_col.primary_key is True


def test_task_model_table_name():
    assert Task.__tablename__ == "tasks"


def test_task_model_columns():
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


def test_task_model_status_indexed():
    status_col = Task.__table__.columns["status"]
    assert status_col.index is True


def test_task_model_priority_indexed():
    priority_col = Task.__table__.columns["priority"]
    assert priority_col.index is True


def test_task_model_is_deleted_indexed():
    col = Task.__table__.columns["is_deleted"]
    assert col.index is True


def test_task_model_foreign_keys():
    created_by_col = Task.__table__.columns["created_by"]
    assigned_to_col = Task.__table__.columns["assigned_to"]
    assert len(created_by_col.foreign_keys) == 1
    assert len(assigned_to_col.foreign_keys) == 1
    fk_created = list(created_by_col.foreign_keys)[0]
    fk_assigned = list(assigned_to_col.foreign_keys)[0]
    assert str(fk_created.target_fullname) == "users.id"
    assert str(fk_assigned.target_fullname) == "users.id"


def test_task_model_assigned_to_nullable():
    col = Task.__table__.columns["assigned_to"]
    assert col.nullable is True


def test_comment_model_table_name():
    assert Comment.__tablename__ == "comments"


def test_comment_model_columns():
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


def test_comment_model_foreign_keys():
    task_id_col = Comment.__table__.columns["task_id"]
    author_id_col = Comment.__table__.columns["author_id"]
    assert len(task_id_col.foreign_keys) == 1
    assert len(author_id_col.foreign_keys) == 1
    fk_task = list(task_id_col.foreign_keys)[0]
    fk_author = list(author_id_col.foreign_keys)[0]
    assert str(fk_task.target_fullname) == "tasks.id"
    assert str(fk_author.target_fullname) == "users.id"


def test_comment_task_id_indexed():
    col = Comment.__table__.columns["task_id"]
    assert col.index is True


def test_all_models_registered_in_base():
    table_names = set(Base.metadata.tables.keys())
    assert "users" in table_names
    assert "tasks" in table_names
    assert "comments" in table_names


def test_user_repr():
    user = User.__new__(User)
    user.__dict__["email"] = "test@example.com"
    assert repr(user) == "<User test@example.com>"


def test_task_repr():
    task = Task.__new__(Task)
    task.__dict__["title"] = "Test task"
    assert repr(task) == "<Task Test task>"


def test_comment_repr():
    comment = Comment.__new__(Comment)
    test_id = uuid.uuid4()
    comment.__dict__["id"] = test_id
    assert repr(comment) == f"<Comment {test_id}>"
