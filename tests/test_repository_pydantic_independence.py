"""Commit 12: Repository layer Pydantic independence enforcement.

These tests verify that repository code does not import or depend on
Pydantic or the pricewatch.schemas package — enforcing the ADR-0006
architectural boundary.

Repository methods MUST accept only:
  - plain Python scalars (int, str, float, bool, None)
  - standard library types (datetime, Decimal)
  - SQLAlchemy ORM entity instances
  - SQLAlchemy Session

Repository methods MUST NOT accept:
  - Pydantic BaseModel instances
  - pricewatch.schemas.* classes
  - Any type that requires Pydantic to be installed

This test module is a static boundary check. It imports repository
modules and verifies no Pydantic symbols are present in their namespace.
"""
from __future__ import annotations

import importlib
import pkgutil
import sys
from types import ModuleType
from typing import List

import pytest


def _get_repository_modules() -> List[ModuleType]:
    """Return all loaded modules from pricewatch.db.repositories."""
    import pricewatch.db.repositories  # ensure package is loaded
    pkg = importlib.import_module("pricewatch.db.repositories")
    modules = [pkg]
    for finder, name, ispkg in pkgutil.iter_modules(pkg.__path__, prefix=pkg.__name__ + "."):
        try:
            mod = importlib.import_module(name)
            modules.append(mod)
        except ImportError:
            pass
    return modules


def _has_pydantic_dependency(module: ModuleType) -> bool:
    """Return True if a module directly imports pydantic or pricewatch.schemas."""
    source_file = getattr(module, "__file__", None)
    if not source_file or not source_file.endswith(".py"):
        return False
    try:
        with open(source_file) as f:
            content = f.read()
    except (OSError, IOError):
        return False

    # Check for direct pydantic imports
    pydantic_indicators = [
        "import pydantic",
        "from pydantic",
        "from pricewatch.schemas",
        "import pricewatch.schemas",
    ]
    for indicator in pydantic_indicators:
        if indicator in content:
            return True
    return False


class TestRepositoryPydanticIndependence:
    """Verify all repository modules are free of Pydantic dependencies."""

    def test_no_pydantic_import_in_store_repository(self):
        import pricewatch.db.repositories.store_repository as mod
        assert not _has_pydantic_dependency(mod), (
            "store_repository must not import pydantic or pricewatch.schemas"
        )

    def test_no_pydantic_import_in_category_repository(self):
        import pricewatch.db.repositories.category_repository as mod
        assert not _has_pydantic_dependency(mod), (
            "category_repository must not import pydantic or pricewatch.schemas"
        )

    def test_no_pydantic_import_in_product_repository(self):
        import pricewatch.db.repositories.product_repository as mod
        assert not _has_pydantic_dependency(mod), (
            "product_repository must not import pydantic or pricewatch.schemas"
        )

    def test_no_pydantic_import_in_mapping_repository(self):
        import pricewatch.db.repositories.mapping_repository as mod
        assert not _has_pydantic_dependency(mod), (
            "mapping_repository must not import pydantic or pricewatch.schemas"
        )

    def test_no_pydantic_import_in_scrape_run_repository(self):
        import pricewatch.db.repositories.scrape_run_repository as mod
        assert not _has_pydantic_dependency(mod), (
            "scrape_run_repository must not import pydantic or pricewatch.schemas"
        )

    def test_no_pydantic_import_in_gap_repository(self):
        import pricewatch.db.repositories.gap_repository as mod
        assert not _has_pydantic_dependency(mod), (
            "gap_repository must not import pydantic or pricewatch.schemas"
        )

    def test_all_repository_modules_pydantic_free(self):
        """Broad check: any new repository module added later must also be pydantic-free."""
        offenders = []
        for mod in _get_repository_modules():
            if _has_pydantic_dependency(mod):
                offenders.append(mod.__name__)
        assert not offenders, (
            f"The following repository modules import Pydantic or pricewatch.schemas "
            f"(violates ADR-0006 boundary): {offenders!r}\n"
            "Repositories must accept plain scalars, datetime/Decimal, and ORM entities only."
        )


class TestRepositorySignaturesAcceptScalars:
    """Spot-check that key repository functions still accept plain Python scalars."""

    def test_upsert_product_accepts_decimal_price(self):
        """upsert_product must accept Decimal (stdlib) price — not a Pydantic Decimal field."""
        from decimal import Decimal
        from pricewatch.db.testing import test_session_scope
        from pricewatch.db.repositories.product_repository import upsert_product
        from pricewatch.db.repositories.store_repository import get_or_create_store
        from pricewatch.db.repositories.category_repository import upsert_category

        with test_session_scope() as session:
            store = get_or_create_store(session, "ScalarTestStore", is_reference=False)
            cat = upsert_category(session, store_id=store.id, name="ScalarCat")
            session.flush()
            prod = upsert_product(
                session,
                store_id=store.id,
                category_id=cat.id,
                name="Scalar Price Product",
                product_url="https://scalar.test/p/1",
                price=Decimal("199.9900"),
                currency="UAH",
            )
            session.flush()
            assert prod.id is not None
            # price stored and retrievable as Decimal-compatible value
            assert float(prod.price) == pytest.approx(199.99, rel=1e-4)

    def test_upsert_category_accepts_plain_strings(self):
        """upsert_category must accept plain str name/url — no Pydantic wrappers."""
        from pricewatch.db.testing import test_session_scope
        from pricewatch.db.repositories.category_repository import upsert_category
        from pricewatch.db.repositories.store_repository import get_or_create_store

        with test_session_scope() as session:
            store = get_or_create_store(session, "ScalarCatStore", is_reference=False)
            cat = upsert_category(
                session,
                store_id=store.id,
                name="Plain String Category",
                url="https://plain.test/cat",
            )
            session.flush()
            assert cat.id is not None
            assert cat.name == "Plain String Category"

