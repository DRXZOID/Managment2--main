import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import RunDetailsDialog from '@/pages/service/history/components/RunDetailsDialog.vue'

// Stub DialogShell so tests don't need Teleport setup
vi.mock('@/components/base/DialogShell.vue', () => ({
  default: {
    name: 'DialogShell',
    template: '<div v-if="open"><slot /><slot name="footer" /></div>',
    props: ['open', 'title'],
    emits: ['close'],
  },
}))

const makeRun = (overrides = {}) => ({
  id: 42,
  store_id: 1,
  store: { id: 1, name: 'prohockey', is_reference: true, base_url: null },
  job_id: null,
  run_type: 'store_category_sync',
  trigger_type: 'manual',
  status: 'success',
  attempt: 1,
  queued_at: '2026-01-01T12:00:00Z',
  started_at: '2026-01-01T12:00:05Z',
  finished_at: '2026-01-01T12:00:30Z',
  worker_id: null,
  categories_processed: 5,
  products_processed: 100,
  products_created: 2,
  products_updated: 8,
  price_changes_detected: 1,
  error_message: null,
  metadata_json: null,
  checkpoint_out_json: null,
  retryable: false,
  retry_of_run_id: null,
  retry_processed: false,
  retry_exhausted: false,
  ...overrides,
})

describe('RunDetailsDialog', () => {
  it('renders nothing when closed', () => {
    const wrapper = mount(RunDetailsDialog, {
      props: { open: false, run: null, loading: false, error: null },
    })
    expect(wrapper.find('.run-details').exists()).toBe(false)
  })

  it('shows loading state when loading=true', () => {
    const wrapper = mount(RunDetailsDialog, {
      props: { open: true, run: null, loading: true, error: null },
    })
    expect(wrapper.text()).toContain('Завантаження')
  })

  it('shows error state when error is set', () => {
    const wrapper = mount(RunDetailsDialog, {
      props: { open: true, run: null, loading: false, error: 'Not found' },
    })
    expect(wrapper.text()).toContain('Not found')
  })

  it('renders run details when open and run is provided', () => {
    const run = makeRun()
    const wrapper = mount(RunDetailsDialog, {
      props: { open: true, run, loading: false, error: null },
    })
    expect(wrapper.find('.run-details').exists()).toBe(true)
    expect(wrapper.text()).toContain('store_category_sync')
    expect(wrapper.text()).toContain('prohockey')
  })

  it('displays attempt badge when attempt > 1', () => {
    const run = makeRun({ attempt: 3 })
    const wrapper = mount(RunDetailsDialog, {
      props: { open: true, run, loading: false, error: null },
    })
    expect(wrapper.text()).toContain('спроба 3')
  })

  it('shows metadata details when metadata_json present', () => {
    const run = makeRun({ metadata_json: { key: 'value' } })
    const wrapper = mount(RunDetailsDialog, {
      props: { open: true, run, loading: false, error: null },
    })
    expect(wrapper.find('details').exists()).toBe(true)
    expect(wrapper.find('.run-details-pre').text()).toContain('"key"')
  })

  it('emits close when close button clicked', async () => {
    const run = makeRun()
    const wrapper = mount(RunDetailsDialog, {
      props: { open: true, run, loading: false, error: null },
    })
    const closeBtn = wrapper.find('button.btn')
    await closeBtn.trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })
})

