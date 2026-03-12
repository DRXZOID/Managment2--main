# Sync Lifecycle

## Purpose

This document describes how operational synchronization keeps DB-backed comparison usable.

## Principle

Synchronization is a write path into persistent storage.
Comparison is a read path from persistent storage.

These responsibilities must remain separate.

## Main lifecycle stages

### 1. Registry → stores
Administrative sync imports known adapters/stores into DB metadata.

### 2. Store → categories
Category sync reads categories from an adapter and persists them for a selected store.

### 3. Category → products
Product sync reads products for a selected category and persists them.

### 4. History capture
Each significant sync action should leave an operational record in scrape history.

## Operational expectations

- sync actions are launched from `/service` or admin API
- sync failures should be visible and inspectable
- stale data should be handled by prompting for refresh, not by changing comparison semantics

## Consistency expectations

After successful sync:
- stores should exist before categories depend on them
- categories should exist before products depend on them
- mappings should be reviewed after category structure changes
- comparisons should operate on the latest persisted state available

## Failure handling

When sync fails:
- the transaction should not leave partial silent corruption
- the error should be visible through API/UI feedback
- previous persisted data may remain, but freshness should be treated accordingly

## Recommended run order for operators

1. sync stores
2. sync categories for affected stores
3. review or create category mappings
4. sync products for mapped categories
5. run comparison or gap review
