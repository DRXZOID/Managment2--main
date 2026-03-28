<template>
  <button
    :class="['btn', variantClass, sizeClass, { 'btn--loading': loading }]"
    :disabled="disabled || loading"
    :type="type"
    v-bind="$attrs"
  >
    <span v-if="loading" class="btn-spinner" aria-hidden="true">⏳</span>
    <slot />
  </button>
</template>

<script setup lang="ts">
/**
 * BaseButton.vue — reusable button primitive.
 *
 * Maps to the existing CSS class system from static/css/common.css:
 *   variant="default"  → .btn
 *   variant="outline"  → .btn .btn-outline
 *   variant="danger"   → .btn .btn-danger
 *   variant="ghost"    → .btn .btn-ghost
 *
 *   size="md"  → .btn         (default)
 *   size="sm"  → .btn .btn-sm
 *
 * Usage:
 *   <BaseButton @click="save">Зберегти</BaseButton>
 *   <BaseButton variant="danger" :loading="deleting" @click="del">Видалити</BaseButton>
 *   <BaseButton variant="outline" size="sm" disabled>Недоступно</BaseButton>
 */

export type ButtonVariant = 'default' | 'outline' | 'danger' | 'ghost'
export type ButtonSize = 'md' | 'sm'
export type ButtonType = 'button' | 'submit' | 'reset'

interface Props {
  variant?: ButtonVariant
  size?: ButtonSize
  disabled?: boolean
  loading?: boolean
  type?: ButtonType
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'md',
  disabled: false,
  loading: false,
  type: 'button',
})

const VARIANT_CLASS: Record<ButtonVariant, string> = {
  default: '',
  outline: 'btn-outline',
  danger:  'btn-danger',
  ghost:   'btn-ghost',
}

const SIZE_CLASS: Record<ButtonSize, string> = {
  md: '',
  sm: 'btn-sm',
}

const variantClass = VARIANT_CLASS[props.variant]
const sizeClass    = SIZE_CLASS[props.size]
</script>

