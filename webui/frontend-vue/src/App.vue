<script setup lang="ts">
import { computed } from 'vue';
import { useUIStore, useRunStore } from '@/stores';
import { useRunStatus } from '@/api';
import TheHeader from '@/components/layout/TheHeader.vue';
import TheSidebar from '@/components/layout/TheSidebar.vue';
import MainContent from '@/components/layout/MainContent.vue';
import { ToastContainer, ConfirmDialog } from '@/components/common';

const ui = useUIStore();
const run = useRunStore();

// Fetch run status on mount and poll while running
const { data: runStatus } = useRunStatus();

// Update run store when status changes
const isRunning = computed(() => runStatus.value?.is_running ?? false);
</script>

<template>
  <div class="min-h-screen bg-surface-base flex flex-col">
    <!-- Safety Banner -->
    <div
      :class="[
        'px-5 py-2 text-center font-semibold text-sm sticky top-0 z-50',
        run.applyEnabled
          ? 'bg-error text-white'
          : 'bg-success text-white',
      ]"
    >
      <template v-if="run.applyEnabled">
        APPLY MODE ENABLED - Changes will be applied to your Plex library
      </template>
      <template v-else>
        SAFE MODE - Dry run only, no changes will be made
      </template>
    </div>

    <!-- Main Layout -->
    <div class="flex flex-1 overflow-hidden">
      <!-- Sidebar -->
      <TheSidebar />

      <!-- Main Content Area -->
      <div class="flex-1 flex flex-col overflow-hidden">
        <!-- Header -->
        <TheHeader :is-running="isRunning" />

        <!-- Content -->
        <main class="flex-1 overflow-auto p-4">
          <MainContent />
        </main>
      </div>
    </div>

    <!-- Toast Notifications -->
    <ToastContainer />

    <!-- Confirm Dialog -->
    <ConfirmDialog />
  </div>
</template>
