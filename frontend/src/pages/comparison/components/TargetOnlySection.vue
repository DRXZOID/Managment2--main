<template>
  <details class="collapsible">
    <summary>
      📦 Тільки в цільовому
      <span class="badge badge-tgt">{{ items.length }}</span>
    </summary>
    <div class="details-body">
      <p v-if="!items.length" class="muted">Немає товарів тільки в цільовому.</p>
      <table v-else>
        <thead>
          <tr><th>Назва</th><th>Ціна</th></tr>
        </thead>
        <tbody>
          <tr
            v-for="item in items"
            :key="item.target_product?.id ?? String(Math.random())"
          >
            <td>
              <ProductLink :product="item.target_product" />
              <CatBadge :cat="item.target_category" />
            </td>
            <td>{{ formatPrice(item.target_product) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </details>
</template>

<script setup lang="ts">
/**
 * TargetOnlySection.vue — collapsible target-only items table.
 */
import type { TargetOnlyItem } from '../types'
import ProductLink from './shared/ProductLink.vue'
import CatBadge from './shared/CatBadge.vue'
import { formatPrice } from './shared/format'

interface Props { items: TargetOnlyItem[] }
withDefaults(defineProps<Props>(), { items: () => [] })
</script>

