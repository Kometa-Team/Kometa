<script setup lang="ts">
interface Props {
  title?: string;
  subtitle?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hoverable?: boolean;
  clickable?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  padding: 'md',
  hoverable: false,
  clickable: false,
});

const emit = defineEmits<{
  (e: 'click', event: MouseEvent): void;
}>();

const paddingClasses = {
  none: '',
  sm: 'p-2',
  md: 'p-4',
  lg: 'p-6',
};
</script>

<template>
  <div
    :class="[
      'card',
      {
        'hover:border-kometa-gold transition-colors': hoverable,
        'cursor-pointer': clickable,
      },
    ]"
    @click="clickable ? emit('click', $event) : undefined"
  >
    <div
      v-if="title || $slots.header"
      class="card-header"
    >
      <slot name="header">
        <div>
          <h3 class="text-md font-semibold text-content-primary">
            {{ title }}
          </h3>
          <p
            v-if="subtitle"
            class="text-sm text-content-secondary mt-0.5"
          >
            {{ subtitle }}
          </p>
        </div>
      </slot>
      <div
        v-if="$slots.headerActions"
        class="ml-auto"
      >
        <slot name="headerActions" />
      </div>
    </div>

    <div :class="['card-body', paddingClasses[padding]]">
      <slot />
    </div>

    <div
      v-if="$slots.footer"
      class="card-footer"
    >
      <slot name="footer" />
    </div>
  </div>
</template>
