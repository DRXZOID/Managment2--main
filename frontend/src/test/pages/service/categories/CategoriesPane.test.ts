import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import CategoriesPane from '@/pages/service/categories/components/CategoriesPane.vue'

const stores = [
  { id: 1, name: 'prohockey', is_reference: true, base_url: null },
  { id: 2, name: 'hockeyworld', is_reference: false, base_url: null },
]

const defaultProps = {
  kind: 'reference' as const,
  stores,
  selectedStoreId: null,
  categories: [],
  loading: false,
  statusText: 'Очікування',
  statusKind: 'info' as const,
  syncLoading: false,
  syncProductsLoadingId: null,
}

describe('CategoriesPane', () => {
  it('renders reference label for kind=reference', () => {
    const w = mount(CategoriesPane, { props: defaultProps })
    expect(w.text()).toContain('Референсний магазин')
  })

  it('renders target label for kind=target', () => {
    const w = mount(CategoriesPane, { props: { ...defaultProps, kind: 'target' } })
    expect(w.text()).toContain('Цільовий магазин')
  })

  it('renders store options', () => {
    const w = mount(CategoriesPane, { props: defaultProps })
    const options = w.find('select').findAll('option')
    // first is placeholder "Оберіть"
    expect(options.length).toBe(3)
    expect(options[1].text()).toContain('prohockey')
  })

  it('emits update:selected-store-id on store select change', async () => {
    const w = mount(CategoriesPane, { props: defaultProps })
    await w.find('select').setValue('2')
    expect(w.emitted('update:selected-store-id')).toBeTruthy()
    expect(w.emitted('update:selected-store-id')![0]).toEqual([2])
  })

  it('emits update:selected-store-id with null when blank selected', async () => {
    const w = mount(CategoriesPane, { props: { ...defaultProps, selectedStoreId: 1 } })
    await w.find('select').setValue('')
    expect(w.emitted('update:selected-store-id')![0]).toEqual([null])
  })

  it('disables sync button when no store selected', () => {
    const w = mount(CategoriesPane, { props: defaultProps })
    const btn = w.find('button.btn')
    expect((btn.element as HTMLButtonElement).disabled).toBe(true)
  })

  it('enables sync button when store is selected', () => {
    const w = mount(CategoriesPane, { props: { ...defaultProps, selectedStoreId: 1 } })
    const btn = w.find('button.btn')
    expect((btn.element as HTMLButtonElement).disabled).toBe(false)
  })

  it('emits sync-categories when sync button clicked', async () => {
    const w = mount(CategoriesPane, { props: { ...defaultProps, selectedStoreId: 1 } })
    await w.find('button.btn').trigger('click')
    expect(w.emitted('sync-categories')).toBeTruthy()
  })

  it('shows status text', () => {
    const w = mount(CategoriesPane, { props: { ...defaultProps, statusText: 'Категорій: 5', statusKind: 'success' as const } })
    expect(w.text()).toContain('Категорій: 5')
  })
})

