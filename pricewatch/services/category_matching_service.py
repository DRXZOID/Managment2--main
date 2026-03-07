"""Category auto-matching service.

Creates CategoryMapping rows based on exact normalized_name matches between
reference and target store categories.  Fuzzy matching is intentionally NOT
implemented here — only exact normalized_name equality is used.

Usage::

    result = CategoryMatchingService.auto_link(
        session,
        reference_store_id=1,
        target_store_id=2,
    )
    # result == {"created": N, "skipped": N}
"""
from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from pricewatch.db.repositories.category_repository import (
    list_categories_by_store,
    get_category_mapping,
    create_category_mapping,
)
from pricewatch.db.models import Store

logger = logging.getLogger(__name__)


class CategoryMatchingService:
    """Auto-link category pairs by exact normalized_name match."""

    # Set to False to disable exact auto-linking at the class level.
    ENABLE_EXACT_AUTO_LINK: bool = True

    @classmethod
    def auto_link(
        cls,
        session: Session,
        *,
        reference_store_id: int,
        target_store_id: int,
    ) -> dict[str, Any]:
        """Create CategoryMapping rows for exact normalized_name matches.

        Only creates a row when:
          - Both categories share the same normalized_name (exact match).
          - The reference_category belongs to a store with is_reference=True.
          - The target_category belongs to a store with is_reference=False.
          - The mapping pair does not yet exist in the DB.

        Returns::

            {"created": int, "skipped": int}
        """
        if not cls.ENABLE_EXACT_AUTO_LINK:
            return {"created": 0, "skipped": 0}

        ref_store = session.get(Store, reference_store_id)
        tgt_store = session.get(Store, target_store_id)

        if ref_store is None:
            raise ValueError(f"Reference store {reference_store_id} not found")
        if tgt_store is None:
            raise ValueError(f"Target store {target_store_id} not found")
        if not getattr(ref_store, "is_reference", False):
            raise ValueError(
                f"Store {reference_store_id} ('{ref_store.name}') is not a reference store"
            )
        if getattr(tgt_store, "is_reference", False):
            raise ValueError(
                f"Store {target_store_id} ('{tgt_store.name}') is a reference store; "
                "target_store_id must be a non-reference store"
            )

        ref_cats = list_categories_by_store(session, reference_store_id)
        tgt_cats = list_categories_by_store(session, target_store_id)

        # Build lookup: normalized_name -> list[Category] for target store
        tgt_by_norm: dict[str, list] = {}
        for cat in tgt_cats:
            norm = cat.normalized_name or ""
            tgt_by_norm.setdefault(norm, []).append(cat)

        created = 0
        skipped = 0

        for ref_cat in ref_cats:
            ref_norm = ref_cat.normalized_name or ""
            if not ref_norm:
                skipped += 1
                continue

            matched_tgt_cats = tgt_by_norm.get(ref_norm, [])
            for tgt_cat in matched_tgt_cats:
                existing = get_category_mapping(
                    session,
                    reference_category_id=ref_cat.id,
                    target_category_id=tgt_cat.id,
                )
                if existing:
                    skipped += 1
                    logger.debug(
                        "auto_link: skipped existing mapping ref_cat=%d tgt_cat=%d",
                        ref_cat.id, tgt_cat.id,
                    )
                    continue

                create_category_mapping(
                    session,
                    reference_category_id=ref_cat.id,
                    target_category_id=tgt_cat.id,
                    match_type="exact",
                    confidence=1.0,
                )
                created += 1
                logger.info(
                    "auto_link: created mapping '%s' (ref_cat=%d) -> '%s' (tgt_cat=%d)",
                    ref_cat.name, ref_cat.id, tgt_cat.name, tgt_cat.id,
                )

        return {"created": created, "skipped": skipped}

