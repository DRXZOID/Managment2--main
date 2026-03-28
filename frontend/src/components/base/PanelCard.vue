<template>
  <div class="panel vue-island">
    <div v-if="hasHeader" class="panel-header">
      <span class="panel-title">
        <slot name="title">{{ title }}</slot>
      </span>
      <div v-if="$slots.actions" class="panel-actions">
        <slot name="actions" />
      </div>
    </div>
    <div class="panel-body">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * PanelCard.vue — section panel wrapper primitive.
 *
 * Maps to the existing CSS structure from static/css/common.css:
 *   .panel, .panel-header, .panel-title, .panel-actions
 *
 * The .vue-island class is added for scoping purposes (see base.css).
 *
 * Slots:
 *   default  — panel body content
 *   title    — panel header title (overrides the title prop)
 *   actions  — right-aligned header action buttons
 *
 * Usage:
 *   <PanelCard title="Scheduler Jobs">
 *     <template #actions>
 *       <BaseButton size="sm">+ Новий</BaseButton>
 *     </template>
 *     <JobTable :jobs="jobs" />
 *   </PanelCard>
 */
import { computed, useSlots } from 'vue'

interface Props {
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
})

const slots = useSlots()
const hasHeader = computed(() => !!(props.title || slots.title || slots.actions))
</script>

