import glob, logging, os, requests
from modules import util
from modules.meta import Metadata
from modules.util import Failed
from plexapi import utils
from plexapi.exceptions import BadRequest, NotFound, Unauthorized
from plexapi.collection import Collections
from plexapi.server import PlexServer
from retrying import retry
from ruamel import yaml
from urllib import parse

logger = logging.getLogger("Plex Meta Manager")

builders = ["plex_all", "plex_collectionless", "plex_search"]
search_translation = {
    "audio_language": "audioLanguage",
    "content_rating": "contentRating",
    "subtitle_language": "subtitleLanguage",
    "added": "addedAt",
    "originally_available": "originallyAvailableAt",
    "audience_rating": "audienceRating",
    "critic_rating": "rating",
    "user_rating": "userRating",
    "plays": "viewCount",
    "episode_title": "episode.title",
    "episode_added": "episode.addedAt",
    "episode_originally_available": "episode.originallyAvailableAt",
    "episode_year": "episode.year",
    "episode_user_rating": "episode.userRating",
    "episode_plays": "episode.viewCount"
}
modifier_translation = {
    "": "",
    ".not": "!",
    ".gt": "%3E%3E",
    ".gte": "%3E",
    ".lt": "%3C%3C",
    ".lte": "%3C",
    ".before": "%3C%3C",
    ".after": "%3E%3E",
    ".begins": "%3C",
    ".ends": "%3E"
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
collection_mode_keys = {-1: "default", 0: "hide", 1: "hideItems", 2: "showItems"}
collection_order_keys = {0: "release", 1: "alpha", 2: "custom"}
advance_keys = {
    "episode_sorting": ("episodeSort", episode_sorting_options),
    "keep_episodes": ("autoDeletionItemPolicyUnwatchedLibrary", keep_episodes_options),
    "delete_episodes": ("autoDeletionItemPolicyWatchedLibrary", delete_episodes_options),
    "season_display": ("flattenSeasons", season_display_options),
    "episode_ordering": ("showOrdering", episode_ordering_options),
    "metadata_language": ("languageOverride", metadata_language_options),
    "use_original_title": ("useOriginalTitle", use_original_title_options)
}
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
    "title", "title.and", "title.not", "title.begins", "title.ends",
    "studio", "studio.and", "studio.not", "studio.begins", "studio.ends",
    "actor", "actor.and", "actor.not",
    "audio_language", "audio_language.and", "audio_language.not",
    "collection", "collection.and", "collection.not",
    "content_rating", "content_rating.and", "content_rating.not",
    "country", "country.and", "country.not",
    "director", "director.and", "director.not",
    "genre", "genre.and", "genre.not",
    "label", "label.and", "label.not",
    "network", "network.and", "network.not",
    "producer", "producer.and", "producer.not",
    "subtitle_language", "subtitle_language.and", "subtitle_language.not",
    "writer", "writer.and", "writer.not",
    "decade", "resolution",
    "added", "added.not", "added.before", "added.after",
    "originally_available", "originally_available.not",
    "originally_available.before", "originally_available.after",
    "duration.gt", "duration.gte", "duration.lt", "duration.lte",
    "user_rating.gt", "user_rating.gte", "user_rating.lt", "user_rating.lte",
    "critic_rating.gt", "critic_rating.gte", "critic_rating.lt", "critic_rating.lte",
    "audience_rating.gt", "audience_rating.gte", "audience_rating.lt", "audience_rating.lte",
    "year", "year.not", "year.gt", "year.gte", "year.lt", "year.lte"
]
movie_only_searches = [
    "audio_language", "audio_language.and", "audio_language.not",
    "country", "country.and", "country.not",
    "subtitle_language", "subtitle_language.and", "subtitle_language.not",
    "decade", "resolution",
    "originally_available.before", "originally_available.after",
    "duration.gt", "duration.gte", "duration.lt", "duration.lte"
]
show_only_searches = [
    "network", "network.and", "network.not",
]
tmdb_searches = [
    "actor", "actor.and", "actor.not",
    "director", "director.and", "director.not",
    "producer", "producer.and", "producer.not",
    "writer", "writer.and", "writer.not"
]
sorts = {
    None: None,
    "title.asc": "titleSort:asc", "title.desc": "titleSort:desc",
    "originally_available.asc": "originallyAvailableAt:asc", "originally_available.desc": "originallyAvailableAt:desc",
    "critic_rating.asc": "rating:asc", "critic_rating.desc": "rating:desc",
    "audience_rating.asc": "audienceRating:asc", "audience_rating.desc": "audienceRating:desc",
    "duration.asc": "duration:asc", "duration.desc": "duration:desc",
    "added.asc": "addedAt:asc", "added.desc": "addedAt:desc"
}
modifiers = {
    ".and": "&",
    ".not": "!",
    ".begins": "<",
    ".ends": ">",
    ".before": "<<",
    ".after": ">>",
    ".gt": ">>",
    ".gte": "__gte",
    ".lt": "<<",
    ".lte": "__lte"
}
mod_displays = {
    "": "is",
    ".not": "is not",
    ".begins": "begins with",
    ".ends": "ends with",
    ".before": "is before",
    ".after": "is after",
    ".gt": "is greater than",
    ".gte": "is greater than or equal",
    ".lt": "is less than",
    ".lte": "is less than or equal"
}
tags = [
    "actor",
    "audio_language",
    "collection",
    "content_rating",
    "country",
    "director",
    "genre",
    "label",
    "network",
    "producer",
    "resolution",
    "studio",
    "subtitle_language",
    "writer"
]
smart_searches = [
    "all", "any",
    "title", "title.not", "title.begins", "title.ends",
    "studio", "studio.not", "studio.begins", "studio.ends",
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
    "decade", "resolution",
    "added", "added.not", "added.before", "added.after",
    "originally_available", "originally_available.not",
    "originally_available.before", "originally_available.after",
    "plays.gt", "plays.gte", "plays.lt", "plays.lte",
    "duration.gt", "duration.gte", "duration.lt", "duration.lte",
    "user_rating.gt", "user_rating.gte", "user_rating.lt", "user_rating.lte",
    "audience_rating.gt", "audience_rating.gte", "audience_rating.lt","audience_rating.lte",
    "critic_rating.gt", "critic_rating.gte", "critic_rating.lt","critic_rating.lte",
    "year", "year.not", "year.gt", "year.gte", "year.lt","year.lte",
    "episode_title", "episode_title.not", "episode_title.begins", "episode_title.ends",
    "episode_added", "episode_added.not", "episode_added.before", "episode_added.after",
    "episode_originally_available", "episode_originally_available.not",
    "episode_originally_available.before", "episode_originally_available.after",
    "episode_year", "episode_year.not", "episode_year.gt", "episode_year.gte", "episode_year.lt","episode_year.lte",
    "episode_user_rating.gt", "episode_user_rating.gte", "episode_user_rating.lt","episode_user_rating.lte",
    "episode_plays.gt", "episode_plays.gte", "episode_plays.lt", "episode_plays.lte"
]
movie_only_smart_searches = [
    "country", "country.not",
    "director", "director.not",
    "producer", "producer.not",
    "writer", "writer.not",
    "decade",
    "originally_available", "originally_available.not",
    "originally_available.before", "originally_available.after",
    "plays.gt", "plays.gte", "plays.lt", "plays.lte",
    "duration.gt", "duration.gte", "duration.lt", "duration.lte"
]
show_only_smart_searches = [
    "episode_title", "episode_title.not", "episode_title.begins", "episode_title.ends",
    "episode_added", "episode_added.not", "episode_added.before", "episode_added.after",
    "episode_originally_available", "episode_originally_available.not",
    "episode_originally_available.before", "episode_originally_available.after",
    "episode_year", "episode_year.not", "episode_year.gt", "episode_year.gte", "episode_year.lt","episode_year.lte",
    "episode_user_rating.gt", "episode_user_rating.gte", "episode_user_rating.lt","episode_user_rating.lte",
    "episode_plays.gt", "episode_plays.gte", "episode_plays.lt", "episode_plays.lte"
]
movie_smart_sorts = {
    "title.asc": "titleSort", "title.desc": "titleSort%3Adesc",
    "year.asc": "year", "year.desc": "year%3Adesc",
    "originally_available.asc": "originallyAvailableAt", "originally_available.desc": "originallyAvailableAt%3Adesc",
    "critic_rating.asc": "rating", "critic_rating.desc": "rating%3Adesc",
    "audience_rating.asc": "audienceRating", "audience_rating.desc": "audienceRating%3Adesc",
    "user_rating.asc": "userRating",  "user_rating.desc": "userRating%3Adesc",
    "content_rating.asc": "contentRating", "content_rating.desc": "contentRating%3Adesc",
    "duration.asc": "duration", "duration.desc": "duration%3Adesc",
    "plays.asc": "viewCount", "plays.desc": "viewCount%3Adesc",
    "added.asc": "addedAt", "added.desc": "addedAt%3Adesc",
    "random": "random"
}
show_smart_sorts = {
    "title.asc": "titleSort", "title.desc": "titleSort%3Adesc",
    "year.asc": "year", "year.desc": "year%3Adesc",
    "originally_available.asc": "originallyAvailableAt", "originally_available.desc": "originallyAvailableAt%3Adesc",
    "critic_rating.asc": "rating", "critic_rating.desc": "rating%3Adesc",
    "audience_rating.asc": "audienceRating", "audience_rating.desc": "audienceRating%3Adesc",
    "user_rating.asc": "userRating",  "user_rating.desc": "userRating%3Adesc",
    "content_rating.asc": "contentRating", "content_rating.desc": "contentRating%3Adesc",
    "added.asc": "addedAt", "added.desc": "addedAt%3Adesc",
    "episode_added.asc": "episode.addedAt", "episode_added.desc": "episode.addedAt%3Adesc",
    "random": "random"
}
season_smart_sorts = {
    "season.asc": "season.index%2Cseason.titleSort", "season.desc": "season.index%3Adesc%2Cseason.titleSort",
    "show.asc": "show.titleSort%2Cindex", "show.desc": "show.titleSort%3Adesc%2Cindex",
    "user_rating.asc": "userRating",  "user_rating.desc": "userRating%3Adesc",
    "added.asc": "addedAt", "added.desc": "addedAt%3Adesc",
    "random": "random"
}
episode_smart_sorts = {
    "title.asc": "titleSort", "title.desc": "titleSort%3Adesc",
    "show.asc": "show.titleSort%2Cseason.index%3AnullsLast%2Cepisode.index%3AnullsLast%2Cepisode.originallyAvailableAt%3AnullsLast%2Cepisode.titleSort%2Cepisode.id",
    "show.desc": "show.titleSort%3Adesc%2Cseason.index%3AnullsLast%2Cepisode.index%3AnullsLast%2Cepisode.originallyAvailableAt%3AnullsLast%2Cepisode.titleSort%2Cepisode.id",
    "year.asc": "year", "year.desc": "year%3Adesc",
    "originally_available.asc": "originallyAvailableAt", "originally_available.desc": "originallyAvailableAt%3Adesc",
    "critic_rating.asc": "rating", "critic_rating.desc": "rating%3Adesc",
    "audience_rating.asc": "audienceRating", "audience_rating.desc": "audienceRating%3Adesc",
    "user_rating.asc": "userRating",  "user_rating.desc": "userRating%3Adesc",
    "duration.asc": "duration", "duration.desc": "duration%3Adesc",
    "plays.asc": "viewCount", "plays.desc": "viewCount%3Adesc",
    "added.asc": "addedAt", "added.desc": "addedAt%3Adesc",
    "random": "random"
}
smart_types = {
    "movies": (1, movie_smart_sorts),
    "shows": (2, show_smart_sorts),
    "seasons": (3, season_smart_sorts),
    "episodes": (4, episode_smart_sorts),
}

class PlexAPI:
    def __init__(self, params, TMDb, TVDb):
        try:
            self.PlexServer = PlexServer(params["plex"]["url"], params["plex"]["token"], timeout=params["plex"]["timeout"])
        except Unauthorized:
            raise Failed("Plex Error: Plex token is invalid")
        except ValueError as e:
            raise Failed(f"Plex Error: {e}")
        except requests.exceptions.ConnectionError:
            util.print_stacktrace()
            raise Failed("Plex Error: Plex url is invalid")
        self.Plex = next((s for s in self.PlexServer.library.sections() if s.title == params["name"]), None)
        if not self.Plex:
            raise Failed(f"Plex Error: Plex Library {params['name']} not found")
        if self.Plex.type not in ["movie", "show"]:
            raise Failed(f"Plex Error: Plex Library must be a Movies or TV Shows library")

        self.agent = self.Plex.agent
        self.is_movie = self.Plex.type == "movie"
        self.is_show = self.Plex.type == "show"
        self.collections = []
        self.metadatas = []

        self.metadata_files = []
        for file_type, metadata_file in params["metadata_path"]:
            try:
                meta_obj = Metadata(self, file_type, metadata_file)
                if meta_obj.collections:
                    self.collections.extend([c for c in meta_obj.collections])
                if meta_obj.metadata:
                    self.metadatas.extend([c for c in meta_obj.metadata])
                self.metadata_files.append(meta_obj)
            except Failed as e:
                logger.error(e)

        if len(self.metadata_files) == 0:
            logger.info("")
            raise Failed("Metadata File Error: No valid metadata files found")

        if params["asset_directory"]:
            logger.info("")
            for ad in params["asset_directory"]:
                logger.info(f"Using Asset Directory: {ad}")

        self.TMDb = TMDb
        self.TVDb = TVDb
        self.Radarr = None
        self.Sonarr = None
        self.Tautulli = None
        self.name = params["name"]
        self.missing_path = os.path.join(params["default_dir"], f"{self.name}_missing.yml")
        self.metadata_path = params["metadata_path"]
        self.asset_directory = params["asset_directory"]
        self.asset_folders = params["asset_folders"]
        self.assets_for_all = params["assets_for_all"]
        self.sync_mode = params["sync_mode"]
        self.show_unmanaged = params["show_unmanaged"]
        self.show_filtered = params["show_filtered"]
        self.show_missing = params["show_missing"]
        self.save_missing = params["save_missing"]
        self.mass_genre_update = params["mass_genre_update"]
        self.mass_audience_rating_update = params["mass_audience_rating_update"]
        self.mass_update = self.mass_genre_update or self.mass_audience_rating_update
        self.plex = params["plex"]
        self.url = params["plex"]["url"]
        self.token = params["plex"]["token"]
        self.timeout = params["plex"]["timeout"]
        self.clean_bundles = params["plex"]["clean_bundles"]
        self.empty_trash = params["plex"]["empty_trash"]
        self.optimize = params["plex"]["optimize"]
        self.missing = {}
        self.run_again = []

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

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def get_all(self):
        return self.Plex.all()

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def server_search(self, data):
        return self.PlexServer.search(data)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def query(self, method):
        return method()

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def query_data(self, method, data):
        return method(data)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def collection_mode_query(self, collection, data):
        collection.modeUpdate(mode=data)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def collection_order_query(self, collection, data):
        collection.sortUpdate(sort=data)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def get_guids(self, item):
        return item.guids

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def edit_query(self, item, edits, advanced=False):
        if advanced:
            item.editAdvanced(**edits)
        else:
            item.edit(**edits)
        item.reload()

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def upload_image(self, item, location, poster=True, url=True):
        if poster and url:
            item.uploadPoster(url=location)
        elif poster:
            item.uploadPoster(filepath=location)
        elif url:
            item.uploadArt(url=location)
        else:
            item.uploadArt(filepath=location)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def get_search_choices(self, search_name, title=True):
        try:
            choices = {}
            for choice in self.Plex.listFilterChoices(search_name):
                choices[choice.title.lower()] = choice.title if title else choice.key
                choices[choice.key.lower()] = choice.title if title else choice.key
            return choices
        except NotFound:
            raise Failed(f"Collection Error: plex search attribute: {search_name} only supported with Plex's New TV Agent")

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def get_labels(self):
        return {label.title: label.key for label in self.Plex.listFilterChoices(field="label")}

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_plex)
    def _query(self, key, post=False, put=False):
        if post:                method = self.Plex._server._session.post
        elif put:               method = self.Plex._server._session.put
        else:                   method = None
        self.Plex._server.query(key, method=method)

    def create_smart_labels(self, title, sort):
        labels = self.get_labels()
        if title not in labels:
            raise Failed(f"Plex Error: Label: {title} does not exist")
        smart_type = 1 if self.is_movie else 2
        sort_type = movie_smart_sorts[sort] if self.is_movie else show_smart_sorts[sort]
        uri_args = f"?type={smart_type}&sort={sort_type}&label={labels[title]}"
        self.create_smart_collection(title, smart_type, uri_args)

    def create_smart_collection(self, title, smart_type, uri_args):
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
        self._query(f"/library/collections/{collection.ratingKey}/items{utils.joinArgs({'uri': self.build_smart_filter(uri_args)})}", put=True)

    def smart(self, collection):
        return utils.cast(bool, self.get_collection(collection)._data.attrib.get('smart', '0'))

    def smart_filter(self, collection):
        smart_filter = self.get_collection(collection)._data.attrib.get('content')
        return smart_filter[smart_filter.index("?"):]

    def validate_search_list(self, data, search_name, title=True, pairs=False):
        final_search = search_translation[search_name] if search_name in search_translation else search_name
        search_choices = self.get_search_choices(final_search, title=title)
        valid_list = []
        for value in util.get_list(data):
            if str(value).lower() in search_choices:
                if pairs:
                    valid_list.append((value, search_choices[str(value).lower()]))
                else:
                    valid_list.append(search_choices[str(value).lower()])
            else:
                raise Failed(f"Plex Error: {search_name}: {value} not found")
        return valid_list

    def get_collection(self, data):
        if isinstance(data, int):
            collection = self.fetchItem(data)
        elif isinstance(data, Collections):
            collection = data
        else:
            collection = util.choose_from_list(self.search(title=str(data), libtype="collection"), "collection", str(data), exact=True)
        if collection:
            return collection
        else:
            raise Failed(f"Plex Error: Collection {data} not found")

    def validate_collections(self, collections):
        valid_collections = []
        for collection in collections:
            try:                                        valid_collections.append(self.get_collection(collection))
            except Failed as e:                         logger.error(e)
        if len(valid_collections) == 0:
            raise Failed(f"Collection Error: No valid Plex Collections in {collections}")
        return valid_collections

    def get_items(self, method, data):
        logger.debug(f"Data: {data}")
        pretty = util.pretty_names[method] if method in util.pretty_names else method
        media_type = "Movie" if self.is_movie else "Show"
        items = []
        if method == "plex_all":
            logger.info(f"Processing {pretty} {media_type}s")
            items = self.get_all()
        elif method == "plex_search":
            search_terms = {}
            has_processed = False
            search_limit = None
            search_sort = None
            for search_method, search_data in data.items():
                if search_method == "limit":
                    search_limit = search_data
                elif search_method == "sort_by":
                    search_sort = search_data
                else:
                    search, modifier = os.path.splitext(str(search_method).lower())
                    final_search = search_translation[search] if search in search_translation else search
                    if search in ["added", "originally_available"] and modifier == "":
                        final_mod = ">>"
                    elif search in ["added", "originally_available"] and modifier == ".not":
                        final_mod = "<<"
                    elif search in ["critic_rating", "audience_rating"] and modifier == ".gt":
                        final_mod = "__gt"
                    elif search in ["critic_rating", "audience_rating"] and modifier == ".lt":
                        final_mod = "__lt"
                    else:
                        final_mod = modifiers[modifier] if modifier in modifiers else ""
                    final_method = f"{final_search}{final_mod}"

                    if search == "duration":
                        search_terms[final_method] = search_data * 60000
                    elif search in ["added", "originally_available"] and modifier in ["", ".not"]:
                        search_terms[final_method] = f"{search_data}d"
                    else:
                        search_terms[final_method] = search_data

                    if search in ["added", "originally_available"] or modifier in [".gt", ".gte", ".lt", ".lte", ".before", ".after"]:
                        ors = f"{search_method}({search_data}"
                    else:
                        ors = ""
                        conjunction = " AND " if final_mod == "&" else " OR "
                        for o, param in enumerate(search_data):
                            or_des = conjunction if o > 0 else f"{search_method}("
                            ors += f"{or_des}{param}"
                    if has_processed:
                        logger.info(f"\t\t      AND {ors})")
                    else:
                        logger.info(f"Processing {pretty}: {ors})")
                        has_processed = True
            if search_sort:
                logger.info(f"\t\t      SORT BY {search_sort})")
            if search_limit:
                logger.info(f"\t\t      LIMIT {search_limit})")
            logger.debug(f"Search: {search_terms}")
            return self.search(sort=sorts[search_sort], maxresults=search_limit, **search_terms)
        elif method == "plex_collectionless":
            good_collections = []
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
            length = 0
            for i, item in enumerate(all_items, 1):
                length = util.print_return(length, f"Processing: {i}/{len(all_items)} {item.title}")
                add_item = True
                self.query(item.reload)
                for collection in item.collections:
                    if collection.id in collection_indexes:
                        add_item = False
                        break
                if add_item:
                    items.append(item)
            util.print_end(length, f"Processed {len(all_items)} {'Movies' if self.is_movie else 'Shows'}")
        else:
            raise Failed(f"Plex Error: Method {method} not supported")
        if len(items) > 0:
            return items
        else:
            raise Failed("Plex Error: No Items found in Plex")

    def add_missing(self, collection, items, is_movie):
        col_name = collection.encode("ascii", "replace").decode()
        if col_name not in self.missing:
            self.missing[col_name] = {}
        section = "Movies Missing (TMDb IDs)" if is_movie else "Shows Missing (TVDb IDs)"
        if section not in self.missing[col_name]:
            self.missing[col_name][section] = {}
        for title, item_id in items:
            self.missing[col_name][section][int(item_id)] = str(title).encode("ascii", "replace").decode()
        with open(self.missing_path, "w"): pass
        try:
            yaml.round_trip_dump(self.missing, open(self.missing_path, "w"))
        except yaml.scanner.ScannerError as e:
            logger.error(f"YAML Error: {util.tab_new_lines(e)}")

    def get_collection_items(self, collection, smart_label_collection):
        if smart_label_collection:
            return self.get_labeled_items(collection.title if isinstance(collection, Collections) else str(collection))
        elif isinstance(collection, Collections):
            return self.query(collection.items)
        else:
            return []

    def get_collection_name_and_items(self, collection, smart_label_collection):
        name = collection.title if isinstance(collection, Collections) else str(collection)
        return name, self.get_collection_items(collection, smart_label_collection)

    def search_item(self, data, year=None):
        kwargs = {}
        if year is not None:
            kwargs["year"] = year
        return util.choose_from_list(self.search(title=str(data), **kwargs), "movie" if self.is_movie else "show", str(data), exact=True)

    def edit_item(self, item, name, item_type, edits, advanced=False):
        if len(edits) > 0:
            logger.debug(f"Details Update: {edits}")
            try:
                self.edit_query(item, edits, advanced=advanced)
                if advanced and "languageOverride" in edits:
                    self.query(item.refresh)
                logger.info(f"{item_type}: {name}{' Advanced' if advanced else ''} Details Update Successful")
            except BadRequest:
                util.print_stacktrace()
                logger.error(f"{item_type}: {name}{' Advanced' if advanced else ''} Details Update Failed")

    def update_item_from_assets(self, item, dirs=None):
        if dirs is None:
            dirs = self.asset_directory
        name = os.path.basename(os.path.dirname(item.locations[0]) if self.is_movie else item.locations[0])
        for ad in dirs:
            if self.asset_folders:
                if not os.path.isdir(os.path.join(ad, name)):
                    continue
                poster_filter = os.path.join(ad, name, "poster.*")
                background_filter = os.path.join(ad, name, "background.*")
            else:
                poster_filter = os.path.join(ad, f"{name}.*")
                background_filter = os.path.join(ad, f"{name}_background.*")
            matches = glob.glob(poster_filter)
            if len(matches) > 0:
                self.upload_image(item, os.path.abspath(matches[0]), url=False)
                logger.info(f"Detail: asset_directory updated {item.title}'s poster to [file] {os.path.abspath(matches[0])}")
            matches = glob.glob(background_filter)
            if len(matches) > 0:
                self.upload_image(item, os.path.abspath(matches[0]), poster=False, url=False)
                logger.info(f"Detail: asset_directory updated {item.title}'s background to [file] {os.path.abspath(matches[0])}")
            if self.is_show:
                for season in self.query(item.seasons):
                    if self.asset_folders:
                        season_filter = os.path.join(ad, name, f"Season{'0' if season.seasonNumber < 10 else ''}{season.seasonNumber}.*")
                    else:
                        season_filter = os.path.join(ad, f"{name}_Season{'0' if season.seasonNumber < 10 else ''}{season.seasonNumber}.*")
                    matches = glob.glob(season_filter)
                    if len(matches) > 0:
                        season_path = os.path.abspath(matches[0])
                        self.upload_image(season, season_path, url=False)
                        logger.info(f"Detail: asset_directory updated {item.title} Season {season.seasonNumber}'s poster to [file] {season_path}")
                    for episode in self.query(season.episodes):
                        if self.asset_folders:
                            episode_filter = os.path.join(ad, name, f"{episode.seasonEpisode.upper()}.*")
                        else:
                            episode_filter = os.path.join(ad, f"{name}_{episode.seasonEpisode.upper()}.*")
                        matches = glob.glob(episode_filter)
                        if len(matches) > 0:
                            episode_path = os.path.abspath(matches[0])
                            self.upload_image(episode, episode_path, url=False)
                            logger.info(f"Detail: asset_directory updated {item.title} {episode.seasonEpisode.upper()}'s poster to [file] {episode_path}")