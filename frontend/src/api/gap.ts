/**
 * frontend/src/api/gap.ts — API helpers for the /gap page.
 *
 * Wraps:
 *   GET  /api/categories/<id>/mapped-target-categories
 *   POST /api/gap
 *   POST /api/gap/status
 *
 * Stores / store-categories are loaded via the shared client.ts helpers.
 */
import { requestJson } from './http'
import type {
  MappedTargetCategory,
  GapRequestBody,
  GapResult,
  GapItemStatus,
} from '@/types/gap'

// ---------------------------------------------------------------------------
// Mapped target categories
// ---------------------------------------------------------------------------

interface RawMappedTargetCatsResponse {
  mapped_target_categories: MappedTargetCategory[]
  reference_category?: unknown
  target_store?: unknown
}

/**
 * GET /api/categories/<refCatId>/mapped-target-categories?target_store_id=...
 */
export async function fetchMappedTargetCategories(
  refCategoryId: number,
  targetStoreId: number,
  signal?: AbortSignal,
): Promise<MappedTargetCategory[]> {
  const data = await requestJson<RawMappedTargetCatsResponse>(
    `/api/categories/${refCategoryId}/mapped-target-categories?target_store_id=${targetStoreId}`,
    { signal },
  )
  return data.mapped_target_categories ?? []
}

// ---------------------------------------------------------------------------
// Gap query
// ---------------------------------------------------------------------------

/**
 * POST /api/gap — return grouped gap items.
 */
export async function postGapQuery(
  body: GapRequestBody,
  signal?: AbortSignal,
): Promise<GapResult> {
  return requestJson<GapResult>('/api/gap', { method: 'POST', body, signal })
}

// ---------------------------------------------------------------------------
// Gap item status
// ---------------------------------------------------------------------------

/**
 * POST /api/gap/status — set gap item review status.
 */
export async function postGapStatus(
  referenceCategoryId: number,
  targetProductId: number,
  status: GapItemStatus,
  signal?: AbortSignal,
): Promise<void> {
  await requestJson<unknown>('/api/gap/status', {
    method: 'POST',
    body: {
      reference_category_id: referenceCategoryId,
      target_product_id: targetProductId,
      status,
    },
    signal,
  })
}

