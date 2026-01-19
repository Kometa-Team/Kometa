import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { LogEntry, LogLevel } from '@/types';

export const useLogsStore = defineStore('logs', () => {
  // ===========================================
  // State
  // ===========================================

  // Log entries
  const entries = ref<LogEntry[]>([]);

  // WebSocket connection state
  const connected = ref(false);
  const connecting = ref(false);

  // Display options
  const autoScroll = ref(true);
  const filterLevel = ref<LogLevel | 'ALL'>('ALL');
  const searchQuery = ref('');

  // Maximum entries to keep in memory
  const maxEntries = ref(5000);

  // ===========================================
  // Getters
  // ===========================================

  const filteredEntries = computed(() => {
    let filtered = entries.value;

    // Filter by level
    if (filterLevel.value !== 'ALL') {
      const levelOrder: LogLevel[] = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'];
      const minLevelIndex = levelOrder.indexOf(filterLevel.value);
      filtered = filtered.filter((entry) => {
        const entryLevelIndex = levelOrder.indexOf(entry.level);
        return entryLevelIndex >= minLevelIndex;
      });
    }

    // Filter by search query
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase();
      filtered = filtered.filter(
        (entry) =>
          entry.message.toLowerCase().includes(query) ||
          entry.module?.toLowerCase().includes(query)
      );
    }

    return filtered;
  });

  const entryCount = computed(() => entries.value.length);

  const filteredCount = computed(() => filteredEntries.value.length);

  const hasErrors = computed(() =>
    entries.value.some((e) => e.level === 'ERROR' || e.level === 'CRITICAL')
  );

  const hasWarnings = computed(() => entries.value.some((e) => e.level === 'WARNING'));

  const errorCount = computed(
    () =>
      entries.value.filter((e) => e.level === 'ERROR' || e.level === 'CRITICAL').length
  );

  const warningCount = computed(
    () => entries.value.filter((e) => e.level === 'WARNING').length
  );

  // ===========================================
  // Actions
  // ===========================================

  function addEntry(entry: LogEntry) {
    entries.value.push(entry);

    // Trim old entries if exceeding max
    if (entries.value.length > maxEntries.value) {
      entries.value.splice(0, entries.value.length - maxEntries.value);
    }
  }

  function addEntries(newEntries: LogEntry[]) {
    entries.value.push(...newEntries);

    // Trim old entries if exceeding max
    if (entries.value.length > maxEntries.value) {
      entries.value.splice(0, entries.value.length - maxEntries.value);
    }
  }

  function clearEntries() {
    entries.value = [];
  }

  function setConnected(isConnected: boolean) {
    connected.value = isConnected;
    if (isConnected) {
      connecting.value = false;
    }
  }

  function setConnecting(isConnecting: boolean) {
    connecting.value = isConnecting;
  }

  function setAutoScroll(enabled: boolean) {
    autoScroll.value = enabled;
  }

  function toggleAutoScroll() {
    autoScroll.value = !autoScroll.value;
  }

  function setFilterLevel(level: LogLevel | 'ALL') {
    filterLevel.value = level;
  }

  function setSearchQuery(query: string) {
    searchQuery.value = query;
  }

  function setMaxEntries(max: number) {
    maxEntries.value = max;
    // Trim if needed
    if (entries.value.length > max) {
      entries.value.splice(0, entries.value.length - max);
    }
  }

  function reset() {
    entries.value = [];
    connected.value = false;
    connecting.value = false;
    autoScroll.value = true;
    filterLevel.value = 'ALL';
    searchQuery.value = '';
  }

  return {
    // State
    entries,
    connected,
    connecting,
    autoScroll,
    filterLevel,
    searchQuery,
    maxEntries,

    // Getters
    filteredEntries,
    entryCount,
    filteredCount,
    hasErrors,
    hasWarnings,
    errorCount,
    warningCount,

    // Actions
    addEntry,
    addEntries,
    clearEntries,
    setConnected,
    setConnecting,
    setAutoScroll,
    toggleAutoScroll,
    setFilterLevel,
    setSearchQuery,
    setMaxEntries,
    reset,
  };
});
