<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  modelValue: string;
  placeholder?: string;
  disabled?: boolean;
  readonly?: boolean;
  error?: string;
  label?: string;
  hint?: string;
  required?: boolean;
  rows?: number;
  maxLength?: number;
  resize?: 'none' | 'vertical' | 'horizontal' | 'both';
  monospace?: boolean;
  id?: string;
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  readonly: false,
  required: false,
  rows: 4,
  resize: 'vertical',
  monospace: false,
});

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void;
  (e: 'focus', event: FocusEvent): void;
  (e: 'blur', event: FocusEvent): void;
}>();

const inputValue = computed({
  get: () => props.modelValue,
  set: (value: string) => emit('update:modelValue', value),
});

const inputId = computed(
  () => props.id || `textarea-${Math.random().toString(36).slice(2, 9)}`
);

const resizeClass = {
  none: 'resize-none',
  vertical: 'resize-y',
  horizontal: 'resize-x',
  both: 'resize',
};

const characterCount = computed(() => props.modelValue?.length || 0);
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

    <textarea
      :id="inputId"
      v-model="inputValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :readonly="readonly"
      :required="required"
      :rows="rows"
      :maxlength="maxLength"
      :class="[
        'input',
        resizeClass[resize],
        { 'input-error': error, 'font-mono text-sm': monospace },
      ]"
      @focus="emit('focus', $event)"
      @blur="emit('blur', $event)"
    />

    <div class="flex justify-between mt-1">
      <p
        v-if="error"
        class="text-sm text-error"
      >
        {{ error }}
      </p>
      <p
        v-else-if="hint"
        class="text-sm text-content-muted"
      >
        {{ hint }}
      </p>
      <span v-else />

      <span
        v-if="maxLength"
        class="text-sm text-content-muted"
      >
        {{ characterCount }}/{{ maxLength }}
      </span>
    </div>
  </div>
</template>
