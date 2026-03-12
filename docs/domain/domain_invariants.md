# Domain Invariants

## Scope

This document defines the stable domain rules of the project independent of UI details and endpoint layout.

## Core entities

### Store

Represents a supported source shop.

Invariants:

- a store is the persisted representation of an adapter-backed source;
- stores are synchronized from the adapter registry into the database;
- a store must be uniquely identifiable within the database;
- products and categories belong to exactly one store.

### Category

Represents a store-specific category.

Invariants:

- category identity is store-local, not globally shared across stores;
- categories from different stores are related only through `category_mappings`;
- a category belongs to exactly one store;
- products belong to exactly one category.

### Product

Represents a persisted store product captured during synchronization.

Invariants:

- a product belongs to exactly one store and one category;
- product rows are read-model data used for comparison;
- comparison does not require live scraping once products are synchronized;
- products are compared only within a category-mapping context.

### CategoryMapping

Represents an explicit relationship between one reference category and one target category.

Invariants:

- category mappings are required for supported DB-first comparison;
- comparison is allowed only when the selected reference category has mapped target categories;
- mappings are many-to-many at the global level;
- pair identity of a mapping is immutable after creation;
- metadata such as confidence or match type may be updated without changing the linked pair.

### ProductMapping

Represents a confirmed product-level relationship.

Invariants:

- confirmed product mappings are authoritative;
- candidate matches are not persisted as product mappings automatically;
- confirmation is an explicit action;
- confirmed product mappings suppress ambiguity for the same compared context.

### ScrapeRun

Represents an administrative sync attempt or execution record.

Invariants:

- sync operations should be observable through scrape runs;
- scrape runs are an operational history, not domain content;
- scrape run entries must be readable independently from sync execution.

### GapItemStatus

Represents review progress for a target-side gap product within a reference category context.

Invariants:

- the default state is `new` and is **implicit**;
- only non-default states are persisted;
- allowed persisted states are `in_progress` and `done`;
- a status row is unique per `(reference_category_id, target_product_id)` pair;
- `done` may be hidden by default in UI filters, but still counts in summary statistics.

## Comparison invariants

### Reference-centered comparison

The system uses a reference store/category as the anchor for comparison.

Invariants:

- one comparison request has exactly one reference category;
- the compared target scope is limited to explicitly selected mapped target categories;
- target categories outside the mapped set are invalid for the comparison context.

### Persisted vs runtime match states

There are two distinct classes of match results:

1. **confirmed** — persisted in `product_mappings`;
2. **candidate** — computed at runtime and not persisted automatically.

Invariants:

- confirmed matches outrank runtime candidates;
- candidates are advisory, not authoritative;
- target-only and reference-only results are derived after confirmed and candidate matching are applied.

### No live scraping in user comparison flow

Invariants:

- main comparison results must be generated from persisted database state;
- stale data is a freshness/operations concern, not a reason to switch comparison to live scraping automatically.

## Gap review invariants

Gap review exists to surface target products that are not already covered by confirmed mappings or candidate lists.

An item is considered a gap item only if all of the following hold:

- it belongs to the selected target store;
- it belongs to one of the selected mapped target categories;
- it is not part of a confirmed `ProductMapping` for the given comparison context;
- it is not included among runtime candidate groups for the given comparison context.

Invariants:

- gap review is target-side only;
- gap review requires mapped categories;
- absence of mappings is a configuration problem, not an empty business result.

## Freshness invariants

The system distinguishes between read-model data and synchronization operations.

Invariants:

- stores/categories/products in the database may become stale over time;
- stale data should be addressed by explicit sync operations;
- read flows should not mutate synchronization state implicitly.

## Documentation invariants

These rules must be reflected consistently in:

- API docs,
- service/admin docs,
- tests,
- future ADRs.

If implementation and this document diverge, the divergence must be resolved explicitly, not silently reinterpreted.
