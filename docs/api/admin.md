# Admin / Service API

## Scope

This document describes operational endpoints used by `/service` and administrative workflows.

These endpoints are part of supported operations, but they are not the same as the primary user-facing comparison contract.

## Store and sync endpoints

### `POST /api/admin/stores/sync`
Synchronize adapter registry metadata into DB stores.

### `POST /api/stores/<store_id>/categories/sync`
Fetch categories for the selected store and persist them.

### `POST /api/categories/<category_id>/products/sync`
Fetch products for the selected category and persist them.

## Category mapping endpoints

### `GET /api/category-mappings`
List category mappings.

### `POST /api/category-mappings`
Create a mapping.

Rules:
- the reference/target pair becomes identity of the mapping
- the pair should not be mutable later

### `PUT /api/category-mappings/<mapping_id>`
Update mapping metadata only.

### `DELETE /api/category-mappings/<mapping_id>`
Delete a mapping.

### `POST /api/category-mappings/auto-link`
Attempt automatic mapping by normalized name or similar deterministic rule.

## Scrape history endpoints

### `GET /api/scrape-runs`
List scrape run history.

### `GET /api/scrape-runs/<run_id>`
Get one run.

### `GET /api/scrape-status`
Return current or latest status suitable for polling from the service UI.

## Contract principles

- admin endpoints may change faster than DB-first read APIs, but should still be documented
- operational side effects must be explicit
- sync endpoints must surface errors clearly
- admin APIs should not be presented as end-user catalog browsing APIs
