import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import Button from '@/components/common/Button.vue';

describe('Button', () => {
  it('renders slot content', () => {
    const wrapper = mount(Button, {
      slots: {
        default: 'Click me',
      },
    });

    expect(wrapper.text()).toBe('Click me');
  });

  it('emits click event when clicked', async () => {
    const wrapper = mount(Button);

    await wrapper.trigger('click');

    expect(wrapper.emitted('click')).toBeTruthy();
    expect(wrapper.emitted('click')).toHaveLength(1);
  });

  it('does not emit click when disabled', async () => {
    const wrapper = mount(Button, {
      props: { disabled: true },
    });

    await wrapper.trigger('click');

    expect(wrapper.emitted('click')).toBeFalsy();
  });

  it('does not emit click when loading', async () => {
    const wrapper = mount(Button, {
      props: { loading: true },
    });

    await wrapper.trigger('click');

    expect(wrapper.emitted('click')).toBeFalsy();
  });

  it('shows spinner when loading', () => {
    const wrapper = mount(Button, {
      props: { loading: true },
      slots: {
        default: 'Submit',
      },
    });

    expect(wrapper.find('.spinner').exists()).toBe(true);
    expect(wrapper.text()).not.toContain('Submit');
  });

  it('applies variant classes', () => {
    const wrapper = mount(Button, {
      props: { variant: 'primary' },
    });

    expect(wrapper.classes()).toContain('btn-primary');
  });

  it('applies size classes', () => {
    const wrapper = mount(Button, {
      props: { size: 'lg' },
    });

    expect(wrapper.classes()).toContain('btn-lg');
  });

  it('applies full width class when fullWidth is true', () => {
    const wrapper = mount(Button, {
      props: { fullWidth: true },
    });

    expect(wrapper.classes()).toContain('w-full');
  });

  it('sets correct button type', () => {
    const wrapper = mount(Button, {
      props: { type: 'submit' },
    });

    expect(wrapper.attributes('type')).toBe('submit');
  });

  it('is disabled when disabled prop is true', () => {
    const wrapper = mount(Button, {
      props: { disabled: true },
    });

    expect(wrapper.attributes('disabled')).toBeDefined();
  });
});
