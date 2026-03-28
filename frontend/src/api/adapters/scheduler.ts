/**
 * frontend/src/api/adapters/scheduler.ts — Scheduler API adapter.
 *
 * Converts raw /api/admin/scrape/jobs and related server payloads
 * to stable frontend DTOs.
 *
 * Adapter responsibilities:
 * - default missing optional fields
 * - normalize null vs undefined
 * - normalize boolean/number fields that may drift
 *
 * Adapters must NOT invent domain semantics or change request/response contracts.
 */
import type {
  SchedulerJobSummary,
  SchedulerSchedule,
  MisfirePolicy,
  ScheduleType,
} from '@/types/scheduler'
import type { ScrapeRunSummary, RunStatus, TriggerType } from '@/types/history'
import { adaptStore } from './stores'

// ---------------------------------------------------------------------------
// Raw server shapes (as returned by serializers.py)
// ---------------------------------------------------------------------------

interface RawJob {
  id: number
  source_key: string
  runner_type: string
  params_json: Record<string, unknown> | null
  enabled: boolean
  priority: number
  allow_overlap: boolean
  timeout_sec: number | null
  max_retries: number
  retry_backoff_sec: number
  concurrency_key: string | null
  next_run_at: string | null
  last_run_at: string | null
  created_at: string | null
  updated_at: string | null
}

interface RawSchedule {
  id: number
  job_id: number
  schedule_type: string
  cron_expr: string | null
  interval_sec: number | null
  timezone: string | null
  jitter_sec: number | null
  misfire_policy: string | null
  enabled: boolean
  created_at: string | null
  updated_at: string | null
}

interface RawRun {
  id: number
  store_id: number | null
  store: Record<string, unknown> | null
  job_id: number | null
  run_type: string
  trigger_type: string | null
  status: string
  attempt: number | null
  queued_at: string | null
  started_at: string | null
  finished_at: string | null
  worker_id: string | null
  categories_processed: number | null
  products_processed: number | null
  products_created: number | null
  products_updated: number | null
  price_changes_detected: number | null
  error_message: string | null
  metadata_json: Record<string, unknown> | null
  checkpoint_out_json: Record<string, unknown> | null
  retryable: boolean | null
  retry_of_run_id: number | null
  retry_processed: boolean | null
  retry_exhausted: boolean | null
}

// ---------------------------------------------------------------------------
// Adapters
// ---------------------------------------------------------------------------

export function adaptJob(raw: RawJob): SchedulerJobSummary {
  return {
    id: raw.id,
    source_key: raw.source_key ?? '',
    runner_type: raw.runner_type ?? '',
    params_json: raw.params_json ?? null,
    enabled: raw.enabled ?? false,
    priority: raw.priority ?? 0,
    allow_overlap: raw.allow_overlap ?? false,
    timeout_sec: raw.timeout_sec ?? null,
    max_retries: raw.max_retries ?? 0,
    retry_backoff_sec: raw.retry_backoff_sec ?? 60,
    concurrency_key: raw.concurrency_key ?? null,
    next_run_at: raw.next_run_at ?? null,
    last_run_at: raw.last_run_at ?? null,
    created_at: raw.created_at ?? null,
    updated_at: raw.updated_at ?? null,
  }
}

export function adaptJobList(raw: RawJob[]): SchedulerJobSummary[] {
  return raw.map(adaptJob)
}

export function adaptSchedule(raw: RawSchedule): SchedulerSchedule {
  return {
    id: raw.id,
    job_id: raw.job_id,
    schedule_type: (raw.schedule_type ?? 'interval') as ScheduleType,
    cron_expr: raw.cron_expr ?? null,
    interval_sec: raw.interval_sec ?? null,
    timezone: raw.timezone ?? 'UTC',
    jitter_sec: raw.jitter_sec ?? 0,
    misfire_policy: (raw.misfire_policy ?? 'skip') as MisfirePolicy,
    enabled: raw.enabled ?? true,
    created_at: raw.created_at ?? null,
    updated_at: raw.updated_at ?? null,
  }
}

export function adaptScheduleList(raw: RawSchedule[]): SchedulerSchedule[] {
  return raw.map(adaptSchedule)
}

export function adaptRun(raw: RawRun): ScrapeRunSummary {
  return {
    id: raw.id,
    store_id: raw.store_id ?? null,
    store: raw.store ? adaptStore(raw.store as unknown as Parameters<typeof adaptStore>[0]) : null,
    job_id: raw.job_id ?? null,
    run_type: raw.run_type ?? '',
    trigger_type: (raw.trigger_type ?? null) as TriggerType | null,
    status: (raw.status ?? 'queued') as RunStatus,
    attempt: raw.attempt ?? 1,
    queued_at: raw.queued_at ?? null,
    started_at: raw.started_at ?? null,
    finished_at: raw.finished_at ?? null,
    worker_id: raw.worker_id ?? null,
    categories_processed: raw.categories_processed ?? null,
    products_processed: raw.products_processed ?? null,
    products_created: raw.products_created ?? null,
    products_updated: raw.products_updated ?? null,
    price_changes_detected: raw.price_changes_detected ?? null,
    error_message: raw.error_message ?? null,
    metadata_json: raw.metadata_json ?? null,
    checkpoint_out_json: raw.checkpoint_out_json ?? null,
    retryable: raw.retryable ?? false,
    retry_of_run_id: raw.retry_of_run_id ?? null,
    retry_processed: raw.retry_processed ?? false,
    retry_exhausted: raw.retry_exhausted ?? false,
  }
}

export function adaptRunList(raw: RawRun[]): ScrapeRunSummary[] {
  return raw.map(adaptRun)
}

