<template>
  <div class="table-wrapper">
    <table class="data-table">
      <thead>
        <tr>
          <th
            v-for="col in columns"
            :key="col.key"
            :style="col.width ? { width: col.width } : undefined"
            :class="['data-table-th', col.align ? `align-${col.align}` : '']"
          >
            {{ col.label }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading">
          <td :colspan="columns.length" class="data-table-empty">
            <slot name="loading">Завантаження…</slot>
          </td>
        </tr>
        <tr v-else-if="!rows.length">
          <td :colspan="columns.length" class="data-table-empty">
            <slot name="empty">Немає даних</slot>
          </td>
        </tr>
        <tr
          v-for="(row, rowIdx) in rows"
          v-else
          :key="rowKey ? String((row as Record<string, unknown>)[String(rowKey)]) : rowIdx"
          :class="['data-table-row', rowClass ? rowClass(row) : '']"
          @click="$emit('row-click', row)"
        >
          <td
            v-for="col in columns"
            :key="col.key"
            :class="['data-table-td', col.align ? `align-${col.align}` : '']"
          >
            <slot :name="`cell-${col.key}`" :row="row" :value="row[col.key]">
              {{ row[col.key] ?? '—' }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts" generic="T extends Record<string, unknown>">
/**
 * DataTable.vue — generic scrollable data table primitive.
 *
 * Wraps the existing .table-wrapper CSS class from static/css/common.css.
 * Provides column definition, row click events, and loading/empty states.
 *
 * Intentionally generic: has no knowledge of scheduler, mappings, or stores.
 *
 * Props:
 *   columns  — column definitions (key, label, optional width/align)
 *   rows     — array of row data records
 *   rowKey   — optional key field for stable row identity (uses index fallback)
 *   loading  — show loading state instead of rows
 *   rowClass — optional function(row) → CSS class string for custom row styling
 *
 * Slots (named per column key):
 *   cell-<colKey>  — custom cell renderer, receives { row, value }
 *   loading        — override the loading row text
 *   empty          — override the empty-state row text
 *
 * Usage:
 *   <DataTable
 *     :columns="[{ key: 'name', label: 'Назва' }, { key: 'status', label: 'Статус' }]"
 *     :rows="jobs"
 *     row-key="id"
 *     @row-click="selectJob"
 *   >
 *     <template #cell-status="{ value }">
 *       <StatusPill :kind="resolveKind(value)" :label="resolveLabel(value)" />
 *     </template>
 *   </DataTable>
 */

export interface TableColumn {
  key: string
  label: string
  width?: string
  align?: 'left' | 'center' | 'right'
}

interface Props {
  columns: TableColumn[]
  rows: T[]
  rowKey?: keyof T & string
  loading?: boolean
  rowClass?: (row: T) => string
}

withDefaults(defineProps<Props>(), {
  rowKey: undefined,
  loading: false,
  rowClass: undefined,
})

defineEmits<{
  (e: 'row-click', row: T): void
}>()
</script>

<style scoped>
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.data-table-th {
  text-align: left;
  padding: 8px 10px;
  border-bottom: 2px solid #e5e7eb;
  font-weight: 600;
  color: #374151;
  white-space: nowrap;
}

.data-table-td {
  padding: 8px 10px;
  border-bottom: 1px solid #f3f4f6;
  vertical-align: middle;
}

.data-table-row:hover {
  background: #f9fafb;
  cursor: pointer;
}

.data-table-empty {
  padding: 24px 10px;
  text-align: center;
  color: #9ca3af;
  font-size: 0.9rem;
}

.align-center { text-align: center; }
.align-right  { text-align: right; }
</style>

