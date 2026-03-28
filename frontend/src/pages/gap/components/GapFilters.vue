<template>
  <div>
    <h2>Параметри перегляду</h2>

    <div class="filter-grid">

      <!-- Target store -->
      <div class="form-group">
        <label for="targetStoreSelect">Цільовий магазин</label>
        <select id="targetStoreSelect" :value="selectedTargetStoreId ?? ''" @change="onTargetStoreChange">
          <option value="">— оберіть магазин —</option>
          <option v-for="s in targetStores" :key="s.id" :value="s.id">{{ s.name }}</option>
        </select>
      </div>

      <!-- Reference category -->
      <div class="form-group">
        <label for="refCategorySelect">Референсна категорія</label>
        <select
          id="refCategorySelect"
          :value="selectedRefCategoryId ?? ''"
          :disabled="!selectedTargetStoreId || refCategoriesLoading"
          @change="onRefCategoryChange"
        >
          <option v-if="!selectedTargetStoreId" value="">— спочатку оберіть магазин —</option>
          <option v-else-if="refCategoriesLoading" value="">— завантаження… —</option>
          <option v-else value="">— оберіть категорію —</option>
          <option v-for="c in referenceCategories" :key="c.id" :value="c.id">
            {{ c.name }}{{ c.product_count ? ` (${c.product_count})` : '' }}
          </option>
        </select>
      </div>

      <!-- Mapped target categories checkboxes -->
      <div class="form-group">
        <label>Цільові категорії (з маппінгів)</label>
        <div class="multi-select-container">
          <span v-if="mappedCatsLoading" class="muted">Завантаження маппінгів…</span>
          <span v-else-if="!selectedRefCategoryId" class="muted">Оберіть референсну категорію</span>
          <span v-else-if="noMappingsWarning" class="muted">Немає маппінгів для цієї категорії</span>
          <template v-else>
            <label
              v-for="cat in mappedTargetCats"
              :key="cat.target_category_id"
              class="multi-select-item"
            >
              <input
                type="checkbox"
                :value="cat.target_category_id"
                :checked="selectedTargetCatIds.has(cat.target_category_id)"
                @change="emit('toggle-target-cat', cat.target_category_id, ($event.target as HTMLInputElement).checked)"
              >
              <span>{{ cat.target_category_name }}</span>
            </label>
          </template>
        </div>
      </div>

      <!-- Search -->
      <div class="form-group">
        <label for="searchInput">Пошук за назвою</label>
        <input
          id="searchInput"
          type="text"
          :value="search"
          placeholder="напр. Bauer Vapor…"
          @input="emit('update:search', ($event.target as HTMLInputElement).value)"
          @keydown.enter="emit('load')"
        >
      </div>

      <!-- Only available -->
      <div class="form-group">
        <label>Фільтри</label>
        <div class="checkbox-group">
          <label class="checkbox-row">
            <input
              type="checkbox"
              :checked="onlyAvailable"
              @change="emit('update:only-available', ($event.target as HTMLInputElement).checked)"
            >
            Лише в наявності
          </label>
        </div>
      </div>

      <!-- Status filters -->
      <div class="form-group">
        <label>Статуси</label>
        <div class="checkbox-group">
          <label class="checkbox-row">
            <input type="checkbox" :checked="statuses.new"
              @change="emit('update:status-new', ($event.target as HTMLInputElement).checked)">
            Нові
          </label>
          <label class="checkbox-row">
            <input type="checkbox" :checked="statuses.in_progress"
              @change="emit('update:status-in-progress', ($event.target as HTMLInputElement).checked)">
            В роботі
          </label>
          <label class="checkbox-row">
            <input type="checkbox" :checked="statuses.done"
              @change="emit('update:status-done', ($event.target as HTMLInputElement).checked)">
            Опрацьовано
          </label>
        </div>
      </div>

    </div>

    <div class="form-actions" style="justify-content:flex-start; margin-top:18px;">
      <button class="btn" type="button" :disabled="!canLoad || loading" @click="emit('load')">
        Показати розрив
      </button>
      <span v-if="noMappingsWarning" style="color:#92400e;font-size:0.9rem;">
        ⚠️ Для цієї категорії немає маппінгів — налаштуйте їх на
        <a href="/service">сервісній сторінці</a>.
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * GapFilters.vue — filter panel for the /gap page.
 * Renders the three-stage cascade selectors, checkboxes, and action button.
 * All state is owned by the parent (GapPage); this component only emits.
 */
import type { StoreSummary, CategorySummary } from '@/types/store'
import type { MappedTargetCategory } from '@/types/gap'
import type { GapStatusFilters } from '../composables/useGapFilters'

interface Props {
  targetStores: StoreSummary[]
  referenceCategories: CategorySummary[]
  mappedTargetCats: MappedTargetCategory[]
  selectedTargetStoreId: number | null
  selectedRefCategoryId: number | null
  selectedTargetCatIds: Set<number>
  search: string
  onlyAvailable: boolean
  statuses: GapStatusFilters
  refCategoriesLoading: boolean
  mappedCatsLoading: boolean
  noMappingsWarning: boolean
  canLoad: boolean
  loading: boolean
}

withDefaults(defineProps<Props>(), {
  targetStores: () => [],
  referenceCategories: () => [],
  mappedTargetCats: () => [],
  selectedTargetStoreId: null,
  selectedRefCategoryId: null,
  loading: false,
  refCategoriesLoading: false,
  mappedCatsLoading: false,
  noMappingsWarning: false,
  canLoad: false,
})

const emit = defineEmits<{
  (e: 'update:target-store', id: number | null): void
  (e: 'update:ref-category', id: number | null): void
  (e: 'toggle-target-cat', id: number, checked: boolean): void
  (e: 'update:search', v: string): void
  (e: 'update:only-available', v: boolean): void
  (e: 'update:status-new', v: boolean): void
  (e: 'update:status-in-progress', v: boolean): void
  (e: 'update:status-done', v: boolean): void
  (e: 'load'): void
}>()

function onTargetStoreChange(event: Event) {
  const val = (event.target as HTMLSelectElement).value
  emit('update:target-store', val ? Number(val) : null)
}

function onRefCategoryChange(event: Event) {
  const val = (event.target as HTMLSelectElement).value
  emit('update:ref-category', val ? Number(val) : null)
}
</script>

