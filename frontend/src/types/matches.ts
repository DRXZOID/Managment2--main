/**
 * frontend/src/types/matches.ts — Product mapping review page DTOs.
 *
 * Mirrors the shapes returned by:
 *   GET  /api/product-mappings   → { product_mappings: ProductMappingRow[], total: number }
 *   DELETE /api/product-mappings/<id>
 */

// ---------------------------------------------------------------------------
// Sub-types embedded in ProductMappingRow
// ---------------------------------------------------------------------------

export type MatchStatus = 'confirmed' | 'rejected' | string

export interface ProductSummary {
  id: number
  store_id: number | null
  category_id: number | null
  name: string
  price: number | string | null
  currency: string | null
  product_url: string | null
}

export interface MatchesCategoryRef {
  id: number
  store_id: number | null
  name: string
}

export interface MatchesStoreRef {
  id: number
  name: string
  is_reference: boolean
}

// ---------------------------------------------------------------------------
// Main row type
// ---------------------------------------------------------------------------

export interface ProductMappingRow {
  id: number
  reference_product_id: number
  target_product_id: number
  match_status: MatchStatus | null
  confidence: number | null
  comment: string | null
  created_at: string | null
  updated_at: string | null
  reference_product: ProductSummary | null
  target_product: ProductSummary | null
  reference_category: MatchesCategoryRef | null
  target_category: MatchesCategoryRef | null
  reference_store: MatchesStoreRef | null
  target_store: MatchesStoreRef | null
}

// ---------------------------------------------------------------------------
// Filter state
// ---------------------------------------------------------------------------

export interface MatchesFilters {
  referenceStoreId: number | null
  targetStoreId: number | null
  referenceCategoryId: number | null
  targetCategoryId: number | null
  /** 'confirmed' | 'rejected' | '' (all) */
  status: string
  search: string
}

// ---------------------------------------------------------------------------
// API response wrapper
// ---------------------------------------------------------------------------

export interface MatchesListResponse {
  rows: ProductMappingRow[]
  total: number
}

