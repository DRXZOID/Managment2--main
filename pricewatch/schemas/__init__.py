"""Pydantic boundary-validation schemas for PriceWatch.

Architecture contract
---------------------
This package owns *boundary* validation only — it is the entry point guard
for data arriving at system boundaries (HTTP requests, import/sync feeds).

Layer responsibilities:
  schemas/requests/  — HTTP request payload DTOs (POST/PUT/PATCH body parsing)
  schemas/sync/      — Import/synchronisation ingestion DTOs (normalize raw
                       adapter output before it reaches service layer)
  schemas/services/  — Optional command DTOs for complex service entrypoints
  schemas/responses/ — Optional response DTOs (only where duplication is clear)

Firm boundaries (never cross these):
  1. Repositories MUST NOT import anything from this package.
     Repository internals use plain Python scalars and ORM entities only.
  2. Business logic MUST NOT live inside schema validators.
     Validators normalize *shape* and primitive types; services decide workflow.
  3. Response schemas are OPTIONAL — add only when serializer duplication is clear.

Usage pattern for HTTP routes
------------------------------
    from pricewatch.schemas.requests.comparison import ComparisonRequest
    from pricewatch.schemas.validation import parse_request_body, validation_error_response

    @app.route("/api/comparison", methods=["POST"])
    def api_comparison():
        payload, err = parse_request_body(ComparisonRequest)
        if err:
            return err
        result = ComparisonService(session).compare(
            reference_category_id=payload.reference_category_id,
            ...
        )
        return jsonify(result)
"""

