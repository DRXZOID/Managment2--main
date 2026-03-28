import { describe, it, expect } from 'vitest'
import {
  initJobForm,
  serializeJobForm,
  initScheduleForm,
  serializeScheduleForm,
} from '@/pages/service/scheduler/composables/formModels'
import type { SchedulerJobDetail, SchedulerSchedule } from '@/types/scheduler'

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

const baseJob: SchedulerJobDetail = {
  id: 1,
  source_key: 'hockeyworld',
  runner_type: 'store_category_sync',
  params_json: { store_id: 3, category_id: 42 },
  enabled: true,
  priority: 5,
  allow_overlap: true,
  timeout_sec: 120,
  max_retries: 2,
  retry_backoff_sec: 90,
  concurrency_key: 'cat-sync',
  next_run_at: null,
  last_run_at: null,
  created_at: null,
  updated_at: null,
}

const baseSchedule: SchedulerSchedule = {
  id: 10,
  job_id: 1,
  schedule_type: 'interval',
  cron_expr: null,
  interval_sec: 7200,
  timezone: 'Europe/Kyiv',
  jitter_sec: 30,
  misfire_policy: 'run_once',
  enabled: false,
  created_at: null,
  updated_at: null,
}

// ---------------------------------------------------------------------------
// initJobForm
// ---------------------------------------------------------------------------

describe('initJobForm — defaults (no job)', () => {
  it('returns safe blank defaults', () => {
    const form = initJobForm()
    expect(form.source_key).toBe('')
    expect(form.runner_type).toBe('store_category_sync')
    expect(form.store_id).toBe('')
    expect(form.category_id).toBe('')
    expect(form.enabled).toBe(true)
    expect(form.allow_overlap).toBe(false)
    expect(form.priority).toBe(0)
    expect(form.max_retries).toBe(0)
    expect(form.retry_backoff_sec).toBe(60)
    expect(form.timeout_sec).toBe('')
    expect(form.concurrency_key).toBe('')
    expect(form.extra_params_json).toBe('')
  })
})

describe('initJobForm — from existing job', () => {
  it('maps simple scalar fields', () => {
    const form = initJobForm(baseJob)
    expect(form.source_key).toBe('hockeyworld')
    expect(form.runner_type).toBe('store_category_sync')
    expect(form.enabled).toBe(true)
    expect(form.allow_overlap).toBe(true)
    expect(form.priority).toBe(5)
    expect(form.max_retries).toBe(2)
    expect(form.retry_backoff_sec).toBe(90)
    expect(form.timeout_sec).toBe('120')
    expect(form.concurrency_key).toBe('cat-sync')
  })

  it('splits store_id and category_id from params_json', () => {
    const form = initJobForm(baseJob)
    expect(form.store_id).toBe('3')
    expect(form.category_id).toBe('42')
  })

  it('puts extra keys (not store_id/category_id) into extra_params_json', () => {
    const job = { ...baseJob, params_json: { store_id: 1, x: 'hello', y: 42 } }
    const form = initJobForm(job)
    const parsed = JSON.parse(form.extra_params_json)
    expect(parsed).toEqual({ x: 'hello', y: 42 })
    expect(form.store_id).toBe('1')
  })

  it('leaves extra_params_json empty when only store_id/category_id in params', () => {
    const form = initJobForm(baseJob)
    const parsed = JSON.parse(form.extra_params_json || '{}')
    expect(Object.keys(parsed)).toHaveLength(0)
  })

  it('handles null params_json gracefully', () => {
    const job = { ...baseJob, params_json: null }
    const form = initJobForm(job)
    expect(form.store_id).toBe('')
    expect(form.category_id).toBe('')
    expect(form.extra_params_json).toBe('')
  })

  it('handles null timeout_sec → empty string', () => {
    const job = { ...baseJob, timeout_sec: null }
    const form = initJobForm(job)
    expect(form.timeout_sec).toBe('')
  })
})

// ---------------------------------------------------------------------------
// serializeJobForm
// ---------------------------------------------------------------------------

describe('serializeJobForm', () => {
  it('round-trips a fully filled form', () => {
    const form = initJobForm(baseJob)
    const { payload, jsonError } = serializeJobForm(form)
    expect(jsonError).toBeNull()
    expect(payload).not.toBeNull()
    expect(payload!['source_key']).toBe('hockeyworld')
    expect(payload!['runner_type']).toBe('store_category_sync')
    expect(payload!['enabled']).toBe(true)
    expect(payload!['allow_overlap']).toBe(true)
    expect(payload!['priority']).toBe(5)
    expect(payload!['max_retries']).toBe(2)
    expect(payload!['retry_backoff_sec']).toBe(90)
    expect(payload!['timeout_sec']).toBe(120)
    expect(payload!['concurrency_key']).toBe('cat-sync')
  })

  it('reassembles params_json with store_id and category_id', () => {
    const form = initJobForm(baseJob)
    const { payload } = serializeJobForm(form)
    const params = payload!['params_json'] as Record<string, unknown>
    expect(params['store_id']).toBe(3)
    expect(params['category_id']).toBe(42)
  })

  it('converts empty timeout_sec string → null', () => {
    const form = initJobForm({ ...baseJob, timeout_sec: null })
    expect(form.timeout_sec).toBe('')
    const { payload } = serializeJobForm(form)
    expect(payload!['timeout_sec']).toBeNull()
  })

  it('converts empty concurrency_key → null in payload', () => {
    const form = initJobForm({ ...baseJob, concurrency_key: null })
    const { payload } = serializeJobForm(form)
    expect(payload!['concurrency_key']).toBeNull()
  })

  it('returns jsonError for invalid extra_params_json', () => {
    const form = initJobForm()
    form.source_key = 'shop'
    form.extra_params_json = '{not: json}'
    const { payload, jsonError } = serializeJobForm(form)
    expect(payload).toBeNull()
    expect(jsonError).toBeTruthy()
  })

  it('returns jsonError when extra_params_json is a JSON array', () => {
    const form = initJobForm()
    form.source_key = 'shop'
    form.extra_params_json = '[1, 2, 3]'
    const { payload, jsonError } = serializeJobForm(form)
    expect(payload).toBeNull()
    expect(jsonError).toContain('об\'єктом')
  })

  it('omits params_json when no params supplied', () => {
    const form = initJobForm()
    form.source_key = 'shop'
    const { payload } = serializeJobForm(form)
    expect(payload!['params_json']).toBeNull()
  })
})

// ---------------------------------------------------------------------------
// initScheduleForm
// ---------------------------------------------------------------------------

describe('initScheduleForm — defaults (no schedule)', () => {
  it('returns safe blank defaults', () => {
    const form = initScheduleForm()
    expect(form.schedule_type).toBe('interval')
    expect(form.interval_sec).toBe('3600')
    expect(form.cron_expr).toBe('')
    expect(form.timezone).toBe('UTC')
    expect(form.jitter_sec).toBe(0)
    expect(form.misfire_policy).toBe('skip')
    expect(form.enabled).toBe(true)
  })
})

describe('initScheduleForm — from existing schedule', () => {
  it('round-trips all fields', () => {
    const form = initScheduleForm(baseSchedule)
    expect(form.schedule_type).toBe('interval')
    expect(form.interval_sec).toBe('7200')
    expect(form.timezone).toBe('Europe/Kyiv')
    expect(form.jitter_sec).toBe(30)
    expect(form.misfire_policy).toBe('run_once')
    expect(form.enabled).toBe(false)
  })

  it('preserves cron fields for cron schedule', () => {
    const cronSchedule = {
      ...baseSchedule,
      schedule_type: 'cron' as const,
      cron_expr: '0 9 * * 1-5',
      interval_sec: null,
    }
    const form = initScheduleForm(cronSchedule)
    expect(form.schedule_type).toBe('cron')
    expect(form.cron_expr).toBe('0 9 * * 1-5')
    expect(form.interval_sec).toBe('')
  })

  it('handles null interval_sec → empty string', () => {
    const form = initScheduleForm({ ...baseSchedule, interval_sec: null })
    expect(form.interval_sec).toBe('')
  })

  it('handles null cron_expr → empty string', () => {
    const form = initScheduleForm({ ...baseSchedule, cron_expr: null })
    expect(form.cron_expr).toBe('')
  })
})

// ---------------------------------------------------------------------------
// serializeScheduleForm
// ---------------------------------------------------------------------------

describe('serializeScheduleForm', () => {
  it('serializes interval schedule correctly', () => {
    const payload = serializeScheduleForm({
      schedule_type: 'interval',
      interval_sec: '7200',
      cron_expr: '',
      timezone: 'UTC',
      jitter_sec: 0,
      misfire_policy: 'skip',
      enabled: true,
    })
    expect(payload['schedule_type']).toBe('interval')
    expect(payload['interval_sec']).toBe(7200)
    expect(payload['cron_expr']).toBeNull()
  })

  it('serializes cron schedule correctly', () => {
    const payload = serializeScheduleForm({
      schedule_type: 'cron',
      interval_sec: '',
      cron_expr: '0 9 * * 1-5',
      timezone: 'Europe/Kyiv',
      jitter_sec: 15,
      misfire_policy: 'run_once',
      enabled: false,
    })
    expect(payload['schedule_type']).toBe('cron')
    expect(payload['cron_expr']).toBe('0 9 * * 1-5')
    expect(payload['interval_sec']).toBeNull()
    expect(payload['timezone']).toBe('Europe/Kyiv')
    expect(payload['jitter_sec']).toBe(15)
    expect(payload['misfire_policy']).toBe('run_once')
    expect(payload['enabled']).toBe(false)
  })

  it('nulls out interval_sec for cron and cron_expr for interval', () => {
    const intervalPayload = serializeScheduleForm({
      schedule_type: 'interval',
      interval_sec: '3600',
      cron_expr: '0 9 * * *', // should be nulled
      timezone: 'UTC',
      jitter_sec: 0,
      misfire_policy: 'skip',
      enabled: true,
    })
    expect(intervalPayload['cron_expr']).toBeNull()

    const cronPayload = serializeScheduleForm({
      schedule_type: 'cron',
      interval_sec: '3600', // should be nulled
      cron_expr: '0 9 * * *',
      timezone: 'UTC',
      jitter_sec: 0,
      misfire_policy: 'skip',
      enabled: true,
    })
    expect(cronPayload['interval_sec']).toBeNull()
  })

  it('falls back to UTC when timezone is blank', () => {
    const payload = serializeScheduleForm({
      schedule_type: 'interval',
      interval_sec: '3600',
      cron_expr: '',
      timezone: '  ',
      jitter_sec: 0,
      misfire_policy: 'skip',
      enabled: true,
    })
    expect(payload['timezone']).toBe('UTC')
  })
})

