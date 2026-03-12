"""Request DTOs for /api/category-mappings and /api/category-mappings/auto-link."""
from __future__ import annotations

from typing import Optional

from pydantic import Field

from pricewatch.schemas.base import PricewatchBaseModel


class AutoLinkCategoryMappingsRequest(PricewatchBaseModel):
    """Request body for POST /api/category-mappings/auto-link."""
    reference_store_id: int = Field(..., gt=0)
    target_store_id: int = Field(..., gt=0)


class CreateCategoryMappingRequest(PricewatchBaseModel):
    """Request body for POST /api/category-mappings."""
    reference_category_id: int = Field(..., gt=0)
    target_category_id: int = Field(..., gt=0)
    match_type: Optional[str] = Field(None, max_length=50)
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


class UpdateCategoryMappingRequest(PricewatchBaseModel):
    """Request body for PUT /api/category-mappings/<id>."""
    match_type: Optional[str] = Field(None, max_length=50)
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)

