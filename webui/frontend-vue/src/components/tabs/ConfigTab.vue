<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useConfigStore } from '@/stores';
import { useConfig, useSaveConfig, useValidateConfig, useCreateBackup, useConfigBackups } from '@/api';
import { useToast, useConfirm } from '@/composables';
import { Card, Button, Badge, Spinner, Modal } from '@/components/common';

const config = useConfigStore();
const toast = useToast();
const { confirmWarning } = useConfirm();

// Fetch config
const { data: configData, isLoading, error, refetch } = useConfig();

// Mutations
const saveConfigMutation = useSaveConfig();
const validateMutation = useValidateConfig();
const createBackupMutation = useCreateBackup();

// Backups
const { data: backups, refetch: refetchBackups } = useConfigBackups();
const showBackupsModal = ref(false);

// Editor state
const editorContent = ref('');
const hasLocalChanges = computed(() => editorContent.value !== configData.value?.content);

// Watch for config data changes
watch(
  () => configData.value?.content,
  (newContent) => {
    if (newContent && !hasLocalChanges.value) {
      editorContent.value = newContent;
      config.setRawConfig(newContent, false);
    }
  },
  { immediate: true }
);

// Validate on change (debounced)
let validateTimeout: ReturnType<typeof setTimeout>;
watch(editorContent, (content) => {
  config.setRawConfig(content);
  clearTimeout(validateTimeout);
  validateTimeout = setTimeout(async () => {
    try {
      const result = await validateMutation.mutateAsync(content);
      config.setValidation(result);
    } catch (err) {
      // Validation error handling
    }
  }, 500);
});

// Save config
const handleSave = async () => {
  if (!config.isValid) {
    toast.error('Cannot save: Configuration has validation errors');
    return;
  }

  try {
    await saveConfigMutation.mutateAsync(editorContent.value);
    config.markSaved();
    toast.success('Configuration saved successfully');
  } catch (err) {
    toast.error('Failed to save configuration');
  }
};

// Create backup
const handleBackup = async () => {
  try {
    const result = await createBackupMutation.mutateAsync();
    refetchBackups();
    toast.success(`Backup created: ${result.filename}`);
  } catch (err) {
    toast.error('Failed to create backup');
  }
};

// Discard changes
const handleDiscard = async () => {
  if (!hasLocalChanges.value) return;

  const confirmed = await confirmWarning(
    'Discard Changes?',
    'Are you sure you want to discard all unsaved changes? This cannot be undone.'
  );

  if (confirmed) {
    editorContent.value = configData.value?.content || '';
    config.setRawConfig(editorContent.value, false);
    toast.info('Changes discarded');
  }
};

// Format timestamp
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString();
};

// Format file size
const formatSize = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};
</script>

<template>
  <div class="h-full flex flex-col gap-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-semibold text-content-primary">
          Configuration
        </h2>
        <p class="text-sm text-content-secondary mt-0.5">
          Edit your Kometa configuration file
        </p>
      </div>

      <div class="flex items-center gap-2">
        <!-- Validation status -->
        <Badge
          v-if="config.hasErrors"
          variant="error"
        >
          {{ config.validation.errors.length }} error(s)
        </Badge>
        <Badge
          v-else-if="config.hasWarnings"
          variant="warning"
        >
          {{ config.validation.warnings.length }} warning(s)
        </Badge>
        <Badge
          v-else-if="editorContent"
          variant="success"
        >
          Valid
        </Badge>

        <!-- Unsaved indicator -->
        <Badge
          v-if="hasLocalChanges"
          variant="warning"
          dot
        >
          Unsaved
        </Badge>

        <!-- Actions -->
        <Button
          variant="ghost"
          size="sm"
          :disabled="!hasLocalChanges"
          @click="handleDiscard"
        >
          Discard
        </Button>

        <Button
          variant="secondary"
          size="sm"
          @click="showBackupsModal = true"
        >
          Backups
        </Button>

        <Button
          variant="secondary"
          size="sm"
          :loading="createBackupMutation.isPending.value"
          @click="handleBackup"
        >
          Create Backup
        </Button>

        <Button
          size="sm"
          :loading="saveConfigMutation.isPending.value"
          :disabled="!hasLocalChanges || !config.isValid"
          @click="handleSave"
        >
          Save
        </Button>
      </div>
    </div>

    <!-- Loading state -->
    <div
      v-if="isLoading"
      class="flex-1 flex items-center justify-center"
    >
      <Spinner size="lg" />
    </div>

    <!-- Error state -->
    <Card
      v-else-if="error"
      class="flex-1"
    >
      <div class="text-center py-8">
        <div class="text-error mb-2">
          Failed to load configuration
        </div>
        <Button
          variant="secondary"
          size="sm"
          @click="refetch()"
        >
          Retry
        </Button>
      </div>
    </Card>

    <!-- Editor -->
    <div
      v-else
      class="flex-1 flex gap-4 min-h-0"
    >
      <!-- Editor panel -->
      <Card
        class="flex-1 flex flex-col min-h-0"
        padding="none"
      >
        <template #header>
          <div class="flex items-center justify-between w-full">
            <span class="font-medium">config.yml</span>
            <span class="text-sm text-content-muted">
              Line {{ config.editorCursorPosition.line }}, Col {{ config.editorCursorPosition.column }}
            </span>
          </div>
        </template>

        <div class="flex-1 min-h-0 overflow-hidden">
          <textarea
            v-model="editorContent"
            class="w-full h-full p-4 bg-surface-primary text-content font-mono text-sm
                   border-0 resize-none focus:ring-0 focus:outline-none"
            spellcheck="false"
            wrap="off"
            @keydown.tab.prevent="editorContent += '  '"
          />
        </div>
      </Card>

      <!-- Validation panel -->
      <Card
        class="w-80 flex flex-col min-h-0"
        padding="none"
      >
        <template #header>
          <span class="font-medium">Validation</span>
        </template>

        <div class="flex-1 overflow-auto p-2">
          <!-- Errors -->
          <div
            v-if="config.validation.errors.length > 0"
            class="mb-4"
          >
            <h4 class="text-sm font-medium text-error mb-2 px-2">
              Errors
            </h4>
            <ul class="space-y-1">
              <li
                v-for="(err, index) in config.validation.errors"
                :key="index"
                class="p-2 rounded bg-error-bg text-sm"
              >
                <div class="font-medium text-error">
                  {{ err.path }}
                </div>
                <div class="text-content-secondary">
                  {{ err.message }}
                </div>
                <div
                  v-if="err.line"
                  class="text-xs text-content-muted mt-1"
                >
                  Line {{ err.line }}
                </div>
              </li>
            </ul>
          </div>

          <!-- Warnings -->
          <div
            v-if="config.validation.warnings.length > 0"
            class="mb-4"
          >
            <h4 class="text-sm font-medium text-warning mb-2 px-2">
              Warnings
            </h4>
            <ul class="space-y-1">
              <li
                v-for="(warn, index) in config.validation.warnings"
                :key="index"
                class="p-2 rounded bg-warning-bg text-sm"
              >
                <div class="font-medium text-warning">
                  {{ warn.path }}
                </div>
                <div class="text-content-secondary">
                  {{ warn.message }}
                </div>
              </li>
            </ul>
          </div>

          <!-- Valid state -->
          <div
            v-if="config.isValid && config.validation.warnings.length === 0"
            class="p-4 text-center"
          >
            <div class="w-12 h-12 mx-auto mb-2 rounded-full bg-success-bg flex items-center justify-center">
              <svg
                class="w-6 h-6 text-success"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
            <p class="text-sm text-content-secondary">
              Configuration is valid
            </p>
          </div>
        </div>
      </Card>
    </div>

    <!-- Backups Modal -->
    <Modal
      v-model:open="showBackupsModal"
      title="Configuration Backups"
      size="md"
    >
      <div
        v-if="backups && backups.length > 0"
        class="space-y-2"
      >
        <div
          v-for="backup in backups"
          :key="backup.filename"
          class="flex items-center justify-between p-3 rounded-lg bg-surface-tertiary"
        >
          <div>
            <div class="font-medium text-sm">
              {{ backup.filename }}
            </div>
            <div class="text-xs text-content-muted">
              {{ formatDate(backup.created) }} - {{ formatSize(backup.size) }}
            </div>
          </div>
          <Button
            variant="secondary"
            size="sm"
          >
            Restore
          </Button>
        </div>
      </div>
      <div
        v-else
        class="text-center py-8 text-content-muted"
      >
        No backups available
      </div>
    </Modal>
  </div>
</template>
