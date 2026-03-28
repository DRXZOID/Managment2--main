<template>
  <div class="panel-header" style="margin-bottom: 16px;">
    <strong class="panel-title">Scheduler</strong>
    <div class="panel-actions">
      <button
        class="btn"
        type="button"
        @click="$emit('create-job')"
      >+ Новий job</button>
      <button
        class="btn-ghost"
        type="button"
        :disabled="refreshing"
        title="Оновити список"
        @click="$emit('refresh')"
      >↺ Оновити</button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  refreshing?: boolean
}
withDefaults(defineProps<Props>(), { refreshing: false })
defineEmits<{
  (e: 'create-job'): void
  (e: 'refresh'): void
}>()
</script>

