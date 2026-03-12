"""Canonical HTTP request-body parsing and validation error mapping.

This module provides two functions that together form the standard validation
pattern for Flask routes in this project:

    parse_request_body(SchemaClass)
        Parse + validate Flask request.json against a Pydantic schema.
        Returns (validated_dto, None) on success or (None, error_response) on failure.

    validation_error_response(exc)
        Convert a Pydantic ValidationError into a standardised Flask JSON error response.
        Returns a (response, 422) tuple ready for direct return from a Flask view.

Standard pattern in routes
---------------------------
    from pricewatch.schemas.validation import parse_request_body

    @app.route("/api/something", methods=["POST"])
    def api_something():
        payload, err = parse_request_body(SomethingRequest)
        if err:
            return err                # already a (response, 422) tuple
        # use payload.<field> directly
        result = some_service.do_work(field=payload.field)
        return jsonify(result)

Error response contract
-----------------------
    {
        "error": "validation_error",
        "message": "Request body is invalid.",
        "details": [
            {"field": "reference_category_id", "message": "Field required"},
            ...
        ]
    }

HTTP status: 422 Unprocessable Entity for Pydantic validation failures,
             400 Bad Request for missing/non-JSON body.
"""
from __future__ import annotations

import json
from typing import TYPE_CHECKING, Type, Tuple, Optional, TypeVar

from flask import request
from pydantic import ValidationError

if TYPE_CHECKING:
    from pydantic import BaseModel

T = TypeVar("T", bound="BaseModel")


def _json_response(data: dict, status: int) -> Tuple:
    """Build a JSON Flask response tuple that works outside of app context.

    ``flask.jsonify`` requires an active application context.  Using
    ``flask.Response`` with ``json.dumps`` avoids that requirement while
    producing an identical HTTP response — useful for unit tests that call
    validation helpers without a full Flask app.
    """
    from flask import Response
    return (
        Response(
            json.dumps(data, ensure_ascii=False),
            status=status,
            mimetype="application/json",
        ),
        status,
    )


def parse_request_body(
    schema_class: Type[T],
) -> Tuple[Optional[T], Optional[Tuple]]:
    """Parse and validate the current Flask request body against *schema_class*.

    Returns
    -------
    (dto, None)
        When validation succeeds.

    (None, (response, status_code))
        When validation fails — return the tuple directly from your view function.
    """
    if not request.is_json:
        return None, _json_response(
            {
                "error": "invalid_content_type",
                "message": "Request must be JSON (Content-Type: application/json).",
            },
            400,
        )

    data = request.get_json(silent=True)
    if data is None:
        return None, _json_response(
            {
                "error": "invalid_json",
                "message": "Request body could not be parsed as JSON.",
            },
            400,
        )

    try:
        dto = schema_class.model_validate(data)
        return dto, None
    except ValidationError as exc:
        return None, validation_error_response(exc)


def validation_error_response(exc: ValidationError) -> Tuple:
    """Convert a Pydantic *ValidationError* to a standardised Flask response tuple (422).

    Works both inside and outside an application context.
    """
    details = []
    for error in exc.errors():
        field = ".".join(str(segment) for segment in error.get("loc", ()))
        details.append({
            "field": field or "__root__",
            "message": error.get("msg", "invalid value"),
        })

    return _json_response(
        {
            "error": "validation_error",
            "message": "Request body is invalid.",
            "details": details,
        },
        422,
    )
