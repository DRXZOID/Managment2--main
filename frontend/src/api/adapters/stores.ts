/**
 * frontend/src/api/adapters/stores.ts — Stores API adapter.
 *
 * Converts raw /api/stores and /api/stores/:id/categories server payloads
 * to stable frontend DTOs.
 *
 * Adapter responsibilities:
 * - default missing optional fields
 * - normalize null vs undefined
 *
 * Adapters must NOT invent domain semantics or change request/response contracts.
 */
import type { StoreSummary, CategorySummary } from '@/types/store'

// ---------------------------------------------------------------------------
// Raw server shapes (as returned by serializers.py)
// ---------------------------------------------------------------------------

interface RawStore {
  id: number
  name: string
  is_reference: boolean
  base_url: string | null
}

interface RawCategory {
  id: number
  store_id: number
  name: string
  normalized_name: string | null
  url: string | null
  external_id: string | null
  updated_at: string | null
  product_count?: number
}

// ---------------------------------------------------------------------------
// Adapters
// ---------------------------------------------------------------------------

export function adaptStore(raw: RawStore): StoreSummary {
  return {
    id: raw.id,
    name: raw.name ?? '',
    is_reference: raw.is_reference ?? false,
    base_url: raw.base_url ?? null,
  }
}

export function adaptStoreList(raw: RawStore[]): StoreSummary[] {
  return raw.map(adaptStore)
}

export function adaptCategory(raw: RawCategory): CategorySummary {
  return {
    id: raw.id,
    store_id: raw.store_id,
    name: raw.name ?? '',
    normalized_name: raw.normalized_name ?? null,
    url: raw.url ?? null,
    external_id: raw.external_id ?? null,
    updated_at: raw.updated_at ?? null,
    product_count: raw.product_count,
  }
}

export function adaptCategoryList(raw: RawCategory[]): CategorySummary[] {
  return raw.map(adaptCategory)
}

