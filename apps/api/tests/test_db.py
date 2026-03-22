from sqlalchemy.orm import DeclarativeBase

from app.db.base import Base
from app.db.session import async_session_factory, engine
from app.models import Base as ModelsBase


def test_base_is_declarative():
    assert issubclass(Base, DeclarativeBase)


def test_models_reexport_base():
    assert ModelsBase is Base


def test_engine_is_configured():
    assert engine is not None
    assert "taskflow" in str(engine.url)


def test_async_session_factory_exists():
    assert async_session_factory is not None


async def test_get_db_yields_session(db_session):
    """Verify the test DB session is usable."""
    assert db_session is not None
