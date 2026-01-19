// Core application types

// ===========================================
// Configuration Types
// ===========================================

export interface KometaConfig {
  libraries?: Record<string, LibraryConfig>;
  playlist_files?: PlaylistFile[];
  settings?: SettingsConfig;
  plex?: PlexConfig;
  tmdb?: TMDbConfig;
  radarr?: RadarrConfig;
  sonarr?: SonarrConfig;
}

export interface LibraryConfig {
  collection_files?: CollectionFile[];
  overlay_files?: OverlayFile[];
  operations?: LibraryOperations;
  settings?: LibrarySettings;
}

export interface CollectionFile {
  file?: string;
  url?: string;
  git?: string;
  repo?: string;
  template_variables?: Record<string, unknown>;
}

export interface OverlayFile {
  file?: string;
  url?: string;
  git?: string;
  repo?: string;
  template_variables?: Record<string, unknown>;
}

export interface PlaylistFile {
  file?: string;
  url?: string;
  git?: string;
  repo?: string;
}

export interface LibraryOperations {
  split_duplicates?: boolean;
  assets_for_all?: boolean;
  delete_collections?: DeleteCollectionsConfig;
  mass_genre_update?: string;
  mass_audience_rating_update?: string;
  mass_critic_rating_update?: string;
  mass_content_rating_update?: string;
  mass_originally_available_update?: string;
  mass_poster_update?: string;
}

export interface DeleteCollectionsConfig {
  configured?: boolean;
  managed?: boolean;
  less?: number;
}

export interface LibrarySettings {
  asset_directory?: string | string[];
  asset_folders?: boolean;
  asset_depth?: number;
  create_asset_folders?: boolean;
  prioritize_assets?: boolean;
  dimensional_asset_rename?: boolean;
  download_url_assets?: boolean;
  show_missing_season_assets?: boolean;
  show_missing_episode_assets?: boolean;
  show_asset_not_needed?: boolean;
  sync_mode?: 'append' | 'sync';
  default_collection_order?: string;
  minimum_items?: number;
  delete_below_minimum?: boolean;
  delete_not_scheduled?: boolean;
  run_again_delay?: number;
  missing_only_released?: boolean;
  show_unmanaged?: boolean;
  show_unconfigured?: boolean;
  show_filtered?: boolean;
  show_options?: boolean;
  show_missing?: boolean;
  only_filter_missing?: boolean;
  show_missing_assets?: boolean;
  save_report?: boolean;
  tvdb_language?: string;
  ignore_ids?: number[];
  ignore_imdb_ids?: string[];
  item_refresh_delay?: number;
  playlist_sync_to_users?: string | string[];
  playlist_exclude_users?: string | string[];
  playlist_report?: boolean;
}

export interface SettingsConfig {
  cache?: boolean;
  cache_expiration?: number;
  run_order?: string[];
  asset_directory?: string | string[];
  asset_folders?: boolean;
  asset_depth?: number;
  create_asset_folders?: boolean;
  prioritize_assets?: boolean;
  dimensional_asset_rename?: boolean;
  download_url_assets?: boolean;
  show_missing_season_assets?: boolean;
  show_missing_episode_assets?: boolean;
  show_asset_not_needed?: boolean;
  sync_mode?: 'append' | 'sync';
  default_collection_order?: string;
  minimum_items?: number;
  delete_below_minimum?: boolean;
  delete_not_scheduled?: boolean;
  run_again_delay?: number;
  missing_only_released?: boolean;
  show_unmanaged?: boolean;
  show_unconfigured?: boolean;
  show_filtered?: boolean;
  show_options?: boolean;
  show_missing?: boolean;
  only_filter_missing?: boolean;
  show_missing_assets?: boolean;
  save_report?: boolean;
  tvdb_language?: string;
  ignore_ids?: number[];
  ignore_imdb_ids?: string[];
  item_refresh_delay?: number;
  playlist_sync_to_users?: string | string[];
  playlist_exclude_users?: string | string[];
  playlist_report?: boolean;
}

export interface PlexConfig {
  url: string;
  token: string;
  timeout?: number;
  db_cache?: number;
  clean_bundles?: boolean;
  empty_trash?: boolean;
  optimize?: boolean;
}

export interface TMDbConfig {
  apikey: string;
  language?: string;
  region?: string;
  cache_expiration?: number;
}

export interface RadarrConfig {
  url: string;
  token: string;
  add_missing?: boolean;
  add_existing?: boolean;
  root_folder_path?: string;
  monitor?: boolean;
  availability?: string;
  quality_profile?: string;
  tag?: string | string[];
  search?: boolean;
  radarr_path?: string;
  plex_path?: string;
  upgrade_existing?: boolean;
  ignore_cache?: boolean;
}

export interface SonarrConfig {
  url: string;
  token: string;
  add_missing?: boolean;
  add_existing?: boolean;
  root_folder_path?: string;
  monitor?: string;
  quality_profile?: string;
  language_profile?: string;
  series_type?: string;
  season_folder?: boolean;
  tag?: string | string[];
  search?: boolean;
  cutoff_search?: boolean;
  sonarr_path?: string;
  plex_path?: string;
  upgrade_existing?: boolean;
  ignore_cache?: boolean;
}

// ===========================================
// Run Types
// ===========================================

export interface RunOptions {
  dryRun: boolean;
  libraries?: string[];
  collections?: string[];
  operations?: string[];
  playlists?: boolean;
  overlays?: boolean;
  metadata?: boolean;
}

export interface Run {
  id: string;
  start_time: string;
  end_time?: string;
  duration_seconds?: number;
  dry_run: boolean;
  status: RunStatus;
  exit_code?: number;
  libraries?: string[];
  collections?: string[];
  run_type?: string;
  log_path?: string;
  error_message?: string;
}

export type RunStatus = 'pending' | 'running' | 'success' | 'failed' | 'cancelled';

export interface RunFilters {
  status?: RunStatus;
  dryRun?: boolean;
  library?: string;
  startDate?: string;
  endDate?: string;
  limit?: number;
  offset?: number;
}

// ===========================================
// Log Types
// ===========================================

export interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  module?: string;
}

export type LogLevel = 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';

// ===========================================
// Media Types
// ===========================================

export interface MediaItem {
  id: string;
  title: string;
  year?: number;
  type: 'movie' | 'show' | 'season' | 'episode';
  poster_url?: string;
  backdrop_url?: string;
  rating?: number;
  summary?: string;
  genres?: string[];
  studio?: string;
  duration?: number;
  added_at?: string;
  updated_at?: string;
}

export interface MediaSearchParams {
  query: string;
  library?: string;
  type?: 'movie' | 'show';
  limit?: number;
}

// ===========================================
// Overlay Types
// ===========================================

export interface OverlayPreview {
  overlay_name: string;
  preview_url: string;
  applied_to: string;
  settings: Record<string, unknown>;
}

export interface OverlayConfig {
  name: string;
  file?: string;
  url?: string;
  git?: string;
  repo?: string;
  horizontal_offset?: number;
  horizontal_align?: 'left' | 'center' | 'right';
  vertical_offset?: number;
  vertical_align?: 'top' | 'center' | 'bottom';
  back_color?: string;
  back_width?: number;
  back_height?: number;
  back_line_width?: number;
}

// ===========================================
// Connection Types
// ===========================================

export interface ConnectionTest {
  service: 'plex' | 'tmdb' | 'radarr' | 'sonarr' | 'tautulli' | 'trakt';
  success: boolean;
  message: string;
  details?: Record<string, unknown>;
}

// ===========================================
// Validation Types
// ===========================================

export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

export interface ValidationError {
  path: string;
  message: string;
  line?: number;
}

export interface ValidationWarning {
  path: string;
  message: string;
  line?: number;
}

// ===========================================
// API Response Types
// ===========================================

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

export interface ApiError {
  error: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

// ===========================================
// UI Types
// ===========================================

export type Theme = 'light' | 'dark' | 'system';

export type TabId =
  | 'config'
  | 'run'
  | 'logs'
  | 'history'
  | 'media'
  | 'overlays'
  | 'settings';

export interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
  dismissible?: boolean;
}

export interface ConfirmDialogOptions {
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'warning' | 'info';
}
