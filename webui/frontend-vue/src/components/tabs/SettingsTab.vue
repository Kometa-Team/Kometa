<script setup lang="ts">
import { ref } from 'vue';
import { useSettings, useTestConnection, useTestAllConnections } from '@/api';
import { useRunStore } from '@/stores';
import { useToast } from '@/composables';
import { Card, Button, Badge, Spinner, Checkbox, Input } from '@/components/common';
import type { ConnectionTest } from '@/types';

const run = useRunStore();
const toast = useToast();

// Settings
const { data: settings, isLoading: settingsLoading } = useSettings();

// Connection testing
const testConnectionMutation = useTestConnection();
const testAllMutation = useTestAllConnections();
const connectionResults = ref<ConnectionTest[]>([]);
const testingAll = ref(false);

// Services to test
const services = [
  { id: 'plex', name: 'Plex', icon: 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z' },
  { id: 'tmdb', name: 'TMDb', icon: 'M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5' },
  { id: 'radarr', name: 'Radarr', icon: 'M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4' },
  { id: 'sonarr', name: 'Sonarr', icon: 'M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4' },
  { id: 'tautulli', name: 'Tautulli', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
  { id: 'trakt', name: 'Trakt', icon: 'M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z' },
];

// Test a single connection
const testConnection = async (service: string) => {
  try {
    const result = await testConnectionMutation.mutateAsync(
      service as 'plex' | 'tmdb' | 'radarr' | 'sonarr' | 'tautulli' | 'trakt'
    );
    // Update or add result
    const index = connectionResults.value.findIndex((r) => r.service === service);
    if (index >= 0) {
      connectionResults.value[index] = result;
    } else {
      connectionResults.value.push(result);
    }

    if (result.success) {
      toast.success(`${service} connection successful`);
    } else {
      toast.error(`${service} connection failed: ${result.message}`);
    }
  } catch (err) {
    toast.error(`Failed to test ${service} connection`);
  }
};

// Test all connections
const testAllConnections = async () => {
  testingAll.value = true;
  try {
    const results = await testAllMutation.mutateAsync();
    connectionResults.value = results;
    const successful = results.filter((r) => r.success).length;
    toast.info(`${successful}/${results.length} connections successful`);
  } catch (err) {
    toast.error('Failed to test connections');
  } finally {
    testingAll.value = false;
  }
};

// Get connection result for a service
const getConnectionResult = (serviceId: string) => {
  return connectionResults.value.find((r) => r.service === serviceId);
};
</script>

<template>
  <div class="h-full flex flex-col gap-4 overflow-auto">
    <!-- Header -->
    <div>
      <h2 class="text-xl font-semibold text-content-primary">
        Settings
      </h2>
      <p class="text-sm text-content-secondary mt-0.5">
        Configure Web UI settings and test connections
      </p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <!-- Safety Settings -->
      <Card title="Safety Settings">
        <div class="space-y-4">
          <Checkbox
            v-model="run.applyEnabled"
            label="Enable Apply Mode"
            description="When enabled, changes can be applied to your Plex library. Use with caution."
          />

          <div class="p-3 rounded-lg bg-warning-bg">
            <div class="flex gap-2">
              <svg
                class="w-5 h-5 text-warning flex-shrink-0"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
              <div class="text-sm">
                <p class="font-medium text-warning">
                  Apply Mode Warning
                </p>
                <p class="text-content-secondary mt-1">
                  When Apply Mode is enabled, Kometa will make actual changes to your
                  Plex library including adding/removing collections, updating metadata,
                  and applying overlays. Always test with Dry Run first.
                </p>
              </div>
            </div>
          </div>
        </div>
      </Card>

      <!-- Version Info -->
      <Card title="About">
        <div
          v-if="settingsLoading"
          class="flex items-center gap-2"
        >
          <Spinner size="sm" />
          <span class="text-content-muted">Loading...</span>
        </div>

        <div
          v-else
          class="space-y-3"
        >
          <div class="flex justify-between">
            <span class="text-content-secondary">Version</span>
            <span class="font-mono">{{ settings?.version || 'Unknown' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-content-secondary">Apply Enabled</span>
            <Badge :variant="settings?.apply_enabled ? 'warning' : 'success'">
              {{ settings?.apply_enabled ? 'Yes' : 'No' }}
            </Badge>
          </div>
          <div class="flex justify-between">
            <span class="text-content-secondary">Password Required</span>
            <Badge :variant="settings?.password_required ? 'info' : 'default'">
              {{ settings?.password_required ? 'Yes' : 'No' }}
            </Badge>
          </div>
        </div>
      </Card>

      <!-- Connection Testing -->
      <Card
        title="Connection Testing"
        class="lg:col-span-2"
      >
        <template #headerActions>
          <Button
            variant="secondary"
            size="sm"
            :loading="testingAll"
            @click="testAllConnections"
          >
            Test All
          </Button>
        </template>

        <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div
            v-for="service in services"
            :key="service.id"
            class="p-4 rounded-lg border border-border"
          >
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-2">
                <svg
                  class="w-5 h-5 text-content-secondary"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    :d="service.icon"
                  />
                </svg>
                <span class="font-medium">{{ service.name }}</span>
              </div>

              <Badge
                v-if="getConnectionResult(service.id)"
                :variant="getConnectionResult(service.id)?.success ? 'success' : 'error'"
              >
                {{ getConnectionResult(service.id)?.success ? 'OK' : 'Failed' }}
              </Badge>
            </div>

            <p
              v-if="getConnectionResult(service.id)?.message"
              class="text-xs text-content-muted mb-3 truncate"
              :title="getConnectionResult(service.id)?.message"
            >
              {{ getConnectionResult(service.id)?.message }}
            </p>

            <Button
              variant="secondary"
              size="sm"
              full-width
              :loading="testConnectionMutation.isPending.value"
              @click="testConnection(service.id)"
            >
              Test
            </Button>
          </div>
        </div>
      </Card>

      <!-- Password -->
      <Card title="Security">
        <div class="space-y-4">
          <Input
            type="password"
            label="UI Password"
            placeholder="Enter password..."
            hint="Set a password to protect the Web UI"
          />
          <Button variant="secondary">
            Update Password
          </Button>
        </div>
      </Card>

      <!-- Documentation -->
      <Card title="Documentation">
        <div class="space-y-2">
          <a
            href="https://kometa.wiki/"
            target="_blank"
            rel="noopener noreferrer"
            class="flex items-center gap-2 p-2 rounded-md hover:bg-surface-tertiary transition-colors"
          >
            <svg
              class="w-5 h-5 text-content-secondary"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
              />
            </svg>
            <span>Kometa Wiki</span>
            <svg
              class="w-4 h-4 ml-auto text-content-muted"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
              />
            </svg>
          </a>
          <a
            href="https://github.com/Kometa-Team/Kometa"
            target="_blank"
            rel="noopener noreferrer"
            class="flex items-center gap-2 p-2 rounded-md hover:bg-surface-tertiary transition-colors"
          >
            <svg
              class="w-5 h-5 text-content-secondary"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                fill-rule="evenodd"
                clip-rule="evenodd"
                d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.17 6.839 9.49.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.604-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.464-1.11-1.464-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0112 6.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.167 22 16.418 22 12c0-5.523-4.477-10-10-10z"
              />
            </svg>
            <span>GitHub Repository</span>
            <svg
              class="w-4 h-4 ml-auto text-content-muted"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
              />
            </svg>
          </a>
          <a
            href="https://discord.gg/kometa"
            target="_blank"
            rel="noopener noreferrer"
            class="flex items-center gap-2 p-2 rounded-md hover:bg-surface-tertiary transition-colors"
          >
            <svg
              class="w-5 h-5 text-content-secondary"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"
              />
            </svg>
            <span>Discord Community</span>
            <svg
              class="w-4 h-4 ml-auto text-content-muted"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
              />
            </svg>
          </a>
        </div>
      </Card>
    </div>
  </div>
</template>
