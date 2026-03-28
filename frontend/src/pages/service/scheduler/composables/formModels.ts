/**
 * formModels.ts — scheduler form state types and init/serialize helpers.
 *
 * Keeps UI form state (string bindings, nullable conversions) separate from
 * API DTOs.  Only the scheduler feature should import from here.
 */
import type { SchedulerJobDetail, SchedulerSchedule, RunnerType, ScheduleType, MisfirePolicy } from '@/types/scheduler'

// ---------------------------------------------------------------------------
// Job form
// ---------------------------------------------------------------------------

export interface JobFormState {
  source_key: string
  runner_type: RunnerType
  /** string for <select> v-model; empty string = none */
  store_id: string
  /** string for <select> v-model; empty string = none */
  category_id: string
  enabled: boolean
  allow_overlap: boolean
  priority: number
  max_retries: number
  retry_backoff_sec: number
  /** string for <input type="number"> v-model; empty string = null */
  timeout_sec: string
  concurrency_key: string
  /** JSON text for additional params (beyond store_id/category_id) */
  extra_params_json: string
}

export function initJobForm(job?: SchedulerJobDetail | null): JobFormState {
  if (!job) {
    return {
      source_key: '',
      runner_type: 'store_category_sync',
      store_id: '',
      category_id: '',
      enabled: true,
      allow_overlap: false,
      priority: 0,
      max_retries: 0,
      retry_backoff_sec: 60,
      timeout_sec: '',
      concurrency_key: '',
      extra_params_json: '',
    }
  }

  const params = job.params_json ?? {}
  const storeId = params['store_id'] != null ? String(params['store_id']) : ''
  const catId = params['category_id'] != null ? String(params['category_id']) : ''

  // Extra params = all keys except store_id / category_id
  const extra = Object.fromEntries(
    Object.entries(params).filter(([k]) => k !== 'store_id' && k !== 'category_id'),
  )
  const extraText = Object.keys(extra).length > 0 ? JSON.stringify(extra, null, 2) : ''

  return {
    source_key: job.source_key,
    runner_type: job.runner_type,
    store_id: storeId,
    category_id: catId,
    enabled: job.enabled,
    allow_overlap: job.allow_overlap,
    priority: job.priority,
    max_retries: job.max_retries,
    retry_backoff_sec: job.retry_backoff_sec,
    timeout_sec: job.timeout_sec != null ? String(job.timeout_sec) : '',
    concurrency_key: job.concurrency_key ?? '',
    extra_params_json: extraText,
  }
}

/** Build API payload from form state. Returns null if JSON parse fails. */
export function serializeJobForm(form: JobFormState): {
  payload: Record<string, unknown> | null
  jsonError: string | null
} {
  let extraParams: Record<string, unknown> = {}
  let jsonError: string | null = null

  if (form.extra_params_json.trim()) {
    try {
      extraParams = JSON.parse(form.extra_params_json)
      if (typeof extraParams !== 'object' || Array.isArray(extraParams)) {
        return { payload: null, jsonError: 'Params JSON повинен бути об\'єктом {}' }
      }
    } catch {
      return { payload: null, jsonError: 'Невалідний JSON у полі параметрів' }
    }
  }

  const params_json: Record<string, unknown> = { ...extraParams }
  if (form.store_id) params_json['store_id'] = Number(form.store_id)
  if (form.category_id) params_json['category_id'] = Number(form.category_id)

  return {
    payload: {
      source_key: form.source_key.trim(),
      runner_type: form.runner_type,
      params_json: Object.keys(params_json).length > 0 ? params_json : null,
      enabled: form.enabled,
      allow_overlap: form.allow_overlap,
      priority: form.priority,
      max_retries: form.max_retries,
      retry_backoff_sec: form.retry_backoff_sec,
      timeout_sec: form.timeout_sec !== '' ? Number(form.timeout_sec) : null,
      concurrency_key: form.concurrency_key.trim() || null,
    },
    jsonError,
  }
}

// ---------------------------------------------------------------------------
// Schedule form
// ---------------------------------------------------------------------------

export interface ScheduleFormState {
  schedule_type: ScheduleType
  /** string for <input type="number"> v-model */
  interval_sec: string
  cron_expr: string
  timezone: string
  jitter_sec: number
  misfire_policy: MisfirePolicy
  enabled: boolean
}

export function initScheduleForm(schedule?: SchedulerSchedule | null): ScheduleFormState {
  if (!schedule) {
    return {
      schedule_type: 'interval',
      interval_sec: '3600',
      cron_expr: '',
      timezone: 'UTC',
      jitter_sec: 0,
      misfire_policy: 'skip',
      enabled: true,
    }
  }
  return {
    schedule_type: schedule.schedule_type,
    interval_sec: schedule.interval_sec != null ? String(schedule.interval_sec) : '',
    cron_expr: schedule.cron_expr ?? '',
    timezone: schedule.timezone ?? 'UTC',
    jitter_sec: schedule.jitter_sec ?? 0,
    misfire_policy: schedule.misfire_policy,
    enabled: schedule.enabled,
  }
}

export function serializeScheduleForm(form: ScheduleFormState): Record<string, unknown> {
  return {
    schedule_type: form.schedule_type,
    interval_sec: form.schedule_type === 'interval' && form.interval_sec !== ''
      ? Number(form.interval_sec) : null,
    cron_expr: form.schedule_type === 'cron' && form.cron_expr.trim()
      ? form.cron_expr.trim() : null,
    timezone: form.timezone.trim() || 'UTC',
    jitter_sec: form.jitter_sec,
    misfire_policy: form.misfire_policy,
    enabled: form.enabled,
  }
}

