<template>
  <span v-if="cat" class="badge badge-cat">
    {{ cat.name ?? '' }}{{ cat.store_name ? ` · ${cat.store_name}` : '' }}
  </span>
</template>

<script setup lang="ts">
import type { ComparisonCategory } from '../../types'
interface Props { cat: ComparisonCategory | null | undefined }
defineProps<Props>()
</script>

