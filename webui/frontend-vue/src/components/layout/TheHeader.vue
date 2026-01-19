<script setup lang="ts">
import { useTheme } from '@/composables';
import { Badge, Spinner } from '@/components/common';

interface Props {
  isRunning?: boolean;
}

defineProps<Props>();

const { theme, toggleTheme, isDark } = useTheme();
</script>

<template>
  <header class="bg-surface-primary border-b border-border px-4 py-3 flex items-center justify-between">
    <!-- Left side: Logo and title -->
    <div class="flex items-center gap-3">
      <div class="flex items-center gap-2">
        <div class="w-8 h-8 bg-kometa-gold rounded-lg flex items-center justify-center">
          <span class="text-lg font-bold text-content-inverse">K</span>
        </div>
        <h1 class="text-lg font-semibold text-content-primary">
          Kometa
        </h1>
      </div>

      <!-- Running indicator -->
      <Badge
        v-if="isRunning"
        variant="warning"
        dot
      >
        <Spinner
          size="sm"
          color="current"
          class="mr-1"
        />
        Running
      </Badge>
    </div>

    <!-- Right side: Actions -->
    <div class="flex items-center gap-2">
      <!-- Theme toggle -->
      <button
        type="button"
        class="p-2 rounded-md text-content-secondary hover:text-content hover:bg-surface-tertiary transition-colors"
        :title="`Switch to ${isDark ? 'light' : 'dark'} mode`"
        @click="toggleTheme"
      >
        <!-- Sun icon (light mode) -->
        <svg
          v-if="isDark"
          class="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
          />
        </svg>
        <!-- Moon icon (dark mode) -->
        <svg
          v-else
          class="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
          />
        </svg>
      </button>

      <!-- GitHub link -->
      <a
        href="https://github.com/Kometa-Team/Kometa"
        target="_blank"
        rel="noopener noreferrer"
        class="p-2 rounded-md text-content-secondary hover:text-content hover:bg-surface-tertiary transition-colors"
        title="View on GitHub"
      >
        <svg
          class="w-5 h-5"
          fill="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            fill-rule="evenodd"
            clip-rule="evenodd"
            d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.17 6.839 9.49.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.604-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.464-1.11-1.464-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0112 6.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.167 22 16.418 22 12c0-5.523-4.477-10-10-10z"
          />
        </svg>
      </a>
    </div>
  </header>
</template>
