<template>
  <DialogShell
    :open="open"
    :title="mode === 'create' ? 'Новий мапінг' : 'Редагувати мапінг'"
    @close="$emit('close')"
  >
    <form id="mapping-dialog-form" autocomplete="off" @submit.prevent="onSubmit">

      <!-- Reference category -->
      <div class="form-group">
        <label for="md-ref-cat">Категорія (reference)</label>
        <select
          id="md-ref-cat"
          v-model="form.reference_category_id"
          required
          :disabled="mode === 'edit'"
        >
          <option value="">— оберіть категорію —</option>
          <option v-for="c in refCategories" :key="c.id" :value="String(c.id)">
            {{ c.name }}
          </option>
        </select>
      </div>

      <!-- Target category -->
      <div class="form-group">
        <label for="md-tgt-cat">Категорія (target)</label>
        <select
          id="md-tgt-cat"
          v-model="form.target_category_id"
          required
          :disabled="mode === 'edit'"
        >
          <option value="">— оберіть категорію —</option>
          <option v-for="c in targetCategories" :key="c.id" :value="String(c.id)">
            {{ c.name }}
          </option>
        </select>
        <p v-if="mode === 'edit'" class="field-help">
          Пара категорій незмінна при редагуванні.
        </p>
      </div>

      <!-- Match type -->
      <div class="form-group">
        <label for="md-match-type">Тип відповідності</label>
        <input
          id="md-match-type"
          v-model="form.match_type"
          placeholder="manual / auto / exact"
        />
      </div>

      <!-- Confidence -->
      <div class="form-group">
        <label for="md-confidence">Confidence (0–1)</label>
        <input
          id="md-confidence"
          type="number"
          min="0"
          max="1"
          step="0.01"
          v-model="form.confidence"
          placeholder="наприклад: 0.95"
        />
      </div>

      <p v-if="errorMsg" class="field-error" style="margin-top: 10px;">{{ errorMsg }}</p>
    </form>

    <template #footer>
      <button class="btn-ghost" type="button" @click="$emit('close')">Скасувати</button>
      <button class="btn" type="submit" form="mapping-dialog-form" :disabled="pending">
        {{ pending ? 'Збереження…' : 'Зберегти' }}
      </button>
    </template>
  </DialogShell>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import DialogShell from '@/components/base/DialogShell.vue'
import type { CategorySummary } from '@/types/store'
import type { MappingRow, MappingFormModel } from '@/types/mappings'

interface Props {
  open: boolean
  mode: 'create' | 'edit'
  mapping?: MappingRow | null
  refCategories: CategorySummary[]
  targetCategories: CategorySummary[]
  pending?: boolean
  errorMsg?: string | null
}

const props = withDefaults(defineProps<Props>(), {
  mapping: null,
  pending: false,
  errorMsg: null,
})

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'submit', form: MappingFormModel): void
}>()

function emptyForm(): MappingFormModel {
  return { reference_category_id: '', target_category_id: '', match_type: '', confidence: '' }
}

const form = ref<MappingFormModel>(emptyForm())

watch(() => props.open, (isOpen) => {
  if (!isOpen) return
  if (props.mode === 'edit' && props.mapping) {
    form.value = {
      reference_category_id: String(props.mapping.reference_category_id),
      target_category_id: String(props.mapping.target_category_id),
      match_type: props.mapping.match_type ?? '',
      confidence: props.mapping.confidence != null ? String(props.mapping.confidence) : '',
    }
  } else {
    form.value = emptyForm()
  }
})

function onSubmit() {
  emit('submit', { ...form.value })
}
</script>

