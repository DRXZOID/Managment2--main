from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from typing import Iterator, Optional, Type

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker, Session

from .base import Base

logger = logging.getLogger(__name__)

DEFAULT_DB_URL = "sqlite:///pricewatch.db"
IN_MEMORY_URL = "sqlite+pysqlite:///:memory:"


def _coerce_bool(value: Optional[str]) -> bool:
    if value is None:
        return False
    return value.lower() in {"1", "true", "yes", "on"}


def resolve_database_url(app_config: Optional[dict] = None) -> str:
    """Return the database URL from config dict or environment variable.

    Priority: app_config["DATABASE_URL"] > DATABASE_URL env var > DEFAULT_DB_URL (SQLite).
    The backend is selected through this single pathway — no backend-specific
    branching exists in services or repositories.
    """
    if app_config and app_config.get("DATABASE_URL"):
        return str(app_config["DATABASE_URL"])
    return os.getenv("DATABASE_URL", DEFAULT_DB_URL)


def _is_sqlite_url(url: str) -> bool:
    return url.startswith("sqlite")


def _is_test_or_dev_mode(app_config: Optional[dict] = None) -> bool:
    """Return True when runtime schema creation (create_all) is permitted.

    Runtime schema auto-create is a convenience mechanism for test and local
    development workflows ONLY.  For non-test PostgreSQL deployments Alembic
    is the canonical schema authority — use ``alembic upgrade head`` instead
    of relying on this path.

    Permitted when ANY of the following is true:
    - TESTING flag is set in app_config
    - APP_ENV / FLASK_ENV is "development", "dev", "test", or "testing"
    - DB_ALLOW_CREATE_ALL=1 is set explicitly in the environment

    Blocked (returns False) when:
    - DB_SKIP_CREATE_ALL=1 env var is set
    - FLASK_ENV / APP_ENV is "production" or "staging"
    """
    cfg = app_config or {}

    # Explicit opt-out always wins
    if _coerce_bool(os.getenv("DB_SKIP_CREATE_ALL")):
        return False

    env_name = (cfg.get("FLASK_ENV") or cfg.get("APP_ENV")
                or os.getenv("FLASK_ENV") or os.getenv("APP_ENV", "")).lower()

    if env_name in {"production", "staging"}:
        return False

    # Explicit opt-in
    if _coerce_bool(os.getenv("DB_ALLOW_CREATE_ALL")):
        return True

    # TESTING flag (pytest / integration tests)
    if cfg.get("TESTING"):
        return True

    # Local / dev environments with explicit names
    if env_name in {"development", "dev", "test", "testing"}:
        return True

    # When no environment is set, be conservative for non-SQLite backends.
    # Allow implicit create_all only for SQLite URLs unless explicitly opted in.
    if env_name == "":
        url = resolve_database_url(app_config)
        if _is_sqlite_url(url):
            return True
        return False
    return False


def should_skip_create_all(app_config: Optional[dict] = None) -> bool:
    """Return True when runtime schema creation should be skipped."""
    return not _is_test_or_dev_mode(app_config)


def init_engine(app_config: Optional[dict] = None) -> Engine:
    """Create and return a SQLAlchemy Engine.

    Backend is selected transparently from the resolved DATABASE_URL.
    SQLite and PostgreSQL are handled by the same code path — no
    backend-specific branches exist here.
    """
    url = resolve_database_url(app_config)
    echo = _coerce_bool(str((app_config or {}).get("DB_DEBUG_SQL", os.getenv("DB_DEBUG_SQL", ""))))
    connect_args = {"check_same_thread": False} if _is_sqlite_url(url) else {}
    engine = create_engine(url, echo=echo, future=True, connect_args=connect_args)
    _log_backend_selection(url)
    return engine


def _log_backend_selection(url: str) -> None:
    """Emit a startup log that clearly states the selected database backend."""
    if _is_sqlite_url(url):
        backend = "SQLite"
    elif "postgresql" in url or "postgres" in url:
        backend = "PostgreSQL"
    else:
        backend = url.split(":")[0]
    # Mask credentials in log output
    safe_url = url.split("@")[-1] if "@" in url else url
    logger.info("Database backend selected: %s (%s)", backend, safe_url)


def get_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)


def get_scoped_session(factory: sessionmaker[Session]):
    return scoped_session(factory)


def init_db(engine: Engine, *, base: Type[Base] = Base, app_config: Optional[dict] = None) -> None:
    """Convenience schema bootstrap for test/dev workflows.

    IMPORTANT: This function is a test/development convenience only.
    For non-test environments (especially PostgreSQL) use Alembic migrations
    as the canonical schema authority:  ``alembic upgrade head``

    For PostgreSQL in production/staging this function is a no-op — if the
    schema is missing the application will fail fast with a clear error rather
    than silently creating tables outside of migration control.
    """
    url = str(engine.url)
    if should_skip_create_all(app_config):
        # Non-test/non-dev environment: do NOT create schema automatically.
        # Alembic is the canonical schema authority here.
        # Perform a fast connectivity check so misconfiguration is caught early.
        if not _is_sqlite_url(url):
            _assert_schema_exists(engine)
        return
    # Test / local dev path: create schema via ORM for convenience.
    base.metadata.create_all(engine)


def _assert_schema_exists(engine: Engine) -> None:
    """Verify DB connectivity and that at least the 'stores' table is present.

    Raises RuntimeError with a clear message if the schema is missing,
    guiding operators to run ``alembic upgrade head``.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1 FROM stores LIMIT 1"))
    except Exception as exc:
        raise RuntimeError(
            "Database schema is missing or inaccessible.  "
            "Run 'alembic upgrade head' to initialise the schema before starting "
            "the application in non-development mode.  "
            f"Original error: {exc}"
        ) from exc


@contextmanager
def session_scope(factory: sessionmaker[Session]) -> Iterator[Session]:
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_test_engine_and_session():
    """Create an in-memory SQLite engine for test/dev convenience.

    This is explicitly a test/dev helper — not a production schema path.
    Schema is created via create_all (ORM convenience), not Alembic.
    """
    engine = create_engine(IN_MEMORY_URL, echo=False, future=True, connect_args={"check_same_thread": False})
    factory = get_session_factory(engine)
    Base.metadata.create_all(engine)
    return engine, factory
