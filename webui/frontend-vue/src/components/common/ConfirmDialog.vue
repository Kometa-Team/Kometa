<script setup lang="ts">
import { useUIStore } from '@/stores';
import Modal from './Modal.vue';
import Button from './Button.vue';

const ui = useUIStore();

const variantColors = {
  danger: 'text-error',
  warning: 'text-warning',
  info: 'text-info',
};

const variantIcons = {
  danger:
    'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
  warning:
    'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
  info: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
};
</script>

<template>
  <Modal
    :open="ui.confirmDialog.open"
    :show-close-button="false"
    size="sm"
    @close="ui.resolveConfirm(false)"
  >
    <div
      v-if="ui.confirmDialog.options"
      class="text-center"
    >
      <div
        :class="[
          'mx-auto w-12 h-12 flex items-center justify-center rounded-full mb-4',
          ui.confirmDialog.options.variant === 'danger' ? 'bg-error-bg' : 'bg-warning-bg',
        ]"
      >
        <svg
          :class="[
            'w-6 h-6',
            variantColors[ui.confirmDialog.options.variant || 'warning'],
          ]"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            :d="variantIcons[ui.confirmDialog.options.variant || 'warning']"
          />
        </svg>
      </div>

      <h3 class="text-lg font-semibold text-content-primary mb-2">
        {{ ui.confirmDialog.options.title }}
      </h3>

      <p class="text-sm text-content-secondary mb-6">
        {{ ui.confirmDialog.options.message }}
      </p>

      <div class="flex gap-3 justify-center">
        <Button
          variant="secondary"
          @click="ui.resolveConfirm(false)"
        >
          {{ ui.confirmDialog.options.cancelText || 'Cancel' }}
        </Button>
        <Button
          :variant="ui.confirmDialog.options.variant === 'danger' ? 'danger' : 'primary'"
          @click="ui.resolveConfirm(true)"
        >
          {{ ui.confirmDialog.options.confirmText || 'Confirm' }}
        </Button>
      </div>
    </div>
  </Modal>
</template>
