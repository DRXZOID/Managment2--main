<template>
  <section class="panel">
    <h2>Вибір магазину</h2>
    <div class="grid-two">
      <div class="form-group">
        <label for="referenceStore">Референсний магазин</label>
        <select id="referenceStore" :value="referenceStoreId ?? ''" @change="onRefStoreChange">
          <option value="">Оберіть магазин</option>
          <option v-for="s in referenceStores" :key="s.id" :value="s.id">{{ s.name }}</option>
        </select>
      </div>
      <div class="form-group">
        <label for="targetStore">Цільовий магазин</label>
        <select id="targetStore" :value="targetStoreId ?? ''" @change="onTargetStoreChange">
          <option value="">Всі цільові магазини</option>
          <option v-for="s in targetStores" :key="s.id" :value="s.id">{{ s.name }}</option>
        </select>
      </div>
    </div>
    <div
      v-if="statusText"
      class="status-block info"
      style="margin-top:16px;"
    >{{ statusText }}</div>
  </section>
</template>

<script setup lang="ts">
/**
 * ComparisonFilters.vue — reference/target store selects + page status.
 * All state is owned by useComparisonPage; this component only emits.
 */
import type { StoreSummary } from '@/types/store'

interface Props {
  referenceStores: StoreSummary[]
  targetStores: StoreSummary[]
  referenceStoreId: number | null
  targetStoreId: number | null
  statusText: string
}
withDefaults(defineProps<Props>(), {
  referenceStores: () => [],
  targetStores:    () => [],
  referenceStoreId: null,
  targetStoreId:    null,
})

const emit = defineEmits<{
  (e: 'update:reference-store', id: number | null): void
  (e: 'update:target-store',    id: number | null): void
}>()

function onRefStoreChange(event: Event) {
  const val = (event.target as HTMLSelectElement).value
  emit('update:reference-store', val ? Number(val) : null)
}
function onTargetStoreChange(event: Event) {
  const val = (event.target as HTMLSelectElement).value
  emit('update:target-store', val ? Number(val) : null)
}
</script>

