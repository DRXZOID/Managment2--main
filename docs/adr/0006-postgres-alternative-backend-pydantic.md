# ADR-0006: Support PostgreSQL as an Alternative Database Backend and Use Pydantic for Boundary Validation

- **Status:** Accepted — implemented
- **Date:** 2026-03-12
- **Decision Makers:** Project maintainers
- **Related RFCs:** RFC-006 — PostgreSQL Backend Enablement; RFC-007 — Pydantic Boundary Validation Rollout

## 1. Context

The project currently uses SQLAlchemy as its persistence abstraction and defaults to SQLite for local and lightweight operation. The existing architecture already follows a shared ORM and repository model and is close to backend-neutral operation, but practical usage remains SQLite-first.

The project also contains a growing amount of manual validation, normalization, and coercion logic at HTTP and service boundaries. Input contracts are often implicit, distributed across routes and services, and not standardized.

The project needs:

1. a stronger alternative backend for production-oriented deployments;
2. a clear rule for preserving one persistence architecture across supported SQL backends;
3. a maintainable validation model at system boundaries;
4. these improvements without replacing SQLAlchemy ORM as the persistence model.

## 2. Decision

The project SHALL:

1. support PostgreSQL as an alternative runtime database backend;
2. retain one shared SQLAlchemy ORM and repository layer for SQLite and PostgreSQL;
3. use Alembic as the canonical schema migration mechanism for non-test environments;
4. retain SQLite as the default local/developer backend;
5. adopt Pydantic for validation at system boundaries only.

The project SHALL NOT:

1. introduce separate SQLite-specific and PostgreSQL-specific repository implementations;
2. replace SQLAlchemy ORM entities with Pydantic models;
3. fork service-layer business logic by database backend;
4. treat runtime schema auto-creation as the canonical production schema path.

## 3. Rationale

### 3.1 Why PostgreSQL

PostgreSQL provides a stronger backend option for:

- concurrent access;
- transactional reliability;
- production-oriented deployment;
- future indexing and query growth;
- operational maturity beyond lightweight local usage.

SQLite remains appropriate for local development and lightweight workflows, but it MUST NOT remain the only effectively supported backend.

### 3.2 Why one persistence layer

The current SQLAlchemy-based architecture already provides the correct abstraction boundary for multi-backend support.

The requirement is backend portability, not multiple persistence implementations. Separate PostgreSQL-specific repositories would duplicate behavior, increase maintenance cost, and create avoidable backend drift.

### 3.3 Why Pydantic

Pydantic provides:

- explicit input contracts;
- centralized coercion and normalization;
- predictable validation failure behavior;
- less manual parsing logic;
- clearer and more testable boundary handling.

### 3.4 Why not use Pydantic as the main model layer

The immediate problem is weak and scattered boundary validation, not the absence of a new primary application model layer.

Replacing ORM entities or introducing a parallel domain model would add complexity without proportionate benefit at this stage.

## 4. Architectural Rules Established by This ADR

### 4.1 Persistence rules

1. The project SHALL maintain one SQLAlchemy ORM model set.
2. The project SHALL maintain one repository and service behavior across supported SQL backends.
3. All production-grade schema evolution SHALL go through Alembic migrations.
4. Runtime schema auto-creation MAY exist only for test/dev convenience workflows.
5. New persistence code SHALL avoid undocumented SQLite-specific assumptions.
6. PostgreSQL-specific optimizations MAY be introduced later only if they preserve repository and service contracts.

### 4.2 Validation rules

1. Pydantic SHALL be used at system boundaries, including:
   - HTTP request payload validation,
   - service input DTOs where raw dictionaries are currently passed across layers,
   - synchronization/import DTOs,
   - selected response DTOs where this removes duplicated serialization logic.
2. Pydantic SHALL NOT replace SQLAlchemy ORM entities.
3. Validation logic SHOULD be concentrated at boundaries rather than duplicated across routes, services, and repositories.
4. Business rules and persistence invariants SHALL remain the responsibility of services and repositories, not DTO shape validation.
5. Repository internals SHALL remain independent from Pydantic implementation details.

## 5. Consequences

### 5.1 Positive consequences

1. PostgreSQL becomes a production-suitable backend option.
2. SQLite remains available for lightweight local workflows.
3. Persistence architecture remains unified.
4. Boundary contracts become explicit and testable.
5. Manual normalization and parsing logic is reduced.
6. Long-term maintainability improves.

### 5.2 Negative consequences

1. Some schema and model choices must be reviewed for cross-backend correctness.
2. Validation rollout will temporarily create mixed old/new validation styles.
3. Additional DTO definitions and tests will increase short-term implementation effort.
4. Some currently permissive flows may fail earlier and more explicitly after validation is formalized.

## 6. Required Follow-up Work

### 6.1 PostgreSQL backend enablement

The project MUST:

1. restrict runtime `init_db` usage to test/dev convenience workflows;
2. make Alembic the canonical schema path for non-test PostgreSQL environments;
3. review schema-sensitive fields for PostgreSQL correctness;
4. migrate price-like fields to exact numeric representation;
5. verify core repository and service behavior on PostgreSQL;
6. document PostgreSQL setup and operational usage.

### 6.2 Boundary validation rollout

The project MUST introduce Pydantic models for:

1. key HTTP request payloads;
2. synchronization/import DTOs;
3. selected service input contracts;
4. selected response DTOs where the benefit is clear.

### 6.3 Deferred optimizations

The project MAY later introduce PostgreSQL-specific optimizations such as:

- `ON CONFLICT`-based upsert strategies;
- PostgreSQL-specific indexes;
- stricter PostgreSQL-specific type constraints.

Such optimizations MUST preserve repository and service contracts and MUST NOT introduce backend-specific business behavior forks.

## 7. Alternatives Considered

### 7.1 Keep SQLite as the only backend

Rejected.

This would preserve the simplest immediate path but would not provide a stronger deployment option or sufficient long-term backend portability.

### 7.2 Create separate PostgreSQL-specific repositories

Rejected.

This would duplicate persistence logic, increase maintenance burden, and create unnecessary divergence between supported backends.

### 7.3 Continue manual validation only

Rejected.

The current validation approach is already too distributed, repetitive, and weakly specified.

### 7.4 Replace SQLAlchemy entities with Pydantic-driven application models

Rejected for now.

This would be a larger architectural shift than is required to address the current persistence and validation needs.

## 8. Non-Goals

This ADR does not:

1. migrate the project away from Flask;
2. define detailed PostgreSQL-specific optimizations;
3. require immediate response-schema standardization for all endpoints;
4. introduce a separate domain model layer;
5. require a mandatory PostgreSQL CI job.

## 9. Acceptance Criteria

This ADR is considered implemented when all of the following are true:

1. the application runs against SQLite and PostgreSQL through the same SQLAlchemy ORM and repository layer;
2. PostgreSQL schema creation and upgrades are performed through Alembic in non-test environments;
3. runtime `init_db` behavior is limited to test/dev convenience use;
4. price-like fields use exact numeric representation;
5. core boundary inputs are validated through Pydantic models;
6. core repository and service flows have been verified on PostgreSQL;
7. no core business flow depends on undocumented SQLite-specific behavior;
8. project documentation reflects the supported backend and validation model.

## 10. Final Statement

The project will evolve toward a single database-agnostic SQLAlchemy persistence layer with:

- SQLite for local and lightweight usage;
- PostgreSQL as a supported production-oriented alternative;
- Pydantic as the standard validation mechanism at application boundaries.

This direction preserves architectural simplicity while strengthening backend portability, schema discipline, and boundary correctness.