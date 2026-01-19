<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  modelValue: boolean;
  disabled?: boolean;
  label?: string;
  description?: string;
  id?: string;
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
});

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'change', value: boolean): void;
}>();

const checked = computed({
  get: () => props.modelValue,
  set: (value: boolean) => {
    emit('update:modelValue', value);
    emit('change', value);
  },
});

const checkboxId = computed(
  () => props.id || `checkbox-${Math.random().toString(36).slice(2, 9)}`
);
</script>

<template>
  <div class="flex items-start gap-3">
    <div class="flex items-center h-5">
      <input
        :id="checkboxId"
        v-model="checked"
        type="checkbox"
        :disabled="disabled"
        class="w-4 h-4 rounded border-border bg-surface-primary text-kometa-gold
               focus:ring-kometa-gold focus:ring-offset-0
               disabled:opacity-50 disabled:cursor-not-allowed"
      >
    </div>

    <div
      v-if="label || description"
      class="flex flex-col"
    >
      <label
        :for="checkboxId"
        :class="[
          'text-sm font-medium',
          disabled ? 'text-content-disabled cursor-not-allowed' : 'text-content cursor-pointer',
        ]"
      >
        {{ label }}
      </label>
      <p
        v-if="description"
        class="text-sm text-content-muted"
      >
        {{ description }}
      </p>
    </div>
  </div>
</template>
