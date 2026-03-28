import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'

// ---------------------------------------------------------------------------
// Mock API modules
// ---------------------------------------------------------------------------

vi.mock('@/api/client', () => ({
  fetchStores: vi.fn(),
  fetchCategoriesForStore: vi.fn(),
}))

vi.mock('@/pages/comparison/api', () => ({
  fetchStores: vi.fn(),
  fetchCategoriesForStore: vi.fn(),
  fetchMappedTargets: vi.fn(),
  runComparison: vi.fn(),
  saveMatchDecision: vi.fn(),
  searchEligibleTargetProducts: vi.fn(),
}))

import * as compApi from '@/pages/comparison/api'

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

const refStore  = { id: 1, name: 'prohockey', is_reference: true,  base_url: null }
const tgtStore  = { id: 2, name: 'hockeyworld', is_reference: false, base_url: null }
const stores    = [refStore, tgtStore]

const refCats = [
  { id: 10, store_id: 1, name: 'Ковзани', normalized_name: null, url: 'https://a.com', external_id: null, updated_at: null },
  { id: 11, store_id: 1, name: 'Шлеми',  normalized_name: null, url: null,            external_id: null, updated_at: null },
]

const mappedTargets = [
  { target_category_id: 20, target_category_name: 'Skates', target_store_id: 2, target_store_name: 'hockeyworld', match_type: 'exact' },
  { target_category_id: 21, target_category_name: 'Skates Pro', target_store_id: 2, target_store_name: 'hockeyworld', match_type: null },
]

const comparisonResult = {
  confirmed_matches: [
    {
      is_confirmed: false,
      reference_product: { id: 100, name: 'Bauer X', price: '1500.00', currency: 'UAH', product_url: 'http://a.com/1' },
      target_product:    { id: 200, name: 'Bauer X copy', price: '1480.00', currency: 'UAH', product_url: null },
      target_category:   { name: 'Skates', store_name: 'hockeyworld' },
      score_percent:     90,
      score_details:     null,
    },
  ],
  candidate_groups: [
    {
      reference_product: { id: 101, name: 'CCM Ref', price: '2000.00', currency: 'UAH', product_url: null },
      candidates: [
        {
          target_product: { id: 201, name: 'CCM Copy', price: '1900.00', currency: 'UAH', product_url: null },
          target_category: { name: 'Skates', store_name: 'hockeyworld' },
          score_percent: 70, score_details: null, can_accept: true, disabled_reason: null,
        },
      ],
    },
  ],
  reference_only: [
    { reference_product: { id: 102, name: 'Ref Only Item', price: '500.00', currency: 'UAH', product_url: null } },
  ],
  target_only: [
    {
      target_product:  { id: 202, name: 'Tgt Only Item', price: '400.00', currency: 'UAH', product_url: null },
      target_category: { name: 'Skates Pro', store_name: 'hockeyworld' },
    },
  ],
  summary: { candidate_groups: 1, reference_only: 1, target_only: 1 },
}

beforeEach(() => {
  vi.clearAllMocks()
  vi.mocked(compApi.fetchStores).mockResolvedValue(stores)
  vi.mocked(compApi.fetchCategoriesForStore).mockResolvedValue(refCats)
  vi.mocked(compApi.fetchMappedTargets).mockResolvedValue(mappedTargets)
  vi.mocked(compApi.runComparison).mockResolvedValue(comparisonResult)
  vi.mocked(compApi.saveMatchDecision).mockResolvedValue(undefined)
  vi.mocked(compApi.searchEligibleTargetProducts).mockResolvedValue([])
})

// ---------------------------------------------------------------------------
// useComparisonPage unit tests
// ---------------------------------------------------------------------------

import { useComparisonPage } from '@/pages/comparison/composables/useComparisonPage'

describe('useComparisonPage — initial state', () => {
  it('starts with empty stores and no selections', () => {
    const p = useComparisonPage()
    expect(p.referenceStores.value).toHaveLength(0)
    expect(p.targetStores.value).toHaveLength(0)
    expect(p.referenceCategoryId.value).toBeNull()
    expect(p.canCompare.value).toBe(false)
  })

  it('canCompare is false before any selection', () => {
    const p = useComparisonPage()
    expect(p.canCompare.value).toBe(false)
  })
})

describe('useComparisonPage — auto-select single reference store', () => {
  it('auto-selects a single reference store and loads its categories', async () => {
    const p = useComparisonPage()
    await p.loadStores()
    await flushPromises()

    expect(p.referenceStoreId.value).toBe(1)
    expect(compApi.fetchCategoriesForStore).toHaveBeenCalledWith(1)
    expect(p.referenceCategories.value).toHaveLength(2)
  })

  it('does NOT auto-select when there are multiple reference stores', async () => {
    vi.mocked(compApi.fetchStores).mockResolvedValue([
      { id: 1, name: 'ref1', is_reference: true, base_url: null },
      { id: 3, name: 'ref2', is_reference: true, base_url: null },
      tgtStore,
    ])
    const p = useComparisonPage()
    await p.loadStores()
    await flushPromises()

    expect(p.referenceStoreId.value).toBeNull()
    expect(compApi.fetchCategoriesForStore).not.toHaveBeenCalled()
  })
})

describe('useComparisonPage — cascade loading', () => {
  it('selectRefCategory loads mapped targets', async () => {
    const p = useComparisonPage()
    await p.loadStores()
    await flushPromises()
    await p.selectRefCategory(10)
    await flushPromises()

    expect(compApi.fetchMappedTargets).toHaveBeenCalledWith(10, null)
    expect(p.mappedTargets.value).toHaveLength(2)
    expect(p.selectedTargetCategoryIds.value.size).toBe(2)
  })

  it('selectRefCategory shows noMappingsWarning when no mapped cats', async () => {
    vi.mocked(compApi.fetchMappedTargets).mockResolvedValue([])
    const p = useComparisonPage()
    p.referenceStoreId.value = 1
    await p.selectRefCategory(10)
    await flushPromises()

    expect(p.noMappingsWarning.value).toBe(true)
    expect(p.canCompare.value).toBe(false)
  })

  it('canCompare becomes true after mapped targets are selected', async () => {
    const p = useComparisonPage()
    await p.loadStores()
    await flushPromises()
    await p.selectRefCategory(10)
    await flushPromises()

    expect(p.canCompare.value).toBe(true)
  })

  it('setTargetStore reloads mapped targets if ref category already selected', async () => {
    const p = useComparisonPage()
    await p.loadStores()
    await flushPromises()
    await p.selectRefCategory(10)
    await flushPromises()

    vi.mocked(compApi.fetchMappedTargets).mockClear()
    await p.setTargetStore(2)
    await flushPromises()

    expect(compApi.fetchMappedTargets).toHaveBeenCalledWith(10, 2)
  })

  it('toggleTargetCategory removes id from set', async () => {
    const p = useComparisonPage()
    await p.loadStores()
    await flushPromises()
    await p.selectRefCategory(10)
    await flushPromises()

    p.toggleTargetCategory(20, false)
    expect(p.selectedTargetCategoryIds.value.has(20)).toBe(false)
  })
})

describe('useComparisonPage — compare button enablement', () => {
  it('compare button is disabled when no ref category selected', async () => {
    const p = useComparisonPage()
    await p.loadStores()
    await flushPromises()
    expect(p.canCompare.value).toBe(false)
  })

  it('compare button is disabled when no target categories checked', async () => {
    const p = useComparisonPage()
    await p.loadStores()
    await flushPromises()
    await p.selectRefCategory(10)
    await flushPromises()

    // Uncheck all
    p.toggleTargetCategory(20, false)
    p.toggleTargetCategory(21, false)
    expect(p.canCompare.value).toBe(false)
  })

  it('compare button enabled when ref category + at least one target selected', async () => {
    const p = useComparisonPage()
    await p.loadStores()
    await flushPromises()
    await p.selectRefCategory(10)
    await flushPromises()
    expect(p.canCompare.value).toBe(true)
  })
})

describe('useComparisonPage — comparison execution', () => {
  it('calls runComparison with correct body', async () => {
    const p = useComparisonPage()
    await p.loadStores()
    await flushPromises()
    await p.selectRefCategory(10)
    await flushPromises()
    await p.compare()

    expect(compApi.runComparison).toHaveBeenCalledWith(
      expect.objectContaining({
        reference_category_id: 10,
        target_category_ids: expect.arrayContaining([20, 21]),
      }),
    )
    expect(p.hasCompared.value).toBe(true)
    expect(p.comparisonResult.value).not.toBeNull()
  })

  it('sets comparisonError on API failure', async () => {
    vi.mocked(compApi.runComparison).mockRejectedValue(new Error('server error'))
    const p = useComparisonPage()
    await p.loadStores()
    await flushPromises()
    await p.selectRefCategory(10)
    await flushPromises()
    await p.compare()

    expect(p.comparisonError.value).toContain('server error')
    expect(p.hasCompared.value).toBe(false)
  })

  it('autoSuggestions filters is_confirmed===false only', async () => {
    vi.mocked(compApi.runComparison).mockResolvedValue({
      ...comparisonResult,
      confirmed_matches: [
        { ...comparisonResult.confirmed_matches[0], is_confirmed: false },
        { ...comparisonResult.confirmed_matches[0], is_confirmed: true,
          reference_product: { id: 999, name: 'Confirmed', price: null, currency: null, product_url: null },
          target_product:    { id: 998, name: 'Persisted', price: null, currency: null, product_url: null },
        },
      ],
    })
    const p = useComparisonPage()
    await p.loadStores()
    await flushPromises()
    await p.selectRefCategory(10)
    await flushPromises()
    await p.compare()

    expect(p.autoSuggestions.value).toHaveLength(1)
    expect(p.autoSuggestions.value[0].is_confirmed).toBe(false)
  })
})

describe('useComparisonPage — makeDecision', () => {
  it('calls saveMatchDecision and refreshes comparison', async () => {
    const p = useComparisonPage()
    await p.loadStores()
    await flushPromises()
    await p.selectRefCategory(10)
    await flushPromises()
    await p.compare()

    vi.mocked(compApi.runComparison).mockClear()
    await p.makeDecision(100, 200, 'confirmed')

    expect(compApi.saveMatchDecision).toHaveBeenCalledWith(
      expect.objectContaining({
        reference_product_id: 100,
        target_product_id:    200,
        match_status:         'confirmed',
      }),
    )
    expect(compApi.runComparison).toHaveBeenCalledTimes(1)
  })

  it('sets decisionError on failure without crashing', async () => {
    vi.mocked(compApi.saveMatchDecision).mockRejectedValue(new Error('conflict'))
    const p = useComparisonPage()
    await p.loadStores()
    await flushPromises()
    await p.selectRefCategory(10)
    await flushPromises()
    await p.compare()
    await p.makeDecision(100, 200, 'confirmed')

    expect(p.decisionError.value).toContain('conflict')
    expect(p.decisionInProgressKey.value).toBeNull()
  })
})

// ---------------------------------------------------------------------------
// useManualPicker unit tests
// ---------------------------------------------------------------------------

import { useManualPicker } from '@/pages/comparison/composables/useManualPicker'

describe('useManualPicker', () => {
  it('starts with empty state', () => {
    const picker = useManualPicker(100, () => [20, 21])
    expect(picker.products.value).toHaveLength(0)
    expect(picker.isSearching.value).toBe(false)
    expect(picker.includeRejected.value).toBe(false)
  })

  it('does not search when query is less than 2 chars', async () => {
    const picker = useManualPicker(100, () => [20])
    picker.onSearchInput('a')
    await flushPromises()
    expect(compApi.searchEligibleTargetProducts).not.toHaveBeenCalled()
    expect(picker.products.value).toHaveLength(0)
  })

  it('calls searchEligibleTargetProducts after debounce', async () => {
    vi.useFakeTimers()
    vi.mocked(compApi.searchEligibleTargetProducts).mockResolvedValue([
      { id: 300, name: 'Found product', price: '100', currency: 'UAH', category: null },
    ])
    const picker = useManualPicker(100, () => [20, 21])
    picker.onSearchInput('Bauer')
    vi.runAllTimers()
    await flushPromises()

    expect(compApi.searchEligibleTargetProducts).toHaveBeenCalledWith(
      expect.objectContaining({ referenceProductId: 100, search: 'Bauer', includeRejected: false }),
    )
    expect(picker.products.value).toHaveLength(1)
    vi.useRealTimers()
  })

  it('retriggers search when includeRejected toggles with active query', async () => {
    vi.useFakeTimers()
    const picker = useManualPicker(100, () => [20])
    picker.onSearchInput('Vapor')
    vi.runAllTimers()
    await flushPromises()
    vi.mocked(compApi.searchEligibleTargetProducts).mockClear()

    picker.setIncludeRejected(true)
    vi.runAllTimers()
    await flushPromises()

    expect(compApi.searchEligibleTargetProducts).toHaveBeenCalledWith(
      expect.objectContaining({ includeRejected: true }),
    )
    vi.useRealTimers()
  })
})

// ---------------------------------------------------------------------------
// ComparisonSummaryBar component tests
// ---------------------------------------------------------------------------

import ComparisonSummaryBar from '@/pages/comparison/components/ComparisonSummaryBar.vue'

describe('ComparisonSummaryBar', () => {
  it('shows comparing text when comparing=true', () => {
    const w = mount(ComparisonSummaryBar, {
      props: { result: null, comparing: true, errorText: null },
    })
    expect(w.text()).toContain('Виконується порівняння')
  })

  it('shows error when errorText is set', () => {
    const w = mount(ComparisonSummaryBar, {
      props: { result: null, comparing: false, errorText: 'Помилка: щось пішло не так' },
    })
    expect(w.text()).toContain('Помилка')
  })

  it('renders summary counts after successful comparison', () => {
    const w = mount(ComparisonSummaryBar, {
      props: { result: comparisonResult, comparing: false, errorText: null },
    })
    expect(w.text()).toContain('Авто-пропозиції: 1')
    expect(w.text()).toContain('Кандидатів: 1')
    expect(w.text()).toContain('Тільки в референсі: 1')
    expect(w.text()).toContain('Тільки в цільовому: 1')
  })

  it('shows nothing when result is null and not comparing', () => {
    const w = mount(ComparisonSummaryBar, {
      props: { result: null, comparing: false, errorText: null },
    })
    expect(w.text().trim()).toBe('')
  })
})

// ---------------------------------------------------------------------------
// ReferenceCategoryList component tests
// ---------------------------------------------------------------------------

import ReferenceCategoryList from '@/pages/comparison/components/ReferenceCategoryList.vue'

describe('ReferenceCategoryList', () => {
  it('renders category names', () => {
    const w = mount(ReferenceCategoryList, {
      props: { categories: refCats, activeCategoryId: null, loading: false },
    })
    expect(w.text()).toContain('Ковзани')
    expect(w.text()).toContain('Шлеми')
  })

  it('emits select on click', async () => {
    const w = mount(ReferenceCategoryList, {
      props: { categories: refCats, activeCategoryId: null, loading: false },
    })
    await w.findAll('[role="button"]')[0].trigger('click')
    expect(w.emitted('select')).toBeTruthy()
    expect(w.emitted('select')![0]).toEqual([10])
  })

  it('marks active category', () => {
    const w = mount(ReferenceCategoryList, {
      props: { categories: refCats, activeCategoryId: 10, loading: false },
    })
    const items = w.findAll('.category-item')
    expect(items[0].classes()).toContain('active')
    expect(items[1].classes()).not.toContain('active')
  })

  it('shows loading message when loading=true', () => {
    const w = mount(ReferenceCategoryList, {
      props: { categories: [], activeCategoryId: null, loading: true },
    })
    expect(w.text()).toContain('Завантаження')
  })
})

// ---------------------------------------------------------------------------
// MappedTargetCategoryList component tests
// ---------------------------------------------------------------------------

import MappedTargetCategoryList from '@/pages/comparison/components/MappedTargetCategoryList.vue'

describe('MappedTargetCategoryList', () => {
  it('renders checkboxes for each mapped target', () => {
    const w = mount(MappedTargetCategoryList, {
      props: {
        mappedTargets,
        selectedIds:        new Set([20, 21]),
        selectedCategoryId: 10,
        loading:            false,
        noMappingsWarning:  false,
      },
    })
    expect(w.findAll('input[type="checkbox"]')).toHaveLength(2)
  })

  it('shows warning when noMappingsWarning=true', () => {
    const w = mount(MappedTargetCategoryList, {
      props: {
        mappedTargets:      [],
        selectedIds:        new Set<number>(),
        selectedCategoryId: 10,
        loading:            false,
        noMappingsWarning:  true,
      },
    })
    expect(w.text()).toContain('ще не створено меппінг')
    expect(w.html()).toContain('/service')
  })

  it('emits toggle with correct args on checkbox change', async () => {
    const w = mount(MappedTargetCategoryList, {
      props: {
        mappedTargets,
        selectedIds:        new Set([20, 21]),
        selectedCategoryId: 10,
        loading:            false,
        noMappingsWarning:  false,
      },
    })
    const cb = w.findAll('input[type="checkbox"]')[0]
    await cb.setValue(false)
    expect(w.emitted('toggle')).toBeTruthy()
    expect(w.emitted('toggle')![0][0]).toBe(20)
    expect(w.emitted('toggle')![0][1]).toBe(false)
  })
})

