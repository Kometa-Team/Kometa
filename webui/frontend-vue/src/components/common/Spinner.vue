<script setup lang="ts">
interface Props {
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'white' | 'current';
}

withDefaults(defineProps<Props>(), {
  size: 'md',
  color: 'primary',
});

const sizeClasses = {
  sm: 'w-4 h-4 border-2',
  md: 'w-6 h-6 border-2',
  lg: 'w-8 h-8 border-3',
};

const colorClasses = {
  primary: 'border-border border-t-kometa-gold',
  white: 'border-white/30 border-t-white',
  current: 'border-current/30 border-t-current',
};
</script>

<template>
  <div
    :class="[
      'spinner animate-spin rounded-full',
      sizeClasses[size],
      colorClasses[color],
    ]"
    role="status"
    aria-label="Loading"
  >
    <span class="sr-only">Loading...</span>
  </div>
</template>
