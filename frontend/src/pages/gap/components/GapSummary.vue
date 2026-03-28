<template>
  <div class="summary-row">
    <div class="summary-card">
      <div class="num">{{ summary.total }}</div>
      <div class="lbl">Усього</div>
    </div>
    <div class="summary-card">
      <div class="num">{{ summary.new }}</div>
      <div class="lbl">Нові</div>
    </div>
    <div class="summary-card">
      <div class="num">{{ summary.in_progress }}</div>
      <div class="lbl">В роботі</div>
    </div>
    <div class="summary-card">
      <div class="num">{{ summary.done }}</div>
      <div class="lbl">Опрацьовано</div>
    </div>
  </div>
</template>

<script setup lang="ts">
/** GapSummary.vue — four-card summary row for gap results. */
import type { GapSummary } from '@/types/gap'

interface Props { summary: GapSummary }
defineProps<Props>()
</script>

