"""Tests for the DB-first ComparisonService and /api/comparison endpoint.

Covers:
  - Rejection when reference category not found / wrong store role
  - Rejection when target_category_id provided but pair not in category_mappings
  - Rejection when no mappings exist and target_category_id omitted
  - Valid comparison for a mapped pair (single target)
  - Valid comparison for all mapped targets (target_category_id omitted)
  - Stored ProductMapping rows are used first (stored matches bypass heuristic)
  - Heuristic fallback when no ProductMapping rows exist
  - Stable response shape (comparisons list) from POST /api/comparison
  - POST /api/comparison/confirm-match creates a ProductMapping row
"""
from __future__ import annotations

from types import SimpleNamespace
from datetime import datetime, timezone

import pytest

from pricewatch.db.testing import test_session_scope as _session_scope
from pricewatch.db.repositories.store_repository import get_or_create_store
from pricewatch.db.repositories.category_repository import upsert_category, create_category_mapping
from pricewatch.db.repositories.product_repository import upsert_product
from pricewatch.db.repositories.mapping_repository import create_product_mapping
from pricewatch.services.comparison_service import ComparisonService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_stores_and_categories(session):
    """Create a reference store + category and a target store + category (NO mapping)."""
    ref_store = get_or_create_store(session, "RefStore", is_reference=True, base_url="https://ref.example.com")
    tgt_store = get_or_create_store(session, "TgtStore", is_reference=False, base_url="https://tgt.example.com")
    ref_cat = upsert_category(session, store_id=ref_store.id, name="Skates", url="https://ref.example.com/skates")
    tgt_cat = upsert_category(session, store_id=tgt_store.id, name="Skates", url="https://tgt.example.com/skates")
    session.flush()
    return ref_store, tgt_store, ref_cat, tgt_cat


def _make_mapped_categories(session):
    """Like _make_stores_and_categories but also creates the category mapping."""
    ref_store, tgt_store, ref_cat, tgt_cat = _make_stores_and_categories(session)
    create_category_mapping(
        session,
        reference_category_id=ref_cat.id,
        target_category_id=tgt_cat.id,
        match_type="manual",
        confidence=1.0,
    )
    session.flush()
    return ref_store, tgt_store, ref_cat, tgt_cat


def _add_product(session, store_id, category_id, name, price, url_suffix):
    return upsert_product(
        session,
        store_id=store_id,
        product_url=f"https://example.com/product/{url_suffix}",
        name=name,
        price=price,
        currency="UAH",
        category_id=category_id,
    )


# ---------------------------------------------------------------------------
# ComparisonService – validation
# ---------------------------------------------------------------------------

class TestComparisonServiceValidation:
    def test_raises_if_reference_category_not_found(self):
        with _session_scope() as session:
            _, _, _, tgt_cat = _make_stores_and_categories(session)
            with pytest.raises(ValueError, match="not found"):
                ComparisonService(session).compare(reference_category_id=99999, target_category_id=tgt_cat.id)

    def test_raises_if_target_category_not_found(self):
        with _session_scope() as session:
            _, _, ref_cat, _ = _make_stores_and_categories(session)
            with pytest.raises(ValueError, match="not found"):
                ComparisonService(session).compare(reference_category_id=ref_cat.id, target_category_id=99999)

    def test_raises_when_reference_category_belongs_to_non_reference_store(self):
        with _session_scope() as session:
            _, _, _, tgt_cat = _make_stores_and_categories(session)
            with pytest.raises(ValueError, match="reference store"):
                ComparisonService(session).compare(reference_category_id=tgt_cat.id, target_category_id=tgt_cat.id)

    def test_raises_when_target_category_belongs_to_reference_store(self):
        with _session_scope() as session:
            _, _, ref_cat, _ = _make_stores_and_categories(session)
            with pytest.raises(ValueError, match="reference store"):
                ComparisonService(session).compare(reference_category_id=ref_cat.id, target_category_id=ref_cat.id)

    def test_raises_when_same_store_for_both(self):
        with _session_scope() as session:
            ref_store = get_or_create_store(session, "OnlyRef2", is_reference=True)
            cat_a = upsert_category(session, store_id=ref_store.id, name="CatA2")
            cat_b = upsert_category(session, store_id=ref_store.id, name="CatB2")
            session.flush()
            with pytest.raises(ValueError):
                ComparisonService(session).compare(reference_category_id=cat_a.id, target_category_id=cat_b.id)

    # --- Mapping-driven validation ---

    def test_raises_when_pair_not_mapped(self):
        """If target_category_id is provided but no mapping exists, must raise ValueError."""
        with _session_scope() as session:
            _, _, ref_cat, tgt_cat = _make_stores_and_categories(session)
            # deliberately NO category mapping created
            with pytest.raises(ValueError, match="маппінг"):
                ComparisonService(session).compare(
                    reference_category_id=ref_cat.id,
                    target_category_id=tgt_cat.id,
                )

    def test_raises_when_no_mappings_and_target_omitted(self):
        """If target_category_id is omitted and no mappings exist, must raise ValueError."""
        with _session_scope() as session:
            _, _, ref_cat, _ = _make_stores_and_categories(session)
            with pytest.raises(ValueError, match="меппінг"):
                ComparisonService(session).compare(reference_category_id=ref_cat.id)

    def test_mapped_pair_does_not_raise(self):
        """A mapped pair must NOT raise even with empty product lists."""
        with _session_scope() as session:
            _, _, ref_cat, tgt_cat = _make_mapped_categories(session)
            result = ComparisonService(session).compare(
                reference_category_id=ref_cat.id,
                target_category_id=tgt_cat.id,
            )
        assert "comparisons" in result
        assert len(result["comparisons"]) == 1

    def test_all_mapped_targets_when_target_omitted(self):
        """When target_category_id is omitted, all mapped targets are compared."""
        with _session_scope() as session:
            _, _, ref_cat, tgt_cat = _make_mapped_categories(session)
            result = ComparisonService(session).compare(reference_category_id=ref_cat.id)
        assert len(result["comparisons"]) == 1
        assert result["comparisons"][0]["target_category"]["id"] == tgt_cat.id


# ---------------------------------------------------------------------------
# ComparisonService – response shape
# ---------------------------------------------------------------------------

class TestComparisonServiceResponseShape:
    def test_returns_new_shape_keys(self):
        with _session_scope() as session:
            _, _, ref_cat, tgt_cat = _make_mapped_categories(session)
            result = ComparisonService(session).compare(ref_cat.id, tgt_cat.id)

        assert "reference_category" in result
        assert "mapped_target_categories" in result
        assert "comparisons" in result
        assert isinstance(result["comparisons"], list)
        assert len(result["comparisons"]) == 1

    def test_comparison_item_has_required_keys(self):
        with _session_scope() as session:
            _, _, ref_cat, tgt_cat = _make_mapped_categories(session)
            result = ComparisonService(session).compare(ref_cat.id, tgt_cat.id)

        comp = result["comparisons"][0]
        for key in ("target_category", "summary", "matches", "ambiguous",
                    "only_in_reference", "only_in_target"):
            assert key in comp, f"missing key in comparison item: {key}"

    def test_summary_keys_present(self):
        with _session_scope() as session:
            _, _, ref_cat, tgt_cat = _make_mapped_categories(session)
            result = ComparisonService(session).compare(ref_cat.id, tgt_cat.id)

        summary = result["comparisons"][0]["summary"]
        for key in ("reference_total", "target_total", "matched", "only_in_reference",
                    "only_in_target", "ambiguous"):
            assert key in summary, f"missing summary key: {key}"

    def test_empty_categories_give_zero_totals(self):
        with _session_scope() as session:
            _, _, ref_cat, tgt_cat = _make_mapped_categories(session)
            result = ComparisonService(session).compare(ref_cat.id, tgt_cat.id)

        s = result["comparisons"][0]["summary"]
        assert s["reference_total"] == 0
        assert s["target_total"] == 0
        assert s["matched"] == 0

    def test_reference_category_info_in_result(self):
        with _session_scope() as session:
            _, _, ref_cat, tgt_cat = _make_mapped_categories(session)
            result = ComparisonService(session).compare(ref_cat.id, tgt_cat.id)

        assert result["reference_category"]["name"] == "Skates"
        assert result["reference_category"]["is_reference"] is True
        assert result["comparisons"][0]["target_category"]["name"] == "Skates"
        assert result["comparisons"][0]["target_category"]["is_reference"] is False

    def test_mapped_target_categories_metadata(self):
        with _session_scope() as session:
            _, _, ref_cat, tgt_cat = _make_mapped_categories(session)
            result = ComparisonService(session).compare(ref_cat.id, tgt_cat.id)

        assert len(result["mapped_target_categories"]) == 1
        meta = result["mapped_target_categories"][0]
        assert meta["target_category_id"] == tgt_cat.id
        assert meta["match_type"] == "manual"


# ---------------------------------------------------------------------------
# ComparisonService – heuristic matching
# ---------------------------------------------------------------------------

class TestComparisonServiceHeuristicMatching:
    def test_unmatched_products_end_up_in_only_in_reference_or_target(self):
        with _session_scope() as session:
            ref_store, tgt_store, ref_cat, tgt_cat = _make_mapped_categories(session)
            _add_product(session, ref_store.id, ref_cat.id, "Bauer Vapor X5 SR", 4500, "ref-1hm")
            _add_product(session, tgt_store.id, tgt_cat.id, "CCM Tacks AS-V SR", 5200, "tgt-1hm")
            session.flush()
            result = ComparisonService(session).compare(ref_cat.id, tgt_cat.id)

        s = result["comparisons"][0]["summary"]
        assert s["matched"] == 0
        assert s["only_in_reference"] == 1
        assert s["only_in_target"] == 1

    def test_matching_products_appear_in_matches(self):
        with _session_scope() as session:
            ref_store, tgt_store, ref_cat, tgt_cat = _make_mapped_categories(session)
            _add_product(session, ref_store.id, ref_cat.id, "Bauer Vapor X5 SR", 4500, "ref-bv-hm")
            _add_product(session, tgt_store.id, tgt_cat.id, "Bauer Vapor X5 Senior", 4800, "tgt-bv-hm")
            session.flush()
            result = ComparisonService(session).compare(ref_cat.id, tgt_cat.id)

        assert result["comparisons"][0]["summary"]["matched"] >= 1

    def test_match_has_reference_and_target_product(self):
        with _session_scope() as session:
            ref_store, tgt_store, ref_cat, tgt_cat = _make_mapped_categories(session)
            _add_product(session, ref_store.id, ref_cat.id, "Bauer Vapor X5 SR", 4500, "ref-bv2-hm")
            _add_product(session, tgt_store.id, tgt_cat.id, "Bauer Vapor X5 Senior", 4800, "tgt-bv2-hm")
            session.flush()
            result = ComparisonService(session).compare(ref_cat.id, tgt_cat.id)

        matches = result["comparisons"][0]["matches"]
        if matches:
            m = matches[0]
            assert m["reference_product"] is not None
            assert m["target_product"] is not None
            assert m["match_source"] == "heuristic"
            assert "score" in m


# ---------------------------------------------------------------------------
# ComparisonService – stored product mappings
# ---------------------------------------------------------------------------

class TestComparisonServiceStoredMappings:
    def test_stored_mapping_appears_as_stored_match(self):
        with _session_scope() as session:
            ref_store, tgt_store, ref_cat, tgt_cat = _make_mapped_categories(session)
            ref_prod = _add_product(session, ref_store.id, ref_cat.id, "Bauer Supreme M4 SR", 3900, "ref-sm-map")
            tgt_prod = _add_product(session, tgt_store.id, tgt_cat.id, "Bauer Supreme M4 Senior", 4100, "tgt-sm-map")
            session.flush()
            create_product_mapping(
                session,
                reference_product_id=ref_prod.id,
                target_product_id=tgt_prod.id,
                match_status="confirmed",
                confidence=1.0,
            )
            session.flush()
            result = ComparisonService(session).compare(ref_cat.id, tgt_cat.id)

        matches = result["comparisons"][0]["matches"]
        stored = [m for m in matches if m["match_source"] == "stored"]
        assert len(stored) >= 1
        assert stored[0]["reference_product"]["id"] == ref_prod.id
        assert stored[0]["target_product"]["id"] == tgt_prod.id
        assert stored[0]["score"] == 1.0

    def test_stored_match_products_not_passed_to_heuristic(self):
        with _session_scope() as session:
            ref_store, tgt_store, ref_cat, tgt_cat = _make_mapped_categories(session)
            ref_prod = _add_product(session, ref_store.id, ref_cat.id, "CCM Tacks 9380 SR", 3500, "ref-ct-map")
            tgt_prod = _add_product(session, tgt_store.id, tgt_cat.id, "CCM Tacks 9380 Senior", 3700, "tgt-ct-map")
            session.flush()
            create_product_mapping(
                session,
                reference_product_id=ref_prod.id,
                target_product_id=tgt_prod.id,
                match_status="confirmed",
                confidence=1.0,
            )
            session.flush()
            result = ComparisonService(session).compare(ref_cat.id, tgt_cat.id)

        comp = result["comparisons"][0]
        ref_ids_unmatched = [item["reference_product"]["id"] for item in comp["only_in_reference"]]
        tgt_ids_unmatched = [item["target_product"]["id"] for item in comp["only_in_target"]]
        assert ref_prod.id not in ref_ids_unmatched
        assert tgt_prod.id not in tgt_ids_unmatched


# ---------------------------------------------------------------------------
# Many-to-many: one ref category mapped to multiple target categories
# ---------------------------------------------------------------------------

class TestComparisonOneToMany:
    def test_compare_all_mapped_returns_multiple_comparisons(self):
        with _session_scope() as session:
            ref_store = get_or_create_store(session, "RefM2M", is_reference=True)
            tgt_store_a = get_or_create_store(session, "TgtM2M_A", is_reference=False)
            tgt_store_b = get_or_create_store(session, "TgtM2M_B", is_reference=False)
            ref_cat = upsert_category(session, store_id=ref_store.id, name="Pads-m2m")
            tgt_cat_a = upsert_category(session, store_id=tgt_store_a.id, name="Pads-tgt-a")
            tgt_cat_b = upsert_category(session, store_id=tgt_store_b.id, name="Pads-tgt-b")
            create_category_mapping(session, reference_category_id=ref_cat.id,
                                    target_category_id=tgt_cat_a.id, match_type="manual")
            create_category_mapping(session, reference_category_id=ref_cat.id,
                                    target_category_id=tgt_cat_b.id, match_type="manual")
            session.flush()

            result = ComparisonService(session).compare(reference_category_id=ref_cat.id)

        assert len(result["comparisons"]) == 2
        assert len(result["mapped_target_categories"]) == 2
        tgt_ids = {c["target_category"]["id"] for c in result["comparisons"]}
        assert tgt_cat_a.id in tgt_ids
        assert tgt_cat_b.id in tgt_ids


# ---------------------------------------------------------------------------
# Flask integration tests — /api/comparison contract
# ---------------------------------------------------------------------------

class TestApiComparisonContract:
    """Test /api/comparison via Flask test client using monkeypatching."""

    def _make_result(self):
        return {
            "reference_category": {"id": 1, "name": "Skates", "store_id": 1,
                                    "store_name": "Ref", "is_reference": True,
                                    "normalized_name": "skates", "url": None},
            "mapped_target_categories": [
                {"target_category_id": 2, "name": "Skates", "normalized_name": "skates",
                 "match_type": "manual", "confidence": 1.0}
            ],
            "comparisons": [
                {
                    "target_category": {"id": 2, "name": "Skates", "store_id": 2,
                                        "store_name": "Tgt", "is_reference": False,
                                        "normalized_name": "skates", "url": None},
                    "summary": {
                        "reference_total": 2, "target_total": 2,
                        "matched": 1, "only_in_reference": 1,
                        "only_in_target": 1, "ambiguous": 0,
                    },
                    "matches": [
                        {"reference_product": {"id": 10, "name": "P1"},
                         "target_product": {"id": 20, "name": "P2"},
                         "score": 95.0, "gap": 10.0, "color": "none",
                         "match_source": "heuristic"}
                    ],
                    "ambiguous": [],
                    "only_in_reference": [{"reference_product": {"id": 11, "name": "P3"}}],
                    "only_in_target": [{"target_product": {"id": 21, "name": "P4"}}],
                }
            ],
        }

    def test_returns_200_with_structured_response(self, monkeypatch):
        from app import app as flask_app
        from pricewatch.services.comparison_service import ComparisonService

        result = self._make_result()
        monkeypatch.setattr(ComparisonService, "compare", lambda self, **kw: result)

        resp = flask_app.test_client().post(
            "/api/comparison",
            json={"reference_category_id": 1, "target_category_id": 2},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "reference_category" in data
        assert "mapped_target_categories" in data
        assert "comparisons" in data
        assert isinstance(data["comparisons"], list)

    def test_returns_400_when_missing_reference_id(self):
        from app import app as flask_app
        resp = flask_app.test_client().post("/api/comparison", json={})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_target_category_id_is_optional(self, monkeypatch):
        """Sending only reference_category_id must not raise 400 at the Flask layer."""
        from app import app as flask_app
        from pricewatch.services.comparison_service import ComparisonService

        result = self._make_result()
        monkeypatch.setattr(ComparisonService, "compare", lambda self, **kw: result)

        resp = flask_app.test_client().post(
            "/api/comparison",
            json={"reference_category_id": 1},
        )
        assert resp.status_code == 200

    def test_returns_400_for_non_json(self):
        from app import app as flask_app
        resp = flask_app.test_client().post("/api/comparison", data="not-json",
                                            content_type="text/plain")
        assert resp.status_code == 400

    def test_returns_400_on_value_error(self, monkeypatch):
        from app import app as flask_app
        from pricewatch.services.comparison_service import ComparisonService

        monkeypatch.setattr(ComparisonService, "compare",
                            lambda self, **kw: (_ for _ in ()).throw(ValueError("Category 999 not found")))

        resp = flask_app.test_client().post(
            "/api/comparison",
            json={"reference_category_id": 999, "target_category_id": 888},
        )
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_returns_400_when_no_mapping_exists(self, monkeypatch):
        from app import app as flask_app
        from pricewatch.services.comparison_service import ComparisonService

        def raise_no_mapping(self, **kw):
            raise ValueError("Для цієї категорії ще не створено меппінг")

        monkeypatch.setattr(ComparisonService, "compare", raise_no_mapping)
        resp = flask_app.test_client().post(
            "/api/comparison",
            json={"reference_category_id": 1},
        )
        assert resp.status_code == 400
        assert "меппінг" in resp.get_json()["error"]

    def test_comparisons_list_in_response(self, monkeypatch):
        from app import app as flask_app
        from pricewatch.services.comparison_service import ComparisonService

        result = self._make_result()
        monkeypatch.setattr(ComparisonService, "compare", lambda self, **kw: result)

        data = flask_app.test_client().post(
            "/api/comparison",
            json={"reference_category_id": 1, "target_category_id": 2},
        ).get_json()

        comp = data["comparisons"][0]
        summary = comp["summary"]
        for key in ("reference_total", "target_total", "matched",
                    "only_in_reference", "only_in_target", "ambiguous"):
            assert key in summary, f"missing summary key: {key}"

    def test_does_not_return_old_top_level_keys(self, monkeypatch):
        """Old shape had top-level target_category/summary/matches — must be gone."""
        from app import app as flask_app
        from pricewatch.services.comparison_service import ComparisonService

        result = self._make_result()
        monkeypatch.setattr(ComparisonService, "compare", lambda self, **kw: result)

        data = flask_app.test_client().post(
            "/api/comparison",
            json={"reference_category_id": 1, "target_category_id": 2},
        ).get_json()

        for old_key in ("target_category", "summary", "matches",
                        "only_in_reference", "only_in_target",
                        "missing", "total_urls", "scanned"):
            assert old_key not in data, f"old top-level key still present: {old_key}"


# ---------------------------------------------------------------------------
# Flask integration tests — /api/comparison/confirm-match
# ---------------------------------------------------------------------------

class TestApiConfirmMatch:
    def _make_pm(self):
        return SimpleNamespace(
            id=1,
            reference_product_id=10,
            target_product_id=20,
            reference_product=None,
            target_product=None,
            match_status="confirmed",
            confidence=None,
            comment=None,
            updated_at=datetime.now(timezone.utc),
        )

    def test_returns_200_with_product_mapping_key(self, monkeypatch):
        from app import app as flask_app
        import app as app_module

        pm = self._make_pm()
        monkeypatch.setattr(app_module, "create_product_mapping", lambda session, **kw: pm)

        resp = flask_app.test_client().post(
            "/api/comparison/confirm-match",
            json={"reference_product_id": 10, "target_product_id": 20},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "product_mapping" in data
        assert data["product_mapping"]["reference_product_id"] == 10
        assert data["product_mapping"]["target_product_id"] == 20

    def test_returns_400_when_ids_missing(self):
        from app import app as flask_app
        resp = flask_app.test_client().post("/api/comparison/confirm-match", json={})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_returns_400_on_exception(self, monkeypatch):
        from app import app as flask_app
        import app as app_module

        monkeypatch.setattr(app_module, "create_product_mapping",
                            lambda session, **kw: (_ for _ in ()).throw(ValueError("integrity error")))
        resp = flask_app.test_client().post(
            "/api/comparison/confirm-match",
            json={"reference_product_id": 10, "target_product_id": 20},
        )
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_confirm_match_route_precedes_comparison_route(self):
        """POST /api/comparison/confirm-match must be reachable (not shadowed by /api/comparison)."""
        from app import app as flask_app
        resp = flask_app.test_client().post(
            "/api/comparison/confirm-match",
            json={},
        )
        assert resp.status_code in (200, 400)
