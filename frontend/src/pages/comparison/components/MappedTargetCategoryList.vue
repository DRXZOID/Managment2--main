<template>
  <div>
    <p v-if="loading" class="muted">Завантаження маппінгів…</p>

    <p v-else-if="!selectedCategoryId" class="muted">
      Оберіть категорію референсного магазину
    </p>

    <!-- No mappings warning -->
    <p
      v-else-if="noMappingsWarning"
      class="muted"
      style="color:#92400e;background:#fef3c7;padding:10px 12px;border-radius:8px;"
    >
      ⚠️ Для цієї категорії ще не створено меппінг.
      Перейдіть на <a href="/service" style="color:var(--accent);">сервісну сторінку</a>
      для створення маппінгу або запустіть авто-маппінг.
    </p>

    <!-- Checkbox list -->
    <div
      v-for="t in mappedTargets"
      :key="t.target_category_id"
      class="mapped-target-item"
    >
      <input
        :id="`tgt_${t.target_category_id}`"
        type="checkbox"
        :checked="selectedIds.has(t.target_category_id)"
        @change="onToggle(t.target_category_id, ($event.target as HTMLInputElement).checked)"
      />
      <label
        :for="`tgt_${t.target_category_id}`"
        style="cursor:pointer;font-weight:normal;margin:0;flex:1;"
      >
        <strong>
          {{ t.target_category_name }}
          <span
            v-if="t.match_type"
            style="font-size:0.75rem;background:#e0e7ff;color:#3730a3;padding:1px 7px;border-radius:999px;"
          >{{ t.match_type }}</span>
        </strong>
        <div class="muted">{{ t.target_store_name ?? '' }}</div>
      </label>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * MappedTargetCategoryList.vue — checkbox list of mapped target categories.
 * Emits 'toggle' with (id, checked) when a checkbox changes.
 */
import type { MappedTarget } from '../types'

interface Props {
  mappedTargets: MappedTarget[]
  selectedIds: Set<number>
  selectedCategoryId: number | null
  loading: boolean
  noMappingsWarning: boolean
}
withDefaults(defineProps<Props>(), {
  mappedTargets:    () => [],
  selectedIds:      () => new Set(),
  selectedCategoryId: null,
  loading:          false,
  noMappingsWarning: false,
})

const emit = defineEmits<{
  (e: 'toggle', id: number, checked: boolean): void
}>()

function onToggle(id: number, checked: boolean) {
  emit('toggle', id, checked)
}
</script>

