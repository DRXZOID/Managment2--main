"""Repository for GapItemStatus — persisted review states for gap items.

Only non-default statuses are stored:
  - ``in_progress``
  - ``done``

The implicit default ``new`` is represented by *absence* of a row.
"""
from __future__ import annotations

from typing import cast

from sqlalchemy.orm import Session

from pricewatch.db.models import GapItemStatus, utcnow

ALLOWED_STATUSES = frozenset({"in_progress", "done"})


def get_gap_status(
    session: Session,
    reference_category_id: int,
    target_product_id: int,
) -> str:
    """Return the persisted status string, or ``'new'`` if no row exists."""
    row = (
        session.query(GapItemStatus)
        .filter(
            GapItemStatus.reference_category_id == reference_category_id,
            GapItemStatus.target_product_id == target_product_id,
        )
        .one_or_none()
    )
    return row.status if row is not None else "new"


def upsert_gap_status(
    session: Session,
    reference_category_id: int,
    target_product_id: int,
    status: str,
) -> GapItemStatus:
    """Create or update a GapItemStatus row.

    Raises ``ValueError`` for any status value outside ``ALLOWED_STATUSES``.
    The caller is responsible for committing the session.
    """
    if status not in ALLOWED_STATUSES:
        raise ValueError(
            f"Invalid gap status '{status}'. Allowed: {sorted(ALLOWED_STATUSES)}"
        )
    row = (
        session.query(GapItemStatus)
        .filter(
            GapItemStatus.reference_category_id == reference_category_id,
            GapItemStatus.target_product_id == target_product_id,
        )
        .one_or_none()
    )
    if row is None:
        row = GapItemStatus(
            reference_category_id=reference_category_id,
            target_product_id=target_product_id,
            status=status,
        )
        session.add(row)
    else:
        row.status = status
        row.updated_at = utcnow()
    session.flush()
    return row


def bulk_get_gap_statuses(
    session: Session,
    reference_category_id: int,
    target_product_ids: list[int],
) -> dict[int, str]:
    """Return a mapping ``{target_product_id: status}`` for the given product ids.

    Products without a persisted row are omitted from the result (caller treats
    them as ``'new'``).
    """
    if not target_product_ids:
        return {}
    rows = cast(
        list[GapItemStatus],
        cast(
            object,
            session.query(GapItemStatus)
            .filter(
                GapItemStatus.reference_category_id == reference_category_id,
                GapItemStatus.target_product_id.in_(target_product_ids),
            )
            .all(),
        ),
    )
    return {row.target_product_id: row.status for row in rows}


__all__ = [
    "ALLOWED_STATUSES",
    "get_gap_status",
    "upsert_gap_status",
    "bulk_get_gap_statuses",
]

