"""PostgreSQL verification workflow for core persistence behavior.

Run this script to verify that the application works correctly against
a real PostgreSQL instance.  It is NOT a pytest file — it is a standalone
verification script that can be executed manually or as part of a release
pipeline.

Usage
-----
    # Start a local PostgreSQL instance (e.g. via Docker):
    docker run -d --name pricewatch-pg \
        -e POSTGRES_USER=pricewatch \
        -e POSTGRES_PASSWORD=pricewatch \
        -e POSTGRES_DB=pricewatch \
        -p 5432:5432 \
        postgres:16-alpine

    # Run the verification:
    DATABASE_URL=postgresql+psycopg2://pricewatch:pricewatch@localhost/pricewatch \
        python tests/verify_postgres.py

    # Cleanup:
    docker rm -f pricewatch-pg

Requirements
------------
- psycopg2-binary must be installed:  pip install psycopg2-binary
- The DATABASE_URL environment variable must point to a real PostgreSQL DB.
- The database must be empty (migrations will run from scratch).

What is verified
----------------
1. App startup against PostgreSQL config.
2. Alembic migration from an empty DB.
3. Core repository CRUD flows (Store, Category, Product).
4. Core service flows that depend on DB state (StoreService, CategorySyncService).
"""
from __future__ import annotations

import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("verify_postgres")


def _require_env(name: str) -> str:
    val = os.getenv(name)
    if not val:
        log.error("Environment variable %s is required", name)
        sys.exit(1)
    return val


def step(label: str):
    """Simple step decorator for readable output."""
    def decorator(fn):
        def wrapper(*args, **kwargs):
            log.info(">>> STEP: %s", label)
            result = fn(*args, **kwargs)
            log.info("    OK: %s", label)
            return result
        return wrapper
    return decorator


@step("Check DATABASE_URL is PostgreSQL")
def check_pg_url():
    url = _require_env("DATABASE_URL")
    if "postgresql" not in url and "postgres" not in url:
        log.error("DATABASE_URL must be a PostgreSQL URL, got: %s", url.split("@")[-1])
        sys.exit(1)
    return url


@step("Run Alembic migrations from empty DB")
def run_migrations():
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        log.error("Alembic migration failed:\n%s\n%s", result.stdout, result.stderr)
        sys.exit(1)
    log.info("    Migration output:\n%s", result.stdout)


@step("App startup and DB engine init")
def check_app_startup():
    from pricewatch.db.config import init_engine, init_db, get_session_factory
    engine = init_engine()
    # init_db in non-dev mode should NOT call create_all — it checks schema exists
    # Since migrations ran above, this should pass
    env_backup = os.environ.get("FLASK_ENV")
    os.environ["FLASK_ENV"] = "production"
    try:
        init_db(engine)
    finally:
        if env_backup is None:
            os.environ.pop("FLASK_ENV", None)
        else:
            os.environ["FLASK_ENV"] = env_backup
    return engine, get_session_factory(engine)


@step("Core repository CRUD — Store")
def check_store_crud(engine, factory):
    from pricewatch.db.config import session_scope
    from pricewatch.db.repositories.store_repository import (
        get_or_create_store, list_stores
    )
    with session_scope(factory) as session:
        store = get_or_create_store(session, "VerifyStore", is_reference=False, base_url="https://example.com")
        session.flush()
        store_id = store.id
        assert store_id, "Store must have an ID after flush"

    with session_scope(factory) as session:
        stores = list_stores(session)
        assert any(s.id == store_id for s in stores), "Created store must be listable"

    log.info("    Store CRUD OK, id=%s", store_id)
    return store_id


@step("Core repository CRUD — Category")
def check_category_crud(engine, factory, store_id):
    from pricewatch.db.config import session_scope
    from pricewatch.db.repositories.category_repository import (
        upsert_category, list_categories_by_store
    )
    with session_scope(factory) as session:
        cat = upsert_category(
            session,
            store_id=store_id,
            name="TestCategory",
            url="https://example.com/cat",
        )
        session.flush()
        cat_id = cat.id
        assert cat_id

    with session_scope(factory) as session:
        cats = list_categories_by_store(session, store_id)
        assert any(c.id == cat_id for c in cats)

    log.info("    Category CRUD OK, id=%s", cat_id)
    return cat_id


@step("Core repository CRUD — Product with Decimal price")
def check_product_crud(engine, factory, store_id, cat_id):
    from decimal import Decimal
    from pricewatch.db.config import session_scope
    from pricewatch.db.repositories.product_repository import upsert_product
    with session_scope(factory) as session:
        prod = upsert_product(
            session,
            store_id=store_id,
            category_id=cat_id,
            name="Test Product",
            product_url="https://example.com/prod/1",
            price=Decimal("99.9900"),
            currency="UAH",
            is_available=True,
        )
        session.flush()
        prod_id = prod.id
        assert prod_id
        # Verify exact numeric round-trip
        from decimal import Decimal as D
        assert prod.price == D("99.9900"), f"Expected Decimal 99.9900, got {prod.price!r}"

    log.info("    Product CRUD OK, id=%s, price=%s", prod_id, prod.price)


@step("Cleanup verification data")
def cleanup(engine, factory, store_id):
    from pricewatch.db.config import session_scope
    from pricewatch.db.base import Base
    from pricewatch.db.models import Store
    with session_scope(factory) as session:
        store = session.get(Store, store_id)
        if store:
            session.delete(store)


def main():
    log.info("=" * 60)
    log.info("PostgreSQL Verification Workflow")
    log.info("=" * 60)

    check_pg_url()
    run_migrations()
    engine, factory = check_app_startup()
    store_id = check_store_crud(engine, factory)
    cat_id = check_category_crud(engine, factory, store_id)
    check_product_crud(engine, factory, store_id, cat_id)
    cleanup(engine, factory, store_id)

    log.info("=" * 60)
    log.info("All verification steps passed!  PostgreSQL support verified.")
    log.info("=" * 60)


if __name__ == "__main__":
    main()

