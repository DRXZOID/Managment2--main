"""Tests for the DB-first ComparisonService and /api/comparison endpoint.

Covers:
  - Valid DB-backed comparison between two categories
  - Rejection when reference category belongs to a non-reference store
  - Rejection when target category belongs to a reference store
  - Stored ProductMapping rows are used first (stored matches bypass heuristic)
  - Heuristic fallback when no ProductMapping rows exist
  - Stable response shape from POST /api/comparison via Flask test client
  - POST /api/comparison/confirm-match creates a ProductMapping row
"""
from __future__ import annotations

from types import SimpleNamespace
from datetime import datetime, timezone

import pytest

from pricewatch.db.testing import test_session_scope as _session_scope
from pricewatch.db.repositories.store_repository import get_or_create_store
from pricewatch.db.repositories.category_repository import upsert_category
from pricewatch.db.repositories.product_repository import upsert_product
from pricewatch.db.repositories.mapping_repository import create_product_mapping
from pricewatch.services.comparison_service import ComparisonService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_stores_and_categories(session):
    """Create a reference store + category and a target store + category."""
    ref_store = get_or_create_store(session, "RefStore", is_reference=True, base_url="https://ref.example.com")
    tgt_store = get_or_create_store(session, "TgtStore", is_reference=False, base_url="https://tgt.example.com")

    ref_cat = upsert_category(session, store_id=ref_store.id, name="Skates", url="https://ref.example.com/skates")
    tgt_cat = upsert_category(session, store_id=tgt_store.id, name="Skates", url="https://tgt.example.com/skates")

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
# ComparisonService – unit tests (in-memory SQLite)
# ---------------------------------------------------------------------------

class TestComparisonServiceValidation:
    def test_raises_if_reference_category_not_found(self):
        with _session_scope() as session:
            _, _, _, tgt_cat = _make_stores_and_categories(session)
            svc = ComparisonService(session)
            with pytest.raises(ValueError, match="not found"):
                svc.compare(reference_category_id=99999, target_category_id=tgt_cat.id)

    def test_raises_if_target_category_not_found(self):
        with _session_scope() as session:
            _, _, ref_cat, _ = _make_stores_and_categories(session)
            svc = ComparisonService(session)
            with pytest.raises(ValueError, match="not found"):
                svc.compare(reference_category_id=ref_cat.id, target_category_id=99999)

    def test_raises_when_reference_category_belongs_to_non_reference_store(self):
        with _session_scope() as session:
            _, tgt_store, _, tgt_cat = _make_stores_and_categories(session)
            svc = ComparisonService(session)
            with pytest.raises(ValueError, match="reference store"):
                svc.compare(reference_category_id=tgt_cat.id, target_category_id=tgt_cat.id)

    def test_raises_when_target_category_belongs_to_reference_store(self):
        with _session_scope() as session:
            _, _, ref_cat, _ = _make_stores_and_categories(session)
            svc = ComparisonService(session)
            with pytest.raises(ValueError, match="reference store"):
                svc.compare(reference_category_id=ref_cat.id, target_category_id=ref_cat.id)

    def test_raises_when_same_store_for_both(self):
        with _session_scope() as session:
            ref_store = get_or_create_store(session, "OnlyRef", is_reference=True)
            cat_a = upsert_category(session, store_id=ref_store.id, name="CatA")
            cat_b = upsert_category(session, store_id=ref_store.id, name="CatB")
            session.flush()
            svc = ComparisonService(session)
            with pytest.raises(ValueError):
                svc.compare(reference_category_id=cat_a.id, target_category_id=cat_b.id)


class TestComparisonServiceResponseShape:
    def test_returns_all_required_keys(self):
        with _session_scope() as session:
            _, _, ref_cat, tgt_cat = _make_stores_and_categories(session)
            result = ComparisonService(session).compare(ref_cat.id, tgt_cat.id)

        assert "reference_category" in result
        assert "target_category" in result
        assert "summary" in result
        assert "matches" in result
        assert "ambiguous" in result
        assert "only_in_reference" in result
        assert "only_in_target" in result

    def test_summary_keys_present(self):
        with _session_scope() as session:
            _, _, ref_cat, tgt_cat = _make_stores_and_categories(session)
            result = ComparisonService(session).compare(ref_cat.id, tgt_cat.id)

        summary = result["summary"]
        for key in ("reference_total", "target_total", "matched", "only_in_reference",
                    "only_in_target", "ambiguous"):
            assert key in summary, f"missing summary key: {key}"

    def test_empty_categories_give_zero_totals(self):
        with _session_scope() as session:
            _, _, ref_cat, tgt_cat = _make_stores_and_categories(session)
            result = ComparisonService(session).compare(ref_cat.id, tgt_cat.id)

        s = result["summary"]
        assert s["reference_total"] == 0
        assert s["target_total"] == 0
        assert s["matched"] == 0

    def test_category_info_in_result(self):
        with _session_scope() as session:
            _, _, ref_cat, tgt_cat = _make_stores_and_categories(session)
            result = ComparisonService(session).compare(ref_cat.id, tgt_cat.id)

        assert result["reference_category"]["name"] == "Skates"
        assert result["target_category"]["name"] == "Skates"
        assert result["reference_category"]["is_reference"] is True
        assert result["target_category"]["is_reference"] is False


class TestComparisonServiceHeuristicMatching:
    def test_unmatched_products_end_up_in_only_in_reference_or_target(self):
        with _session_scope() as session:
            ref_store, tgt_store, ref_cat, tgt_cat = _make_stores_and_categories(session)
            _add_product(session, ref_store.id, ref_cat.id, "Bauer Vapor X5 SR", 4500, "ref-1")
            _add_product(session, tgt_store.id, tgt_cat.id, "CCM Tacks AS-V SR", 5200, "tgt-1")
            session.flush()
            result = ComparisonService(session).compare(ref_cat.id, tgt_cat.id)

        s = result["summary"]
        # Different brands → hard brand block → no match expected
        assert s["matched"] == 0
        assert s["only_in_reference"] == 1
        assert s["only_in_target"] == 1

    def test_matching_products_appear_in_matches(self):
        with _session_scope() as session:
            ref_store, tgt_store, ref_cat, tgt_cat = _make_stores_and_categories(session)
            _add_product(session, ref_store.id, ref_cat.id, "Bauer Vapor X5 SR", 4500, "ref-bv")
            _add_product(session, tgt_store.id, tgt_cat.id, "Bauer Vapor X5 Senior", 4800, "tgt-bv")
            session.flush()
            result = ComparisonService(session).compare(ref_cat.id, tgt_cat.id)

        s = result["summary"]
        assert s["matched"] >= 1

    def test_match_has_reference_and_target_product(self):
        with _session_scope() as session:
            ref_store, tgt_store, ref_cat, tgt_cat = _make_stores_and_categories(session)
            _add_product(session, ref_store.id, ref_cat.id, "Bauer Vapor X5 SR", 4500, "ref-bv2")
            _add_product(session, tgt_store.id, tgt_cat.id, "Bauer Vapor X5 Senior", 4800, "tgt-bv2")
            session.flush()
            result = ComparisonService(session).compare(ref_cat.id, tgt_cat.id)

        if result["matches"]:
            m = result["matches"][0]
            assert m["reference_product"] is not None
            assert m["target_product"] is not None
            assert m["match_source"] == "heuristic"
            assert "score" in m


class TestComparisonServiceStoredMappings:
    def test_stored_mapping_appears_as_stored_match(self):
        with _session_scope() as session:
            ref_store, tgt_store, ref_cat, tgt_cat = _make_stores_and_categories(session)
            ref_prod = _add_product(session, ref_store.id, ref_cat.id, "Bauer Supreme M4 SR", 3900, "ref-sm")
            tgt_prod = _add_product(session, tgt_store.id, tgt_cat.id, "Bauer Supreme M4 Senior", 4100, "tgt-sm")
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

        stored = [m for m in result["matches"] if m["match_source"] == "stored"]
        assert len(stored) >= 1
        stored_match = stored[0]
        assert stored_match["reference_product"]["id"] == ref_prod.id
        assert stored_match["target_product"]["id"] == tgt_prod.id
        assert stored_match["score"] == 1.0

    def test_stored_match_products_not_passed_to_heuristic(self):
        """Products covered by stored mappings must not appear in only_in_reference/target."""
        with _session_scope() as session:
            ref_store, tgt_store, ref_cat, tgt_cat = _make_stores_and_categories(session)
            ref_prod = _add_product(session, ref_store.id, ref_cat.id, "CCM Tacks 9380 SR", 3500, "ref-ct")
            tgt_prod = _add_product(session, tgt_store.id, tgt_cat.id, "CCM Tacks 9380 Senior", 3700, "tgt-ct")
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

        ref_ids_unmatched = [
            item["reference_product"]["id"]
            for item in result["only_in_reference"]
        ]
        tgt_ids_unmatched = [
            item["target_product"]["id"]
            for item in result["only_in_target"]
        ]
        assert ref_prod.id not in ref_ids_unmatched
        assert tgt_prod.id not in tgt_ids_unmatched


# ---------------------------------------------------------------------------
# Flask integration tests — /api/comparison contract
# ---------------------------------------------------------------------------

class TestApiComparisonContract:
    """Test /api/comparison via Flask test client using monkeypatching."""

    def _make_result(self):
        return {
            "reference_category": {"id": 1, "name": "Skates", "store_id": 1, "store_name": "Ref",
                                    "is_reference": True, "normalized_name": "skates", "url": None},
            "target_category": {"id": 2, "name": "Skates", "store_id": 2, "store_name": "Tgt",
                                 "is_reference": False, "normalized_name": "skates", "url": None},
            "summary": {
                "reference_total": 2, "target_total": 2,
                "matched": 1, "only_in_reference": 1, "only_in_target": 1, "ambiguous": 0,
            },
            "matches": [{"reference_product": {"id": 10, "name": "P1"}, "target_product": {"id": 20, "name": "P2"},
                         "score": 95.0, "gap": 10.0, "color": "none", "match_source": "heuristic"}],
            "ambiguous": [],
            "only_in_reference": [{"reference_product": {"id": 11, "name": "P3"}}],
            "only_in_target": [{"target_product": {"id": 21, "name": "P4"}}],
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
        for key in ("reference_category", "target_category", "summary",
                    "matches", "ambiguous", "only_in_reference", "only_in_target"):
            assert key in data, f"missing key: {key}"

    def test_returns_400_when_missing_params(self):
        from app import app as flask_app
        resp = flask_app.test_client().post("/api/comparison", json={})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_returns_400_for_non_json(self):
        from app import app as flask_app
        resp = flask_app.test_client().post("/api/comparison", data="not-json",
                                            content_type="text/plain")
        assert resp.status_code == 400

    def test_returns_400_on_value_error(self, monkeypatch):
        from app import app as flask_app
        from pricewatch.services.comparison_service import ComparisonService

        def fail(self, **kw):
            raise ValueError("Category 999 not found")

        monkeypatch.setattr(ComparisonService, "compare", fail)
        resp = flask_app.test_client().post(
            "/api/comparison",
            json={"reference_category_id": 999, "target_category_id": 888},
        )
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_summary_keys_present_in_response(self, monkeypatch):
        from app import app as flask_app
        from pricewatch.services.comparison_service import ComparisonService

        result = self._make_result()
        monkeypatch.setattr(ComparisonService, "compare", lambda self, **kw: result)

        data = flask_app.test_client().post(
            "/api/comparison",
            json={"reference_category_id": 1, "target_category_id": 2},
        ).get_json()

        summary = data["summary"]
        for key in ("reference_total", "target_total", "matched",
                    "only_in_reference", "only_in_target", "ambiguous"):
            assert key in summary, f"missing summary key: {key}"

    def test_does_not_return_old_missing_shape(self, monkeypatch):
        """Old /api/comparison returned {missing, total, total_urls, scanned} — must be gone."""
        from app import app as flask_app
        from pricewatch.services.comparison_service import ComparisonService

        result = self._make_result()
        monkeypatch.setattr(ComparisonService, "compare", lambda self, **kw: result)

        data = flask_app.test_client().post(
            "/api/comparison",
            json={"reference_category_id": 1, "target_category_id": 2},
        ).get_json()

        for old_key in ("missing", "total_urls", "scanned"):
            assert old_key not in data, f"old key still present: {old_key}"


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

        def fail(session, **kw):
            raise ValueError("integrity error")

        monkeypatch.setattr(app_module, "create_product_mapping", fail)
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
        assert resp.status_code in (200, 400), (
            f"Expected 200/400 from confirm-match, got {resp.status_code}"
        )
