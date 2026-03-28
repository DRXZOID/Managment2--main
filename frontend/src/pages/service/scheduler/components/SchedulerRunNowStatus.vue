<template>
  <div
    v-if="status.kind !== 'idle'"
    :class="['status-block', blockClass]"
    style="margin-bottom: 12px;"
    role="status"
    aria-live="polite"
  >
    {{ status.message }}
    <button
      class="btn-ghost btn-sm"
      style="float: right; margin-top: -2px;"
      type="button"
      aria-label="Закрити"
      @click="$emit('clear')"
    >✕</button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ActionStatus } from '../composables/useSchedulerActions'

interface Props {
  status: ActionStatus
}
const props = defineProps<Props>()
defineEmits<{ (e: 'clear'): void }>()

const blockClass = computed(() => {
  const map: Record<string, string> = {
    pending:  'info',
    success:  'success',
    error:    'error',
    conflict: 'warn',
  }
  return map[props.status.kind] ?? 'info'
})
</script>

