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

class PlexAPI:
    def __init__(self, params, TMDb, TVDb):
        try:                                                                    self.PlexServer = PlexServer(params["plex"]["url"], params["plex"]["token"], timeout=params["plex"]["timeout"])
        except Unauthorized:                                                    raise Failed("Plex Error: Plex token is invalid")
        except ValueError as e:                                                 raise Failed(f"Plex Error: {e}")
        except requests.exceptions.ConnectionError:
            util.print_stacktrace()
            raise Failed("Plex Error: Plex url is invalid")
        self.is_movie = params["library_type"] == "movie"
        self.is_show = params["library_type"] == "show"
        self.Plex = next((s for s in self.PlexServer.library.sections() if s.title == params["name"] and ((self.is_movie and isinstance(s, MovieSection)) or (self.is_show and isinstance(s, ShowSection)))), None)
        if not self.Plex:                                                       raise Failed(f"Plex Error: Plex Library {params['name']} not found")
        try:                                                                    self.data, ind, bsi = yaml.util.load_yaml_guess_indent(open(params["metadata_path"], encoding="utf-8"))
        except yaml.scanner.ScannerError as e:                                  raise Failed(f"YAML Error: {util.tab_new_lines(e)}")

        def get_dict(attribute):
            if attribute in self.data:
                if self.data[attribute]:
                    if isinstance(self.data[attribute], dict):                              return self.data[attribute]
                    else:                                                                   logger.warning(f"Config Warning: {attribute} must be a dictionary")
                else:                                                                   logger.warning(f"Config Warning: {attribute} attribute is blank")
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

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def search(self, title, libtype=None, year=None):
        if libtype is not None and year is not None:        return self.Plex.search(title=title, year=year, libtype=libtype)
        elif libtype is not None:                           return self.Plex.search(title=title, libtype=libtype)
        elif year is not None:                              return self.Plex.search(title=title, year=year)
        else:                                               return self.Plex.search(title=title)

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def fetchItem(self, data):
        return self.PlexServer.fetchItem(data)

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def server_search(self, data):
        return self.PlexServer.search(data)

    def get_all_collections(self):
        return self.Plex.search(libtype="collection")

    def get_collection(self, data):
        collection = util.choose_from_list(self.search(str(data), libtype="collection"), "collection", str(data), exact=True)
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
                    if method in util.method_alias:
                        method_name = util.method_alias[method]
                        logger.warning(f"Collection Warning: {method} attribute will run as {method_name}")
                    else:
                        method_name = method
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
                        if (modifier == ".lte" and attr > filter_data) or (modifier == ".gte" and attr < filter_data):
                            match = False
                            break
                    else:
                        attrs = []
                        if method_name in ["video_resolution", "audio_language", "subtitle_language"]:
                            for media in current.media:
                                if method_name == "video_resolution":                                                           attrs.extend([media.videoResolution])
                                for part in media.parts:
                                    if method_name == "audio_language":                                                             attrs.extend([a.language for a in part.audioStreams()])
                                    if method_name == "subtitle_language":                                                          attrs.extend([s.language for s in part.subtitleStreams()])
                        elif method_name in ["contentRating", "studio", "year", "rating", "originallyAvailableAt"]:     attrs = [str(getattr(current, method_name))]
                        elif method_name in ["actors", "countries", "directors", "genres", "writers", "collections"]:   attrs = [getattr(x, "tag") for x in getattr(current, method_name)]

                        if (not list(set(filter_data) & set(attrs)) and modifier != ".not") or (list(set(filter_data) & set(attrs)) and modifier == ".not"):
                            match = False
                            break
                length = util.print_return(length, f"Filtering {(' ' * (max_length - len(str(i)))) + str(i)}/{total} {current.title}")
            if match:
                util.print_end(length, f"{name} Collection | {'=' if current in collection_items else '+'} | {current.title}")
                if current in collection_items:             rating_key_map[current.ratingKey] = None
                else:                                       current.addCollection(name)
            elif show_filtered is True:
                logger.info(f"{name} Collection | X | {current.title}")
        media_type = f"{'Movie' if self.is_movie else 'Show'}{'s' if total > 1 else ''}"
        util.print_end(length, f"{total} {media_type} Processed")
        return rating_key_map

    def search_item(self, data, year=None):
        return util.choose_from_list(self.search(data, year=year), "movie" if self.is_movie else "show", str(data), exact=True)

    def update_metadata(self, TMDb, test):
        logger.info("")
        util.separator(f"{self.name} Library Metadata")
        logger.info("")
        if not self.metadata:
            raise Failed("No metadata to edit")
        for m in self.metadata:
            if test and ("test" not in self.metadata[m] or self.metadata[m]["test"] is not True):
                continue
            logger.info("")
            util.separator()
            logger.info("")
            year = None
            if "year" in self.metadata[m]:
                year = util.check_number(self.metadata[m]["year"], "year", minimum=1800, maximum=datetime.now().year + 1)

            title = m
            if "title" in self.metadata[m]:
                if self.metadata[m]["title"] is None:                                   logger.error("Metadata Error: title attribute is blank")
                else:                                                                   title = self.metadata[m]["title"]

            item = self.search_item(title, year=year)

            if item is None:
                item = self.search_item(f"{title} (SUB)", year=year)

            if item is None and "alt_title" in self.metadata[m]:
                if self.metadata[m]["alt_title"] is None:
                    logger.error("Metadata Error: alt_title attribute is blank")
                else:
                    alt_title = self.metadata[m]["alt_title"]
                    item = self.search_item(alt_title, year=year)

            if item is None:
                logger.error(f"Plex Error: Item {m} not found")
                logger.error(f"Skipping {m}")
                continue

            item_type = "Movie" if self.is_movie else "Show"
            logger.info(f"Updating {item_type}: {title}...")

            tmdb_item = None
            try:
                if "tmdb_id" in self.metadata[m]:
                    if self.metadata[m]["tmdb_id"] is None:                                 logger.error("Metadata Error: tmdb_id attribute is blank")
                    elif self.is_show:                                                      logger.error("Metadata Error: tmdb_id attribute only works with movie libraries")
                    else:                                                                   tmdb_item = TMDb.get_show(util.regex_first_int(self.metadata[m]["tmdb_id"], "Show"))
            except Failed as e:
                logger.error(e)

            originally_available = tmdb_item.first_air_date if tmdb_item else None
            rating = tmdb_item.vote_average if tmdb_item else None
            original_title = tmdb_item.original_name if tmdb_item and tmdb_item.original_name != tmdb_item.name else None
            studio = tmdb_item.networks[0].name if tmdb_item else None
            tagline = tmdb_item.tagline if tmdb_item and len(tmdb_item.tagline) > 0 else None
            summary = tmdb_item.overview if tmdb_item else None

            edits = {}
            def add_edit(name, current, group, key=None, value=None):
                if value or name in group:
                    if value or group[name]:
                        if key is None:         key = name
                        if value is None:       value = group[name]
                        if str(current) != str(value):
                            edits[f"{key}.value"] = value
                            edits[f"{key}.locked"] = 1
                            logger.info(f"Detail: {name} updated to {value}")
                    else:
                        logger.error(f"Metadata Error: {name} attribute is blank")
            add_edit("title", item.title, self.metadata[m], value=title)
            add_edit("sort_title", item.titleSort, self.metadata[m], key="titleSort")
            add_edit("originally_available", str(item.originallyAvailableAt)[:-9], self.metadata[m], key="originallyAvailableAt", value=originally_available)
            add_edit("rating", item.rating, self.metadata[m], value=rating)
            add_edit("content_rating", item.contentRating, self.metadata[m], key="contentRating")
            add_edit("original_title", item.originalTitle, self.metadata[m], key="originalTitle", value=original_title)
            add_edit("studio", item.studio, self.metadata[m], value=studio)
            add_edit("tagline", item.tagline, self.metadata[m], value=tagline)
            add_edit("summary", item.summary, self.metadata[m], value=summary)
            if len(edits) > 0:
                logger.debug(f"Details Update: {edits}")
                try:
                    item.edit(**edits)
                    item.reload()
                    logger.info(f"{item_type}: {m} Details Update Successful")
                except BadRequest:
                    util.print_stacktrace()
                    logger.error(f"{item_type}: {m} Details Update Failed")
            else:
                logger.info(f"{item_type}: {m} Details Update Not Needed")

            genres = []

            if tmdb_item:
                genres.extend([genre.name for genre in tmdb_item.genres])

            if "genre" in self.metadata[m]:
                if self.metadata[m]["genre"]:                                           genres.extend(util.get_list(self.metadata[m]["genre"]))
                else:                                                                   logger.error("Metadata Error: genre attribute is blank")

            if len(genres) > 0:
                item_genres = [genre.tag for genre in item.genres]
                if "genre_sync_mode" in self.metadata[m]:
                    if self.metadata[m]["genre_sync_mode"] is None:                         logger.error("Metadata Error: genre_sync_mode attribute is blank defaulting to append")
                    elif self.metadata[m]["genre_sync_mode"] not in ["append", "sync"]:     logger.error("Metadata Error: genre_sync_mode attribute must be either 'append' or 'sync' defaulting to append")
                    elif self.metadata[m]["genre_sync_mode"] == "sync":
                        for genre in (g for g in item_genres if g not in genres):
                            item.removeGenre(genre)
                            logger.info(f"Detail: Genre {genre} removed")
                for genre in (g for g in genres if g not in item_genres):
                    item.addGenre(genre)
                    logger.info(f"Detail: Genre {genre} added")

            if "label" in self.metadata[m]:
                if self.metadata[m]["label"]:
                    item_labels = [label.tag for label in item.labels]
                    labels = util.get_list(self.metadata[m]["label"])
                    if "label_sync_mode" in self.metadata[m]:
                        if self.metadata[m]["label_sync_mode"] is None:                         logger.error("Metadata Error: label_sync_mode attribute is blank defaulting to append")
                        elif self.metadata[m]["label_sync_mode"] not in ["append", "sync"]:     logger.error("Metadata Error: label_sync_mode attribute must be either 'append' or 'sync' defaulting to append")
                        elif self.metadata[m]["label_sync_mode"] == "sync":
                            for label in (la for la in item_labels if la not in labels):
                                item.removeLabel(label)
                                logger.info(f"Detail: Label {label} removed")
                    for label in (la for la in labels if la not in item_labels):
                        item.addLabel(label)
                        logger.info(f"Detail: Label {label} added")
                else:
                    logger.error("Metadata Error: label attribute is blank")

            if "seasons" in self.metadata[m] and self.is_show:
                if self.metadata[m]["seasons"]:
                    for season_id in self.metadata[m]["seasons"]:
                        logger.info("")
                        logger.info(f"Updating season {season_id} of {m}...")
                        if isinstance(season_id, int):
                            try:                                season = item.season(season_id)
                            except NotFound:                    logger.error(f"Metadata Error: Season: {season_id} not found")
                            else:

                                if "title" in self.metadata[m]["seasons"][season_id] and self.metadata[m]["seasons"][season_id]["title"]:
                                    title = self.metadata[m]["seasons"][season_id]["title"]
                                else:
                                    title = season.title
                                if "sub" in self.metadata[m]["seasons"][season_id]:
                                    if self.metadata[m]["seasons"][season_id]["sub"] is None:
                                        logger.error("Metadata Error: sub attribute is blank")
                                    elif self.metadata[m]["seasons"][season_id]["sub"] is True and "(SUB)" not in title:
                                        title = f"{title} (SUB)"
                                    elif self.metadata[m]["seasons"][season_id]["sub"] is False and title.endswith(" (SUB)"):
                                        title = title[:-6]
                                    else:
                                        logger.error("Metadata Error: sub attribute must be True or False")

                                edits = {}
                                add_edit("title", season.title, self.metadata[m]["seasons"][season_id], value=title)
                                add_edit("summary", season.summary, self.metadata[m]["seasons"][season_id])
                                if len(edits) > 0:
                                    logger.debug(f"Season: {season_id} Details Update: {edits}")
                                    try:
                                        season.edit(**edits)
                                        season.reload()
                                        logger.info(f"Season: {season_id} Details Update Successful")
                                    except BadRequest:
                                        util.print_stacktrace()
                                        logger.error(f"Season: {season_id} Details Update Failed")
                                else:
                                    logger.info(f"Season: {season_id} Details Update Not Needed")
                        else:
                            logger.error(f"Metadata Error: Season: {season_id} invalid, it must be an integer")
                else:
                    logger.error("Metadata Error: seasons attribute is blank")

            if "episodes" in self.metadata[m] and self.is_show:
                if self.metadata[m]["episodes"]:
                    for episode_str in self.metadata[m]["episodes"]:
                        logger.info("")
                        match = re.search("[Ss]\\d+[Ee]\\d+", episode_str)
                        if match:
                            output = match.group(0)[1:].split("E" if "E" in match.group(0) else "e")
                            episode_id = int(output[0])
                            season_id = int(output[1])
                            logger.info(f"Updating episode S{episode_id}E{season_id} of {m}...")
                            try:                                episode = item.episode(season=season_id, episode=episode_id)
                            except NotFound:                    logger.error(f"Metadata Error: episode {episode_id} of season {season_id} not found")
                            else:
                                if "title" in self.metadata[m]["episodes"][episode_str] and self.metadata[m]["episodes"][episode_str]["title"]:
                                    title = self.metadata[m]["episodes"][episode_str]["title"]
                                else:
                                    title = episode.title
                                if "sub" in self.metadata[m]["episodes"][episode_str]:
                                    if self.metadata[m]["episodes"][episode_str]["sub"] is None:
                                        logger.error("Metadata Error: sub attribute is blank")
                                    elif self.metadata[m]["episodes"][episode_str]["sub"] is True and "(SUB)" not in title:
                                        title = f"{title} (SUB)"
                                    elif self.metadata[m]["episodes"][episode_str]["sub"] is False and title.endswith(" (SUB)"):
                                        title = title[:-6]
                                    else:
                                        logger.error("Metadata Error: sub attribute must be True or False")
                                edits = {}
                                add_edit("title", episode.title, self.metadata[m]["episodes"][episode_str], value=title)
                                add_edit("sort_title", episode.titleSort, self.metadata[m]["episodes"][episode_str], key="titleSort")
                                add_edit("rating", episode.rating, self.metadata[m]["episodes"][episode_str])
                                add_edit("originally_available", str(episode.originallyAvailableAt)[:-9], self.metadata[m]["episodes"][episode_str], key="originallyAvailableAt")
                                add_edit("summary", episode.summary, self.metadata[m]["episodes"][episode_str])
                                if len(edits) > 0:
                                    logger.debug(f"Season: {season_id} Episode: {episode_id} Details Update: {edits}")
                                    try:
                                        episode.edit(**edits)
                                        episode.reload()
                                        logger.info(
                                            f"Season: {season_id} Episode: {episode_id} Details Update Successful")
                                    except BadRequest:
                                        util.print_stacktrace()
                                        logger.error(f"Season: {season_id} Episode: {episode_id} Details Update Failed")
                                else:
                                    logger.info(f"Season: {season_id} Episode: {episode_id} Details Update Not Needed")
                        else:
                            logger.error(f"Metadata Error: episode {episode_str} invalid must have S##E## format")
                else:
                    logger.error("Metadata Error: episodes attribute is blank")
