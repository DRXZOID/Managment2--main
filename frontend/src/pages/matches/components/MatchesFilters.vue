<template>
  <div>
    <h2>Фільтри</h2>
    <div class="filter-grid">

      <!-- Reference store -->
      <div class="form-group">
        <label for="refStoreFilter">Референсний магазин</label>
        <select
          id="refStoreFilter"
          :value="filters.referenceStoreId ?? ''"
          @change="onRefStoreChange"
        >
          <option value="">— всі —</option>
          <option v-for="s in referenceStores" :key="s.id" :value="s.id">
            {{ s.name }}
          </option>
        </select>
      </div>

      <!-- Reference category -->
      <div class="form-group">
        <label for="refCatFilter">Референсна категорія</label>
        <select
          id="refCatFilter"
          :value="filters.referenceCategoryId ?? ''"
          @change="v => emit('update:reference-category-id', numOrNull((v.target as HTMLSelectElement).value))"
        >
          <option value="">— всі —</option>
          <option v-for="c in referenceCategories" :key="c.id" :value="c.id">
            {{ c.name }}
          </option>
        </select>
      </div>

      <!-- Target store -->
      <div class="form-group">
        <label for="tgtStoreFilter">Цільовий магазин</label>
        <select
          id="tgtStoreFilter"
          :value="filters.targetStoreId ?? ''"
          @change="onTgtStoreChange"
        >
          <option value="">— всі —</option>
          <option v-for="s in targetStores" :key="s.id" :value="s.id">
            {{ s.name }}
          </option>
        </select>
      </div>

      <!-- Target category -->
      <div class="form-group">
        <label for="tgtCatFilter">Цільова категорія</label>
        <select
          id="tgtCatFilter"
          :value="filters.targetCategoryId ?? ''"
          @change="v => emit('update:target-category-id', numOrNull((v.target as HTMLSelectElement).value))"
        >
          <option value="">— всі —</option>
          <option v-for="c in targetCategories" :key="c.id" :value="c.id">
            {{ c.name }}
          </option>
        </select>
      </div>

      <!-- Status -->
      <div class="form-group">
        <label for="statusFilter">Статус</label>
        <select
          id="statusFilter"
          :value="filters.status"
          @change="v => emit('update:status', (v.target as HTMLSelectElement).value)"
        >
          <option value="confirmed">Підтверджені</option>
          <option value="rejected">Відхилені</option>
          <option value="">Всі</option>
        </select>
      </div>

      <!-- Search -->
      <div class="form-group">
        <label for="searchFilter">Пошук за назвою</label>
        <input
          id="searchFilter"
          type="text"
          :value="filters.search"
          placeholder="напр. Bauer Vapor…"
          @input="v => emit('update:search', (v.target as HTMLInputElement).value)"
          @keydown.enter="emit('load')"
        >
      </div>

    </div>

    <div class="form-actions" style="justify-content:flex-start; margin-top:18px;">
      <button class="btn" type="button" :disabled="loading" @click="emit('load')">
        Показати
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * MatchesFilters.vue — filter panel for the /matches page.
 *
 * Renders all filter controls and emits fine-grained change events upward.
 * Does not own filter state — parent (MatchesPage) is the single source of truth.
 */
import type { StoreSummary, CategorySummary } from '@/types/store'
import type { MatchesFilters } from '@/types/matches'

interface Props {
  referenceStores: StoreSummary[]
  targetStores: StoreSummary[]
  referenceCategories: CategorySummary[]
  targetCategories: CategorySummary[]
  filters: MatchesFilters
  loading?: boolean
}

withDefaults(defineProps<Props>(), {
  referenceStores: () => [],
  targetStores: () => [],
  referenceCategories: () => [],
  targetCategories: () => [],
  loading: false,
})

const emit = defineEmits<{
  (e: 'update:reference-store', id: number | null): void
  (e: 'update:target-store', id: number | null): void
  (e: 'update:reference-category-id', id: number | null): void
  (e: 'update:target-category-id', id: number | null): void
  (e: 'update:status', status: string): void
  (e: 'update:search', search: string): void
  (e: 'load'): void
}>()

function numOrNull(val: string): number | null {
  return val ? Number(val) : null
}

function onRefStoreChange(event: Event) {
  emit('update:reference-store', numOrNull((event.target as HTMLSelectElement).value))
}

function onTgtStoreChange(event: Event) {
  emit('update:target-store', numOrNull((event.target as HTMLSelectElement).value))
}
</script>

