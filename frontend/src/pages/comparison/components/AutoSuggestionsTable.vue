<template>
  <div class="comp-section">
    <h3>
      🔍 Авто-пропозиції (висока впевненість)
      <span class="badge badge-heuristic">{{ suggestions.length }}</span>
    </h3>
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Референс</th><th>Ціна</th>
            <th>Цільовий</th><th>Ціна</th>
            <th>Score</th><th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="m in suggestions" :key="`${m.reference_product?.id}:${m.target_product?.id}`">
            <td>
              <ProductLink :product="m.reference_product" />
              <span class="badge badge-heuristic">🔍 авто</span>
            </td>
            <td>{{ formatPrice(m.reference_product) }}</td>
            <td>
              <ProductLink :product="m.target_product" />
              <CatBadge :cat="m.target_category" />
            </td>
            <td>{{ formatPrice(m.target_product) }}</td>
            <td><ScorePill :percent="m.score_percent" :details="m.score_details" /></td>
            <td class="action-cell">
              <button
                class="btn btn-sm"
                :disabled="isInProgress(m.reference_product?.id, m.target_product?.id)"
                @click="onConfirm(m)"
              >
                {{ isInProgress(m.reference_product?.id, m.target_product?.id) ? '…' : '✔ Підтвердити' }}
              </button>
              <button
                class="btn btn-sm btn-reject"
                :disabled="isInProgress(m.reference_product?.id, m.target_product?.id)"
                @click="onReject(m)"
              >
                {{ isInProgress(m.reference_product?.id, m.target_product?.id) ? '…' : '✖ Відхилити' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * AutoSuggestionsTable.vue — high-confidence auto-suggestion matches.
 * Emits 'decision' with (refId, tgtId, status) on confirm/reject.
 */
import type { ConfirmedMatch, MatchStatus } from '../types'
import ProductLink from './shared/ProductLink.vue'
import CatBadge from './shared/CatBadge.vue'
import ScorePill from './shared/ScorePill.vue'
import { formatPrice } from './shared/format'

interface Props {
  suggestions: ConfirmedMatch[]
  decisionInProgressKey: string | null
}
const props = withDefaults(defineProps<Props>(), {
  suggestions: () => [],
  decisionInProgressKey: null,
})


const emit = defineEmits<{
  (e: 'decision', refId: number, tgtId: number, status: MatchStatus): void
}>()

function isInProgress(refId: number | undefined, tgtId: number | undefined): boolean {
  if (refId == null || tgtId == null) return false
  return props.decisionInProgressKey === `${refId}:${tgtId}`
}

function onConfirm(m: ConfirmedMatch) {
  if (m.reference_product?.id && m.target_product?.id)
    emit('decision', m.reference_product.id, m.target_product.id, 'confirmed')
}
function onReject(m: ConfirmedMatch) {
  if (m.reference_product?.id && m.target_product?.id)
    emit('decision', m.reference_product.id, m.target_product.id, 'rejected')
}
</script>

