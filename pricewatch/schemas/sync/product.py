"""Sync/import DTO for product ingestion normalization.

This DTO centralizes the raw adapter product normalization that was
previously spread across ProductSyncService._normalize_product_dto().
It handles:
  - field aliases (url -> product_url, source/source_site -> source_url)
  - empty string -> None normalization
  - safe numeric price coercion (int, float, or price string)
  - boolean is_available coercion
  - URL field trimming

Architecture contract
---------------------
- Inherits LooseBaseModel (extra=ignore).
- Normalization of shape and primitive types ONLY.
- No business decisions — those stay in ProductSyncService.
- Never imported from repository code.

URL resolution (relative -> absolute) is NOT done here because it requires
a category_url context that belongs to the service layer.
"""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Optional

from pydantic import Field, field_validator, model_validator

from pricewatch.schemas.base import LooseBaseModel


def _safe_decimal(value) -> Optional[Decimal]:
    """Attempt to coerce *value* to Decimal.  Return None on failure."""
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float)):
        try:
            return Decimal(str(value))
        except InvalidOperation:
            return None
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        # Try direct conversion first
        try:
            return Decimal(stripped)
        except InvalidOperation:
            pass
        # Try cleaning whitespace and comma-decimal separators
        cleaned = stripped.replace('\u00A0', '').replace('\u202F', '').replace(' ', '').replace(',', '.')
        m = re.search(r"-?\d+(?:\.\d+)?", cleaned)
        if m:
            try:
                return Decimal(m.group(0))
            except InvalidOperation:
                pass
    return None


class ProductIngestDTO(LooseBaseModel):
    """Normalized product record from an adapter's product output.

    Supports dict and object input via model_validate().

    The DTO normalizes the raw adapter shape into a consistent structure
    that ProductSyncService can consume directly without repeated ad hoc
    parsing.

    Usage in ProductSyncService::

        dto = ProductIngestDTO.model_validate(raw_item)
        if not dto.is_valid:
            # skip — missing product_url or name
            continue
        upsert_product(
            session,
            store_id=store_id,
            name=dto.name,
            product_url=dto.product_url,   # service resolves relative URLs
            price=dto.price,
            currency=dto.currency,
            ...
        )
    """
    # Core identity fields
    name: Optional[str] = Field(None)
    product_url: Optional[str] = Field(None, alias="url")  # prefer product_url, fall back to url
    external_id: Optional[str] = Field(None)
    description: Optional[str] = Field(None)

    # Price fields — normalized to Decimal
    price: Optional[Decimal] = Field(None)
    price_raw: Optional[str] = Field(None)
    currency: Optional[str] = Field(None)

    # Availability
    is_available: Optional[bool] = Field(None)

    # Source tracking
    source_url: Optional[str] = Field(None, alias="source")

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
        "strict": False,
    }

    # ------------------------------------------------------------------
    # Field normalizers
    # ------------------------------------------------------------------

    @field_validator("name", "description", "external_id", mode="before")
    @classmethod
    def _strip_or_none(cls, v):
        if isinstance(v, str):
            stripped = v.strip()
            return stripped if stripped else None
        return v

    @field_validator("product_url", "source_url", mode="before")
    @classmethod
    def _strip_url(cls, v):
        if isinstance(v, str):
            stripped = v.strip()
            return stripped if stripped else None
        return v

    @field_validator("currency", mode="before")
    @classmethod
    def _strip_currency(cls, v):
        if isinstance(v, str):
            stripped = v.strip()
            return stripped.upper() if stripped else None
        return v

    @field_validator("is_available", mode="before")
    @classmethod
    def _coerce_bool(cls, v):
        if v is None:
            return None
        if isinstance(v, bool):
            return v
        if isinstance(v, int):
            return bool(v)
        if isinstance(v, str):
            return v.lower() not in {"false", "0", "no", ""}
        return bool(v)

    @field_validator("price", mode="before")
    @classmethod
    def _coerce_price(cls, v):
        """Coerce price to Decimal.  Strings like '12 999,00 ₴' are parsed."""
        return _safe_decimal(v)

    @model_validator(mode="after")
    def _resolve_price_from_raw(self):
        """If price is still None after direct coercion, attempt to parse price_raw."""
        if self.price is None and self.price_raw:
            from pricewatch.core.normalize import parse_price_value
            try:
                parsed_price, parsed_currency = parse_price_value(self.price_raw)
                if parsed_price is not None:
                    self.price = _safe_decimal(parsed_price)
                if not self.currency and parsed_currency:
                    self.currency = parsed_currency.upper() if parsed_currency else None
            except Exception:
                pass
        return self

    @model_validator(mode="after")
    def _resolve_product_url_alias(self):
        """Support both 'product_url' and 'url' field names from adapter dicts."""
        # model_validator runs after field assignment; product_url already set via alias
        return self

    @property
    def is_valid(self) -> bool:
        """Return True if the DTO has minimum required fields to be persisted."""
        return bool(self.product_url and self.name)

