/**
 * useServiceTabs.ts — reactive tab-switching state for the Service Console page.
 *
 * Previously tab switching was handled by static/js/service.js via DOM listeners.
 * After Commit 10 this composable is the single source of truth for the active tab.
 *
 * Tab IDs intentionally mirror the former HTML section ids (tab-<id>) so that
 * bookmarks / devtools inspection remain consistent.
 */
import { ref } from 'vue'

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

export type ServiceTabId = 'categories' | 'mappings' | 'scheduler' | 'history'

export interface ServiceTabDef {
  id: ServiceTabId
  label: string
}

// ---------------------------------------------------------------------------
// Static tab definitions
// ---------------------------------------------------------------------------

export const SERVICE_TABS: ServiceTabDef[] = [
  { id: 'categories', label: 'Категорії' },
  { id: 'mappings', label: 'Мапінги' },
  { id: 'scheduler', label: '⏱ Scheduler' },
  { id: 'history', label: 'Історія' },
]

// ---------------------------------------------------------------------------
// Composable
// ---------------------------------------------------------------------------

export function useServiceTabs(initial: ServiceTabId = 'categories') {
  const activeTab = ref<ServiceTabId>(initial)

  function switchTab(tab: ServiceTabId): void {
    activeTab.value = tab
  }

  return { activeTab, switchTab }
}

