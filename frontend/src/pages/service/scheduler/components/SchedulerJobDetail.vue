<template>
  <div class="sch-info-grid">
    <InfoRow label="Source key"><code>{{ job.source_key }}</code></InfoRow>
    <InfoRow label="Runner">
      <span class="sch-runner-label">{{ getRunnerUiSpec(job.runner_type).label }}</span>
    </InfoRow>
    <InfoRow label="Enabled">
      <span :class="['sch-badge', job.enabled ? 'sch-badge-enabled' : 'sch-badge-disabled']">
        {{ job.enabled ? 'enabled' : 'disabled' }}
      </span>
    </InfoRow>
    <InfoRow label="Allow overlap">{{ job.allow_overlap ? '✓ так' : '✗ ні' }}</InfoRow>
    <InfoRow label="Max retries">{{ job.max_retries }}</InfoRow>
    <InfoRow label="Retry backoff">{{ job.retry_backoff_sec }}s</InfoRow>
    <InfoRow v-if="job.timeout_sec != null" label="Timeout">{{ job.timeout_sec }}s</InfoRow>
    <InfoRow label="Priority">{{ job.priority }}</InfoRow>
    <InfoRow v-if="job.concurrency_key" label="Concurrency key">
      <code>{{ job.concurrency_key }}</code>
    </InfoRow>
    <InfoRow v-if="job.next_run_at" label="Наступний запуск">{{ fmtDate(job.next_run_at) }}</InfoRow>
    <InfoRow v-if="job.last_run_at" label="Останній запуск">{{ fmtDate(job.last_run_at) }}</InfoRow>
    <InfoRow v-if="job.created_at" label="Створено">{{ fmtDate(job.created_at) }}</InfoRow>
    <InfoRow v-if="job.updated_at" label="Оновлено">{{ fmtDate(job.updated_at) }}</InfoRow>
  </div>

  <!-- Params summary -->
  <div v-if="job.params_json && hasParams" class="subpanel" style="margin-top: 12px;">
    <div class="panel-header">
      <strong class="panel-title">Параметри</strong>
    </div>
    <pre class="sch-params-code">{{ JSON.stringify(job.params_json, null, 2) }}</pre>
  </div>
</template>

<script setup lang="ts">
/**
 * SchedulerJobDetail.vue — job info-grid for the detail panel.
 * Read-only: shows all job fields using existing .sch-info-grid CSS.
 */
import { computed, h } from 'vue'
import type { FunctionalComponent } from 'vue'
import { getRunnerUiSpec } from '@/types/scheduler'
import type { SchedulerJobDetail } from '@/types/scheduler'

interface Props {
  job: SchedulerJobDetail
}

const props = defineProps<Props>()

const hasParams = computed(
  () => props.job.params_json && Object.keys(props.job.params_json).length > 0,
)

function fmtDate(iso: string | null): string {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString('uk-UA', {
      year: 'numeric', month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit',
    })
  } catch {
    return iso
  }
}

// Functional InfoRow component — renders .sch-info-row with label + slot content
const InfoRow: FunctionalComponent<{ label: string }> = (props, { slots }) =>
  h('div', { class: 'sch-info-row' }, [
    h('span', { class: 'sch-info-label' }, props.label),
    h('span', { class: 'sch-info-value' }, slots.default?.()),
  ])
InfoRow.props = ['label']
</script>

