# Contributing

This document defines the working conventions for contributors to the project.
It does not replace architectural or API documentation from `docs/`; instead, it explains how changes should be prepared, validated, and documented.

## Scope

This repository contains:

- Flask application entrypoints and routes
- DB-backed comparison flows
- store/category/product mapping logic
- scraper adapter integrations
- migrations and test suite
- templates/static assets for user-facing and service/admin UI

Contributors must preserve the current architectural direction:

- main product flow is DB-first
- external shop scraping is integration-layer behavior
- confirmed mappings are persisted truth
- runtime candidates are advisory only
- gap review is an operational workflow with its own state model

## Change categories

### 1. Domain changes

Examples:

- new mapping rules
- comparison semantics changes
- gap-state logic changes
- schema/model invariant changes

Required alongside code changes:

- update relevant files in `docs/domain/`
- add or update tests that encode the invariant
- mention migration impact explicitly if persistence changes

### 2. API changes

Examples:

- request/response contract changes
- endpoint additions/removals
- admin/service route changes

Required alongside code changes:

- update the matching file in `docs/api/`
- preserve clear separation between DB-first, admin/service, and internal/legacy APIs
- document whether the change is backward-compatible

### 3. Integration changes

Examples:

- new scraper adapter
- adapter registry changes
- shop-specific extraction logic

Required alongside code changes:

- update `docs/integrations/adapter_contract.md`
- add adapter-focused tests
- avoid leaking shop-specific assumptions into domain/core layers

### 4. Operational changes

Examples:

- sync lifecycle changes
- new manual review flows
- new runbook-worthy maintenance steps

Required alongside code changes:

- update `docs/operations/`
- document failure modes and operator expectations

## Branch and commit expectations

Prefer small, reviewable commits.

Recommended commit structure:

1. schema/model changes
2. repository/service logic
3. route/controller updates
4. tests
5. documentation

When a change spans all layers, keep docs in the same PR and do not defer documentation to “later”.

## Testing expectations

Before opening or merging a change, run the relevant test subset and the full suite when touching cross-cutting behavior.

At minimum, contributors should validate:

- repository behavior for persistence-related changes
- API contract tests for route changes
- comparison/gap tests for business-rule changes
- adapter tests for scraper integration changes

Refer to `docs/testing/testing_strategy.md` for the full testing guidance.

## Documentation rules

Documentation is part of the deliverable.

A change is incomplete when it modifies one of the following without updating docs:

- domain invariants
- API contract
- operator workflow
- architecture boundaries
- adapter integration contract

### Source-of-truth policy

- `docs/architecture/` explains structure and boundaries
- `docs/domain/` explains invariants and business semantics
- `docs/api/` explains externally or internally consumed contracts
- `docs/integrations/` explains adapter/plugin contracts
- `docs/operations/` explains sync and maintenance procedures
- tests enforce behavior and should align with the above

The root `README.md` should remain an overview and navigation entrypoint, not the only place where the system is specified.

## Review checklist

Before merging, reviewers should verify:

- architecture boundaries are preserved
- DB-first behavior remains the default for main comparison flow
- no new persistent semantics are introduced without documentation
- legacy/debug endpoints are not expanded into product-facing contract accidentally
- tests reflect the claimed behavior
- docs were updated where needed

## Anti-patterns to avoid

Avoid the following unless there is an explicit ADR or approved refactor plan:

- putting new core business logic directly into a large route/controller file
- coupling comparison logic to live scraping
- storing runtime candidate matches as if they were confirmed mappings
- treating gap status rows as a complete set of all visible gap items
- adding product-facing dependencies on legacy/debug endpoints
- encoding critical invariants only in README prose without docs/tests alignment
- importing `pricewatch.schemas.*` from repository code (violates ADR-0006 boundary)
- adding business logic inside Pydantic validators (validators normalize shape only)
- calling `Base.metadata.create_all()` outside of test/dev helpers (use `alembic upgrade head` instead)
- using `Float` for price/monetary fields (use `Numeric(12, 4)` — see ADR-0006)

---

## Database and schema management

### Default backend

SQLite is the default backend for local and lightweight development.
No additional configuration is required.

### PostgreSQL support

PostgreSQL is a supported alternative backend.  To use it:

```bash
export DATABASE_URL=postgresql+psycopg2://user:pass@host/dbname
alembic upgrade head
flask run
```

PostgreSQL behavior is verified via `tests/verify_postgres.py` (see that file for setup instructions).

### Schema management — Alembic is the canonical authority

**For non-test environments (especially PostgreSQL) Alembic is the ONLY supported schema management path.**

- Never rely on `init_db()` / `Base.metadata.create_all()` in production or staging.
- Always run `alembic upgrade head` before starting the application after a schema change.
- Add a new Alembic migration whenever the ORM models change.
- For SQLite local development, runtime `create_all` is still available as a convenience — but it is not the recommended path even there.

### Adding a new Alembic migration

```bash
# Generate migration from ORM model changes:
alembic revision --autogenerate -m "describe the change"
# Review the generated migration in migrations/versions/
# Apply it:
alembic upgrade head
```

For SQLite migrations that use ALTER TABLE, ensure `render_as_batch=True` is set in `migrations/env.py` (it is already configured).

---

## Boundary validation (Pydantic schemas)

### What the schemas/ package is for

`pricewatch/schemas/` contains Pydantic DTOs for **boundary validation only**.  These are used at:

- HTTP request boundaries (`schemas/requests/`) — validate POST/PUT/PATCH payloads
- Sync/import boundaries (`schemas/sync/`) — normalize raw adapter output before service processing

### How to add a new request DTO

1. Create a class in `pricewatch/schemas/requests/<domain>.py` that extends `PricewatchBaseModel`.
2. Use `parse_request_body(MySchema)` in the Flask route.
3. Business validation stays in the service layer — not in validators.

```python
# Example route pattern
from pricewatch.schemas.validation import parse_request_body
from pricewatch.schemas.requests.my_domain import MyRequest

@app.route("/api/something", methods=["POST"])
def api_something():
    payload, err = parse_request_body(MyRequest)
    if err:
        return err   # (response, 422) tuple
    result = MyService(session).do_work(field=payload.field)
    return jsonify(result)
```

### How to add a sync/import DTO

1. Create a class in `pricewatch/schemas/sync/<domain>.py` that extends `LooseBaseModel`.
2. Use `MyDTO.model_validate(raw_item)` in the service to normalize raw adapter data.
3. Check `dto.is_valid` before persisting.

### Firm boundaries — never cross these

1. **Repositories MUST NOT import anything from `pricewatch.schemas`.**
   Repository methods accept plain Python scalars, `datetime`, `Decimal`, and ORM entities only.
2. **Business logic MUST NOT live inside Pydantic validators.**
   Validators normalize shape and primitive types; services decide workflow.
3. **Response DTOs are OPTIONAL** — only add them when serializer duplication is clearly significant.

### Validation error contract

When Pydantic validation fails on a migrated route, the response is:

```json
{
  "error": "validation_error",
  "message": "Request body is invalid.",
  "details": [
    {"field": "reference_category_id", "message": "Field required"},
    ...
  ]
}
```

HTTP status: `422 Unprocessable Entity` for Pydantic validation failures,
`400 Bad Request` for missing/non-JSON body.

---
