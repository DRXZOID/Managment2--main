import { describe, it, expect, vi, beforeEach } from 'vitest'
import { flushPromises } from '@vue/test-utils'
import { useServiceHistory } from '@/pages/service/history/composables/useServiceHistory'

// ---------------------------------------------------------------------------
// Mock API client
// ---------------------------------------------------------------------------

vi.mock('@/api/client', () => ({
  fetchStores: vi.fn(),
  fetchScrapeRuns: vi.fn(),
  fetchScrapeRunDetail: vi.fn(),
}))

import * as client from '@/api/client'

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

const stores = [
  { id: 1, name: 'prohockey', is_reference: true, base_url: null },
  { id: 2, name: 'hockeyworld', is_reference: false, base_url: null },
]

const makeRun = (id: number, overrides = {}) => ({
  id,
  store_id: 1,
  store: null,
  job_id: null,
  run_type: 'store_category_sync',
  trigger_type: 'manual',
  status: 'success',
  attempt: 1,
  queued_at: '2026-01-01T12:00:00Z',
  started_at: '2026-01-01T12:00:05Z',
  finished_at: '2026-01-01T12:00:30Z',
  worker_id: null,
  categories_processed: 5,
  products_processed: 100,
  products_created: 2,
  products_updated: 8,
  price_changes_detected: 1,
  error_message: null,
  metadata_json: null,
  checkpoint_out_json: null,
  retryable: false,
  retry_of_run_id: null,
  retry_processed: false,
  retry_exhausted: false,
  ...overrides,
})

const runs = [makeRun(1), makeRun(2), makeRun(3)]

beforeEach(() => {
  vi.clearAllMocks()
  vi.mocked(client.fetchStores).mockResolvedValue(stores)
  vi.mocked(client.fetchScrapeRuns).mockResolvedValue(runs)
  vi.mocked(client.fetchScrapeRunDetail).mockResolvedValue(makeRun(1))
})

// ---------------------------------------------------------------------------
// Initial state
// ---------------------------------------------------------------------------

describe('useServiceHistory — initial state', () => {
  it('loads stores and runs on mount', async () => {
    const state = useServiceHistory()
    await flushPromises()

    expect(state.stores.value).toHaveLength(2)
    expect(state.runs.value).toHaveLength(3)
    expect(state.loading.value).toBe(false)
    expect(state.error.value).toBeNull()
  })

  it('starts on page 0 with default filters', () => {
    const state = useServiceHistory()
    expect(state.page.value).toBe(0)
    expect(state.filters.storeId).toBe('')
    expect(state.filters.runType).toBe('')
    expect(state.filters.status).toBe('')
    expect(state.filters.triggerType).toBe('')
  })
})

// ---------------------------------------------------------------------------
// Filter change causes reload
// ---------------------------------------------------------------------------

describe('useServiceHistory — filter change', () => {
  it('resets page to 0 when filter changes', async () => {
    const state = useServiceHistory()
    await flushPromises()

    // navigate to page 1
    state.nextPage()
    await flushPromises()
    expect(state.page.value).toBe(1)

    // changing a filter resets to page 0
    state.setFilter('status', 'failed')
    expect(state.page.value).toBe(0)
  })

  it('calls fetchScrapeRuns with correct params after filter change', async () => {
    const state = useServiceHistory()
    await flushPromises()
    vi.clearAllMocks()
    vi.mocked(client.fetchScrapeRuns).mockResolvedValue([])

    state.setFilter('status', 'failed')
    await flushPromises()

    expect(client.fetchScrapeRuns).toHaveBeenCalledWith(
      expect.objectContaining({ status: 'failed', offset: 0 }),
      expect.anything(),
    )
  })

  it('calls fetchScrapeRuns with store_id filter', async () => {
    const state = useServiceHistory()
    await flushPromises()
    vi.clearAllMocks()
    vi.mocked(client.fetchScrapeRuns).mockResolvedValue([])

    state.setFilter('storeId', '2')
    await flushPromises()

    expect(client.fetchScrapeRuns).toHaveBeenCalledWith(
      expect.objectContaining({ store_id: 2 }),
      expect.anything(),
    )
  })

  it('sends null for empty string filters', async () => {
    const state = useServiceHistory()
    await flushPromises()
    vi.clearAllMocks()
    vi.mocked(client.fetchScrapeRuns).mockResolvedValue([])

    // default empty filters → all null
    state.reload()
    await flushPromises()

    expect(client.fetchScrapeRuns).toHaveBeenCalledWith(
      expect.objectContaining({
        store_id: null,
        run_type: null,
        status: null,
        trigger_type: null,
      }),
      expect.anything(),
    )
  })
})

// ---------------------------------------------------------------------------
// Pagination
// ---------------------------------------------------------------------------

describe('useServiceHistory — pagination', () => {
  it('increments page on nextPage', async () => {
    const state = useServiceHistory()
    await flushPromises()

    state.nextPage()
    expect(state.page.value).toBe(1)
  })

  it('decrements page on prevPage when page > 0', async () => {
    const state = useServiceHistory()
    await flushPromises()

    state.nextPage()
    state.prevPage()
    expect(state.page.value).toBe(0)
  })

  it('does not go below page 0 on prevPage', async () => {
    const state = useServiceHistory()
    await flushPromises()

    state.prevPage()
    expect(state.page.value).toBe(0)
  })

  it('fetches with correct offset on page 2', async () => {
    const state = useServiceHistory()
    await flushPromises()
    vi.clearAllMocks()
    vi.mocked(client.fetchScrapeRuns).mockResolvedValue([])

    state.nextPage()
    state.nextPage()
    await flushPromises()

    expect(client.fetchScrapeRuns).toHaveBeenLastCalledWith(
      expect.objectContaining({ offset: 20 }),
      expect.anything(),
    )
  })
})

// ---------------------------------------------------------------------------
// Run details dialog
// ---------------------------------------------------------------------------

describe('useServiceHistory — details', () => {
  it('starts with no detail open', () => {
    const state = useServiceHistory()
    expect(state.detailRunId.value).toBeNull()
    expect(state.detailRun.value).toBeNull()
  })

  it('loads detail when openDetails is called', async () => {
    const state = useServiceHistory()
    await flushPromises()

    await state.openDetails(1)
    await flushPromises()

    expect(state.detailRunId.value).toBe(1)
    expect(state.detailRun.value).not.toBeNull()
    expect(state.detailRun.value?.id).toBe(1)
    expect(state.detailLoading.value).toBe(false)
    expect(state.detailError.value).toBeNull()
  })

  it('sets detailError on fetch failure', async () => {
    vi.mocked(client.fetchScrapeRunDetail).mockRejectedValue(new Error('Not found'))
    const state = useServiceHistory()
    await flushPromises()

    await state.openDetails(999)
    await flushPromises()

    expect(state.detailError.value).toBe('Not found')
    expect(state.detailRun.value).toBeNull()
  })

  it('clears detail state on closeDetails', async () => {
    const state = useServiceHistory()
    await flushPromises()

    await state.openDetails(1)
    await flushPromises()

    state.closeDetails()

    expect(state.detailRunId.value).toBeNull()
    expect(state.detailRun.value).toBeNull()
    expect(state.detailError.value).toBeNull()
  })
})

// ---------------------------------------------------------------------------
// Error handling
// ---------------------------------------------------------------------------

describe('useServiceHistory — error state', () => {
  it('sets error when fetchScrapeRuns rejects', async () => {
    vi.mocked(client.fetchScrapeRuns).mockRejectedValue(new Error('Server error'))
    const state = useServiceHistory()
    await flushPromises()

    expect(state.error.value).toBe('Server error')
    expect(state.runs.value).toEqual([])
  })
})

