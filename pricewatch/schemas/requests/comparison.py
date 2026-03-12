"""Request DTOs for /api/comparison and /api/comparison/confirm-match endpoints."""
from __future__ import annotations

from typing import List, Optional

from pydantic import Field, field_validator

from pricewatch.schemas.base import PricewatchBaseModel


class ComparisonRequest(PricewatchBaseModel):
    """Request body for POST /api/comparison.

    Business rule: reference_category_id is required.
    Exactly one of {target_category_id, target_category_ids, target_store_id}
    must be supplied — validated downstream in ComparisonService (not here).
    """
    reference_category_id: int = Field(..., gt=0, description="ID of the reference category")
    target_category_id: Optional[int] = Field(None, gt=0)
    target_category_ids: Optional[List[int]] = Field(None, min_length=1)
    target_store_id: Optional[int] = Field(None, gt=0)

    @field_validator("target_category_ids", mode="before")
    @classmethod
    def _coerce_target_ids(cls, v):
        if v is not None:
            return [int(i) for i in v]
        return v


class ConfirmMatchRequest(PricewatchBaseModel):
    """Request body for POST /api/comparison/confirm-match."""
    reference_product_id: int = Field(..., gt=0)
    target_product_id: int = Field(..., gt=0)
    match_status: Optional[str] = Field("confirmed", max_length=50)
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    comment: Optional[str] = Field(None, max_length=2000)

