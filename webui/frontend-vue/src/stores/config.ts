import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { KometaConfig, ValidationResult, ValidationError, ValidationWarning } from '@/types';

export const useConfigStore = defineStore('config', () => {
  // ===========================================
  // State
  // ===========================================

  // Raw YAML content
  const rawConfig = ref<string>('');

  // Parsed configuration (may be null if parsing failed)
  const parsedConfig = ref<KometaConfig | null>(null);

  // Validation state
  const validation = ref<ValidationResult>({
    valid: true,
    errors: [],
    warnings: [],
  });

  // Edit state
  const isDirty = ref(false);
  const lastSaved = ref<Date | null>(null);
  const isLoading = ref(false);
  const isSaving = ref(false);

  // Editor state
  const editorCursorPosition = ref({ line: 1, column: 1 });

  // ===========================================
  // Getters
  // ===========================================

  const hasErrors = computed(() => validation.value.errors.length > 0);

  const hasWarnings = computed(() => validation.value.warnings.length > 0);

  const isValid = computed(() => validation.value.valid);

  const libraries = computed(() => {
    if (!parsedConfig.value?.libraries) return [];
    return Object.keys(parsedConfig.value.libraries);
  });

  const collections = computed(() => {
    if (!parsedConfig.value?.libraries) return [];
    const allCollections: string[] = [];
    for (const library of Object.values(parsedConfig.value.libraries)) {
      if (library.collection_files) {
        for (const cf of library.collection_files) {
          if (cf.file) {
            allCollections.push(cf.file);
          }
        }
      }
    }
    return allCollections;
  });

  const canSave = computed(() => isDirty.value && isValid.value && !isSaving.value);

  // ===========================================
  // Actions
  // ===========================================

  function setRawConfig(content: string, markDirty = true) {
    rawConfig.value = content;
    if (markDirty) {
      isDirty.value = true;
    }
  }

  function setParsedConfig(config: KometaConfig | null) {
    parsedConfig.value = config;
  }

  function setValidation(result: ValidationResult) {
    validation.value = result;
  }

  function addValidationError(error: ValidationError) {
    validation.value.errors.push(error);
    validation.value.valid = false;
  }

  function addValidationWarning(warning: ValidationWarning) {
    validation.value.warnings.push(warning);
  }

  function clearValidation() {
    validation.value = {
      valid: true,
      errors: [],
      warnings: [],
    };
  }

  function markSaved() {
    isDirty.value = false;
    lastSaved.value = new Date();
  }

  function setLoading(loading: boolean) {
    isLoading.value = loading;
  }

  function setSaving(saving: boolean) {
    isSaving.value = saving;
  }

  function setCursorPosition(line: number, column: number) {
    editorCursorPosition.value = { line, column };
  }

  function reset() {
    rawConfig.value = '';
    parsedConfig.value = null;
    validation.value = { valid: true, errors: [], warnings: [] };
    isDirty.value = false;
    lastSaved.value = null;
    isLoading.value = false;
    isSaving.value = false;
  }

  return {
    // State
    rawConfig,
    parsedConfig,
    validation,
    isDirty,
    lastSaved,
    isLoading,
    isSaving,
    editorCursorPosition,

    // Getters
    hasErrors,
    hasWarnings,
    isValid,
    libraries,
    collections,
    canSave,

    // Actions
    setRawConfig,
    setParsedConfig,
    setValidation,
    addValidationError,
    addValidationWarning,
    clearValidation,
    markSaved,
    setLoading,
    setSaving,
    setCursorPosition,
    reset,
  };
});
