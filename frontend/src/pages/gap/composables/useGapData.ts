/**
 * useGapData.ts — Gap query state for POST /api/gap.
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
    result.value = null
    hasLoaded.value = false
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

