<template>
  <template v-if="product?.product_url">
    <a class="link-btn" :href="product.product_url" target="_blank" rel="noopener">
      {{ product.name ?? '—' }}
    </a>
  </template>
  <template v-else>{{ product?.name ?? '—' }}</template>
</template>

<script setup lang="ts">
import type { ComparisonProduct } from '../../types'
interface Props { product: ComparisonProduct | null | undefined }
defineProps<Props>()
</script>

