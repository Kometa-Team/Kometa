import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useUIStore } from '@/stores/ui';

describe('UI Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  describe('theme', () => {
    it('defaults to dark theme', () => {
      const store = useUIStore();
      expect(store.theme).toBe('dark');
    });

    it('toggles theme', () => {
      const store = useUIStore();
      store.toggleTheme();
      expect(store.theme).toBe('light');
      store.toggleTheme();
      expect(store.theme).toBe('dark');
    });

    it('sets theme', () => {
      const store = useUIStore();
      store.setTheme('light');
      expect(store.theme).toBe('light');
    });

    it('saves theme to localStorage', () => {
      const store = useUIStore();
      store.setTheme('light');
      expect(localStorage.setItem).toHaveBeenCalledWith('kometa-theme', 'light');
    });
  });

  describe('tabs', () => {
    it('defaults to config tab', () => {
      const store = useUIStore();
      expect(store.activeTab).toBe('config');
    });

    it('changes active tab', () => {
      const store = useUIStore();
      store.setActiveTab('run');
      expect(store.activeTab).toBe('run');
    });
  });

  describe('sidebar', () => {
    it('defaults to open', () => {
      const store = useUIStore();
      expect(store.sidebarOpen).toBe(true);
    });

    it('toggles sidebar', () => {
      const store = useUIStore();
      store.toggleSidebar();
      expect(store.sidebarOpen).toBe(false);
      store.toggleSidebar();
      expect(store.sidebarOpen).toBe(true);
    });
  });

  describe('toasts', () => {
    it('shows toast', () => {
      const store = useUIStore();
      store.showToast('success', 'Test message');

      expect(store.toasts).toHaveLength(1);
      expect(store.toasts[0].type).toBe('success');
      expect(store.toasts[0].message).toBe('Test message');
    });

    it('dismisses toast', () => {
      const store = useUIStore();
      const id = store.showToast('info', 'Test');

      expect(store.toasts).toHaveLength(1);

      store.dismissToast(id);

      expect(store.toasts).toHaveLength(0);
    });

    it('clears all toasts', () => {
      const store = useUIStore();
      store.showToast('info', 'Test 1');
      store.showToast('info', 'Test 2');

      expect(store.toasts).toHaveLength(2);

      store.clearAllToasts();

      expect(store.toasts).toHaveLength(0);
    });

    it('provides convenience toast methods', () => {
      const store = useUIStore();

      store.toast.success('Success!');
      expect(store.toasts[0].type).toBe('success');

      store.toast.error('Error!');
      expect(store.toasts[1].type).toBe('error');

      store.toast.warning('Warning!');
      expect(store.toasts[2].type).toBe('warning');

      store.toast.info('Info!');
      expect(store.toasts[3].type).toBe('info');
    });
  });

  describe('confirm dialog', () => {
    it('opens confirm dialog', async () => {
      const store = useUIStore();

      const confirmPromise = store.confirm({
        title: 'Confirm?',
        message: 'Are you sure?',
      });

      expect(store.confirmDialog.open).toBe(true);
      expect(store.confirmDialog.options?.title).toBe('Confirm?');

      // Resolve the dialog
      store.resolveConfirm(true);

      const result = await confirmPromise;
      expect(result).toBe(true);
      expect(store.confirmDialog.open).toBe(false);
    });

    it('can be cancelled', async () => {
      const store = useUIStore();

      const confirmPromise = store.confirm({
        title: 'Confirm?',
        message: 'Are you sure?',
      });

      store.resolveConfirm(false);

      const result = await confirmPromise;
      expect(result).toBe(false);
    });
  });

  describe('loading state', () => {
    it('sets loading state', () => {
      const store = useUIStore();

      store.setLoading(true, 'Loading...');

      expect(store.globalLoading).toBe(true);
      expect(store.loadingMessage).toBe('Loading...');
    });

    it('clears loading state', () => {
      const store = useUIStore();

      store.setLoading(true, 'Loading...');
      store.setLoading(false);

      expect(store.globalLoading).toBe(false);
      expect(store.loadingMessage).toBe('');
    });
  });
});
