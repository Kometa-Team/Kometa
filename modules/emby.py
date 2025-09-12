import os
import re
import time
from datetime import datetime, timedelta
# from importlib.metadata import pass_none
from urllib.parse import unquote
from xml.etree.ElementTree import ParseError

import requests
from PIL import Image
from plexapi import utils
from plexapi.audio import Artist, Track, Album
from plexapi.collection import Collection
from plexapi.exceptions import BadRequest, NotFound, Unauthorized
from plexapi.library import Role, FilterChoice
from plexapi.playlist import Playlist
from plexapi.video import Movie, Show, Season, Episode
from requests.exceptions import ConnectionError, ConnectTimeout
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_not_exception_type

from modules import builder, util
from modules.emby_server import EmbyServer, FilterChoiceEmby
from modules.library import Library
from modules.logs import WARNING
from modules.poster import ImageData
from modules.request import parse_qs, quote_plus, urlparse
from modules.util import Failed

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
    "dovi": "dovi",
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
    "composer": "composers",
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
    "composers": "composer",
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
episode_ordering_options = {"default": None, "tmdb_aired": "tmdbAiring", "tvdb_aired": "tvdbAiring", "tvdb_dvd": "tvdbDvd", "tvdb_absolute": "tvdbAbsolute"}
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
    "network.and", "producer.and", "composer.and", "subtitle_language.and", "writer.and"
]
or_searches = [
    "title", "studio", "actor", "audio_language", "collection", "content_rating",
    "country", "director", "genre", "label", "network", "producer", "composer", "subtitle_language",
    "writer", "decade", "resolution", "year", "episode_title", "episode_year"
]
movie_only_searches = [
    "director", "director.not", "producer", "producer.not", "composer", "composer.not", "writer", "writer.not",
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
    "dovi", "hdr", "unmatched", "duplicate", "unplayed", "progress", "trash", "unplayed_episodes", "episode_unplayed",
    "episode_duplicate", "episode_progress", "episode_unmatched", "show_unmatched", "artist_unmatched", "album_unmatched", "track_trash"
]
tmdb_attributes = ["actor", "director", "producer", "composer", "writer"]
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
    "producer", "composer", "resolution", "studio", "subtitle_language", "writer", "season_collection", "episode_collection", "edition",
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

MAX_IMAGE_SIZE = 10480000  # a little less than 10MB

class Emby(Library):
    def __init__(self, config, params):
        super().__init__(config, params)

        self.filter_items_cache = {}
        self.emby = params["emby"]
        self.emby_server_url = self.emby["url"]
        self.session = self.config.Requests.session # init?
        if self.emby["verify_ssl"] is False and self.config.Requests.global_ssl is True:
            logger.debug("Overriding verify_ssl to False for Emby connection")
            self.session = self.config.Requests.create_session(verify_ssl=False)
        if self.emby["verify_ssl"] is True and self.config.Requests.global_ssl is False:
            logger.debug("Overriding verify_ssl to True for Emby connection")
            self.session = self.config.Requests.create_session()
        self.emby_api_key = self.emby["api_key"]
        self.emby_user_id = self.emby["user_id"]
        self.overlay_destination_folder = self.emby["overlay_destination_folder"]
        self.timeout = self.emby["timeout"]
        logger.secret(self.emby_server_url)
        logger.secret(self.emby_api_key)
        logger.secret(self.emby_user_id)
        self.EmbyServer = None
        try:
            self.EmbyServer = EmbyServer(self.emby_server_url, self.emby_user_id, self.emby_api_key,config, params["name"])
            # timeout not set - self.timeout
            logger.info(f"Connected to server {self.EmbyServer.friendlyName} version {self.EmbyServer.version}")
            logger.info(f"Running on {self.EmbyServer.platform} version {self.EmbyServer.platformVersion}")
            # srv_settings = self.EmbyServer.settings
            # try:
            #     db_cache = srv_settings.get("DatabaseCacheSize")
            #     logger.info(f"Plex DB cache setting: {db_cache.value} MB")
            #     if self.plex["db_cache"] and self.plex["db_cache"] != db_cache.value:
            #         db_cache.set(self.plex["db_cache"])
            #         self.PlexServer.settings.save()
            #         logger.info(f"Plex DB Cache updated to {self.plex['db_cache']} MB")
            # except NotFound:
            #     logger.info(f"Plex DB cache setting: Unknown")
            # try:
            #     chl_num = srv_settings.get("butlerUpdateChannel").value
            #     if chl_num == "16":
            #         uc_str = f"Public update channel."
            #     elif chl_num == "8":
            #         uc_str = f"PlexPass update channel."
            #     else:
            #         uc_str = f"Unknown update channel: {chl_num}."
            # except NotFound:
            #     uc_str = f"Unknown update channel."
            # TODO - subscription info
            # logger.info(f"PlexPass: {self.EmbyServer.myPlexSubscription} on {uc_str}")

            # try:
            #     logger.info(f"Scheduled maintenance running between {srv_settings.get('butlerStartHour').value}:00 and {srv_settings.get('butlerEndHour').value}:00")
            # except NotFound:
            #     logger.info("Scheduled maintenance times could not be found")
        except Unauthorized:
            logger.info(f"Emby Error: Emby connection attempt returned 'Unauthorized'")
            raise Failed("Emby Error: Emby API key is invalid")
        except ConnectTimeout:
            raise Failed(f"Emby Error: Emby did not respond within the {self.timeout}-second timeout.")
        except ValueError as e:
            logger.info(f"Emby Error: Emby connection attempt returned 'ValueError'")
            logger.stacktrace()
            raise Failed(f"Emby Error: {e}")
        except (ConnectionError, ParseError):
            logger.info(f"Emby Error: Emby connection attempt returned 'ConnectionError' or 'ParseError'")
            logger.stacktrace()
            raise Failed("Emby Error: Plex URL is probably invalid")

        self.Emby = None

        emby_library_names = []
        # print(params)
        self.lib_type = None
        for s in self.EmbyServer.get_libraries():
            # print(s)
            emby_library_names.append(s["Name"])
            if s["CollectionType"] == 'tvshows':
                self.lib_type = "show"
            elif s["CollectionType"] == 'movies':
                self.lib_type = "movie"
            if s["Name"] == params["name"]:
                self.Emby = s
                self.EmbyServer.library_id= self.Emby.get('Id')
                print(s)
                break
        # print(emby_library_names)
        if not self.Emby:
            raise Failed(f"Emby Error: Emby Library '{params['name']}' not found. Options: {emby_library_names}")
        # --------------

        self.type = self.Emby.get("CollectionType", "")
        # Entferne das 's', wenn self.type 'movies' oder 'shows' ist

        # Now, find out the library type
        collection_type = self.Emby.get("CollectionType", "").lower()
        if collection_type == "movies":
            self.emby_type = "Movie"
        elif collection_type == "tvshows":
            self.emby_type = "Show"
        elif collection_type == "music":
            self.emby_type = "Artist"
        else:
            self.emby_type = "Other"
        self.type= self.emby_type
        # print(f"Collection type is: '{collection_type}'")
        # coll = Collection()
        if self.emby_type.lower() not in library_types:
            raise Failed(f"Emby Error: Emby Library must be a Movies, TV Shows, or Music library")



        # print(f"EMBY Library type: {self.type}")
        # print(self.type)
        self._users = []
        self.emby_users = []
        self._all_items = []
        self._emby_all_items = []
        self._emby_all_items_native = []
        self._account = None

        # source_setting = next((s for s in self.Plex.settings() if s.id in ["ratingsSource"]), None)
        # Todo
        # print(f"Checkie: {source_setting}")
        # Checkie: <Setting:ratingsSource:rottentomatoes>
        # Checkie: <Setting:ratingsSource:imdb>
        # Checkie: <Setting:ratingsSource:themoviedb>
        self.ratings_source = "N/A" # lets' use RT
        # self.ratings_source = source_setting.enumValues[source_setting.value] if source_setting else "N/A"

        self.is_movie = self.emby_type == "Movie"
        self.is_show = self.emby_type == "Show"
        self.is_music = self.emby_type == "Artist"
        self.is_other = self.emby_type == "Other"

        # todo: needed for Emby?
        if self.is_other and self.type == "Movie":
            self.type = "Video"
        if not self.is_music and self.update_blank_track_titles:
            self.update_blank_track_titles = False
            logger.error(f"update_blank_track_titles library operation only works with music libraries")

        logger.info(f"Connected to library {params['name']}")
        logger.info(f"Type: {self.type}")
        logger.info(f"Ratings Source: {self.ratings_source}")
# ToDo - Untested, develop; use this with db cache instead of set_image_smart
    def _upload_image(self, item, image):
        upload_success = True
        try:
            if image.is_url and "theposterdb.com" in image.location:
                now = datetime.now()
                if self.config.tpdb_timer is not None:
                    while self.config.tpdb_timer + timedelta(seconds=6) > now:
                        time.sleep(1)
                        now = datetime.now()
                self.config.tpdb_timer = now
            if image.is_poster and image.is_url:
                self.upload_poster(item, url=image.location)
            elif image.is_poster:
                upload_success = self.validate_image_size(image)
                if upload_success:
                    self.upload_poster(item, image.location)
            elif image.is_background and image.is_url:
                item.uploadArt(url=image.location)
            elif image.is_background:
                upload_success = self.validate_image_size(image)
                if upload_success:
                    item.uploadArt(filepath=image.location)
            elif image.is_url:
                item.uploadLogo(url=image.location)
            else:
                item.uploadLogo(filepath=image.location)
            self.reload(item, force=True)
            return upload_success
        except BadRequest as e:
            item.refresh()
            raise Failed(e)

    def edit_tags(self, attr, obj, add_tags=None, remove_tags=None, sync_tags=None, do_print=True, locked=True,
                  is_locked=None):

        display = ""
        final = ""
        attribute_translation[attr] if attr in attribute_translation else attr
        "similar" if attr == "similar_artist" else attr
        attr_display = attr.replace("_", " ").title()

        if add_tags or remove_tags or sync_tags is not None:
            _add_tags = add_tags if add_tags else []
            _remove_tags = remove_tags if remove_tags else []
            _sync_tags = sync_tags if sync_tags else []

            if attr == "label":
                _item_tags = self.EmbyServer.get_emby_item_tags(obj, self.Emby.get("Id"), from_cache=False)
            elif attr == "genre":
                _item_tags = self.EmbyServer.get_emby_item_genres(obj, self.Emby.get("Id"), from_cache=False)
            else:
                pass

            _add = [t for t in _add_tags + _sync_tags if t not in _item_tags]
            _remove = [t for t in _item_tags if (sync_tags is not None and t not in _sync_tags) or t in _remove_tags]

            # Berechne die finalen Tags
            final_tags = sorted(set([t for t in _item_tags if t not in _remove] + _add))
            final_tags = sorted(set(final_tags))  # Entferne eventuelle Duplikate
            if final_tags != sorted(set(_item_tags)):
                if attr == "label":
                    self.EmbyServer.set_tags(obj.ratingKey, final_tags)
                elif attr == "genre":
                    self.EmbyServer.set_genres(obj.ratingKey, final_tags)
                else:
                    raise WARNING(f"edit_tags: I won't edit {attr} with {final_tags}")

            if _add:
                display += f"+{', +'.join(_add)}"
            if _remove:
                if display:
                    display += ", "
                display += f"-{', -'.join(_remove)}"
            if is_locked is not None and not display and is_locked != locked:
                # self.edit_query(obj, {f"{actual}.locked": 1 if locked else 0})
                # todo: add emby locked?
                display = "Locked" if locked else "Unlocked"
            final = f"{obj.title[:25]:<25} | {attr_display} | {display}" if display else display
            if do_print and final:
                logger.info(final)
        return final[28:] if final else final

        # if add_tags and not remove_tags and not None:
        #     self.EmbyServer.add_tags(obj.ratingKey, add_tags)
        #     return
        raise WARNING(
            f"EMBY EDIT TAGS: {self} - {attr} - {obj} - {add_tags} - {remove_tags} - {sync_tags} - {locked} - {is_locked}")

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

    def find_poster_url(self, item):
        pass
    def get_all(self, builder_level=None, load=False):
        pass
    def get_all_native(self, builder_level=None, load=False):
        # todo remove
        pass
    def get_native_emby_item(self, emby_item_id):
        # todo remove
        pass
    def get_provider_ids(self, item):
        # used once, maybe remove
        pass
    def image_update(self, item, image, tmdb=None, title=None, poster=True):
        pass
    def item_labels(self, item):
        pass
    def item_posters(self, item, providers=None):
        pass
    def notify(self, text, collection=None, critical=True):
        pass
    def notify_delete(self, message):
        pass
    def reload(self, item, force=False):
        pass
    def upload_poster(self, item, image, url=False):
        pass
    def upload_poster_overlay(self, item, image, url=False):
        pass
    def upload_background(self, item, image, url=False):
        pass