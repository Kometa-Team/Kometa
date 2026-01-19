<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useMediaSearch, useLibraries } from '@/api';
import { Card, Input, Select, Spinner, Badge } from '@/components/common';
import type { MediaSearchParams } from '@/types';

// Search state
const searchQuery = ref('');
const searchLibrary = ref('');
const searchType = ref<'movie' | 'show' | ''>('');

// Libraries for filter
const { data: libraries } = useLibraries();

// Computed search params
const searchParams = computed<MediaSearchParams>(() => ({
  query: searchQuery.value,
  library: searchLibrary.value || undefined,
  type: searchType.value || undefined,
  limit: 24,
}));

// Search query (debounced)
const debouncedQuery = ref('');
let debounceTimeout: ReturnType<typeof setTimeout>;

watch(searchQuery, (query) => {
  clearTimeout(debounceTimeout);
  debounceTimeout = setTimeout(() => {
    debouncedQuery.value = query;
  }, 300);
});

// Media search
const { data: searchResults, isLoading } = useMediaSearch({
  ...searchParams.value,
  query: debouncedQuery.value,
});

// Library options
const libraryOptions = computed(() => [
  { value: '', label: 'All Libraries' },
  ...(libraries.value?.map((l) => ({ value: l.name, label: l.name })) || []),
]);

// Type options
const typeOptions = [
  { value: '', label: 'All Types' },
  { value: 'movie', label: 'Movies' },
  { value: 'show', label: 'TV Shows' },
];

// Placeholder image
const placeholderImage =
  'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 450"><rect fill="%232a2a4e" width="300" height="450"/><text x="150" y="225" text-anchor="middle" fill="%23666" font-size="24">No Poster</text></svg>';
</script>

<template>
  <div class="h-full flex flex-col gap-4">
    <!-- Header -->
    <div>
      <h2 class="text-xl font-semibold text-content-primary">
        Media Search
      </h2>
      <p class="text-sm text-content-secondary mt-0.5">
        Search and browse your Plex media library
      </p>
    </div>

    <!-- Search & Filters -->
    <div class="flex items-center gap-4">
      <div class="flex-1">
        <Input
          v-model="searchQuery"
          type="search"
          placeholder="Search movies and shows..."
        />
      </div>
      <div class="w-48">
        <Select
          v-model="searchLibrary"
          :options="libraryOptions"
        />
      </div>
      <div class="w-40">
        <Select
          v-model="searchType"
          :options="typeOptions"
        />
      </div>
    </div>

    <!-- Results -->
    <div class="flex-1 overflow-auto">
      <!-- Loading -->
      <div
        v-if="isLoading"
        class="flex items-center justify-center py-12"
      >
        <Spinner size="lg" />
      </div>

      <!-- No query -->
      <div
        v-else-if="!debouncedQuery"
        class="flex flex-col items-center justify-center py-12 text-content-muted"
      >
        <svg
          class="w-16 h-16 mb-4 opacity-50"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
        <p>Enter a search term to find media</p>
      </div>

      <!-- No results -->
      <div
        v-else-if="!searchResults?.items?.length"
        class="flex flex-col items-center justify-center py-12 text-content-muted"
      >
        <svg
          class="w-16 h-16 mb-4 opacity-50"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <p>No results found for "{{ debouncedQuery }}"</p>
      </div>

      <!-- Results grid -->
      <div
        v-else
        class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4"
      >
        <Card
          v-for="item in searchResults.items"
          :key="item.id"
          class="overflow-hidden cursor-pointer hover:ring-2 hover:ring-kometa-gold transition-all"
          padding="none"
          hoverable
        >
          <!-- Poster -->
          <div class="aspect-[2/3] bg-surface-tertiary">
            <img
              :src="item.poster_url || placeholderImage"
              :alt="item.title"
              class="w-full h-full object-cover"
              loading="lazy"
            >
          </div>

          <!-- Info -->
          <div class="p-2">
            <h3 class="font-medium text-sm truncate">
              {{ item.title }}
            </h3>
            <div class="flex items-center gap-2 mt-1">
              <span
                v-if="item.year"
                class="text-xs text-content-muted"
              >
                {{ item.year }}
              </span>
              <Badge
                size="sm"
                :variant="item.type === 'movie' ? 'info' : 'success'"
              >
                {{ item.type }}
              </Badge>
            </div>
            <div
              v-if="item.rating"
              class="flex items-center gap-1 mt-1"
            >
              <svg
                class="w-3 h-3 text-kometa-gold"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
                />
              </svg>
              <span class="text-xs text-content-secondary">
                {{ item.rating.toFixed(1) }}
              </span>
            </div>
          </div>
        </Card>
      </div>

      <!-- Results count -->
      <div
        v-if="searchResults?.total"
        class="text-center text-sm text-content-muted mt-4"
      >
        Showing {{ searchResults.items.length }} of {{ searchResults.total }} results
      </div>
    </div>
  </div>
</template>
