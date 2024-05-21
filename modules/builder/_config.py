from modules import anidb, anilist, icheckmovies, imdb, letterboxd, mal, mojo, plex, radarr, reciperr, sonarr, tautulli, tmdb, trakt, tvdb, mdblist

advance_new_agent = ["item_metadata_language", "item_use_original_title"]
advance_show = ["item_episode_sorting", "item_keep_episodes", "item_delete_episodes", "item_season_display", "item_episode_sorting"]
all_builders = anidb.builders + anilist.builders + icheckmovies.builders + imdb.builders + \
               letterboxd.builders + mal.builders + mojo.builders + plex.builders + reciperr.builders + tautulli.builders + \
               tmdb.builders + trakt.builders + tvdb.builders + mdblist.builders + radarr.builders + sonarr.builders
show_only_builders = [
    "tmdb_network", "tmdb_show", "tmdb_show_details", "tvdb_show", "tvdb_show_details", "tmdb_airing_today",
    "tmdb_on_the_air", "builder_level", "item_tmdb_season_titles", "sonarr_all", "sonarr_taglist"
]
movie_only_builders = [
    "letterboxd_list", "letterboxd_list_details", "icheckmovies_list", "icheckmovies_list_details", "stevenlu_popular",
    "tmdb_collection", "tmdb_collection_details", "tmdb_movie", "tmdb_movie_details", "tmdb_now_playing", "item_edition",
    "tvdb_movie", "tvdb_movie_details", "tmdb_upcoming", "trakt_boxoffice", "reciperr_list", "radarr_all", "radarr_taglist",
    "mojo_world", "mojo_domestic", "mojo_international", "mojo_record", "mojo_all_time", "mojo_never"
]
music_only_builders = ["item_album_sorting"]
summary_details = [
    "summary", "tmdb_summary", "tmdb_description", "tmdb_biography", "tvdb_summary",
    "tvdb_description", "trakt_description", "letterboxd_description", "icheckmovies_description"
]
poster_details = ["url_poster", "tmdb_poster", "tmdb_profile", "tvdb_poster", "file_poster"]
background_details = ["url_background", "tmdb_background", "tvdb_background", "file_background"]
boolean_details = [
    "show_filtered", "show_missing", "save_report", "missing_only_released", "only_filter_missing",
    "delete_below_minimum", "asset_folders", "create_asset_folders"
]
scheduled_boolean = ["visible_library", "visible_home", "visible_shared"]
string_details = ["sort_title", "content_rating", "name_mapping"]
ignored_details = [
    "smart_filter", "smart_label", "smart_url", "run_again", "schedule", "sync_mode", "template", "variables", "test", "suppress_overlays",
    "delete_not_scheduled", "tmdb_person", "build_collection", "collection_order", "builder_level", "overlay", "kometa_poster",
    "validate_builders", "libraries", "sync_to_users", "exclude_users", "collection_name", "playlist_name", "name", "limit",
    "blank_collection", "allowed_library_types", "run_definition", "delete_playlist", "ignore_blank_results", "only_run_on_create",
    "delete_collections_named", "tmdb_person_offset", "append_label", "key_name", "translation_key", "translation_prefix", "tmdb_birthday"
]
details = [
    "ignore_ids", "ignore_imdb_ids", "server_preroll", "changes_webhooks", "collection_filtering", "collection_mode", "url_theme",
    "file_theme", "minimum_items", "label", "album_sorting", "cache_builders", "tmdb_region", "default_percent"
] + boolean_details + scheduled_boolean + string_details
collectionless_details = ["collection_order", "plex_collectionless", "label", "label_sync_mode", "test", "item_label"] + \
                         poster_details + background_details + summary_details + string_details + all_builders
item_false_details = ["item_lock_background", "item_lock_poster", "item_lock_title"]
item_bool_details = ["item_tmdb_season_titles", "revert_overlay", "item_assets", "item_refresh"] + item_false_details
item_details = ["non_item_remove_label", "item_label", "item_genre", "item_edition", "item_radarr_tag", "item_sonarr_tag", "item_refresh_delay"] + item_bool_details + list(plex.item_advance_keys.keys())
none_details = ["label.sync", "item_label.sync", "item_genre.sync", "radarr_taglist", "sonarr_taglist", "item_edition"]
none_builders = ["radarr_tag_list", "sonarr_taglist"]
radarr_details = [
    "radarr_add_missing", "radarr_add_existing", "radarr_upgrade_existing", "radarr_monitor_existing", "radarr_folder", "radarr_monitor",
    "radarr_search", "radarr_availability", "radarr_quality", "radarr_tag", "item_radarr_tag", "radarr_ignore_cache",
]
sonarr_details = [
    "sonarr_add_missing", "sonarr_add_existing", "sonarr_upgrade_existing", "sonarr_monitor_existing", "sonarr_folder", "sonarr_monitor", "sonarr_language",
    "sonarr_series", "sonarr_quality", "sonarr_season", "sonarr_search", "sonarr_cutoff_search", "sonarr_tag", "item_sonarr_tag", "sonarr_ignore_cache"
]
album_details = ["non_item_remove_label", "item_label", "item_album_sorting"]
sub_filters = [
    "filepath", "audio_track_title", "subtitle_track_title", "resolution", "audio_language", "subtitle_language", "has_dolby_vision",
    "channels", "height", "width", "aspect", "audio_codec", "audio_profile", "video_codec", "video_profile", "versions"
]
filters_by_type = {
    "movie_show_season_episode_artist_album_track": ["title", "summary", "collection", "has_collection", "added", "last_played", "user_rating", "plays", "filepath", "label", "audio_track_title", "subtitle_track_title", "versions"],
    "movie_show_season_episode_album_track": ["year"],
    "movie_show_season_episode_artist_album": ["has_overlay"],
    "movie_show_season_episode": ["resolution", "audio_language", "subtitle_language", "has_dolby_vision", "channels", "height", "width", "aspect", "audio_codec", "audio_profile", "video_codec", "video_profile"],
    "movie_show_episode_album": ["release", "critic_rating", "history"],
    "movie_show_episode_track": ["duration"],
    "movie_show_artist_album": ["genre"],
    "movie_show_episode": ["actor", "content_rating", "audience_rating"],
    "movie_show": ["studio", "original_language", "tmdb_vote_count", "tmdb_vote_average", "tmdb_year", "tmdb_genre", "tmdb_title", "tmdb_keyword", "imdb_keyword"],
    "movie_episode": ["director", "producer", "writer"],
    "movie_artist": ["country"],
    "show_artist": ["folder"],
    "show_season": ["episodes"],
    "artist_album": ["tracks"],
    "movie": ["edition", "has_edition", "stinger_rating", "has_stinger"],
    "show": ["seasons", "tmdb_status", "tmdb_type", "origin_country", "network", "first_episode_aired", "last_episode_aired", "last_episode_aired_or_never", "tvdb_title", "tvdb_status", "tvdb_genre"],
    "artist": ["albums"],
    "album": ["record_label"]
}
filters = {
    "movie": [item for check, sub in filters_by_type.items() for item in sub if "movie" in check],
    "show": [item for check, sub in filters_by_type.items() for item in sub if "show" in check],
    "season": [item for check, sub in filters_by_type.items() for item in sub if "season" in check],
    "episode": [item for check, sub in filters_by_type.items() for item in sub if "episode" in check],
    "artist": [item for check, sub in filters_by_type.items() for item in sub if "artist" in check],
    "album": [item for check, sub in filters_by_type.items() for item in sub if "album" in check],
    "track": [item for check, sub in filters_by_type.items() for item in sub if "track" in check]
}
tmdb_filters = [
    "original_language", "origin_country", "tmdb_vote_count", "tmdb_vote_average", "tmdb_year", "tmdb_keyword", "tmdb_genre",
    "first_episode_aired", "last_episode_aired", "last_episode_aired_or_never", "tmdb_status", "tmdb_type", "tmdb_title"
]
tvdb_filters = ["tvdb_title", "tvdb_status", "tvdb_genre"]
imdb_filters = ["imdb_keyword"]
string_filters = [
    "title", "summary", "studio", "edition", "record_label", "folder", "filepath", "audio_track_title", "subtitle_track_title", "tmdb_title",
    "audio_codec", "audio_profile", "video_codec", "video_profile", "tvdb_title", "tvdb_status"
]
string_modifiers = ["", ".not", ".is", ".isnot", ".begins", ".ends", ".regex"]
tag_filters = [
    "actor", "collection", "content_rating", "country", "director", "network", "genre", "label", "producer", "year",
    "origin_country", "writer", "resolution", "audio_language", "subtitle_language", "tmdb_keyword", "tmdb_genre", "imdb_keyword", "tvdb_genre"
]
tag_modifiers = ["", ".not", ".regex", ".count_gt", ".count_gte", ".count_lt", ".count_lte"]
boolean_filters = ["has_collection", "has_edition", "has_overlay", "has_dolby_vision", "has_stinger"]
date_filters = ["release", "added", "last_played", "first_episode_aired", "last_episode_aired", "last_episode_aired_or_never"]
date_modifiers = ["", ".not", ".before", ".after", ".regex"]
number_filters = [
    "year", "tmdb_year", "critic_rating", "audience_rating", "user_rating", "tmdb_vote_count", "tmdb_vote_average", "plays", "duration",
    "channels", "height", "width", "aspect", "versions", "stinger_rating"]
number_modifiers = ["", ".not", ".gt", ".gte", ".lt", ".lte"]
special_filters = [
    "history", "episodes", "seasons", "albums", "tracks", "original_language", "original_language.not",
    "tmdb_status", "tmdb_status.not", "tmdb_type", "tmdb_type.not"
]
all_filters = boolean_filters + special_filters + \
              [f"{f}{m}" for f in string_filters for m in string_modifiers] + \
              [f"{f}{m}" for f in tag_filters for m in tag_modifiers] + \
              [f"{f}{m}" for f in date_filters for m in date_modifiers] + \
              [f"{f}{m}" for f in number_filters for m in number_modifiers]
date_attributes = plex.date_attributes + ["first_episode_aired", "last_episode_aired", "last_episode_aired_or_never"]
year_attributes = plex.year_attributes + ["tmdb_year"]
number_attributes = plex.number_attributes + ["channels", "height", "width", "tmdb_vote_count"]
tag_attributes = plex.tag_attributes
string_attributes = plex.string_attributes + string_filters
float_attributes = plex.float_attributes + ["aspect", "tmdb_vote_average"]
boolean_attributes = plex.boolean_attributes + boolean_filters
smart_invalid = ["collection_order", "builder_level"]
smart_only = ["collection_filtering"]
smart_url_invalid = ["filters", "run_again", "sync_mode", "show_filtered", "show_missing", "save_report", "smart_label"] + radarr_details + sonarr_details
custom_sort_builders = [
    "plex_search", "plex_watchlist", "plex_pilots", "tmdb_list", "tmdb_popular", "tmdb_now_playing", "tmdb_top_rated",
    "tmdb_trending_daily", "tmdb_trending_weekly", "tmdb_discover", "reciperr_list", "trakt_chart", "trakt_userlist",
    "tvdb_list", "imdb_chart", "imdb_list", "imdb_award", "imdb_search", "imdb_watchlist", "stevenlu_popular", "anidb_popular",
    "tmdb_upcoming", "tmdb_airing_today", "tmdb_on_the_air", "trakt_list", "trakt_watchlist", "trakt_collection",
    "trakt_trending", "trakt_popular", "trakt_boxoffice", "trakt_collected_daily", "trakt_collected_weekly",
    "trakt_collected_monthly", "trakt_collected_yearly", "trakt_collected_all", "trakt_recommendations",
    "trakt_recommended_personal", "trakt_recommended_daily", "trakt_recommended_weekly", "trakt_recommended_monthly",
    "trakt_recommended_yearly", "trakt_recommended_all", "trakt_watched_daily", "trakt_watched_weekly",
    "trakt_watched_monthly", "trakt_watched_yearly", "trakt_watched_all",
    "tautulli_popular", "tautulli_watched", "mdblist_list", "letterboxd_list", "icheckmovies_list",
    "anilist_top_rated", "anilist_popular", "anilist_trending", "anilist_search", "anilist_userlist",
    "mal_all", "mal_airing", "mal_upcoming", "mal_tv", "mal_movie", "mal_ova", "mal_special", "mal_search",
    "mal_popular", "mal_favorite", "mal_suggested", "mal_userlist", "mal_season", "mal_genre", "mal_studio",
    "mojo_world", "mojo_domestic", "mojo_international", "mojo_record", "mojo_all_time", "mojo_never"
]
episode_parts_only = ["plex_pilots"]
overlay_only = ["overlay", "suppress_overlays"]
overlay_attributes = [
     "filters", "limit", "show_missing", "save_report", "missing_only_released", "minimum_items", "cache_builders", "tmdb_region", "default_percent"
] + all_builders + overlay_only
parts_collection_valid = [
     "filters", "plex_all", "plex_search", "trakt_list", "trakt_list_details", "collection_filtering", "collection_mode", "label", "visible_library", "limit",
     "visible_home", "visible_shared", "show_missing", "save_report", "missing_only_released", "server_preroll", "changes_webhooks",
     "item_lock_background", "item_lock_poster", "item_lock_title", "item_refresh", "item_refresh_delay", "imdb_list", "imdb_search",
     "cache_builders", "url_theme", "file_theme", "item_label", "default_percent", "non_item_remove_label"
] + episode_parts_only + summary_details + poster_details + background_details + string_details
playlist_attributes = [
    "filters", "name_mapping", "show_filtered", "show_missing", "save_report", "allowed_library_types", "run_definition",
    "missing_only_released", "only_filter_missing", "delete_below_minimum", "ignore_ids", "ignore_imdb_ids",
    "server_preroll", "changes_webhooks", "minimum_items", "cache_builders", "default_percent"
] + custom_sort_builders + summary_details + poster_details + radarr_details + sonarr_details
music_attributes = [
   "non_item_remove_label", "item_label", "collection_filtering", "item_lock_background", "item_lock_poster", "item_lock_title",
   "item_assets", "item_refresh", "item_refresh_delay", "plex_search", "plex_all", "filters"
] + details + summary_details + poster_details + background_details
