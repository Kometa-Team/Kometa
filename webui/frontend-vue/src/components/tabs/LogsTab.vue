<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue';
import { useLogsStore } from '@/stores';
import { useLogWebSocket } from '@/composables';
import { Card, Button, Badge, Input, Select, Checkbox } from '@/components/common';
import type { LogLevel } from '@/types';

const logs = useLogsStore();
const logContainer = ref<HTMLElement | null>(null);

// WebSocket connection for live logs
const { connected, data: wsData } = useLogWebSocket();

// Watch for new log entries from WebSocket
watch(wsData, (data) => {
  if (data && typeof data === 'object' && 'message' in data) {
    logs.addEntry(data as { timestamp: string; level: LogLevel; message: string });
  }
});

// Auto-scroll to bottom when new logs arrive
watch(
  () => logs.entries.length,
  async () => {
    if (logs.autoScroll && logContainer.value) {
      await nextTick();
      logContainer.value.scrollTop = logContainer.value.scrollHeight;
    }
  }
);

// Filter options
const levelOptions = [
  { value: 'ALL', label: 'All Levels' },
  { value: 'DEBUG', label: 'Debug' },
  { value: 'INFO', label: 'Info' },
  { value: 'WARNING', label: 'Warning' },
  { value: 'ERROR', label: 'Error' },
];

// Log level colors
const levelColors: Record<LogLevel, string> = {
  DEBUG: 'text-content-muted',
  INFO: 'text-info',
  WARNING: 'text-warning',
  ERROR: 'text-error',
  CRITICAL: 'text-error font-bold',
};

// Format timestamp
const formatTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleTimeString();
};

// Export logs
const exportLogs = () => {
  const content = logs.entries
    .map((e) => `[${e.timestamp}] [${e.level}] ${e.message}`)
    .join('\n');

  const blob = new Blob([content], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `kometa-logs-${new Date().toISOString().slice(0, 10)}.txt`;
  a.click();
  URL.revokeObjectURL(url);
};
</script>

<template>
  <div class="h-full flex flex-col gap-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <div>
          <h2 class="text-xl font-semibold text-content-primary">
            Logs
          </h2>
          <p class="text-sm text-content-secondary mt-0.5">
            Live log output from Kometa
          </p>
        </div>

        <Badge
          :variant="connected ? 'success' : 'error'"
          dot
        >
          {{ connected ? 'Connected' : 'Disconnected' }}
        </Badge>
      </div>

      <div class="flex items-center gap-2">
        <!-- Stats -->
        <Badge
          v-if="logs.errorCount > 0"
          variant="error"
        >
          {{ logs.errorCount }} errors
        </Badge>
        <Badge
          v-if="logs.warningCount > 0"
          variant="warning"
        >
          {{ logs.warningCount }} warnings
        </Badge>

        <Button
          variant="secondary"
          size="sm"
          @click="exportLogs"
        >
          Export
        </Button>

        <Button
          variant="secondary"
          size="sm"
          @click="logs.clearEntries"
        >
          Clear
        </Button>
      </div>
    </div>

    <!-- Filters -->
    <div class="flex items-center gap-4">
      <div class="w-48">
        <Select
          :model-value="logs.filterLevel"
          :options="levelOptions"
          placeholder="Filter by level"
          @update:model-value="logs.setFilterLevel($event as LogLevel | 'ALL')"
        />
      </div>

      <div class="flex-1">
        <Input
          :model-value="logs.searchQuery"
          type="search"
          placeholder="Search logs..."
          @update:model-value="logs.setSearchQuery($event as string)"
        />
      </div>

      <Checkbox
        :model-value="logs.autoScroll"
        label="Auto-scroll"
        @update:model-value="logs.setAutoScroll"
      />

      <span class="text-sm text-content-muted">
        {{ logs.filteredCount }} / {{ logs.entryCount }} entries
      </span>
    </div>

    <!-- Log viewer -->
    <Card
      class="flex-1 min-h-0"
      padding="none"
    >
      <div
        ref="logContainer"
        class="h-full overflow-auto font-mono text-sm bg-surface-base"
      >
        <div
          v-if="logs.filteredEntries.length === 0"
          class="p-8 text-center text-content-muted"
        >
          <template v-if="logs.entries.length === 0">
            No log entries yet. Start a run to see logs.
          </template>
          <template v-else>
            No entries match your filter criteria.
          </template>
        </div>

        <div
          v-for="(entry, index) in logs.filteredEntries"
          :key="index"
          class="log-entry flex"
        >
          <span class="log-timestamp w-24 flex-shrink-0">
            {{ formatTime(entry.timestamp) }}
          </span>
          <span
            :class="['w-16 flex-shrink-0', levelColors[entry.level]]"
          >
            [{{ entry.level }}]
          </span>
          <span class="text-content flex-1 break-all">
            {{ entry.message }}
          </span>
        </div>
      </div>
    </Card>
  </div>
</template>
