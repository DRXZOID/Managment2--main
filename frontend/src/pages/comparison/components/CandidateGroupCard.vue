<template>
  <div class="candidate-card">
    <!-- Reference product row -->
    <div class="ref-row">
      <ProductLink :product="group.reference_product" />
      <span class="muted"> — {{ formatPrice(group.reference_product) }}</span>
    </div>

    <!-- Candidates list -->
    <div class="candidate-list">
      <div
        v-for="c in group.candidates"
        :key="c.target_product?.id ?? String(Math.random())"
        class="candidate-item"
      >
        <ProductLink :product="c.target_product" />
        <CatBadge :cat="c.target_category" />
        <span class="muted">{{ formatPrice(c.target_product) }}</span>
        <ScorePill :percent="c.score_percent" :details="c.score_details" />

        <!-- Accept button -->
        <button
          v-if="c.can_accept !== false"
          class="btn btn-sm"
          :disabled="isInProgress(c.target_product?.id)"
          @click="c.target_product && onAccept(c.target_product.id)"
        >
          {{ isInProgress(c.target_product?.id) ? '…' : '✔ Прийняти' }}
        </button>
        <button
          v-else
          class="btn btn-sm"
          disabled
          style="opacity:0.4;"
          :title="c.disabled_reason ?? ''"
        >🚫 Вже використано</button>

        <!-- Reject button -->
        <button
          class="btn btn-sm btn-reject"
          :disabled="isInProgress(c.target_product?.id)"
          @click="c.target_product && onReject(c.target_product.id)"
        >
          {{ isInProgress(c.target_product?.id) ? '…' : '✖ Відхилити' }}
        </button>
      </div>
    </div>

    <!-- Manual picker -->
    <ManualPicker
      v-if="group.reference_product?.id"
      :ref-product-id="group.reference_product.id"
      :target-category-ids="targetCategoryIds"
      @pick="onPickerPick"
    />
  </div>
</template>

<script setup lang="ts">
/**
 * CandidateGroupCard.vue — one candidate group (reference product + candidates + manual picker).
 */
import type { CandidateGroup, MatchStatus } from '../types'
import ProductLink from './shared/ProductLink.vue'
import CatBadge from './shared/CatBadge.vue'
import ScorePill from './shared/ScorePill.vue'
import ManualPicker from './ManualPicker.vue'
import { formatPrice } from './shared/format'

interface Props {
  group: CandidateGroup
  targetCategoryIds: number[]
  decisionInProgressKey: string | null
}
const props = withDefaults(defineProps<Props>(), {
  targetCategoryIds:     () => [],
  decisionInProgressKey: null,
})


const emit = defineEmits<{
  (e: 'decision', refId: number, tgtId: number, status: MatchStatus): void
}>()

function isInProgress(tgtId: number | undefined): boolean {
  if (tgtId == null || !props.group.reference_product?.id) return false
  return props.decisionInProgressKey === `${props.group.reference_product.id}:${tgtId}`
}

function onAccept(tgtId: number) {
  if (props.group.reference_product?.id)
    emit('decision', props.group.reference_product.id, tgtId, 'confirmed')
}
function onReject(tgtId: number) {
  if (props.group.reference_product?.id)
    emit('decision', props.group.reference_product.id, tgtId, 'rejected')
}
function onPickerPick(tgtId: number) {
  if (props.group.reference_product?.id)
    emit('decision', props.group.reference_product.id, tgtId, 'confirmed')
}
</script>

