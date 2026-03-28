<template>
  <div class="gap-page">

    <!-- ── Filter panel ──────────────────────────────── -->
    <section class="panel">
      <GapFilters
        :target-stores="filters.targetStores.value"
        :reference-categories="filters.referenceCategories.value"
        :mapped-target-cats="filters.mappedTargetCats.value"
        :selected-target-store-id="filters.selectedTargetStoreId.value"
        :selected-ref-category-id="filters.selectedRefCategoryId.value"
        :selected-target-cat-ids="filters.selectedTargetCatIds.value"
        :search="filters.search.value"
        :only-available="filters.onlyAvailable.value"
        :statuses="filters.statuses"
        :ref-categories-loading="filters.refCategoriesLoading.value"
        :mapped-cats-loading="filters.mappedCatsLoading.value"
        :no-mappings-warning="filters.noMappingsWarning.value"
        :can-load="filters.canLoad.value"
        :loading="data.loading.value"
        @update:target-store="filters.setTargetStore"
        @update:ref-category="filters.setRefCategory"
        @toggle-target-cat="filters.toggleTargetCat"
        @update:search="v => { filters.search.value = v }"
        @update:only-available="v => { filters.onlyAvailable.value = v }"
        @update:status-new="v => { filters.statuses.new = v }"
        @update:status-in-progress="v => { filters.statuses.in_progress = v }"
        @update:status-done="v => { filters.statuses.done = v }"
        @load="handleLoad"
      />
    </section>

    <!-- ── Summary row ───────────────────────────────── -->
    <GapSummary v-if="data.result.value" :summary="data.result.value.summary" />

    <!-- ── Status / error / empty banner ─────────────── -->
    <GapStatusBanner
      :loading="data.loading.value || filters.storesLoading.value"
      :error="data.error.value ?? actions.actionError.value"
      :stores-error="filters.storesError.value"
      :is-empty="data.hasLoaded.value && !data.result.value?.groups?.length"
      :has-loaded="data.hasLoaded.value"
    />

    <!-- ── Grouped results ───────────────────────────── -->
    <template v-if="data.result.value?.groups?.length">
      <GapGroupTable
        v-for="group in data.result.value.groups"
        :key="group.target_category?.id ?? String(Math.random())"
        :group="group"
        :ref-category-id="filters.selectedRefCategoryId.value ?? 0"
        :action-in-progress-id="actions.actionInProgressId.value"
        @action="handleAction"
      />
    </template>

  </div>
</template>

<script setup lang="ts">
/**
 * GapPage.vue — root Vue component for the /gap page.
 *
 * Mounted from frontend/src/entries/gap.ts on #gap-app.
 *
 * Owns:
 *   - store/category cascade loading via useGapFilters
 *   - gap query and result state via useGapData
 *   - item status actions via useGapActions
 *
 * Flask still owns: page shell (header/nav), CSS, <title>.
 */
import { onMounted } from 'vue'
import { useGapFilters } from './composables/useGapFilters'
import { useGapData } from './composables/useGapData'
import { useGapActions } from './composables/useGapActions'
import GapFilters from './components/GapFilters.vue'
import GapSummary from './components/GapSummary.vue'
import GapStatusBanner from './components/GapStatusBanner.vue'
import GapGroupTable from './components/GapGroupTable.vue'
import type { GapItemStatus } from '@/types/gap'

const filters = useGapFilters()
const data = useGapData()
const actions = useGapActions()

onMounted(() => {
  void filters.loadStores()
})

function buildBody() {
  const checkedStatuses: GapItemStatus[] = []
  if (filters.statuses.new) checkedStatuses.push('new')
  if (filters.statuses.in_progress) checkedStatuses.push('in_progress')
  if (filters.statuses.done) checkedStatuses.push('done')

  return {
    target_store_id: filters.selectedTargetStoreId.value!,
    reference_category_id: filters.selectedRefCategoryId.value!,
    target_category_ids: Array.from(filters.selectedTargetCatIds.value),
    search: filters.search.value.trim() || null,
    only_available: filters.onlyAvailable.value || null,
    statuses: checkedStatuses.length ? checkedStatuses : ['new' as GapItemStatus, 'in_progress' as GapItemStatus],
  }
}

async function handleLoad() {
  if (!filters.canLoad.value) return
  await data.loadGap(buildBody())
}

async function handleAction(refCatId: number, targetProductId: number, status: GapItemStatus) {
  const ok = await actions.setStatus(refCatId, targetProductId, status)
  if (ok && data.lastBody.value) {
    await data.loadGap(data.lastBody.value)
  }
}
</script>

