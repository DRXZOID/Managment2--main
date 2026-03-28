<template>
  <div>
    <!-- Empty state -->
    <p v-if="categories.length === 0" class="muted">
      {{ loading ? 'Завантаження…' : 'Немає категорій. Синхронізуйте дані.' }}
    </p>

    <!-- Table -->
    <div v-else class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Назва</th>
            <th>Оновлено</th>
            <th>Продукти</th>
            <th>URL</th>
            <th>Дії</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="cat in categories" :key="cat.id">
            <td>{{ cat.name }}</td>
            <td>{{ cat.updated_at ? new Date(cat.updated_at).toLocaleString() : '—' }}</td>
            <td>{{ cat.product_count ?? 0 }}</td>
            <td>
              <a
                v-if="cat.url"
                :href="cat.url"
                target="_blank"
                rel="noopener"
              >Відкрити</a>
              <span v-else>—</span>
            </td>
            <td>
              <button
                class="btn-ghost btn-sm"
                type="button"
                :disabled="syncProductsLoadingId === cat.id"
                @click="emit('sync-products', cat.id)"
              >
                {{ syncProductsLoadingId === cat.id ? '⏳' : 'Синхронізувати товари' }}
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
 * CategoryTable.vue — renders a single-store category list.
 *
 * Emits 'sync-products' with category id when the row button is clicked.
 */
import type { CategorySummary } from '@/types/store'

interface Props {
  categories: CategorySummary[]
  loading?: boolean
  syncProductsLoadingId?: number | null
}

withDefaults(defineProps<Props>(), {
  loading: false,
  syncProductsLoadingId: null,
})

const emit = defineEmits<{
  (e: 'sync-products', categoryId: number): void
}>()
</script>

