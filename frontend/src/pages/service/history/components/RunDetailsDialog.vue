<template>
  <DialogShell
    :open="open"
    title="Деталі запуску"
    @close="emit('close')"
  >
    <!-- Loading state -->
    <div v-if="loading" class="empty-state" style="min-height: 120px;">
      <div class="empty-state-icon" aria-live="polite">⏳</div>
      <p class="empty-state-title">Завантаження…</p>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="status-block error" role="alert">
      ⚠ {{ error }}
    </div>

    <!-- Run details -->
    <div v-else-if="run" class="run-details">
      <!-- Summary grid -->
      <dl class="run-details-grid">
        <dt>ID</dt>
        <dd>{{ run.id }}</dd>

        <dt>Тип</dt>
        <dd>{{ run.run_type || '—' }}</dd>

        <dt>Статус</dt>
        <dd>
          <span :class="['status-pill', `status-${statusKind(run.status)}`]">
            {{ run.status || '—' }}
          </span>
          <span v-if="run.attempt > 1" class="sch-attempt-badge">спроба {{ run.attempt }}</span>
        </dd>

        <dt>Тригер</dt>
        <dd>{{ triggerLabel(run.trigger_type) }}</dd>

        <dt>Магазин</dt>
        <dd>{{ run.store ? run.store.name : (run.store_id ? `#${run.store_id}` : '—') }}</dd>

        <dt>Поставлено у чергу</dt>
        <dd>{{ formatDate(run.queued_at) }}</dd>

        <dt>Розпочато</dt>
        <dd>{{ formatDate(run.started_at) }}</dd>

        <dt>Завершено</dt>
        <dd>{{ formatDate(run.finished_at) }}</dd>

        <template v-if="run.categories_processed !== null">
          <dt>Категорій</dt>
          <dd>{{ run.categories_processed }}</dd>
        </template>

        <template v-if="run.products_processed !== null">
          <dt>Товарів оброблено</dt>
          <dd>{{ run.products_processed }}</dd>
        </template>

        <template v-if="run.products_created !== null">
          <dt>Товарів створено</dt>
          <dd>{{ run.products_created }}</dd>
        </template>

        <template v-if="run.products_updated !== null">
          <dt>Товарів оновлено</dt>
          <dd>{{ run.products_updated }}</dd>
        </template>

        <template v-if="run.price_changes_detected !== null">
          <dt>Змін ціни</dt>
          <dd>{{ run.price_changes_detected }}</dd>
        </template>

        <template v-if="run.error_message">
          <dt>Помилка</dt>
          <dd class="run-details-error">{{ run.error_message }}</dd>
        </template>

        <template v-if="run.retryable">
          <dt>Повтор</dt>
          <dd>
            {{ run.retry_exhausted ? 'вичерпано' : (run.retry_processed ? 'оброблено' : 'очікує') }}
          </dd>
        </template>
      </dl>

      <!-- metadata_json collapsible -->
      <details v-if="run.metadata_json" style="margin-top: 12px;">
        <summary class="btn-ghost btn-sm" style="cursor: pointer; display: inline-block;">
          Метадані (JSON)
        </summary>
        <pre class="run-details-pre">{{ JSON.stringify(run.metadata_json, null, 2) }}</pre>
      </details>
    </div>

    <template #footer>
      <button class="btn" type="button" @click="emit('close')">Закрити</button>
    </template>
  </DialogShell>
</template>

<script setup lang="ts">
/**
 * RunDetailsDialog.vue — Vue-owned run details dialog.
 *
 * Uses DialogShell (Teleport-based).
 * Renders structured run metadata instead of raw JSON dump.
 */
import DialogShell from '@/components/base/DialogShell.vue'
import type { ScrapeRunSummary, RunStatus, TriggerType } from '@/types/history'
import type { StatusKind } from '@/types/common'

interface Props {
  open: boolean
  run: ScrapeRunSummary | null
  loading: boolean
  error: string | null
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'close'): void
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

<style scoped>
.run-details-grid {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: 6px 16px;
  margin: 0;
  font-size: 0.9rem;
}

.run-details-grid dt {
  font-weight: 600;
  color: #6b7280;
  white-space: nowrap;
}

.run-details-grid dd {
  margin: 0;
  word-break: break-word;
}

.run-details-error {
  color: #dc2626;
}

.run-details-pre {
  max-height: 240px;
  overflow: auto;
  background: #f5f7ff;
  padding: 10px 12px;
  border-radius: 6px;
  font-size: 0.82rem;
  margin-top: 8px;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>

