import logging, os, plexapi, requests
from modules import builder, util
from modules.library import Library
from modules.util import Failed, ImageData
from plexapi import utils
from plexapi.exceptions import BadRequest, NotFound, Unauthorized
from plexapi.collection import Collection
from plexapi.server import PlexServer
from retrying import retry
from urllib import parse
from xml.etree.ElementTree import ParseError

logger = logging.getLogger("Plex Meta Manager")

builders = ["plex_all", "plex_collectionless", "plex_search"]
search_translation = {
    "episode_title": "episode.title",
    "network": "show.network",
    "critic_rating": "rating",
    "audience_rating": "audienceRating",
    "user_rating": "userRating",
    "episode_user_rating": "episode.userRating",
    "content_rating": "contentRating",
    "episode_year": "episode.year",
    "release": "originallyAvailableAt",
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
    "unplayed_episodes": "show.unwatchedLeaves"
}
show_translation = {
    "title": "show.title",
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
modifier_translation = {
    "": "", ".not": "!", ".is": "%3D", ".isnot": "!%3D", ".gt": "%3E%3E", ".gte": "%3E", ".lt": "%3C%3C", ".lte": "%3C",
    ".before": "%3C%3C", ".after": "%3E%3E", ".begins": "%3C", ".ends": "%3E"
}
episode_sorting_options = {"default": "-1", "oldest": "0", "newest": "1"}
keep_episodes_options = {"all": 0, "5_latest": 5, "3_latest": 3, "latest": 1, "past_3": -3, "past_7": -7, "past_30": -30}
delete_episodes_options = {"never": 0, "day": 1, "week": 7, "refresh": 100}
season_display_options = {"default": -1, "show": 0, "hide": 1}
episode_ordering_options = {"default": None, "tmdb_aired": "tmdbAiring", "tvdb_aired": "aired", "tvdb_dvd": "dvd", "tvdb_absolute": "absolute"}
plex_languages = ["default", "ar-SA", "ca-ES", "cs-CZ", "da-DK", "de-DE", "el-GR", "en-AU", "en-CA", "en-GB", "en-US",
                  "es-ES", "es-MX", "et-EE", "fa-IR", "fi-FI", "fr-CA", "fr-FR", "he-IL", "hi-IN", "hu-HU", "id-ID",
                  "it-IT", "ja-JP", "ko-KR", "lt-LT", "lv-LV", "nb-NO", "nl-NL", "pl-PL", "pt-BR", "pt-PT", "ro-RO",
                  "ru-RU", "sk-SK", "sv-SE", "th-TH", "tr-TR", "uk-UA", "vi-VN", "zh-CN", "zh-HK", "zh-TW"]
metadata_language_options = {lang.lower(): lang for lang in plex_languages}
metadata_language_options["default"] = None
use_original_title_options = {"default": -1, "no": 0, "yes": 1}
collection_mode_options = {
    "default": "default", "hide": "hide",
    "hide_items": "hideItems", "hideitems": "hideItems",
    "show_items": "showItems", "showitems": "showItems"
}
collection_order_options = ["release", "alpha", "custom"]
collection_level_options = ["episode", "season"]
collection_mode_keys = {-1: "default", 0: "hide", 1: "hideItems", 2: "showItems"}
collection_order_keys = {0: "release", 1: "alpha", 2: "custom"}
item_advance_keys = {
    "item_episode_sorting": ("episodeSort", episode_sorting_options),
    "item_keep_episodes": ("autoDeletionItemPolicyUnwatchedLibrary", keep_episodes_options),
    "item_delete_episodes": ("autoDeletionItemPolicyWatchedLibrary", delete_episodes_options),
    "item_season_display": ("flattenSeasons", season_display_options),
    "item_episode_ordering": ("showOrdering", episode_ordering_options),
    "item_metadata_language": ("languageOverride", metadata_language_options),
    "item_use_original_title": ("useOriginalTitle", use_original_title_options)
}
new_plex_agents = ["tv.plex.agents.movie", "tv.plex.agents.series"]
searches = [
    "title", "title.not", "title.is", "title.isnot", "title.begins", "title.ends",
    "studio", "studio.not", "studio.is", "studio.isnot", "studio.begins", "studio.ends",
    "actor", "actor.not",
    "audio_language", "audio_language.not",
    "collection", "collection.not",
    "content_rating", "content_rating.not",
    "country", "country.not",
    "director", "director.not",
    "genre", "genre.not",
    "label", "label.not",
    "network", "network.not",
    "producer", "producer.not",
    "subtitle_language", "subtitle_language.not",
    "writer", "writer.not",
    "decade", "resolution", "hdr", "unmatched", "duplicate", "unplayed", "progress", "trash",
    "last_played", "last_played.not", "last_played.before", "last_played.after",
    "added", "added.not", "added.before", "added.after",
    "release", "release.not", "release.before", "release.after",
    "duration.gt", "duration.gte", "duration.lt", "duration.lte",
    "plays.gt", "plays.gte", "plays.lt", "plays.lte",
    "user_rating.gt", "user_rating.gte", "user_rating.lt", "user_rating.lte",
    "critic_rating.gt", "critic_rating.gte", "critic_rating.lt", "critic_rating.lte",
    "audience_rating.gt", "audience_rating.gte", "audience_rating.lt", "audience_rating.lte",
    "year", "year.not", "year.gt", "year.gte", "year.lt", "year.lte",
    "unplayed_episodes", "episode_unplayed", "episode_duplicate", "episode_progress", "episode_unmatched",
    "episode_title", "episode_title.not", "episode_title.is", "episode_title.isnot", "episode_title.begins", "episode_title.ends",
    "episode_added", "episode_added.not", "episode_added.before", "episode_added.after",
    "episode_air_date", "episode_air_date.not", "episode_air_date.before", "episode_air_date.after",
    "episode_last_played", "episode_last_played.not", "episode_last_played.before", "episode_last_played.after",
    "episode_plays.gt", "episode_plays.gte", "episode_plays.lt", "episode_plays.lte",
    "episode_user_rating.gt", "episode_user_rating.gte", "episode_user_rating.lt", "episode_user_rating.lte",
    "episode_year", "episode_year.not", "episode_year.gt", "episode_year.gte", "episode_year.lt", "episode_year.lte"
]
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
    "country", "country.not", "director", "director.not", "producer", "producer.not", "writer", "writer.not",
    "decade", "duplicate", "unplayed", "progress",
    "duration.gt", "duration.gte", "duration.lt", "duration.lte"
]
show_only_searches = [
    "network", "network.not",
    "episode_title", "episode_title.not", "episode_title.is", "episode_title.isnot", "episode_title.begins", "episode_title.ends",
    "episode_added", "episode_added.not", "episode_added.before", "episode_added.after",
    "episode_air_date", "episode_air_date.not",
    "episode_air_date.before", "episode_air_date.after",
    "episode_last_played", "episode_last_played.not", "episode_last_played.before", "episode_last_played.after",
    "episode_plays.gt", "episode_plays.gte", "episode_plays.lt", "episode_plays.lte",
    "episode_user_rating.gt", "episode_user_rating.gte", "episode_user_rating.lt", "episode_user_rating.lte",
    "episode_year", "episode_year.not", "episode_year.gt", "episode_year.gte", "episode_year.lt", "episode_year.lte",
    "unplayed_episodes", "episode_unplayed", "episode_duplicate", "episode_progress", "episode_unmatched",
]
float_attributes = ["user_rating", "episode_user_rating", "critic_rating", "audience_rating"]
boolean_attributes = [
    "hdr", "unmatched", "duplicate", "unplayed", "progress", "trash",
    "unplayed_episodes", "episode_unplayed", "episode_duplicate", "episode_progress", "episode_unmatched",
]
tmdb_attributes = ["actor", "director", "producer", "writer"]
date_attributes = ["added", "episode_added", "release", "episode_air_date", "last_played", "episode_last_played", "first_episode_aired", "last_episode_aired"]
number_attributes = ["plays", "episode_plays", "duration", "tmdb_vote_count"] + date_attributes
search_display = {"added": "Date Added", "release": "Release Date", "hdr": "HDR", "progress": "In Progress", "episode_progress": "Episode In Progress"}
tags = [
    "actor", "audio_language", "collection", "content_rating", "country", "director", "genre", "label",
    "network", "producer", "resolution", "studio", "subtitle_language", "writer"
]
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
    "plays.asc": "viewCount", "plays.desc": "viewCount%3Adesc",
    "added.asc": "addedAt", "added.desc": "addedAt%3Adesc",
    "random": "random"
}
show_sorts = {
    "title.asc": "titleSort", "title.desc": "titleSort%3Adesc",
    "year.asc": "year", "year.desc": "year%3Adesc",
    "originally_available.asc": "originallyAvailableAt", "originally_available.desc": "originallyAvailableAt%3Adesc",
    "release.asc": "originallyAvailableAt", "release.desc": "originallyAvailableAt%3Adesc",
    "critic_rating.asc": "rating", "critic_rating.desc": "rating%3Adesc",
    "audience_rating.asc": "audienceRating", "audience_rating.desc": "audienceRating%3Adesc",
    "user_rating.asc": "userRating",  "user_rating.desc": "userRating%3Adesc",
    "content_rating.asc": "contentRating", "content_rating.desc": "contentRating%3Adesc",
    "added.asc": "addedAt", "added.desc": "addedAt%3Adesc",
    "episode_added.asc": "episode.addedAt", "episode_added.desc": "episode.addedAt%3Adesc",
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
    "release.asc": "originallyAvailableAt", "release.desc": "originallyAvailableAt%3Adesc",
    "critic_rating.asc": "rating", "critic_rating.desc": "rating%3Adesc",
    "audience_rating.asc": "audienceRating", "audience_rating.desc": "audienceRating%3Adesc",
    "user_rating.asc": "userRating",  "user_rating.desc": "userRating%3Adesc",
    "duration.asc": "duration", "duration.desc": "duration%3Adesc",
    "plays.asc": "viewCount", "plays.desc": "viewCount%3Adesc",
    "added.asc": "addedAt", "added.desc": "addedAt%3Adesc",
    "random": "random"
}
sort_types = {"movies": (1, movie_sorts), "shows": (2, show_sorts), "seasons": (3, season_sorts), "episodes": (4, episode_sorts)}

class Plex(Library):
    def __init__(self, config, params):
        super().__init__(config, params)
        self.plex = params["plex"]
        self.url = params["plex"]["url"]
        self.token = params["plex"]["token"]
        self.timeout = params["plex"]["timeout"]
        logger.info("")
        try:
            self.PlexServer = PlexServer(baseurl=self.url, token=self.token, session=self.config.session, timeout=self.timeout)
        except Unauthorized:
            raise Failed("Plex Error: Plex token is invalid")
        except ValueError as e:
            raise Failed(f"Plex Error: {e}")
        except (requests.exceptions.ConnectionError, ParseError):
            util.print_stacktrace()
            raise Failed("Plex Error: Plex url is invalid")
        self.Plex = None
        library_names = []
        for s in self.PlexServer.library.sections():
            library_names.append(s.title)
            if s.title == params["name"]:
                self.Plex = s
                break
        if not self.Plex:
            raise Failed(f"Plex Error: Plex Library {params['name']} not found. Options: {library_names}")
        if self.Plex.type in ["movie", "show"]:
            self.type = self.Plex.type.capitalize()
        else:
            raise Failed(f"Plex Error: Plex Library must be a Movies or TV Shows library")

        self.agent = self.Plex.agent
        self.is_movie = self.type == "Movie"
        self.is_show = self.type == "Show"
        self.is_other = self.agent == "com.plexapp.agents.none"
        if self.is_other:
            self.type = "Video"
        if self.tmdb_collections and self.is_show:
            self.tmdb_collections = None
            logger.error("Config Error: tmdb_collections only work with Movie Libraries.")

    def set_server_preroll(self, preroll):
        self.PlexServer.settings.get('cinemaTrailersPrerollID').set(preroll)
        self.PlexServer.settings.save()

    def get_all_collections(self):
        return self.search(libtype="collection")

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def search(self, title=None, libtype=None, sort=None, maxresults=None, **kwargs):
        return self.Plex.search(title=title, sort=sort, maxresults=maxresults, libtype=libtype, **kwargs)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def exact_search(self, title, libtype=None, year=None):
        if year:
            terms = {"title=": title, "year": year}
        else:
            terms = {"title=": title}
        return self.Plex.search(libtype=libtype, **terms)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def get_labeled_items(self, label):
        return self.Plex.search(label=label)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def fetchItem(self, data):
        return self.PlexServer.fetchItem(data)

    def get_all(self):
        logger.info(f"Loading All {self.type}s from Library: {self.name}")
        key = f"/library/sections/{self.Plex.key}/all?includeGuids=1&type={utils.searchType(self.Plex.TYPE)}"
        container_start = 0
        container_size = plexapi.X_PLEX_CONTAINER_SIZE
        results = []
        while self.Plex._totalViewSize is None or container_start <= self.Plex._totalViewSize:
            results.extend(self.fetchItems(key, container_start, container_size))
            util.print_return(f"Loaded: {container_start}/{self.Plex._totalViewSize}")
            container_start += container_size
        logger.info(util.adjust_space(f"Loaded {self.Plex._totalViewSize} {self.type}s"))
        return results

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def fetchItems(self, key, container_start, container_size):
        return self.Plex.fetchItems(key, container_start=container_start, container_size=container_size)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def query(self, method):
        return method()

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def query_data(self, method, data):
        return method(data)

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
    def reload(self, item):
        try:
            item.reload(checkFiles=False, includeAllConcerts=False, includeBandwidths=False, includeChapters=False,
                        includeChildren=False, includeConcerts=False, includeExternalMedia=False, includeExtras=False,
                        includeFields=False, includeGeolocation=False, includeLoudnessRamps=False, includeMarkers=False,
                        includeOnDeck=False, includePopularLeaves=False, includeRelated=False,
                        includeRelatedCount=0, includeReviews=False, includeStations=False)
        except (BadRequest, NotFound) as e:
            util.print_stacktrace()
            raise Failed(f"Item Failed to Load: {e}")

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def edit_query(self, item, edits, advanced=False):
        if advanced:
            item.editAdvanced(**edits)
        else:
            item.edit(**edits)
        self.reload(item)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def _upload_image(self, item, image):
        try:
            if image.is_poster and image.is_url:
                item.uploadPoster(url=image.location)
            elif image.is_poster:
                item.uploadPoster(filepath=image.location)
            elif image.is_url:
                item.uploadArt(url=image.location)
            else:
                item.uploadArt(filepath=image.location)
            self.reload(item)
        except BadRequest as e:
            raise Failed(e)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def upload_file_poster(self, item, image):
        item.uploadPoster(filepath=image)
        self.reload(item)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def get_search_choices(self, search_name, title=True):
        final_search = search_translation[search_name] if search_name in search_translation else search_name
        final_search = show_translation[final_search] if self.is_show and final_search in show_translation else final_search
        try:
            choices = {}
            for choice in self.Plex.listFilterChoices(final_search):
                choices[choice.title.lower()] = choice.title if title else choice.key
                choices[choice.key.lower()] = choice.title if title else choice.key
            return choices
        except NotFound:
            logger.debug(f"Search Attribute: {final_search}")
            raise Failed(f"Collection Error: plex search attribute: {search_name} not supported")

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def get_labels(self):
        return {label.title: label.key for label in self.Plex.listFilterChoices(field="label")}

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def _query(self, key, post=False, put=False):
        if post:                method = self.Plex._server._session.post
        elif put:               method = self.Plex._server._session.put
        else:                   method = None
        return self.Plex._server.query(key, method=method)

    def alter_collection(self, item, collection, smart_label_collection=False, add=True):
        if smart_label_collection:
            self.query_data(item.addLabel if add else item.removeLabel, collection)
        else:
            locked = True
            if self.agent in ["tv.plex.agents.movie", "tv.plex.agents.series"]:
                field = next((f for f in item.fields if f.name == "collection"), None)
                locked = field is not None
            self.query_collection(item, collection, locked=locked, add=add)

    def move_item(self, collection, item, after=None):
        key = f"{collection.key}/items/{item}/move"
        if after:
            key += f"?after={after}"
        self._query(key, put=True)

    def smart_label_url(self, title, sort):
        labels = self.get_labels()
        if title not in labels:
            raise Failed(f"Plex Error: Label: {title} does not exist")
        smart_type = 1 if self.is_movie else 2
        sort_type = movie_sorts[sort] if self.is_movie else show_sorts[sort]
        return smart_type, f"?type={smart_type}&sort={sort_type}&label={labels[title]}"

    def test_smart_filter(self, uri_args):
        logger.debug(f"Smart Collection Test: {uri_args}")
        test_items = self.get_filter_items(uri_args)
        if len(test_items) < 1:
            raise Failed(f"Plex Error: No items for smart filter: {uri_args}")

    def create_smart_collection(self, title, smart_type, uri_args):
        self.test_smart_filter(uri_args)
        args = {
            "type": smart_type,
            "title": title,
            "smart": 1,
            "sectionId": self.Plex.key,
            "uri": self.build_smart_filter(uri_args)
        }
        self._query(f"/library/collections{utils.joinArgs(args)}", post=True)

    def get_smart_filter_from_uri(self, uri):
        smart_filter = parse.parse_qs(parse.urlparse(uri.replace("/#!/", "/")).query)["key"][0]
        args = smart_filter[smart_filter.index("?"):]
        return self.build_smart_filter(args), int(args[args.index("type=") + 5:args.index("type=") + 6])

    def build_smart_filter(self, uri_args):
        return f"server://{self.PlexServer.machineIdentifier}/com.plexapp.plugins.library/library/sections/{self.Plex.key}/all{uri_args}"

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

    def get_collection(self, data):
        if isinstance(data, int):
            return self.fetchItem(data)
        elif isinstance(data, Collection):
            return data
        else:
            for d in self.search(title=str(data), libtype="collection"):
                if d.title == data:
                    return d
        raise Failed(f"Plex Error: Collection {data} not found")

    def validate_collections(self, collections):
        valid_collections = []
        for collection in collections:
            try:                                        valid_collections.append(self.get_collection(collection))
            except Failed as e:                         logger.error(e)
        if len(valid_collections) == 0:
            raise Failed(f"Collection Error: No valid Plex Collections in {collections}")
        return valid_collections

    def get_rating_keys(self, method, data):
        items = []
        if method == "plex_all":
            logger.info(f"Processing Plex All {self.type}s")
            items = self.get_all()
        elif method == "plex_search":
            util.print_multiline(data[1], info=True)
            items = self.get_filter_items(data[2])
        elif method == "plex_collectionless":
            good_collections = []
            logger.info(f"Processing Plex Collectionless")
            logger.info("Collections Excluded")
            for col in self.get_all_collections():
                keep_collection = True
                for pre in data["exclude_prefix"]:
                    if col.title.startswith(pre) or (col.titleSort and col.titleSort.startswith(pre)):
                        keep_collection = False
                        logger.info(f"{col.title} excluded by prefix match {pre}")
                        break
                if keep_collection:
                    for ext in data["exclude"]:
                        if col.title == ext or (col.titleSort and col.titleSort == ext):
                            keep_collection = False
                            logger.info(f"{col.title} excluded by exact match")
                            break
                if keep_collection:
                    logger.info(f"Collection Passed: {col.title}")
                    good_collections.append(col)
            logger.info("")
            logger.info("Collections Not Excluded (Items in these collections are not added to Collectionless)")
            for col in good_collections:
                logger.info(col.title)
            collection_indexes = [c.index for c in good_collections]
            all_items = self.get_all()
            for i, item in enumerate(all_items, 1):
                util.print_return(f"Processing: {i}/{len(all_items)} {item.title}")
                add_item = True
                self.reload(item)
                for collection in item.collections:
                    if collection.id in collection_indexes:
                        add_item = False
                        break
                if add_item:
                    items.append(item)
            logger.info(util.adjust_space(f"Processed {len(all_items)} {self.type}s"))
        else:
            raise Failed(f"Plex Error: Method {method} not supported")
        if len(items) > 0:
            ids = [item.ratingKey for item in items]
            logger.debug("")
            logger.debug(f"{len(ids)} Keys Found: {ids}")
            return ids
        else:
            raise Failed("Plex Error: No Items found in Plex")

    def get_collection_items(self, collection, smart_label_collection):
        if smart_label_collection:
            return self.get_labeled_items(collection.title if isinstance(collection, Collection) else str(collection))
        elif isinstance(collection, Collection):
            if collection.smart:
                return self.get_filter_items(self.smart_filter(collection))
            else:
                return self.query(collection.items)
        else:
            return []

    def get_filter_items(self, uri_args):
        key = f"/library/sections/{self.Plex.key}/all{uri_args}"
        return self.Plex._search(key, None, 0, plexapi.X_PLEX_CONTAINER_SIZE)

    def get_collection_name_and_items(self, collection, smart_label_collection):
        name = collection.title if isinstance(collection, Collection) else str(collection)
        return name, self.get_collection_items(collection, smart_label_collection)

    def get_tmdb_from_map(self, item):
        return self.movie_rating_key_map[item.ratingKey] if item.ratingKey in self.movie_rating_key_map else None

    def get_tvdb_from_map(self, item):
        return self.show_rating_key_map[item.ratingKey] if item.ratingKey in self.show_rating_key_map else None

    def search_item(self, data, year=None):
        kwargs = {}
        if year is not None:
            kwargs["year"] = year
        for d in self.search(title=str(data), **kwargs):
            if d.title == data:
                return d
        return None

    def edit_item(self, item, name, item_type, edits, advanced=False):
        if len(edits) > 0:
            logger.debug(f"Details Update: {edits}")
            try:
                self.edit_query(item, edits, advanced=advanced)
                if advanced and ("languageOverride" in edits or "useOriginalTitle" in edits):
                    self.query(item.refresh)
                logger.info(f"{item_type}: {name}{' Advanced' if advanced else ''} Details Update Successful")
                return True
            except BadRequest:
                util.print_stacktrace()
                logger.error(f"{item_type}: {name}{' Advanced' if advanced else ''} Details Update Failed")
        return False

    def edit_tags(self, attr, obj, add_tags=None, remove_tags=None, sync_tags=None):
        display = ""
        key = builder.filter_translation[attr] if attr in builder.filter_translation else attr
        if add_tags or remove_tags or sync_tags is not None:
            _add_tags = add_tags if add_tags else []
            _remove_tags = [t.lower() for t in remove_tags] if remove_tags else []
            _sync_tags = [t.lower() for t in sync_tags] if sync_tags else []
            try:
                self.reload(obj)
                _item_tags = [item_tag.tag.lower() for item_tag in getattr(obj, key)]
            except BadRequest:
                _item_tags = []
            _add = [f"{t[:1].upper()}{t[1:]}" for t in _add_tags + _sync_tags if t.lower() not in _item_tags]
            _remove = [t for t in _item_tags if (sync_tags is not None and t not in _sync_tags) or t in _remove_tags]
            if _add:
                self.query_data(getattr(obj, f"add{attr.capitalize()}"), _add)
                display += f"+{', +'.join(_add)}"
            if _remove:
                self.query_data(getattr(obj, f"remove{attr.capitalize()}"), _remove)
                display += f"-{', -'.join(_remove)}"
            if len(display) > 0:
                logger.info(f"{obj.title[:25]:<25} | {attr.capitalize()} | {display}")
        return len(display) > 0

    def update_item_from_assets(self, item, overlay=None, create=False):
        name = os.path.basename(os.path.dirname(str(item.locations[0])) if self.is_movie else str(item.locations[0]))
        found_folder = False
        poster = None
        background = None
        for ad in self.asset_directory:
            item_dir = None
            if self.asset_folders:
                if os.path.isdir(os.path.join(ad, name)):
                    item_dir = os.path.join(ad, name)
                else:
                    matches = util.glob_filter(os.path.join(ad, "*", name))
                    if len(matches) > 0:
                        item_dir = os.path.abspath(matches[0])
                if item_dir is None:
                    continue
                found_folder = True
                poster_filter = os.path.join(item_dir, "poster.*")
                background_filter = os.path.join(item_dir, "background.*")
            else:
                poster_filter = os.path.join(ad, f"{name}.*")
                background_filter = os.path.join(ad, f"{name}_background.*")
            matches = util.glob_filter(poster_filter)
            if len(matches) > 0:
                poster = ImageData("asset_directory", os.path.abspath(matches[0]), prefix=f"{item.title}'s ", is_url=False)
            matches = util.glob_filter(background_filter)
            if len(matches) > 0:
                background = ImageData("asset_directory", os.path.abspath(matches[0]), prefix=f"{item.title}'s ", is_poster=False, is_url=False)
            if poster or background:
                self.upload_images(item, poster=poster, background=background, overlay=overlay)
            if self.is_show:
                for season in self.query(item.seasons):
                    season_name = f"Season{'0' if season.seasonNumber < 10 else ''}{season.seasonNumber}"
                    if item_dir:
                        season_poster_filter = os.path.join(item_dir, f"{season_name}.*")
                        season_background_filter = os.path.join(item_dir, f"{season_name}_background.*")
                    else:
                        season_poster_filter = os.path.join(ad, f"{name}_{season_name}.*")
                        season_background_filter = os.path.join(ad, f"{name}_{season_name}_background.*")
                    matches = util.glob_filter(season_poster_filter)
                    season_poster = None
                    season_background = None
                    if len(matches) > 0:
                        season_poster = ImageData("asset_directory", os.path.abspath(matches[0]), prefix=f"{item.title} Season {season.seasonNumber}'s ", is_url=False)
                    matches = util.glob_filter(season_background_filter)
                    if len(matches) > 0:
                        season_background = ImageData("asset_directory", os.path.abspath(matches[0]), prefix=f"{item.title} Season {season.seasonNumber}'s ", is_poster=False, is_url=False)
                    if season_poster or season_background:
                        self.upload_images(season, poster=season_poster, background=season_background)
                    for episode in self.query(season.episodes):
                        if item_dir:
                            episode_filter = os.path.join(item_dir, f"{episode.seasonEpisode.upper()}.*")
                        else:
                            episode_filter = os.path.join(ad, f"{name}_{episode.seasonEpisode.upper()}.*")
                        matches = util.glob_filter(episode_filter)
                        if len(matches) > 0:
                            episode_poster = ImageData("asset_directory", os.path.abspath(matches[0]), prefix=f"{item.title} {episode.seasonEpisode.upper()}'s ", is_url=False)
                            self.upload_images(episode, poster=episode_poster)
        if not poster and overlay:
            self.upload_images(item, overlay=overlay)
        if create and self.asset_folders and not found_folder:
            os.makedirs(os.path.join(self.asset_directory[0], name), exist_ok=True)
            logger.info(f"Asset Directory Created: {os.path.join(self.asset_directory[0], name)}")
        elif not overlay and self.asset_folders and not found_folder:
            logger.error(f"Asset Warning: No asset folder found called '{name}'")
        elif not poster and not background and self.show_missing_assets:
            logger.error(f"Asset Warning: No poster or background found in an assets folder for '{name}'")
