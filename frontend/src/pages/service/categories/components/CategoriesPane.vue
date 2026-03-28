<template>
  <div class="categories-pane">
    <!-- Store selector -->
    <div class="form-group">
      <label :for="`store-select-${kind}`">
        {{ kind === 'reference' ? 'Референсний магазин' : 'Цільовий магазин' }}
      </label>
      <select
        :id="`store-select-${kind}`"
        :value="selectedStoreId ?? ''"
        @change="onStoreChange"
      >
        <option value="">Оберіть</option>
        <option v-for="s in stores" :key="s.id" :value="s.id">
          {{ s.name }}{{ s.is_reference ? ' (ref)' : '' }}
        </option>
      </select>
    </div>

    <!-- Sync action -->
    <div class="panel-actions" style="margin-top:10px;">
      <button
        class="btn"
        type="button"
        :disabled="!selectedStoreId || syncLoading"
        @click="emit('sync-categories')"
      >
        {{ syncLoading ? '⏳ Синхронізація…' : 'Синхронізувати категорії' }}
      </button>
    </div>

    <!-- Status pill -->
    <div
      :class="['status-pill', `status-${statusKind}`, 'categories-status']"
      style="margin-top:12px;"
      role="status"
    >
      {{ statusText }}
    </div>

    <!-- Categories table -->
    <CategoryTable
      :categories="categories"
      :loading="loading"
      :sync-products-loading-id="syncProductsLoadingId"
      style="margin-top:12px;"
      @sync-products="emit('sync-products', $event)"
    />
  </div>
</template>

<script setup lang="ts">
/**
 * CategoriesPane.vue — one side of the two-pane categories layout.
 *
 * Renders the store selector, sync button, status pill, and category table
 * for either the reference or target store side.
 *
 * Props mirror the PaneState shape from useServiceCategories.
 * All actions are handled by the parent via emitted events.
 */
import CategoryTable from './CategoryTable.vue'
import type { StoreSummary, CategorySummary } from '@/types/store'
import type { StatusKind } from '@/types/common'

interface Props {
  kind: 'reference' | 'target'
  stores: StoreSummary[]
  selectedStoreId: number | null
  categories: CategorySummary[]
  loading: boolean
  statusText: string
  statusKind: StatusKind
  syncLoading: boolean
  syncProductsLoadingId: number | null
}

withDefaults(defineProps<Props>(), {
  stores: () => [],
  categories: () => [],
  loading: false,
  syncLoading: false,
  syncProductsLoadingId: null,
})

const emit = defineEmits<{
  (e: 'update:selected-store-id', id: number | null): void
  (e: 'sync-categories'): void
  (e: 'sync-products', categoryId: number): void
}>()

function onStoreChange(event: Event) {
  const val = (event.target as HTMLSelectElement).value
  emit('update:selected-store-id', val ? Number(val) : null)
}
</script>

<style scoped>
.categories-pane {
  display: flex;
  flex-direction: column;
}
.categories-status {
  display: inline-block;
}
</style>

