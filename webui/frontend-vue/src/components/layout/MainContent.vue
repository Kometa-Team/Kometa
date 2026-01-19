<script setup lang="ts">
import { useUIStore } from '@/stores';

// Tab content components
import ConfigTab from '@/components/tabs/ConfigTab.vue';
import RunTab from '@/components/tabs/RunTab.vue';
import LogsTab from '@/components/tabs/LogsTab.vue';
import HistoryTab from '@/components/tabs/HistoryTab.vue';
import MediaTab from '@/components/tabs/MediaTab.vue';
import OverlaysTab from '@/components/tabs/OverlaysTab.vue';
import SettingsTab from '@/components/tabs/SettingsTab.vue';

const ui = useUIStore();

const tabs = {
  config: ConfigTab,
  run: RunTab,
  logs: LogsTab,
  history: HistoryTab,
  media: MediaTab,
  overlays: OverlaysTab,
  settings: SettingsTab,
};
</script>

<template>
  <div class="h-full">
    <Transition
      name="fade"
      mode="out-in"
    >
      <component
        :is="tabs[ui.activeTab]"
        :key="ui.activeTab"
      />
    </Transition>
  </div>
</template>
