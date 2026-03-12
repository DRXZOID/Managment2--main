# Project Documentation

This directory contains the internal project documentation for **PriceWatch**.

The purpose of these documents is to separate stable engineering knowledge from the root `README.md`, reduce ambiguity, and make implementation and review easier.

## Principles

- `README.md` in the project root should remain a concise entry point.
- Stable design decisions, contracts, and invariants belong in `docs/`.
- Tests validate behavior, but should not be the only place where the behavior is specified.
- API behavior must be described independently from UI flows.
- Domain rules must be documented independently from endpoint descriptions.

## Recommended structure

```text
docs/
  README.md
  architecture/
    overview.md
    module_boundaries.md
    runtime_flows.md
  domain/
    domain_invariants.md
    comparison_and_matching.md
    gap_review.md
  api/
    db_first.md
    admin.md
    internal_legacy.md
  adapters/
    adapter_contract.md
    registry_and_discovery.md
  operations/
    sync_lifecycle.md
    scrape_runs.md
  testing/
    testing_strategy.md
  adr/
    0001-db-first-read-model.md
    0002-plugin-adapter-registry.md
    0003-gap-status-persistence.md
```

## Document index

### Architecture

- `architecture/overview.md` — high-level architecture, responsibilities, and major flows.
- `architecture/module_boundaries.md` — responsibilities of `app.py`, `pricewatch/core`, `db`, `services`, `shops`.
- `architecture/runtime_flows.md` — request-to-service-to-repository execution flows.

### Domain

- `domain/domain_invariants.md` — core entities, allowed states, uniqueness assumptions, lifecycle rules.
- `domain/comparison_and_matching.md` — matching semantics, candidate generation, confirmed mappings, score interpretation.
- `domain/gap_review.md` — formal specification for the gap review workflow.

### API

- `api/db_first.md` — supported read/query API used by the main UI.
- `api/admin.md` — sync, mapping management, scrape runs, service page operations.
- `api/internal_legacy.md` — debug or transitional endpoints, explicitly non-primary.

### Adapters

- `adapters/adapter_contract.md` — required adapter interface and data contract.
- `adapters/registry_and_discovery.md` — plugin registry, auto-discovery, domain resolution.

### Operations

- `operations/sync_lifecycle.md` — registry sync, category sync, product sync, failure handling, freshness model.
- `operations/scrape_runs.md` — scrape run lifecycle and observability expectations.

### Testing

- `testing/testing_strategy.md` — what is covered by tests, what remains specification-only, and required test layers.

### ADR

- `adr/0001-db-first-read-model.md`
- `adr/0002-plugin-adapter-registry.md`
- `adr/0003-gap-status-persistence.md`

## Migration plan from current root README

The current root README mixes:

- product overview,
- local setup,
- UI description,
- endpoint reference,
- domain rules,
- and implementation constraints.

That content should be split as follows:

- keep in root `README.md`:
  - project overview,
  - quick start,
  - minimal route summary,
  - link to `docs/README.md`.
- move to `docs/`:
  - detailed endpoint contracts,
  - comparison rules,
  - gap workflow,
  - adapter architecture,
  - invariants and operational flows.

## Definition of done for documentation baseline

The documentation baseline is considered established when:

1. all supported API families are documented in `docs/api/`;
2. core entities and invariants are documented in `docs/domain/`;
3. plugin/adapters and sync lifecycle are documented;
4. root `README.md` links to the documentation index;
5. temporary, debug, and legacy routes are explicitly marked as such.
