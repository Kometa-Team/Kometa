<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  modelValue: string | number;
  type?: 'text' | 'password' | 'email' | 'number' | 'search' | 'url';
  placeholder?: string;
  disabled?: boolean;
  readonly?: boolean;
  error?: string;
  label?: string;
  hint?: string;
  required?: boolean;
  id?: string;
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  disabled: false,
  readonly: false,
  required: false,
});

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | number): void;
  (e: 'focus', event: FocusEvent): void;
  (e: 'blur', event: FocusEvent): void;
}>();

const inputValue = computed({
  get: () => props.modelValue,
  set: (value: string | number) => emit('update:modelValue', value),
});

const inputId = computed(() => props.id || `input-${Math.random().toString(36).slice(2, 9)}`);
</script>

<template>
  <div class="w-full">
    <label
      v-if="label"
      :for="inputId"
      class="label"
    >
      {{ label }}
      <span
        v-if="required"
        class="text-error"
      >*</span>
    </label>

    <div class="relative">
      <input
        :id="inputId"
        v-model="inputValue"
        :type="type"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :required="required"
        :class="[
          'input',
          { 'input-error': error },
        ]"
        @focus="emit('focus', $event)"
        @blur="emit('blur', $event)"
      >

      <slot name="suffix" />
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
