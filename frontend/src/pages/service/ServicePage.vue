<template>
  <div class="service-page">
    <!-- ── Tab bar — formerly owned by service.js DOM listeners ── -->
    <div class="tabs">
      <button
        v-for="tab in SERVICE_TABS"
        :key="tab.id"
        type="button"
        :class="['tab-btn', { active: activeTab === tab.id }]"
        @click="switchTab(tab.id)"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- ── Tab panels — v-show keeps all components mounted ── -->
    <!-- All islands mount at page load; data preloads in background.      -->
    <!-- v-show (not v-if) preserves component state across tab switches.  -->

    <section id="tab-categories" class="panel" v-show="activeTab === 'categories'">
      <ServiceCategoriesTab />
    </section>

    <section id="tab-mappings" class="panel" v-show="activeTab === 'mappings'">
      <MappingsTab />
    </section>

    <section id="tab-scheduler" class="panel" v-show="activeTab === 'scheduler'">
      <SchedulerApp />
    </section>

    <section id="tab-history" class="panel" v-show="activeTab === 'history'">
      <ServiceHistoryApp />
    </section>
  </div>
</template>

<script setup lang="ts">
/**
 * ServicePage.vue — root Vue component for the Service Console (/service).
 *
 * Replaces the legacy tab-orchestration responsibility of static/js/service.js.
 * Mounted from frontend/src/entries/service.ts on #serviceApp.
 *
 * Owns:
 *   - active tab state (default: categories)
 *   - tab button rendering with reactive active class
 *   - tab panel visibility via v-show
 *
 * Each tab is a self-contained Vue island component that owns its own data
 * loading. They all mount immediately (v-show, not v-if) so data preloads
 * in the background while the user reads the categories tab.
 *
 * The legacy window.__PW_VUE_SCHEDULER__.activate() bridge is no longer
 * needed: SchedulerApp.vue calls model.activate() in onMounted, which runs
 * once on initial mount regardless of which tab is active.
 *
 * Flask still owns:
 *   - the page shell (header / nav / <main>)
 *   - SERVICE_CONFIG injection
 *   - CSS asset inclusion
 */
import { useServiceTabs, SERVICE_TABS } from './composables/useServiceTabs'
import ServiceCategoriesTab from './categories/ServiceCategoriesTab.vue'
import MappingsTab from './mappings/MappingsTab.vue'
import SchedulerApp from './scheduler/SchedulerApp.vue'
import ServiceHistoryApp from './history/ServiceHistoryApp.vue'

const { activeTab, switchTab } = useServiceTabs()
</script>

