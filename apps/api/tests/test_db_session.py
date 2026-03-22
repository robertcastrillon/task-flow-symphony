from sqlalchemy.ext.asyncio import async_sessionmaker

from app.db.base import Base
from app.db.session import async_session_factory, engine


def test_engine_is_async():
    assert engine is not None
    assert str(engine.url) != ""


def test_async_session_factory_exists():
    assert isinstance(async_session_factory, async_sessionmaker)


def test_base_is_declarative():
    assert hasattr(Base, "metadata")
    assert hasattr(Base, "registry")
