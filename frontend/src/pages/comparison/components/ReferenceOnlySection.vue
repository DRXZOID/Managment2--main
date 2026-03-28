<template>
  <details class="collapsible">
    <summary>
      📋 Тільки в референсі
      <span class="badge badge-ref">{{ items.length }}</span>
    </summary>
    <div class="details-body">
      <p v-if="!items.length" class="muted">Немає товарів тільки в референсі.</p>
      <div
        v-for="item in items"
        :key="item.reference_product?.id ?? String(Math.random())"
        class="candidate-card"
      >
        <div class="ref-row">
          <ProductLink :product="item.reference_product" />
          <span class="muted"> — {{ formatPrice(item.reference_product) }}</span>
        </div>
        <ManualPicker
          v-if="item.reference_product?.id"
          :ref-product-id="item.reference_product.id"
          :target-category-ids="targetCategoryIds"
          @pick="(tgtId) => item.reference_product && emit('decision', item.reference_product.id, tgtId, 'confirmed')"
        />
      </div>
    </div>
  </details>
</template>

<script setup lang="ts">
/**
 * ReferenceOnlySection.vue — collapsible reference-only items, each with a manual picker.
 */
import type { ReferenceOnlyItem, MatchStatus } from '../types'
import ProductLink from './shared/ProductLink.vue'
import ManualPicker from './ManualPicker.vue'
import { formatPrice } from './shared/format'

interface Props {
  items: ReferenceOnlyItem[]
  targetCategoryIds: number[]
}
withDefaults(defineProps<Props>(), {
  items:             () => [],
  targetCategoryIds: () => [],
})

const emit = defineEmits<{
  (e: 'decision', refId: number, tgtId: number, status: MatchStatus): void
}>()
</script>

