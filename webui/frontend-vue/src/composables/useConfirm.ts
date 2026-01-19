import { useUIStore } from '@/stores';
import type { ConfirmDialogOptions } from '@/types';

export function useConfirm() {
  const ui = useUIStore();

  const confirm = (options: ConfirmDialogOptions): Promise<boolean> => {
    return ui.confirm(options);
  };

  const confirmDanger = (
    title: string,
    message: string,
    confirmText = 'Delete'
  ): Promise<boolean> => {
    return confirm({
      title,
      message,
      confirmText,
      cancelText: 'Cancel',
      variant: 'danger',
    });
  };

  const confirmWarning = (
    title: string,
    message: string,
    confirmText = 'Proceed'
  ): Promise<boolean> => {
    return confirm({
      title,
      message,
      confirmText,
      cancelText: 'Cancel',
      variant: 'warning',
    });
  };

  return {
    confirm,
    confirmDanger,
    confirmWarning,
  };
}
