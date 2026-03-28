<template>
  <div class="pagination">
    <button
      class="btn-ghost"
      type="button"
      :disabled="disabled || page === 0"
      @click="emit('prev')"
    >Назад</button>

    <span>Сторінка {{ page + 1 }}</span>

    <button
      class="btn-ghost"
      type="button"
      :disabled="disabled || !hasNext"
      @click="emit('next')"
    >Вперед</button>
  </div>
</template>

<script setup lang="ts">
/**
 * HistoryPagination.vue — prev/next pagination controls.
 *
 * Props:
 *   page      — zero-based current page index
 *   pageSize  — items per page
 *   itemCount — number of items in the current page (used to derive hasNext)
 *   disabled  — disable all buttons (e.g. while loading)
 *
 * Emits: prev, next
 */
import { computed } from 'vue'

interface Props {
  page: number
  pageSize: number
  itemCount: number
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
})

const emit = defineEmits<{
  (e: 'prev'): void
  (e: 'next'): void
}>()

// If we got a full page, there may be more data.
const hasNext = computed(() => props.itemCount >= props.pageSize)
</script>

