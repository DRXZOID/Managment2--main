import { describe, it, expect } from 'vitest'
import { adaptJob, adaptSchedule, adaptRun } from '@/api/adapters/scheduler'

// ---------------------------------------------------------------------------
// adaptJob
// ---------------------------------------------------------------------------

describe('adaptJob', () => {
  const base = {
    id: 1,
    source_key: 'hockeyshop',
    runner_type: 'store_category_sync',
    params_json: { store_id: 2 },
    enabled: true,
    priority: 0,
    allow_overlap: false,
    timeout_sec: null,
    max_retries: 3,
    retry_backoff_sec: 60,
    concurrency_key: null,
    next_run_at: '2026-01-01T12:00:00Z',
    last_run_at: null,
    created_at: '2025-12-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  }

  it('passes through all required fields', () => {
    const job = adaptJob(base)
    expect(job.id).toBe(1)
    expect(job.source_key).toBe('hockeyshop')
    expect(job.runner_type).toBe('store_category_sync')
    expect(job.enabled).toBe(true)
    expect(job.next_run_at).toBe('2026-01-01T12:00:00Z')
    expect(job.last_run_at).toBeNull()
  })

  it('defaults params_json to null when missing', () => {
    const job = adaptJob({ ...base, params_json: undefined as unknown as null })
    expect(job.params_json).toBeNull()
  })

  it('defaults max_retries to 0 when missing', () => {
    const job = adaptJob({ ...base, max_retries: undefined as unknown as number })
    expect(job.max_retries).toBe(0)
  })
})

// ---------------------------------------------------------------------------
// adaptSchedule
// ---------------------------------------------------------------------------

describe('adaptSchedule', () => {
  const base = {
    id: 10,
    job_id: 1,
    schedule_type: 'interval',
    cron_expr: null,
    interval_sec: 3600,
    timezone: 'Europe/Kyiv',
    jitter_sec: 30,
    misfire_policy: 'skip',
    enabled: true,
    created_at: '2025-12-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  }

  it('passes through all fields', () => {
    const s = adaptSchedule(base)
    expect(s.id).toBe(10)
    expect(s.interval_sec).toBe(3600)
    expect(s.timezone).toBe('Europe/Kyiv')
    expect(s.schedule_type).toBe('interval')
  })

  it('defaults timezone to UTC when null', () => {
    const s = adaptSchedule({ ...base, timezone: null })
    expect(s.timezone).toBe('UTC')
  })

  it('defaults jitter_sec to 0 when null', () => {
    const s = adaptSchedule({ ...base, jitter_sec: null })
    expect(s.jitter_sec).toBe(0)
  })

  it('defaults misfire_policy to skip when null', () => {
    const s = adaptSchedule({ ...base, misfire_policy: null })
    expect(s.misfire_policy).toBe('skip')
  })
})

// ---------------------------------------------------------------------------
// adaptRun
// ---------------------------------------------------------------------------

describe('adaptRun', () => {
  const base = {
    id: 99,
    store_id: 2,
    store: null,
    job_id: 1,
    run_type: 'store_category_sync',
    trigger_type: 'scheduled',
    status: 'success',
    attempt: 1,
    queued_at: '2026-01-01T12:00:00Z',
    started_at: '2026-01-01T12:00:05Z',
    finished_at: '2026-01-01T12:00:30Z',
    worker_id: 'w-1',
    categories_processed: 10,
    products_processed: 200,
    products_created: 5,
    products_updated: 15,
    price_changes_detected: 3,
    error_message: null,
    metadata_json: null,
    checkpoint_out_json: null,
    retryable: false,
    retry_of_run_id: null,
    retry_processed: false,
    retry_exhausted: false,
  }

  it('passes through core fields', () => {
    const run = adaptRun(base)
    expect(run.id).toBe(99)
    expect(run.status).toBe('success')
    expect(run.attempt).toBe(1)
    expect(run.categories_processed).toBe(10)
  })

  it('defaults retryable to false when null', () => {
    const run = adaptRun({ ...base, retryable: null as unknown as boolean })
    expect(run.retryable).toBe(false)
  })

  it('defaults attempt to 1 when null', () => {
    const run = adaptRun({ ...base, attempt: null as unknown as number })
    expect(run.attempt).toBe(1)
  })

  it('defaults status to queued when missing', () => {
    const run = adaptRun({ ...base, status: undefined as unknown as string })
    expect(run.status).toBe('queued')
  })
})

