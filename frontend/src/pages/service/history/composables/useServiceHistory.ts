/**
 * useServiceHistory.ts — History tab state and data management composable.
 *
 * Owns:
 *   - filter state (storeId, runType, status, triggerType)
 *   - pagination state (page, pageSize)
 *   - runs list loading / error / data
 *   - stores list loading for filter
 *   - details dialog coordination (selectedRunId, detailRun, detailLoading, detailError)
 *
 * Does NOT commit to any session. Does NOT contain UI logic.
 */
import { ref, watch, type Ref } from 'vue'
import { fetchScrapeRuns, fetchScrapeRunDetail } from '@/api/client'
import { fetchStores } from '@/api/client'
import type { ScrapeRunSummary } from '@/types/history'
import type { StoreSummary } from '@/types/store'

export interface HistoryFilters {
  storeId: string
  runType: string
  status: string
  triggerType: string
}

export interface ServiceHistoryState {
  // Stores (for filter options)
  stores: Ref<StoreSummary[]>
  storesLoading: Ref<boolean>

  // Filters
  filters: HistoryFilters
  setFilter: (key: keyof HistoryFilters, value: string) => void
  resetFilters: () => void

  // Pagination
  page: Ref<number>
  pageSize: Ref<number>
  prevPage: () => void
  nextPage: () => void

  // Runs list
  runs: Ref<ScrapeRunSummary[]>
  loading: Ref<boolean>
  error: Ref<string | null>
  reload: () => void

  // Run details
  detailRunId: Ref<number | null>
  detailRun: Ref<ScrapeRunSummary | null>
  detailLoading: Ref<boolean>
  detailError: Ref<string | null>
  openDetails: (runId: number) => void
  closeDetails: () => void
}

const PAGE_SIZE = 10

export function useServiceHistory(): ServiceHistoryState {
  // ── Stores ─────────────────────────────────────────────────────
  const stores = ref<StoreSummary[]>([])
  const storesLoading = ref(false)

  async function loadStores() {
    storesLoading.value = true
    try {
      stores.value = await fetchStores()
    } catch {
      // non-fatal: filter will just show no store options
    } finally {
      storesLoading.value = false
    }
  }

  // ── Filters ────────────────────────────────────────────────────
  // reactive wrappers — we keep individual refs so watchers are explicit
  const storeId = ref('')
  const runType = ref('')
  const status = ref('')
  const triggerType = ref('')

  // proxy object that components can use via v-model-like pattern
  const filtersProxy = {
    get storeId() { return storeId.value },
    set storeId(v: string) { storeId.value = v },
    get runType() { return runType.value },
    set runType(v: string) { runType.value = v },
    get status() { return status.value },
    set status(v: string) { status.value = v },
    get triggerType() { return triggerType.value },
    set triggerType(v: string) { triggerType.value = v },
  } as HistoryFilters

  function setFilter(key: keyof HistoryFilters, value: string) {
    if (key === 'storeId') storeId.value = value
    else if (key === 'runType') runType.value = value
    else if (key === 'status') status.value = value
    else if (key === 'triggerType') triggerType.value = value
    page.value = 0
  }

  function resetFilters() {
    storeId.value = ''
    runType.value = ''
    status.value = ''
    triggerType.value = ''
    page.value = 0
  }

  // ── Pagination ────────────────────────────────────────────────
  const page = ref(0)
  const pageSize = ref(PAGE_SIZE)

  function prevPage() {
    if (page.value > 0) page.value--
  }
  function nextPage() {
    page.value++
  }

  // ── Runs list ─────────────────────────────────────────────────
  const runs = ref<ScrapeRunSummary[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  let abortController: AbortController | null = null

  async function loadRuns() {
    if (abortController) abortController.abort()
    abortController = new AbortController()
    loading.value = true
    error.value = null

    try {
      const result = await fetchScrapeRuns(
        {
          store_id: storeId.value ? Number(storeId.value) : null,
          run_type: runType.value || null,
          status: status.value || null,
          trigger_type: triggerType.value || null,
          limit: pageSize.value,
          offset: page.value * pageSize.value,
        },
        abortController.signal,
      )
      runs.value = result
    } catch (err: unknown) {
      if ((err as Error)?.name === 'AbortError') return
      error.value = err instanceof Error ? err.message : String(err)
      runs.value = []
    } finally {
      loading.value = false
    }
  }

  function reload() {
    void loadRuns()
  }

  // Watch all filter and page changes → reload
  watch([storeId, runType, status, triggerType, page], () => {
    void loadRuns()
  })

  // ── Details ───────────────────────────────────────────────────
  const detailRunId = ref<number | null>(null)
  const detailRun = ref<ScrapeRunSummary | null>(null)
  const detailLoading = ref(false)
  const detailError = ref<string | null>(null)

  async function openDetails(runId: number) {
    detailRunId.value = runId
    detailRun.value = null
    detailLoading.value = true
    detailError.value = null
    try {
      detailRun.value = await fetchScrapeRunDetail(runId)
    } catch (err: unknown) {
      detailError.value = err instanceof Error ? err.message : String(err)
    } finally {
      detailLoading.value = false
    }
  }

  function closeDetails() {
    detailRunId.value = null
    detailRun.value = null
    detailError.value = null
  }

  // ── Bootstrap ─────────────────────────────────────────────────
  void loadStores()
  void loadRuns()

  return {
    stores,
    storesLoading,
    filters: filtersProxy,
    setFilter,
    resetFilters,
    page,
    pageSize,
    prevPage,
    nextPage,
    runs,
    loading,
    error,
    reload,
    detailRunId,
    detailRun,
    detailLoading,
    detailError,
    openDetails,
    closeDetails,
  }
}

