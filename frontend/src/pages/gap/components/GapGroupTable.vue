<template>
  <div class="group-block panel">
    <!-- Group header -->
    <div class="group-header">
      <h3>{{ group.target_category?.name ?? '—' }}</h3>
      <span class="badge badge-cat">{{ group.count }} товарів</span>
    </div>

    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Назва</th>
            <th>Ціна</th>
            <th>Наявність</th>
            <th>Статус</th>
            <th>Дія</th>
            <th>Посилання</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in group.items" :key="item.target_product?.id ?? String(Math.random())">
            <td>{{ item.target_product?.name ?? '—' }}</td>
            <td class="price-cell">{{ formatPrice(item.target_product) }}</td>
            <td>
              <span v-if="item.target_product?.is_available" class="avail-yes">✓ є</span>
              <span v-else class="avail-no">✗ нема</span>
            </td>
            <td>
              <span :class="['badge', `badge-${item.status}`]">
                {{ statusLabel(item.status) }}
              </span>
            </td>
            <td>
              <button
                v-if="item.status === 'new'"
                class="btn btn-sm btn-action-take"
                type="button"
                :disabled="actionInProgressId === item.target_product?.id"
                @click="item.target_product && emit('action', refCategoryId, item.target_product.id, 'in_progress')"
              >
                {{ actionInProgressId === item.target_product?.id ? '…' : 'Взяти в роботу' }}
              </button>
              <button
                v-else-if="item.status === 'in_progress'"
                class="btn btn-sm btn-action-done"
                type="button"
                :disabled="actionInProgressId === item.target_product?.id"
                @click="item.target_product && emit('action', refCategoryId, item.target_product.id, 'done')"
              >
                {{ actionInProgressId === item.target_product?.id ? '…' : 'Позначити опрацьованим' }}
              </button>
              <span v-else class="badge badge-done">✓</span>
            </td>
            <td>
              <a
                v-if="item.target_product?.product_url"
                class="link-ext"
                :href="item.target_product.product_url"
                target="_blank"
                rel="noopener"
              >↗</a>
              <span v-else>—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * GapGroupTable.vue — one grouped result block for a target category.
 * Emits 'action' with (refCatId, targetProductId, newStatus) on row button click.
 */
import type { GapGroup, GapItemStatus, GapProduct } from '@/types/gap'

interface Props {
  group: GapGroup
  refCategoryId: number
  actionInProgressId: number | null
}

withDefaults(defineProps<Props>(), { actionInProgressId: null })

const emit = defineEmits<{
  (e: 'action', refCatId: number, targetProductId: number, status: GapItemStatus): void
}>()

function formatPrice(p: GapProduct | null | undefined): string {
  if (!p) return '—'
  const v = p.price
  if (v == null || v === '') return '—'
  const num = typeof v === 'string' ? parseFloat(v) : v
  if (isNaN(num)) return String(v)
  return p.currency ? `${num.toFixed(2)} ${p.currency}` : num.toFixed(2)
}

function statusLabel(status: GapItemStatus): string {
  return ({ new: 'Новий', in_progress: 'В роботі', done: 'Опрацьовано' } as Record<string, string>)[status] ?? status
}
</script>

