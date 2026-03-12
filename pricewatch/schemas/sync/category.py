"""Sync/import DTOs for category ingestion normalization.

These DTOs normalize raw adapter output (dicts or objects with varying field
names) into a canonical shape before it reaches the service layer.

Architecture contract
---------------------
- Inherits LooseBaseModel (extra=ignore — adapter output may include extras).
- Normalizes shape and primitive types only.
- Business decisions (what to do with normalized data) stay in services.
- Never imported from repository code.
"""
from __future__ import annotations

from typing import Optional

from pydantic import Field, field_validator

from pricewatch.schemas.base import LooseBaseModel


class CategoryIngestDTO(LooseBaseModel):
    """Normalized category record from an adapter's get_categories() output.

    Supports both dict and object input via model_validate().

    Usage in CategorySyncService::

        dto = CategoryIngestDTO.model_validate(raw_cat)
        if not dto.name:
            # skip — name is required
            continue
        upsert_category(session, store_id=store_id, name=dto.name,
                        external_id=dto.external_id, url=dto.url)
    """
    name: Optional[str] = Field(None)
    url: Optional[str] = Field(None)
    external_id: Optional[str] = Field(None)

    @field_validator("name", mode="before")
    @classmethod
    def _strip_name(cls, v):
        if isinstance(v, str):
            stripped = v.strip()
            return stripped if stripped else None
        return v

    @field_validator("url", "external_id", mode="before")
    @classmethod
    def _strip_str_or_none(cls, v):
        if isinstance(v, str):
            stripped = v.strip()
            return stripped if stripped else None
        return v

    @property
    def is_valid(self) -> bool:
        """Return True if this category has the minimum required fields."""
        return bool(self.name)

