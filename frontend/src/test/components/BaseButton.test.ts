import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseButton from '@/components/base/BaseButton.vue'

describe('BaseButton', () => {
  it('renders a <button> element', () => {
    const wrapper = mount(BaseButton, { slots: { default: 'Click' } })
    expect(wrapper.element.tagName).toBe('BUTTON')
  })

  it('renders slot content', () => {
    const wrapper = mount(BaseButton, { slots: { default: 'Зберегти' } })
    expect(wrapper.text()).toContain('Зберегти')
  })

  it('always has the btn class', () => {
    const wrapper = mount(BaseButton)
    expect(wrapper.classes()).toContain('btn')
  })

  it('default type is button', () => {
    const wrapper = mount(BaseButton)
    expect(wrapper.attributes('type')).toBe('button')
  })

  it('type=submit sets submit type', () => {
    const wrapper = mount(BaseButton, { props: { type: 'submit' } })
    expect(wrapper.attributes('type')).toBe('submit')
  })

  it('disabled prop disables the button', () => {
    const wrapper = mount(BaseButton, { props: { disabled: true } })
    expect((wrapper.element as HTMLButtonElement).disabled).toBe(true)
  })

  it('loading prop also disables the button', () => {
    const wrapper = mount(BaseButton, { props: { loading: true } })
    expect((wrapper.element as HTMLButtonElement).disabled).toBe(true)
  })

  it.each([
    ['outline', 'btn-outline'],
    ['danger',  'btn-danger'],
    ['ghost',   'btn-ghost'],
  ] as const)('variant="%s" → CSS class "%s"', (variant, cssClass) => {
    const wrapper = mount(BaseButton, { props: { variant } })
    expect(wrapper.classes()).toContain(cssClass)
  })

  it('variant=default adds no extra variant class', () => {
    const wrapper = mount(BaseButton, { props: { variant: 'default' } })
    expect(wrapper.classes()).not.toContain('btn-outline')
    expect(wrapper.classes()).not.toContain('btn-danger')
    expect(wrapper.classes()).not.toContain('btn-ghost')
  })

  it('size=sm adds btn-sm class', () => {
    const wrapper = mount(BaseButton, { props: { size: 'sm' } })
    expect(wrapper.classes()).toContain('btn-sm')
  })

  it('emits a click event', async () => {
    const wrapper = mount(BaseButton, { slots: { default: 'OK' } })
    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
  })
})

