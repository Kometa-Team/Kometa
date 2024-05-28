from modules import util
from modules.util import Failed, Continue
from arrapi import RadarrAPI
from arrapi.exceptions import ArrException

logger = util.logger

builders = ["radarr_all", "radarr_taglist"]
availability_translation = {"announced": "announced", "cinemas": "inCinemas", "released": "released", "db": "preDB"}
monitor_translation = {"movie": "movieOnly", "collection": "movieAndCollection", "none": "none"}
apply_tags_translation = {"": "add", "sync": "replace", "remove": "remove"}
availability_descriptions = {"announced": "For Announced", "cinemas": "For In Cinemas", "released": "For Released", "db": "For PreDB"}
monitor_descriptions = {"movie": "Monitor Only the Movie", "collection": "Monitor the Movie and Collection", "none": "Do not Monitor"}

class Radarr:
    def __init__(self, requests, cache, library, params):
        self.requests = requests
        self.cache = cache
        self.library = library
        self.url = params["url"]
        self.token = params["token"]
        logger.secret(self.url)
        logger.secret(self.token)
        try:
            self.api = RadarrAPI(self.url, self.token, session=self.requests.session)
            self.api.respect_list_exclusions_when_adding()
            self.api._validate_add_options(params["root_folder_path"], params["quality_profile"]) # noqa
            self.profiles = self.api.quality_profile()
        except ArrException as e:
            raise Failed(e)
        self.add_missing = params["add_missing"]
        self.add_existing = params["add_existing"]
        self.upgrade_existing = params["upgrade_existing"]
        self.monitor_existing = params["monitor_existing"]
        self.root_folder_path = params["root_folder_path"]
        self.monitor = params["monitor"]
        self.availability = params["availability"]
        self.quality_profile = params["quality_profile"]
        self.tag = params["tag"]
        self.search = params["search"]
        self.radarr_path = params["radarr_path"] if params["radarr_path"] and params["plex_path"] else ""
        self.plex_path = params["plex_path"] if params["radarr_path"] and params["plex_path"] else ""
        self.ignore_cache = params["ignore_cache"]

    def add_tmdb(self, tmdb_ids, **options):
        _ids = []
        _paths = []
        for tmdb_id in tmdb_ids:
            if isinstance(tmdb_id, tuple):
                _paths.append(tmdb_id)
            else:
                _ids.append(tmdb_id)
        logger.info("")
        logger.separator(f"Adding {'Missing' if _ids else 'Existing'} to Radarr", space=False, border=False)
        logger.debug("")
        logger.debug(f"Radarr Adds: {_ids if _ids else ''}")
        for tmdb_id in _paths:
            logger.debug(tmdb_id)
        logger.trace("")
        upgrade_existing = options["upgrade_existing"] if "upgrade_existing" in options else self.upgrade_existing
        monitor_existing = options["monitor_existing"] if "monitor_existing" in options else self.monitor_existing
        ignore_cache = options["ignore_cache"] if "ignore_cache" in options else self.ignore_cache
        folder = options["folder"] if "folder" in options else self.root_folder_path
        monitor = options["monitor"] if "monitor" in options else self.monitor
        availability = availability_translation[options["availability"] if "availability" in options else self.availability]
        quality_profile = options["quality"] if "quality" in options else self.quality_profile
        tags = options["tag"] if "tag" in options else self.tag
        search = options["search"] if "search" in options else self.search
        logger.trace(f"Upgrade Existing: {upgrade_existing}")
        logger.trace(f"Monitor Existing: {monitor_existing}")
        logger.trace(f"Ignore Cache: {ignore_cache}")
        logger.trace(f"Folder: {folder}")
        logger.trace(f"Monitor: {monitor}")
        logger.trace(f"Availability: {availability}")
        logger.trace(f"Quality Profile: {quality_profile}")
        logger.trace(f"Tags: {tags}")
        logger.trace(f"Search: {search}")
        logger.trace("")

        arr_paths = {}
        arr_ids = {}
        for movie in self.api.all_movies():
            if movie.path:
                arr_paths[movie.path[:-1].lower() if movie.path.endswith(("/", "\\")) else movie.path.lower()] = movie.tmdbId
            arr_ids[movie.tmdbId] = movie
        logger.trace(arr_paths)
        logger.trace(arr_ids)
        logger.trace("")

        added = []
        exists = []
        skipped = []
        invalid = []
        excluded = []
        invalid_root = []
        movies = []
        path_lookup = {}
        mismatched = {}
        path_in_use = {}

        for i, item in enumerate(tmdb_ids, 1):
            path = item[1] if isinstance(item, tuple) else None
            tmdb_id = item[0] if isinstance(item, tuple) else item
            logger.ghost(f"Loading TMDb ID {i}/{len(tmdb_ids)} ({tmdb_id})")
            try:
                if self.cache and not ignore_cache:
                    _id = self.cache.query_radarr_adds(tmdb_id, self.library.original_mapping_name)
                    if _id:
                        skipped.append(item)
                        raise Continue
                if tmdb_id in arr_ids:
                    exists.append(arr_ids[tmdb_id])
                    raise Continue
                if path and path.lower() in arr_paths:
                    mismatched[path] = tmdb_id
                    raise Continue
                if path and not path.startswith(folder):
                    invalid_root.append(item)
                    raise Continue
                movie = self.api.get_movie(tmdb_id=tmdb_id)
                logger.trace(f"Folder to Check: {folder}/{movie.folder}")
                if f"{folder}/{movie.folder}".lower() in arr_paths:
                    path_in_use[f"{folder}/{movie.folder}"] = tmdb_id
                    raise Continue
                if path:
                    movies.append((movie, path))
                    path_lookup[path] = tmdb_id
                else:
                    movies.append(movie)
            except ArrException:
                invalid.append(item)
            except Continue:
                pass
            if movies and (len(movies) == 100 or len(tmdb_ids) == i):
                try:
                    _a, _e, _i, _x = self.api.add_multiple_movies(movies, folder, quality_profile, monitor, search,
                                                                  availability, tags, per_request=100)
                    added.extend(_a)
                    exists.extend(_e)
                    invalid.extend(_i)
                    excluded.extend(_x)
                    movies = []
                except ArrException as e:
                    logger.stacktrace()
                    raise Failed(f"Radarr Error: {e}")

        qp = None
        for profile in self.profiles:
            if (isinstance(quality_profile, int) and profile.id == quality_profile) or profile.name == quality_profile:
                qp = profile

        if len(added) > 0:
            logger.info("")
            for movie in added:
                logger.info(f"Added to Radarr | {movie.tmdbId:<7} | {movie.title}")
                if self.cache:
                    self.cache.update_radarr_adds(movie.tmdbId, self.library.original_mapping_name)
            logger.info(f"{len(added)} Movie{'s' if len(added) > 1 else ''} added to Radarr")

        if len(exists) > 0 or len(skipped) > 0:
            logger.info("")
            if len(exists) > 0:
                upgrade_qp = []
                remonitor = []
                for movie in exists:
                    if (movie.monitored != monitor and monitor_existing) or (movie.qualityProfileId != qp.id and upgrade_existing):
                        if movie.monitored != monitor and monitor_existing:
                            remonitor.append(movie)
                        if movie.qualityProfileId != qp.id and upgrade_existing:
                            upgrade_qp.append(movie)
                    else:
                        logger.info(f"Already in Radarr | {movie.tmdbId:<7} | {movie.title}")
                    if self.cache:
                        self.cache.update_radarr_adds(movie.tmdbId, self.library.original_mapping_name)
                if upgrade_qp:
                    self.api.edit_multiple_movies(upgrade_qp, quality_profile=qp)
                    for movie in upgrade_qp:
                        logger.info(f"Quality Upgraded To {qp.name} | {movie.tmdbId:<7} | {movie.title}")
                if remonitor:
                    self.api.edit_multiple_movies(remonitor, monitored=monitor)
                    for movie in remonitor:
                        logger.info(f"Monitored: {monitor} in Radarr | {movie.tmdbId:<7} | {movie.title}")
            if len(skipped) > 0:
                logger.info(f"Skipped In Cache: {skipped}")
            logger.info("")
            logger.info(f"{len(exists) + len(skipped)} Movie{'s' if len(skipped) > 1 else ''} already exist in Radarr")

        if len(mismatched) > 0:
            logger.info("")
            logger.info("Items in Plex that have already been added to Radarr but under a different TMDb ID then in Plex")
            for path, tmdb_id in mismatched.items():
                logger.info(f"Plex TMDb ID: {tmdb_id:<7} | Radarr TMDb ID: {arr_paths[path.lower()]:<7} | Path: {path}")
            logger.info("")
            logger.info(f"{len(mismatched)} Movie{'s' if len(mismatched) > 1 else ''} with mismatched TMDb IDs")

        if len(path_in_use) > 0:
            logger.info("")
            logger.info("TMDb IDs that cannot be added to Radarr because the path they will use is already in use by a different TMDb ID")
            for path, tmdb_id in path_in_use.items():
                logger.info(f"TMDb ID: {tmdb_id:<7} | Radarr TMDb ID: {arr_paths[path.lower()]:<7} | Path: {path}")
            logger.info("")
            logger.info(f"{len(path_in_use)} Movie{'s' if len(path_in_use) > 1 else ''} with paths already in use by other TMDb IDs")

        if len(invalid) > 0:
            logger.info("")
            logger.info(f"Invalid TMDb IDs: {invalid}")
            logger.info("")
            logger.info(f"{len(invalid)} Movie{'s' if len(invalid) > 1 else ''} with Invalid IDs")

        if len(excluded) > 0:
            logger.info("")
            logger.info(f"Excluded TMDb IDs: {excluded}")
            logger.info("")
            logger.info(f"{len(excluded)} Movie{'s' if len(excluded) > 1 else ''} ignored by Radarr's Exclusion List")

        if len(invalid_root) > 0:
            logger.info("")
            for tmdb_id, path in invalid_root:
                logger.info(f"Invalid Root Folder for TMDb ID | {tmdb_id:<7} | {path}")
            logger.info("")
            logger.info(f"{len(invalid_root)} Movie{'s' if len(invalid_root) > 1 else ''} with Invalid Paths")

        return added

    def edit_tags(self, tmdb_ids, tags, apply_tags):
        logger.info("")
        logger.info(f"{apply_tags_translation[apply_tags].capitalize()} Radarr Tags: {tags}")

        edited, not_exists = self.api.edit_multiple_movies(tmdb_ids, tags=tags, apply_tags=apply_tags_translation[apply_tags], per_request=100)

        if len(edited) > 0:
            logger.info("")
            for movie in edited:
                logger.info(f"Radarr Tags | {movie.title:<25} | {movie.tags}")
            logger.info(f"{len(edited)} Movie{'s' if len(edited) > 1 else ''} edited in Radarr")

        if len(not_exists) > 0:
            logger.info("")
            for tmdb_id in not_exists:
                logger.info(f"TMDb ID Not in Radarr | {tmdb_id}")

    def remove_all_with_tags(self, tags):
        lower_tags = [_t.lower() for _t in tags]
        remove_items = []
        for movie in self.api.all_movies():
            tag_strs = [_t.label.lower() for _t in movie.tags]
            remove = True
            for tag in lower_tags:
                if tag not in tag_strs:
                    remove = False
                    break
            if remove:
                remove_items.append(movie)
        if remove_items:
            self.api.delete_multiple_movies(remove_items)

    def get_tmdb_ids(self, method, data):
        ids = []
        allowed = [t.id for t in self.api.all_tags() if t.label.lower() in data] if method == "radarr_taglist" else []
        for movie in self.api.all_movies():
            append = False
            if method == "radarr_all":
                append = True
            elif method == "radarr_taglist":
                if data:
                    for tag in movie.tags:
                        if tag.id in allowed:
                            append = True
                            break
                elif not movie.tags:
                    append = True
            if append:
                ids.append((movie.tmdbId, "tmdb"))
        return ids
