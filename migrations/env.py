from __future__ import annotations

import os
from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from alembic import context

from pricewatch.db import Base  # noqa
from pricewatch.db import models  # noqa: F401  # ensure models are loaded

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# ---------------------------------------------------------------------------
# Alembic is the canonical non-test schema authority.
# For local SQLite dev without a DATABASE_URL the default fallback is used.
# For PostgreSQL always set DATABASE_URL and run: alembic upgrade head
# ---------------------------------------------------------------------------
_SQLITE_DEFAULT = "sqlite:///pricewatch.db"


def get_url() -> str:
    return os.getenv("DATABASE_URL", _SQLITE_DEFAULT)


def _is_sqlite(url: str) -> bool:
    return url.startswith("sqlite")


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # render_as_batch allows ALTER TABLE on SQLite via table recreation
        render_as_batch=_is_sqlite(url),
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = get_url()
    connectable = create_engine(
        url,
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # render_as_batch allows ALTER TABLE on SQLite via table recreation
            render_as_batch=_is_sqlite(url),
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
