/**
 * useSchedulerReadModel.ts — composable owning all read-only scheduler state.
 *
 * Manages:
 *  - jobs list loading
 *  - job selection
 *  - detail + schedules + recent runs loading
 *  - first-activation guard (loads only on first tab open)
 *  - refresh
 *
 * Does NOT contain any mutation logic (create/edit/run-now/toggle).
 * Mutations are deferred to the next commit.
 */
import { ref } from 'vue'
import type { Ref } from 'vue'
import {
  fetchSchedulerJobs,
  fetchSchedulerJobDetail,
  fetchSchedulerRuns,
} from '@/api/client'
import type { SchedulerJobSummary, SchedulerJobDetail, SchedulerSchedule } from '@/types/scheduler'
import type { ScrapeRunSummary } from '@/types/history'

export interface SchedulerReadModel {
  jobs: Ref<SchedulerJobSummary[]>
  selectedJobId: Ref<number | null>
  selectedJob: Ref<SchedulerJobDetail | null>
  selectedSchedules: Ref<SchedulerSchedule[]>
  selectedRuns: Ref<ScrapeRunSummary[]>

  loadingJobs: Ref<boolean>
  loadingDetail: Ref<boolean>
  errorJobs: Ref<Error | null>
  errorDetail: Ref<Error | null>

  /** Load jobs on first call only; subsequent calls are no-ops unless force=true. */
  activate: (force?: boolean) => Promise<void>
  /** Select a job by id; loads detail + schedules + recent runs. */
  selectJob: (jobId: number) => Promise<void>
  /** Reload jobs list and, if a job is selected, reload its detail. */
  refresh: () => Promise<void>
}

export function useSchedulerReadModel(): SchedulerReadModel {
  const jobs = ref<SchedulerJobSummary[]>([])
  const selectedJobId = ref<number | null>(null)
  const selectedJob = ref<SchedulerJobDetail | null>(null)
  const selectedSchedules = ref<SchedulerSchedule[]>([])
  const selectedRuns = ref<ScrapeRunSummary[]>([])

  const loadingJobs = ref(false)
  const loadingDetail = ref(false)
  const errorJobs = ref<Error | null>(null)
  const errorDetail = ref<Error | null>(null)

  let _activated = false

  // ── Internal helpers ────────────────────────────────────────────────

  async function _loadJobs(): Promise<void> {
    loadingJobs.value = true
    errorJobs.value = null
    try {
      jobs.value = await fetchSchedulerJobs()
    } catch (err) {
      errorJobs.value = err instanceof Error ? err : new Error(String(err))
    } finally {
      loadingJobs.value = false
    }
  }

  async function _loadDetail(jobId: number): Promise<void> {
    loadingDetail.value = true
    errorDetail.value = null
    selectedJob.value = null
    selectedSchedules.value = []
    selectedRuns.value = []
    try {
      const [detail, runs] = await Promise.all([
        fetchSchedulerJobDetail(jobId),
        fetchSchedulerRuns(jobId, { limit: 20 }),
      ])
      selectedJob.value = detail.job
      selectedSchedules.value = detail.schedules
      selectedRuns.value = runs
    } catch (err) {
      errorDetail.value = err instanceof Error ? err : new Error(String(err))
    } finally {
      loadingDetail.value = false
    }
  }

  // ── Public API ───────────────────────────────────────────────────────

  async function activate(force = false): Promise<void> {
    if (_activated && !force) return
    _activated = true
    await _loadJobs()
  }

  async function selectJob(jobId: number): Promise<void> {
    selectedJobId.value = jobId
    await _loadDetail(jobId)
  }

  async function refresh(): Promise<void> {
    await _loadJobs()
    if (selectedJobId.value !== null) {
      await _loadDetail(selectedJobId.value)
    }
  }

  return {
    jobs,
    selectedJobId,
    selectedJob,
    selectedSchedules,
    selectedRuns,
    loadingJobs,
    loadingDetail,
    errorJobs,
    errorDetail,
    activate,
    selectJob,
    refresh,
  }
}

