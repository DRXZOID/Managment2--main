/**
 * useGapFilters.ts — Filter state and dependent cascade loading for /gap.
 *
 * Manages the three-stage cascade:
 *   1. stores load → populate target store selector
 *   2. target store select → load reference categories from first ref store
 *   3. ref category select → load mapped target categories (checkboxes)
 *
 * Exposes computed `canLoad` to drive the Load button enabled state.
 */
import { ref, computed, reactive } from 'vue'
import type { Ref, ComputedRef } from 'vue'
import { fetchStores, fetchCategoriesForStore } from '@/api/client'
import { fetchMappedTargetCategories } from '@/api/gap'
import type { StoreSummary, CategorySummary } from '@/types/store'
import type { MappedTargetCategory } from '@/types/gap'

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

export interface GapStatusFilters {
  new: boolean
  in_progress: boolean
  done: boolean
}

export interface GapFiltersState {
  // Stores
  targetStores: Ref<StoreSummary[]>
  referenceStores: Ref<StoreSummary[]>
  storesLoading: Ref<boolean>
  storesError: Ref<string | null>

  // Selected values
  selectedTargetStoreId: Ref<number | null>
  selectedRefCategoryId: Ref<number | null>

  // Dependent data
  referenceCategories: Ref<CategorySummary[]>
  refCategoriesLoading: Ref<boolean>

  mappedTargetCats: Ref<MappedTargetCategory[]>
  mappedCatsLoading: Ref<boolean>
  noMappingsWarning: Ref<boolean>

  // Selected checkbox state
  selectedTargetCatIds: Ref<Set<number>>

  // Other filter values
  search: Ref<string>
  onlyAvailable: Ref<boolean>
  statuses: GapStatusFilters

  // Derived
  canLoad: ComputedRef<boolean>

  // Actions
  loadStores: () => Promise<void>
  setTargetStore: (id: number | null) => Promise<void>
  setRefCategory: (id: number | null) => Promise<void>
  toggleTargetCat: (id: number, checked: boolean) => void
}

// ---------------------------------------------------------------------------
// Composable
// ---------------------------------------------------------------------------

export function useGapFilters(): GapFiltersState {
  // ── Stores ────────────────────────────────────────────────────
  const allStores = ref<StoreSummary[]>([])
  const targetStores = computed(() => allStores.value.filter((s) => !s.is_reference))
  const referenceStores = computed(() => allStores.value.filter((s) => s.is_reference))
  const storesLoading = ref(false)
  const storesError = ref<string | null>(null)

  // ── Selections ────────────────────────────────────────────────
  const selectedTargetStoreId = ref<number | null>(null)
  const selectedRefCategoryId = ref<number | null>(null)

  // ── Reference categories ──────────────────────────────────────
  const referenceCategories = ref<CategorySummary[]>([])
  const refCategoriesLoading = ref(false)

  // ── Mapped target categories (checkboxes) ─────────────────────
  const mappedTargetCats = ref<MappedTargetCategory[]>([])
  const mappedCatsLoading = ref(false)
  const noMappingsWarning = ref(false)

  // All mapped cats are checked by default when loaded
  const selectedTargetCatIds = ref<Set<number>>(new Set())

  // ── Other filters ─────────────────────────────────────────────
  const search = ref('')
  const onlyAvailable = ref(false)
  const statuses = reactive<GapStatusFilters>({
    new: true,
    in_progress: true,
    done: false,
  })

  // ── Derived ───────────────────────────────────────────────────
  const canLoad = computed(
    () =>
      selectedTargetCatIds.value.size > 0 &&
      !mappedCatsLoading.value &&
      !noMappingsWarning.value,
  )

  // ── Actions ───────────────────────────────────────────────────

  async function loadStores(): Promise<void> {
    storesLoading.value = true
    storesError.value = null
    try {
      allStores.value = await fetchStores()
    } catch (err) {
      storesError.value = 'Помилка завантаження магазинів: ' + (err instanceof Error ? err.message : String(err))
    } finally {
      storesLoading.value = false
    }
  }

  async function setTargetStore(id: number | null): Promise<void> {
    selectedTargetStoreId.value = id
    selectedRefCategoryId.value = null
    referenceCategories.value = []
    mappedTargetCats.value = []
    selectedTargetCatIds.value = new Set()
    noMappingsWarning.value = false

    if (!id) return

    refCategoriesLoading.value = true
    try {
      const refStore = referenceStores.value[0]
      if (!refStore) {
        referenceCategories.value = []
        return
      }
      referenceCategories.value = await fetchCategoriesForStore(refStore.id)
    } catch {
      referenceCategories.value = []
    } finally {
      refCategoriesLoading.value = false
    }
  }

  async function setRefCategory(id: number | null): Promise<void> {
    selectedRefCategoryId.value = id
    mappedTargetCats.value = []
    selectedTargetCatIds.value = new Set()
    noMappingsWarning.value = false

    if (!id || !selectedTargetStoreId.value) return

    mappedCatsLoading.value = true
    try {
      const cats = await fetchMappedTargetCategories(id, selectedTargetStoreId.value)
      mappedTargetCats.value = cats
      if (!cats.length) {
        noMappingsWarning.value = true
      } else {
        // All checked by default
        selectedTargetCatIds.value = new Set(cats.map((c) => c.target_category_id))
      }
    } catch {
      mappedTargetCats.value = []
    } finally {
      mappedCatsLoading.value = false
    }
  }

  function toggleTargetCat(id: number, checked: boolean): void {
    const next = new Set(selectedTargetCatIds.value)
    checked ? next.add(id) : next.delete(id)
    selectedTargetCatIds.value = next
  }

  return {
    targetStores,
    referenceStores,
    storesLoading,
    storesError,
    selectedTargetStoreId,
    selectedRefCategoryId,
    referenceCategories,
    refCategoriesLoading,
    mappedTargetCats,
    mappedCatsLoading,
    noMappingsWarning,
    selectedTargetCatIds,
    search,
    onlyAvailable,
    statuses,
    canLoad,
    loadStores,
    setTargetStore,
    setRefCategory,
    toggleTargetCat,
  }
}

