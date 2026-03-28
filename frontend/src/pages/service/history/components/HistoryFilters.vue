<template>
  <div class="inline-inputs">
    <!-- Store filter -->
    <div class="form-group">
      <label for="hw-store-filter">Магазин</label>
      <select
        id="hw-store-filter"
        :value="storeId"
        @change="emit('update:storeId', ($event.target as HTMLSelectElement).value)"
      >
        <option value="">Будь-який</option>
        <option v-for="s in stores" :key="s.id" :value="String(s.id)">
          {{ s.name }}{{ s.is_reference ? ' (ref)' : '' }}
        </option>
      </select>
    </div>

    <!-- Run type filter -->
    <div class="form-group">
      <label for="hw-type-filter">Тип</label>
      <select
        id="hw-type-filter"
        :value="runType"
        @change="emit('update:runType', ($event.target as HTMLSelectElement).value)"
      >
        <option value="">Будь-який</option>
        <option value="categories">Категорії</option>
        <option value="category_products">Категорійні товари</option>
        <option value="store_category_sync">store_category_sync</option>
        <option value="category_product_sync">category_product_sync</option>
        <option value="all_stores_category_sync">all_stores_category_sync</option>
      </select>
    </div>

    <!-- Status filter -->
    <div class="form-group">
      <label for="hw-status-filter">Статус</label>
      <select
        id="hw-status-filter"
        :value="status"
        @change="emit('update:status', ($event.target as HTMLSelectElement).value)"
      >
        <option value="">Будь-який</option>
        <option value="queued">Черга</option>
        <option value="running">В процесі</option>
        <option value="success">Успіх</option>
        <option value="finished">Завершено (legacy)</option>
        <option value="partial">Частково</option>
        <option value="failed">Помилка</option>
        <option value="skipped">Пропущено</option>
        <option value="cancelled">Скасовано</option>
      </select>
    </div>

    <!-- Trigger filter -->
    <div class="form-group">
      <label for="hw-trigger-filter">Тригер</label>
      <select
        id="hw-trigger-filter"
        :value="triggerType"
        @change="emit('update:triggerType', ($event.target as HTMLSelectElement).value)"
      >
        <option value="">Будь-який</option>
        <option value="manual">manual</option>
        <option value="scheduled">scheduled</option>
        <option value="retry">retry</option>
      </select>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * HistoryFilters.vue — four filter selects for the history tab.
 *
 * Emits v-model-compatible update events for each filter field.
 * Store options are provided by the parent via props.
 */
import type { StoreSummary } from '@/types/store'

interface Props {
  stores: StoreSummary[]
  storeId: string
  runType: string
  status: string
  triggerType: string
}

withDefaults(defineProps<Props>(), {
  stores: () => [],
  storeId: '',
  runType: '',
  status: '',
  triggerType: '',
})

const emit = defineEmits<{
  (e: 'update:storeId', value: string): void
  (e: 'update:runType', value: string): void
  (e: 'update:status', value: string): void
  (e: 'update:triggerType', value: string): void
}>()
</script>

