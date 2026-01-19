<script setup lang="ts">
interface Props {
  variant?: 'success' | 'warning' | 'error' | 'info' | 'default';
  size?: 'sm' | 'md';
  dot?: boolean;
}

withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'md',
  dot: false,
});

const variantClasses = {
  success: 'badge-success',
  warning: 'badge-warning',
  error: 'badge-error',
  info: 'badge-info',
  default: 'bg-surface-tertiary text-content-secondary',
};

const sizeClasses = {
  sm: 'px-1.5 py-0.5 text-xs',
  md: 'px-2 py-0.5 text-xs',
};

const dotClasses = {
  success: 'bg-success',
  warning: 'bg-warning',
  error: 'bg-error',
  info: 'bg-info',
  default: 'bg-content-muted',
};
</script>

<template>
  <span
    :class="[
      'badge inline-flex items-center gap-1 font-medium rounded-full',
      variantClasses[variant],
      sizeClasses[size],
    ]"
  >
    <span
      v-if="dot"
      :class="['w-1.5 h-1.5 rounded-full', dotClasses[variant]]"
    />
    <slot />
  </span>
</template>
