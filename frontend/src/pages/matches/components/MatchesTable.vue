<template>
  <div class="table-wrapper">
    <table>
      <thead>
        <tr>
          <th>Референс (товар)</th>
          <th>Ціна</th>
          <th>Цільовий (товар)</th>
          <th>Ціна</th>
          <th>Статус</th>
          <th>Score</th>
          <th>Оновлено</th>
          <th>Дії</th>
        </tr>
      </thead>
      <tbody>
        <MatchesTableRow
          v-for="row in rows"
          :key="row.id"
          :row="row"
          :is-deleting-id="deletingId"
          @delete="emit('delete', $event)"
        />
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
/**
 * MatchesTable.vue — table shell for the matches page.
 * Delegates row rendering to MatchesTableRow.
 */
import MatchesTableRow from './MatchesTableRow.vue'
import type { ProductMappingRow } from '@/types/matches'

interface Props {
  rows: ProductMappingRow[]
  deletingId: number | null
}

withDefaults(defineProps<Props>(), {
  deletingId: null,
})

const emit = defineEmits<{
  (e: 'delete', mappingId: number): void
}>()
</script>

