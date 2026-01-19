import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Run, RunOptions, RunStatus } from '@/types';

export const useRunStore = defineStore('run', () => {
  // ===========================================
  // State
  // ===========================================

  // Current run state
  const isRunning = ref(false);
  const currentRun = ref<Run | null>(null);
  const progress = ref(0);

  // Run options
  const runOptions = ref<RunOptions>({
    dryRun: true,
    libraries: [],
    collections: [],
    operations: [],
    playlists: true,
    overlays: true,
    metadata: true,
  });

  // Apply mode enabled (dangerous mode)
  const applyEnabled = ref(false);

  // Run history (cached)
  const recentRuns = ref<Run[]>([]);

  // ===========================================
  // Getters
  // ===========================================

  const canStartRun = computed(() => !isRunning.value);

  const canApply = computed(() => applyEnabled.value && !runOptions.value.dryRun);

  const isDryRun = computed(() => runOptions.value.dryRun);

  const currentStatus = computed((): RunStatus | null => {
    if (!currentRun.value) return null;
    return currentRun.value.status;
  });

  const selectedLibraries = computed(() => runOptions.value.libraries || []);

  const selectedCollections = computed(() => runOptions.value.collections || []);

  // ===========================================
  // Actions
  // ===========================================

  function setRunning(running: boolean) {
    isRunning.value = running;
  }

  function setCurrentRun(run: Run | null) {
    currentRun.value = run;
    if (run) {
      isRunning.value = run.status === 'running' || run.status === 'pending';
    }
  }

  function updateCurrentRunStatus(status: RunStatus) {
    if (currentRun.value) {
      currentRun.value.status = status;
      isRunning.value = status === 'running' || status === 'pending';
    }
  }

  function setProgress(value: number) {
    progress.value = Math.max(0, Math.min(100, value));
  }

  function setDryRun(dryRun: boolean) {
    runOptions.value.dryRun = dryRun;
  }

  function setApplyEnabled(enabled: boolean) {
    applyEnabled.value = enabled;
  }

  function setSelectedLibraries(libraries: string[]) {
    runOptions.value.libraries = libraries;
  }

  function setSelectedCollections(collections: string[]) {
    runOptions.value.collections = collections;
  }

  function setSelectedOperations(operations: string[]) {
    runOptions.value.operations = operations;
  }

  function toggleLibrary(library: string) {
    const libs = runOptions.value.libraries || [];
    const index = libs.indexOf(library);
    if (index === -1) {
      libs.push(library);
    } else {
      libs.splice(index, 1);
    }
    runOptions.value.libraries = libs;
  }

  function toggleCollection(collection: string) {
    const cols = runOptions.value.collections || [];
    const index = cols.indexOf(collection);
    if (index === -1) {
      cols.push(collection);
    } else {
      cols.splice(index, 1);
    }
    runOptions.value.collections = cols;
  }

  function setRecentRuns(runs: Run[]) {
    recentRuns.value = runs;
  }

  function addRecentRun(run: Run) {
    // Add to beginning and keep last 50
    recentRuns.value.unshift(run);
    if (recentRuns.value.length > 50) {
      recentRuns.value.pop();
    }
  }

  function updateRecentRun(runId: string, updates: Partial<Run>) {
    const index = recentRuns.value.findIndex((r) => r.id === runId);
    if (index !== -1) {
      recentRuns.value[index] = { ...recentRuns.value[index], ...updates };
    }
  }

  function resetOptions() {
    runOptions.value = {
      dryRun: true,
      libraries: [],
      collections: [],
      operations: [],
      playlists: true,
      overlays: true,
      metadata: true,
    };
  }

  function reset() {
    isRunning.value = false;
    currentRun.value = null;
    progress.value = 0;
    resetOptions();
    recentRuns.value = [];
  }

  return {
    // State
    isRunning,
    currentRun,
    progress,
    runOptions,
    applyEnabled,
    recentRuns,

    // Getters
    canStartRun,
    canApply,
    isDryRun,
    currentStatus,
    selectedLibraries,
    selectedCollections,

    // Actions
    setRunning,
    setCurrentRun,
    updateCurrentRunStatus,
    setProgress,
    setDryRun,
    setApplyEnabled,
    setSelectedLibraries,
    setSelectedCollections,
    setSelectedOperations,
    toggleLibrary,
    toggleCollection,
    setRecentRuns,
    addRecentRun,
    updateRecentRun,
    resetOptions,
    reset,
  };
});
