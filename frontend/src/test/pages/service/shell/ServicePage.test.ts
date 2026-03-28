import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { useServiceTabs, SERVICE_TABS } from '@/pages/service/composables/useServiceTabs'

// ---------------------------------------------------------------------------
// useServiceTabs unit tests
// ---------------------------------------------------------------------------

describe('useServiceTabs', () => {
  it('defaults to categories tab', () => {
    const { activeTab } = useServiceTabs()
    expect(activeTab.value).toBe('categories')
  })

  it('accepts a custom initial tab', () => {
    const { activeTab } = useServiceTabs('history')
    expect(activeTab.value).toBe('history')
  })

  it('switchTab updates activeTab', () => {
    const { activeTab, switchTab } = useServiceTabs()
    switchTab('mappings')
    expect(activeTab.value).toBe('mappings')
  })

  it('switchTab cycles through all tabs', () => {
    const { activeTab, switchTab } = useServiceTabs()
    for (const tab of SERVICE_TABS) {
      switchTab(tab.id)
      expect(activeTab.value).toBe(tab.id)
    }
  })

  it('SERVICE_TABS contains all four tabs', () => {
    const ids = SERVICE_TABS.map((t) => t.id)
    expect(ids).toContain('categories')
    expect(ids).toContain('mappings')
    expect(ids).toContain('scheduler')
    expect(ids).toContain('history')
    expect(SERVICE_TABS).toHaveLength(4)
  })
})

// ---------------------------------------------------------------------------
// ServicePage component tests (tab shell only, islands are stubbed)
// ---------------------------------------------------------------------------

// Stub all four tab island components so we can test the shell independently.
vi.mock('@/pages/service/categories/ServiceCategoriesTab.vue', () => ({
  default: { template: '<div data-testid="categories-island">categories</div>' },
}))
vi.mock('@/pages/service/mappings/MappingsTab.vue', () => ({
  default: { template: '<div data-testid="mappings-island">mappings</div>' },
}))
vi.mock('@/pages/service/scheduler/SchedulerApp.vue', () => ({
  default: { template: '<div data-testid="scheduler-island">scheduler</div>' },
}))
vi.mock('@/pages/service/history/ServiceHistoryApp.vue', () => ({
  default: { template: '<div data-testid="history-island">history</div>' },
}))

import ServicePage from '@/pages/service/ServicePage.vue'

beforeEach(() => {
  vi.clearAllMocks()
})

describe('ServicePage — tab bar rendering', () => {
  it('renders four tab buttons', () => {
    const w = mount(ServicePage)
    const btns = w.findAll('.tab-btn')
    expect(btns).toHaveLength(4)
  })

  it('first tab button is active by default', () => {
    const w = mount(ServicePage)
    const btns = w.findAll('.tab-btn')
    expect(btns[0].classes()).toContain('active')
    expect(btns[1].classes()).not.toContain('active')
  })

  it('tab button labels match SERVICE_TABS', () => {
    const w = mount(ServicePage)
    const btns = w.findAll('.tab-btn')
    SERVICE_TABS.forEach((tab, i) => {
      expect(btns[i].text()).toContain(tab.label.replace(/^⏱\s*/, ''))
    })
  })
})

describe('ServicePage — tab switching', () => {
  it('clicking mappings tab sets it active', async () => {
    const w = mount(ServicePage)
    const btns = w.findAll('.tab-btn')
    await btns[1].trigger('click')
    expect(btns[1].classes()).toContain('active')
    expect(btns[0].classes()).not.toContain('active')
  })

  it('clicking scheduler tab sets it active', async () => {
    const w = mount(ServicePage)
    const btns = w.findAll('.tab-btn')
    await btns[2].trigger('click')
    expect(btns[2].classes()).toContain('active')
  })

  it('clicking history tab then back to categories works', async () => {
    const w = mount(ServicePage)
    const btns = w.findAll('.tab-btn')
    await btns[3].trigger('click')
    expect(btns[3].classes()).toContain('active')
    await btns[0].trigger('click')
    expect(btns[0].classes()).toContain('active')
    expect(btns[3].classes()).not.toContain('active')
  })
})

describe('ServicePage — tab panels visibility', () => {
  it('categories panel is visible by default', () => {
    const w = mount(ServicePage)
    const panel = w.find('#tab-categories')
    expect(panel.isVisible()).toBe(true)
  })

  it('other panels are hidden by default', () => {
    const w = mount(ServicePage)
    expect(w.find('#tab-mappings').isVisible()).toBe(false)
    expect(w.find('#tab-scheduler').isVisible()).toBe(false)
    expect(w.find('#tab-history').isVisible()).toBe(false)
  })

  it('mappings panel becomes visible after tab click', async () => {
    const w = mount(ServicePage)
    await w.findAll('.tab-btn')[1].trigger('click')
    expect(w.find('#tab-mappings').isVisible()).toBe(true)
    expect(w.find('#tab-categories').isVisible()).toBe(false)
  })

  it('scheduler panel becomes visible after tab click', async () => {
    const w = mount(ServicePage)
    await w.findAll('.tab-btn')[2].trigger('click')
    expect(w.find('#tab-scheduler').isVisible()).toBe(true)
  })

  it('all four panels are present in the DOM (v-show, not v-if)', () => {
    const w = mount(ServicePage)
    expect(w.find('#tab-categories').exists()).toBe(true)
    expect(w.find('#tab-mappings').exists()).toBe(true)
    expect(w.find('#tab-scheduler').exists()).toBe(true)
    expect(w.find('#tab-history').exists()).toBe(true)
  })
})

