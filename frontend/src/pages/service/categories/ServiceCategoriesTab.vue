<template>
  <div class="vue-island">
    <!-- Panel header -->
    <div class="panel-header">
      <h2 class="panel-title">Категорії та скрапінг</h2>

      <!-- Admin-only store sync controls -->
      <div v-if="state.enableAdminSync.value" class="panel-actions">
        <button
          class="btn-ghost"
          type="button"
          :disabled="state.storeSyncLoading.value"
          @click="state.triggerStoreSync"
        >
          {{ state.storeSyncLoading.value ? '⏳ Синхронізація…' : 'Синхронізувати магазини' }}
        </button>
        <span
          v-if="state.storeSyncStatus.value"
          :class="['status-pill', `status-${state.storeSyncStatus.value.kind}`]"
        >
          {{ state.storeSyncStatus.value.text }}
        </span>
      </div>
    </div>

    <!-- Scrape status widget -->
    <ScrapeStatusList :runs="state.scrapeRuns.value" />

    <!-- Two-pane categories layout -->
    <div class="grid-two" style="margin-top:20px;">
      <!-- Reference pane -->
      <CategoriesPane
        kind="reference"
        :stores="state.stores.value"
        :selected-store-id="state.refPane.storeId.value"
        :categories="state.refPane.categories.value"
        :loading="state.refPane.loading.value"
        :status-text="state.refPane.statusText.value"
        :status-kind="state.refPane.statusKind.value"
        :sync-loading="state.refPane.syncLoading.value"
        :sync-products-loading-id="state.refPane.syncProductsLoadingId.value"
        @update:selected-store-id="state.refPane.setStore"
        @sync-categories="state.refPane.triggerSync"
        @sync-products="state.refPane.triggerProductSync"
      />

      <!-- Target pane -->
      <CategoriesPane
        kind="target"
        :stores="state.stores.value"
        :selected-store-id="state.targetPane.storeId.value"
        :categories="state.targetPane.categories.value"
        :loading="state.targetPane.loading.value"
        :status-text="state.targetPane.statusText.value"
        :status-kind="state.targetPane.statusKind.value"
        :sync-loading="state.targetPane.syncLoading.value"
        :sync-products-loading-id="state.targetPane.syncProductsLoadingId.value"
        @update:selected-store-id="state.targetPane.setStore"
        @sync-categories="state.targetPane.triggerSync"
        @sync-products="state.targetPane.triggerProductSync"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * ServiceCategoriesTab.vue — root component for the Categories tab Vue island.
 *
 * Mounted from frontend/src/entries/service.ts on #service-categories-root.
 * Owns all categories tab UI and actions; no legacy JS dependency.
 */
import { useServiceCategories } from './composables/useServiceCategories'
import ScrapeStatusList from './components/ScrapeStatusList.vue'
import CategoriesPane from './components/CategoriesPane.vue'

const state = useServiceCategories()
</script>

