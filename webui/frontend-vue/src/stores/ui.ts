import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Theme, TabId, Toast, ConfirmDialogOptions } from '@/types';

export const useUIStore = defineStore('ui', () => {
  // ===========================================
  // State
  // ===========================================

  // Theme
  const theme = ref<Theme>(
    (localStorage.getItem('kometa-theme') as Theme) || 'dark'
  );

  // Navigation
  const activeTab = ref<TabId>('config');
  const sidebarOpen = ref(true);

  // Toasts
  const toasts = ref<Toast[]>([]);
  let toastIdCounter = 0;

  // Modals
  const confirmDialog = ref<{
    open: boolean;
    options: ConfirmDialogOptions | null;
    resolve: ((value: boolean) => void) | null;
  }>({
    open: false,
    options: null,
    resolve: null,
  });

  // Loading states
  const globalLoading = ref(false);
  const loadingMessage = ref('');

  // ===========================================
  // Getters
  // ===========================================

  const isDarkMode = computed(() => {
    if (theme.value === 'system') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    return theme.value === 'dark';
  });

  const hasToasts = computed(() => toasts.value.length > 0);

  // ===========================================
  // Actions
  // ===========================================

  // Theme actions
  function setTheme(newTheme: Theme) {
    theme.value = newTheme;
    localStorage.setItem('kometa-theme', newTheme);

    // Update document class
    if (newTheme === 'light') {
      document.documentElement.classList.add('light');
    } else if (newTheme === 'dark') {
      document.documentElement.classList.remove('light');
    } else {
      // System preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      if (prefersDark) {
        document.documentElement.classList.remove('light');
      } else {
        document.documentElement.classList.add('light');
      }
    }
  }

  function toggleTheme() {
    setTheme(theme.value === 'dark' ? 'light' : 'dark');
  }

  // Navigation actions
  function setActiveTab(tab: TabId) {
    activeTab.value = tab;
  }

  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value;
  }

  // Toast actions
  function showToast(
    type: Toast['type'],
    message: string,
    options?: { duration?: number; dismissible?: boolean }
  ) {
    const id = `toast-${++toastIdCounter}`;
    const toast: Toast = {
      id,
      type,
      message,
      duration: options?.duration ?? 5000,
      dismissible: options?.dismissible ?? true,
    };

    toasts.value.push(toast);

    // Auto-dismiss
    if (toast.duration && toast.duration > 0) {
      setTimeout(() => {
        dismissToast(id);
      }, toast.duration);
    }

    return id;
  }

  function dismissToast(id: string) {
    const index = toasts.value.findIndex((t) => t.id === id);
    if (index !== -1) {
      toasts.value.splice(index, 1);
    }
  }

  function clearAllToasts() {
    toasts.value = [];
  }

  // Convenience toast methods
  const toast = {
    success: (message: string, options?: { duration?: number }) =>
      showToast('success', message, options),
    error: (message: string, options?: { duration?: number }) =>
      showToast('error', message, { ...options, duration: options?.duration ?? 8000 }),
    warning: (message: string, options?: { duration?: number }) =>
      showToast('warning', message, options),
    info: (message: string, options?: { duration?: number }) =>
      showToast('info', message, options),
  };

  // Confirm dialog
  function confirm(options: ConfirmDialogOptions): Promise<boolean> {
    return new Promise((resolve) => {
      confirmDialog.value = {
        open: true,
        options,
        resolve,
      };
    });
  }

  function resolveConfirm(result: boolean) {
    if (confirmDialog.value.resolve) {
      confirmDialog.value.resolve(result);
    }
    confirmDialog.value = {
      open: false,
      options: null,
      resolve: null,
    };
  }

  // Loading state
  function setLoading(loading: boolean, message?: string) {
    globalLoading.value = loading;
    loadingMessage.value = message || '';
  }

  return {
    // State
    theme,
    activeTab,
    sidebarOpen,
    toasts,
    confirmDialog,
    globalLoading,
    loadingMessage,

    // Getters
    isDarkMode,
    hasToasts,

    // Actions
    setTheme,
    toggleTheme,
    setActiveTab,
    toggleSidebar,
    showToast,
    dismissToast,
    clearAllToasts,
    toast,
    confirm,
    resolveConfirm,
    setLoading,
  };
});
