from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Tuple

from sqlalchemy.orm import Session, sessionmaker, scoped_session

from pricewatch.db.config import create_test_engine_and_session, session_scope, get_scoped_session
from pricewatch.db.base import Base


def make_test_db():
    """Create a fresh in-memory SQLite DB and return (engine, factory, scoped_session).

    All three objects are wired to the *same* engine so that data written
    through the session factory is immediately visible to any other session
    created from the same factory — including sessions used inside a Flask
    app created with ``create_app({"DATABASE_URL": url, "TESTING": True})``.

    Usage in fixtures::

        engine, factory, scoped = make_test_db()
        app = create_app({"DATABASE_URL": str(engine.url), "TESTING": True})
        # app.extensions["db_scoped_session"] already uses the same URL,
        # but to guarantee the *same* engine instance inject it directly:
        with app.app_context():
            app.extensions["db_engine"] = engine
            app.extensions["db_session_factory"] = factory
            app.extensions["db_scoped_session"] = scoped
    """
    engine, factory = create_test_engine_and_session()
    _scoped = get_scoped_session(factory)
    return engine, factory, _scoped


def make_test_session_factory() -> Tuple[Session, sessionmaker[Session]]:
    engine, factory = create_test_engine_and_session()
    return factory(), factory


@contextmanager
def test_session_scope() -> Iterator[Session]:
    engine, factory = create_test_engine_and_session()
    try:
        with session_scope(factory) as session:
            yield session
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()
