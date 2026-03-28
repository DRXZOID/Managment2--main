<template>
  <span v-if="percent != null" class="tooltip-wrap">
    <span :class="['score-pill', scoreClass]">{{ percent }}%</span>
    <span v-if="tooltipText" class="tooltip-box">{{ tooltipText }}</span>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  percent: number | null | undefined
  details: Record<string, unknown> | null | undefined
}
const props = withDefaults(defineProps<Props>(), { percent: null, details: null })

const scoreClass = computed(() => {
  if (props.percent == null) return ''
  if (props.percent >= 85) return ''
  if (props.percent >= 65) return 'medium'
  return 'low'
})

const tooltipText = computed(() =>
  props.details ? JSON.stringify(props.details, null, 2) : '',
)
</script>

