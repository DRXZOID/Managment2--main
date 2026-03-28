<template>
  <select
    :value="modelValue"
    :disabled="disabled"
    :class="['form-select', { 'form-select--loading': loading }]"
    v-bind="$attrs"
    @change="onchange"
  >
    <option v-if="placeholder" value="">{{ placeholder }}</option>
    <option
      v-for="opt in options"
      :key="opt.value"
      :value="opt.value"
      :disabled="opt.disabled ?? false"
    >
      {{ opt.label }}
    </option>
  </select>
</template>

<script setup lang="ts">
/**
 * BaseSelect.vue — reusable select primitive.
 *
 * Designed to be used wherever the existing pages render <select> controls —
 * primarily the scheduler job form (store/category pickers) and filter bars.
 *
 * Uses v-model via modelValue + update:modelValue emit pattern.
 *
 * Usage:
 *   <BaseSelect
 *     v-model="selectedStoreId"
 *     :options="storeOptions"
 *     placeholder="— оберіть магазин —"
 *   />
 */

export interface SelectOption {
  value: string | number
  label: string
  disabled?: boolean
}

interface Props {
  modelValue: string | number | null | undefined
  options: SelectOption[]
  placeholder?: string
  disabled?: boolean
  loading?: boolean
}

withDefaults(defineProps<Props>(), {
  placeholder: undefined,
  disabled: false,
  loading: false,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | number): void
}>()

function onchange(event: Event): void {
  const target = event.target as HTMLSelectElement
  emit('update:modelValue', target.value)
}
</script>

