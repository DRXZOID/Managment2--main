/**
 * frontend/src/api/adapters/productMappings.ts — Product-mappings API adapter.
 *
 * Converts raw /api/product-mappings server payload (serialize_product_mapping_rich)
 * to stable frontend ProductMappingRow DTOs.
 */
import type {
  ProductMappingRow,
  ProductSummary,
  MatchesCategoryRef,
  MatchesStoreRef,
} from '@/types/matches'

// ---------------------------------------------------------------------------
// Raw server shapes (as returned by serializers.py serialize_product_mapping_rich)
// ---------------------------------------------------------------------------

interface RawProductSummary {
  id: number
  store_id: number | null
  category_id: number | null
  name: string | null
  price: number | string | null
  currency: string | null
  product_url: string | null
}

interface RawCategoryRef {
  id: number
  store_id: number | null
  name: string | null
}

interface RawStoreRef {
  id: number
  name: string | null
  is_reference: boolean
}

export interface RawProductMapping {
  id: number
  reference_product_id: number
  target_product_id: number
  match_status: string | null
  confidence: number | null
  comment: string | null
  created_at: string | null
  updated_at: string | null
  reference_product: RawProductSummary | null
  target_product: RawProductSummary | null
  reference_category: RawCategoryRef | null
  target_category: RawCategoryRef | null
  reference_store: RawStoreRef | null
  target_store: RawStoreRef | null
}

// ---------------------------------------------------------------------------
// Adapters
// ---------------------------------------------------------------------------

function adaptProduct(raw: RawProductSummary | null): ProductSummary | null {
  if (!raw) return null
  return {
    id: raw.id,
    store_id: raw.store_id ?? null,
    category_id: raw.category_id ?? null,
    name: raw.name ?? '',
    price: raw.price ?? null,
    currency: raw.currency ?? null,
    product_url: raw.product_url ?? null,
  }
}

function adaptCategoryRef(raw: RawCategoryRef | null): MatchesCategoryRef | null {
  if (!raw) return null
  return {
    id: raw.id,
    store_id: raw.store_id ?? null,
    name: raw.name ?? '',
  }
}

function adaptStoreRef(raw: RawStoreRef | null): MatchesStoreRef | null {
  if (!raw) return null
  return {
    id: raw.id,
    name: raw.name ?? '',
    is_reference: raw.is_reference ?? false,
  }
}

export function adaptProductMapping(raw: RawProductMapping): ProductMappingRow {
  return {
    id: raw.id,
    reference_product_id: raw.reference_product_id,
    target_product_id: raw.target_product_id,
    match_status: raw.match_status ?? null,
    confidence: raw.confidence ?? null,
    comment: raw.comment ?? null,
    created_at: raw.created_at ?? null,
    updated_at: raw.updated_at ?? null,
    reference_product: adaptProduct(raw.reference_product),
    target_product: adaptProduct(raw.target_product),
    reference_category: adaptCategoryRef(raw.reference_category),
    target_category: adaptCategoryRef(raw.target_category),
    reference_store: adaptStoreRef(raw.reference_store),
    target_store: adaptStoreRef(raw.target_store),
  }
}

export function adaptProductMappingList(raw: RawProductMapping[]): ProductMappingRow[] {
  return (raw ?? []).map(adaptProductMapping)
}

