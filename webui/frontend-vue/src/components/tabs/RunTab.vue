<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useRunStore, useConfigStore } from '@/stores';
import { useRunStatus, useStartRun, useStartApplyRun, useStopRun, useLibraries } from '@/api';
import { useToast, useConfirm } from '@/composables';
import { Card, Button, Badge, Checkbox, Spinner } from '@/components/common';

const run = useRunStore();
const config = useConfigStore();
const toast = useToast();
const { confirmDanger } = useConfirm();

// Fetch current status
const { data: runStatus, isLoading: statusLoading } = useRunStatus();

// Fetch available libraries
const { data: libraries } = useLibraries();

// Mutations
const startRunMutation = useStartRun();
const startApplyMutation = useStartApplyRun();
const stopRunMutation = useStopRun();

// Update store from status
watch(
  runStatus,
  (status) => {
    if (status) {
      run.setRunning(status.is_running);
      run.setCurrentRun(status.current_run);
      run.setProgress(status.progress);
    }
  },
  { immediate: true }
);

// Library selection
const selectedLibraries = ref<string[]>([]);
const allLibrariesSelected = computed(() =>
  libraries.value && selectedLibraries.value.length === libraries.value.length
);

const toggleAllLibraries = () => {
  if (allLibrariesSelected.value) {
    selectedLibraries.value = [];
  } else {
    selectedLibraries.value = libraries.value?.map((l) => l.name) || [];
  }
};

// Run options
const runPlaylists = ref(true);
const runOverlays = ref(true);
const runOperations = ref(true);

// Start dry run
const handleDryRun = async () => {
  try {
    await startRunMutation.mutateAsync({
      dryRun: true,
      libraries: selectedLibraries.value.length > 0 ? selectedLibraries.value : undefined,
      playlists: runPlaylists.value,
      overlays: runOverlays.value,
      operations: runOperations.value ? ['all'] : [],
    });
    toast.success('Dry run started');
  } catch (err) {
    toast.error('Failed to start dry run');
  }
};

// Start apply run
const handleApplyRun = async () => {
  if (!run.applyEnabled) {
    toast.error('Apply mode is not enabled');
    return;
  }

  const confirmed = await confirmDanger(
    'Apply Changes?',
    'This will apply all changes to your Plex library. This action cannot be undone. Are you sure you want to proceed?',
    'Apply Changes'
  );

  if (!confirmed) return;

  try {
    await startApplyMutation.mutateAsync({
      libraries: selectedLibraries.value.length > 0 ? selectedLibraries.value : undefined,
      playlists: runPlaylists.value,
      overlays: runOverlays.value,
      operations: runOperations.value ? ['all'] : [],
    });
    toast.success('Apply run started');
  } catch (err) {
    toast.error('Failed to start apply run');
  }
};

// Stop run
const handleStop = async () => {
  try {
    await stopRunMutation.mutateAsync();
    toast.info('Run stopped');
  } catch (err) {
    toast.error('Failed to stop run');
  }
};

// Format duration
const formatDuration = (seconds: number) => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}m ${secs}s`;
};

// Get status color
const getStatusColor = (status: string) => {
  switch (status) {
    case 'success':
      return 'success';
    case 'failed':
      return 'error';
    case 'running':
    case 'pending':
      return 'warning';
    default:
      return 'default';
  }
};
</script>

<template>
  <div class="h-full flex flex-col gap-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-semibold text-content-primary">
          Run Kometa
        </h2>
        <p class="text-sm text-content-secondary mt-0.5">
          Execute Kometa to update your Plex library
        </p>
      </div>

      <!-- Apply mode toggle -->
      <div class="flex items-center gap-4">
        <Checkbox
          v-model="run.applyEnabled"
          label="Enable Apply Mode"
          description="Allow changes to be applied to Plex"
        />
      </div>
    </div>

    <div class="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-4 min-h-0">
      <!-- Run Controls -->
      <Card title="Run Options">
        <!-- Library Selection -->
        <div class="mb-4">
          <div class="flex items-center justify-between mb-2">
            <label class="label mb-0">Libraries</label>
            <button
              type="button"
              class="text-sm text-kometa-gold hover:text-kometa-gold-light"
              @click="toggleAllLibraries"
            >
              {{ allLibrariesSelected ? 'Deselect All' : 'Select All' }}
            </button>
          </div>

          <div
            v-if="libraries && libraries.length > 0"
            class="grid grid-cols-2 gap-2"
          >
            <Checkbox
              v-for="library in libraries"
              :key="library.name"
              :model-value="selectedLibraries.includes(library.name)"
              :label="library.name"
              :description="library.type"
              @update:model-value="
                (v) =>
                  v
                    ? selectedLibraries.push(library.name)
                    : selectedLibraries.splice(selectedLibraries.indexOf(library.name), 1)
              "
            />
          </div>
          <p
            v-else
            class="text-sm text-content-muted"
          >
            No libraries configured
          </p>
        </div>

        <!-- Run Options -->
        <div class="mb-6 space-y-2">
          <Checkbox
            v-model="runPlaylists"
            label="Run Playlists"
          />
          <Checkbox
            v-model="runOverlays"
            label="Run Overlays"
          />
          <Checkbox
            v-model="runOperations"
            label="Run Operations"
          />
        </div>

        <!-- Run Buttons -->
        <div class="flex gap-2">
          <Button
            v-if="!run.isRunning"
            variant="primary"
            :loading="startRunMutation.isPending.value"
            @click="handleDryRun"
          >
            Start Dry Run
          </Button>

          <Button
            v-if="!run.isRunning && run.applyEnabled"
            variant="danger"
            :loading="startApplyMutation.isPending.value"
            @click="handleApplyRun"
          >
            Apply Changes
          </Button>

          <Button
            v-if="run.isRunning"
            variant="danger"
            :loading="stopRunMutation.isPending.value"
            @click="handleStop"
          >
            Stop Run
          </Button>
        </div>
      </Card>

      <!-- Current Status -->
      <Card title="Run Status">
        <div v-if="statusLoading">
          <Spinner />
        </div>

        <div v-else-if="run.currentRun">
          <div class="space-y-4">
            <!-- Status badge -->
            <div class="flex items-center gap-2">
              <Badge :variant="getStatusColor(run.currentRun.status)">
                {{ run.currentRun.status.toUpperCase() }}
              </Badge>
              <Badge v-if="run.currentRun.dry_run">
                Dry Run
              </Badge>
            </div>

            <!-- Progress bar -->
            <div
              v-if="run.isRunning"
              class="space-y-1"
            >
              <div class="flex justify-between text-sm">
                <span class="text-content-secondary">Progress</span>
                <span class="text-content">{{ run.progress }}%</span>
              </div>
              <div class="h-2 bg-surface-tertiary rounded-full overflow-hidden">
                <div
                  class="h-full bg-kometa-gold transition-all duration-300"
                  :style="{ width: `${run.progress}%` }"
                />
              </div>
            </div>

            <!-- Details -->
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span class="text-content-muted">Started</span>
                <div class="text-content">
                  {{ new Date(run.currentRun.start_time).toLocaleTimeString() }}
                </div>
              </div>

              <div v-if="run.currentRun.duration_seconds">
                <span class="text-content-muted">Duration</span>
                <div class="text-content">
                  {{ formatDuration(run.currentRun.duration_seconds) }}
                </div>
              </div>

              <div v-if="run.currentRun.libraries?.length">
                <span class="text-content-muted">Libraries</span>
                <div class="text-content">
                  {{ run.currentRun.libraries.join(', ') }}
                </div>
              </div>
            </div>

            <!-- Error message -->
            <div
              v-if="run.currentRun.error_message"
              class="p-3 rounded-lg bg-error-bg text-error text-sm"
            >
              {{ run.currentRun.error_message }}
            </div>
          </div>
        </div>

        <div
          v-else
          class="text-center py-8 text-content-muted"
        >
          <svg
            class="w-12 h-12 mx-auto mb-2 opacity-50"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
            />
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p>No run in progress</p>
          <p class="text-sm mt-1">
            Start a dry run to preview changes
          </p>
        </div>
      </Card>
    </div>
  </div>
</template>
