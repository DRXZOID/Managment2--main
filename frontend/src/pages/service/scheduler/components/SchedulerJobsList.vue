<template>
  <!-- Loading state -->
  <div v-if="loading" class="select-list-empty" aria-live="polite">Завантаження…</div>

  <!-- Error state -->
  <div v-else-if="error" class="select-list-empty status-error" style="color: #991b1b;">
    ⚠ {{ error.message }}
  </div>

  <!-- Empty state -->
  <div v-else-if="!jobs.length" class="select-list-empty">
    <div class="empty-state-icon">🗓</div>
    <div class="empty-state-title">Немає задач</div>
    <div class="empty-state-body">Задачі scheduler відсутні.</div>
  </div>

  <!-- Jobs list -->
  <template v-else>
    <div
      v-for="job in jobs"
      :key="job.id"
      :class="['sch-job-item', { selected: job.id === selectedJobId }]"
      role="button"
      :aria-selected="job.id === selectedJobId"
      tabindex="0"
      @click="$emit('select', job.id)"
      @keydown.enter="$emit('select', job.id)"
      @keydown.space.prevent="$emit('select', job.id)"
    >
      <div class="sch-job-item-top">
        <span class="sch-job-source">{{ job.source_key }}</span>
        <span :class="['sch-badge', job.enabled ? 'sch-badge-enabled' : 'sch-badge-disabled']">
          {{ job.enabled ? 'ON' : 'OFF' }}
        </span>
      </div>
      <div class="sch-job-item-sub">
        <span class="sch-runner-label">{{ getRunnerUiSpec(job.runner_type).label }}</span>
      </div>
      <div v-if="storeHint(job)" class="sch-job-item-store">
        🏪 {{ storeHint(job) }}
      </div>
      <div v-if="job.next_run_at" class="sch-job-item-next">
        ⏱ {{ fmtDate(job.next_run_at) }}
      </div>
    </div>
  </template>
</template>

<script setup lang="ts">
/**
 * SchedulerJobsList.vue — left-panel jobs list for the Scheduler tab.
 *
 * Renders the job items using existing .sch-job-item CSS classes.
 * Emits 'select' with the job id on click.
 * Read-only: no mutation buttons.
 */
import { getRunnerUiSpec } from '@/types/scheduler'
import type { SchedulerJobSummary } from '@/types/scheduler'

interface Props {
  jobs: SchedulerJobSummary[]
  selectedJobId: number | null
  loading: boolean
  error: Error | null
}

withDefaults(defineProps<Props>(), {
  selectedJobId: null,
  error: null,
})

defineEmits<{
  (e: 'select', jobId: number): void
}>()

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function fmtDate(iso: string | null): string {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString('uk-UA', {
      month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit',
    })
  } catch {
    return iso
  }
}

function storeHint(job: SchedulerJobSummary): string | null {
  const params = job.params_json
  if (!params) return null
  const storeId = params['store_id']
  return storeId != null ? String(storeId) : null
}
</script>

