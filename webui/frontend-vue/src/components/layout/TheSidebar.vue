<script setup lang="ts">
import { computed } from 'vue';
import { useUIStore, useLogsStore } from '@/stores';
import type { TabId } from '@/types';

const ui = useUIStore();
const logs = useLogsStore();

interface NavItem {
  id: TabId;
  label: string;
  icon: string;
  badge?: number;
}

const navItems = computed<NavItem[]>(() => [
  {
    id: 'config',
    label: 'Configuration',
    icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z',
  },
  {
    id: 'run',
    label: 'Run',
    icon: 'M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
  },
  {
    id: 'logs',
    label: 'Logs',
    icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    badge: logs.errorCount > 0 ? logs.errorCount : undefined,
  },
  {
    id: 'history',
    label: 'History',
    icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
  },
  {
    id: 'media',
    label: 'Media',
    icon: 'M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z',
  },
  {
    id: 'overlays',
    label: 'Overlays',
    icon: 'M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z',
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: 'M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4',
  },
]);

const isActive = (id: TabId) => ui.activeTab === id;

const selectTab = (id: TabId) => {
  ui.setActiveTab(id);
};
</script>

<template>
  <aside
    :class="[
      'bg-surface-primary border-r border-border flex flex-col transition-all duration-300',
      ui.sidebarOpen ? 'w-56' : 'w-16',
    ]"
  >
    <!-- Toggle button -->
    <button
      type="button"
      class="p-3 text-content-secondary hover:text-content hover:bg-surface-tertiary transition-colors"
      :title="ui.sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'"
      @click="ui.toggleSidebar"
    >
      <svg
        class="w-5 h-5 mx-auto"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M4 6h16M4 12h16M4 18h16"
        />
      </svg>
    </button>

    <!-- Navigation -->
    <nav class="flex-1 py-2">
      <ul class="space-y-1 px-2">
        <li
          v-for="item in navItems"
          :key="item.id"
        >
          <button
            type="button"
            :class="[
              'w-full flex items-center gap-3 px-3 py-2 rounded-md transition-colors',
              isActive(item.id)
                ? 'bg-kometa-gold/10 text-kometa-gold'
                : 'text-content-secondary hover:text-content hover:bg-surface-tertiary',
            ]"
            :title="!ui.sidebarOpen ? item.label : undefined"
            @click="selectTab(item.id)"
          >
            <svg
              class="w-5 h-5 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                :d="item.icon"
              />
            </svg>

            <span
              v-if="ui.sidebarOpen"
              class="flex-1 text-left text-sm font-medium truncate"
            >
              {{ item.label }}
            </span>

            <span
              v-if="item.badge && ui.sidebarOpen"
              class="px-1.5 py-0.5 text-xs font-medium rounded-full bg-error text-white"
            >
              {{ item.badge }}
            </span>
          </button>
        </li>
      </ul>
    </nav>

    <!-- Version info -->
    <div
      v-if="ui.sidebarOpen"
      class="p-3 border-t border-border text-xs text-content-muted"
    >
      Kometa Web UI v1.0.0
    </div>
  </aside>
</template>
