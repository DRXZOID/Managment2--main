"""Tests for standardised HTTP validation error mapping (Commit 8).

Verifies:
1. parse_request_body returns (dto, None) for valid payload.
2. parse_request_body returns (None, (response, 422)) for invalid payload.
3. validation_error_response produces the standardised error contract shape.
4. Non-JSON body returns (None, (response, 400)).
5. Unparseable JSON body returns (None, (response, 400)).
6. Extra forbidden fields are rejected with 422.
"""
from __future__ import annotations

import json
from typing import List, Optional

import pytest
from pydantic import ValidationError

from pricewatch.schemas.base import PricewatchBaseModel
from pricewatch.schemas.validation import validation_error_response


# ---------------------------------------------------------------------------
# Minimal schema fixtures
# ---------------------------------------------------------------------------

class _SampleRequest(PricewatchBaseModel):
    reference_category_id: int
    target_store_id: int
    names: Optional[List[str]] = None


# ---------------------------------------------------------------------------
# validation_error_response unit tests (no Flask context needed)
# ---------------------------------------------------------------------------

def _make_validation_error(schema_class, data: dict) -> ValidationError:
    try:
        schema_class.model_validate(data)
    except ValidationError as exc:
        return exc
    raise AssertionError("Expected ValidationError was not raised")


def test_validation_error_response_top_level_keys():
    """Error response must contain error, message, details keys."""
    exc = _make_validation_error(_SampleRequest, {})
    response, status_code = validation_error_response(exc)
    assert status_code == 422
    body = json.loads(response.data)
    assert body["error"] == "validation_error"
    assert "message" in body
    assert isinstance(body["details"], list)


def test_validation_error_response_field_details():
    """Each detail entry must have 'field' and 'message' keys."""
    exc = _make_validation_error(_SampleRequest, {"reference_category_id": "not_an_int"})
    response, status_code = validation_error_response(exc)
    body = json.loads(response.data)
    assert body["details"], "details list must not be empty"
    for detail in body["details"]:
        assert "field" in detail, f"'field' key missing in detail: {detail}"
        assert "message" in detail, f"'message' key missing in detail: {detail}"


def test_validation_error_response_missing_required_fields():
    """Missing required fields must appear as detail entries."""
    exc = _make_validation_error(_SampleRequest, {})
    response, _ = validation_error_response(exc)
    body = json.loads(response.data)
    field_names = {d["field"] for d in body["details"]}
    assert "reference_category_id" in field_names
    assert "target_store_id" in field_names


def test_validation_error_response_extra_fields_forbidden():
    """Extra fields must trigger validation error when schema uses extra=forbid."""
    exc = _make_validation_error(_SampleRequest, {
        "reference_category_id": 1,
        "target_store_id": 2,
        "unexpected_field": "surprise",
    })
    response, status_code = validation_error_response(exc)
    assert status_code == 422
    body = json.loads(response.data)
    assert body["error"] == "validation_error"


# ---------------------------------------------------------------------------
# parse_request_body integration tests (require Flask app context)
# ---------------------------------------------------------------------------

@pytest.fixture()
def _flask_app():
    """Minimal Flask app for request context in parse_request_body tests."""
    from flask import Flask
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app


def test_parse_request_body_valid(_flask_app):
    """Valid payload returns (dto, None)."""
    from pricewatch.schemas.validation import parse_request_body
    payload = {"reference_category_id": 42, "target_store_id": 7}
    with _flask_app.test_request_context(
        "/", method="POST",
        data=json.dumps(payload),
        content_type="application/json",
    ):
        dto, err = parse_request_body(_SampleRequest)
    assert err is None
    assert dto is not None
    assert dto.reference_category_id == 42
    assert dto.target_store_id == 7


def test_parse_request_body_invalid_returns_422(_flask_app):
    """Missing required fields return (None, (response, 422))."""
    from pricewatch.schemas.validation import parse_request_body
    with _flask_app.test_request_context(
        "/", method="POST",
        data=json.dumps({}),
        content_type="application/json",
    ):
        dto, err = parse_request_body(_SampleRequest)
    assert dto is None
    assert err is not None
    response, status_code = err
    assert status_code == 422
    body = json.loads(response.get_data(as_text=True))
    assert body["error"] == "validation_error"
    assert isinstance(body["details"], list)
    assert len(body["details"]) >= 1


def test_parse_request_body_non_json_returns_400(_flask_app):
    """Non-JSON Content-Type returns (None, (response, 400))."""
    from pricewatch.schemas.validation import parse_request_body
    with _flask_app.test_request_context(
        "/", method="POST",
        data="not json at all",
        content_type="text/plain",
    ):
        dto, err = parse_request_body(_SampleRequest)
    assert dto is None
    assert err is not None
    _, status_code = err
    assert status_code == 400


def test_parse_request_body_bad_json_returns_400(_flask_app):
    """Unparseable JSON returns (None, (response, 400))."""
    from pricewatch.schemas.validation import parse_request_body
    with _flask_app.test_request_context(
        "/", method="POST",
        data="{broken json",
        content_type="application/json",
    ):
        dto, err = parse_request_body(_SampleRequest)
    assert dto is None
    assert err is not None
    _, status_code = err
    assert status_code == 400


def test_parse_request_body_extra_fields_rejected(_flask_app):
    """Extra fields (extra=forbid) return (None, (response, 422))."""
    from pricewatch.schemas.validation import parse_request_body
    payload = {
        "reference_category_id": 1,
        "target_store_id": 2,
        "unknown_field": "oops",
    }
    with _flask_app.test_request_context(
        "/", method="POST",
        data=json.dumps(payload),
        content_type="application/json",
    ):
        dto, err = parse_request_body(_SampleRequest)
    assert dto is None
    assert err is not None
    _, status_code = err
    assert status_code == 422

