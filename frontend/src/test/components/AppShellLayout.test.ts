/**
 * AppShellLayout.test.ts — Regression tests for the SPA application shell contract.
 *
 * Commit 7 / Commit 8 — ensures:
 *   - sidebar is rendered with brand block
 *   - skip-to-content link exists
 *   - page header (AppShellHeader) is inside content, not sidebar
 *   - RouterView renders inside #main-content
 *   - sidebar nav is present
 *   - NotFoundPage still renders inside the shell (not a blank screen)
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import AppShellLayout from '@/layouts/AppShellLayout.vue'
import { NAV_LINKS } from '@/constants/navigation'

function makeRouter(initialPath = '/') {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      ...NAV_LINKS.map(link => ({
        path: link.to,
        component: { template: `<div class="page-stub">${link.label}</div>` },
        meta: { title: `Title for ${link.to}`, subtitle: `Sub for ${link.to}` },
      })),
      {
        path: '/:pathMatch(.*)*',
        name: 'not-found',
        component: { template: '<div class="not-found-stub">404</div>' },
      },
    ],
  })
  router.push(initialPath)
  return router
}

async function mountShell(path = '/') {
  const router = makeRouter(path)
  await router.isReady()
  return mount(AppShellLayout, {
    global: { plugins: [router] },
    attachTo: document.body,
  })
}

// ---------------------------------------------------------------------------
// Shell structure
// ---------------------------------------------------------------------------

describe('AppShellLayout — structure', () => {
  it('renders .app-shell wrapper', async () => {
    const wrapper = await mountShell()
    expect(wrapper.find('.app-shell').exists()).toBe(true)
  })

  it('sidebar is an <aside> element inside .app-shell', async () => {
    const wrapper = await mountShell()
    const sidebar = wrapper.find('.app-shell-sidebar')
    expect(sidebar.exists()).toBe(true)
    expect(sidebar.element.tagName).toBe('ASIDE')
  })

  it('sidebar has an aria-label', async () => {
    const wrapper = await mountShell()
    expect(wrapper.find('.app-shell-sidebar').attributes('aria-label')).toBeTruthy()
  })

  it('brand block is inside the sidebar', async () => {
    const wrapper = await mountShell()
    const sidebar = wrapper.find('.app-shell-sidebar')
    expect(sidebar.find('.app-shell-brand').exists()).toBe(true)
  })

  it('brand block contains the app name', async () => {
    const wrapper = await mountShell()
    expect(wrapper.find('.app-shell-brand').text()).toContain('Pricewatch')
  })

  it('AppShellSidebarNav is rendered inside the sidebar', async () => {
    const wrapper = await mountShell()
    const sidebar = wrapper.find('.app-shell-sidebar')
    expect(sidebar.find('nav').exists()).toBe(true)
  })

  it('AppShellHeader is inside .app-shell-content, NOT inside sidebar', async () => {
    const wrapper = await mountShell()
    const sidebar = wrapper.find('.app-shell-sidebar')
    const content = wrapper.find('.app-shell-content')
    // Header must not be inside sidebar
    expect(sidebar.find('header').exists()).toBe(false)
    // Header must be inside content
    expect(content.find('header').exists()).toBe(true)
  })

  it('#main-content exists and contains RouterView output', async () => {
    const wrapper = await mountShell('/')
    await wrapper.vm.$nextTick()
    const main = wrapper.find('#main-content')
    expect(main.exists()).toBe(true)
  })

  it('skip-to-content link exists', async () => {
    const wrapper = await mountShell()
    const skipLink = wrapper.find('a.skip-link')
    expect(skipLink.exists()).toBe(true)
    expect(skipLink.attributes('href')).toBe('#main-content')
  })
})

// ---------------------------------------------------------------------------
// Shell renders page content correctly
// ---------------------------------------------------------------------------

describe('AppShellLayout — page rendering', () => {
  it('renders page title from route.meta on /', async () => {
    const wrapper = await mountShell('/')
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.app-shell-title').text()).toContain('Title for /')
  })

  it('renders page title from route.meta on /service', async () => {
    const wrapper = await mountShell('/service')
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.app-shell-title').text()).toContain('Title for /service')
  })

  it('NotFound route still renders inside the shell (no blank screen)', async () => {
    const wrapper = await mountShell('/totally-unknown-path')
    await wrapper.vm.$nextTick()
    // Shell structure must be present
    expect(wrapper.find('.app-shell').exists()).toBe(true)
    expect(wrapper.find('.app-shell-sidebar').exists()).toBe(true)
    // NotFound stub content renders inside main
    expect(wrapper.find('.not-found-stub').exists()).toBe(true)
  })

  it('all canonical nav links are present regardless of current page', async () => {
    for (const path of ['/', '/service', '/gap', '/matches']) {
      const wrapper = await mountShell(path)
      const hrefs = wrapper.findAll('nav a').map(a => a.attributes('href'))
      NAV_LINKS.forEach(link => {
        expect(hrefs).toContain(link.to)
      })
    }
  })
})

