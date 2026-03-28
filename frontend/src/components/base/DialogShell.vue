<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="dialog-backdrop"
      role="dialog"
      :aria-modal="true"
      :aria-labelledby="titleId"
      @keydown.esc="$emit('close')"
    >
      <div class="dialog-shell" @click.stop>
        <!-- Header -->
        <div class="dialog-header">
          <span :id="titleId" class="dialog-title">
            <slot name="title">{{ title }}</slot>
          </span>
          <button
            class="btn-ghost btn-sm dialog-close"
            type="button"
            aria-label="Закрити"
            @click="$emit('close')"
          >✕</button>
        </div>

        <!-- Body -->
        <div class="dialog-body">
          <slot />
        </div>

        <!-- Footer -->
        <div v-if="$slots.footer" class="dialog-footer">
          <slot name="footer" />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
/**
 * DialogShell.vue — reusable dialog/modal shell primitive.
 *
 * Owns shell structure only (backdrop, header, footer, close button).
 * Dialog content is always provided via the default slot.
 *
 * Uses <Teleport to="body"> so dialogs render above the page shell.
 * Closes on Escape key and emits 'close' so the parent can react.
 *
 * Slots:
 *   default  — dialog body content
 *   title    — overrides the title prop
 *   footer   — optional footer (cancel / confirm buttons)
 *
 * Usage:
 *   <DialogShell :open="dialog.isOpen.value" title="Редагування задачі" @close="dialog.close()">
 *     <JobEditForm :job="dialog.payload.value" @saved="dialog.close()" />
 *     <template #footer>
 *       <BaseButton variant="outline" @click="dialog.close()">Скасувати</BaseButton>
 *       <BaseButton type="submit" form="job-form">Зберегти</BaseButton>
 *     </template>
 *   </DialogShell>
 */
import { computed } from 'vue'

interface Props {
  open: boolean
  title?: string
}

withDefaults(defineProps<Props>(), {
  title: '',
})

defineEmits<{
  (e: 'close'): void
}>()

// Stable element id for aria-labelledby
const titleId = computed(() => `dialog-title-${Math.random().toString(36).slice(2, 7)}`)
</script>

<style scoped>
.dialog-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog-shell {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.18);
  min-width: 360px;
  max-width: 680px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px 12px;
  border-bottom: 1px solid #e5e7eb;
}

.dialog-title {
  font-weight: 700;
  font-size: 1rem;
}

.dialog-close {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
  color: #6b7280;
  line-height: 1;
  padding: 2px 6px;
}

.dialog-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.dialog-footer {
  padding: 12px 20px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}
</style>

