# Boundary Validation Architecture

**Related:** ADR-0006, RFC-007

## Overview

Boundary validation in this project uses **Pydantic** exclusively at system boundaries — HTTP request ingestion and sync/import ingestion. It does NOT extend into service logic or repository internals.

```
HTTP Request Body
     │
     ▼
┌─────────────────────────────┐
│  pricewatch/schemas/        │  ← Pydantic boundary (this layer)
│  requests/  sync/           │
└──────────────┬──────────────┘
               │ plain Python scalars / typed attrs
               ▼
┌─────────────────────────────┐
│  pricewatch/services/       │  ← business logic, no Pydantic DTOs
└──────────────┬──────────────┘
               │ scalars / ORM entities
               ▼
┌─────────────────────────────┐
│  pricewatch/db/repositories/│  ← plain scalars + ORM entities only
└─────────────────────────────┘
```

## Package layout

```
pricewatch/schemas/
├── __init__.py         — architecture contract docstring
├── base.py             — PricewatchBaseModel (strict), LooseBaseModel (permissive)
├── validation.py       — parse_request_body(), validation_error_response()
├── requests/           — HTTP request body DTOs (POST/PUT/PATCH)
│   ├── comparison.py   — ComparisonRequest, ConfirmMatchRequest
│   ├── gap.py          — GapRequest, GapStatusRequest
│   └── mappings.py     — AutoLinkCategoryMappingsRequest, CreateCategoryMappingRequest, ...
├── sync/               — Import/sync normalization DTOs
│   ├── category.py     — CategoryIngestDTO
│   └── product.py      — ProductIngestDTO
├── services/           — Service command DTOs (optional, selective)
└── responses/          — Response DTOs (optional, only where duplication is clear)
```

## Base model types

| Class | Config | Use for |
|---|---|---|
| `PricewatchBaseModel` | `extra="forbid"`, `strict=False` | HTTP request DTOs — reject unknown fields |
| `LooseBaseModel` | `extra="ignore"`, `strict=False` | Sync/import DTOs — tolerate extra adapter fields |

## Standard HTTP route pattern

```python
from pricewatch.schemas.validation import parse_request_body
from pricewatch.schemas.requests.my_domain import MyRequest

@app.route("/api/something", methods=["POST"])
def api_something():
    payload, err = parse_request_body(MyRequest)
    if err:
        return err   # (Response, 422) or (Response, 400) tuple
    result = MyService(session).do_work(field=payload.field)
    return jsonify(result)
```

## Standard sync/import pattern

```python
from pricewatch.schemas.sync.product import ProductIngestDTO

for raw_item in adapter.get_products():
    dto = ProductIngestDTO.model_validate(
        raw_item if isinstance(raw_item, dict) else raw_item.__dict__
    )
    if not dto.is_valid:
        # log and skip
        continue
    upsert_product(session, name=dto.name, product_url=dto.product_url, price=dto.price, ...)
```

## Validation error contract

All Pydantic validation failures on migrated HTTP routes use this response shape:

```json
{
  "error": "validation_error",
  "message": "Request body is invalid.",
  "details": [
    {"field": "reference_category_id", "message": "Field required"},
    {"field": "target_store_id",        "message": "Input should be greater than 0"}
  ]
}
```

- HTTP `422` — Pydantic validation error (malformed/missing fields)
- HTTP `400` — missing or non-JSON body

## Firm boundaries — NEVER cross these

1. **Repositories MUST NOT import `pricewatch.schemas.*` or `pydantic`.**
   - Repositories accept only plain Python scalars (`int`, `str`, `float`, `bool`), `datetime`, `Decimal`, and SQLAlchemy ORM entity instances.
   - This is enforced by `tests/test_repository_pydantic_independence.py`.

2. **Business logic MUST NOT live inside Pydantic validators.**
   - Validators normalize *shape and primitive types* only.
   - Workflow rules (e.g. "reference store must differ from target store") stay in services.

3. **Response DTOs are OPTIONAL.**
   - Add only where manual serializer duplication is clearly significant.
   - Do not introduce response schemas speculatively.

## Adding a new request DTO

1. Add a class extending `PricewatchBaseModel` in `pricewatch/schemas/requests/<domain>.py`.
2. Declare required fields with `Field(..., gt=0)` etc. — Pydantic enforces them.
3. Use `parse_request_body(MySchema)` in the Flask route.
4. Add route tests for valid payload, missing required fields (expect 422), non-JSON (expect 400).

## Adding a sync/import DTO

1. Add a class extending `LooseBaseModel` in `pricewatch/schemas/sync/<domain>.py`.
2. Add `@field_validator` for normalization (strip whitespace, empty→None, safe numeric coerce).
3. Add an `is_valid` property for minimum required field check.
4. Add unit tests in `tests/test_sync_dtos.py`.

## What has been migrated (as of ADR-0006 implementation)

### Request DTOs (HTTP boundary)
- `POST /api/comparison` — `ComparisonRequest`
- `POST /api/comparison/confirm-match` — `ConfirmMatchRequest`
- `POST /api/gap` — `GapRequest`
- `POST /api/gap/status` — `GapStatusRequest`
- `POST /api/category-mappings/auto-link` — `AutoLinkCategoryMappingsRequest`
- `POST /api/category-mappings` — `CreateCategoryMappingRequest`
- `PUT  /api/category-mappings/<id>` — `UpdateCategoryMappingRequest`

### Sync/import DTOs
- Category sync via `CategoryIngestDTO` (used in `CategorySyncService`)
- Product ingest normalization via `ProductIngestDTO` (available; full service migration optional)

### Intentionally deferred
- Legacy/debug endpoints (`/api/check`, `/api/parse-example`, `/api/reference-products`)
- Response DTO adoption (deferred — duplication not yet critical)
- Full `ProductSyncService` migration to `ProductIngestDTO` (foundation laid, service migration is Follow-up B)

