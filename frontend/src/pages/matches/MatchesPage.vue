<template>
  <div class="matches-page">

    <!-- ── Filters panel ──────────────────────────────────── -->
    <section class="panel">
      <MatchesFilters
        :reference-stores="state.referenceStores.value"
        :target-stores="state.targetStores.value"
        :reference-categories="state.referenceCategories.value"
        :target-categories="state.targetCategories.value"
        :filters="state.filters"
        :loading="state.isLoadingRows.value"
        @update:reference-store="state.setReferenceStore"
        @update:target-store="state.setTargetStore"
        @update:reference-category-id="id => { state.filters.referenceCategoryId = id }"
        @update:target-category-id="id => { state.filters.targetCategoryId = id }"
        @update:status="s => { state.filters.status = s }"
        @update:search="s => { state.filters.search = s }"
        @load="state.loadMappings"
      />
    </section>

    <!-- ── Summary row (shown after first load) ──────────── -->
    <MatchesSummary v-if="state.hasLoaded.value" :total="state.total.value" />

    <!-- ── Inline status block ───────────────────────────── -->
    <div
      v-if="state.isBootstrapping.value || state.isLoadingRows.value"
      class="status-block info"
      role="status"
      aria-live="polite"
    >
      Завантаження…
    </div>
    <div
      v-else-if="state.errorMessage.value"
      class="status-block error"
      role="alert"
    >
      {{ state.errorMessage.value }}
    </div>
    <div
      v-else-if="state.infoMessage.value"
      class="status-block info"
      role="status"
    >
      {{ state.infoMessage.value }}
    </div>

    <!-- ── Results table ─────────────────────────────────── -->
    <section
      v-if="state.rows.value.length"
      class="panel"
    >
      <MatchesTable
        :rows="state.rows.value"
        :deleting-id="state.isDeletingId.value"
        @delete="state.deleteRow"
      />
    </section>

  </div>
</template>

<script setup lang="ts">
/**
 * MatchesPage.vue — root Vue component for the /matches page.
 *
 * Mounted from frontend/src/entries/matches.ts on #matches-app.
 *
 * Owns:
 *   - all page state via useMatchesPage()
 *   - filter coordination
 *   - category loading on store selection
 *   - mappings load / refresh cycle
 *   - delete action
 *
 * Flask still owns: page shell (header/nav), CSS includes, <title>.
 */
import { useMatchesPage } from './composables/useMatchesPage'
import MatchesFilters from './components/MatchesFilters.vue'
import MatchesSummary from './components/MatchesSummary.vue'
import MatchesTable from './components/MatchesTable.vue'

const state = useMatchesPage()
</script>

