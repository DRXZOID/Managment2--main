<template>
  <div class="empty-state">
    <div v-if="icon" class="empty-state-icon" aria-hidden="true">{{ icon }}</div>
    <p class="empty-state-title">
      <slot name="title">{{ title }}</slot>
    </p>
    <p v-if="body || $slots.body" class="empty-state-body">
      <slot name="body">{{ body }}</slot>
    </p>
    <div v-if="$slots.action" class="empty-state-action" style="margin-top: 12px;">
      <slot name="action" />
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * EmptyState.vue — empty content state primitive.
 *
 * Maps to the existing CSS structure from static/css/common.css:
 *   .empty-state, .empty-state-icon, .empty-state-title, .empty-state-body
 *
 * Slots:
 *   default  — unused (prefer named slots)
 *   title    — overrides the title prop
 *   body     — overrides the body prop
 *   action   — optional call-to-action button area below the body text
 *
 * Usage:
 *   <EmptyState icon="🗓" title="Немає задач" body="Натисніть + щоб створити першу." />
 *
 *   <EmptyState icon="📭" title="Немає результатів">
 *     <template #action>
 *       <BaseButton @click="createJob">Створити задачу</BaseButton>
 *     </template>
 *   </EmptyState>
 */

interface Props {
  icon?: string
  title?: string
  body?: string
}

withDefaults(defineProps<Props>(), {
  icon: undefined,
  title: 'Нічого не знайдено',
  body: undefined,
})
</script>

