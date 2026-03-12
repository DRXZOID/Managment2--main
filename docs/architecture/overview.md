# Architecture Overview

## Purpose

The application is a database-backed product comparison system for multiple stores with a plugin-based scraping layer.

Its main operational model is:

1. discover supported stores through adapter registry;
2. synchronize store/category/product data into the database;
3. manage category mappings between reference and target stores;
4. perform DB-first comparison using persisted products and mappings;
5. review unresolved target-side assortment gaps through a dedicated workflow.

## Architectural style

The current codebase follows a pragmatic layered architecture:

- **UI / HTTP layer** — Flask routes, HTML pages, JSON endpoints;
- **Service layer** — orchestration of sync, comparison, and review workflows;
- **Core/domain logic** — normalization, heuristics, matching, scoring;
- **Persistence layer** — SQLAlchemy models, repositories, migrations;
- **Integration layer** — per-shop adapters with registry-based discovery.

The code is not fully separated into strict modules yet, because `app.py` still acts as a composition root and also contains significant routing logic. That is acceptable for the current size of the project, but the boundaries must be documented clearly.

## Main runtime components

### 1. Flask application

Responsibilities:

- create and configure the application;
- expose HTML pages (`/`, `/service`, `/gap`);
- expose JSON APIs for DB-first flows and admin flows;
- translate HTTP requests into service operations;
- return API-appropriate status codes and payloads.

Non-goals:

- no heavy business logic in route handlers;
- no scraping logic embedded directly in route handlers;
- no domain-specific matching rules defined at HTTP boundary.

### 2. Adapter registry

Responsibilities:

- discover available store adapters;
- resolve adapter by domain/store;
- provide canonical source of supported scraping integrations.

The registry is the integration boundary between internal logic and external shop-specific scraping/parsing implementations.

### 3. Sync services

Responsibilities:

- synchronize stores from registry into the database;
- synchronize categories for a store;
- synchronize products for a category;
- record scrape runs and expose operational visibility.

Sync is an explicit administrative operation. End-user read flows must not depend on live scraping.

### 4. Domain comparison engine

Responsibilities:

- normalize titles / attributes;
- classify products for matching;
- generate candidate matches;
- combine confirmed mappings with runtime candidates;
- identify target-only products for gap review.

This is the core business logic of the project.

### 5. Persistence

Responsibilities:

- persist normalized store/category/product data;
- persist category mappings and confirmed product mappings;
- persist scrape run history;
- persist non-default gap review statuses.

The database is the read model for the main user-facing comparison experience.

## Primary user-facing flows

### DB-first comparison flow

1. Admin syncs stores/categories/products into the database.
2. Admin creates or auto-links category mappings.
3. User opens `/` and selects reference and target context.
4. System reads products and mappings from the database only.
5. System produces comparison result:
   - confirmed matches,
   - candidate groups,
   - reference-only products,
   - target-only products.

### Gap review flow

1. Reviewer opens `/gap`.
2. Reviewer selects target store and reference category.
3. System derives mapped target categories.
4. System returns target products not covered by confirmed mappings or candidate lists.
5. Reviewer marks items as `in_progress` or `done`.
6. Default state `new` remains implicit when no status row exists.

### Administrative sync flow

1. Service page triggers registry-to-DB store sync.
2. Category sync loads categories for a selected store.
3. Product sync loads products for a selected category.
4. Each operation emits a scrape run record for visibility and troubleshooting.

## Design principles

### DB-first reads

The default user-facing comparison flow must read from persisted data, not from live site scraping. This improves reproducibility, debuggability, and UI responsiveness.

### Explicit mappings over hidden inference

Category mappings and confirmed product mappings are first-class persisted entities. Runtime heuristics may suggest candidates, but confirmed mappings are authoritative.

### Plugin isolation

Each store-specific adapter should implement the same contract, while normalization and comparison remain internal and reusable.

### Reviewable operational state

Long-running or failure-prone operations such as synchronization must be observable through scrape runs and service endpoints.

### Minimal persistence for reviewer workflow

Gap review stores only non-default statuses. The absence of a row means `new`.

## Known architecture tensions

### `app.py` as a multi-role module

`app.py` currently combines composition root, page routing, and API routing. This should be documented now and optionally refactored later into:

- app factory / bootstrap,
- page blueprints,
- API blueprints,
- dependency wiring.

### Documentation spread across README and tests

The project has good behavioral coverage in tests, but stable rules should be lifted into dedicated `docs/` files.

### Legacy/debug endpoints in production tree

Some endpoints are intentionally internal or transitional. They should remain documented, but isolated from the supported API surface.

## Architectural boundaries to preserve

The following boundaries are important and should not be blurred further:

- adapters do not define domain matching policy;
- routes do not define normalization policy;
- end-user pages do not depend on live scraping;
- candidate matches are runtime-only unless explicitly confirmed;
- gap status persistence must remain sparse and non-default-only.
