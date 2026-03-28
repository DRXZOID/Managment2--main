import { describe, it, expect, vi, beforeEach } from 'vitest'
import { nextTick } from 'vue'
import { useSchedulerReadModel } from '@/pages/service/scheduler/composables/useSchedulerReadModel'

// ---------------------------------------------------------------------------
// Mock the API client module
// ---------------------------------------------------------------------------

vi.mock('@/api/client', () => ({
  fetchSchedulerJobs: vi.fn(),
  fetchSchedulerJobDetail: vi.fn(),
  fetchSchedulerRuns: vi.fn(),
}))

import * as client from '@/api/client'

const mockJobs = [
  {
    id: 1, source_key: 'hockeyshop', runner_type: 'store_category_sync',
    enabled: true, priority: 0, allow_overlap: false, timeout_sec: null,
    max_retries: 0, retry_backoff_sec: 60, concurrency_key: null,
    params_json: { store_id: 3 }, next_run_at: null, last_run_at: null,
    created_at: null, updated_at: null,
  },
  {
    id: 2, source_key: 'hockeyworld', runner_type: 'all_stores_category_sync',
    enabled: false, priority: 0, allow_overlap: false, timeout_sec: null,
    max_retries: 0, retry_backoff_sec: 60, concurrency_key: null,
    params_json: null, next_run_at: null, last_run_at: null,
    created_at: null, updated_at: null,
  },
]

const mockJobDetail = {
  job: { ...mockJobs[0] },
  schedules: [
    {
      id: 10, job_id: 1, schedule_type: 'interval', cron_expr: null,
      interval_sec: 3600, timezone: 'UTC', jitter_sec: 0,
      misfire_policy: 'skip', enabled: true, created_at: null, updated_at: null,
    },
  ],
}

const mockRuns = [
  {
    id: 99, store_id: 3, store: null, job_id: 1,
    run_type: 'store_category_sync', trigger_type: 'scheduled',
    status: 'success', attempt: 1, queued_at: null,
    started_at: '2026-01-01T12:00:00Z', finished_at: '2026-01-01T12:00:30Z',
    worker_id: null, categories_processed: 5, products_processed: 50,
    products_created: 2, products_updated: 3, price_changes_detected: 1,
    error_message: null, metadata_json: null, checkpoint_out_json: null,
    retryable: false, retry_of_run_id: null, retry_processed: false, retry_exhausted: false,
  },
]

beforeEach(() => {
  vi.clearAllMocks()
})

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('useSchedulerReadModel — initial state', () => {
  it('starts with empty jobs and no selection', () => {
    const model = useSchedulerReadModel()
    expect(model.jobs.value).toEqual([])
    expect(model.selectedJobId.value).toBeNull()
    expect(model.selectedJob.value).toBeNull()
    expect(model.loadingJobs.value).toBe(false)
    expect(model.loadingDetail.value).toBe(false)
    expect(model.errorJobs.value).toBeNull()
    expect(model.errorDetail.value).toBeNull()
  })
})

describe('useSchedulerReadModel — activate()', () => {
  it('loads jobs on first activate', async () => {
    vi.mocked(client.fetchSchedulerJobs).mockResolvedValueOnce(mockJobs)
    const model = useSchedulerReadModel()

    await model.activate()

    expect(client.fetchSchedulerJobs).toHaveBeenCalledTimes(1)
    expect(model.jobs.value).toHaveLength(2)
    expect(model.jobs.value[0].source_key).toBe('hockeyshop')
    expect(model.loadingJobs.value).toBe(false)
  })

  it('does NOT reload on subsequent activate() without force', async () => {
    vi.mocked(client.fetchSchedulerJobs).mockResolvedValue(mockJobs)
    const model = useSchedulerReadModel()

    await model.activate()
    await model.activate()
    await model.activate()

    expect(client.fetchSchedulerJobs).toHaveBeenCalledTimes(1)
  })

  it('force=true reloads even if already activated', async () => {
    vi.mocked(client.fetchSchedulerJobs).mockResolvedValue(mockJobs)
    const model = useSchedulerReadModel()

    await model.activate()
    await model.activate(true)

    expect(client.fetchSchedulerJobs).toHaveBeenCalledTimes(2)
  })

  it('sets errorJobs when fetch fails', async () => {
    vi.mocked(client.fetchSchedulerJobs).mockRejectedValueOnce(new Error('network error'))
    const model = useSchedulerReadModel()

    await model.activate()

    expect(model.errorJobs.value).toBeInstanceOf(Error)
    expect(model.errorJobs.value?.message).toBe('network error')
    expect(model.jobs.value).toEqual([])
  })
})

describe('useSchedulerReadModel — selectJob()', () => {
  it('loads detail and runs when a job is selected', async () => {
    vi.mocked(client.fetchSchedulerJobs).mockResolvedValue(mockJobs)
    vi.mocked(client.fetchSchedulerJobDetail).mockResolvedValue(mockJobDetail)
    vi.mocked(client.fetchSchedulerRuns).mockResolvedValue(mockRuns)

    const model = useSchedulerReadModel()
    await model.activate()
    await model.selectJob(1)

    expect(model.selectedJobId.value).toBe(1)
    expect(model.selectedJob.value?.source_key).toBe('hockeyshop')
    expect(model.selectedSchedules.value).toHaveLength(1)
    expect(model.selectedRuns.value).toHaveLength(1)
    expect(model.loadingDetail.value).toBe(false)
    expect(model.errorDetail.value).toBeNull()
  })

  it('sets errorDetail when job detail fetch fails', async () => {
    vi.mocked(client.fetchSchedulerJobs).mockResolvedValue(mockJobs)
    vi.mocked(client.fetchSchedulerJobDetail).mockRejectedValueOnce(new Error('404'))
    vi.mocked(client.fetchSchedulerRuns).mockResolvedValue([])

    const model = useSchedulerReadModel()
    await model.activate()
    await model.selectJob(1)

    expect(model.errorDetail.value?.message).toBe('404')
    expect(model.selectedJob.value).toBeNull()
  })

  it('clears previous selection before loading new one', async () => {
    vi.mocked(client.fetchSchedulerJobs).mockResolvedValue(mockJobs)
    vi.mocked(client.fetchSchedulerJobDetail).mockResolvedValue(mockJobDetail)
    vi.mocked(client.fetchSchedulerRuns).mockResolvedValue(mockRuns)

    const model = useSchedulerReadModel()
    await model.activate()
    await model.selectJob(1)

    expect(model.selectedJob.value).not.toBeNull()

    // Change selection — during loading, previous data is cleared
    let resolveDetail!: (v: typeof mockJobDetail) => void
    vi.mocked(client.fetchSchedulerJobDetail).mockReturnValueOnce(
      new Promise((r) => { resolveDetail = r }),
    )
    vi.mocked(client.fetchSchedulerRuns).mockResolvedValue([])

    const selecting = model.selectJob(2)
    await nextTick()

    expect(model.selectedJobId.value).toBe(2)
    expect(model.selectedJob.value).toBeNull()  // cleared before new load

    resolveDetail(mockJobDetail)
    await selecting
  })
})

describe('useSchedulerReadModel — refresh()', () => {
  it('reloads jobs and detail when a job is selected', async () => {
    vi.mocked(client.fetchSchedulerJobs).mockResolvedValue(mockJobs)
    vi.mocked(client.fetchSchedulerJobDetail).mockResolvedValue(mockJobDetail)
    vi.mocked(client.fetchSchedulerRuns).mockResolvedValue(mockRuns)

    const model = useSchedulerReadModel()
    await model.activate()
    await model.selectJob(1)
    await model.refresh()

    // fetchSchedulerJobs: once from activate + once from refresh
    expect(client.fetchSchedulerJobs).toHaveBeenCalledTimes(2)
    // fetchSchedulerJobDetail: once from selectJob + once from refresh
    expect(client.fetchSchedulerJobDetail).toHaveBeenCalledTimes(2)
  })

  it('only reloads jobs when no job is selected', async () => {
    vi.mocked(client.fetchSchedulerJobs).mockResolvedValue(mockJobs)

    const model = useSchedulerReadModel()
    await model.activate()
    await model.refresh()

    expect(client.fetchSchedulerJobs).toHaveBeenCalledTimes(2)
    expect(client.fetchSchedulerJobDetail).not.toHaveBeenCalled()
  })
})

