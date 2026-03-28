/**
 * frontend/src/pages/comparison/api.ts — Thin API wrappers for the comparison page.
 *
 * Encapsulates:
 *   fetchStores / fetchCategoriesForStore  (re-exported from shared client)
 *   fetchMappedTargets                     (GET /api/categories/<id>/mapped-target-categories)
 *   runComparison                          (POST /api/comparison)
 *   saveMatchDecision                      (POST /api/comparison/match-decision)
 *   searchEligibleTargetProducts           (GET /api/comparison/eligible-target-products)
 *
 * Does NOT reshape backend contracts — uses thin adapters only.
 */
import { requestJson } from '@/api/http'
import { fetchStores, fetchCategoriesForStore } from '@/api/client'
import type {
  MappedTarget,
  ComparisonResult,
  ComparisonRequestBody,
  MatchDecisionBody,
  EligibleProduct,
} from './types'

// Re-export shared helpers so callers only import from one place
export { fetchStores, fetchCategoriesForStore }

// ---------------------------------------------------------------------------
// Mapped target categories
// ---------------------------------------------------------------------------

export async function fetchMappedTargets(
  refCategoryId: number,
  targetStoreId?: number | null,
  signal?: AbortSignal,
): Promise<MappedTarget[]> {
  let url = `/api/categories/${refCategoryId}/mapped-target-categories`
  if (targetStoreId) url += `?target_store_id=${targetStoreId}`
  const data = await requestJson<{ mapped_target_categories: MappedTarget[] }>(url, { signal })
  return data.mapped_target_categories ?? []
}

// ---------------------------------------------------------------------------
// Comparison
// ---------------------------------------------------------------------------

export async function runComparison(
  body: ComparisonRequestBody,
  signal?: AbortSignal,
): Promise<ComparisonResult> {
  return requestJson<ComparisonResult>('/api/comparison', { method: 'POST', body, signal })
}

// ---------------------------------------------------------------------------
// Match decision
// ---------------------------------------------------------------------------

export async function saveMatchDecision(
  body: MatchDecisionBody,
  signal?: AbortSignal,
): Promise<void> {
  await requestJson<unknown>('/api/comparison/match-decision', { method: 'POST', body, signal })
}

// ---------------------------------------------------------------------------
// Manual picker — eligible target products
// ---------------------------------------------------------------------------

export interface EligibleProductsParams {
  referenceProductId: number
  targetCategoryIds: number[]
  search: string
  includeRejected: boolean
  limit?: number
}

export async function searchEligibleTargetProducts(
  params: EligibleProductsParams,
  signal?: AbortSignal,
): Promise<EligibleProduct[]> {
  const base = params.targetCategoryIds
    .map((id) => `target_category_ids=${id}`)
    .join('&')
  const incRej = params.includeRejected ? '&include_rejected=true' : ''
  const limit  = params.limit ?? 30
  const url =
    `/api/comparison/eligible-target-products` +
    `?reference_product_id=${params.referenceProductId}` +
    `&${base}` +
    `&search=${encodeURIComponent(params.search)}` +
    `&limit=${limit}${incRej}`
  const data = await requestJson<{ products: EligibleProduct[] }>(url, { signal })
  return data.products ?? []
}

