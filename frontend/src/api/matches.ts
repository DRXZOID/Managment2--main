/**
 * frontend/src/api/matches.ts — API helpers for the /matches page.
 *
 * Wraps:
 *   GET    /api/product-mappings
 *   DELETE /api/product-mappings/<id>
 *
 * Stores/categories are loaded via the shared client.ts helpers.
 */
import { requestJson } from './http'
import { adaptProductMappingList } from './adapters/productMappings'
import type { RawProductMapping } from './adapters/productMappings'
import type { MatchesFilters, MatchesListResponse } from '@/types/matches'

/**
 * GET /api/product-mappings — list product mappings with optional filters.
 *
 * Filter semantics mirror legacy matches.js exactly:
 *   - numeric ids are only sent when non-null
 *   - status is always sent ('' = all, 'confirmed' | 'rejected' for specific)
 *   - search is only sent when non-empty
 */
export async function listProductMappings(
  filters: MatchesFilters,
  signal?: AbortSignal,
): Promise<MatchesListResponse> {
  const params = new URLSearchParams()

  if (filters.referenceStoreId)
    params.set('reference_store_id', String(filters.referenceStoreId))
  if (filters.targetStoreId)
    params.set('target_store_id', String(filters.targetStoreId))
  if (filters.referenceCategoryId)
    params.set('reference_category_id', String(filters.referenceCategoryId))
  if (filters.targetCategoryId)
    params.set('target_category_id', String(filters.targetCategoryId))

  // Always send status — backend default is 'confirmed', passing '' means all
  params.set('status', filters.status)

  if (filters.search.trim())
    params.set('search', filters.search.trim())

  const data = await requestJson<{ product_mappings: RawProductMapping[]; total: number }>(
    `/api/product-mappings?${params}`,
    { signal },
  )

  const rows = adaptProductMappingList(data.product_mappings ?? [])
  return { rows, total: data.total ?? rows.length }
}

/**
 * DELETE /api/product-mappings/<id> — hard-delete a persisted mapping row.
 */
export async function deleteProductMapping(
  mappingId: number,
  signal?: AbortSignal,
): Promise<void> {
  await requestJson<unknown>(
    `/api/product-mappings/${mappingId}`,
    { method: 'DELETE', signal },
  )
}

