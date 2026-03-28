/**
 * useGapData.ts — Gap query state for POST /api/gap.
 *
 * Mutation UX policy:
 *   - loadGap() is non-destructive for subsequent loads: current result stays
 *     visible while the new request is in-flight (loading=true but result unchanged).
 *   - Only the very first load (hasLoaded===false) treats result as empty initially.
 */
import { ref } from 'vue'
import type { Ref } from 'vue'
import { postGapQuery } from '@/api/gap'
import type { GapResult, GapRequestBody } from '@/types/gap'

export interface GapDataState {
  result: Ref<GapResult | null>
  loading: Ref<boolean>
  error: Ref<string | null>
  hasLoaded: Ref<boolean>
  lastBody: Ref<GapRequestBody | null>
  loadGap: (body: GapRequestBody) => Promise<void>
}

export function useGapData(): GapDataState {
  const result = ref<GapResult | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const hasLoaded = ref(false)
  const lastBody = ref<GapRequestBody | null>(null)

  async function loadGap(body: GapRequestBody): Promise<void> {
    loading.value = true
    error.value = null
    // Keep current result visible during reload — do NOT clear result or hasLoaded
    lastBody.value = body

    try {
      result.value = await postGapQuery(body)
      hasLoaded.value = true
    } catch (err) {
      error.value = 'Помилка запиту: ' + (err instanceof Error ? err.message : String(err))
    } finally {
      loading.value = false
    }
  }

  return { result, loading, error, hasLoaded, lastBody, loadGap }
}
