/**
 * Entry point: / (Main comparison page)
 *
 * Mounts ComparisonPage Vue app on #comparison-app.
 * ComparisonPage owns all interactive UI: store/category cascade,
 * comparison execution, confirm/reject decisions, manual picker.
 *
 * Flask still owns: page shell (header/nav), CSS includes, <title>.
 */
import { createApp } from 'vue'
import '@/styles/base.css'
import ComparisonPage from '@/pages/comparison/ComparisonPage.vue'

const appEl = document.getElementById('comparison-app')

if (appEl) {
  createApp(ComparisonPage).mount(appEl)
} else {
  console.error('[pricewatch] #comparison-app mount root not found')
}
