<template>
  <span :class="['status-pill', kindClass]">
    <slot>{{ label }}</slot>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { StatusKind } from '@/types/common'

interface Props {
  kind: StatusKind
  label?: string
}

const props = withDefaults(defineProps<Props>(), {
  label: '',
})

const KIND_CSS: Record<StatusKind, string> = {
  info:    'status-info',
  success: 'status-success',
  warning: 'status-warning',
  error:   'status-error',
  muted:   'status-muted',
}

const kindClass = computed(() => KIND_CSS[props.kind] ?? 'status-info')
</script>

