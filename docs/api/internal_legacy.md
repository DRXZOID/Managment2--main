# Internal / Legacy / Debug API

## Scope

This document marks endpoints that exist in the codebase but should not be treated as stable product API.

## Endpoints

### `GET /api/reference-products`
Live scraping of reference adapter/category data.

### `POST /api/check`
Live scraping of arbitrary URLs or diagnostic comparison flow.

### `POST /api/parse-example`
Debug parsing of HTML fragments/examples.

## Status

These endpoints are considered one or more of:
- legacy
- internal
- debug-only
- migration aids during transition to DB-first architecture

## Rules

- do not document these as public product contracts
- do not build primary UI behavior around them
- do not promise response stability to external consumers
- prefer DB-first endpoints for all normal user workflows

## Recommended future direction

Choose one of:
1. keep as internal-only with explicit flags and naming
2. move to a debug blueprint/namespace
3. remove after migration is complete
