"""Request DTOs for /api/gap and /api/gap/status endpoints."""
from __future__ import annotations

from typing import List, Optional

from pydantic import Field, field_validator

from pricewatch.schemas.base import PricewatchBaseModel

# Valid gap item statuses.  "new" is implicit (absence of a row) — only
# non-default states are stored in gap_item_statuses.
GAP_ITEM_STATUSES = {"in_progress", "done", "new"}


class GapRequest(PricewatchBaseModel):
    """Request body for POST /api/gap."""
    target_store_id: int = Field(..., gt=0)
    reference_category_id: int = Field(..., gt=0)
    target_category_ids: List[int] = Field(..., min_length=1)
    search: Optional[str] = Field(None, max_length=500)
    only_available: Optional[bool] = None
    statuses: Optional[List[str]] = None

    @field_validator("target_category_ids", mode="before")
    @classmethod
    def _coerce_ids(cls, v):
        if v is not None:
            return [int(i) for i in v]
        return v

    @field_validator("search", mode="before")
    @classmethod
    def _empty_str_to_none(cls, v):
        if isinstance(v, str) and not v.strip():
            return None
        return v


class GapStatusRequest(PricewatchBaseModel):
    """Request body for POST /api/gap/status."""
    reference_category_id: int = Field(..., gt=0)
    target_product_id: int = Field(..., gt=0)
    status: str = Field(..., max_length=50)

    @field_validator("status")
    @classmethod
    def _validate_status(cls, v: str) -> str:
        if v not in GAP_ITEM_STATUSES:
            raise ValueError(
                f"status must be one of: {', '.join(sorted(GAP_ITEM_STATUSES))}"
            )
        return v

