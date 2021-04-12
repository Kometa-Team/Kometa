import logging, os, re, requests
from datetime import datetime, timedelta
from modules import util
from modules.util import Failed
from plexapi.exceptions import BadRequest, NotFound, Unauthorized
from plexapi.library import MovieSection, ShowSection
from plexapi.collection import Collections
from plexapi.server import PlexServer
from plexapi.video import Movie, Show
from retrying import retry
from ruamel import yaml

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
    "user_rating": "userRating"
}
episode_sorting_options = {"default": "-1", "oldest": "0", "newest": "1"}
keep_episodes_options = {"all": 0, "5_latest": 5, "3_latest": 3, "latest": 1, "past_3": -3, "past_7": -7, "past_30": -30}
delete_episodes_options = {"never": 0, "day": 1, "week": 7, "refresh": 100}
season_display_options = {"default": -1, "show": 0, "hide": 1}
episode_ordering_options = {"default": None, "tmdb_aired": "tmdbAiring", "tvdb_aired": "airing", "tvdb_dvd": "dvd", "tvdb_absolute": "absolute"}
plex_languages = ["default", "ar-SA", "ca-ES", "cs-CZ", "da-DK", "de-DE", "el-GR", "en-AU", "en-CA", "en-GB", "en-US",
                  "es-ES", "es-MX", "et-EE", "fa-IR", "fi-FI", "fr-CA", "fr-FR", "he-IL", "hi-IN", "hu-HU", "id-ID",
                  "it-IT", "ja-JP", "ko-KR", "lt-LT", "lv-LV", "nb-NO", "nl-NL", "pl-PL", "pt-BR", "pt-PT", "ro-RO",
                  "ru-RU", "sk-SK", "sv-SE", "th-TH", "tr-TR", "uk-UA", "vi-VN", "zh-CN", "zh-HK", "zh-TW"]
metadata_language_options = {lang.lower(): lang for lang in plex_languages}
metadata_language_options["default"] = None
use_original_title_options = {"default": -1, "no": 0, "yes": 1}
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
    "added.before", "added.after",
    "originally_available.before", "originally_available.after",
    "duration.greater", "duration.less",
    "user_rating.greater", "user_rating.less",
    "audience_rating.greater", "audience_rating.less",
    "critic_rating.greater", "critic_rating.less",
    "year", "year.not", "year.greater", "year.less"
]
movie_only_searches = [
    "audio_language", "audio_language.and", "audio_language.not",
    "country", "country.and", "country.not",
    "subtitle_language", "subtitle_language.and", "subtitle_language.not",
    "decade", "resolution",
    "originally_available.before", "originally_available.after",
    "duration.greater", "duration.less"
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
    ".greater": ">>",
    ".less": "<<"
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
        self.is_movie = params["library_type"] == "movie"
        self.is_show = params["library_type"] == "show"
        self.Plex = next((s for s in self.PlexServer.library.sections() if s.title == params["name"] and ((self.is_movie and isinstance(s, MovieSection)) or (self.is_show and isinstance(s, ShowSection)))), None)
        if not self.Plex:
            raise Failed(f"Plex Error: Plex Library {params['name']} not found")

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
            raise Failed("YAML Error: metadata attributes or collections attribute required")

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
        self.sync_mode = params["sync_mode"]
        self.show_unmanaged = params["show_unmanaged"]
        self.show_filtered = params["show_filtered"]
        self.show_missing = params["show_missing"]
        self.save_missing = params["save_missing"]
        self.mass_genre_update = params["mass_genre_update"]
        self.plex = params["plex"]
        self.timeout = params["plex"]["timeout"]
        self.missing = {}
        self.run_again = []

    def get_all_collections(self):
        return self.search(libtype="collection")

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def search(self, title=None, libtype=None, sort=None, maxresults=None, **kwargs):
        return self.Plex.search(title=title, sort=sort, maxresults=maxresults, libtype=libtype, **kwargs)

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
    def add_collection(self, item, name):
        item.addCollection(name)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def get_search_choices(self, search_name, key=False):
        try:
            if key:             return {c.key.lower(): c.key for c in self.Plex.listFilterChoices(search_name)}
            else:               return {c.title.lower(): c.title for c in self.Plex.listFilterChoices(search_name)}
        except NotFound:
            raise Failed(f"Collection Error: plex search attribute: {search_name} only supported with Plex's New TV Agent")

    def validate_search_list(self, data, search_name):
        final_search = search_translation[search_name] if search_name in search_translation else search_name
        search_choices = self.get_search_choices(final_search, key=final_search.endswith("Language"))
        valid_list = []
        for value in util.get_list(data):
            if str(value).lower() in search_choices:
                valid_list.append(search_choices[str(value).lower()])
            else:
                logger.error(f"Plex Error: {search_name}: {value} not found")
        return valid_list

    def get_collection(self, data):
        collection = util.choose_from_list(self.search(title=str(data), libtype="collection"), "collection", str(data), exact=True)
        if collection:                              return collection
        else:                                       raise Failed(f"Plex Error: Collection {data} not found")

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
                    elif search in ["critic_rating", "audience_rating"] and modifier == ".greater":
                        final_mod = "__gte"
                    elif search in ["critic_rating", "audience_rating"] and modifier == ".less":
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
                        if search in ["added", "originally_available"] or modifier in [".greater", ".less", ".before", ".after"]:
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
            for col in self.get_all_collections():
                keep_collection = True
                for pre in data["exclude_prefix"]:
                    if col.title.startswith(pre) or (col.titleSort and col.titleSort.startswith(pre)):
                        keep_collection = False
                        break
                if keep_collection:
                    for ext in data["exclude"]:
                        if col.title == ext or (col.titleSort and col.titleSort == ext):
                            keep_collection = False
                            break
                if keep_collection:
                    good_collections.append(col.index)
            all_items = self.get_all()
            length = 0
            for i, item in enumerate(all_items, 1):
                length = util.print_return(length, f"Processing: {i}/{len(all_items)} {item.title}")
                add_item = True
                item.reload()
                for collection in item.collections:
                    if collection.id in good_collections:
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

    def add_to_collection(self, collection, items, filters, show_filtered, rating_key_map, movie_map, show_map):
        name = collection.title if isinstance(collection, Collections) else collection
        collection_items = collection.items() if isinstance(collection, Collections) else []
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
                            if current.ratingKey == value:
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
                    elif modifier in [".gte", ".lte"]:
                        if method_name == "vote_count":
                            tmdb_item = None
                            for key, value in movie_map.items():
                                if current.ratingKey == value:
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
                else:                                       self.add_collection(current, name)
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
            try:
                if "tmdb_id" in methods:
                    if meta[methods["tmdb_id"]] is None:        logger.error("Metadata Error: tmdb_id attribute is blank")
                    elif self.is_show:                          logger.error("Metadata Error: tmdb_id attribute only works with movie libraries")
                    else:                                       tmdb_item = TMDb.get_show(util.regex_first_int(meta[methods["tmdb_id"]], "Show"))
            except Failed as e:
                logger.error(e)

            originally_available = tmdb_item.first_air_date if tmdb_item else None
            rating = tmdb_item.vote_average if tmdb_item else None
            original_title = tmdb_item.original_name if tmdb_item and tmdb_item.original_name != tmdb_item.name else None
            studio = tmdb_item.networks[0].name if tmdb_item else None
            tagline = tmdb_item.tagline if tmdb_item and len(tmdb_item.tagline) > 0 else None
            summary = tmdb_item.overview if tmdb_item else None

            updated = False

            edits = {}
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
            if len(edits) > 0:
                logger.debug(f"Details Update: {edits}")
                updated = True
                try:
                    item.edit(**edits)
                    item.reload()
                    logger.info(f"{item_type}: {mapping_name} Details Update Successful")
                except BadRequest:
                    util.print_stacktrace()
                    logger.error(f"{item_type}: {mapping_name} Details Update Failed")

            advance_edits = {}
            def add_advanced_edit(attr, options, key=None, show_library=False):
                if key is None:
                    key = attr
                if attr in methods:
                    if show_library and not self.is_show:
                        logger.error(f"Metadata Error: {attr} attribute only works for show libraries")
                    elif meta[methods[attr]]:
                        method_data = str(meta[methods[attr]]).lower()
                        if method_data in options and getattr(item, key) != options[method_data]:
                            advance_edits[key] = options[method_data]
                            logger.info(f"Detail: {attr} updated to {method_data}")
                        else:
                            logger.error(f"Metadata Error: {meta[methods[attr]]} {attr} attribute invalid")
                    else:
                        logger.error(f"Metadata Error: {attr} attribute is blank")

            add_advanced_edit("episode_sorting", episode_sorting_options, key="episodeSort", show_library=True)
            add_advanced_edit("keep_episodes", keep_episodes_options, key="autoDeletionItemPolicyUnwatchedLibrary", show_library=True)
            add_advanced_edit("delete_episodes", delete_episodes_options, key="autoDeletionItemPolicyWatchedLibrary", show_library=True)
            add_advanced_edit("season_display", season_display_options, key="flattenSeasons", show_library=True)
            add_advanced_edit("episode_ordering", episode_ordering_options, key="showOrdering", show_library=True)
            add_advanced_edit("metadata_language", metadata_language_options, key="languageOverride")
            add_advanced_edit("use_original_title", use_original_title_options, key="useOriginalTitle")

            if len(advance_edits) > 0:
                logger.debug(f"Details Update: {advance_edits}")
                updated = True
                try:
                    check_dict = {pref.id: list(pref.enumValues.keys()) for pref in item.preferences()}
                    logger.info(check_dict)
                    item.editAdvanced(**advance_edits)
                    item.reload()
                    logger.info(f"{item_type}: {mapping_name} Advanced Details Update Successful")
                except BadRequest:
                    util.print_stacktrace()
                    logger.error(f"{item_type}: {mapping_name} Advanced Details Update Failed")

            def edit_tags(attr, obj, key=None, extra=None, movie_library=False):
                if key is None:
                    key = f"{attr}s"
                if attr in methods and f"{attr}.sync" in methods:
                    logger.error(f"Metadata Error: Cannot use {attr} and {attr}.sync together")
                elif attr in methods or f"{attr}.sync" in methods:
                    attr_key = attr if attr in methods else f"{attr}.sync"
                    if movie_library and not self.is_movie:
                        logger.error(f"Metadata Error: {attr_key} attribute only works for movie libraries")
                    elif meta[methods[attr_key]] or extra:
                        item_tags = [item_tag.tag for item_tag in getattr(obj, key)]
                        input_tags = []
                        if meta[methods[attr_key]]:
                            input_tags.extend(util.get_list(meta[methods[attr_key]]))
                        if extra:
                            input_tags.extend(extra)
                        if f"{attr}.sync" in methods:
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

            genres = [genre.name for genre in tmdb_item.genres] if tmdb_item else []
            edit_tags("genre", item, extra=genres)
            edit_tags("label", item)
            edit_tags("collection", item)
            edit_tags("country", item, key="countries", movie_library=True)
            edit_tags("director", item, movie_library=True)
            edit_tags("producer", item, movie_library=True)
            edit_tags("writer", item, movie_library=True)

            if "seasons" in methods and self.is_show:
                if meta[methods["seasons"]]:
                    for season_id in meta[methods["seasons"]]:
                        logger.info("")
                        logger.info(f"Updating season {season_id} of {mapping_name}...")
                        if isinstance(season_id, int):
                            try:                                season = item.season(season_id)
                            except NotFound:                    logger.error(f"Metadata Error: Season: {season_id} not found")
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
                                add_edit("summary", season.summary, season_methods, season_dict)
                                if len(edits) > 0:
                                    logger.debug(f"Season: {season_id} Details Update: {edits}")
                                    updated = True
                                    try:
                                        season.edit(**edits)
                                        season.reload()
                                        logger.info(f"Season: {season_id} Details Update Successful")
                                    except BadRequest:
                                        util.print_stacktrace()
                                        logger.error(f"Season: {season_id} Details Update Failed")
                        else:
                            logger.error(f"Metadata Error: Season: {season_id} invalid, it must be an integer")
                else:
                    logger.error("Metadata Error: seasons attribute is blank")
            elif "seasons" in methods:
                logger.error("Metadata Error: seasons attribute only works for show libraries")

            if "episodes" in methods and self.is_show:
                if meta[methods["episodes"]]:
                    for episode_str in meta[methods["episodes"]]:
                        logger.info("")
                        match = re.search("[Ss]\\d+[Ee]\\d+", episode_str)
                        if match:
                            output = match.group(0)[1:].split("E" if "E" in match.group(0) else "e")
                            season_id = int(output[0])
                            episode_id = int(output[1])
                            logger.info(f"Updating episode S{episode_id}E{season_id} of {mapping_name}...")
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
                                if len(edits) > 0:
                                    logger.debug(f"Season: {season_id} Episode: {episode_id} Details Update: {edits}")
                                    updated = True
                                    try:
                                        episode.edit(**edits)
                                        episode.reload()
                                        logger.info(
                                            f"Season: {season_id} Episode: {episode_id} Details Update Successful")
                                    except BadRequest:
                                        util.print_stacktrace()
                                        logger.error(f"Season: {season_id} Episode: {episode_id} Details Update Failed")
                                edit_tags("director", episode)
                                edit_tags("writer", episode)

                        else:
                            logger.error(f"Metadata Error: episode {episode_str} invalid must have S##E## format")
                else:
                    logger.error("Metadata Error: episodes attribute is blank")
            elif "episodes" in methods:
                logger.error("Metadata Error: episodes attribute only works for show libraries")

            if not updated:
                logger.info(f"{item_type}: {mapping_name} Details Update Not Needed")