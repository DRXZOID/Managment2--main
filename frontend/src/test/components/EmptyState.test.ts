import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import EmptyState from '@/components/base/EmptyState.vue'

describe('EmptyState', () => {
  it('renders the title prop', () => {
    const wrapper = mount(EmptyState, { props: { title: 'Немає задач' } })
    expect(wrapper.text()).toContain('Немає задач')
  })

  it('renders the body prop when provided', () => {
    const wrapper = mount(EmptyState, {
      props: { title: 'Порожньо', body: 'Додайте першу задачу' },
    })
    expect(wrapper.text()).toContain('Додайте першу задачу')
  })

  it('does not render body element when body is absent', () => {
    const wrapper = mount(EmptyState, { props: { title: 'Нічого' } })
    expect(wrapper.find('.empty-state-body').exists()).toBe(false)
  })

  it('renders icon when provided', () => {
    const wrapper = mount(EmptyState, {
      props: { icon: '🗓', title: 'Test' },
    })
    expect(wrapper.find('.empty-state-icon').exists()).toBe(true)
    expect(wrapper.find('.empty-state-icon').text()).toBe('🗓')
  })

  it('does not render icon element when icon is absent', () => {
    const wrapper = mount(EmptyState, { props: { title: 'No icon' } })
    expect(wrapper.find('.empty-state-icon').exists()).toBe(false)
  })

  it('has the empty-state CSS class', () => {
    const wrapper = mount(EmptyState, { props: { title: 'Test' } })
    expect(wrapper.classes()).toContain('empty-state')
  })

  it('renders title slot over title prop', () => {
    const wrapper = mount(EmptyState, {
      props: { title: 'Prop title' },
      slots: { title: 'Slot title' },
    })
    expect(wrapper.text()).toContain('Slot title')
    expect(wrapper.text()).not.toContain('Prop title')
  })

  it('renders action slot when provided', () => {
    const wrapper = mount(EmptyState, {
      props: { title: 'Empty' },
      slots: { action: '<button>Створити</button>' },
    })
    expect(wrapper.find('button').exists()).toBe(true)
    expect(wrapper.find('button').text()).toBe('Створити')
  })
})

