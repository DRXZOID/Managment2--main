"""Tests for Commit 10: sync/import normalization DTOs.

Covers:
- CategoryIngestDTO: name stripping, empty->None, is_valid flag
- ProductIngestDTO: price coercion, alias fields, is_valid, price_raw fallback
"""
from __future__ import annotations

from decimal import Decimal

import pytest

from pricewatch.schemas.sync.category import CategoryIngestDTO
from pricewatch.schemas.sync.product import ProductIngestDTO


# ---------------------------------------------------------------------------
# CategoryIngestDTO
# ---------------------------------------------------------------------------

class TestCategoryIngestDTO:
    def test_valid_dict(self):
        dto = CategoryIngestDTO.model_validate({"name": "Helmets", "url": "https://example.com/helmets"})
        assert dto.name == "Helmets"
        assert dto.url == "https://example.com/helmets"
        assert dto.is_valid is True

    def test_name_stripped(self):
        dto = CategoryIngestDTO.model_validate({"name": "  Helmets  ", "url": None})
        assert dto.name == "Helmets"

    def test_empty_name_becomes_none(self):
        dto = CategoryIngestDTO.model_validate({"name": "   "})
        assert dto.name is None
        assert dto.is_valid is False

    def test_missing_name(self):
        dto = CategoryIngestDTO.model_validate({"url": "https://example.com"})
        assert dto.name is None
        assert dto.is_valid is False

    def test_empty_url_becomes_none(self):
        dto = CategoryIngestDTO.model_validate({"name": "Helmets", "url": "  "})
        assert dto.url is None

    def test_extra_fields_ignored(self):
        dto = CategoryIngestDTO.model_validate({"name": "Sticks", "unknown": "surprise"})
        assert dto.name == "Sticks"
        assert not hasattr(dto, "unknown")

    def test_object_with_attrs(self):
        class FakeCat:
            name = "Skates"
            url = "https://example.com/skates"
            external_id = "sk-01"
        dto = CategoryIngestDTO.model_validate({"name": FakeCat.name, "url": FakeCat.url, "external_id": FakeCat.external_id})
        assert dto.name == "Skates"
        assert dto.external_id == "sk-01"
        assert dto.is_valid is True


# ---------------------------------------------------------------------------
# ProductIngestDTO — basic fields
# ---------------------------------------------------------------------------

class TestProductIngestDTOBasic:
    def test_valid_dict(self):
        dto = ProductIngestDTO.model_validate({
            "name": "Helmet Pro",
            "product_url": "https://example.com/helmet-pro",
            "price": 999.0,
            "currency": "UAH",
        })
        assert dto.name == "Helmet Pro"
        assert dto.product_url == "https://example.com/helmet-pro"
        assert dto.price == Decimal("999")
        assert dto.currency == "UAH"
        assert dto.is_valid is True

    def test_url_alias_accepted(self):
        """'url' field should map to product_url via alias."""
        dto = ProductIngestDTO.model_validate({
            "name": "Helmet Pro",
            "url": "https://example.com/helmet-pro",
        })
        assert dto.product_url == "https://example.com/helmet-pro"
        assert dto.is_valid is True

    def test_missing_name_is_invalid(self):
        dto = ProductIngestDTO.model_validate({"product_url": "https://example.com/h"})
        assert dto.is_valid is False

    def test_missing_url_is_invalid(self):
        dto = ProductIngestDTO.model_validate({"name": "Helmet"})
        assert dto.is_valid is False

    def test_empty_name_becomes_none(self):
        dto = ProductIngestDTO.model_validate({"name": "   ", "product_url": "https://x.com"})
        assert dto.name is None
        assert dto.is_valid is False

    def test_empty_url_becomes_none(self):
        dto = ProductIngestDTO.model_validate({"name": "X", "product_url": "  "})
        assert dto.product_url is None

    def test_extra_fields_ignored(self):
        dto = ProductIngestDTO.model_validate({
            "name": "X", "product_url": "https://x.com", "mystery_field": "ignored"
        })
        assert not hasattr(dto, "mystery_field")


# ---------------------------------------------------------------------------
# ProductIngestDTO — price coercion
# ---------------------------------------------------------------------------

class TestProductIngestDTOPriceCoercion:
    def test_float_price(self):
        dto = ProductIngestDTO.model_validate({"name": "X", "product_url": "https://x.com", "price": 123.5})
        assert dto.price == Decimal("123.5")

    def test_int_price(self):
        dto = ProductIngestDTO.model_validate({"name": "X", "product_url": "https://x.com", "price": 999})
        assert dto.price == Decimal("999")

    def test_string_price_plain(self):
        dto = ProductIngestDTO.model_validate({"name": "X", "product_url": "https://x.com", "price": "1299.00"})
        assert dto.price == Decimal("1299.00")

    def test_string_price_with_spaces_and_comma(self):
        dto = ProductIngestDTO.model_validate({"name": "X", "product_url": "https://x.com", "price": "12 999,00"})
        assert dto.price == Decimal("12999.00")

    def test_price_none_with_price_raw_fallback(self):
        dto = ProductIngestDTO.model_validate({
            "name": "X", "product_url": "https://x.com",
            "price": None, "price_raw": "500 UAH",
        })
        # price_raw fallback via parse_price_value
        assert dto.price is not None
        assert float(dto.price) == pytest.approx(500.0)

    def test_invalid_price_string_becomes_none(self):
        dto = ProductIngestDTO.model_validate({"name": "X", "product_url": "https://x.com", "price": "N/A"})
        assert dto.price is None

    def test_currency_uppercased(self):
        dto = ProductIngestDTO.model_validate({
            "name": "X", "product_url": "https://x.com", "currency": "uah"
        })
        assert dto.currency == "UAH"


# ---------------------------------------------------------------------------
# ProductIngestDTO — is_available coercion
# ---------------------------------------------------------------------------

class TestProductIngestDTOAvailability:
    def test_true_bool(self):
        dto = ProductIngestDTO.model_validate({"name": "X", "product_url": "https://x.com", "is_available": True})
        assert dto.is_available is True

    def test_false_bool(self):
        dto = ProductIngestDTO.model_validate({"name": "X", "product_url": "https://x.com", "is_available": False})
        assert dto.is_available is False

    def test_string_false(self):
        dto = ProductIngestDTO.model_validate({"name": "X", "product_url": "https://x.com", "is_available": "false"})
        assert dto.is_available is False

    def test_string_true(self):
        dto = ProductIngestDTO.model_validate({"name": "X", "product_url": "https://x.com", "is_available": "true"})
        assert dto.is_available is True

    def test_none_remains_none(self):
        dto = ProductIngestDTO.model_validate({"name": "X", "product_url": "https://x.com"})
        assert dto.is_available is None


# ---------------------------------------------------------------------------
# ProductIngestDTO — source_url alias
# ---------------------------------------------------------------------------

class TestProductIngestDTOSourceUrl:
    def test_source_alias(self):
        dto = ProductIngestDTO.model_validate({
            "name": "X", "product_url": "https://x.com",
            "source": "https://source.example.com/item",
        })
        assert dto.source_url == "https://source.example.com/item"

    def test_explicit_source_url(self):
        dto = ProductIngestDTO.model_validate({
            "name": "X", "product_url": "https://x.com",
            "source_url": "https://explicit.example.com/item",
        })
        assert dto.source_url == "https://explicit.example.com/item"

