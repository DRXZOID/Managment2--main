/**
 * frontend/src/types/gap.ts — Gap analysis page DTOs.
 *
 * Mirrors the shapes returned by:
 *   GET  /api/categories/<id>/mapped-target-categories
 *   POST /api/gap
 *   POST /api/gap/status
 */

// ---------------------------------------------------------------------------
// Mapped-target-categories
// ---------------------------------------------------------------------------

export interface MappedTargetCategory {
  target_category_id: number
  target_category_name: string
  target_store_id?: number | null
  target_store_name?: string | null
  mapping_id?: number | null
}

// ---------------------------------------------------------------------------
// Gap result shapes
// ---------------------------------------------------------------------------

export type GapItemStatus = 'new' | 'in_progress' | 'done'

export interface GapProduct {
  id: number
  name: string | null
  price: number | string | null
  currency: string | null
  is_available: boolean | null
  product_url: string | null
}

export interface GapItem {
  status: GapItemStatus
  target_product: GapProduct | null
}

export interface GapGroup {
  target_category: { id: number; name: string } | null
  count: number
  items: GapItem[]
}

export interface GapSummary {
  total: number
  new: number
  in_progress: number
  done: number
}

export interface GapResult {
  summary: GapSummary
  groups: GapGroup[]
}

// ---------------------------------------------------------------------------
// Request body
// ---------------------------------------------------------------------------

export interface GapRequestBody {
  target_store_id: number
  reference_category_id: number
  target_category_ids: number[]
  search: string | null
  only_available: boolean | null
  statuses: GapItemStatus[]
}

