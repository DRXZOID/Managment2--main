/**
 * frontend/src/types/store.ts — Store and category frontend DTO types.
 *
 * These reflect the shapes returned by:
 *   GET /api/stores                         → { stores: StoreSummary[] }
 *   GET /api/stores/:id/categories          → { categories: CategorySummary[] }
 *
 * Field names match the current serializer output (pricewatch/web/serializers.py).
 */

// ---------------------------------------------------------------------------
// Store
// ---------------------------------------------------------------------------

export interface StoreSummary {
  id: number
  name: string
  is_reference: boolean
  base_url: string | null
}

// ---------------------------------------------------------------------------
// Category
// ---------------------------------------------------------------------------

export interface CategorySummary {
  id: number
  store_id: number
  name: string
  normalized_name: string | null
  url: string | null
  external_id: string | null
  updated_at: string | null
  /** Optional — present when requested with product_count=true */
  product_count?: number
}

