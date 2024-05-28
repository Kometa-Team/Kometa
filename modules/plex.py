import os, plexapi, re, time
from datetime import datetime, timedelta
from modules import builder, util
from modules.library import Library
from modules.poster import ImageData
from modules.request import parse_qs, quote_plus, urlparse
from modules.util import Failed
from PIL import Image
from plexapi import utils
from plexapi.audio import Artist, Track, Album
from plexapi.exceptions import BadRequest, NotFound, Unauthorized
from plexapi.collection import Collection
from plexapi.library import Role, FilterChoice
from plexapi.playlist import Playlist
from plexapi.server import PlexServer
from plexapi.video import Movie, Show, Season, Episode
from requests.exceptions import ConnectionError, ConnectTimeout
from retrying import retry
from xml.etree.ElementTree import ParseError

logger = util.logger

builders = ["plex_all", "plex_watchlist", "plex_pilots", "plex_collectionless", "plex_search"]
library_types = ["movie", "show", "artist"]
search_translation = {
    "episode_actor": "episode.actor",
    "episode_title": "episode.title",
    "network": "show.network",
    "edition": "editionTitle",
    "critic_rating": "rating",
    "audience_rating": "audienceRating",
    "episode_critic_rating": "episode.rating",
    "episode_audience_rating": "episode.audienceRating",
    "user_rating": "userRating",
    "episode_user_rating": "episode.userRating",
    "content_rating": "contentRating",
    "episode_year": "episode.year",
    "release": "originallyAvailableAt",
    "show_unmatched": "show.unmatched",
    "episode_unmatched": "episode.unmatched",
    "episode_duplicate": "episode.duplicate",
    "added": "addedAt",
    "episode_added": "episode.addedAt",
    "episode_air_date": "episode.originallyAvailableAt",
    "plays": "viewCount",
    "episode_plays": "episode.viewCount",
    "last_played": "lastViewedAt",
    "episode_last_played": "episode.lastViewedAt",
    "unplayed": "unwatched",
    "episode_unplayed": "episode.unwatched",
    "subtitle_language": "subtitleLanguage",
    "audio_language": "audioLanguage",
    "progress": "inProgress",
    "episode_progress": "episode.inProgress",
    "unplayed_episodes": "show.unwatchedLeaves",
    "season_collection": "season.collection",
    "episode_collection": "episode.collection",
    "season_label": "season.label",
    "episode_label": "episode.label",
    "artist_title": "artist.title",
    "artist_user_rating": "artist.userRating",
    "artist_genre": "artist.genre",
    "artist_collection": "artist.collection",
    "artist_country": "artist.country",
    "artist_mood": "artist.mood",
    "artist_style": "artist.style",
    "artist_added": "artist.addedAt",
    "artist_last_played": "artist.lastViewedAt",
    "artist_unmatched": "artist.unmatched",
    "artist_label": "artist.label",
    "album_title": "album.title",
    "album_year": "album.year",
    "album_decade": "album.decade",
    "album_genre": "album.genre",
    "album_plays": "album.viewCount",
    "album_last_played": "album.lastViewedAt",
    "album_user_rating": "album.userRating",
    "album_critic_rating": "album.rating",
    "album_record_label": "album.studio",
    "album_mood": "album.mood",
    "album_style": "album.style",
    "album_format": "album.format",
    "album_type": "album.subformat",
    "album_collection": "album.collection",
    "album_added": "album.addedAt",
    "album_released": "album.originallyAvailableAt",
    "album_unmatched": "album.unmatched",
    "album_source": "album.source",
    "album_label": "album.label",
    "track_mood": "track.mood",
    "track_title": "track.title",
    "track_plays": "track.viewCount",
    "track_last_played": "track.lastViewedAt",
    "track_skips": "track.skipCount",
    "track_last_skipped": "track.lastSkippedAt",
    "track_user_rating": "track.userRating",
    "track_last_rated": "track.lastRatedAt",
    "track_added": "track.addedAt",
    "track_trash": "track.trash",
    "track_source": "track.source",
    "track_label": "track.label"
}
show_translation = {
    "title": "show.title",
    "country": "show.country",
    "studio": "show.studio",
    "rating": "show.rating",
    "audienceRating": "show.audienceRating",
    "userRating": "show.userRating",
    "contentRating": "show.contentRating",
    "year": "show.year",
    "originallyAvailableAt": "show.originallyAvailableAt",
    "unmatched": "show.unmatched",
    "genre": "show.genre",
    "collection": "show.collection",
    "actor": "show.actor",
    "addedAt": "show.addedAt",
    "viewCount": "show.viewCount",
    "lastViewedAt": "show.lastViewedAt",
    "resolution": "episode.resolution",
    "hdr": "episode.hdr",
    "subtitleLanguage": "episode.subtitleLanguage",
    "audioLanguage": "episode.audioLanguage",
    "trash": "episode.trash",
    "label": "show.label",
}
get_tags_translation = {"episode.actor": "actor"}
modifier_translation = {
    "": "", ".not": "!", ".is": "%3D", ".isnot": "!%3D", ".gt": "%3E%3E", ".gte": "%3E", ".lt": "%3C%3C", ".lte": "%3C",
    ".before": "%3C%3C", ".after": "%3E%3E", ".begins": "%3C", ".ends": "%3E", ".regex": "", ".rated": ""
}
attribute_translation = {
    "aspect": "aspectRatio",
    "channels": "audioChannels",
    "audio_codec": "audioCodec",
    "audio_profile ": "audioProfile",
    "video_codec": "videoCodec",
    "video_profile": "videoProfile",
    "resolution": "videoResolution",
    "record_label": "studio",
    "similar_artist": "similar",
    "actor": "actors",
    "audience_rating": "audienceRating",
    "collection": "collections",
    "content_rating": "contentRating",
    "country": "countries",
    "critic_rating": "rating",
    "director": "directors",
    "genre": "genres",
    "label": "labels",
    "producer": "producers",
    "release": "originallyAvailableAt",
    "originally_available": "originallyAvailableAt",
    "added": "addedAt",
    "last_played": "lastViewedAt",
    "plays": "viewCount",
    "user_rating": "userRating",
    "writer": "writers",
    "mood": "moods",
    "style": "styles",
    "episode_number": "episodeNumber",
    "season_number": "seasonNumber",
    "original_title": "originalTitle",
    "edition": "editionTitle",
    "runtime": "duration",
    "season_title": "parentTitle",
    "episode_count": "leafCount",
    "versions": "media"
}
method_alias = {
    "actors": "actor", "role": "actor", "roles": "actor",
    "show_actor": "actor", "show_actors": "actor", "show_role": "actor", "show_roles": "actor",
    "collections": "collection", "plex_collection": "collection",
    "show_collections": "collection", "show_collection": "collection",
    "content_ratings": "content_rating", "contentRating": "content_rating", "contentRatings": "content_rating",
    "countries": "country",
    "decades": "decade",
    "directors": "director",
    "genres": "genre",
    "labels": "label",
    "collection_minimum": "minimum_items",
    "playlist_minimum": "minimum_items",
    "save_missing": "save_report",
    "rating": "critic_rating",
    "show_user_rating": "user_rating",
    "video_resolution": "resolution",
    "tmdb_trending": "tmdb_trending_daily",
    "play": "plays", "show_plays": "plays", "show_play": "plays", "episode_play": "episode_plays",
    "originally_available": "release", "episode_originally_available": "episode_air_date",
    "episode_release": "episode_air_date", "episode_released": "episode_air_date",
    "show_originally_available": "release", "show_release": "release", "show_air_date": "release",
    "released": "release", "show_released": "release", "max_age": "release",
    "studios": "studio",
    "networks": "network",
    "producers": "producer",
    "writers": "writer",
    "years": "year", "show_year": "year", "show_years": "year",
    "show_title": "title", "filter": "filters",
    "seasonyear": "year", "isadult": "adult", "startdate": "start", "enddate": "end", "averagescore": "score",
    "minimum_tag_percentage": "min_tag_percent", "minimumtagrank": "min_tag_percent", "minimum_tag_rank": "min_tag_percent",
    "anilist_tag": "anilist_search", "anilist_genre": "anilist_search", "anilist_season": "anilist_search",
    "mal_producer": "mal_studio", "mal_licensor": "mal_studio",
    "trakt_recommended": "trakt_recommended_weekly", "trakt_watched": "trakt_watched_weekly", "trakt_collected": "trakt_collected_weekly",
    "collection_changes_webhooks": "changes_webhooks",
    "radarr_add": "radarr_add_missing", "sonarr_add": "sonarr_add_missing",
    "trakt_recommended_personal": "trakt_recommendations",
    "collection_level": "builder_level", "overlay_level": "builder_level",
}
modifier_alias = {".greater": ".gt", ".less": ".lt"}
date_sub_mods = {"s": "Seconds", "m": "Minutes", "h": "Hours", "d": "Days", "w": "Weeks", "o": "Months", "y": "Years"}
album_sorting_options = {"default": -1, "newest": 0, "oldest": 1, "name": 2}
episode_sorting_options = {"default": -1, "oldest": 0, "newest": 1}
keep_episodes_options = {"all": 0, "5_latest": 5, "3_latest": 3, "latest": 1, "past_3": -3, "past_7": -7, "past_30": -30}
delete_episodes_options = {"never": 0, "day": 1, "week": 7, "month": 30, "refresh": 100}
season_display_options = {"default": -1, "show": 0, "hide": 1}
episode_ordering_options = {"default": None, "tmdb_aired": "tmdbAiring", "tvdb_aired": "aired", "tvdb_dvd": "dvd", "tvdb_absolute": "absolute"}
plex_languages = ["default", "ar-SA", "ca-ES", "cs-CZ", "da-DK", "de-DE", "el-GR", "en-AU", "en-CA", "en-GB", "en-US",
                  "es-ES", "es-MX", "et-EE", "fa-IR", "fi-FI", "fr-CA", "fr-FR", "he-IL", "hi-IN", "hu-HU", "id-ID",
                  "it-IT", "ja-JP", "ko-KR", "lt-LT", "lv-LV", "nb-NO", "nl-NL", "pl-PL", "pt-BR", "pt-PT", "ro-RO",
                  "ru-RU", "sk-SK", "sv-SE", "th-TH", "tr-TR", "uk-UA", "vi-VN", "zh-CN", "zh-HK", "zh-TW"]
metadata_language_options = {lang.lower(): lang for lang in plex_languages}
metadata_language_options["default"] = None
use_original_title_options = {"default": -1, "no": 0, "yes": 1}
credits_detection_options = {"default": -1, "disabled": 0}
audio_language_options = {lang.lower(): lang for lang in plex_languages}
audio_language_options["en"] = "en"
subtitle_language_options = {lang.lower(): lang for lang in plex_languages}
subtitle_language_options["en"] = "en"
subtitle_mode_options = {"default": -1, "manual": 0, "foreign": 1, "always": 2}
collection_order_options = ["release", "alpha", "custom"]
collection_filtering_options = ["user", "admin"]
collection_mode_options = {
    "default": "default", "hide": "hide",
    "hide_items": "hideItems", "hideitems": "hideItems",
    "show_items": "showItems", "showitems": "showItems"
}
builder_level_show_options = ["episode", "season"]
builder_level_music_options = ["album", "track"]
builder_level_options = builder_level_show_options + builder_level_music_options
collection_mode_keys = {-1: "default", 0: "hide", 1: "hideItems", 2: "showItems"}
collection_order_keys = {0: "release", 1: "alpha", 2: "custom"}
item_advance_keys = {
    "item_album_sorting": ("albumSort", album_sorting_options),
    "item_episode_sorting": ("episodeSort", episode_sorting_options),
    "item_keep_episodes": ("autoDeletionItemPolicyUnwatchedLibrary", keep_episodes_options),
    "item_delete_episodes": ("autoDeletionItemPolicyWatchedLibrary", delete_episodes_options),
    "item_season_display": ("flattenSeasons", season_display_options),
    "item_episode_ordering": ("showOrdering", episode_ordering_options),
    "item_metadata_language": ("languageOverride", metadata_language_options),
    "item_use_original_title": ("useOriginalTitle", use_original_title_options),
    "item_credits_detection": ("enableCreditsMarkerGeneration", credits_detection_options),
    "item_audio_language": ("audioLanguage", audio_language_options),
    "item_subtitle_language": ("subtitleLanguage", subtitle_language_options),
    "item_subtitle_mode": ("subtitleMode", subtitle_mode_options)
}
new_plex_agents = ["tv.plex.agents.movie", "tv.plex.agents.series"]
and_searches = [
    "title.and", "studio.and", "actor.and", "audio_language.and", "collection.and",
    "content_rating.and", "country.and",  "director.and", "genre.and", "label.and",
    "network.and", "producer.and", "subtitle_language.and", "writer.and"
]
or_searches = [
    "title", "studio", "actor", "audio_language", "collection", "content_rating",
    "country", "director", "genre", "label", "network", "producer", "subtitle_language",
    "writer", "decade", "resolution", "year", "episode_title", "episode_year"
]
movie_only_searches = [
    "director", "director.not", "producer", "producer.not", "writer", "writer.not",
    "decade", "duplicate", "unplayed", "progress",
    "duration.gt", "duration.gte", "duration.lt", "duration.lte"
    "edition", "edition.not", "edition.is", "edition.isnot", "edition.begins", "edition.ends"
]
show_only_searches = [
    "network", "network.not",
    "season_collection", "season_collection.not",
    "episode_collection", "episode_collection.not",
    "season_label", "season_label.not",
    "episode_label", "episode_label.not",
    "episode_title", "episode_title.not", "episode_title.is", "episode_title.isnot", "episode_title.begins", "episode_title.ends",
    "episode_added", "episode_added.not", "episode_added.before", "episode_added.after",
    "episode_air_date", "episode_air_date.not",
    "episode_air_date.before", "episode_air_date.after",
    "episode_last_played", "episode_last_played.not", "episode_last_played.before", "episode_last_played.after",
    "episode_plays.gt", "episode_plays.gte", "episode_plays.lt", "episode_plays.lte",
    "episode_user_rating.gt", "episode_user_rating.gte", "episode_user_rating.lt", "episode_user_rating.lte", "episode_user_rating.rated",
    "episode_critic_rating.gt", "episode_critic_rating.gte", "episode_critic_rating.lt", "episode_critic_rating.lte", "episode_critic_rating.rated",
    "episode_audience_rating.gt", "episode_audience_rating.gte", "episode_audience_rating.lt", "episode_audience_rating.lte", "episode_audience_rating.rated",
    "episode_year", "episode_year.not", "episode_year.gt", "episode_year.gte", "episode_year.lt", "episode_year.lte",
    "unplayed_episodes", "episode_unplayed", "episode_duplicate", "episode_progress", "episode_unmatched", "show_unmatched",
]
string_attributes = ["title", "studio", "edition", "episode_title", "artist_title", "album_title", "album_record_label", "track_title"]
string_modifiers = ["", ".not", ".is", ".isnot", ".begins", ".ends"]
boolean_attributes = [
    "hdr", "unmatched", "duplicate", "unplayed", "progress", "trash", "unplayed_episodes", "episode_unplayed",
    "episode_duplicate", "episode_progress", "episode_unmatched", "show_unmatched", "artist_unmatched", "album_unmatched", "track_trash"
]
tmdb_attributes = ["actor", "director", "producer", "writer"]
date_attributes = [
    "added", "episode_added", "release", "episode_air_date", "last_played", "episode_last_played",
    "artist_added", "artist_last_played", "album_last_played",
    "album_added", "album_released", "track_last_played", "track_last_skipped", "track_last_rated", "track_added"
]
date_modifiers = ["", ".not", ".before", ".after"]
year_attributes = ["decade", "year", "episode_year", "album_year", "album_decade"]
number_attributes = ["plays", "episode_plays", "album_plays", "track_plays", "track_skips"] + year_attributes
number_modifiers = [".gt", ".gte", ".lt", ".lte"]
float_attributes = [
    "user_rating", "episode_user_rating", "critic_rating", "episode_critic_rating", "audience_rating", "episode_audience_rating",
    "duration", "artist_user_rating", "album_user_rating", "album_critic_rating", "track_user_rating"
]
float_modifiers = number_modifiers + [".rated"]
search_display = {"added": "Date Added", "release": "Release Date", "hdr": "HDR", "progress": "In Progress", "episode_progress": "Episode In Progress"}
tag_attributes = [
    "actor", "episode_actor", "audio_language", "collection", "content_rating", "country", "director", "genre", "label", "season_label", "episode_label", "network",
    "producer", "resolution", "studio", "subtitle_language", "writer", "season_collection", "episode_collection", "edition",
    "artist_genre", "artist_collection", "artist_country", "artist_mood", "artist_label", "artist_style", "album_genre", "album_mood",
    "album_style", "album_format", "album_type", "album_collection", "album_source", "album_label", "track_mood", "track_source", "track_label"
]
tag_modifiers = ["", ".not", ".regex"]
no_not_mods = ["resolution", "decade", "album_decade"]
searches = boolean_attributes + \
               [f"{f}{m}" for f in string_attributes for m in string_modifiers] + \
               [f"{f}{m}" for f in tag_attributes + year_attributes for m in tag_modifiers if f not in no_not_mods or m != ".not"] + \
               [f"{f}{m}" for f in date_attributes for m in date_modifiers] + \
               [f"{f}{m}" for f in number_attributes for m in number_modifiers if f not in no_not_mods] + \
               [f"{f}{m}" for f in float_attributes for m in float_modifiers if f != "duration" or m != ".rated"]
music_searches = [a for a in searches if a.startswith(("artist", "album", "track"))]
movie_sorts = {
    "title.asc": "titleSort", "title.desc": "titleSort%3Adesc",
    "year.asc": "year", "year.desc": "year%3Adesc",
    "originally_available.asc": "originallyAvailableAt", "originally_available.desc": "originallyAvailableAt%3Adesc",
    "release.asc": "originallyAvailableAt", "release.desc": "originallyAvailableAt%3Adesc",
    "critic_rating.asc": "rating", "critic_rating.desc": "rating%3Adesc",
    "audience_rating.asc": "audienceRating", "audience_rating.desc": "audienceRating%3Adesc",
    "user_rating.asc": "userRating",  "user_rating.desc": "userRating%3Adesc",
    "content_rating.asc": "contentRating", "content_rating.desc": "contentRating%3Adesc",
    "duration.asc": "duration", "duration.desc": "duration%3Adesc",
    "progress.asc": "viewOffset", "progress.desc": "viewOffset%3Adesc",
    "plays.asc": "viewCount", "plays.desc": "viewCount%3Adesc",
    "added.asc": "addedAt", "added.desc": "addedAt%3Adesc",
    "viewed.asc": "lastViewedAt", "viewed.desc": "lastViewedAt%3Adesc",
    "resolution.asc": "mediaHeight", "resolution.desc": "mediaHeight%3Adesc",
    "bitrate.asc": "mediaBitrate", "bitrate.desc": "mediaBitrate%3Adesc",
    "random": "random"
}
show_sorts = {
    "title.asc": "titleSort", "title.desc": "titleSort%3Adesc",
    "year.asc": "year", "year.desc": "year%3Adesc",
    "originally_available.asc": "originallyAvailableAt", "originally_available.desc": "originallyAvailableAt%3Adesc",
    "episode_originally_available.asc": "episode.originallyAvailableAt", "episode_originally_available.desc": "episode.originallyAvailableAt%3Adesc",
    "release.asc": "originallyAvailableAt", "release.desc": "originallyAvailableAt%3Adesc",
    "episode_release.asc": "episode.originallyAvailableAt", "episode_release.desc": "episode.originallyAvailableAt%3Adesc",
    "critic_rating.asc": "rating", "critic_rating.desc": "rating%3Adesc",
    "audience_rating.asc": "audienceRating", "audience_rating.desc": "audienceRating%3Adesc",
    "user_rating.asc": "userRating",  "user_rating.desc": "userRating%3Adesc",
    "content_rating.asc": "contentRating", "content_rating.desc": "contentRating%3Adesc",
    "unplayed.asc": "unviewedLeafCount", "unplayed.desc": "unviewedLeafCount%3Adesc",
    "episode_added.asc": "episode.addedAt", "episode_added.desc": "episode.addedAt%3Adesc",
    "added.asc": "addedAt", "added.desc": "addedAt%3Adesc",
    "viewed.asc": "lastViewedAt", "viewed.desc": "lastViewedAt%3Adesc",
    "random": "random"
}
season_sorts = {
    "season.asc": "season.index%2Cseason.titleSort", "season.desc": "season.index%3Adesc%2Cseason.titleSort",
    "show.asc": "show.titleSort%2Cindex", "show.desc": "show.titleSort%3Adesc%2Cindex",
    "user_rating.asc": "userRating",  "user_rating.desc": "userRating%3Adesc",
    "added.asc": "addedAt", "added.desc": "addedAt%3Adesc",
    "random": "random"
}
episode_sorts = {
    "title.asc": "titleSort", "title.desc": "titleSort%3Adesc",
    "show.asc": "show.titleSort%2Cseason.index%3AnullsLast%2Cepisode.index%3AnullsLast%2Cepisode.originallyAvailableAt%3AnullsLast%2Cepisode.titleSort%2Cepisode.id",
    "show.desc": "show.titleSort%3Adesc%2Cseason.index%3AnullsLast%2Cepisode.index%3AnullsLast%2Cepisode.originallyAvailableAt%3AnullsLast%2Cepisode.titleSort%2Cepisode.id",
    "year.asc": "year", "year.desc": "year%3Adesc",
    "originally_available.asc": "originallyAvailableAt", "originally_available.desc": "originallyAvailableAt%3Adesc",
    "episode_originally_available.asc": "episode.originallyAvailableAt", "episode_originally_available.desc": "episode.originallyAvailableAt%3Adesc",
    "release.asc": "originallyAvailableAt", "release.desc": "originallyAvailableAt%3Adesc",
    "episode_release.asc": "episode.originallyAvailableAt", "episode_release.desc": "episode.originallyAvailableAt%3Adesc",
    "critic_rating.asc": "rating", "critic_rating.desc": "rating%3Adesc",
    "audience_rating.asc": "audienceRating", "audience_rating.desc": "audienceRating%3Adesc",
    "user_rating.asc": "userRating",  "user_rating.desc": "userRating%3Adesc",
    "duration.asc": "duration", "duration.desc": "duration%3Adesc",
    "progress.asc": "viewOffset", "progress.desc": "viewOffset%3Adesc",
    "plays.asc": "viewCount", "plays.desc": "viewCount%3Adesc",
    "added.asc": "addedAt", "added.desc": "addedAt%3Adesc",
    "viewed.asc": "lastViewedAt", "viewed.desc": "lastViewedAt%3Adesc",
    "resolution.asc": "mediaHeight", "resolution.desc": "mediaHeight%3Adesc",
    "bitrate.asc": "mediaBitrate", "bitrate.desc": "mediaBitrate%3Adesc",
    "random": "random"
}
artist_sorts = {
    "title.asc": "titleSort", "title.desc": "titleSort%3Adesc",
    "user_rating.asc": "userRating",  "user_rating.desc": "userRating%3Adesc",
    "added.asc": "addedAt", "added.desc": "addedAt%3Adesc",
    "played.asc": "lastViewedAt", "played.desc": "lastViewedAt%3Adesc",
    "plays.asc": "viewCount", "plays.desc": "viewCount%3Adesc",
    "random": "random"
}
album_sorts = {
    "title.asc": "titleSort", "title.desc": "titleSort%3Adesc",
    "album_artist.asc": "artist.titleSort%2Calbum.titleSort%2Calbum.index%2Calbum.id%2Calbum.originallyAvailableAt",
    "album_artist.desc": "artist.titleSort%3Adesc%2Calbum.titleSort%2Calbum.index%2Calbum.id%2Calbum.originallyAvailableAt",
    "year.asc": "year", "year.desc": "year%3Adesc",
    "originally_available.asc": "originallyAvailableAt", "originally_available.desc": "originallyAvailableAt%3Adesc",
    "release.asc": "originallyAvailableAt", "release.desc": "originallyAvailableAt%3Adesc",
    "critic_rating.asc": "rating", "critic_rating.desc": "rating%3Adesc",
    "user_rating.asc": "userRating",  "user_rating.desc": "userRating%3Adesc",
    "added.asc": "addedAt", "added.desc": "addedAt%3Adesc",
    "played.asc": "lastViewedAt", "played.desc": "lastViewedAt%3Adesc",
    "plays.asc": "viewCount", "plays.desc": "viewCount%3Adesc",
    "random": "random"
}
track_sorts = {
    "title.asc": "titleSort", "title.desc": "titleSort%3Adesc",
    "album_artist.asc": "artist.titleSort%2Calbum.titleSort%2Calbum.year%2Ctrack.absoluteIndex%2Ctrack.index%2Ctrack.titleSort%2Ctrack.id",
    "album_artist.desc": "artist.titleSort%3Adesc%2Calbum.titleSort%2Calbum.year%2Ctrack.absoluteIndex%2Ctrack.index%2Ctrack.titleSort%2Ctrack.id",
    "artist.asc": "originalTitle", "artist.desc": "originalTitle%3Adesc",
    "album.asc": "album.titleSort", "album.desc": "album.titleSort%3Adesc",
    "user_rating.asc": "userRating",  "user_rating.desc": "userRating%3Adesc",
    "duration.asc": "duration", "duration.desc": "duration%3Adesc",
    "plays.asc": "viewCount", "plays.desc": "viewCount%3Adesc",
    "added.asc": "addedAt", "added.desc": "addedAt%3Adesc",
    "played.asc": "lastViewedAt", "played.desc": "lastViewedAt%3Adesc",
    "rated.asc": "lastRatedAt", "rated.desc": "lastRatedAt%3Adesc",
    "popularity.asc": "ratingCount", "popularity.desc": "ratingCount%3Adesc",
    "bitrate.asc": "mediaBitrate", "bitrate.desc": "mediaBitrate%3Adesc",
    "random": "random"
}
sort_types = {
    "movie": ("title.asc", 1, movie_sorts),
    "show": ("title.asc", 2, show_sorts),
    "season": ("season.asc", 3, season_sorts),
    "episode": ("title.asc", 4, episode_sorts),
    "artist": ("title.asc", 8, artist_sorts),
    "album": ("title.asc", 9, album_sorts),
    "track": ("title.asc", 10, track_sorts)
}
watchlist_sorts = {
    "added.asc": "watchlistedAt:asc", "added.desc": "watchlistedAt:desc",
    "title.asc": "titleSort:asc", "title.desc": "titleSort:desc",
    "release.asc": "originallyAvailableAt:asc", "release.desc": "originallyAvailableAt:desc",
    "critic_rating.asc": "rating:asc", "critic_rating.desc": "rating:desc",
}

class Plex(Library):
    def __init__(self, config, params):
        super().__init__(config, params)
        self.plex = params["plex"]
        self.url = self.plex["url"]
        plex_session = self.config.Requests.session
        if self.plex["verify_ssl"] is False and self.config.Requests.global_ssl is True:
            logger.debug("Overriding verify_ssl to False for Plex connection")
            plex_session = self.config.Requests.create_session(verify_ssl=False)
        if self.plex["verify_ssl"] is True and self.config.Requests.global_ssl is False:
            logger.debug("Overriding verify_ssl to True for Plex connection")
            plex_session = self.config.Requests.create_session()
        self.token = self.plex["token"]
        self.timeout = self.plex["timeout"]
        logger.secret(self.url)
        logger.secret(self.token)
        try:
            self.PlexServer = PlexServer(baseurl=self.url, token=self.token, session=plex_session, timeout=self.timeout)
            plexapi.server.TIMEOUT = self.timeout
            os.environ["PLEXAPI_PLEXAPI_TIMEOUT"] = str(self.timeout)
            logger.info(f"Connected to server {self.PlexServer.friendlyName} version {self.PlexServer.version}")
            logger.info(f"Running on {self.PlexServer.platform} version {self.PlexServer.platformVersion}")
            srv_settings = self.PlexServer.settings
            try:
                db_cache = srv_settings.get("DatabaseCacheSize")
                logger.info(f"Plex DB cache setting: {db_cache.value} MB")
                if self.plex["db_cache"] and self.plex["db_cache"] != db_cache.value:
                    db_cache.set(self.plex["db_cache"])
                    self.PlexServer.settings.save()
                    logger.info(f"Plex DB Cache updated to {self.plex['db_cache']} MB")
            except NotFound:
                logger.info(f"Plex DB cache setting: Unknown")
            try:
                chl_num = srv_settings.get("butlerUpdateChannel").value
                if chl_num == "16":
                    uc_str = f"Public update channel."
                elif chl_num == "8":
                    uc_str = f"PlexPass update channel."
                else:
                    uc_str = f"Unknown update channel: {chl_num}."
            except NotFound:
                uc_str = f"Unknown update channel."
            logger.info(f"PlexPass: {self.PlexServer.myPlexSubscription} on {uc_str}")
            try:
                logger.info(f"Scheduled maintenance running between {srv_settings.get('butlerStartHour').value}:00 and {srv_settings.get('butlerEndHour').value}:00")
            except NotFound:
                logger.info("Scheduled maintenance times could not be found")
        except Unauthorized:
            logger.info(f"Plex Error: Plex connection attempt returned 'Unauthorized'")
            raise Failed("Plex Error: Plex token is invalid")
        except ConnectTimeout:
            raise Failed(f"Plex Error: Plex did not respond within the {self.timeout}-second timeout.")
        except ValueError as e:
            logger.info(f"Plex Error: Plex connection attempt returned 'ValueError'")
            logger.stacktrace()
            raise Failed(f"Plex Error: {e}")
        except (ConnectionError, ParseError):
            logger.info(f"Plex Error: Plex connection attempt returned 'ConnectionError' or 'ParseError'")
            logger.stacktrace()
            raise Failed("Plex Error: Plex URL is probably invalid")
        self.Plex = None
        library_names = []
        for s in self.PlexServer.library.sections():
            library_names.append(s.title)
            if s.title == params["name"]:
                self.Plex = s
                break
        if not self.Plex:
            raise Failed(f"Plex Error: Plex Library '{params['name']}' not found. Options: {library_names}")
        if self.Plex.type not in library_types:
            raise Failed(f"Plex Error: Plex Library must be a Movies, TV Shows, or Music library")
        if not self.Plex.allowSync:
            raise Failed("Plex Error: Plex Token is read only. Please get a new token")

        self.type = self.Plex.type.capitalize()
        self.plex_pass = self.PlexServer.myPlexSubscription
        self._users = []
        self._all_items = []
        self._account = None
        self.agent = self.Plex.agent
        self.scanner = self.Plex.scanner
        source_setting = next((s for s in self.Plex.settings() if s.id in ["ratingsSource"]), None)
        self.ratings_source = source_setting.enumValues[source_setting.value] if source_setting else "N/A"
        self.is_movie = self.type == "Movie"
        self.is_show = self.type == "Show"
        self.is_music = self.type == "Artist"
        self.is_other = self.agent == "com.plexapp.agents.none"
        if self.is_other and self.type == "Movie":
            self.type = "Video"
        if not self.is_music and self.update_blank_track_titles:
            self.update_blank_track_titles = False
            logger.error(f"update_blank_track_titles library operation only works with music libraries")
        logger.info(f"Connected to library {params['name']}")
        logger.info(f"Type: {self.type}")
        logger.info(f"Agent: {self.agent}")
        logger.info(f"Scanner: {self.scanner}")
        logger.info(f"Ratings Source: {self.ratings_source}")

    def notify(self, text, collection=None, critical=True):
        self.config.notify(text, server=self.PlexServer.friendlyName, library=self.name, collection=collection, critical=critical)

    def notify_delete(self, message):
        self.config.notify_delete(message, server=self.PlexServer.friendlyName, library=self.name)

    def set_server_preroll(self, preroll):
        self.PlexServer.settings.get('cinemaTrailersPrerollID').set(preroll)
        self.PlexServer.settings.save()

    def get_all_collections(self, label=None):
        args = "?type=18"
        if label:
            label_id = next((c.key for c in self.get_tags("label") if c.title == label), None) # noqa
            if label_id:
                args = f"{args}&label={label_id}"
            else:
                return []
        return self.fetchItems(args)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def search(self, title=None, sort=None, maxresults=None, libtype=None, **kwargs):
        return self.Plex.search(title=title, sort=sort, maxresults=maxresults, libtype=libtype, **kwargs)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def exact_search(self, title, libtype=None, year=None):
        terms = {"title=": title}
        if year:
            terms["year"] = year
        return self.Plex.search(libtype=libtype, **terms)

    def fetch_item(self, item):
        if isinstance(item, (Movie, Show, Season, Episode, Artist, Album, Track)):
            return self.reload(item)
        key = int(item)
        if key in self.cached_items:
            return self.reload(self.cached_items[key][0])
        try:
            current = self.fetchItem(key)
            if isinstance(current, (Movie, Show, Season, Episode, Artist, Album, Track)):
                return self.reload(current)
        except (BadRequest, NotFound) as e:
            logger.trace(e)
        raise Failed(f"Plex Error: Item {item} not found")

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def fetchItem(self, data):
        return self.PlexServer.fetchItem(data)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def fetchItems(self, uri_args):
        return self.Plex.fetchItems(f"/library/sections/{self.Plex.key}/all{'' if uri_args is None else uri_args}")

    def get_all(self, builder_level=None, load=False):
        if load and builder_level in [None, "show", "artist", "movie"]:
            self._all_items = []
        if self._all_items and builder_level in [None, "show", "artist", "movie"]:
            return self._all_items
        builder_type = builder_level if builder_level else self.Plex.TYPE
        if not builder_level:
            builder_level = self.type
        logger.info(f"Loading All {builder_level.capitalize()}s from Library: {self.name}")
        key = f"/library/sections/{self.Plex.key}/all?includeGuids=1&type={utils.searchType(builder_type)}"
        container_start = 0
        container_size = plexapi.X_PLEX_CONTAINER_SIZE
        results = []
        total_size = 1
        while total_size > len(results) and container_start <= total_size:
            data = self.Plex._server.query(key, headers={"X-Plex-Container-Start": str(container_start), "X-Plex-Container-Size": str(container_size)})
            subresults = self.Plex.findItems(data, initpath=key)
            total_size = utils.cast(int, data.attrib.get('totalSize') or data.attrib.get('size')) or len(subresults)

            librarySectionID = utils.cast(int, data.attrib.get('librarySectionID'))
            if librarySectionID:
                for item in subresults:
                    item.librarySectionID = librarySectionID

            results.extend(subresults)
            container_start += container_size
            logger.ghost(f"Loaded: {total_size if container_start > total_size else container_start}/{total_size}")

        logger.info(f"Loaded {total_size} {builder_level.capitalize()}s")
        if builder_level in [None, "show", "artist", "movie"]:
            self._all_items = results
        return results

    def upload_theme(self, collection, url=None, filepath=None):
        key = f"/library/metadata/{collection.ratingKey}/themes"
        if url:
            self.PlexServer.query(f"{key}?url={quote_plus(url)}", method=self.PlexServer._session.post)
        elif filepath:
            self.PlexServer.query(key, method=self.PlexServer._session.post, data=open(filepath, 'rb').read())

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def create_playlist(self, name, items):
        return self.PlexServer.createPlaylist(name, items=items)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def moveItem(self, obj, item, after):
        try:
            obj.moveItem(item, after=after)
        except (BadRequest, NotFound, Unauthorized) as e:
            logger.error(e)
            raise Failed("Move Failed")

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def query(self, method):
        return method()

    def delete(self, obj):
        try:
            return self.query(obj.delete)
        except Exception:
            logger.stacktrace()
            raise Failed(f"Plex Error: Failed to delete {obj.title}")

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def query_data(self, method, data):
        return method(data)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def tag_edit(self, item, attribute, data, locked=True, remove=False):
        return item.editTags(attribute, data, locked=locked, remove=remove)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def query_collection(self, item, collection, locked=True, add=True):
        if add:
            item.addCollection(collection, locked=locked)
        else:
            item.removeCollection(collection, locked=locked)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def collection_mode_query(self, collection, data):
        collection.modeUpdate(mode=data)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def collection_order_query(self, collection, data):
        collection.sortUpdate(sort=data)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def item_labels(self, item):
        try:
            return item.labels
        except BadRequest:
            raise Failed(f"Item: {item.title} Labels failed to load")

    def find_poster_url(self, item):
        if isinstance(item, Movie):
            if item.ratingKey in self.movie_rating_key_map:
                return self.config.TMDb.get_movie(self.movie_rating_key_map[item.ratingKey]).poster_url
        elif isinstance(item, (Show, Season, Episode)):
            check_key = item.ratingKey if isinstance(item, Show) else item.show().ratingKey
            if check_key in self.show_rating_key_map:
                tmdb_id = self.config.Convert.tvdb_to_tmdb(self.show_rating_key_map[check_key])
                if isinstance(item, Show) and item.ratingKey in self.show_rating_key_map:
                    return self.config.TMDb.get_show(tmdb_id).poster_url
                elif isinstance(item, Season):
                    return self.config.TMDb.get_season(tmdb_id, item.seasonNumber).poster_url
                elif isinstance(item, Episode):
                    return self.config.TMDb.get_episode(tmdb_id, item.seasonNumber, item.episodeNumber).still_url

    def item_posters(self, item, providers=None):
        if providers is None:
            providers = ["plex", "tmdb"]
        image_url = None
        for provider in providers:
            if provider == "plex":
                for poster in item.posters():
                    if poster.key.startswith("/"):
                        image_url = f"{self.url}{poster.key}&X-Plex-Token={self.token}"
                        if poster.ratingKey.startswith("upload"):
                            try:
                                self.check_image_for_overlay(image_url, os.path.join(self.overlay_backup, "temp"), remove=True)
                            except Failed as e:
                                logger.trace(f"Plex Error: {e}")
                                continue
                    else:
                        image_url = poster.key
                    break
            if provider == "tmdb":
                try:
                    image_url = self.find_poster_url(item)
                except Failed as e:
                    logger.trace(e)
                    continue
            if image_url:
                break
        if not image_url and "plex" in providers and isinstance(item, Season):
            for poster in item.show().posters():
                if poster.key.startswith("/"):
                    image_url = f"{self.url}{poster.key}&X-Plex-Token={self.token}"
                    if poster.ratingKey.startswith("upload"):
                        try:
                            self.check_image_for_overlay(image_url, os.path.join(self.overlay_backup, "temp"), remove=True)
                        except Failed as e:
                            logger.trace(f"Plex Error: {e}")
                            continue
                else:
                    image_url = poster.key
                break
        if not image_url:
            raise Failed("Overlay Error: No Poster found to reset")
        return image_url

    def item_reload(self, item):
        item.reload(checkFiles=False, includeAllConcerts=False, includeBandwidths=False, includeChapters=False,
                    includeChildren=False, includeConcerts=False, includeExternalMedia=False, includeExtras=False,
                    includeFields=False, includeGeolocation=False, includeLoudnessRamps=False, includeMarkers=False,
                    includeOnDeck=False, includePopularLeaves=False, includeRelated=False, includeRelatedCount=0,
                    includeReviews=False, includeStations=False)
        item._autoReload = False
        return item

    def load_from_cache(self, rating_key):
        if rating_key in self.cached_items:
            item, _ = self.cached_items[rating_key]
            return item

    def load_list_from_cache(self, rating_keys):
        item_list = []
        for rating_key in rating_keys:
            item = self.load_from_cache(rating_key)
            if item:
                item_list.append(item)
        return item_list

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def reload(self, item, force=False):
        is_full = False
        if not force and item.ratingKey in self.cached_items:
            item, is_full = self.cached_items[item.ratingKey]
        try:
            if not is_full or force:
                self.item_reload(item)
                self.cached_items[item.ratingKey] = (item, True)
        except (BadRequest, NotFound) as e:
            logger.stacktrace()
            raise Failed(f"Item Failed to Load: {e}")
        return item

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def edit_query(self, item, edits, advanced=False):
        if advanced:
            item.editAdvanced(**edits)
        else:
            item.edit(**edits)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def _upload_image(self, item, image):
        try:
            if image.is_url and "theposterdb.com" in image.location:
                now = datetime.now()
                if self.config.tpdb_timer is not None:
                    while self.config.tpdb_timer + timedelta(seconds=6) > now:
                        time.sleep(1)
                        now = datetime.now()
                self.config.tpdb_timer = now
            if image.is_poster and image.is_url:
                item.uploadPoster(url=image.location)
            elif image.is_poster:
                item.uploadPoster(filepath=image.location)
            elif image.is_url:
                item.uploadArt(url=image.location)
            else:
                item.uploadArt(filepath=image.location)
            self.reload(item, force=True)
        except BadRequest as e:
            item.refresh()
            raise Failed(e)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def upload_poster(self, item, image, url=False):
        if url:
            item.uploadPoster(url=image)
        else:
            item.uploadPoster(filepath=image)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def upload_background(self, item, image, url=False):
        if url:
            item.uploadArt(url=image)
        else:
            item.uploadArt(filepath=image)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def get_actor_id(self, name):
        results = self.Plex.hubSearch(name)
        for result in results:
            if isinstance(result, Role) and result.librarySectionID == self.Plex.key and result.tag == name:
                return result.id

    def get_search_choices(self, search_name, title=True, name_pairs=False):
        final_search = search_translation[search_name] if search_name in search_translation else search_name
        final_search = show_translation[final_search] if self.is_show and final_search in show_translation else final_search
        final_search = get_tags_translation[final_search] if final_search in get_tags_translation else final_search
        try:
            names = []
            choices = {}
            use_title = title and final_search not in ["contentRating", "audioLanguage", "subtitleLanguage", "resolution"]
            for choice in self.get_tags(final_search):
                if choice.title not in names:
                    names.append((choice.title, choice.key) if name_pairs else choice.title)
                choices[choice.title] = choice.title if use_title else choice.key
                choices[choice.key] = choice.title if use_title else choice.key
                choices[choice.title.lower()] = choice.title if use_title else choice.key
                choices[choice.key.lower()] = choice.title if use_title else choice.key
            return choices, names
        except NotFound:
            logger.debug(f"Search Attribute: {final_search}")
            raise Failed(f"Plex Error: plex_search attribute: {search_name} not supported")

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def get_tags(self, tag):
        if isinstance(tag, str):
            match = re.match(r'(?:([a-zA-Z]*)\.)?([a-zA-Z]+)', tag)
            if not match:
                raise BadRequest(f'Invalid filter field: {tag}')
            _libtype, tag = match.groups()
            libtype = _libtype or self.Plex.TYPE
            try:
                tag = next(f for f in self.Plex.listFilters(libtype) if f.filter == tag)
            except StopIteration:
                available_filters = [f.filter for f in self.Plex.listFilters(libtype)]
                raise NotFound(f'Unknown filter field "{tag}" for libtype "{libtype}". '
                               f'Available filters: {available_filters}') from None
        items = self.Plex.findItems(self.Plex._server.query(tag.key), FilterChoice)
        if tag.key.endswith("/collection?type=4"):
            keys = [k.key for k in items]
            keys.extend([k.key for k in self.Plex.findItems(self.Plex._server.query(f"{tag.key[:-1]}3"), FilterChoice)])
            items = [i for i in self.Plex.findItems(self.Plex._server.query(tag.key[:-7]), FilterChoice) if i.key not in keys]
        return items

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def _query(self, key, post=False, put=False):
        if post:                method = self.Plex._server._session.post
        elif put:               method = self.Plex._server._session.put
        else:                   method = None
        return self.Plex._server.query(key, method=method)

    @property
    def users(self):
        if not self._users:
            users = []
            for user in self.account.users():
                if self.PlexServer.machineIdentifier in [s.machineIdentifier for s in user.servers]:
                    users.append(user.title)
            self._users = users
        return self._users

    def delete_user_playlist(self, title, user):
        try:
            self.delete(self.PlexServer.switchUser(user).playlist(title))
        except NotFound as e:
            raise Failed(e)

    @property
    def account(self):
        if self._account is None:
            self._account = self.PlexServer.myPlexAccount()
        return self._account

    def playlist_report(self):
        playlists = {}
        def scan_user(server, username):
            try:
                for playlist in server.playlists():
                    if isinstance(playlist, Playlist):
                        if playlist.title not in playlists:
                            playlists[playlist.title] = []
                        playlists[playlist.title].append(username)
            except ConnectionError:
                pass
        scan_user(self.PlexServer, self.account.title)
        for user in self.users:
            scan_user(self.PlexServer.switchUser(user), user)
        return playlists

    def manage_recommendations(self):
        return [(r.title, r._data.attrib.get('identifier'), r._data.attrib.get('promotedToRecommended'),
                 r._data.attrib.get('promotedToOwnHome'), r._data.attrib.get('promotedToSharedHome'))
                for r in self.Plex.fetchItems(f"/hubs/sections/{self.Plex.key}/manage")]

    def alter_collection(self, items, collection, smart_label_collection=False, add=True):
        maintain_status = True
        locked_items = []
        unlocked_items = []
        if not smart_label_collection and maintain_status and self.agent in ["tv.plex.agents.movie", "tv.plex.agents.series"]:
            for item in items:
                item = self.reload(item)
                if next((f for f in item.fields if f.name == "collection"), None) is not None:
                    locked_items.append(item)
                else:
                    unlocked_items.append(item)
        else:
            locked_items = items

        for _items, locked in [(locked_items, True), (unlocked_items, False)]:
            if _items:
                self.Plex.batchMultiEdits(_items)
                if smart_label_collection:
                    self.query_data(self.Plex.addLabel if add else self.Plex.removeLabel, collection)
                elif add:
                    self.Plex.addCollection(collection, locked=locked)
                else:
                    self.Plex.removeCollection(collection, locked=locked)
                self.Plex.saveMultiEdits()

    def move_item(self, collection, item, after=None):
        key = f"{collection.key}/items/{item}/move"
        if after:
            key += f"?after={after}"
        self._query(key, put=True)

    def smart_label_check(self, label):
        labels = [la.title for la in self.get_tags("label")] # noqa
        if label in labels:
            return True
        logger.trace(f"Label not found in Plex. Options: {labels}")
        return False

    def test_smart_filter(self, uri_args):
        logger.debug(f"Smart Collection Test: {uri_args}")
        test_items = self.fetchItems(uri_args)
        if len(test_items) < 1:
            raise Failed(f"Plex Error: No items for smart filter: {uri_args}")

    def create_smart_collection(self, title, smart_type, uri_args, ignore_blank_results):
        if not ignore_blank_results:
            self.test_smart_filter(uri_args)
        args = {
            "type": smart_type,
            "title": title,
            "smart": 1,
            "sectionId": self.Plex.key,
            "uri": self.build_smart_filter(uri_args)
        }
        self._query(f"/library/collections{utils.joinArgs(args)}", post=True)

    def create_blank_collection(self, title):
        args = {
            "type": 1 if self.is_movie else 2 if self.is_show else 8,
            "title": title,
            "smart": 0,
            "sectionId": self.Plex.key,
            "uri": f"{self.PlexServer._uriRoot()}/library/metadata"
        }
        self._query(f"/library/collections{utils.joinArgs(args)}", post=True)

    def get_smart_filter_from_uri(self, uri):
        smart_filter = parse_qs(urlparse(uri.replace("/#!/", "/")).query)["key"][0] # noqa
        args = smart_filter[smart_filter.index("?"):]
        return self.build_smart_filter(args), int(args[args.index("type=") + 5:args.index("type=") + 6])

    def build_smart_filter(self, uri_args):
        return f"{self.PlexServer._uriRoot()}/library/sections/{self.Plex.key}/all{uri_args}"

    def update_smart_collection(self, collection, uri_args):
        self.test_smart_filter(uri_args)
        self._query(f"/library/collections/{collection.ratingKey}/items{utils.joinArgs({'uri': self.build_smart_filter(uri_args)})}", put=True)

    def smart_filter(self, collection):
        smart_filter = self.get_collection(collection).content
        return smart_filter[smart_filter.index("?"):]

    def collection_visibility(self, collection):
        try:
            attrs = self._query(f"/hubs/sections/{self.Plex.key}/manage?metadataItemId={collection.ratingKey}")[0].attrib
            return {
                "library": utils.cast(bool, attrs.get("promotedToRecommended", "0")),
                "home": utils.cast(bool, attrs.get("promotedToOwnHome", "0")),
                "shared": utils.cast(bool, attrs.get("promotedToSharedHome", "0"))
            }
        except IndexError:
            return {"library": False, "home": False, "shared": False}

    def collection_visibility_update(self, collection, visibility=None, library=None, home=None, shared=None):
        if visibility is None:
            visibility = self.collection_visibility(collection)
        key = f"/hubs/sections/{self.Plex.key}/manage?metadataItemId={collection.ratingKey}"
        key += f"&promotedToRecommended={1 if (library is None and visibility['library']) or library else 0}"
        key += f"&promotedToOwnHome={1 if (home is None and visibility['home']) or home else 0}"
        key += f"&promotedToSharedHome={1 if (shared is None and visibility['shared']) or shared else 0}"
        self._query(key, post=True)

    def get_playlist(self, title):
        try:
            return self.PlexServer.playlist(title)
        except NotFound:
            raise Failed(f"Plex Error: Playlist {title} not found")

    def get_playlist_from_users(self, playlist_title):
        for user in self.users:
            try:
                for playlist in self.PlexServer.switchUser(user).playlists():
                    if isinstance(playlist, Playlist) and playlist.title == playlist_title:
                        return playlist
            except ConnectionError:
                pass
        raise Failed(f"Plex Error: Playlist {playlist_title} not found")

    def get_collection(self, data, force_search=False, debug=True):
        if isinstance(data, Collection):
            return data
        elif isinstance(data, int) and not force_search:
            return self.fetchItem(data)
        else:
            cols = self.search(title=str(data), libtype="collection")
            for d in cols:
                if d.title == data:
                    return d
            if debug:
                logger.debug("")
                for d in cols:
                    logger.debug(f"Found: {d.title}")
                logger.debug(f"Looking for: {data}")
        raise Failed(f"Plex Error: Collection {data} not found")

    def validate_collections(self, collections):
        valid_collections = []
        for collection in collections:
            try:
                valid_collections.append(self.get_collection(collection))
            except Failed as e:
                logger.error(e)
        if len(valid_collections) == 0:
            raise Failed(f"Collection Error: No valid Plex Collections in {collections}")
        return valid_collections

    def get_watchlist(self, sort=None, is_playlist=False):
        if is_playlist:
            libtype = None
        elif self.is_movie:
            libtype = "movie"
        else:
            libtype = "show"
        watchlist = self.account.watchlist(sort=watchlist_sorts[sort], libtype=libtype)
        ids = []
        for item in watchlist:
            tmdb_id = []
            tvdb_id = []
            imdb_id = []
            if self.config.Cache:
                cache_id, _, media_type, _ = self.config.Cache.query_guid_map(item.guid)
                if cache_id:
                    ids.extend([(t_id, "tmdb" if "movie" in media_type else "tvdb") for t_id in cache_id])
                    continue
            try:
                fin = False
                for guid_tag in item.guids:
                    url_parsed = urlparse(guid_tag.id)
                    if url_parsed.scheme == "tvdb":
                        if isinstance(item, Show):
                            ids.append((int(url_parsed.netloc), "tvdb"))
                            fin = True
                    elif url_parsed.scheme == "imdb":
                        imdb_id.append(url_parsed.netloc)
                    elif url_parsed.scheme == "tmdb":
                        if isinstance(item, Movie):
                            ids.append((int(url_parsed.netloc), "tmdb"))
                            fin = True
                        tmdb_id.append(int(url_parsed.netloc))
                    if fin:
                        break
                if fin:
                    continue
            except ConnectionError:
                continue
            if imdb_id and not tmdb_id:
                for imdb in imdb_id:
                    tmdb, tmdb_type = self.config.Convert.imdb_to_tmdb(imdb)
                    if tmdb:
                        tmdb_id.append(tmdb)
            if tmdb_id and isinstance(item, Show) and not tvdb_id:
                for tmdb in tmdb_id:
                    tvdb = self.config.Convert.tmdb_to_tvdb(tmdb)
                    if tvdb:
                        tvdb_id.append(tvdb)
            if isinstance(item, Show) and tvdb_id:
                ids.extend([(t_id, "tvdb") for t_id in tvdb_id])
            if isinstance(item, Movie) and tmdb_id:
                ids.extend([(t_id, "tmdb") for t_id in tmdb_id])
        return ids

    def get_rating_keys(self, method, data, is_playlist=False):
        items = []
        if method == "plex_all":
            logger.info(f"Processing Plex All {data.capitalize()}s")
            items = self.get_all(builder_level=data)
        elif method == "plex_watchlist":
            logger.info(f"Processing Plex Watchlist")
            return self.get_watchlist(sort=data, is_playlist=is_playlist)
        elif method == "plex_pilots":
            logger.info(f"Processing Plex Pilot {data.capitalize()}s")
            items = []
            for item in self.get_all():
                try:
                    items.append(item.episode(season=1, episode=1))
                except NotFound:
                    logger.warning(f"Plex Warning: {item.title} has no Season 1 Episode 1 ")
        elif method == "plex_search":
            logger.info(f"Processing {data[1]}")
            logger.trace(data[2])
            items = self.fetchItems(data[2])
        elif method == "plex_collectionless":
            good_collections = []
            logger.info(f"Processing Plex Collectionless")
            logger.info("")
            for col in self.get_all_collections():
                keep_collection = True
                for pre in data["exclude_prefix"]:
                    if col.title.startswith(pre) or (col.titleSort and col.titleSort.startswith(pre)):
                        keep_collection = False
                        logger.info(f"Excluded by Prefix Match: {col.title}")
                        break
                if keep_collection:
                    for ext in data["exclude"]:
                        if col.title == ext or (col.titleSort and col.titleSort == ext):
                            keep_collection = False
                            logger.info(f"Excluded by Exact Match: {col.title}")
                            break
                if keep_collection:
                    good_collections.append(col)
            logger.info("")
            logger.info("Collections Not Excluded (Items in these collections are not added to Collectionless)")
            for col in good_collections:
                logger.info(col.title)
            logger.info("")
            collection_indexes = [str(c.title).lower() for c in good_collections]
            all_items = self.get_all()
            for i, item in enumerate(all_items, 1):
                logger.ghost(f"Processing: {i}/{len(all_items)} {item.title}")
                add_item = True
                item = self.reload(item)
                for collection in item.collections:
                    if str(collection.tag).lower() in collection_indexes:
                        add_item = False
                        break
                if add_item:
                    items.append(item)
            logger.info(f"Processed {len(all_items)} {self.type}s")
        else:
            raise Failed(f"Plex Error: Method {method} not supported")
        if not items:
            raise Failed("Plex Error: No Items found in Plex")
        return [(item.ratingKey, "ratingKey") for item in items]

    def get_collection_items(self, collection, smart_label_collection):
        if smart_label_collection:
            return self.search(label=collection.title if isinstance(collection, Collection) else str(collection))
        elif isinstance(collection, (Collection, Playlist)):
            if collection.smart:
                return self.fetchItems(self.smart_filter(collection))
            else:
                return self.query(collection.items)
        else:
            return []

    def get_collection_name_and_items(self, collection, smart_label_collection):
        name = collection.title if isinstance(collection, (Collection, Playlist)) else str(collection)
        return name, self.get_collection_items(collection, smart_label_collection)

    def get_tmdb_from_map(self, item):
        return self.movie_rating_key_map[item.ratingKey] if item.ratingKey in self.movie_rating_key_map else None

    def get_tvdb_from_map(self, item):
        return self.show_rating_key_map[item.ratingKey] if item.ratingKey in self.show_rating_key_map else None

    def get_imdb_from_map(self, item):
        return self.imdb_rating_key_map[item.ratingKey] if item.ratingKey in self.imdb_rating_key_map else None

    def search_item(self, data, year=None, edition=None):
        kwargs = {}
        if year is not None:
            kwargs["year"] = year
        if edition is not None:
            kwargs["editionTitle"] = edition
        return [d for d in self.search(title=str(data), **kwargs) if d.title == data]

    def edit_advance(self, item, edits):
        try:
            self.edit_query(item, edits, advanced=True)
            if "languageOverride" in edits or "useOriginalTitle" in edits:
                self.query(item.refresh)
            return True
        except BadRequest:
            logger.stacktrace()
            return False

    def edit_tags(self, attr, obj, add_tags=None, remove_tags=None, sync_tags=None, do_print=True, locked=True, is_locked=None):
        display = ""
        final = ""
        key = attribute_translation[attr] if attr in attribute_translation else attr
        actual = "similar" if attr == "similar_artist" else attr
        attr_display = attr.replace("_", " ").title()
        if add_tags or remove_tags or sync_tags is not None:
            _add_tags = add_tags if add_tags else []
            _remove_tags = remove_tags if remove_tags else []
            _sync_tags = sync_tags if sync_tags else []
            try:
                obj = self.reload(obj)
                _item_tags = [item_tag.tag for item_tag in getattr(obj, key)]
            except BadRequest:
                _item_tags = []
            _add = [t for t in _add_tags + _sync_tags if t not in _item_tags]
            _remove = [t for t in _item_tags if (sync_tags is not None and t not in _sync_tags) or t in _remove_tags]
            if _add:
                self.tag_edit(obj, actual, _add, locked=locked)
                display += f"+{', +'.join(_add)}"
            if _remove:
                self.tag_edit(obj, actual, _remove, locked=locked, remove=True)
                if display:
                    display += ", "
                display += f"-{', -'.join(_remove)}"
            if is_locked is not None and not display and is_locked != locked:
                self.edit_query(obj, {f"{actual}.locked": 1 if locked else 0})
                display = "Locked" if locked else "Unlocked"
            final = f"{obj.title[:25]:<25} | {attr_display} | {display}" if display else display
            if do_print and final:
                logger.info(final)
        return final[28:] if final else final

    def image_update(self, item, image, tmdb=None, title=None, poster=True):
        text = f"{f'{title} ' if title else ''}{'Poster' if poster else 'Background'}"
        attr = self.mass_poster_update["source"] if poster else self.mass_background_update["source"]
        if attr == "lock":
            self.query(item.lockPoster if poster else item.lockArt)
            logger.info(f"{text} | Locked")
        elif attr == "unlock":
            self.query(item.unlockPoster if poster else item.unlockArt)
            logger.info(f"{text} | Unlocked")
        else:
            location = "the Assets Directory" if image else ""
            image_url = False if image else True
            image = image.location if image else None
            if not image:
                if attr == "tmdb" and tmdb:
                    image = tmdb
                    location = "TMDb"
                if not image:
                    images = item.posters() if poster else item.arts()
                    temp_image = next((p for p in images), None)
                    if temp_image:
                        if temp_image.key.startswith("/"):
                            image = f"{self.url}{temp_image.key}&X-Plex-Token={self.token}"
                        else:
                            image = temp_image.key
                        location = "Plex"
            if image:
                logger.info(f"{text} | Reset from {location}")
                if poster:
                    try:
                        self.upload_poster(item, image, url=image_url)
                    except BadRequest as e:
                        logger.stacktrace()
                        logger.error(f"Plex Error: {e}")
                else:
                    try:
                        self.upload_background(item, image, url=image_url)
                    except BadRequest as e:
                        logger.stacktrace()
                        logger.error(f"Plex Error: {e}")
                if poster and "Overlay" in [la.tag for la in self.item_labels(item)]:
                    logger.info(self.edit_tags("label", item, remove_tags="Overlay", do_print=False))
            else:
                logger.warning(f"{text} | No Reset Image Found")

    def item_images(self, item, group, alias, initial=False, asset_location=None, asset_directory=None, title=None, image_name=None, folder_name=None, style_data=None):
        if title is None:
            title = item.title
        posters, backgrounds = util.get_image_dicts(group, alias)
        if style_data and "url_poster" in style_data and style_data["url_poster"]:
            posters["style_data"] = style_data["url_poster"]
        elif style_data and "tpdb_poster" in style_data and style_data["tpdb_poster"]:
            posters["style_data"] = f"https://theposterdb.com/api/assets/{style_data['tpdb_poster']}"
        if style_data and "url_background" in style_data and style_data["url_background"]:
            backgrounds["style_data"] = style_data["url_background"]
        elif style_data and "tpdb_background" in style_data and style_data["tpdb_background"]:
            backgrounds["style_data"] = f"https://theposterdb.com/api/assets/{style_data['tpdb_background']}"
        try:
            asset_poster, asset_background, item_dir, folder_name = self.find_item_assets(item, item_asset_directory=asset_location, asset_directory=asset_directory)
            if asset_poster:
                posters["asset_directory"] = asset_poster
            if asset_background:
                backgrounds["asset_directory"] = asset_background
            if asset_location is None or initial:
                asset_location = item_dir
        except Failed as e:
            logger.warning(e)
        poster = self.pick_image(title, posters, self.prioritize_assets, self.download_url_assets, asset_location, image_name=image_name)
        background = self.pick_image(title, backgrounds, self.prioritize_assets, self.download_url_assets, asset_location,
                                     is_poster=False, image_name=f"{image_name}_background" if image_name else image_name)
        updated = False
        if poster or background:
            pu, bu = self.upload_images(item, poster=poster, background=background, overlay=True)
            if pu or bu:
                updated = True
        return asset_location, folder_name, updated

    def find_and_upload_assets(self, item, current_labels, asset_directory=None):
        item_dir = None
        name = None
        try:
            poster, background, item_dir, name = self.find_item_assets(item, asset_directory=asset_directory)
            if "Overlay" not in current_labels:
                if poster or background:
                    self.upload_images(item, poster=poster, background=background)
                elif self.show_missing_assets:
                    logger.warning(f"Asset Warning: No poster or background found in the assets folder '{item_dir}'")
            else:
                logger.info(f"Item: {name} has an Overlay and will be updated when overlays are run")
        except Failed as e:
            if self.show_missing_assets:
                logger.warning(e)
        if isinstance(item, Show) and ((self.asset_folders and item_dir) or not self.asset_folders):
            missing_seasons = ""
            missing_episodes = ""
            found_season = False
            found_episode = False
            for season in self.query(item.seasons):
                try:
                    season_poster, season_background, _, _ = self.find_item_assets(season, item_asset_directory=item_dir, asset_directory=asset_directory, folder_name=name)
                    if season_poster:
                        found_season = True
                    elif self.show_missing_season_assets and season.seasonNumber > 0:
                        missing_seasons += f"\nMissing Season {season.seasonNumber} Poster"
                    if season_poster or season_background and "Overlay" not in [la.tag for la in self.item_labels(season)]:
                        self.upload_images(season, poster=season_poster, background=season_background)
                except Failed as e:
                    if self.show_missing_assets:
                        logger.warning(e)
                for episode in self.query(season.episodes):
                    try:
                        if episode.seasonEpisode:
                            episode_poster, episode_background, _, _ = self.find_item_assets(episode, item_asset_directory=item_dir, asset_directory=asset_directory, folder_name=name)
                            if episode_poster or episode_background:
                                found_episode = True
                                if "Overlay" not in [la.tag for la in self.item_labels(episode)]:
                                    self.upload_images(episode, poster=episode_poster, background=episode_background)
                            elif self.show_missing_episode_assets:
                                missing_episodes += f"\nMissing {episode.seasonEpisode.upper()} Title Card"
                    except Failed as e:
                        if self.show_missing_assets:
                            logger.warning(e)
            if (found_season and missing_seasons) or (found_episode and missing_episodes):
                logger.info(f"Missing Posters for {item.title}{missing_seasons}{missing_episodes}")
        if isinstance(item, Artist):
            missing_assets = ""
            found_album = False
            for album in self.query(item.albums):
                try:
                    album_poster, album_background, _, _ = self.find_item_assets(album, item_asset_directory=item_dir, asset_directory=asset_directory, folder_name=name)
                    if album_poster or album_background:
                        found_album = True
                    elif self.show_missing_season_assets:
                        missing_assets += f"\nMissing Album {album.title} Poster"
                    if album_poster or album_background:
                        self.upload_images(album, poster=album_poster, background=album_background)
                except Failed as e:
                    if self.show_missing_assets:
                        logger.warning(e)
            if self.show_missing_season_assets and found_album and missing_assets:
                logger.info(f"Missing Album Posters for {item.title}{missing_assets}")

    def find_item_assets(self, item, item_asset_directory=None, asset_directory=None, folder_name=None):
        poster = None
        background = None

        if asset_directory is None:
            asset_directory = self.asset_directory

        is_top_level = isinstance(item, (Movie, Artist, Show, Collection, Playlist, str))
        if isinstance(item, Album):
            prefix = f"{item.parentTitle} Album {item.title}'s "
            file_name = item.title
        elif isinstance(item, Season):
            prefix = f"{item.parentTitle} Season {item.seasonNumber}'s "
            file_name = f"Season{'0' if not item.seasonNumber or item.seasonNumber < 10 else ''}{item.seasonNumber}"
        elif isinstance(item, Episode):
            prefix = f"{item.grandparentTitle} {item.seasonEpisode.upper()}'s "
            file_name = item.seasonEpisode.upper()
        else:
            prefix = f"{item if isinstance(item, str) else item.title}'s "
            file_name = "poster"

        if not item_asset_directory:
            if isinstance(item, (Movie, Artist, Album, Show, Episode, Season)):
                if isinstance(item, (Episode, Season)):
                    starting = item.show()
                elif isinstance(item, (Album, Track)):
                    starting = item.artist()
                else:
                    starting = item
                if not starting.locations:
                    raise Failed(f"Asset Warning: No video filepath found for {item.title}")
                path_test = str(starting.locations[0])
                if not os.path.dirname(path_test):
                    path_test = path_test.replace("\\", "/")
                folder_name = os.path.basename(os.path.dirname(path_test) if isinstance(starting, Movie) else path_test)
            elif isinstance(item, (Collection, Playlist)):
                folder_name = item.title
            else:
                folder_name = item
            folder_name, _ = util.validate_filename(folder_name)

        if not self.asset_folders:
            file_name = folder_name if file_name == "poster" else f"{folder_name}_{file_name}"

        if not item_asset_directory:
            for ad in asset_directory:
                if self.asset_folders:
                    if os.path.isdir(os.path.join(ad, folder_name)):
                        item_asset_directory = os.path.join(ad, folder_name)
                    else:
                        for n in range(1, self.asset_depth + 1):
                            new_path = ad
                            for i in range(1, n + 1):
                                new_path = os.path.join(new_path, "*")
                            matches = util.glob_filter(os.path.join(new_path, folder_name))
                            if len(matches) > 0:
                                item_asset_directory = os.path.abspath(matches[0])
                                break
                else:
                    matches = util.glob_filter(os.path.join(ad, f"{file_name}.*"))
                    if len(matches) > 0:
                        item_asset_directory = ad
                if item_asset_directory:
                    break
            if not item_asset_directory:
                if self.asset_folders:
                    if self.create_asset_folders and asset_directory:
                        item_asset_directory = os.path.join(asset_directory[0], folder_name)
                        os.makedirs(item_asset_directory, exist_ok=True)
                        logger.warning(f"Asset Warning: Asset Directory Not Found and Created: {item_asset_directory}")
                    else:
                        raise Failed(f"Asset Warning: Unable to find asset folder: '{folder_name}'")
                return None, None, item_asset_directory, folder_name

        poster_filter = os.path.join(item_asset_directory, f"{file_name}.*")
        background_filter = os.path.join(item_asset_directory, "background.*" if file_name == "poster" else f"{file_name}_background.*")

        poster_matches = util.glob_filter(poster_filter)
        if len(poster_matches) > 0:
            poster = ImageData("asset_directory", os.path.abspath(poster_matches[0]), prefix=prefix, is_url=False)

        background_matches = util.glob_filter(background_filter)
        if len(background_matches) > 0:
            background = ImageData("asset_directory", os.path.abspath(background_matches[0]), prefix=prefix, is_poster=False, is_url=False)

        if is_top_level and self.asset_folders and self.dimensional_asset_rename and (not poster or not background):
            for file in util.glob_filter(os.path.join(item_asset_directory, "*.*")):
                if file.lower().endswith((".png", ".jpg", ".jpeg", "webp")) and not re.match(r"s\d+e\d+|season\d+", os.path.basename(file).lower()):
                    try:
                        with Image.open(file) as image:
                            _w, _h = image.size
                        if not poster and _h >= _w:
                            new_path = os.path.join(os.path.dirname(file), f"poster{os.path.splitext(file)[1].lower()}")
                            os.rename(file, new_path)
                            poster = ImageData("asset_directory", os.path.abspath(new_path), prefix=prefix, is_url=False)
                        elif not background and _w > _h:
                            new_path = os.path.join(os.path.dirname(file), f"background{os.path.splitext(file)[1].lower()}")
                            os.rename(file, new_path)
                            background = ImageData("asset_directory", os.path.abspath(new_path), prefix=prefix, is_poster=False, is_url=False)
                        if poster and background:
                            break
                    except OSError:
                        logger.error(f"Asset Error: Failed to open image: {file}")

        return poster, background, item_asset_directory, folder_name

    def get_ids(self, item):
        tmdb_id = None
        tvdb_id = None
        imdb_id = None
        if self.config.Cache:
            t_id, i_id, guid_media_type, _ = self.config.Cache.query_guid_map(item.guid)
            if t_id:
                if "movie" in guid_media_type:
                    tmdb_id = t_id[0]
                else:
                    tvdb_id = t_id[0]
            if i_id:
                imdb_id = i_id[0]
        if not tmdb_id and not tvdb_id:
            tmdb_id = self.get_tmdb_from_map(item)
        if not tmdb_id and not tvdb_id and self.is_show:
            tvdb_id = self.get_tvdb_from_map(item)
        if not imdb_id:
            imdb_id = self.get_imdb_from_map(item)
        return tmdb_id, tvdb_id, imdb_id

    def get_locked_attributes(self, item, titles=None, year_titles=None, item_type=None):
        if not item_type:
            item_type = self.type
        item = self.reload(item)
        attrs = {}
        match_dict = {}
        fields = {f.name: f for f in item.fields if f.locked}
        if isinstance(item, (Artist, Album, Track)):
            if item.userRating:
                fields["userRating"] = item.userRating
        if isinstance(item, (Movie, Show)) and titles and titles.count(item.title) > 1:
            if year_titles.count(f"{item.title} ({item.year})") > 1:
                match_dict["title"] = item.title
                match_dict["year"] = item.year
                if hasattr(item, "editionTitle") and item.editionTitle:
                    map_key = f"{item.title} ({item.year}) [{item.editionTitle}]"
                    match_dict["edition"] = item.editionTitle
                else:
                    map_key = f"{item.title} ({item.year})"
                    match_dict["blank_edition"] = True
            else:
                map_key = f"{item.title} ({item.year})"
                match_dict["title"] = item.title
                match_dict["year"] = item.year
        elif isinstance(item, (Season, Episode, Track)) and item.index:
            map_key = int(item.index)
        else:
            map_key = item.title

        if "title" in fields:
            attrs["title"] = item.title
            if isinstance(item, (Movie, Show)):
                tmdb_id, tvdb_id, imdb_id = self.get_ids(item)
                tmdb_item = self.config.TMDb.get_item(item, tmdb_id, tvdb_id, imdb_id, is_movie=isinstance(item, Movie))
                if tmdb_item and tmdb_item.title != item.title:
                    match_dict["title"] = [item.title, tmdb_item.title]

        if match_dict:
            attrs["match"] = match_dict

        def check_field(plex_key, kometa_key, var_key=None):
            if plex_key in fields and kometa_key not in self.metadata_backup["exclude"]:
                if not var_key:
                    var_key = plex_key
                if hasattr(item, var_key):
                    plex_value = getattr(item, var_key)
                    if isinstance(plex_value, list):
                        plex_tags = [t.tag for t in plex_value]
                        if len(plex_tags) > 0 or self.metadata_backup["sync_tags"]:
                            attrs[f"{kometa_key}.sync" if self.metadata_backup["sync_tags"] else kometa_key] = None if not plex_tags else plex_tags[0] if len(plex_tags) == 1 else plex_tags
                    elif isinstance(plex_value, datetime):
                        attrs[kometa_key] = datetime.strftime(plex_value, "%Y-%m-%d")
                    else:
                        attrs[kometa_key] = plex_value

        check_field("titleSort", "sort_title")
        check_field("editionTitle", "edition")
        check_field("originalTitle", "original_artist" if self.is_music else "original_title")
        check_field("originallyAvailableAt", "originally_available")
        check_field("contentRating", "content_rating")
        check_field("userRating", "user_rating")
        check_field("audienceRating", "audience_rating")
        check_field("rating", "critic_rating")
        check_field("studio", "record_label" if self.is_music else "studio")
        check_field("tagline", "tagline")
        check_field("summary", "summary")
        check_field("index", "track")
        check_field("parentIndex", "disc")
        check_field("director", "director", var_key="directors")
        check_field("country", "country", var_key="countries")
        check_field("genre", "genre", var_key="genres")
        check_field("writer", "writer", var_key="writers")
        check_field("producer", "producer", var_key="producers")
        check_field("collection", "collection", var_key="collections")
        check_field("label", "label", var_key="labels")
        check_field("mood", "mood", var_key="moods")
        check_field("style", "style", var_key="styles")
        check_field("similar", "similar_artist")
        if item_type in util.advance_tags_to_edit:
            for advance_edit in util.advance_tags_to_edit[item_type]:
                key, options = item_advance_keys[f"item_{advance_edit}"]
                if advance_edit in self.metadata_backup["exclude"] or not hasattr(item, key) or not getattr(item, key):
                    continue
                keys = {v: k for k, v in options.items()}
                attr = getattr(item, key)
                if attr not in keys:
                    logger.error(f"Item {item.title} {advance_edit} {attr} Not Found rating key: {item.ratingKey}")
                elif keys[attr] not in ["default", "all", "never"]:
                    attrs[advance_edit] = keys[attr]

        def _recur(sub, item_type_in=None):
            sub_items = {}
            for sub_item in getattr(item, sub)():
                sub_item_key, sub_item_attrs = self.get_locked_attributes(sub_item, item_type=item_type_in)
                if sub_item_attrs:
                    sub_items[sub_item_key] = sub_item_attrs
            if sub_items:
                attrs[sub] = sub_items

        if isinstance(item, Show):
            _recur("seasons")
        elif isinstance(item, Season):
            _recur("episodes", item_type_in="Season")
        elif isinstance(item, Artist):
            _recur("albums")
        elif isinstance(item, Album):
            _recur("tracks")

        return map_key, attrs

    def get_item_sort_title(self, item_to_sort, atr="titleSort"):
        if isinstance(item_to_sort, Album):
            return f"{getattr(item_to_sort.artist(), atr)} Album {getattr(item_to_sort, atr)}"
        elif isinstance(item_to_sort, Season):
            return f"{getattr(item_to_sort.show(), atr)} Season {item_to_sort.seasonNumber}"
        elif isinstance(item_to_sort, Episode):
            return f"{getattr(item_to_sort.show(), atr)} {item_to_sort.seasonEpisode.upper()}"
        else:
            return getattr(item_to_sort, atr)

    def split(self, text):
        attribute, modifier = os.path.splitext(str(text).lower())
        attribute = method_alias[attribute] if attribute in method_alias else attribute
        modifier = modifier_alias[modifier] if modifier in modifier_alias else modifier

        if attribute == "add_to_arr":
            attribute = "radarr_add_missing" if self.is_movie else "sonarr_add_missing"
        elif attribute in ["arr_tag", "arr_folder"]:
            attribute = f"{'rad' if self.is_movie else 'son'}{attribute}"
        elif attribute in builder.date_attributes and modifier in [".gt", ".gte"]:
            modifier = ".after"
        elif attribute in builder.date_attributes and modifier in [".lt", ".lte"]:
            modifier = ".before"
        final = f"{attribute}{modifier}"
        if text != final:
            logger.warning(f"Collection Warning: {text} attribute will run as {final}")
        return attribute, modifier, final

    def check_filters(self, item, filters_in, current_time):
        for filter_method, filter_data in filters_in:
            filter_attr, modifier, filter_final = self.split(filter_method)
            if self.check_filter(item, filter_attr, modifier, filter_final, filter_data, current_time) is False:
                return False
        return True

    def check_filter(self, item, filter_attr, modifier, filter_final, filter_data, current_time):
        filter_actual = attribute_translation[filter_attr] if filter_attr in attribute_translation else filter_attr
        if isinstance(item, Movie):
            item_type = "movie"
        elif isinstance(item, Show):
            item_type = "show"
        elif isinstance(item, Season):
            item_type = "season"
        elif isinstance(item, Episode):
            item_type = "episode"
        elif isinstance(item, Artist):
            item_type = "artist"
        elif isinstance(item, Album):
            item_type = "album"
        elif isinstance(item, Track):
            item_type = "track"
        else:
            return True
        item = self.reload(item)
        if filter_attr not in builder.filters[item_type]:
            return True
        elif filter_attr in builder.date_filters:
            if util.is_date_filter(getattr(item, filter_actual), modifier, filter_data, filter_final, current_time):
                return False
        elif filter_attr in builder.string_filters:
            values = []
            if filter_attr == "audio_track_title":
                for media in item.media:
                    for part in media.parts:
                        values.extend([a.extendedDisplayTitle for a in part.audioStreams() if a.extendedDisplayTitle])
            elif filter_attr == "subtitle_track_title":
                for media in item.media:
                    for part in media.parts:
                        values.extend([a.extendedDisplayTitle for a in part.subtitleStreams() if a.extendedDisplayTitle])
            elif filter_attr in ["audio_codec", "audio_profile", "video_codec", "video_profile"]:
                for media in item.media:
                    attr = getattr(media, filter_actual)
                    if attr and attr not in values:
                        values.append(attr)
            elif filter_attr in ["filepath", "folder"]:
                values = [loc for loc in item.locations if loc]
            else:
                test_value = getattr(item, filter_actual)
                values = [test_value] if test_value else []
            if util.is_string_filter(values, modifier, filter_data):
                return False
        elif filter_attr in builder.boolean_filters:
            filter_check = False
            if filter_attr == "has_collection":
                filter_check = len(item.collections) > 0
            elif filter_attr == "has_edition":
                filter_check = True if item.editionTitle else False
            elif filter_attr == "has_stinger":
                filter_check = False
                if item.ratingKey in self.movie_rating_key_map and self.movie_rating_key_map[item.ratingKey] in self.config.mediastingers:
                    filter_check = True
            elif filter_attr == "has_overlay":
                for label in self.item_labels(item):
                    if label.tag.lower().endswith(" overlay") or label.tag.lower() == "overlay":
                        filter_check = True
                        break
            elif filter_attr == "has_dolby_vision":
                for media in item.media:
                    for part in media.parts:
                        for stream in part.videoStreams():
                            if stream.DOVIPresent:
                                filter_check = True
                                break
            if util.is_boolean_filter(filter_data, filter_check):
                return False
        elif filter_attr == "history":
            item_date = item.originallyAvailableAt
            if item_date is None:
                return False
            elif filter_data == "day":
                if item_date.month != current_time.month or item_date.day != current_time.day:
                    return False
            elif filter_data == "month":
                if item_date.month != current_time.month:
                    return False
            else:
                date_match = False
                for i in range(filter_data):
                    check_date = current_time - timedelta(days=i)
                    if item_date.month == check_date.month and item_date.day == check_date.day:
                        date_match = True
                if date_match is False:
                    return False
        elif filter_attr in ["seasons", "episodes", "albums", "tracks"]:
            if filter_attr == "seasons":
                sub_items = item.seasons()
            elif filter_attr == "albums":
                sub_items = item.albums()
            elif filter_attr == "tracks":
                sub_items = item.tracks()
            else:
                sub_items = item.episodes()
            filters_in = []
            percentage = 60
            for sub_atr, sub_data in filter_data.items():
                if sub_atr == "percentage":
                    percentage = sub_data
                else:
                    filters_in.append((sub_atr, sub_data))
            failure_threshold = len(sub_items) * ((100 - percentage) / 100)
            failures = 0
            for sub_item in sub_items:
                if self.check_filters(sub_item, filters_in, current_time) is False:
                    failures += 1
                if failures > failure_threshold:
                    return False
        elif (filter_attr != "year" and filter_attr in builder.number_filters) or modifier in [".gt", ".gte", ".lt", ".lte", ".count_gt", ".count_gte", ".count_lt", ".count_lte"]:
            test_number = []
            if filter_attr in ["channels", "height", "width", "aspect"]:
                test_number = 0
                for media in item.media:
                    attr = getattr(media, filter_actual)
                    if attr and attr > test_number:
                        test_number = attr
            elif filter_attr == "stinger_rating":
                test_number = None
                if item.ratingKey in self.movie_rating_key_map and self.movie_rating_key_map[item.ratingKey] in self.config.mediastingers:
                    test_number = self.config.mediastingers[self.movie_rating_key_map[item.ratingKey]]
            elif filter_attr == "versions":
                test_number = len(item.media)
            elif filter_attr == "audio_language":
                for media in item.media:
                    for part in media.parts:
                        test_number.extend([a.language for a in part.audioStreams()])
            elif filter_attr == "subtitle_language":
                for media in item.media:
                    for part in media.parts:
                        test_number.extend([s.language for s in part.subtitleStreams()])
            elif filter_attr == "duration":
                test_number = getattr(item, filter_actual)
                if test_number:
                    test_number /= 60000
            else:
                test_number = getattr(item, filter_actual)
            if modifier in [".count_gt", ".count_gte", ".count_lt", ".count_lte"]:
                test_number = len(test_number) if test_number else 0
                modifier = f".{modifier[7:]}"
            if test_number is None or util.is_number_filter(test_number, modifier, filter_data):
                return False
        else:
            attrs = []
            if filter_attr in ["resolution", "audio_language", "subtitle_language"]:
                for media in item.media:
                    if filter_attr == "resolution":
                        attrs.append(media.videoResolution)
                    for part in media.parts:
                        if filter_attr == "audio_language":
                            for a in part.audioStreams():
                                attrs.extend([a.language, a.languageCode])
                        if filter_attr == "subtitle_language":
                            for s in part.subtitleStreams():
                                attrs.extend([s.language, s.languageCode])
            elif filter_attr in ["content_rating", "year", "rating"]:
                attrs = [getattr(item, filter_actual)]
            elif filter_attr in ["actor", "country", "director", "genre", "label", "producer", "writer",
                                 "collection", "network"]:
                attrs = [attr.tag for attr in getattr(item, filter_actual)]
            else:
                raise Failed(f"Filter Error: filter: {filter_final} not supported")
            if modifier == ".regex":
                has_match = False
                for reg in filter_data:
                    for name in attrs:
                        if isinstance(name, str):
                            if re.compile(reg).search(name):
                                has_match = True
                if has_match is False:
                    return False
            elif (not list(set(filter_data) & set(attrs)) and modifier == "") \
                    or (list(set(filter_data) & set(attrs)) and modifier == ".not"):
                return False
        return True
