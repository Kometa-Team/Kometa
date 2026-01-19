<script setup lang="ts">
import { ref } from 'vue';
import { useOverlayList, useGenerateOverlayPreview, useMediaSearch } from '@/api';
import { useToast } from '@/composables';
import { Card, Button, Input, Select, Spinner } from '@/components/common';

const toast = useToast();

// Fetch overlay list
const { data: overlays, isLoading: overlaysLoading } = useOverlayList();

// Preview state
const selectedOverlay = ref('');
const searchQuery = ref('');
const selectedMedia = ref('');
const previewUrl = ref('');
const isGenerating = ref(false);

// Media search for preview
const { data: mediaResults, isLoading: mediaLoading } = useMediaSearch({
  query: searchQuery.value,
  limit: 10,
});

// Generate preview mutation
const generatePreview = useGenerateOverlayPreview();

// Handle generate preview
const handleGeneratePreview = async () => {
  if (!selectedOverlay.value || !selectedMedia.value) {
    toast.warning('Please select an overlay and a media item');
    return;
  }

  isGenerating.value = true;

  try {
    const result = await generatePreview.mutateAsync({
      overlay_name: selectedOverlay.value,
      media_id: selectedMedia.value,
    });
    previewUrl.value = result.preview_url;
    toast.success('Preview generated');
  } catch (err) {
    toast.error('Failed to generate preview');
  } finally {
    isGenerating.value = false;
  }
};
</script>

<template>
  <div class="h-full flex flex-col gap-4">
    <!-- Header -->
    <div>
      <h2 class="text-xl font-semibold text-content-primary">
        Overlay Preview
      </h2>
      <p class="text-sm text-content-secondary mt-0.5">
        Preview how overlays will appear on your media posters
      </p>
    </div>

    <div class="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-4 min-h-0">
      <!-- Controls -->
      <Card title="Preview Settings">
        <div class="space-y-4">
          <!-- Overlay selection -->
          <div>
            <label class="label">Overlay</label>
            <Select
              v-if="!overlaysLoading && overlays"
              v-model="selectedOverlay"
              :options="
                overlays.overlays.map((o) => ({ value: o, label: o }))
              "
              placeholder="Select an overlay..."
            />
            <div
              v-else
              class="flex items-center gap-2"
            >
              <Spinner size="sm" />
              <span class="text-sm text-content-muted">Loading overlays...</span>
            </div>
          </div>

          <!-- Media search -->
          <div>
            <label class="label">Media Item</label>
            <Input
              v-model="searchQuery"
              type="search"
              placeholder="Search for a movie or show..."
            />

            <div
              v-if="mediaLoading"
              class="mt-2"
            >
              <Spinner size="sm" />
            </div>

            <div
              v-else-if="mediaResults?.items?.length"
              class="mt-2 space-y-1 max-h-48 overflow-auto"
            >
              <button
                v-for="item in mediaResults.items"
                :key="item.id"
                type="button"
                :class="[
                  'w-full flex items-center gap-3 p-2 rounded-md text-left transition-colors',
                  selectedMedia === item.id
                    ? 'bg-kometa-gold/10 text-kometa-gold'
                    : 'hover:bg-surface-tertiary',
                ]"
                @click="selectedMedia = item.id"
              >
                <img
                  v-if="item.poster_url"
                  :src="item.poster_url"
                  :alt="item.title"
                  class="w-8 h-12 object-cover rounded"
                >
                <div
                  v-else
                  class="w-8 h-12 bg-surface-tertiary rounded"
                />
                <div class="flex-1 min-w-0">
                  <div class="font-medium text-sm truncate">
                    {{ item.title }}
                  </div>
                  <div class="text-xs text-content-muted">
                    {{ item.year }} - {{ item.type }}
                  </div>
                </div>
              </button>
            </div>
          </div>

          <!-- Generate button -->
          <Button
            :loading="isGenerating"
            :disabled="!selectedOverlay || !selectedMedia"
            @click="handleGeneratePreview"
          >
            Generate Preview
          </Button>
        </div>
      </Card>

      <!-- Preview -->
      <Card
        title="Preview"
        class="flex flex-col"
      >
        <div class="flex-1 flex items-center justify-center bg-surface-tertiary rounded-lg min-h-[300px]">
          <img
            v-if="previewUrl"
            :src="previewUrl"
            alt="Overlay preview"
            class="max-w-full max-h-full object-contain rounded"
          >
          <div
            v-else
            class="text-center text-content-muted"
          >
            <svg
              class="w-16 h-16 mx-auto mb-2 opacity-50"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            <p>Select an overlay and media item</p>
            <p class="text-sm">to generate a preview</p>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>
