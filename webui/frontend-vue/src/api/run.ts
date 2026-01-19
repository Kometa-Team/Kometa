import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query';
import { api } from './client';
import type { Run, RunOptions, RunFilters } from '@/types';

// Query keys
export const runKeys = {
  all: ['runs'] as const,
  lists: () => [...runKeys.all, 'list'] as const,
  list: (filters: RunFilters) => [...runKeys.lists(), filters] as const,
  details: () => [...runKeys.all, 'detail'] as const,
  detail: (id: string) => [...runKeys.details(), id] as const,
  current: () => [...runKeys.all, 'current'] as const,
  status: () => [...runKeys.all, 'status'] as const,
};

// Types
interface RunHistoryResponse {
  runs: Run[];
  total: number;
}

interface StartRunResponse {
  success: boolean;
  run_id: string;
  message: string;
}

interface RunStatusResponse {
  is_running: boolean;
  current_run: Run | null;
  progress: number;
}

// Queries

/**
 * Fetch run history with optional filters
 */
export function useRunHistory(filters: RunFilters = {}) {
  return useQuery({
    queryKey: runKeys.list(filters),
    queryFn: () =>
      api.get<RunHistoryResponse>('/runs', {
        params: {
          status: filters.status,
          dry_run: filters.dryRun,
          library: filters.library,
          start_date: filters.startDate,
          end_date: filters.endDate,
          limit: filters.limit || 50,
          offset: filters.offset || 0,
        },
      }),
  });
}

/**
 * Fetch details of a specific run
 */
export function useRunDetail(id: string) {
  return useQuery({
    queryKey: runKeys.detail(id),
    queryFn: () => api.get<Run>(`/runs/${id}`),
    enabled: !!id,
  });
}

/**
 * Fetch current run status
 */
export function useRunStatus() {
  return useQuery({
    queryKey: runKeys.status(),
    queryFn: () => api.get<RunStatusResponse>('/run/status'),
    refetchInterval: (query) => {
      // Refetch every 2 seconds if running
      return query.state.data?.is_running ? 2000 : false;
    },
  });
}

/**
 * Fetch logs for a specific run
 */
export function useRunLogs(id: string) {
  return useQuery({
    queryKey: [...runKeys.detail(id), 'logs'],
    queryFn: () => api.get<{ logs: string }>(`/runs/${id}/logs`),
    enabled: !!id,
  });
}

// Mutations

/**
 * Start a new Kometa run
 */
export function useStartRun() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (options: RunOptions) =>
      api.post<StartRunResponse>('/run', {
        dry_run: options.dryRun,
        libraries: options.libraries,
        collections: options.collections,
        operations: options.operations,
        playlists: options.playlists,
        overlays: options.overlays,
        metadata: options.metadata,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: runKeys.status() });
      queryClient.invalidateQueries({ queryKey: runKeys.lists() });
    },
  });
}

/**
 * Start an apply run (non-dry-run)
 */
export function useStartApplyRun() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (options: Omit<RunOptions, 'dryRun'>) =>
      api.post<StartRunResponse>('/run/apply', {
        libraries: options.libraries,
        collections: options.collections,
        operations: options.operations,
        playlists: options.playlists,
        overlays: options.overlays,
        metadata: options.metadata,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: runKeys.status() });
      queryClient.invalidateQueries({ queryKey: runKeys.lists() });
    },
  });
}

/**
 * Stop the current run
 */
export function useStopRun() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => api.post<{ success: boolean; message: string }>('/run/stop'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: runKeys.status() });
      queryClient.invalidateQueries({ queryKey: runKeys.lists() });
    },
  });
}

/**
 * Delete a run from history
 */
export function useDeleteRun() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => api.delete<{ success: boolean }>(`/runs/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: runKeys.lists() });
    },
  });
}
