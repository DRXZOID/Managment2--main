/**
 * frontend/src/types/scheduler.ts — Scheduler job/schedule frontend DTO types.
 *
 * These reflect the shapes returned by:
 *   GET  /api/admin/scrape/jobs              → { jobs: SchedulerJobSummary[] }
 *   GET  /api/admin/scrape/jobs/:id          → { job: SchedulerJobDetail, schedules: SchedulerSchedule[] }
 *   PATCH /api/admin/scrape/jobs/:id         → { job: SchedulerJobDetail }
 *   POST /api/admin/scrape/jobs/:id/run      → { run: SchedulerRunSummary }
 *   GET  /api/admin/scrape/jobs/:id/runs     → { runs: SchedulerRunSummary[] }
 *   GET  /api/admin/scrape/jobs/:id/schedule → { schedules: SchedulerSchedule[] }
 *   PUT  /api/admin/scrape/jobs/:id/schedule → { schedule: SchedulerSchedule }
 *
 * Field names match the current serializer output (pricewatch/web/serializers.py).
 * These are frontend adapter types — not canonical backend schemas.
 */

// ---------------------------------------------------------------------------
// Runner type
// ---------------------------------------------------------------------------

/**
 * RunnerType — the set of known runner identifiers as declared in
 * static/js/service.scheduler.state.js RUNNER_SPECS.
 *
 * An `unknown` string literal union member is included to handle future
 * backend additions without breaking the frontend at parse time.
 */
export type RunnerType =
  | 'store_category_sync'
  | 'category_product_sync'
  | 'all_stores_category_sync'
  | (string & {})  // allow unknown future runner types

// ---------------------------------------------------------------------------
// Scheduler job
// ---------------------------------------------------------------------------

export interface SchedulerJobSummary {
  id: number
  source_key: string
  runner_type: RunnerType
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

/** Alias used when a single job is returned with its schedules. */
export type SchedulerJobDetail = SchedulerJobSummary

// ---------------------------------------------------------------------------
// Scheduler schedule
// ---------------------------------------------------------------------------

export type ScheduleType = 'interval' | 'cron' | (string & {})
export type MisfirePolicy = 'skip' | 'run_once' | (string & {})

export interface SchedulerSchedule {
  id: number
  job_id: number
  schedule_type: ScheduleType
  cron_expr: string | null
  interval_sec: number | null
  timezone: string
  jitter_sec: number
  misfire_policy: MisfirePolicy
  enabled: boolean
  created_at: string | null
  updated_at: string | null
}

// ---------------------------------------------------------------------------
// Runner UI spec (mirrors RUNNER_SPECS from service.scheduler.state.js)
// ---------------------------------------------------------------------------

export interface RunnerUiSpec {
  label: string
  requiresStore: boolean
  requiresCategory: boolean
  storeHelp?: string
  categoryHelp?: string
  paramsStoreKey: string | null
  paramsCatKey: string | null
}

/** The canonical runner UI spec lookup table. */
export const RUNNER_SPECS: Record<string, RunnerUiSpec> = {
  store_category_sync: {
    label: 'Синхронізація категорій магазину',
    requiresStore: true,
    requiresCategory: false,
    storeHelp: 'Магазин, категорії якого синхронізувати',
    paramsStoreKey: 'store_id',
    paramsCatKey: null,
  },
  category_product_sync: {
    label: 'Синхронізація товарів категорії',
    requiresStore: true,
    requiresCategory: true,
    storeHelp: 'Магазин, що містить категорію',
    categoryHelp: 'Категорія для синхронізації товарів',
    paramsStoreKey: 'store_id',
    paramsCatKey: 'category_id',
  },
  all_stores_category_sync: {
    label: 'Синхронізація категорій всіх магазинів',
    requiresStore: false,
    requiresCategory: false,
    paramsStoreKey: null,
    paramsCatKey: null,
  },
}

export function getRunnerUiSpec(runnerType: RunnerType): RunnerUiSpec {
  return (
    RUNNER_SPECS[runnerType] ?? {
      label: runnerType,
      requiresStore: false,
      requiresCategory: false,
      paramsStoreKey: null,
      paramsCatKey: null,
    }
  )
}

