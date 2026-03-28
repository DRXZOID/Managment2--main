/**
 * Entry point: /matches (Product Match Review page)
 *
 * Mounts MatchesPage Vue app on #matches-app.
 * MatchesPage owns all interactive UI: filters, data loading,
 * summary, table, and delete flow.
 *
 * Flask still owns the page shell (header, nav, <title>, CSS).
 */
import { createApp } from 'vue'
import '@/styles/base.css'
import MatchesPage from '@/pages/matches/MatchesPage.vue'

const appEl = document.getElementById('matches-app')

if (appEl) {
  createApp(MatchesPage).mount(appEl)
} else {
  console.error('[pricewatch] #matches-app mount root not found')
}
