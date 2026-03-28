/**
 * Entry point: /service (Service Console)
 *
 * Mounts a single ServicePage Vue app on #serviceApp.
 * ServicePage.vue owns tab state and renders all four tab islands:
 *   - categories  → ServiceCategoriesTab.vue
 *   - mappings    → MappingsTab.vue
 *   - scheduler   → SchedulerApp.vue
 *   - history     → ServiceHistoryApp.vue
 *
 * Previously this file bootstrapped four separate Vue islands and the legacy
 * static/js/service.js managed tab switching. After Commit 10 all tab
 * orchestration lives in ServicePage.vue / useServiceTabs.ts.
 *
 * Flask still owns the page shell (header, nav, <main>) and SERVICE_CONFIG
 * injection. Vue owns all client-side UI interaction inside <main>.
 *
 * Migration status (all tabs fully Vue-owned):
 *   Categories → ServiceCategoriesTab  (Commit 9)
 *   Scheduler  → SchedulerApp          (Commit 6)
 *   Mappings   → MappingsTab           (Commit 7)
 *   History    → ServiceHistoryApp     (Commit 8)
 *   Tab shell  → ServicePage           (Commit 10)
 */
import { createApp } from 'vue'
import '@/styles/base.css'
import ServicePage from '@/pages/service/ServicePage.vue'

const appEl = document.getElementById('serviceApp')

if (appEl) {
  createApp(ServicePage).mount(appEl)
} else {
  console.error('[pricewatch] #serviceApp mount root not found')
}
