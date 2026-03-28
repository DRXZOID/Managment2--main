<template>
  <div class="vue-island history-island">
    <!-- Header -->
    <div class="panel-header">
      <h2 class="panel-title">Історія скрапінгу</h2>
      <div class="panel-actions">
        <button
          class="btn-ghost btn-sm"
          type="button"
          :disabled="state.loading.value"
          title="Оновити"
          @click="state.reload"
        >↺ Оновити</button>
      </div>
    </div>

    <!-- Filters -->
    <HistoryFilters
      :stores="state.stores.value"
      :store-id="state.filters.storeId"
      :run-type="state.filters.runType"
      :status="state.filters.status"
      :trigger-type="state.filters.triggerType"
      @update:store-id="v => state.setFilter('storeId', v)"
      @update:run-type="v => state.setFilter('runType', v)"
      @update:status="v => state.setFilter('status', v)"
      @update:trigger-type="v => state.setFilter('triggerType', v)"
    />

    <!-- Status banner -->
    <div
      v-if="state.loading.value"
      class="status-block info"
      style="margin-top: 16px;"
      role="status"
      aria-live="polite"
    >
      ⏳ Завантаження…
    </div>
    <div
      v-else-if="state.error.value"
      class="status-block error"
      style="margin-top: 16px;"
      role="alert"
    >
      ⚠ {{ state.error.value }}
    </div>
    <div
      v-else
      class="status-block info"
      style="margin-top: 16px;"
      role="status"
    >
      Записів на сторінці: {{ state.runs.value.length }}
    </div>

    <!-- Runs table -->
    <HistoryTable
      :runs="state.runs.value"
      @details="state.openDetails"
    />

    <!-- Pagination -->
    <HistoryPagination
      :page="state.page.value"
      :page-size="state.pageSize.value"
      :item-count="state.runs.value.length"
      :disabled="state.loading.value"
      @prev="state.prevPage"
      @next="state.nextPage"
    />

    <!-- Run details dialog — Vue owned, renders via Teleport -->
    <RunDetailsDialog
      :open="state.detailRunId.value !== null"
      :run="state.detailRun.value"
      :loading="state.detailLoading.value"
      :error="state.detailError.value"
      @close="state.closeDetails"
    />
  </div>
</template>

<script setup lang="ts">
/**
 * ServiceHistoryApp.vue — root component for the History tab Vue island.
 *
 * Owns:
 *   - layout for the history tab
 *   - filter coordination via useServiceHistory
 *   - details dialog lifecycle
 *
 * Mounted from frontend/src/entries/service.ts on #service-history-root.
 */
import { useServiceHistory } from './composables/useServiceHistory'
import HistoryFilters from './components/HistoryFilters.vue'
import HistoryTable from './components/HistoryTable.vue'
import HistoryPagination from './components/HistoryPagination.vue'
import RunDetailsDialog from './components/RunDetailsDialog.vue'

const state = useServiceHistory()
</script>

<style scoped>
.history-island {
  padding: 0;
}
</style>

