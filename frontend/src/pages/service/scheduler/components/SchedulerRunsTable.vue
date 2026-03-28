<template>
  <div class="subpanel" style="margin-top: 16px;">
    <div class="panel-header">
      <strong class="panel-title">Останні запуски</strong>
    </div>

    <div v-if="!runs.length" class="sch-no-schedule">Запусків ще немає.</div>

    <table v-else class="sch-runs-table">
      <thead>
        <tr>
          <th>#</th>
          <th>Статус</th>
          <th>Тригер</th>
          <th>Початок</th>
          <th>Тривалість</th>
          <th>Спроба</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="run in runs" :key="run.id">
          <tr>
            <td class="muted">{{ run.id }}</td>
            <td>
              <span :class="['status-pill', statusClass(run.status)]">
                {{ statusLabel(run.status) }}
              </span>
            </td>
            <td class="muted">{{ run.trigger_type ?? '—' }}</td>
            <td>{{ fmtDate(run.started_at ?? run.queued_at) }}</td>
            <td>{{ fmtDuration(run.started_at, run.finished_at) }}</td>
            <td>
              <span v-if="(run.attempt ?? 1) > 1" class="sch-attempt-badge">
                #{{ run.attempt }}
              </span>
              <span v-else class="muted">1</span>
            </td>
          </tr>
          <!-- Error message row -->
          <tr v-if="run.error_message" class="sch-err-row">
            <td :colspan="6">
              <div class="sch-run-error" :title="run.error_message">
                ✗ {{ run.error_message.slice(0, 160) }}{{ run.error_message.length > 160 ? '…' : '' }}
              </div>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
/**
 * SchedulerRunsTable.vue — recent runs compact table.
 * Read-only. Uses existing .sch-runs-table CSS.
 */
import { useStatusPill } from '@/composables/useStatusPill'
import type { ScrapeRunSummary, RunStatus } from '@/types/history'

interface Props {
  runs: ScrapeRunSummary[]
}

defineProps<Props>()

const { resolveKind, resolveLabel } = useStatusPill()

// Map StatusKind to the CSS class suffix used by status-pill in common.css
const KIND_CSS: Record<string, string> = {
  info:    'status-info',
  success: 'status-success',
  warning: 'status-warning',
  error:   'status-error',
  muted:   'status-muted',
}

function statusClass(status: RunStatus): string {
  return KIND_CSS[resolveKind(status)] ?? 'status-info'
}

function statusLabel(status: RunStatus): string {
  return resolveLabel(status)
}

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

function fmtDuration(started: string | null, finished: string | null): string {
  if (!started || !finished) return '—'
  try {
    const ms = new Date(finished).getTime() - new Date(started).getTime()
    if (ms < 0) return '—'
    if (ms < 1000) return `${ms}ms`
    if (ms < 60_000) return `${(ms / 1000).toFixed(1)}s`
    return `${Math.floor(ms / 60_000)}m ${Math.round((ms % 60_000) / 1000)}s`
  } catch {
    return '—'
  }
}
</script>

