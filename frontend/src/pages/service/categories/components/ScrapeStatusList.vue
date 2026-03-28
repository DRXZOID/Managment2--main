<template>
  <div v-if="runs.length > 0" class="scrape-status-list">
    <div
      v-for="run in runs"
      :key="run.id"
      :class="['scrape-status-card', statusCardClass(run.status)]"
    >
      <strong>{{ run.store ? run.store.name : (run.store_id ? `store #${run.store_id}` : '—') }}</strong>
      <div style="font-size:0.85rem; margin-top:4px;">
        {{ run.run_type || '—' }} · {{ run.status }}
      </div>
      <div style="font-size:0.8rem; color:#666;">
        {{ run.started_at ? new Date(run.started_at).toLocaleString() : '—' }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * ScrapeStatusList.vue — compact horizontal list of recent scrape runs.
 *
 * Mirrors the legacy service.categories.js loadScrapeStatus() rendering.
 * Renders nothing when runs is empty (widget not shown until data arrives).
 */
import type { ScrapeRunSummary, RunStatus } from '@/types/history'

interface Props {
  runs: ScrapeRunSummary[]
}

defineProps<Props>()

function statusCardClass(status: RunStatus | string | null | undefined): string {
  if (!status) return ''
  const s = status.toLowerCase()
  if (s === 'finished' || s === 'success') return 'finished'
  if (s === 'failed') return 'failed'
  return 'running'
}
</script>

