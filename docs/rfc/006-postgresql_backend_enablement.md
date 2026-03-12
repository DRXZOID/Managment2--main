# RFC-006: PostgreSQL Backend Enablement

- **Status:** Draft
- **Date:** 2026-03-12
- **Owners:** Project maintainers
- **Related ADRs:** ADR-0006 — Support PostgreSQL as an Alternative Database Backend and Use Pydantic for Boundary Validation

## 1. Summary

This RFC defines the requirements and rollout for making PostgreSQL a supported alternative backend within the existing SQLAlchemy-based persistence architecture.

In this project, PostgreSQL support means more than accepting a PostgreSQL connection URL. PostgreSQL is considered supported only when:

- the same ORM, repository, and service contracts work without backend-specific forks;
- schema creation and upgrades are managed through Alembic in non-test environments;
- schema-sensitive fields have been reviewed and corrected where necessary;
- core repository and service flows have been verified on PostgreSQL;
- documented operational guidance exists.

This RFC does not introduce a separate PostgreSQL persistence implementation.

## 2. Goals

This RFC establishes the work required to:

1. support PostgreSQL through the existing shared SQLAlchemy ORM and repository layer;
2. keep SQLite as the default local/developer backend;
3. make Alembic the canonical schema authority for non-test PostgreSQL environments;
4. correct schema choices that are weak under cross-backend operation;
5. verify that core persistence behavior works on PostgreSQL;
6. allow future PostgreSQL-specific optimizations without changing repository or service contracts.

## 3. Non-Goals

This RFC does not:

1. replace SQLite as the default developer backend;
2. introduce separate PostgreSQL-specific repositories;
3. redesign the domain model;
4. migrate the project away from Flask;
5. require a mandatory PostgreSQL CI job;
6. require immediate use of PostgreSQL-specific SQL features.

## 4. Compatibility Contract

PostgreSQL support is valid only if all of the following are true:

1. one shared SQLAlchemy ORM model set is used for SQLite and PostgreSQL;
2. one shared repository and service behavior is preserved across both backends;
3. Alembic can create and upgrade schema from an empty PostgreSQL database;
4. no core write path depends on undocumented SQLite-only coercion or transaction behavior;
5. schema-sensitive fields have documented PostgreSQL-safe behavior;
6. PostgreSQL setup and operational usage are documented.

## 5. Decisions

### 5.1 Backend model

The project SHALL support PostgreSQL as an alternative SQLAlchemy backend, not as a separate persistence architecture.

The project SHALL maintain:

- one ORM model set;
- one repository layer;
- one service-layer behavior model.

Backend-specific differences SHALL be limited to:

1. engine configuration;
2. migration execution;
3. approved schema corrections;
4. optional backend-specific optimizations introduced later.

### 5.2 Bootstrap policy

Runtime schema auto-creation MAY exist only for test and local development convenience workflows.

Runtime schema auto-creation SHALL NOT be treated as the canonical schema management mechanism for PostgreSQL or any other non-test deployment.

All non-test PostgreSQL environments SHALL use Alembic-managed schema creation and upgrades.

### 5.3 Exact numeric policy

Any field representing prices, monetary values, or other exact comparable business quantities SHALL use exact numeric storage.

Price-like fields SHALL be migrated from floating-point representation to `Decimal` / exact numeric database types.

Application-side conversion and serialization behavior for such fields SHALL be explicit.

### 5.4 Verification policy

PostgreSQL SHALL NOT be described as a supported backend until the following have been verified:

1. application startup with PostgreSQL configuration;
2. Alembic migration execution from an empty PostgreSQL database;
3. core repository flows on PostgreSQL;
4. core service flows on PostgreSQL;
5. documented PostgreSQL setup and operational guidance.

A mandatory PostgreSQL CI job is not required. Verification MAY be performed through maintained local or release-validation workflows.

### 5.5 Optimization policy

PostgreSQL-specific optimizations MAY be introduced later.

Such optimizations MUST:

1. preserve repository and service contracts;
2. preserve functional behavior;
3. avoid backend-specific forks in business logic.

Examples include:

- `ON CONFLICT`-based upsert strategies;
- PostgreSQL-specific indexes;
- PostgreSQL-specific type constraints.

## 6. Required Review Areas

Before PostgreSQL is declared supported, the project MUST review the following areas for cross-backend correctness:

1. floating-point vs exact numeric fields;
2. JSON fields;
3. timezone-aware timestamps;
4. constrained string/state fields;
5. unique and foreign-key constrained columns;
6. integrity-sensitive lookup-then-insert/update flows.

## 7. Implementation Phases

### Phase 1: Runtime and bootstrap discipline

Objectives:

1. verify startup with PostgreSQL configuration;
2. separate test/dev bootstrap from deployment schema management;
3. remove ambiguity about the canonical schema path.

Deliverables:

- documented backend configuration behavior;
- explicit restriction of runtime schema auto-create to test/dev use;
- documented Alembic-first posture for PostgreSQL.

### Phase 2: Schema corrections

Objectives:

1. identify schema choices unsafe or weak under PostgreSQL;
2. migrate price-like fields to exact numeric representation;
3. review JSON, timestamps, and constrained-string fields.

Deliverables:

- updated ORM definitions where needed;
- migrations for schema corrections;
- documented cross-backend schema decisions.

### Phase 3: Migration validation

Objectives:

1. verify Alembic-driven schema creation on PostgreSQL;
2. verify upgrade path from empty database to current schema;
3. eliminate ambiguity between runtime init and supported deployment path.

Deliverables:

- validated PostgreSQL migration flow;
- documented PostgreSQL setup steps;
- confirmed Alembic-first deployment guidance.

### Phase 4: Behavior verification

Objectives:

1. verify repository behavior on PostgreSQL;
2. verify service flows that depend on relational state;
3. identify and correct SQLite-only assumptions.

Deliverables:

- PostgreSQL verification workflow;
- evidence for core CRUD and service behavior;
- documented limitations if any remain.

### Phase 5: Support signoff

Objectives:

1. document PostgreSQL as supported only after verification is complete;
2. publish operational guidance;
3. record any deferred optimizations separately.

Deliverables:

- updated backend documentation;
- support-status confirmation;
- known limitations section, if needed.

## 8. Repository and Service Expectations

Repositories MUST be reviewed for:

1. implicit ordering assumptions;
2. reliance on permissive SQLite coercion;
3. race-sensitive create/update flows;
4. predictable handling of integrity violations;
5. transactional expectations.

Service-layer flows that depend on relational state MUST be verified on PostgreSQL, especially where they assume insert/update behavior that may differ under stricter backend semantics.

## 9. Risks

### 9.1 Type migration risk

Migrating price-like fields from floating-point to exact numeric representation may require data migration care, serializer changes, and application-side normalization updates.

### 9.2 Bootstrap ambiguity risk

If runtime schema initialization remains too permissive outside test/dev workflows, contributors may bypass Alembic and create schema drift.

### 9.3 Integrity and concurrency risk

Flows that appear correct under SQLite may reveal uniqueness or transaction issues under PostgreSQL.

### 9.4 False support risk

If verification discipline is weak, PostgreSQL may appear supported in documentation without sufficient operational proof.

## 10. Mitigations

The project SHOULD mitigate these risks by:

1. migrating exact numeric fields before claiming PostgreSQL support;
2. explicitly restricting runtime schema bootstrap to test/dev workflows;
3. reviewing integrity-sensitive repository flows directly;
4. tying support claims to demonstrated verification rather than configuration-level plausibility.

## 11. Acceptance Criteria

This RFC is implemented when all of the following are true:

1. the application runs against PostgreSQL through the same SQLAlchemy ORM and repository layer used for SQLite;
2. PostgreSQL schema creation and upgrades are performed through Alembic in non-test environments;
3. runtime `init_db` behavior is limited to test/dev convenience use;
4. price-like fields use exact numeric representation;
5. core repository and service flows have been verified on PostgreSQL;
6. no core business flow depends on undocumented SQLite-only behavior;
7. project documentation describes PostgreSQL as a supported backend with defined operational guidance;
8. later PostgreSQL-specific optimizations remain optional and contract-preserving.

## 12. Fixed Decisions

The following decisions are fixed by this RFC:

1. `init_db` is restricted to test/dev convenience workflows only;
2. price-like fields are to be migrated to `Decimal` / exact numeric representation;
3. a mandatory PostgreSQL CI job is not required;
4. PostgreSQL-specific optimizations are allowed later, provided they preserve repository and service contracts.

## 13. Final Recommendation

PostgreSQL SHOULD be enabled as a first-class alternative backend through the existing SQLAlchemy architecture.

Implementation SHALL focus on:

- Alembic as the canonical non-test schema authority;
- exact numeric correctness for price-like fields;
- verification of real PostgreSQL behavior;
- removal or isolation of SQLite-only assumptions;
- optional later PostgreSQL-specific optimizations that preserve functional contracts.