<script setup lang="ts">
import type { Toast } from '@/types';

interface Props {
  toast: Toast;
}

defineProps<Props>();

const emit = defineEmits<{
  (e: 'dismiss', id: string): void;
}>();

const iconPaths = {
  success:
    'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
  error:
    'M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z',
  warning:
    'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
  info: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
};

const typeClasses = {
  success: 'bg-success-bg border-success text-success',
  error: 'bg-error-bg border-error text-error',
  warning: 'bg-warning-bg border-warning text-warning',
  info: 'bg-info-bg border-info text-info',
};
</script>

<template>
  <div
    :class="[
      'flex items-start gap-3 p-3 rounded-lg border shadow-md',
      typeClasses[toast.type],
    ]"
    role="alert"
  >
    <svg
      class="w-5 h-5 flex-shrink-0 mt-0.5"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        :d="iconPaths[toast.type]"
      />
    </svg>

    <p class="flex-1 text-sm text-content">
      {{ toast.message }}
    </p>

    <button
      v-if="toast.dismissible"
      type="button"
      class="flex-shrink-0 p-0.5 rounded hover:bg-surface-tertiary transition-colors"
      aria-label="Dismiss"
      @click="emit('dismiss', toast.id)"
    >
      <svg
        class="w-4 h-4"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M6 18L18 6M6 6l12 12"
        />
      </svg>
    </button>
  </div>
</template>
