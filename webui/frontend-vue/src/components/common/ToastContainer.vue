<script setup lang="ts">
import { useUIStore } from '@/stores';
import Toast from './Toast.vue';

const ui = useUIStore();
</script>

<template>
  <Teleport to="body">
    <div class="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm">
      <TransitionGroup name="slide">
        <Toast
          v-for="toast in ui.toasts"
          :key="toast.id"
          :toast="toast"
          @dismiss="ui.dismissToast"
        />
      </TransitionGroup>
    </div>
  </Teleport>
</template>
