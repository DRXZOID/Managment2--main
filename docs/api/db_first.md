# DB-First API

## Scope

This document describes the supported API surface for the primary user-facing flow.

These endpoints operate on persisted data and are the main product contract.

## Endpoints

### `GET /api/stores`
Returns stores from the database.

### `GET /api/stores/<store_id>/categories`
Returns categories for a store from the database.

### `GET /api/categories/<category_id>/products`
Returns products for a category from the database.

### `GET /api/categories/<reference_category_id>/mapped-target-categories`
Returns target categories mapped to the selected reference category.
May support optional filtering by target store.

### `POST /api/comparison`
Builds comparison output from persisted data and mappings.

Expected behavior:
- reject requests without valid mapped context
- return DB-backed comparison results only

### `POST /api/comparison/confirm-match`
Persists a confirmed product match into `ProductMapping`.

### `POST /api/gap`
Returns grouped gap items for the selected review context.

Validation expectations:
- `target_store_id` is required
- `reference_category_id` is required
- `target_category_ids` must be non-empty and must belong to mapping scope

### `POST /api/gap/status`
Persists review status for a gap item.

Accepted statuses:
- `in_progress`
- `done`

Rejected as input:
- `new` because it is implicit

## Contract principles

- DB-backed endpoints are stable product behavior
- they should not depend on live scrape execution during request handling
- validation errors are preferable to implicit fallback behavior
