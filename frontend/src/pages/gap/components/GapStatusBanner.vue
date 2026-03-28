<template>
  <div
    v-if="visible"
    :class="['status-block', kind]"
    role="status"
    :aria-live="kind === 'error' ? 'assertive' : 'polite'"
  >
    {{ message }}
  </div>
</template>

<script setup lang="ts">
/** GapStatusBanner.vue — loading / error / empty state banner. */
import { computed } from 'vue'

interface Props {
  loading: boolean
  error: string | null
  isEmpty: boolean
  hasLoaded: boolean
  storesError: string | null
}

const props = withDefaults(defineProps<Props>(), {
  error: null,
  storesError: null,
})

const visible = computed(
  () => props.loading || !!props.error || !!props.storesError || (props.hasLoaded && props.isEmpty),
)

const kind = computed(() => {
  if (props.error || props.storesError) return 'error'
  if (props.loading) return 'info'
  return 'info'
})

const message = computed(() => {
  if (props.storesError) return props.storesError
  if (props.loading) return 'Завантаження…'
  if (props.error) return props.error
  if (props.hasLoaded && props.isEmpty) return 'Розрив відсутній або всі товари відфільтровані.'
  return ''
})
</script>

