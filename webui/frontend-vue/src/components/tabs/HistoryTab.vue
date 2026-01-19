<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRunHistory, useDeleteRun, useRunLogs } from '@/api';
import { useToast, useConfirm } from '@/composables';
import { Card, Button, Badge, Spinner, Modal, Select } from '@/components/common';
import type { Run, RunStatus, RunFilters } from '@/types';

const toast = useToast();
const { confirmDanger } = useConfirm();

// Filters
const filters = ref<RunFilters>({
  limit: 50,
});

// Fetch history
const { data: historyData, isLoading, refetch } = useRunHistory(filters.value);

// Delete mutation
const deleteMutation = useDeleteRun();

// Selected run for details
const selectedRun = ref<Run | null>(null);
const showDetailsModal = ref(false);

// Fetch logs for selected run
const { data: runLogs, isLoading: logsLoading } = useRunLogs(
  computed(() => selectedRun.value?.id || '')
);

// Status filter options
const statusOptions = [
  { value: '', label: 'All Statuses' },
  { value: 'success', label: 'Success' },
  { value: 'failed', label: 'Failed' },
  { value: 'running', label: 'Running' },
  { value: 'cancelled', label: 'Cancelled' },
];

// Type filter options
const typeOptions = [
  { value: '', label: 'All Types' },
  { value: 'true', label: 'Dry Run' },
  { value: 'false', label: 'Apply' },
];

// Status badge variant
const getStatusVariant = (status: RunStatus) => {
  switch (status) {
    case 'success':
      return 'success';
    case 'failed':
      return 'error';
    case 'running':
    case 'pending':
      return 'warning';
    case 'cancelled':
      return 'default';
    default:
      return 'default';
  }
};

// Format date
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString();
};

// Format duration
const formatDuration = (seconds?: number) => {
  if (!seconds) return '-';
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  if (mins > 0) {
    return `${mins}m ${secs}s`;
  }
  return `${secs}s`;
};

// View run details
const viewDetails = (run: Run) => {
  selectedRun.value = run;
  showDetailsModal.value = true;
};

// Delete run
const handleDelete = async (run: Run) => {
  const confirmed = await confirmDanger(
    'Delete Run?',
    `Are you sure you want to delete this run from ${formatDate(run.start_time)}? This will also delete associated logs.`
  );

  if (!confirmed) return;

  try {
    await deleteMutation.mutateAsync(run.id);
    toast.success('Run deleted');
    refetch();
  } catch (err) {
    toast.error('Failed to delete run');
  }
};
</script>

<template>
  <div class="h-full flex flex-col gap-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-semibold text-content-primary">
          Run History
        </h2>
        <p class="text-sm text-content-secondary mt-0.5">
          View past Kometa runs and their results
        </p>
      </div>

      <Button
        variant="secondary"
        size="sm"
        @click="refetch()"
      >
        Refresh
      </Button>
    </div>

    <!-- Filters -->
    <div class="flex items-center gap-4">
      <div class="w-40">
        <Select
          :model-value="filters.status || ''"
          :options="statusOptions"
          @update:model-value="filters.status = $event as RunStatus || undefined"
        />
      </div>
      <div class="w-40">
        <Select
          :model-value="filters.dryRun?.toString() || ''"
          :options="typeOptions"
          @update:model-value="filters.dryRun = $event === '' ? undefined : $event === 'true'"
        />
      </div>
    </div>

    <!-- Loading -->
    <div
      v-if="isLoading"
      class="flex-1 flex items-center justify-center"
    >
      <Spinner size="lg" />
    </div>

    <!-- History table -->
    <Card
      v-else
      class="flex-1 min-h-0 overflow-hidden"
      padding="none"
    >
      <div class="h-full overflow-auto">
        <table class="w-full">
          <thead class="bg-surface-tertiary sticky top-0">
            <tr>
              <th class="px-4 py-3 text-left text-sm font-medium text-content-secondary">
                Started
              </th>
              <th class="px-4 py-3 text-left text-sm font-medium text-content-secondary">
                Type
              </th>
              <th class="px-4 py-3 text-left text-sm font-medium text-content-secondary">
                Status
              </th>
              <th class="px-4 py-3 text-left text-sm font-medium text-content-secondary">
                Duration
              </th>
              <th class="px-4 py-3 text-left text-sm font-medium text-content-secondary">
                Libraries
              </th>
              <th class="px-4 py-3 text-right text-sm font-medium text-content-secondary">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border">
            <tr
              v-for="run in historyData?.runs"
              :key="run.id"
              class="hover:bg-surface-tertiary transition-colors"
            >
              <td class="px-4 py-3 text-sm">
                {{ formatDate(run.start_time) }}
              </td>
              <td class="px-4 py-3">
                <Badge :variant="run.dry_run ? 'info' : 'warning'">
                  {{ run.dry_run ? 'Dry Run' : 'Apply' }}
                </Badge>
              </td>
              <td class="px-4 py-3">
                <Badge :variant="getStatusVariant(run.status)">
                  {{ run.status }}
                </Badge>
              </td>
              <td class="px-4 py-3 text-sm text-content-secondary">
                {{ formatDuration(run.duration_seconds) }}
              </td>
              <td class="px-4 py-3 text-sm text-content-secondary">
                {{ run.libraries?.join(', ') || 'All' }}
              </td>
              <td class="px-4 py-3 text-right">
                <div class="flex justify-end gap-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="viewDetails(run)"
                  >
                    View
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="handleDelete(run)"
                  >
                    Delete
                  </Button>
                </div>
              </td>
            </tr>

            <tr v-if="!historyData?.runs?.length">
              <td
                colspan="6"
                class="px-4 py-8 text-center text-content-muted"
              >
                No runs found
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>

    <!-- Details Modal -->
    <Modal
      v-model:open="showDetailsModal"
      :title="`Run Details - ${selectedRun ? formatDate(selectedRun.start_time) : ''}`"
      size="lg"
    >
      <template v-if="selectedRun">
        <div class="space-y-4">
          <!-- Status and type -->
          <div class="flex gap-2">
            <Badge :variant="getStatusVariant(selectedRun.status)">
              {{ selectedRun.status }}
            </Badge>
            <Badge :variant="selectedRun.dry_run ? 'info' : 'warning'">
              {{ selectedRun.dry_run ? 'Dry Run' : 'Apply' }}
            </Badge>
          </div>

          <!-- Details grid -->
          <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span class="text-content-muted">Started</span>
              <div>{{ formatDate(selectedRun.start_time) }}</div>
            </div>
            <div>
              <span class="text-content-muted">Ended</span>
              <div>{{ selectedRun.end_time ? formatDate(selectedRun.end_time) : '-' }}</div>
            </div>
            <div>
              <span class="text-content-muted">Duration</span>
              <div>{{ formatDuration(selectedRun.duration_seconds) }}</div>
            </div>
            <div>
              <span class="text-content-muted">Exit Code</span>
              <div>{{ selectedRun.exit_code ?? '-' }}</div>
            </div>
            <div class="col-span-2">
              <span class="text-content-muted">Libraries</span>
              <div>{{ selectedRun.libraries?.join(', ') || 'All' }}</div>
            </div>
          </div>

          <!-- Error message -->
          <div
            v-if="selectedRun.error_message"
            class="p-3 rounded-lg bg-error-bg text-error text-sm"
          >
            {{ selectedRun.error_message }}
          </div>

          <!-- Logs -->
          <div>
            <h4 class="font-medium mb-2">
              Logs
            </h4>
            <div
              v-if="logsLoading"
              class="text-center py-4"
            >
              <Spinner />
            </div>
            <pre
              v-else-if="runLogs?.logs"
              class="p-3 rounded-lg bg-surface-tertiary text-sm font-mono max-h-64 overflow-auto"
            >{{ runLogs.logs }}</pre>
            <p
              v-else
              class="text-content-muted text-sm"
            >
              No logs available
            </p>
          </div>
        </div>
      </template>
    </Modal>
  </div>
</template>
