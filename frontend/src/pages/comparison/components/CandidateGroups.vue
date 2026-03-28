<template>
  <div class="comp-section">
    <h3>
      🔎 Групи кандидатів
      <span class="badge badge-ambig">{{ groups.length }}</span>
    </h3>
    <p v-if="!groups.length" class="muted">Немає груп кандидатів.</p>
    <CandidateGroupCard
      v-for="g in groups"
      :key="g.reference_product?.id ?? String(Math.random())"
      :group="g"
      :target-category-ids="targetCategoryIds"
      :decision-in-progress-key="decisionInProgressKey"
      @decision="(refId, tgtId, status) => emit('decision', refId, tgtId, status)"
    />
  </div>
</template>

<script setup lang="ts">
/**
 * CandidateGroups.vue — section wrapper for all candidate group cards.
 */
import type { CandidateGroup, MatchStatus } from '../types'
import CandidateGroupCard from './CandidateGroupCard.vue'

interface Props {
  groups: CandidateGroup[]
  targetCategoryIds: number[]
  decisionInProgressKey: string | null
}
withDefaults(defineProps<Props>(), {
  groups:                () => [],
  targetCategoryIds:     () => [],
  decisionInProgressKey: null,
})

const emit = defineEmits<{
  (e: 'decision', refId: number, tgtId: number, status: MatchStatus): void
}>()
</script>

