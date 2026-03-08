"""Regression tests: shared DB wiring between Flask test client and session helpers.

These tests explicitly prove that data inserted through a test session scope
is immediately visible to Flask endpoints called via test_client().

If the Flask app and the session helpers use different DB engines (e.g.
one uses the file-based pricewatch.db and the other uses :memory:) these
tests will fail with "mapped_target_categories == []".
"""
from __future__ import annotations

import pytest

from pricewatch.db.repositories.store_repository import get_or_create_store
from pricewatch.db.repositories.category_repository import (
    upsert_category,
    create_category_mapping,
)
from pricewatch.db.repositories.product_repository import upsert_product
from pricewatch.db.repositories.mapping_repository import create_product_mapping as repo_create_product_mapping


# ---------------------------------------------------------------------------
# 1. mapped-target-categories endpoint sees committed data
# ---------------------------------------------------------------------------

class TestSharedDbWiring:
    def test_mapped_target_categories_endpoint_sees_committed_data(
        self, client, db_session_scope
    ):
        """Core regression: Flask must read rows committed through the test session."""
        with db_session_scope() as session:
            ref_store = get_or_create_store(session, "RegRefStore", is_reference=True)
            tgt_store = get_or_create_store(session, "RegTgtStore", is_reference=False)
            ref_cat = upsert_category(session, store_id=ref_store.id, name="Reg-Skates")
            tgt_cat = upsert_category(session, store_id=tgt_store.id, name="Reg-Skates-T")
            create_category_mapping(
                session,
                reference_category_id=ref_cat.id,
                target_category_id=tgt_cat.id,
                match_type="manual",
            )
            session.flush()
            ref_cat_id = ref_cat.id
            tgt_cat_id = tgt_cat.id
        # committed here

        resp = client.get(f"/api/categories/{ref_cat_id}/mapped-target-categories")
        assert resp.status_code == 200, resp.data
        data = resp.get_json()

        assert "mapped_target_categories" in data
        mapped_ids = [m["target_category_id"] for m in data["mapped_target_categories"]]
        assert tgt_cat_id in mapped_ids, (
            f"Flask endpoint did not see committed data. "
            f"Expected target_category_id={tgt_cat_id} in {mapped_ids}. "
            f"This means the Flask app and the test session are using different DB engines."
        )

    def test_stores_endpoint_sees_committed_store(self, client, db_session_scope):
        """Flask /api/stores must return a store inserted through the test session."""
        with db_session_scope() as session:
            store = get_or_create_store(session, "WiringTestStore", is_reference=False)
            session.flush()
            store_id = store.id

        resp = client.get("/api/stores")
        assert resp.status_code == 200
        stores = resp.get_json()["stores"]
        ids = [s["id"] for s in stores]
        assert store_id in ids, (
            f"Flask /api/stores did not see store id={store_id}. "
            f"Shared DB wiring is broken."
        )

    def test_confirm_match_endpoint_creates_row_visible_to_session(
        self, client, flask_app, db_session_scope
    ):
        """confirm-match endpoint writes data that the test session can then read back."""
        from pricewatch.db.repositories.mapping_repository import get_product_mapping

        with db_session_scope() as session:
            ref_store = get_or_create_store(session, "CMRefStore", is_reference=True)
            tgt_store = get_or_create_store(session, "CMTgtStore", is_reference=False)
            ref_cat = upsert_category(session, store_id=ref_store.id, name="CM-Helmets")
            tgt_cat = upsert_category(session, store_id=tgt_store.id, name="CM-Helmets-T")
            create_category_mapping(
                session,
                reference_category_id=ref_cat.id,
                target_category_id=tgt_cat.id,
                match_type="manual",
            )
            ref_prod = upsert_product(
                session, store_id=ref_store.id, category_id=ref_cat.id,
                name="Bauer RE-AKT 200", price=3500, currency="UAH",
                product_url="https://ref.example.com/prod/bauer-reakt-200",
            )
            tgt_prod = upsert_product(
                session, store_id=tgt_store.id, category_id=tgt_cat.id,
                name="Bauer RE-AKT 200 SR", price=3600, currency="UAH",
                product_url="https://tgt.example.com/prod/bauer-reakt-200-sr",
            )
            session.flush()
            ref_prod_id = ref_prod.id
            tgt_prod_id = tgt_prod.id

        resp = client.post(
            "/api/comparison/confirm-match",
            json={
                "reference_product_id": ref_prod_id,
                "target_product_id": tgt_prod_id,
                "match_status": "confirmed",
                "confidence": 0.95,
            },
        )
        assert resp.status_code == 200, resp.data
        pm_data = resp.get_json()["product_mapping"]
        assert pm_data["match_status"] == "confirmed"

        # Now verify the row is readable through the test session (same engine)
        with db_session_scope() as session:
            pm = get_product_mapping(
                session,
                reference_product_id=ref_prod_id,
                target_product_id=tgt_prod_id,
            )
            assert pm is not None, (
                f"ProductMapping for ref={ref_prod_id}/tgt={tgt_prod_id} created by "
                f"Flask endpoint not found through test session — shared DB wiring is broken."
            )
            assert pm.match_status == "confirmed"

