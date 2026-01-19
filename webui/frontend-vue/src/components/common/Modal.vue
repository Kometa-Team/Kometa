<script setup lang="ts">
import { watch, onMounted, onUnmounted } from 'vue';

interface Props {
  open: boolean;
  title?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  closeOnOverlay?: boolean;
  closeOnEscape?: boolean;
  showCloseButton?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  closeOnOverlay: true,
  closeOnEscape: true,
  showCloseButton: true,
});

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'update:open', value: boolean): void;
}>();

const sizeClasses = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
  full: 'max-w-full mx-4',
};

const handleOverlayClick = () => {
  if (props.closeOnOverlay) {
    close();
  }
};

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && props.closeOnEscape && props.open) {
    close();
  }
};

const close = () => {
  emit('close');
  emit('update:open', false);
};

// Lock body scroll when modal is open
watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
  }
);

onMounted(() => {
  document.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown);
  document.body.style.overflow = '';
});
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="open"
        class="fixed inset-0 z-50 flex items-center justify-center"
      >
        <!-- Overlay -->
        <div
          class="absolute inset-0 bg-black/60 backdrop-blur-sm"
          @click="handleOverlayClick"
        />

        <!-- Modal content -->
        <div
          :class="[
            'relative w-full bg-surface-secondary border border-border rounded-lg shadow-xl',
            sizeClasses[size],
          ]"
          role="dialog"
          aria-modal="true"
        >
          <!-- Header -->
          <div
            v-if="title || $slots.header || showCloseButton"
            class="flex items-center justify-between px-4 py-3 border-b border-border"
          >
            <slot name="header">
              <h2 class="text-lg font-semibold text-content-primary">
                {{ title }}
              </h2>
            </slot>

            <button
              v-if="showCloseButton"
              type="button"
              class="p-1 rounded-md text-content-secondary hover:text-content hover:bg-surface-tertiary transition-colors"
              aria-label="Close modal"
              @click="close"
            >
              <svg
                class="w-5 h-5"
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

          <!-- Body -->
          <div class="p-4">
            <slot />
          </div>

          <!-- Footer -->
          <div
            v-if="$slots.footer"
            class="flex items-center justify-end gap-2 px-4 py-3 border-t border-border"
          >
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
