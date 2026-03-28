import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { flushPromises } from '@vue/test-utils'

// ---------------------------------------------------------------------------
// Mock API modules
// ---------------------------------------------------------------------------

vi.mock('@/api/client', () => ({
  fetchStores: vi.fn(),
  fetchCategoriesForStore: vi.fn(),
}))

vi.mock('@/api/matches', () => ({
  listProductMappings: vi.fn(),
  deleteProductMapping: vi.fn(),
}))

import * as clientApi from '@/api/client'
import * as matchesApi from '@/api/matches'

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

const stores = [
  { id: 1, name: 'prohockey', is_reference: true, base_url: null },
  { id: 2, name: 'hockeyworld', is_reference: false, base_url: null },
]

const categories = [
  { id: 10, store_id: 1, name: 'Ковзани', normalized_name: null, url: null, external_id: null, updated_at: null },
]

function makeRow(overrides: Record<string, unknown> = {}) {
  return {
    id: 1,
    reference_product_id: 100,
    target_product_id: 200,
    match_status: 'confirmed',
    confidence: 0.92,
    comment: null,
    created_at: null,
    updated_at: '2026-01-15T12:00:00Z',
    reference_product: { id: 100, store_id: 1, category_id: 10, name: 'Bauer Vapor X5', price: '1500.00', currency: 'UAH', product_url: 'http://a.com/1' },
    target_product: { id: 200, store_id: 2, category_id: 20, name: 'Bauer Vapor X5 Pro', price: '1499.00', currency: 'UAH', product_url: null },
    reference_category: { id: 10, store_id: 1, name: 'Ковзани' },
    target_category: { id: 20, store_id: 2, name: 'Skates' },
    reference_store: { id: 1, name: 'prohockey', is_reference: true },
    target_store: { id: 2, name: 'hockeyworld', is_reference: false },
    ...overrides,
  }
}

beforeEach(() => {
  vi.clearAllMocks()
  vi.mocked(clientApi.fetchStores).mockResolvedValue(stores)
  vi.mocked(clientApi.fetchCategoriesForStore).mockResolvedValue(categories)
  vi.mocked(matchesApi.listProductMappings).mockResolvedValue({ rows: [], total: 0 })
  vi.mocked(matchesApi.deleteProductMapping).mockResolvedValue(undefined)
})

// ---------------------------------------------------------------------------
// useMatchesPage composable tests
// ---------------------------------------------------------------------------

import { useMatchesPage } from '@/pages/matches/composables/useMatchesPage'

describe('useMatchesPage — initial state', () => {
  it('loads stores on init', async () => {
    const state = useMatchesPage()
    await flushPromises()
    expect(state.stores.value).toHaveLength(2)
    expect(clientApi.fetchStores).toHaveBeenCalledTimes(1)
  })

  it('splits stores into reference and target', async () => {
    const state = useMatchesPage()
    await flushPromises()
    expect(state.referenceStores.value).toHaveLength(1)
    expect(state.referenceStores.value[0].name).toBe('prohockey')
    expect(state.targetStores.value).toHaveLength(1)
    expect(state.targetStores.value[0].name).toBe('hockeyworld')
  })

  it('defaults status filter to confirmed', () => {
    const state = useMatchesPage()
    expect(state.filters.status).toBe('confirmed')
  })

  it('hasLoaded is false before first load', async () => {
    const state = useMatchesPage()
    await flushPromises()
    expect(state.hasLoaded.value).toBe(false)
  })
})

describe('useMatchesPage — setReferenceStore', () => {
  it('loads categories when store is selected', async () => {
    const state = useMatchesPage()
    await state.setReferenceStore(1)
    expect(clientApi.fetchCategoriesForStore).toHaveBeenCalledWith(1)
    expect(state.referenceCategories.value).toEqual(categories)
  })

  it('clears categories and resets category filter when null is passed', async () => {
    const state = useMatchesPage()
    await state.setReferenceStore(1)
    await state.setReferenceStore(null)
    expect(state.referenceCategories.value).toHaveLength(0)
    expect(state.filters.referenceCategoryId).toBeNull()
  })
})

describe('useMatchesPage — loadMappings', () => {
  it('sets hasLoaded after successful fetch', async () => {
    vi.mocked(matchesApi.listProductMappings).mockResolvedValue({ rows: [makeRow()], total: 1 })
    const state = useMatchesPage()
    await state.loadMappings()
    expect(state.hasLoaded.value).toBe(true)
    expect(state.rows.value).toHaveLength(1)
    expect(state.total.value).toBe(1)
  })

  it('sets infoMessage when rows are empty', async () => {
    const state = useMatchesPage()
    await state.loadMappings()
    expect(state.infoMessage.value).toContain('не знайдено')
  })

  it('sets errorMessage on API failure', async () => {
    vi.mocked(matchesApi.listProductMappings).mockRejectedValue(new Error('Network error'))
    const state = useMatchesPage()
    await state.loadMappings()
    expect(state.errorMessage.value).toContain('Network error')
    expect(state.hasLoaded.value).toBe(false)
  })
})

describe('useMatchesPage — deleteRow', () => {
  it('calls deleteProductMapping and reloads on confirm=true', async () => {
    vi.stubGlobal('confirm', vi.fn().mockReturnValue(true))
    vi.mocked(matchesApi.listProductMappings).mockResolvedValue({ rows: [makeRow()], total: 1 })
    const state = useMatchesPage()
    await state.deleteRow(1)
    expect(matchesApi.deleteProductMapping).toHaveBeenCalledWith(1)
    expect(matchesApi.listProductMappings).toHaveBeenCalled()
    vi.unstubAllGlobals()
  })

  it('does NOT call deleteProductMapping when confirm=false', async () => {
    vi.stubGlobal('confirm', vi.fn().mockReturnValue(false))
    const state = useMatchesPage()
    await state.deleteRow(1)
    expect(matchesApi.deleteProductMapping).not.toHaveBeenCalled()
    vi.unstubAllGlobals()
  })

  it('sets errorMessage on delete failure', async () => {
    vi.stubGlobal('confirm', vi.fn().mockReturnValue(true))
    vi.mocked(matchesApi.deleteProductMapping).mockRejectedValue(new Error('Delete failed'))
    const state = useMatchesPage()
    await state.deleteRow(1)
    expect(state.errorMessage.value).toContain('Delete failed')
    vi.unstubAllGlobals()
  })
})

// ---------------------------------------------------------------------------
// MatchesTableRow component tests
// ---------------------------------------------------------------------------

import MatchesTableRow from '@/pages/matches/components/MatchesTableRow.vue'

describe('MatchesTableRow — rendering', () => {
  it('renders confirmed status badge', () => {
    const w = mount(MatchesTableRow, {
      props: { row: makeRow({ match_status: 'confirmed' }), isDeletingId: null },
    })
    expect(w.text()).toContain('підтверджено')
    expect(w.find('.status-badge').classes()).toContain('confirmed')
  })

  it('renders rejected status badge', () => {
    const w = mount(MatchesTableRow, {
      props: { row: makeRow({ match_status: 'rejected' }), isDeletingId: null },
    })
    expect(w.text()).toContain('відхилено')
    expect(w.find('.status-badge').classes()).toContain('rejected')
  })

  it('renders score pill with correct percentage', () => {
    const w = mount(MatchesTableRow, {
      props: { row: makeRow({ confidence: 0.92 }), isDeletingId: null },
    })
    expect(w.text()).toContain('92%')
  })

  it('formats price with currency', () => {
    const w = mount(MatchesTableRow, {
      props: { row: makeRow(), isDeletingId: null },
    })
    expect(w.text()).toContain('1500.00 UAH')
  })

  it('emits delete event when delete button clicked', async () => {
    const w = mount(MatchesTableRow, {
      props: { row: makeRow(), isDeletingId: null },
    })
    await w.find('button').trigger('click')
    expect(w.emitted('delete')).toBeTruthy()
    expect(w.emitted('delete')![0]).toEqual([1])
  })

  it('disables delete button when isDeletingId matches row id', () => {
    const w = mount(MatchesTableRow, {
      props: { row: makeRow(), isDeletingId: 1 },
    })
    expect((w.find('button').element as HTMLButtonElement).disabled).toBe(true)
    expect(w.find('button').text()).toBe('…')
  })
})

// ---------------------------------------------------------------------------
// MatchesFilters component tests
// ---------------------------------------------------------------------------

import MatchesFilters from '@/pages/matches/components/MatchesFilters.vue'

const defaultFilterProps = {
  referenceStores: [{ id: 1, name: 'prohockey', is_reference: true, base_url: null }],
  targetStores: [{ id: 2, name: 'hockeyworld', is_reference: false, base_url: null }],
  referenceCategories: [],
  targetCategories: [],
  filters: {
    referenceStoreId: null,
    targetStoreId: null,
    referenceCategoryId: null,
    targetCategoryId: null,
    status: 'confirmed',
    search: '',
  },
}

describe('MatchesFilters — rendering', () => {
  it('renders Показати button', () => {
    const w = mount(MatchesFilters, { props: defaultFilterProps })
    expect(w.text()).toContain('Показати')
  })

  it('emits load on button click', async () => {
    const w = mount(MatchesFilters, { props: defaultFilterProps })
    await w.find('button.btn').trigger('click')
    expect(w.emitted('load')).toBeTruthy()
  })

  it('emits load on Enter in search field', async () => {
    const w = mount(MatchesFilters, { props: defaultFilterProps })
    await w.find('#searchFilter').trigger('keydown', { key: 'Enter' })
    expect(w.emitted('load')).toBeTruthy()
  })

  it('emits update:reference-store when store select changes', async () => {
    const w = mount(MatchesFilters, { props: defaultFilterProps })
    await w.find('#refStoreFilter').setValue('1')
    expect(w.emitted('update:reference-store')).toBeTruthy()
    expect(w.emitted('update:reference-store')![0]).toEqual([1])
  })
})

// ---------------------------------------------------------------------------
// MatchesSummary component tests
// ---------------------------------------------------------------------------

import MatchesSummary from '@/pages/matches/components/MatchesSummary.vue'

describe('MatchesSummary', () => {
  it('renders the total count', () => {
    const w = mount(MatchesSummary, { props: { total: 42 } })
    expect(w.text()).toContain('42')
    expect(w.text()).toContain('Показано')
  })
})

