import { useQuery, useMutation } from '@tanstack/vue-query';
import { api } from './client';
import type { MediaItem, MediaSearchParams, OverlayPreview, ConnectionTest } from '@/types';

// Query keys
export const mediaKeys = {
  all: ['media'] as const,
  search: (params: MediaSearchParams) => [...mediaKeys.all, 'search', params] as const,
  item: (id: string) => [...mediaKeys.all, 'item', id] as const,
};

export const overlayKeys = {
  all: ['overlays'] as const,
  list: () => [...overlayKeys.all, 'list'] as const,
  preview: (name: string) => [...overlayKeys.all, 'preview', name] as const,
};

export const connectionKeys = {
  all: ['connections'] as const,
  test: (service: string) => [...connectionKeys.all, 'test', service] as const,
};

// Types
interface MediaSearchResponse {
  items: MediaItem[];
  total: number;
}

interface OverlayListResponse {
  overlays: string[];
}

// Media Queries

/**
 * Search for media items
 */
export function useMediaSearch(params: MediaSearchParams) {
  return useQuery({
    queryKey: mediaKeys.search(params),
    queryFn: () =>
      api.get<MediaSearchResponse>('/media/search', {
        params: {
          query: params.query,
          library: params.library,
          type: params.type,
          limit: params.limit || 20,
        },
      }),
    enabled: !!params.query && params.query.length >= 2,
  });
}

/**
 * Get media item details
 */
export function useMediaItem(id: string) {
  return useQuery({
    queryKey: mediaKeys.item(id),
    queryFn: () => api.get<MediaItem>(`/media/${id}`),
    enabled: !!id,
  });
}

// Overlay Queries

/**
 * Get list of available overlays
 */
export function useOverlayList() {
  return useQuery({
    queryKey: overlayKeys.list(),
    queryFn: () => api.get<OverlayListResponse>('/overlays'),
  });
}

/**
 * Generate overlay preview
 */
export function useGenerateOverlayPreview() {
  return useMutation({
    mutationFn: (params: {
      overlay_name: string;
      media_id: string;
      settings?: Record<string, unknown>;
    }) => api.post<OverlayPreview>('/overlays/preview', params),
  });
}

// Connection Testing

/**
 * Test a service connection
 */
export function useTestConnection() {
  return useMutation({
    mutationFn: (service: 'plex' | 'tmdb' | 'radarr' | 'sonarr' | 'tautulli' | 'trakt') =>
      api.post<ConnectionTest>(`/test/${service}`),
  });
}

/**
 * Test all connections
 */
export function useTestAllConnections() {
  return useMutation({
    mutationFn: () => api.post<ConnectionTest[]>('/test/all'),
  });
}

// Settings

/**
 * Get current settings (apply mode, password requirement, etc.)
 */
export function useSettings() {
  return useQuery({
    queryKey: ['settings'],
    queryFn: () =>
      api.get<{
        apply_enabled: boolean;
        password_required: boolean;
        version: string;
      }>('/settings'),
  });
}

/**
 * Update settings
 */
export function useUpdateSettings() {
  return useMutation({
    mutationFn: (settings: { apply_enabled?: boolean; password?: string }) =>
      api.put<{ success: boolean }>('/settings', settings),
  });
}
