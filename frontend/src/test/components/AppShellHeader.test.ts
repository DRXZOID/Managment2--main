import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import AppShellHeader from '@/components/AppShellHeader.vue'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Build a minimal router that covers the four SPA routes. */
function makeRouter(initialPath = '/') {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/',        component: {}, meta: { title: 'Pricewatch',            subtitle: 'Subtitle A' } },
      { path: '/service', component: {}, meta: { title: 'Service Console',       subtitle: 'Subtitle B' } },
      { path: '/gap',     component: {}, meta: { title: '📋 Розрив асортименту', subtitle: 'Subtitle C' } },
      { path: '/matches', component: {}, meta: { title: '✅ Підтверджені збіги', subtitle: 'Subtitle D' } },
    ],
  })
  router.push(initialPath)
  return router
}

/** Mount AppShellHeader after the router has resolved the initial navigation. */
async function mountHeader(path = '/') {
  const router = makeRouter(path)
  await router.isReady()
  return mount(AppShellHeader, {
    global: { plugins: [router] },
  })
}

// ---------------------------------------------------------------------------
// Structure
// ---------------------------------------------------------------------------

describe('AppShellHeader — structure', () => {
  it('renders an <header> element with app-shell-header class', async () => {
    const wrapper = await mountHeader()
    expect(wrapper.find('header.app-shell-header').exists()).toBe(true)
  })

  it('renders a nav element', async () => {
    const wrapper = await mountHeader()
    expect(wrapper.find('nav').exists()).toBe(true)
  })

  it('renders four navigation links', async () => {
    const wrapper = await mountHeader()
    const links = wrapper.findAllComponents({ name: 'RouterLink' })
    expect(links).toHaveLength(4)
  })

  it('every nav link has app-shell-nav-link class', async () => {
    const wrapper = await mountHeader()
    wrapper.findAll('a').forEach(link => {
      expect(link.classes()).toContain('app-shell-nav-link')
    })
  })
})

// ---------------------------------------------------------------------------
// Title and subtitle from route meta
// ---------------------------------------------------------------------------

describe('AppShellHeader — route meta', () => {
  it('shows the title from route meta on /', async () => {
    const wrapper = await mountHeader('/')
    expect(wrapper.find('.app-shell-title').text()).toBe('Pricewatch')
  })

  it('shows the title from route meta on /service', async () => {
    const wrapper = await mountHeader('/service')
    expect(wrapper.find('.app-shell-title').text()).toBe('Service Console')
  })

  it('shows the subtitle from route meta', async () => {
    const wrapper = await mountHeader('/')
    expect(wrapper.find('.app-shell-subtitle').text()).toBe('Subtitle A')
  })

  it('falls back to "Pricewatch" when meta.title is absent', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/', component: {} }],
    })
    await router.push('/')
    await router.isReady()
    const wrapper = mount(AppShellHeader, { global: { plugins: [router] } })
    expect(wrapper.find('.app-shell-title').text()).toBe('Pricewatch')
  })

  it('omits subtitle element when meta.subtitle is absent', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/', component: {}, meta: { title: 'No Subtitle' } }],
    })
    await router.push('/')
    await router.isReady()
    const wrapper = mount(AppShellHeader, { global: { plugins: [router] } })
    expect(wrapper.find('.app-shell-subtitle').exists()).toBe(false)
  })
})

// ---------------------------------------------------------------------------
// Navigation link destinations
// ---------------------------------------------------------------------------

describe('AppShellHeader — navigation links', () => {
  it('contains a link to /', async () => {
    const wrapper = await mountHeader()
    const hrefs = wrapper.findAll('a').map(a => a.attributes('href'))
    expect(hrefs).toContain('/')
  })

  it('contains a link to /service', async () => {
    const wrapper = await mountHeader()
    const hrefs = wrapper.findAll('a').map(a => a.attributes('href'))
    expect(hrefs).toContain('/service')
  })

  it('contains a link to /gap', async () => {
    const wrapper = await mountHeader()
    const hrefs = wrapper.findAll('a').map(a => a.attributes('href'))
    expect(hrefs).toContain('/gap')
  })

  it('contains a link to /matches', async () => {
    const wrapper = await mountHeader()
    const hrefs = wrapper.findAll('a').map(a => a.attributes('href'))
    expect(hrefs).toContain('/matches')
  })
})

// ---------------------------------------------------------------------------
// aria-current accessibility
// ---------------------------------------------------------------------------

describe('AppShellHeader — aria-current', () => {
  it('sets aria-current="page" on the active link', async () => {
    const wrapper = await mountHeader('/service')
    const serviceLink = wrapper.findAll('a').find(a => a.attributes('href') === '/service')
    expect(serviceLink?.attributes('aria-current')).toBe('page')
  })

  it('does not set aria-current on inactive links', async () => {
    const wrapper = await mountHeader('/service')
    const otherLinks = wrapper.findAll('a').filter(a => a.attributes('href') !== '/service')
    otherLinks.forEach(link => {
      expect(link.attributes('aria-current')).toBeUndefined()
    })
  })
})
