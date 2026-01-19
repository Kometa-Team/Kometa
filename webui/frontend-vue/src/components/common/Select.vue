<script setup lang="ts">
import { computed } from 'vue';

interface Option {
  value: string | number;
  label: string;
  disabled?: boolean;
}

interface Props {
  modelValue: string | number | null;
  options: Option[];
  placeholder?: string;
  disabled?: boolean;
  error?: string;
  label?: string;
  hint?: string;
  required?: boolean;
  id?: string;
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  required: false,
  placeholder: 'Select an option',
});

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | number | null): void;
  (e: 'change', value: string | number | null): void;
}>();

const selectedValue = computed({
  get: () => props.modelValue,
  set: (value: string | number | null) => {
    emit('update:modelValue', value);
    emit('change', value);
  },
});

const selectId = computed(
  () => props.id || `select-${Math.random().toString(36).slice(2, 9)}`
);
</script>

<template>
  <div class="w-full">
    <label
      v-if="label"
      :for="selectId"
      class="label"
    >
      {{ label }}
      <span
        v-if="required"
        class="text-error"
      >*</span>
    </label>

    <div class="relative">
      <select
        :id="selectId"
        v-model="selectedValue"
        :disabled="disabled"
        :required="required"
        :class="[
          'input appearance-none pr-10',
          { 'input-error': error },
        ]"
      >
        <option
          v-if="placeholder"
          value=""
          disabled
        >
          {{ placeholder }}
        </option>
        <option
          v-for="option in options"
          :key="option.value"
          :value="option.value"
          :disabled="option.disabled"
        >
          {{ option.label }}
        </option>
      </select>

      <!-- Dropdown arrow -->
      <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
        <svg
          class="w-4 h-4 text-content-muted"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </div>
    </div>

    <p
      v-if="error"
      class="mt-1 text-sm text-error"
    >
      {{ error }}
    </p>
    <p
      v-else-if="hint"
      class="mt-1 text-sm text-content-muted"
    >
      {{ hint }}
    </p>
  </div>
</template>
