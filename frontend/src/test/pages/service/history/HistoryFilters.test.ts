import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import HistoryFilters from '@/pages/service/history/components/HistoryFilters.vue'

const stores = [
  { id: 1, name: 'prohockey', is_reference: true, base_url: null },
  { id: 2, name: 'hockeyworld', is_reference: false, base_url: null },
]

describe('HistoryFilters', () => {
  it('renders store options from props', () => {
    const wrapper = mount(HistoryFilters, {
      props: { stores, storeId: '', runType: '', status: '', triggerType: '' },
    })
    const options = wrapper.find('#hw-store-filter').findAll('option')
    // first option is "Будь-який" placeholder
    expect(options.length).toBe(3)
    expect(options[1].text()).toContain('prohockey')
    expect(options[2].text()).toContain('hockeyworld')
  })

  it('marks reference store in option text', () => {
    const wrapper = mount(HistoryFilters, {
      props: { stores, storeId: '', runType: '', status: '', triggerType: '' },
    })
    const opt = wrapper.find('#hw-store-filter').findAll('option')[1]
    expect(opt.text()).toContain('(ref)')
  })

  it('emits update:storeId on store select change', async () => {
    const wrapper = mount(HistoryFilters, {
      props: { stores, storeId: '', runType: '', status: '', triggerType: '' },
    })
    const select = wrapper.find('#hw-store-filter')
    await select.setValue('2')
    expect(wrapper.emitted('update:storeId')).toBeTruthy()
    expect(wrapper.emitted('update:storeId')![0]).toEqual(['2'])
  })

  it('emits update:status on status select change', async () => {
    const wrapper = mount(HistoryFilters, {
      props: { stores, storeId: '', runType: '', status: '', triggerType: '' },
    })
    const select = wrapper.find('#hw-status-filter')
    await select.setValue('failed')
    expect(wrapper.emitted('update:status')).toBeTruthy()
    expect(wrapper.emitted('update:status')![0]).toEqual(['failed'])
  })

  it('emits update:runType on run type select change', async () => {
    const wrapper = mount(HistoryFilters, {
      props: { stores, storeId: '', runType: '', status: '', triggerType: '' },
    })
    const select = wrapper.find('#hw-type-filter')
    await select.setValue('store_category_sync')
    expect(wrapper.emitted('update:runType')).toBeTruthy()
    expect(wrapper.emitted('update:runType')![0]).toEqual(['store_category_sync'])
  })

  it('emits update:triggerType on trigger select change', async () => {
    const wrapper = mount(HistoryFilters, {
      props: { stores, storeId: '', runType: '', status: '', triggerType: '' },
    })
    const select = wrapper.find('#hw-trigger-filter')
    await select.setValue('scheduled')
    expect(wrapper.emitted('update:triggerType')).toBeTruthy()
    expect(wrapper.emitted('update:triggerType')![0]).toEqual(['scheduled'])
  })
})

