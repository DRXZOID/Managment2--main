# RFC-007: Pydantic Boundary Validation Rollout

- **Status:** Draft
- **Date:** 2026-03-12
- **Owners:** Project maintainers
- **Related ADRs:** ADR-0006 — Support PostgreSQL as an Alternative Database Backend and Use Pydantic for Boundary Validation

## 1. Summary

This RFC defines how the project will use Pydantic as the standard mechanism for validation and normalization at system boundaries.

In this project, boundary validation means:

- HTTP request payload validation;
- service-boundary DTO validation where raw dictionaries are currently passed across layers;
- synchronization and import payload normalization;
- standardized validation error handling.

This RFC does not replace SQLAlchemy ORM, does not introduce a separate domain model, and does not move business-rule validation into DTO schemas.

## 2. Goals

This RFC establishes the work required to:

1. validate key HTTP request payloads through explicit Pydantic schemas;
2. normalize synchronization and import payloads through dedicated DTOs;
3. reduce ad hoc dictionary parsing in routes and selected service entrypoints;
4. standardize validation failure handling;
5. preserve SQLAlchemy ORM as the persistence model;
6. keep repositories independent from DTO implementation details.

## 3. Non-Goals

This RFC does not:

1. replace SQLAlchemy ORM entities with Pydantic models;
2. introduce a separate rich domain model layer;
3. require immediate migration of all routes and services;
4. require broad response-schema standardization;
5. move the project away from Flask;
6. treat Pydantic validation as a substitute for business-rule validation.

## 4. Boundary Validation Model

Pydantic SHALL be the standard mechanism for validation and normalization at system boundaries.

The primary boundaries are:

1. HTTP request ingress;
2. synchronization/import ingress;
3. selected service entrypoints that currently accept loosely structured dictionaries.

Pydantic SHALL NOT:

1. replace SQLAlchemy ORM entities;
2. define persistence behavior;
3. substitute for business-rule validation;
4. become a dependency of repository internals.

## 5. Validation Responsibility Split

Pydantic is responsible only for boundary-level concerns, including:

- payload shape;
- required and optional fields;
- type coercion;
- normalization;
- field alias handling;
- basic constrained values;
- default value assignment.

Services and repositories remain responsible for:

- business rules;
- relational checks;
- uniqueness expectations;
- conflict handling;
- workflow and state transitions;
- persistence invariants.

Pydantic validation SHALL NOT be treated as a substitute for business validation.

## 6. DTO Categories

The rollout defines the following DTO categories.

### 6.1 Request DTOs

Request DTOs validate HTTP payloads received by route handlers.

They SHOULD be introduced first for high-value POST, PUT, and PATCH routes with non-trivial payload shape or repeated manual parsing logic.

### 6.2 Sync / Import DTOs

Sync and import DTOs normalize inbound category, product, and related ingestion payloads before service logic persists or compares them.

These DTOs SHOULD handle:

- alternative inbound field names;
- empty-string normalization;
- optional field defaults;
- numeric parsing and coercion;
- required identifier checks;
- safe URL or external-id normalization where needed.

### 6.3 Service Command DTOs

Service command DTOs MAY be introduced where service entrypoints currently accept loose or dictionary-shaped inputs.

These DTOs SHALL be introduced selectively only where they materially improve clarity and reduce repeated normalization logic.

### 6.4 Response DTOs

Response DTOs are explicitly secondary and optional in this rollout.

They MAY be introduced only where they remove clear duplication or clarify a public API contract.

Broad response-schema standardization is explicitly deferred.

## 7. Validation Error Contract

Validation failures SHOULD be mapped to one standardized HTTP error shape.

At minimum, the validation error response MUST include:

1. a stable top-level error code or type;
2. a human-readable summary;
3. field-level validation details where available.

Route-specific custom validation error formats SHOULD be eliminated as routes are migrated.

## 8. Migration Policy

Pydantic adoption SHALL be incremental.

The project SHALL NOT require all routes, services, and serializers to be migrated at once.

Priority SHALL be given to:

1. high-value POST, PUT, and PATCH request payloads;
2. synchronization and import flows with significant manual normalization;
3. service entrypoints that currently accept loosely structured dictionaries.

Legacy or low-value endpoints MAY remain on manual validation temporarily until the pattern is established.

## 9. Package Structure

Boundary validation schemas SHALL be organized under a dedicated `schemas/` package.

The recommended structure is:

- `schemas/requests/`
- `schemas/sync/`
- `schemas/services/`
- `schemas/responses/`

This structure SHALL remain clearly separated from SQLAlchemy ORM entities and persistence code.

## 10. Implementation Phases

### Phase 1: Validation foundation

Objectives:

1. add Pydantic validation conventions;
2. introduce the `schemas/` package structure;
3. define standardized validation error mapping.

Deliverables:

- schema package layout;
- shared validation integration pattern;
- one canonical HTTP validation error mapper.

### Phase 2: High-value request DTOs

Objectives:

1. migrate the most important route payloads first;
2. reduce repeated `request.get_json()` and direct dictionary parsing;
3. stabilize the request-validation pattern.

Deliverables:

- first request DTO set;
- route integration for selected endpoints;
- validation tests for migrated routes.

### Phase 3: Sync / import DTOs

Objectives:

1. move ingestion normalization into dedicated DTOs;
2. reduce ad hoc field extraction and coercion in sync services;
3. make normalization behavior explicit and testable.

Deliverables:

- product sync DTOs;
- category sync DTOs;
- malformed-input and normalization tests.

### Phase 4: Selective service command DTOs

Objectives:

1. improve service entrypoints that still accept loose structured input;
2. reduce route-to-service coupling through raw dictionaries.

Deliverables:

- selected service command DTOs where justified;
- simplified service boundary contracts.

### Phase 5: Optional response DTOs

Objectives:

1. introduce response DTOs only where they remove clear duplication;
2. avoid premature response-model standardization.

Deliverables:

- selective response DTOs if justified;
- no blanket rewrite requirement.

## 11. Explicit Anti-Goals

This rollout SHALL NOT:

1. replace ORM entities with Pydantic models;
2. push DTO objects into repository internals;
3. duplicate the same validation logic across DTOs, services, and repositories without necessity;
4. move business-rule enforcement into request schemas;
5. require broad response-schema standardization before request and sync boundaries are stabilized.

## 12. Risks

### 12.1 Mixed-style transition risk

During rollout, the codebase will temporarily contain both manual validation and DTO-based validation.

### 12.2 Over-modeling risk

If every internal structure becomes a Pydantic model prematurely, the project may accumulate unnecessary schema duplication.

### 12.3 Boundary leakage risk

If DTO concerns leak into repositories or persistence internals, coupling may increase instead of decrease.

### 12.4 Business-rule confusion risk

There is a risk of incorrectly moving business validation into DTOs.

## 13. Mitigations

The project SHOULD mitigate these risks by:

1. migrating incrementally rather than all at once;
2. keeping Pydantic at boundaries only;
3. documenting the split between shape validation and business validation;
4. introducing response DTOs only where they clearly reduce duplication;
5. preserving repository independence from DTO implementation details.

## 14. Acceptance Criteria

This RFC is implemented when all of the following are true:

1. key HTTP payloads are validated through explicit Pydantic schemas;
2. core synchronization and import flows use DTO-based normalization;
3. validation failures are returned through a standardized error contract;
4. core service logic no longer depends on raw unvalidated route payloads;
5. SQLAlchemy ORM remains the persistence model;
6. repositories remain independent from Pydantic implementation details.

## 15. Fixed Decisions

The following decisions are fixed by this RFC:

1. boundary schemas are organized under `schemas/`;
2. response DTOs are selective and optional;
3. service command DTOs are introduced selectively only where justified;
4. a minimal standardized validation error contract is required.

## 16. Final Recommendation

The project SHOULD adopt Pydantic incrementally as the standard mechanism for validation and normalization at HTTP, synchronization/import, and selected service boundaries.

Implementation SHALL focus on:

- explicit boundary contracts;
- clear separation of shape validation from business validation;
- standardized validation failures;
- preservation of SQLAlchemy ORM as the persistence model;
- repository independence from DTO implementation details.