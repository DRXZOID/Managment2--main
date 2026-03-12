"""Shared Pydantic base model configuration for PriceWatch schemas.

All schema classes should inherit from PricewatchBaseModel to inherit:
- strict mode for API request schemas (no silent coercion of wrong types)
- populate_by_name=True (aliases and field names both accepted)
- frozen=False (mutable for convenience during construction in tests)

For import/sync schemas that receive loose external data, use LooseBaseModel
which permits more permissive coercion (str -> int, etc.).
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class PricewatchBaseModel(BaseModel):
    """Strict base model for HTTP request boundaries.

    Use this for API request body DTOs where the caller is expected to
    provide well-typed data.  Unexpected extra fields are forbidden to
    prevent silent data loss.
    """
    model_config = ConfigDict(
        strict=False,           # allow int->float coercion etc, but not str->int
        populate_by_name=True,  # accept both alias and field name
        extra="forbid",         # reject unknown fields — fail fast on typos
        frozen=False,
    )


class LooseBaseModel(BaseModel):
    """Permissive base model for sync/import boundaries.

    Use this for adapter/scraper output normalization where external data
    may arrive with type inconsistencies (e.g. price as string "99.90").
    Extra fields are ignored rather than rejected.
    """
    model_config = ConfigDict(
        strict=False,
        populate_by_name=True,
        extra="ignore",  # tolerate extra fields from adapters
        frozen=False,
    )

