<template>
  <div>
    <div v-if="errorText" class="status-block" style="background:#ffe3e3;color:#b20000;">
      {{ errorText }}
    </div>
    <div v-else-if="comparing" class="status-block info">Виконується порівняння…</div>
    <div v-else-if="result" class="status-block info">
      Авто-пропозиції: {{ autoCount }}  •
      Кандидатів: {{ result.summary.candidate_groups }}  •
      Тільки в референсі: {{ result.summary.reference_only }}  •
      Тільки в цільовому: {{ result.summary.target_only }}
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * ComparisonSummaryBar.vue — one-line status/summary after comparison.
 */
import { computed } from 'vue'
import type { ComparisonResult } from '../types'

interface Props {
  result: ComparisonResult | null
  comparing: boolean
  errorText: string | null
}
const props = withDefaults(defineProps<Props>(), {
  result:    null,
  comparing: false,
  errorText: null,
})


const autoCount = computed(() =>
  (props.result?.confirmed_matches ?? []).filter((m) => !m.is_confirmed).length,
)
</script>

