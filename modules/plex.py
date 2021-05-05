import glob, logging, os, re, requests
from datetime import datetime, timedelta
from modules import util
from modules.util import Failed
from plexapi import utils
from plexapi.exceptions import BadRequest, NotFound, Unauthorized
from plexapi.collection import Collections
from plexapi.server import PlexServer
from plexapi.video import Movie, Show
from retrying import retry
from ruamel import yaml
from urllib import parse

logger = logging.getLogger("Plex Meta Manager")

builders = ["plex_all", "plex_collection", "plex_collectionless", "plex_search"]
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
filter_alias = {
    "actor": "actors",
    "audience_rating": "audienceRating",
    "collection": "collections",
    "content_rating": "contentRating",
    "country": "countries",
    "critic_rating": "rating",
    "director": "directors",
    "genre": "genres",
    "originally_available": "originallyAvailableAt",
    "tmdb_vote_count": "vote_count",
    "user_rating": "userRating",
    "writer": "writers"
}
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
    "audience_rating.gt", "audience_rating.gte", "audience_rating.lt", "audience_rating.lte"\
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

        logger.info(f"Using Metadata File: {params['metadata_path']}")
        try:
            self.data, ind, bsi = yaml.util.load_yaml_guess_indent(open(params["metadata_path"], encoding="utf-8"))
        except yaml.scanner.ScannerError as ye:
            raise Failed(f"YAML Error: {util.tab_new_lines(ye)}")
        except Exception as e:
            util.print_stacktrace()
            raise Failed(f"YAML Error: {e}")

        def get_dict(attribute):
            if attribute in self.data:
                if self.data[attribute]:
                    if isinstance(self.data[attribute], dict):
                        return self.data[attribute]
                    else:
                        logger.warning(f"Config Warning: {attribute} must be a dictionary")
                else:
                    logger.warning(f"Config Warning: {attribute} attribute is blank")
            return None

        self.metadata = get_dict("metadata")
        self.templates = get_dict("templates")
        self.collections = get_dict("collections")

        if self.metadata is None and self.collections is None:
            raise Failed("YAML Error: metadata or collections attribute is required")

        if params["asset_directory"]:
            for ad in params["asset_directory"]:
                logger.info(f"Using Asset Directory: {ad}")

        self.TMDb = TMDb
        self.TVDb = TVDb
        self.Radarr = None
        self.Sonarr = None
        self.Tautulli = None
        self.name = params["name"]
        self.missing_path = os.path.join(os.path.dirname(os.path.abspath(params["metadata_path"])), f"{os.path.splitext(os.path.basename(params['metadata_path']))[0]}_missing.yml")
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
        self.missing = {}
        self.run_again = []

    def get_all_collections(self):
        return self.search(libtype="collection")

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def search(self, title=None, libtype=None, sort=None, maxresults=None, **kwargs):
        return self.Plex.search(title=title, sort=sort, maxresults=maxresults, libtype=libtype, **kwargs)

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def get_labeled_items(self, label):
        return self.Plex.search(label=label)

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def fetchItem(self, data):
        return self.PlexServer.fetchItem(data)

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def get_all(self):
        return self.Plex.all()

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def server_search(self, data):
        return self.PlexServer.search(data)

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def query(self, method):
        return method()

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def query_data(self, method, data):
        return method(data)

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def collection_mode_query(self, collection, data):
        collection.modeUpdate(mode=data)

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def collection_order_query(self, collection, data):
        collection.sortUpdate(sort=data)

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def edit_query(self, item, edits, advance=False):
        if advance:
            item.editAdvanced(**edits)
        else:
            item.edit(**edits)
        item.reload()

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
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

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def get_labels(self):
        return {label.title: label.key for label in self.Plex.listFilterChoices(field="label")}

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
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

    def validate_search_list(self, data, search_name, fail=False, title=True, pairs=False):
        final_search = search_translation[search_name] if search_name in search_translation else search_name
        search_choices = self.get_search_choices(final_search, title=title)
        valid_list = []
        for value in util.get_list(data):
            if str(value).lower() in search_choices:
                if pairs:
                    valid_list.append((value, search_choices[str(value).lower()]))
                else:
                    valid_list.append(search_choices[str(value).lower()])
            elif fail:
                raise Failed(f"Plex Error: {search_name}: {value} not found")
            else:
                logger.error(f"Plex Error: {search_name}: {value} not found")
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

    def get_items(self, method, data, status_message=True):
        if status_message:
            logger.debug(f"Data: {data}")
        pretty = util.pretty_names[method] if method in util.pretty_names else method
        media_type = "Movie" if self.is_movie else "Show"
        items = []
        if method == "plex_all":
            if status_message:
                logger.info(f"Processing {pretty} {media_type}s")
            items = self.get_all()
        elif method == "plex_collection":
            if status_message:
                logger.info(f"Processing {pretty} {data}")
            items = data.items()
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

                    if status_message:
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
            if status_message:
                if search_sort:
                    logger.info(f"\t\t      SORT BY {search_sort})")
                if search_limit:
                    logger.info(f"\t\t      LIMIT {search_limit})")
                logger.debug(f"Search: {search_terms}")
            return self.search(sort=sorts[search_sort], maxresults=search_limit, **search_terms)
        elif method == "plex_collectionless":
            good_collections = []
            if status_message:
                logger.info("Collections Excluded")
            for col in self.get_all_collections():
                keep_collection = True
                for pre in data["exclude_prefix"]:
                    if col.title.startswith(pre) or (col.titleSort and col.titleSort.startswith(pre)):
                        keep_collection = False
                        if status_message:
                            logger.info(f"{col.title} excluded by prefix match {pre}")
                        break
                if keep_collection:
                    for ext in data["exclude"]:
                        if col.title == ext or (col.titleSort and col.titleSort == ext):
                            keep_collection = False
                            if status_message:
                                logger.info(f"{col.title} excluded by exact match")
                            break
                if keep_collection:
                    logger.info(f"Collection Passed: {col.title}")
                    good_collections.append(col)
            if status_message:
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

    def add_to_collection(self, collection, items, filters, show_filtered, smart, rating_key_map, movie_map, show_map):
        name, collection_items = self.get_collection_name_and_items(collection, smart)
        total = len(items)
        max_length = len(str(total))
        length = 0
        for i, item in enumerate(items, 1):
            try:
                current = self.fetchItem(item.ratingKey if isinstance(item, (Movie, Show)) else int(item))
                if not isinstance(current, (Movie, Show)):
                    raise NotFound
            except (BadRequest, NotFound):
                logger.error(f"Plex Error: Item {item} not found")
                continue
            match = True
            if filters:
                length = util.print_return(length, f"Filtering {(' ' * (max_length - len(str(i)))) + str(i)}/{total} {current.title}")
                for filter_method, filter_data in filters:
                    modifier = filter_method[-4:]
                    method = filter_method[:-4] if modifier in [".not", ".lte", ".gte"] else filter_method
                    method_name = filter_alias[method] if method in filter_alias else method
                    if method_name == "max_age":
                        threshold_date = datetime.now() - timedelta(days=filter_data)
                        if current.originallyAvailableAt is None or current.originallyAvailableAt < threshold_date:
                            match = False
                            break
                    elif method_name == "original_language":
                        movie = None
                        for key, value in movie_map.items():
                            if current.ratingKey in value:
                                try:
                                    movie = self.TMDb.get_movie(key)
                                    break
                                except Failed:
                                    pass
                        if movie is None:
                            logger.warning(f"Filter Error: No TMDb ID found for {current.title}")
                            continue
                        if (modifier == ".not" and movie.original_language in filter_data) or (modifier != ".not" and movie.original_language not in filter_data):
                            match = False
                            break
                    elif method_name == "audio_track_title":
                        jailbreak = False
                        for media in current.media:
                            for part in media.parts:
                                for audio in part.audioStreams():
                                    for check_title in filter_data:
                                        title = audio.title if audio.title else ""
                                        if check_title.lower() in title.lower():
                                            jailbreak = True
                                            break
                                    if jailbreak: break
                                if jailbreak: break
                            if jailbreak: break
                        if (jailbreak and modifier == ".not") or (not jailbreak and modifier != ".not"):
                            match = False
                            break
                    elif method_name == "filepath":
                        jailbreak = False
                        for location in current.locations:
                            for location_prefix in filter_data:
                                if location.startswith(location_prefix):
                                    jailbreak = True
                                    break
                            if jailbreak: break
                        if (jailbreak and modifier == ".not") or (not jailbreak and modifier != ".not"):
                            match = False
                            break
                    elif modifier in [".gte", ".lte"]:
                        if method_name == "vote_count":
                            tmdb_item = None
                            for key, value in movie_map.items():
                                if current.ratingKey in value:
                                    try:
                                        tmdb_item = self.TMDb.get_movie(key) if self.is_movie else self.TMDb.get_show(key)
                                        break
                                    except Failed:
                                        pass
                            if tmdb_item is None:
                                logger.warning(f"Filter Error: No TMDb ID found for {current.title}")
                                continue
                            attr = tmdb_item.vote_count
                        else:
                            attr = getattr(current, method_name) / 60000 if method_name == "duration" else getattr(current, method_name)
                        if attr is None or (modifier == ".lte" and attr > filter_data) or (modifier == ".gte" and attr < filter_data):
                            match = False
                            break
                    else:
                        attrs = []
                        if method_name in ["video_resolution", "audio_language", "subtitle_language"]:
                            for media in current.media:
                                if method_name == "video_resolution":
                                    attrs.extend([media.videoResolution])
                                for part in media.parts:
                                    if method_name == "audio_language":
                                        attrs.extend([a.language for a in part.audioStreams()])
                                    if method_name == "subtitle_language":
                                        attrs.extend([s.language for s in part.subtitleStreams()])
                        elif method_name in ["contentRating", "studio", "year", "rating", "originallyAvailableAt"]:
                            attrs = [str(getattr(current, method_name))]
                        elif method_name in ["actors", "countries", "directors", "genres", "writers", "collections"]:
                            attrs = [getattr(x, "tag") for x in getattr(current, method_name)]
                        else:
                            raise Failed(f"Filter Error: filter: {method_name} not supported")

                        if (not list(set(filter_data) & set(attrs)) and modifier != ".not") or (list(set(filter_data) & set(attrs)) and modifier == ".not"):
                            match = False
                            break
                length = util.print_return(length, f"Filtering {(' ' * (max_length - len(str(i)))) + str(i)}/{total} {current.title}")
            if match:
                util.print_end(length, f"{name} Collection | {'=' if current in collection_items else '+'} | {current.title}")
                if current in collection_items:             rating_key_map[current.ratingKey] = None
                elif smart:                                 self.query_data(current.addLabel, name)
                else:                                       self.query_data(current.addCollection, name)
            elif show_filtered is True:
                logger.info(f"{name} Collection | X | {current.title}")
        media_type = f"{'Movie' if self.is_movie else 'Show'}{'s' if total > 1 else ''}"
        util.print_end(length, f"{total} {media_type} Processed")
        return rating_key_map

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

    def update_metadata(self, TMDb, test):
        logger.info("")
        util.separator(f"{self.name} Library Metadata")
        logger.info("")
        if not self.metadata:
            raise Failed("No metadata to edit")
        for mapping_name, meta in self.metadata.items():
            methods = {mm.lower(): mm for mm in meta}
            if test and ("test" not in methods or meta[methods["test"]] is not True):
                continue

            updated = False
            edits = {}
            advance_edits = {}
            def add_edit(name, current, group, alias, key=None, value=None, var_type="str"):
                if value or name in alias:
                    if value or group[alias[name]]:
                        if key is None:         key = name
                        if value is None:       value = group[alias[name]]
                        try:
                            if var_type == "date":
                                final_value = util.check_date(value, name, return_string=True, plex_date=True)
                            elif var_type == "float":
                                final_value = util.check_number(value, name, number_type="float", minimum=0, maximum=10)
                            else:
                                final_value = value
                            if str(current) != str(final_value):
                                edits[f"{key}.value"] = final_value
                                edits[f"{key}.locked"] = 1
                                logger.info(f"Detail: {name} updated to {final_value}")
                        except Failed as ee:
                            logger.error(ee)
                    else:
                        logger.error(f"Metadata Error: {name} attribute is blank")

            def add_advanced_edit(attr, obj, group, alias, show_library=False, new_agent=False):
                key, options = advance_keys[attr]
                if attr in alias:
                    if new_agent and self.agent not in new_plex_agents:
                        logger.error(f"Metadata Error: {attr} attribute only works for with the New Plex Movie Agent and New Plex TV Agent")
                    elif show_library and not self.is_show:
                        logger.error(f"Metadata Error: {attr} attribute only works for show libraries")
                    elif group[alias[attr]]:
                        method_data = str(group[alias[attr]]).lower()
                        if method_data not in options:
                            logger.error(f"Metadata Error: {group[alias[attr]]} {attr} attribute invalid")
                        elif getattr(obj, key) != options[method_data]:
                            advance_edits[key] = options[method_data]
                            logger.info(f"Detail: {attr} updated to {method_data}")
                    else:
                        logger.error(f"Metadata Error: {attr} attribute is blank")

            def edit_tags(attr, obj, group, alias, key=None, extra=None, movie_library=False):
                if key is None:
                    key = f"{attr}s"
                if attr in alias and f"{attr}.sync" in alias:
                    logger.error(f"Metadata Error: Cannot use {attr} and {attr}.sync together")
                elif attr in alias or f"{attr}.sync" in alias:
                    attr_key = attr if attr in alias else f"{attr}.sync"
                    if movie_library and not self.is_movie:
                        logger.error(f"Metadata Error: {attr_key} attribute only works for movie libraries")
                    elif group[alias[attr_key]] or extra:
                        item_tags = [item_tag.tag for item_tag in getattr(obj, key)]
                        input_tags = []
                        if group[alias[attr_key]]:
                            input_tags.extend(util.get_list(group[alias[attr_key]]))
                        if extra:
                            input_tags.extend(extra)
                        if f"{attr}.sync" in alias:
                            remove_method = getattr(obj, f"remove{attr.capitalize()}")
                            for tag in (t for t in item_tags if t not in input_tags):
                                updated = True
                                remove_method(tag)
                                logger.info(f"Detail: {attr.capitalize()} {tag} removed")
                        add_method = getattr(obj, f"add{attr.capitalize()}")
                        for tag in (t for t in input_tags if t not in item_tags):
                            updated = True
                            add_method(tag)
                            logger.info(f"Detail: {attr.capitalize()} {tag} added")
                    else:
                        logger.error(f"Metadata Error: {attr} attribute is blank")

            def set_image(attr, obj, group, alias, poster=True, url=True):
                if group[alias[attr]]:
                    message = f"{'poster' if poster else 'background'} to [{'URL' if url else 'File'}] {group[alias[attr]]}"
                    self.upload_image(obj, group[alias[attr]], poster=poster, url=url)
                    logger.info(f"Detail: {attr} updated {message}")
                else:
                    logger.error(f"Metadata Error: {attr} attribute is blank")

            def set_images(obj, group, alias):
                if "url_poster" in alias:
                    set_image("url_poster", obj, group, alias)
                elif "file_poster" in alias:
                    set_image("file_poster", obj, group, alias, url=False)
                if "url_background" in alias:
                    set_image("url_background", obj, group, alias, poster=False)
                elif "file_background" in alias:
                    set_image("file_background", obj, group, alias, poster=False, url=False)

            logger.info("")
            util.separator()
            logger.info("")
            year = None
            if "year" in methods:
                year = util.check_number(meta[methods["year"]], "year", minimum=1800, maximum=datetime.now().year + 1)

            title = mapping_name
            if "title" in methods:
                if meta[methods["title"]] is None:              logger.error("Metadata Error: title attribute is blank")
                else:                                           title = meta[methods["title"]]

            item = self.search_item(title, year=year)

            if item is None:
                item = self.search_item(f"{title} (SUB)", year=year)

            if item is None and "alt_title" in methods:
                if meta[methods["alt_title"]] is None:
                    logger.error("Metadata Error: alt_title attribute is blank")
                else:
                    alt_title = meta["alt_title"]
                    item = self.search_item(alt_title, year=year)

            if item is None:
                logger.error(f"Plex Error: Item {mapping_name} not found")
                logger.error(f"Skipping {mapping_name}")
                continue

            item_type = "Movie" if self.is_movie else "Show"
            logger.info(f"Updating {item_type}: {title}...")

            tmdb_item = None
            tmdb_is_movie = None
            if ("tmdb_show" in methods or "tmdb_id" in methods) and "tmdb_movie" in methods:
                logger.error("Metadata Error: Cannot use tmdb_movie and tmdb_show when editing the same metadata item")

            if "tmdb_show" in methods or "tmdb_id" in methods or "tmdb_movie" in methods:
                try:
                    if "tmdb_show" in methods or "tmdb_id" in methods:
                        data = meta[methods["tmdb_show" if "tmdb_show" in methods else "tmdb_id"]]
                        if data is None:
                            logger.error("Metadata Error: tmdb_show attribute is blank")
                        else:
                            tmdb_is_movie = False
                            tmdb_item = TMDb.get_show(util.regex_first_int(data, "Show"))
                    elif "tmdb_movie" in methods:
                        if meta[methods["tmdb_movie"]] is None:
                            logger.error("Metadata Error: tmdb_movie attribute is blank")
                        else:
                            tmdb_is_movie = True
                            tmdb_item = TMDb.get_movie(util.regex_first_int(meta[methods["tmdb_movie"]], "Movie"))
                except Failed as e:
                    logger.error(e)

            originally_available = None
            original_title = None
            rating = None
            studio = None
            tagline = None
            summary = None
            genres = []
            if tmdb_item:
                originally_available = tmdb_item.release_date if tmdb_is_movie else tmdb_item.first_air_date
                if tmdb_item and tmdb_is_movie is True and tmdb_item.original_title != tmdb_item.title:
                    original_title = tmdb_item.original_title
                elif tmdb_item and tmdb_is_movie is False and tmdb_item.original_name != tmdb_item.name:
                    original_title = tmdb_item.original_name
                rating = tmdb_item.vote_average
                if tmdb_is_movie is True and tmdb_item.production_companies:
                    studio = tmdb_item.production_companies[0].name
                elif tmdb_is_movie is False and tmdb_item.networks:
                    studio = tmdb_item.networks[0].name
                tagline = tmdb_item.tagline if len(tmdb_item.tagline) > 0 else None
                summary = tmdb_item.overview
                genres = [genre.name for genre in tmdb_item.genres]

            edits = {}
            add_edit("title", item.title, meta, methods, value=title)
            add_edit("sort_title", item.titleSort, meta, methods, key="titleSort")
            add_edit("originally_available", str(item.originallyAvailableAt)[:-9], meta, methods, key="originallyAvailableAt", value=originally_available, var_type="date")
            add_edit("critic_rating", item.rating, meta, methods, value=rating, key="rating", var_type="float")
            add_edit("audience_rating", item.audienceRating, meta, methods, key="audienceRating", var_type="float")
            add_edit("content_rating", item.contentRating, meta, methods, key="contentRating")
            add_edit("original_title", item.originalTitle, meta, methods, key="originalTitle", value=original_title)
            add_edit("studio", item.studio, meta, methods, value=studio)
            add_edit("tagline", item.tagline, meta, methods, value=tagline)
            add_edit("summary", item.summary, meta, methods, value=summary)
            self.edit_item(item, mapping_name, item_type, edits)

            advance_edits = {}
            add_advanced_edit("episode_sorting", item, meta, methods, show_library=True)
            add_advanced_edit("keep_episodes", item, meta, methods, show_library=True)
            add_advanced_edit("delete_episodes", item, meta, methods, show_library=True)
            add_advanced_edit("season_display", item, meta, methods, show_library=True)
            add_advanced_edit("episode_ordering", item, meta, methods, show_library=True)
            add_advanced_edit("metadata_language", item, meta, methods, new_agent=True)
            add_advanced_edit("use_original_title", item, meta, methods, new_agent=True)
            self.edit_item(item, mapping_name, item_type, advance_edits, advanced=True)

            edit_tags("genre", item, meta, methods, extra=genres)
            edit_tags("label", item, meta, methods)
            edit_tags("collection", item, meta, methods)
            edit_tags("country", item, meta, methods, key="countries", movie_library=True)
            edit_tags("director", item, meta, methods, movie_library=True)
            edit_tags("producer", item, meta, methods, movie_library=True)
            edit_tags("writer", item, meta, methods, movie_library=True)

            logger.info(f"{item_type}: {mapping_name} Details Update {'Complete' if updated else 'Not Needed'}")

            set_images(item, meta, methods)

            if "seasons" in methods and self.is_show:
                if meta[methods["seasons"]]:
                    for season_id in meta[methods["seasons"]]:
                        updated = False
                        logger.info("")
                        logger.info(f"Updating season {season_id} of {mapping_name}...")
                        if isinstance(season_id, int):
                            season = None
                            for s in item.seasons():
                                if s.index == season_id:
                                    season = s
                                    break
                            if season is None:
                                logger.error(f"Metadata Error: Season: {season_id} not found")
                            else:
                                season_dict = meta[methods["seasons"]][season_id]
                                season_methods = {sm.lower(): sm for sm in season_dict}

                                if "title" in season_methods and season_dict[season_methods["title"]]:
                                    title = season_dict[season_methods["title"]]
                                else:
                                    title = season.title
                                if "sub" in season_methods:
                                    if season_dict[season_methods["sub"]] is None:
                                        logger.error("Metadata Error: sub attribute is blank")
                                    elif season_dict[season_methods["sub"]] is True and "(SUB)" not in title:
                                        title = f"{title} (SUB)"
                                    elif season_dict[season_methods["sub"]] is False and title.endswith(" (SUB)"):
                                        title = title[:-6]
                                    else:
                                        logger.error("Metadata Error: sub attribute must be True or False")

                                edits = {}
                                add_edit("title", season.title, season_dict, season_methods, value=title)
                                add_edit("summary", season.summary, season_dict, season_methods)
                                self.edit_item(season, season_id, "Season", edits)
                                set_images(season, season_dict, season_methods)
                        else:
                            logger.error(f"Metadata Error: Season: {season_id} invalid, it must be an integer")
                        logger.info(f"Season {season_id} of {mapping_name} Details Update {'Complete' if updated else 'Not Needed'}")
                else:
                    logger.error("Metadata Error: seasons attribute is blank")
            elif "seasons" in methods:
                logger.error("Metadata Error: seasons attribute only works for show libraries")

            if "episodes" in methods and self.is_show:
                if meta[methods["episodes"]]:
                    for episode_str in meta[methods["episodes"]]:
                        updated = False
                        logger.info("")
                        match = re.search("[Ss]\\d+[Ee]\\d+", episode_str)
                        if match:
                            output = match.group(0)[1:].split("E" if "E" in match.group(0) else "e")
                            season_id = int(output[0])
                            episode_id = int(output[1])
                            logger.info(f"Updating episode S{season_id}E{episode_id} of {mapping_name}...")
                            try:                                episode = item.episode(season=season_id, episode=episode_id)
                            except NotFound:                    logger.error(f"Metadata Error: episode {episode_id} of season {season_id} not found")
                            else:
                                episode_dict = meta[methods["episodes"]][episode_str]
                                episode_methods = {em.lower(): em for em in episode_dict}

                                if "title" in episode_methods and episode_dict[episode_methods["title"]]:
                                    title = episode_dict[episode_methods["title"]]
                                else:
                                    title = episode.title
                                if "sub" in episode_dict:
                                    if episode_dict[episode_methods["sub"]] is None:
                                        logger.error("Metadata Error: sub attribute is blank")
                                    elif episode_dict[episode_methods["sub"]] is True and "(SUB)" not in title:
                                        title = f"{title} (SUB)"
                                    elif episode_dict[episode_methods["sub"]] is False and title.endswith(" (SUB)"):
                                        title = title[:-6]
                                    else:
                                        logger.error("Metadata Error: sub attribute must be True or False")
                                edits = {}
                                add_edit("title", episode.title, episode_dict, episode_methods, value=title)
                                add_edit("sort_title", episode.titleSort, episode_dict, episode_methods, key="titleSort")
                                add_edit("rating", episode.rating, episode_dict, episode_methods)
                                add_edit("originally_available", str(episode.originallyAvailableAt)[:-9], episode_dict, episode_methods, key="originallyAvailableAt")
                                add_edit("summary", episode.summary, episode_dict, episode_methods)
                                self.edit_item(episode, f"{season_id} Episode: {episode_id}", "Season", edits)
                                edit_tags("director", episode, episode_dict, episode_methods)
                                edit_tags("writer", episode, episode_dict, episode_methods)
                                set_images(episode, episode_dict, episode_methods)
                            logger.info(f"Episode S{episode_id}E{season_id}  of {mapping_name} Details Update {'Complete' if updated else 'Not Needed'}")
                        else:
                            logger.error(f"Metadata Error: episode {episode_str} invalid must have S##E## format")
                else:
                    logger.error("Metadata Error: episodes attribute is blank")
            elif "episodes" in methods:
                logger.error("Metadata Error: episodes attribute only works for show libraries")

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