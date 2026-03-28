/**
 * frontend/src/types/common.ts — Cross-cutting UI / pagination types.
 *
 * These are purely frontend adapter types and are not coupled to Python
 * internal naming or backend schema field names.
 */

// ---------------------------------------------------------------------------
// Status / variant token
// ---------------------------------------------------------------------------

/**
 * StatusKind — the canonical set of visual variant tokens used across the UI.
 *
 * Maps to the existing CSS class suffix convention:
 *   info    → .status-info      / .status-block.info
 *   success → .status-success   / .status-block.success
 *   warning → .status-warning   / .status-block.warn
 *   error   → .status-error     / .status-block.error
 *   muted   → grey / disabled visual state (no specific global class yet)
 */
export type StatusKind = 'info' | 'success' | 'warning' | 'error' | 'muted'

// ---------------------------------------------------------------------------
// Pagination wrapper
// ---------------------------------------------------------------------------

/**
 * PaginatedResult<T> — lightweight wrapper for paged list responses.
 *
 * Used by API adapter functions that return a page of items together
 * with metadata needed to request the next page.
 */
export interface PaginatedResult<T> {
  items: T[]
  total: number
  offset: number
  limit: number
}

