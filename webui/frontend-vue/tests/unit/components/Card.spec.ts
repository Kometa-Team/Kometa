import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import Card from '@/components/common/Card.vue';

describe('Card', () => {
  it('renders title when provided', () => {
    const wrapper = mount(Card, {
      props: { title: 'Test Card' },
    });

    expect(wrapper.text()).toContain('Test Card');
  });

  it('renders subtitle when provided', () => {
    const wrapper = mount(Card, {
      props: { title: 'Title', subtitle: 'Subtitle text' },
    });

    expect(wrapper.text()).toContain('Subtitle text');
  });

  it('renders slot content', () => {
    const wrapper = mount(Card, {
      slots: {
        default: 'Card content here',
      },
    });

    expect(wrapper.text()).toContain('Card content here');
  });

  it('renders header slot', () => {
    const wrapper = mount(Card, {
      slots: {
        header: '<span data-test="header">Custom Header</span>',
      },
    });

    expect(wrapper.find('[data-test="header"]').exists()).toBe(true);
  });

  it('renders footer slot', () => {
    const wrapper = mount(Card, {
      slots: {
        footer: '<button>Footer Button</button>',
      },
    });

    expect(wrapper.find('button').text()).toBe('Footer Button');
  });

  it('applies padding class based on prop', () => {
    const wrapper = mount(Card, {
      props: { padding: 'lg' },
      slots: { default: 'Content' },
    });

    expect(wrapper.find('.card-body').classes()).toContain('p-6');
  });

  it('applies hoverable class when hoverable is true', () => {
    const wrapper = mount(Card, {
      props: { hoverable: true },
    });

    expect(wrapper.find('.card').classes()).toContain('hover:border-kometa-gold');
  });

  it('emits click event when clickable', async () => {
    const wrapper = mount(Card, {
      props: { clickable: true },
    });

    await wrapper.find('.card').trigger('click');

    expect(wrapper.emitted('click')).toBeTruthy();
  });

  it('does not emit click when not clickable', async () => {
    const wrapper = mount(Card, {
      props: { clickable: false },
    });

    await wrapper.find('.card').trigger('click');

    expect(wrapper.emitted('click')).toBeFalsy();
  });
});
