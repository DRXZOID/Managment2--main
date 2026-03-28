/**
 * useSchedulerActions.ts — scheduler mutation composable.
 *
 * Encapsulates all write operations for the Scheduler tab:
 *   - createJob
 *   - updateJob
 *   - toggleEnabled
 *   - runNow  (with 409 conflict handling)
 *   - upsertSchedule
 *   - refreshRuns (runs-only reload)
 *
 * Accepts the read-model instance so it can update shared state after mutations.
 * All post-mutation refreshes are explicit (no optimistic updates).
 */
import { ref } from 'vue'
import type { Ref } from 'vue'
import {
  createSchedulerJob,
  updateSchedulerJob,
  enqueueJobRun,
  upsertJobSchedule,
  fetchSchedulerRuns,
  fetchSchedulerJobDetail,
  fetchSchedulerJobs,
} from '@/api/client'
import { ApiError } from '@/api/errors'
import type { SchedulerJobDetail, SchedulerSchedule } from '@/types/scheduler'
import type { SchedulerReadModel } from './useSchedulerReadModel'
import type { JobFormState, ScheduleFormState } from './formModels'
import { serializeJobForm, serializeScheduleForm } from './formModels'

// ---------------------------------------------------------------------------
// Status token
// ---------------------------------------------------------------------------

export type ActionStatusKind = 'idle' | 'pending' | 'success' | 'error' | 'conflict'

export interface ActionStatus {
  kind: ActionStatusKind
  message: string
}

const IDLE: ActionStatus = { kind: 'idle', message: '' }

// ---------------------------------------------------------------------------
// Interface
// ---------------------------------------------------------------------------

export interface SchedulerActions {
  // ── Run now ─────────────────────────────────────────
  runNowStatus: Ref<ActionStatus>
  runNowPending: Ref<boolean>
  runNow: (jobId: number) => Promise<void>
  clearRunNowStatus: () => void

  // ── Toggle enabled ──────────────────────────────────
  togglePending: Ref<boolean>
  toggleEnabled: (job: SchedulerJobDetail) => Promise<void>

  // ── Create / update job ─────────────────────────────
  jobFormPending: Ref<boolean>
  jobFormError: Ref<string | null>
  createJob: (form: JobFormState) => Promise<SchedulerJobDetail | null>
  updateJob: (jobId: number, form: JobFormState) => Promise<SchedulerJobDetail | null>

  // ── Schedule ────────────────────────────────────────
  schedulePending: Ref<boolean>
  scheduleError: Ref<string | null>
  upsertSchedule: (jobId: number, form: ScheduleFormState) => Promise<SchedulerSchedule | null>

  // ── Runs-only refresh ───────────────────────────────
  runsRefreshPending: Ref<boolean>
  refreshRuns: (jobId: number) => Promise<void>
}

// ---------------------------------------------------------------------------
// Implementation
// ---------------------------------------------------------------------------

export function useSchedulerActions(model: SchedulerReadModel): SchedulerActions {

  // ── Run now ─────────────────────────────────────────

  const runNowStatus = ref<ActionStatus>({ ...IDLE })
  const runNowPending = ref(false)

  async function runNow(jobId: number): Promise<void> {
    if (runNowPending.value) return
    runNowPending.value = true
    runNowStatus.value = { kind: 'pending', message: 'Запуск…' }
    try {
      await enqueueJobRun(jobId)
      runNowStatus.value = { kind: 'success', message: '✓ Задачу поставлено в чергу' }
      // Refresh runs table without disturbing the rest of the detail
      await refreshRuns(jobId)
    } catch (err) {
      if (err instanceof ApiError && err.isConflict) {
        runNowStatus.value = {
          kind: 'conflict',
          message: `⚠ Конфлікт: задача вже виконується (allow_overlap=false). Дочекайтесь завершення або увімкніть allow_overlap.`,
        }
      } else {
        const msg = err instanceof Error ? err.message : String(err)
        runNowStatus.value = { kind: 'error', message: `✗ Помилка: ${msg}` }
      }
    } finally {
      runNowPending.value = false
    }
  }

  function clearRunNowStatus(): void {
    runNowStatus.value = { ...IDLE }
  }

  // ── Toggle enabled ──────────────────────────────────

  const togglePending = ref(false)

  async function toggleEnabled(job: SchedulerJobDetail): Promise<void> {
    if (togglePending.value) return
    togglePending.value = true
    try {
      const updated = await updateSchedulerJob(job.id, { enabled: !job.enabled })
      // Patch the job in the list in-place so the badge updates immediately
      const idx = model.jobs.value.findIndex((j) => j.id === job.id)
      if (idx !== -1) {
        model.jobs.value = [
          ...model.jobs.value.slice(0, idx),
          { ...model.jobs.value[idx], enabled: updated.enabled },
          ...model.jobs.value.slice(idx + 1),
        ]
      }
      // Also update selected job detail
      if (model.selectedJob.value?.id === job.id) {
        model.selectedJob.value = { ...model.selectedJob.value, enabled: updated.enabled }
      }
    } catch {
      // Silently fail toggle — user sees no change (state stays consistent)
    } finally {
      togglePending.value = false
    }
  }

  // ── Create job ───────────────────────────────────────

  const jobFormPending = ref(false)
  const jobFormError = ref<string | null>(null)

  async function createJob(form: JobFormState): Promise<SchedulerJobDetail | null> {
    const { payload, jsonError } = serializeJobForm(form)
    if (jsonError || !payload) {
      jobFormError.value = jsonError ?? 'Невалідні дані форми'
      return null
    }
    if (!payload['source_key'] || !(payload['source_key'] as string).trim()) {
      jobFormError.value = "source_key є обов'язковим полем"
      return null
    }

    jobFormPending.value = true
    jobFormError.value = null
    try {
      const job = await createSchedulerJob(payload as Parameters<typeof createSchedulerJob>[0])
      // Refresh jobs list, then select the new job
      const jobs = await fetchSchedulerJobs()
      model.jobs.value = jobs
      model.selectedJobId.value = job.id
      const [detail, runs] = await Promise.all([
        fetchSchedulerJobDetail(job.id),
        fetchSchedulerRuns(job.id, { limit: 20 }),
      ])
      model.selectedJob.value = detail.job
      model.selectedSchedules.value = detail.schedules
      model.selectedRuns.value = runs
      return job
    } catch (err) {
      jobFormError.value = err instanceof Error ? err.message : String(err)
      return null
    } finally {
      jobFormPending.value = false
    }
  }

  // ── Update job ───────────────────────────────────────

  async function updateJob(jobId: number, form: JobFormState): Promise<SchedulerJobDetail | null> {
    const { payload, jsonError } = serializeJobForm(form)
    if (jsonError || !payload) {
      jobFormError.value = jsonError ?? 'Невалідні дані форми'
      return null
    }

    jobFormPending.value = true
    jobFormError.value = null
    try {
      const updated = await updateSchedulerJob(jobId, payload as Parameters<typeof updateSchedulerJob>[1])
      // Patch list badge
      const idx = model.jobs.value.findIndex((j) => j.id === jobId)
      if (idx !== -1) {
        model.jobs.value = [
          ...model.jobs.value.slice(0, idx),
          { ...model.jobs.value[idx], ...updated },
          ...model.jobs.value.slice(idx + 1),
        ]
      }
      // Reload full detail
      const [detail, runs] = await Promise.all([
        fetchSchedulerJobDetail(jobId),
        fetchSchedulerRuns(jobId, { limit: 20 }),
      ])
      model.selectedJob.value = detail.job
      model.selectedSchedules.value = detail.schedules
      model.selectedRuns.value = runs
      return updated
    } catch (err) {
      jobFormError.value = err instanceof Error ? err.message : String(err)
      return null
    } finally {
      jobFormPending.value = false
    }
  }

  // ── Upsert schedule ──────────────────────────────────

  const schedulePending = ref(false)
  const scheduleError = ref<string | null>(null)

  async function upsertSchedule(jobId: number, form: ScheduleFormState): Promise<SchedulerSchedule | null> {
    scheduleError.value = null
    // Client-side validation
    if (form.schedule_type === 'interval' && !form.interval_sec) {
      scheduleError.value = 'Вкажіть інтервал у секундах'
      return null
    }
    if (form.schedule_type === 'cron' && !form.cron_expr.trim()) {
      scheduleError.value = 'Вкажіть cron вираз'
      return null
    }

    schedulePending.value = true
    try {
      const payload = serializeScheduleForm(form)
      const schedule = await upsertJobSchedule(jobId, payload)
      // Refresh schedule in detail
      const detail = await fetchSchedulerJobDetail(jobId)
      model.selectedJob.value = detail.job
      model.selectedSchedules.value = detail.schedules
      return schedule
    } catch (err) {
      scheduleError.value = err instanceof Error ? err.message : String(err)
      return null
    } finally {
      schedulePending.value = false
    }
  }

  // ── Refresh runs only ────────────────────────────────

  const runsRefreshPending = ref(false)

  async function refreshRuns(jobId: number): Promise<void> {
    runsRefreshPending.value = true
    try {
      model.selectedRuns.value = await fetchSchedulerRuns(jobId, { limit: 20 })
    } catch {
      // Non-blocking: runs table stays stale rather than surfacing an error
    } finally {
      runsRefreshPending.value = false
    }
  }

  return {
    runNowStatus,
    runNowPending,
    runNow,
    clearRunNowStatus,
    togglePending,
    toggleEnabled,
    jobFormPending,
    jobFormError,
    createJob,
    updateJob,
    schedulePending,
    scheduleError,
    upsertSchedule,
    runsRefreshPending,
    refreshRuns,
  }
}

