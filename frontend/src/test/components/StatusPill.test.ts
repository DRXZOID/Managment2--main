import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import StatusPill from '@/components/base/StatusPill.vue'

describe('StatusPill', () => {
  it('renders the label prop as text', () => {
    const wrapper = mount(StatusPill, {
      props: { kind: 'success', label: '✓ success' },
    })
    expect(wrapper.text()).toBe('✓ success')
  })

  it('renders slot content over label prop', () => {
    const wrapper = mount(StatusPill, {
      props: { kind: 'info' },
      slots: { default: 'custom text' },
    })
    expect(wrapper.text()).toBe('custom text')
  })

  it('applies status-pill class always', () => {
    const wrapper = mount(StatusPill, { props: { kind: 'warning' } })
    expect(wrapper.classes()).toContain('status-pill')
  })

  it.each([
    ['info',    'status-info'],
    ['success', 'status-success'],
    ['warning', 'status-warning'],
    ['error',   'status-error'],
    ['muted',   'status-muted'],
  ] as const)('kind="%s" → CSS class "%s"', (kind, cssClass) => {
    const wrapper = mount(StatusPill, { props: { kind } })
    expect(wrapper.classes()).toContain(cssClass)
  })

  it('renders a <span> element', () => {
    const wrapper = mount(StatusPill, { props: { kind: 'success' } })
    expect(wrapper.element.tagName).toBe('SPAN')
  })
})

