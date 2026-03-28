<template>
  <div class="summary-row">
    <div class="summary-card">
      <div class="num">{{ total }}</div>
      <div class="lbl">Показано</div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * MatchesSummary.vue — row count summary card.
 * Rendered only when MatchesPage has loaded at least once (v-if on parent).
 */
interface Props {
  total: number
}

defineProps<Props>()
</script>

