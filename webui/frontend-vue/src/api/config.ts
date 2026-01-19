import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query';
import { api } from './client';
import type { ValidationResult } from '@/types';

// Query keys
export const configKeys = {
  all: ['config'] as const,
  detail: () => [...configKeys.all, 'detail'] as const,
  validation: () => [...configKeys.all, 'validation'] as const,
  backups: () => [...configKeys.all, 'backups'] as const,
  libraries: () => [...configKeys.all, 'libraries'] as const,
};

// Types
interface ConfigResponse {
  content: string;
  last_modified: string;
}

interface BackupInfo {
  filename: string;
  created: string;
  size: number;
}

interface LibraryInfo {
  name: string;
  type: string;
  item_count?: number;
}

// Queries

/**
 * Fetch the current configuration
 */
export function useConfig() {
  return useQuery({
    queryKey: configKeys.detail(),
    queryFn: () => api.get<ConfigResponse>('/config'),
  });
}

/**
 * Validate configuration content
 */
export function useValidateConfig() {
  return useMutation({
    mutationFn: (content: string) =>
      api.post<ValidationResult>('/config/validate', { content }),
  });
}

/**
 * Fetch list of backups
 */
export function useConfigBackups() {
  return useQuery({
    queryKey: configKeys.backups(),
    queryFn: () => api.get<BackupInfo[]>('/config/backups'),
  });
}

/**
 * Fetch available libraries from config
 */
export function useLibraries() {
  return useQuery({
    queryKey: configKeys.libraries(),
    queryFn: () => api.get<LibraryInfo[]>('/libraries'),
  });
}

// Mutations

/**
 * Save configuration
 */
export function useSaveConfig() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (content: string) =>
      api.put<{ success: boolean; message: string }>('/config', { content }),
    onSuccess: () => {
      // Invalidate config queries to refetch fresh data
      queryClient.invalidateQueries({ queryKey: configKeys.all });
    },
  });
}

/**
 * Create a backup of current configuration
 */
export function useCreateBackup() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () =>
      api.post<{ success: boolean; filename: string }>('/config/backup'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: configKeys.backups() });
    },
  });
}

/**
 * Restore configuration from backup
 */
export function useRestoreBackup() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (filename: string) =>
      api.post<{ success: boolean; message: string }>('/config/restore', {
        filename,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: configKeys.all });
    },
  });
}

/**
 * Delete a backup
 */
export function useDeleteBackup() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (filename: string) =>
      api.delete<{ success: boolean }>(`/config/backups/${filename}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: configKeys.backups() });
    },
  });
}
