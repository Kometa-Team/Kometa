import { useUIStore } from '@/stores';

export function useToast() {
  const ui = useUIStore();

  return {
    success: (message: string, options?: { duration?: number }) =>
      ui.toast.success(message, options),

    error: (message: string, options?: { duration?: number }) =>
      ui.toast.error(message, options),

    warning: (message: string, options?: { duration?: number }) =>
      ui.toast.warning(message, options),

    info: (message: string, options?: { duration?: number }) =>
      ui.toast.info(message, options),

    dismiss: (id: string) => ui.dismissToast(id),

    clear: () => ui.clearAllToasts(),
  };
}
