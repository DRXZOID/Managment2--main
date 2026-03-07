"""DB-first comparison service.

Compares persisted products from two categories (reference vs target) without
performing any live scraping.  Matching priority:

1. Stored ``ProductMapping`` rows (created via /api/comparison/confirm-match or
   the service admin UI) are used first for the covered product pairs.
2. Remaining unmapped products are matched heuristically via
   ``heuristic_match`` from ``pricewatch.core.normalize``.

The service is intentionally free of Flask and HTTP concerns – it only works
with a SQLAlchemy session and returns plain Python dicts.
"""
from __future__ import annotations

from typing import Any

from pricewatch.db.models import Category, Product
from pricewatch.db.repositories.category_repository import get_category
from pricewatch.db.repositories.product_repository import list_products_by_category
from pricewatch.db.repositories.mapping_repository import list_matches_for_reference_product
from pricewatch.core.normalize import heuristic_match


def _serialize_product(prod: Product) -> dict[str, Any]:
    """Return a compact serialisable dict for a DB Product row."""
    return {
        "id": prod.id,
        "store_id": prod.store_id,
        "category_id": prod.category_id,
        "name": prod.name,
        "normalized_name": prod.normalized_name,
        "name_hash": prod.name_hash,
        "price": prod.price,
        "currency": prod.currency,
        "product_url": prod.product_url,
        "source_url": prod.source_url,
        "is_available": prod.is_available,
        "scraped_at": prod.scraped_at.isoformat() if prod.scraped_at else None,
        "updated_at": prod.updated_at.isoformat() if prod.updated_at else None,
    }


def _serialize_category(cat: Category) -> dict[str, Any]:
    store = getattr(cat, "store", None)
    return {
        "id": cat.id,
        "store_id": cat.store_id,
        "name": cat.name,
        "normalized_name": cat.normalized_name,
        "url": cat.url,
        "store_name": getattr(store, "name", None),
        "is_reference": getattr(store, "is_reference", None),
    }


def _product_to_item(prod: Product) -> dict[str, Any]:
    """Convert a DB Product to the dict shape expected by heuristic_match."""
    price_str = f"{prod.price or ''} {prod.currency or ''}".strip()
    return {
        # keys used by heuristic_match internals
        "name": prod.name,
        "price_raw": price_str,
        "url": prod.product_url,
        # extra fields preserved verbatim in _raw so the service can re-attach
        # the DB id after matching
        "_db_id": prod.id,
    }


class ComparisonService:
    """Compare products from two DB-backed categories.

    Usage::

        svc = ComparisonService(session)
        result = svc.compare(reference_category_id=1, target_category_id=2)
    """

    def __init__(self, session) -> None:
        self.session = session

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compare(
        self,
        reference_category_id: int,
        target_category_id: int,
    ) -> dict[str, Any]:
        """Run a full DB-first comparison and return a structured result dict.

        Raises ``ValueError`` for invalid inputs (missing category, wrong store
        role, same store for both categories).

        Response shape::

            {
              "reference_category": {...},
              "target_category": {...},
              "summary": {
                "reference_total": int,
                "target_total": int,
                "matched": int,
                "only_in_reference": int,
                "only_in_target": int,
                "ambiguous": int,
              },
              "matches": [
                {
                  "reference_product": {...},
                  "target_product": {...},
                  "score": float,
                  "gap": float,
                  "color": str,
                  "match_source": "stored" | "heuristic",
                }
              ],
              "ambiguous": [
                {
                  "reference_product": {...} | None,
                  "target_product": {...} | None,
                  "score": float,
                  "gap": float,
                  "color": str,
                  "candidates": [...],   # only when reference_product is set
                }
              ],
              "only_in_reference": [{"reference_product": {...}}],
              "only_in_target":    [{"target_product": {...}}],
            }
        """
        ref_cat, tgt_cat = self._load_and_validate_categories(
            reference_category_id, target_category_id
        )

        ref_products = list_products_by_category(self.session, reference_category_id)
        tgt_products = list_products_by_category(self.session, target_category_id)

        # Build id→product maps for quick look-up after matching
        ref_by_id: dict[int, Product] = {p.id: p for p in ref_products}
        tgt_by_id: dict[int, Product] = {p.id: p for p in tgt_products}

        # --- Phase 1: apply stored ProductMapping rows ---
        stored_matches: list[dict[str, Any]] = []
        ref_ids_covered: set[int] = set()
        tgt_ids_covered: set[int] = set()

        for ref_prod in ref_products:
            saved = list_matches_for_reference_product(self.session, ref_prod.id)
            for pm in saved:
                tgt_id = pm.target_product_id
                if tgt_id not in tgt_by_id:
                    # mapping points outside this target category – skip
                    continue
                if tgt_id in tgt_ids_covered:
                    continue
                ref_ids_covered.add(ref_prod.id)
                tgt_ids_covered.add(tgt_id)
                stored_matches.append({
                    "reference_product": _serialize_product(ref_prod),
                    "target_product": _serialize_product(tgt_by_id[tgt_id]),
                    "score": pm.confidence if pm.confidence is not None else 1.0,
                    "gap": None,
                    "color": "none",
                    "match_source": "stored",
                })

        # --- Phase 2: heuristic matching for remaining products ---
        remaining_ref = [p for p in ref_products if p.id not in ref_ids_covered]
        remaining_tgt = [p for p in tgt_products if p.id not in tgt_ids_covered]

        ref_items = [_product_to_item(p) for p in remaining_ref]
        tgt_items = [_product_to_item(p) for p in remaining_tgt]

        heuristic_results = heuristic_match(ref_items, tgt_items) if (ref_items or tgt_items) else []

        # --- Phase 3: classify heuristic results into the four groups ---
        heuristic_matches: list[dict[str, Any]] = []
        ambiguous: list[dict[str, Any]] = []
        only_in_reference: list[dict[str, Any]] = []
        only_in_target: list[dict[str, Any]] = []

        for row in heuristic_results:
            status = row["status"]
            raw_main = row.get("main")
            raw_other = row.get("other")

            ref_prod_dict = self._enrich_from_db(raw_main, ref_by_id) if raw_main else None
            tgt_prod_dict = self._enrich_from_db(raw_other, tgt_by_id) if raw_other else None

            if status == "matched":
                heuristic_matches.append({
                    "reference_product": ref_prod_dict,
                    "target_product": tgt_prod_dict,
                    "score": row.get("score"),
                    "gap": row.get("gap"),
                    "color": row.get("color", "none"),
                    "match_source": "heuristic",
                })
            elif status == "ambiguous":
                candidates = row.get("candidates")
                entry: dict[str, Any] = {
                    "reference_product": ref_prod_dict,
                    "target_product": tgt_prod_dict,
                    "score": row.get("score"),
                    "gap": row.get("gap"),
                    "color": row.get("color", "blue"),
                    "match_source": "heuristic",
                }
                if candidates is not None:
                    entry["candidates"] = candidates
                ambiguous.append(entry)
            else:
                # no_match — classify by which side is present
                if raw_main is not None and raw_other is None:
                    only_in_reference.append({"reference_product": ref_prod_dict})
                elif raw_other is not None and raw_main is None:
                    only_in_target.append({"target_product": tgt_prod_dict})

        all_matches = stored_matches + heuristic_matches

        return {
            "reference_category": _serialize_category(ref_cat),
            "target_category": _serialize_category(tgt_cat),
            "summary": {
                "reference_total": len(ref_products),
                "target_total": len(tgt_products),
                "matched": len(all_matches),
                "only_in_reference": len(only_in_reference),
                "only_in_target": len(only_in_target),
                "ambiguous": len(ambiguous),
            },
            "matches": all_matches,
            "ambiguous": ambiguous,
            "only_in_reference": only_in_reference,
            "only_in_target": only_in_target,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_and_validate_categories(
        self,
        reference_category_id: int,
        target_category_id: int,
    ) -> tuple[Category, Category]:
        ref_cat = get_category(self.session, reference_category_id)
        if ref_cat is None:
            raise ValueError(f"Category {reference_category_id} not found")

        tgt_cat = get_category(self.session, target_category_id)
        if tgt_cat is None:
            raise ValueError(f"Category {target_category_id} not found")

        ref_store = getattr(ref_cat, "store", None)
        tgt_store = getattr(tgt_cat, "store", None)

        if not getattr(ref_store, "is_reference", False):
            raise ValueError(
                f"Category {reference_category_id} does not belong to a reference store "
                f"(store '{getattr(ref_store, 'name', ref_cat.store_id)}' is not marked as reference)"
            )
        if getattr(tgt_store, "is_reference", False):
            raise ValueError(
                f"Category {target_category_id} belongs to a reference store; "
                "target_category_id must belong to a non-reference store"
            )
        if ref_cat.store_id == tgt_cat.store_id:
            raise ValueError(
                "reference_category_id and target_category_id must belong to different stores"
            )

        return ref_cat, tgt_cat

    @staticmethod
    def _enrich_from_db(
        raw_item: dict[str, Any] | None,
        id_map: dict[int, Product],
    ) -> dict[str, Any] | None:
        """Return the full serialised product for the raw heuristic item.

        ``_product_to_item`` stores ``_db_id`` in the raw dict so we can look
        up the original DB row and return all its fields.
        """
        if raw_item is None:
            return None
        db_id = raw_item.get("_db_id")
        if db_id is not None and db_id in id_map:
            return _serialize_product(id_map[db_id])
        # fallback: return the raw item as-is (should not happen in normal flow)
        return raw_item

