<script setup lang="ts">
import { computed } from 'vue';

interface Tab {
  id: string;
  label: string;
  icon?: string;
  badge?: string | number;
  disabled?: boolean;
}

interface Props {
  tabs: Tab[];
  modelValue: string;
  variant?: 'underline' | 'pills' | 'boxed';
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'underline',
});

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void;
}>();

const activeTab = computed({
  get: () => props.modelValue,
  set: (value: string) => emit('update:modelValue', value),
});

const selectTab = (tab: Tab) => {
  if (!tab.disabled) {
    activeTab.value = tab.id;
  }
};

const baseTabClasses = 'flex items-center gap-2 font-medium transition-colors';

const variantClasses = {
  underline: {
    container: 'flex border-b border-border',
    tab: `${baseTabClasses} px-4 py-2 -mb-px border-b-2 border-transparent hover:text-content hover:border-border`,
    active: 'text-kometa-gold border-kometa-gold',
    inactive: 'text-content-secondary',
  },
  pills: {
    container: 'flex gap-1 p-1 bg-surface-tertiary rounded-lg',
    tab: `${baseTabClasses} px-3 py-1.5 rounded-md hover:text-content`,
    active: 'bg-surface-primary text-content shadow-sm',
    inactive: 'text-content-secondary',
  },
  boxed: {
    container: 'flex gap-2',
    tab: `${baseTabClasses} px-4 py-2 border border-border rounded-md hover:border-kometa-gold`,
    active: 'bg-kometa-gold text-content-inverse border-kometa-gold',
    inactive: 'text-content-secondary bg-surface-secondary',
  },
};
</script>

<template>
  <div>
    <div
      :class="variantClasses[variant].container"
      role="tablist"
    >
      <button
        v-for="tab in tabs"
        :key="tab.id"
        type="button"
        role="tab"
        :aria-selected="tab.id === activeTab"
        :aria-disabled="tab.disabled"
        :tabindex="tab.disabled ? -1 : 0"
        :class="[
          variantClasses[variant].tab,
          tab.id === activeTab
            ? variantClasses[variant].active
            : variantClasses[variant].inactive,
          { 'opacity-50 cursor-not-allowed': tab.disabled },
        ]"
        @click="selectTab(tab)"
      >
        <span
          v-if="tab.icon"
          class="text-lg"
          v-html="tab.icon"
        />
        <span>{{ tab.label }}</span>
        <span
          v-if="tab.badge !== undefined"
          class="px-1.5 py-0.5 text-xs rounded-full bg-surface-tertiary"
        >
          {{ tab.badge }}
        </span>
      </button>
    </div>

    <div class="mt-4">
      <slot :active-tab="activeTab" />
    </div>
  </div>
</template>
