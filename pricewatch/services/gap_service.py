"""Gap review service.

Builds the assortment-gap view for content managers on the /gap page.

Business rules
--------------
* A "gap item" is a target-only product: present in a target store/category
  but absent from the reference category (not used in any confirmed match and
  not appearing in any candidate list).
* The definition of "target_only" is fully delegated to ComparisonService —
  this service does NOT re-implement that logic.
* Gap review statuses:
    - ``new``         – implicit (no DB row)
    - ``in_progress`` – persisted
    - ``done``        – persisted
* Default visible statuses: ``new`` + ``in_progress``
* ``done`` items are always counted in summary even when filtered out.
"""
from __future__ import annotations

from typing import Any

from pricewatch.db.repositories.category_repository import get_category
from pricewatch.db.repositories.gap_repository import (
    bulk_get_gap_statuses,
    upsert_gap_status,
    ALLOWED_STATUSES,
)
from pricewatch.services.comparison_service import ComparisonService

_DEFAULT_STATUSES = ("new", "in_progress")


class GapService:
    """Orchestrate gap-view building and status persistence."""

    def __init__(self, session) -> None:
        self.session = session

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_gap_view(
        self,
        target_store_id: int,
        reference_category_id: int,
        target_category_ids: list[int],
        *,
        search: str | None = None,
        only_available: bool | None = None,
        statuses: list[str] | None = None,
    ) -> dict[str, Any]:
        """Build the full gap view payload.

        Parameters
        ----------
        target_store_id:
            Non-reference store to review.
        reference_category_id:
            Reference category that defines the assortment baseline.
        target_category_ids:
            Mapped target categories to include.  Must all be mapped to
            *reference_category_id*; validated by ComparisonService.
        search:
            Optional substring filter on target product name (case-insensitive).
        only_available:
            When ``True`` keep only products with ``is_available == True``.
        statuses:
            Visibility filter; defaults to ``['new', 'in_progress']``.
            ``done`` items are always counted in summary even if not listed.

        Returns
        -------
        dict
            Matches the shape documented in the API spec.
        """
        if statuses is None:
            statuses = list(_DEFAULT_STATUSES)

        # 1. Validate context: store & reference category must exist
        ref_cat = get_category(self.session, reference_category_id)
        if ref_cat is None:
            raise ValueError(f"Reference category {reference_category_id} not found")

        # 2. Validate that all target_category_ids are mapped to reference_category_id
        #    within the given target_store_id.  ComparisonService does this validation
        #    for us and raises ValueError on failure.
        comparison_result = ComparisonService(self.session).compare(
            reference_category_id=reference_category_id,
            target_category_ids=target_category_ids,
            target_store_id=target_store_id,
        )

        # 3. Extract target_only items
        raw_target_only: list[dict[str, Any]] = comparison_result.get("target_only", [])

        # 4. Collect all target product IDs and bulk-fetch persisted statuses
        all_tgt_ids = [
            item["target_product"]["id"]
            for item in raw_target_only
            if item.get("target_product") and item["target_product"].get("id")
        ]
        persisted_statuses = bulk_get_gap_statuses(
            self.session, reference_category_id, all_tgt_ids
        )

        # 5. Enrich each item with its status
        enriched: list[dict[str, Any]] = []
        for item in raw_target_only:
            tgt_prod = item.get("target_product") or {}
            tgt_id = tgt_prod.get("id")
            status = persisted_statuses.get(tgt_id, "new") if tgt_id else "new"
            enriched.append(
                {
                    "target_product": tgt_prod,
                    "target_category": item.get("target_category"),
                    "status": status,
                }
            )

        # 6. Build summary BEFORE applying visibility filters (done must be counted)
        summary = self._build_summary(enriched)

        # 7. Apply filters: only_available, search
        filtered = enriched
        if only_available:
            filtered = [
                i for i in filtered if i["target_product"].get("is_available")
            ]
        if search:
            q = search.strip().lower()
            filtered = [
                i
                for i in filtered
                if q in (i["target_product"].get("name") or "").lower()
            ]

        # 8. Apply status visibility filter
        status_set = set(statuses) if statuses else set(_DEFAULT_STATUSES)
        visible = [i for i in filtered if i["status"] in status_set]

        # 9. Group by target_category
        groups = self._group_by_category(visible)

        # 10. Build metadata from comparison result
        ref_cat_meta = comparison_result.get("reference_category") or {
            "id": reference_category_id,
            "name": getattr(ref_cat, "name", None),
        }
        target_store_meta = comparison_result.get("target_store")
        selected_cats = comparison_result.get("selected_target_categories", [])

        return {
            "reference_category": ref_cat_meta,
            "target_store": target_store_meta,
            "selected_target_categories": selected_cats,
            "summary": summary,
            "groups": groups,
        }

    def set_gap_item_status(
        self,
        reference_category_id: int,
        target_product_id: int,
        status: str,
    ) -> dict[str, Any]:
        """Persist a gap item status and return minimal updated metadata.

        Raises ``ValueError`` for disallowed status values.
        """
        if status not in ALLOWED_STATUSES:
            raise ValueError(
                f"Invalid gap status '{status}'. Allowed: {sorted(ALLOWED_STATUSES)}"
            )
        row = upsert_gap_status(
            self.session,
            reference_category_id=reference_category_id,
            target_product_id=target_product_id,
            status=status,
        )
        return {
            "reference_category_id": row.reference_category_id,
            "target_product_id": row.target_product_id,
            "status": row.status,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_summary(enriched: list[dict[str, Any]]) -> dict[str, int]:
        total = len(enriched)
        in_progress = sum(1 for i in enriched if i["status"] == "in_progress")
        done = sum(1 for i in enriched if i["status"] == "done")
        new = total - in_progress - done
        return {
            "total": total,
            "new": new,
            "in_progress": in_progress,
            "done": done,
        }

    @staticmethod
    def _group_by_category(
        items: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Group enriched items by target_category, preserving insertion order."""
        order: list[int | None] = []
        groups: dict[int | None, dict[str, Any]] = {}

        for item in items:
            tgt_cat = item.get("target_category") or {}
            cat_id: int | None = tgt_cat.get("id") if isinstance(tgt_cat, dict) else None
            if cat_id not in groups:
                order.append(cat_id)
                groups[cat_id] = {
                    "target_category": tgt_cat,
                    "count": 0,
                    "items": [],
                }
            groups[cat_id]["items"].append(
                {
                    "target_product": item["target_product"],
                    "status": item["status"],
                }
            )
            groups[cat_id]["count"] += 1

        return [groups[cid] for cid in order]

