/**
 * Entry point: /gap (Gap Analysis page)
 *
 * Mounts GapPage Vue app on #gap-app.
 * GapPage owns all interactive UI: filters, dependent cascade loading,
 * summary, grouped results, and item status actions.
 *
 * Flask still owns: page shell (header/nav), CSS includes, <title>.
 */
import { createApp } from 'vue'
import '@/styles/base.css'
import GapPage from '@/pages/gap/GapPage.vue'

const appEl = document.getElementById('gap-app')

if (appEl) {
  createApp(GapPage).mount(appEl)
} else {
  console.error('[pricewatch] #gap-app mount root not found')
}
