<template>
  <div class="panel-header" style="flex-wrap: wrap; gap: 8px; margin-bottom: 16px;">
    <h2 class="panel-title">Мапінги категорій</h2>
    <div class="panel-actions" style="flex-wrap: wrap; gap: 8px;">

      <!-- Store selectors -->
      <div class="inline-inputs" style="margin-bottom: 0;">
        <div class="form-group" style="margin-bottom: 0;">
          <label for="mapp-ref-store">Reference store</label>
          <select
            id="mapp-ref-store"
            :value="refStoreId ?? ''"
            @change="onRefChange"
          >
            <option value="">— оберіть —</option>
            <option v-for="s in stores" :key="s.id" :value="s.id">
              {{ s.name }}{{ s.is_reference ? ' ★' : '' }}
            </option>
          </select>
        </div>
        <div class="form-group" style="margin-bottom: 0;">
          <label for="mapp-tgt-store">Target store</label>
          <select
            id="mapp-tgt-store"
            :value="targetStoreId ?? ''"
            @change="onTargetChange"
          >
            <option value="">— оберіть —</option>
            <option v-for="s in stores" :key="s.id" :value="s.id">
              {{ s.name }}{{ s.is_reference ? ' ★' : '' }}
            </option>
          </select>
        </div>
      </div>

      <!-- Action buttons -->
      <button
        class="btn"
        type="button"
        :disabled="!bothSelected"
        @click="$emit('create')"
      >+ Створити мапінг</button>

      <button
        class="btn-ghost"
        type="button"
        :disabled="!bothSelected || autoLinkBusy"
        title="Авто-маппінг за нормалізованою назвою категорії"
        @click="$emit('auto-link')"
      >
        {{ autoLinkBusy ? '⏳ Авто-маппінг…' : '⚡ Авто-маппінг за назвою' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { StoreSummary } from '@/types/store'

interface Props {
  stores: StoreSummary[]
  refStoreId: number | null
  targetStoreId: number | null
  autoLinkBusy?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  autoLinkBusy: false,
})

const emit = defineEmits<{
  (e: 'update:refStoreId', id: number | null): void
  (e: 'update:targetStoreId', id: number | null): void
  (e: 'create'): void
  (e: 'auto-link'): void
}>()

const bothSelected = computed(() => !!props.refStoreId && !!props.targetStoreId)

function onRefChange(ev: Event) {
  const val = (ev.target as HTMLSelectElement).value
  emit('update:refStoreId', val ? Number(val) : null)
}

function onTargetChange(ev: Event) {
  const val = (ev.target as HTMLSelectElement).value
  emit('update:targetStoreId', val ? Number(val) : null)
}
</script>

