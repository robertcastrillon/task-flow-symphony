import contextlib

from sqlalchemy.orm import DeclarativeBase

from app.db.base import Base
from app.db.session import async_session_factory, engine, get_db
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


async def test_get_db_yields_session():
    gen = get_db()
    session = await gen.__anext__()
    assert session is not None
    with contextlib.suppress(StopAsyncIteration):
        await gen.aclose()
