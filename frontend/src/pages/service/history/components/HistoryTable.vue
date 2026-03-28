<template>
  <div>
    <!-- Empty state -->
    <div v-if="runs.length === 0" class="empty-state" style="margin-top: 12px;">
      <div class="empty-state-icon">📋</div>
      <p class="empty-state-title">Немає записів</p>
      <p class="empty-state-body">Синхронізуйте дані або змініть фільтри.</p>
    </div>

    <!-- Table -->
    <div v-else class="table-wrapper" style="margin-top: 12px;">
      <table>
        <thead>
          <tr>
            <th>Дата</th>
            <th>Магазин</th>
            <th>Тип</th>
            <th>Тригер</th>
            <th>Статус</th>
            <th>Дії</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="run in runs" :key="run.id">
            <td>{{ formatDate(run.started_at ?? run.queued_at) }}</td>
            <td>{{ run.store ? run.store.name : (run.store_id ? `#${run.store_id}` : '—') }}</td>
            <td>{{ run.run_type || '—' }}</td>
            <td>{{ triggerLabel(run.trigger_type) }}</td>
            <td>
              <span :class="['status-pill', `status-${statusKind(run.status)}`]">
                {{ run.status || '—' }}
              </span>
              <span v-if="run.attempt > 1" class="sch-attempt-badge">{{ run.attempt }}</span>
            </td>
            <td>
              <button
                class="btn-ghost btn-sm"
                type="button"
                @click="emit('details', run.id)"
              >Деталі</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * HistoryTable.vue — renders the scrape run list.
 *
 * Emits 'details' with run id when user clicks the details button.
 * Status/trigger display logic mirrors service.history.js.
 */
import type { ScrapeRunSummary, RunStatus, TriggerType } from '@/types/history'
import type { StatusKind } from '@/types/common'

interface Props {
  runs: ScrapeRunSummary[]
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'details', runId: number): void
}>()

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleString()
}

const STATUS_KIND: Record<string, StatusKind> = {
  queued: 'info',
  running: 'warning',
  success: 'success',
  finished: 'success',
  partial: 'warning',
  failed: 'error',
  skipped: 'info',
  cancelled: 'info',
  retry: 'warning',
}

function statusKind(s: RunStatus | string | null | undefined): StatusKind {
  if (!s) return 'warning'
  return STATUS_KIND[s.toLowerCase()] ?? 'info'
}

const TRIGGER_LABEL: Record<string, string> = {
  manual: '🖱 manual',
  scheduled: '⏱ scheduled',
  retry: '🔄 retry',
}

function triggerLabel(t: TriggerType | null | undefined): string {
  if (!t) return '—'
  return TRIGGER_LABEL[t] ?? t
}
</script>

