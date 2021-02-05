import datetime, logging, os, requests
from lxml import html
from modules import util
from modules.radarr import RadarrAPI
from modules.sonarr import SonarrAPI
from modules.tautulli import TautulliAPI
from modules.util import Failed
from plexapi.exceptions import BadRequest, NotFound, Unauthorized
from plexapi.library import Collections, MovieSection, ShowSection
from plexapi.server import PlexServer
from plexapi.video import Movie, Show
from retrying import retry
from ruamel import yaml

logger = logging.getLogger("Plex Meta Manager")

class PlexAPI:
    def __init__(self, params):
        try:                                                                    self.PlexServer = PlexServer(params["plex"]["url"], params["plex"]["token"], timeout=600)
        except Unauthorized:                                                    raise Failed("Plex Error: Plex token is invalid")
        except ValueError as e:                                                 raise Failed("Plex Error: {}".format(e))
        except requests.exceptions.ConnectionError as e:
            util.print_stacktrace()
            raise Failed("Plex Error: Plex url is invalid")
        self.is_movie = params["library_type"] == "movie"
        self.is_show = params["library_type"] == "show"
        self.Plex = next((s for s in self.PlexServer.library.sections() if s.title == params["name"] and ((self.is_movie and isinstance(s, MovieSection)) or (self.is_show and isinstance(s, ShowSection)))), None)
        if not self.Plex:                                                       raise Failed("Plex Error: Plex Library {} not found".format(params["name"]))
        try:                                                                    self.data, ind, bsi = yaml.util.load_yaml_guess_indent(open(params["metadata_path"], encoding="utf-8"))
        except yaml.scanner.ScannerError as e:                                  raise Failed("YAML Error: {}".format(str(e).replace("\n", "\n|\t      ")))

        self.metadata = None
        if "metadata" in self.data:
            if self.data["metadata"]:                                               self.metadata = self.data["metadata"]
            else:                                                                   logger.warning("Config Warning: metadata attribute is blank")
        else:                                                                   logger.warning("Config Warning: metadata attribute not found")

        self.collections = None
        if "collections" in self.data:
            if self.data["collections"]:                                            self.collections = self.data["collections"]
            else:                                                                   logger.warning("Config Warning: collections attribute is blank")
        else:                                                                   logger.warning("Config Warning: collections attribute not found")

        if self.metadata is None and self.collections is None:
            raise Failed("YAML Error: metadata attributes or collections attribute required")

        if params["asset_directory"]:
            logger.info("Using Asset Directory: {}".format(params["asset_directory"]))

        self.Radarr = None
        if params["tmdb"] and params["radarr"]:
            logger.info("Connecting to {} library's Radarr...".format(params["name"]))
            try:                                                                    self.Radarr = RadarrAPI(params["tmdb"], params["radarr"])
            except Failed as e:                                                     logger.error(e)
            logger.info("{} library's Radarr Connection {}".format(params["name"], "Failed" if self.Radarr is None else "Successful"))

        self.Sonarr = None
        if params["tvdb"] and params["sonarr"]:
            logger.info("Connecting to {} library's Sonarr...".format(params["name"]))
            try:                                                                    self.Sonarr = SonarrAPI(params["tvdb"], params["sonarr"], self.Plex.language)
            except Failed as e:                                                     logger.error(e)
            logger.info("{} library's Sonarr Connection {}".format(params["name"], "Failed" if self.Sonarr is None else "Successful"))

        self.Tautulli = None
        if params["tautulli"]:
            logger.info("Connecting to {} library's Tautulli...".format(params["name"]))
            try:                                                                    self.Tautulli = TautulliAPI(params["tautulli"])
            except Failed as e:                                                     logger.error(e)
            logger.info("{} library's Tautulli Connection {}".format(params["name"], "Failed" if self.Tautulli is None else "Successful"))

        self.name = params["name"]

        self.missing_path = os.path.join(os.path.dirname(os.path.abspath(params["metadata_path"])), "{}_missing.yml".format(os.path.splitext(os.path.basename(params["metadata_path"]))[0]))
        self.metadata_path = params["metadata_path"]
        self.asset_directory = params["asset_directory"]
        self.sync_mode = params["sync_mode"]
        self.plex = params["plex"]
        self.radarr = params["radarr"]
        self.sonarr = params["sonarr"]
        self.tautulli = params["tautulli"]

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
        else:                                       raise Failed("Plex Error: Collection {} not found".format(data))

    def validate_collections(self, collections):
        valid_collections = []
        for collection in collections:
            try:                                        valid_collections.append(self.get_collection(collection))
            except Failed as e:                         logger.error(e)
        if len(valid_collections) == 0:
            raise Failed("Collection Error: No valid Plex Collections in {}".format(collections[c][m]))
        return valid_collections

    def del_collection_if_empty(self, collection):
        missing_data = {}
        if not os.path.exists(self.missing_path):
            with open(self.missing_path, "w"): pass
        try:
            missing_data, ind, bsi = yaml.util.load_yaml_guess_indent(open(self.missing_path))
            if not missing_data:
                missing_data = {}
            if collection in missing_data and len(missing_data[collection]) == 0:
                del missing_data[collection]
            yaml.round_trip_dump(missing_data, open(self.missing_path, "w"), indent=ind, block_seq_indent=bsi)
        except yaml.scanner.ScannerError as e:
            logger.error("YAML Error: {}".format(str(e).replace("\n", "\n|\t      ")))

    def clear_collection_missing(self, collection):
        missing_data = {}
        if not os.path.exists(self.missing_path):
            with open(self.missing_path, "w"): pass
        try:
            missing_data, ind, bsi = yaml.util.load_yaml_guess_indent(open(self.missing_path))
            if not missing_data:
                missing_data = {}
            if collection in missing_data:
                missing_data[collection.encode("ascii", "replace").decode()] = {}
            yaml.round_trip_dump(missing_data, open(self.missing_path, "w"), indent=ind, block_seq_indent=bsi)
        except yaml.scanner.ScannerError as e:
            logger.error("YAML Error: {}".format(str(e).replace("\n", "\n|\t      ")))

    def save_missing(self, collection, items, is_movie):
        missing_data = {}
        if not os.path.exists(self.missing_path):
            with open(self.missing_path, "w"): pass
        try:
            missing_data, ind, bsi = yaml.util.load_yaml_guess_indent(open(self.missing_path))
            if not missing_data:
                missing_data = {}
            col_name = collection.encode("ascii", "replace").decode()
            if col_name not in missing_data:
                missing_data[col_name] = {}
            section = "Movies Missing (TMDb IDs)" if is_movie else "Shows Missing (TVDb IDs)"
            if section not in missing_data[col_name]:
                missing_data[col_name][section] = {}
            for title, item_id in items:
                missing_data[col_name][section][int(item_id)] = str(title).encode("ascii", "replace").decode()
            yaml.round_trip_dump(missing_data, open(self.missing_path, "w"), indent=ind, block_seq_indent=bsi)
        except yaml.scanner.ScannerError as e:
            logger.error("YAML Error: {}".format(str(e).replace("\n", "\n|\t      ")))

    def add_to_collection(self, collection, items, filters, map={}):
        name = collection.title if isinstance(collection, Collections) else collection
        collection_items = collection.items() if isinstance(collection, Collections) else []
        total = len(items)
        max_length = len(str(total))
        length = 0
        for i, item in enumerate(items, 1):
            try:                                        current = self.fetchItem(item.ratingKey if isinstance(item, (Movie, Show)) else int(item))
            except BadRequest:                          raise Failed("Plex Error: Item {} not found".format(item))
            match = True
            if filters:
                length = util.print_return(length, "Filtering {}/{} {}".format((" " * (max_length - len(str(i)))) + str(i), total, current.title))
                for f in filters:
                    modifier = f[0][-4:]
                    method = util.filter_alias[f[0][:-4]] if modifier in [".not", ".lte", ".gte"] else util.filter_alias[f[0]]
                    if method == "max_age":
                        threshold_date = datetime.now() - timedelta(days=f[1])
                        attr = getattr(current, "originallyAvailableAt")
                        if attr is None or attr < threshold_date:
                            match = False
                            break
                    elif modifier in [".gte", ".lte"]:
                        if method == "originallyAvailableAt":
                            threshold_date = datetime.strptime(f[1], "%m/%d/%y")
                            attr = getattr(current, "originallyAvailableAt")
                            if (modifier == ".lte" and attr > threshold_date) or (modifier == ".gte" and attr < threshold_date):
                                match = False
                                break
                        elif method in ["year", "rating"]:
                            attr = getattr(current, method)
                            if (modifier == ".lte" and attr > f[1]) or (modifier == ".gte" and attr < f[1]):
                                match = False
                                break
                    else:
                        terms = f[1] if isinstance(f[1], list) else str(f[1]).split(", ")
                        if method in ["video_resolution", "audio_language", "subtitle_language"]:
                            for media in current.media:
                                if method == "video_resolution":                                                                attrs = [media.videoResolution]
                                for part in media.parts:
                                    if method == "audio_language":                                                                  attrs = ([a.language for a in part.audioStreams()])
                                    if method == "subtitle_language":                                                               attrs = ([s.language for s in part.subtitleStreams()])
                        elif method in ["contentRating", "studio", "year", "rating", "originallyAvailableAt"]:          attrs = [str(getattr(current, method))]
                        elif method in ["actors", "countries", "directors", "genres", "writers", "collections"]:        attrs = [getattr(x, "tag") for x in getattr(current, method)]

                        if (not list(set(terms) & set(attrs)) and modifier != ".not") or (list(set(terms) & set(attrs)) and modifier == ".not"):
                            match = False
                            break
                length = util.print_return(length, "Filtering {}/{} {}".format((" " * (max_length - len(str(i)))) + str(i), total, current.title))
            if match:
                util.print_end(length, "{} Collection | {} | {}".format(name, "=" if current in collection_items else "+", current.title))
                if current in collection_items:             map[current.ratingKey] = None
                else:                                       current.addCollection(name)
        media_type = "{}{}".format("Movie" if self.is_movie else "Show", "s" if total > 1 else "")
        util.print_end(length, "{} {} Processed".format(total, media_type))
        return map

    def search_item(self, data, year=None):
        return util.choose_from_list(self.search(data, year=year), "movie" if self.is_movie else "show", str(data), exact=True)

    def update_metadata(self, TMDb):
        logger.info("")
        util.seperator("{} Library Metadata".format(self.name))
        logger.info("")
        if not self.metadata:
            raise Failed("No metadata to edit")
        for m in self.metadata:
            logger.info("")
            util.seperator()
            logger.info("")
            year = None
            if "year" in self.metadata[m]:
                now = datetime.datetime.now()
                if self.metadata[m]["year"] is None:                                    logger.error("Metadata Error: year attribute is blank")
                elif not isinstance(self.metadata[m]["year"], int):                     logger.error("Metadata Error: year attribute must be an integer")
                elif self.metadata[m]["year"] not in range(1800, now.year + 2):         logger.error("Metadata Error: year attribute must be between 1800-{}".format(now.year + 1))
                else:                                                                   year = self.metadata[m]["year"]

            title = m
            if "title" in self.metadata[m]:
                if self.metadata[m]["title"] is None:                                   logger.error("Metadata Error: title attribute is blank")
                else:                                                                   title = self.metadata[m]["title"]

            item = self.search_item(title, year=year)

            if item is None:
                item = self.search_item("{} (SUB)".format(title), year=year)

            if item is None and "alt_title" in self.metadata[m]:
                if self.metadata[m]["alt_title"] is None:
                    logger.error("Metadata Error: alt_title attribute is blank")
                else:
                    alt_title = self.metadata[m]["alt_title"]
                    item = self.search_item(alt_title, year=year)

            if item is None:
                logger.error("Plex Error: Item {} not found".format(m))
                logger.error("Skipping {}".format(m))
                continue

            logger.info("Updating {}: {}...".format("Movie" if self.is_movie else "Show", title))

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
                            edits["{}.value".format(key)] = value
                            edits["{}.locked".format(key)] = 1
                    else:
                        logger.error("Metadata Error: {} attribute is blank".format(name))
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
                logger.debug("Details Update: {}".format(edits))
                try:
                    item.edit(**edits)
                    item.reload()
                    logger.info("{}: {} Details Update Successful".format("Movie" if self.is_movie else "Show", m))
                except BadRequest:
                    util.print_stacktrace()
                    logger.error("{}: {} Details Update Failed".format("Movie" if self.is_movie else "Show", m))
            else:
                logger.info("{}: {} Details Update Not Needed".format("Movie" if self.is_movie else "Show", m))

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
                            logger.info("Detail: Genre {} removed".format(genre))
                for genre in (g for g in genres if g not in item_genres):
                    item.addGenre(genre)
                    logger.info("Detail: Genre {} added".format(genre))

            if "label" in self.metadata[m]:
                if self.metadata[m]["label"]:
                    item_labels = [label.tag for label in item.labels]
                    labels = util.get_list(self.metadata[m]["label"])
                    if "label_sync_mode" in self.metadata[m]:
                        if self.metadata[m]["label_sync_mode"] is None:                         logger.error("Metadata Error: label_sync_mode attribute is blank defaulting to append")
                        elif self.metadata[m]["label_sync_mode"] not in ["append", "sync"]:     logger.error("Metadata Error: label_sync_mode attribute must be either 'append' or 'sync' defaulting to append")
                        elif self.metadata[m]["label_sync_mode"] == "sync":
                            for label in (l for l in item_labels if l not in labels):
                                item.removeLabel(label)
                                logger.info("Detail: Label {} removed".format(label))
                    for label in (l for l in labels if l not in item_labels):
                        item.addLabel(label)
                        logger.info("Detail: Label {} added".format(label))
                else:
                    logger.error("Metadata Error: label attribute is blank")

            if "seasons" in self.metadata[m] and self.is_show:
                if self.metadata[m]["seasons"]:
                    for season_id in self.metadata[m]["seasons"]:
                        logger.info("")
                        logger.info("Updating season {} of {}...".format(season_id, m))
                        if isinstance(season_id, int):
                            try:                                season = item.season(season_id)
                            except NotFound:                    logger.error("Metadata Error: Season: {} not found".format(season_id))
                            else:

                                if "title" in self.metadata[m]["seasons"][season_id] and self.metadata[m]["seasons"][season_id]["title"]:
                                    title = self.metadata[m]["seasons"][season_id]["title"]
                                else:
                                    title = season.title
                                if "sub" in self.metadata[m]["seasons"][season_id]:
                                    if self.metadata[m]["seasons"][season_id]["sub"] is None:
                                        logger.error("Metadata Error: sub attribute is blank")
                                    elif self.metadata[m]["seasons"][season_id]["sub"] is True and "(SUB)" not in title:
                                        title = "{} (SUB)".format(title)
                                    elif self.metadata[m]["seasons"][season_id]["sub"] is False and title.endswith(" (SUB)"):
                                        title = title[:-6]
                                    else:
                                        logger.error("Metadata Error: sub attribute must be True or False")

                                edits = {}
                                add_edit("title", season.title, self.metadata[m]["seasons"][season_id], value=title)
                                add_edit("summary", season.summary, self.metadata[m]["seasons"][season_id])
                                if len(edits) > 0:
                                    logger.debug("Season: {} Details Update: {}".format(season_id, edits))
                                    try:
                                        season.edit(**edits)
                                        season.reload()
                                        logger.info("Season: {} Details Update Successful".format(season_id))
                                    except BadRequest:
                                        util.print_stacktrace()
                                        logger.error("Season: {} Details Update Failed".format(season_id))
                                else:
                                    logger.info("Season: {} Details Update Not Needed".format(season_id))
                        else:
                            logger.error("Metadata Error: Season: {} invalid, it must be an integer".format(season_id))
                else:
                    logger.error("Metadata Error: seasons attribute is blank")

            if "episodes" in self.metadata[m] and self.is_show:
                if self.metadata[m]["episodes"]:
                    for episode_str in self.metadata[m]["episodes"]:
                        logger.info("")
                        match = re.search("[Ss]{1}\d+[Ee]{1}\d+", episode_str)
                        if match:
                            output = match.group(0)[1:].split("E" if "E" in m.group(0) else "e")
                            episode_id = int(output[0])
                            season_id = int(output[1])
                            logger.info("Updating episode S{}E{} of {}...".format(episode_id, season_id, m))
                            try:                                episode = item.episode(season=season_id, episode=episode_id)
                            except NotFound:                    logger.error("Metadata Error: episode {} of season {} not found".format(episode_id, season_id))
                            else:
                                if "title" in self.metadata[m]["episodes"][episode_str] and self.metadata[m]["episodes"][episode_str]["title"]:
                                    title = self.metadata[m]["episodes"][episode_str]["title"]
                                else:
                                    title = episode.title
                                if "sub" in self.metadata[m]["episodes"][episode_str]:
                                    if self.metadata[m]["episodes"][episode_str]["sub"] is None:
                                        logger.error("Metadata Error: sub attribute is blank")
                                    elif self.metadata[m]["episodes"][episode_str]["sub"] is True and "(SUB)" not in title:
                                        title = "{} (SUB)".format(title)
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
                                    logger.debug("Season: {} Episode: {} Details Update: {}".format(season_id, episode_id, edits))
                                    try:
                                        episode.edit(**edits)
                                        episode.reload()
                                        logger.info("Season: {} Episode: {} Details Update Successful".format(season_id, episode_id))
                                    except BadRequest:
                                        util.print_stacktrace()
                                        logger.error("Season: {} Episode: {} Details Update Failed".format(season_id, episode_id))
                                else:
                                    logger.info("Season: {} Episode: {} Details Update Not Needed".format(season_id, episode_id))
                        else:
                            logger.error("Metadata Error: episode {} invlaid must have S##E## format".format(episode_str))
                else:
                    logger.error("Metadata Error: episodes attribute is blank")
