from modules import util
from modules.util import Failed
from arrapi import RadarrAPI
from arrapi.exceptions import ArrException

logger = util.logger

availability_translation = {"announced": "announced", "cinemas": "inCinemas", "released": "released", "db": "preDB"}
apply_tags_translation = {"": "add", "sync": "replace", "remove": "remove"}
availability_descriptions = {"announced": "For Announced", "cinemas": "For In Cinemas", "released": "For Released", "db": "For PreDB"}

class Radarr:
    def __init__(self, config, library, params):
        self.config = config
        self.library = library
        self.url = params["url"]
        self.token = params["token"]
        logger.secret(self.url)
        logger.secret(self.token)
        try:
            self.api = RadarrAPI(self.url, self.token, session=self.config.session)
            self.api.respect_list_exclusions_when_adding()
            self.api._validate_add_options(params["root_folder_path"], params["quality_profile"])
        except ArrException as e:
            raise Failed(e)
        self.add_missing = params["add_missing"]
        self.add_existing = params["add_existing"]
        self.root_folder_path = params["root_folder_path"]
        self.monitor = params["monitor"]
        self.availability = params["availability"]
        self.quality_profile = params["quality_profile"]
        self.tag = params["tag"]
        self.search = params["search"]
        self.radarr_path = params["radarr_path"] if params["radarr_path"] and params["plex_path"] else ""
        self.plex_path = params["plex_path"] if params["radarr_path"] and params["plex_path"] else ""

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
        folder = options["folder"] if "folder" in options else self.root_folder_path
        monitor = options["monitor"] if "monitor" in options else self.monitor
        availability = availability_translation[options["availability"] if "availability" in options else self.availability]
        quality_profile = options["quality"] if "quality" in options else self.quality_profile
        tags = options["tag"] if "tag" in options else self.tag
        search = options["search"] if "search" in options else self.search

        arr_paths = {}
        arr_ids = {}
        for movie in self.api.all_movies():
            if movie.path:
                arr_paths[movie.path[:-1].lower() if movie.path.endswith(("/", "\\")) else movie.path.lower()] = movie.tmdbId
            arr_ids[movie.tmdbId] = movie
        if self.config.trace_mode:
            logger.debug(arr_paths)
            logger.debug(arr_ids)

        added = []
        exists = []
        skipped = []
        invalid = []
        invalid_root = []
        movies = []
        path_lookup = {}
        mismatched = {}
        path_in_use = {}

        def mass_add():
            try:
                _a, _e, _i = self.api.add_multiple_movies(movies, folder, quality_profile, monitor, search,
                                                          availability, tags, per_request=100)
                added.extend(_a)
                exists.extend(_e)
                invalid.extend(_i)
            except ArrException as e:
                logger.stacktrace()
                raise Failed(f"Radarr Error: {e}")

        for i, item in enumerate(tmdb_ids, 1):
            path = item[1] if isinstance(item, tuple) else None
            tmdb_id = item[0] if isinstance(item, tuple) else item
            logger.ghost(f"Loading TMDb ID {i}/{len(tmdb_ids)} ({tmdb_id})")
            if self.config.Cache:
                _id = self.config.Cache.query_radarr_adds(tmdb_id, self.library.original_mapping_name)
                if _id:
                    skipped.append(item)
                    continue
            try:
                if tmdb_id in arr_ids:
                    exists.append(arr_ids[tmdb_id])
                    continue
                if path and path.lower() in arr_paths:
                    mismatched[path] = tmdb_id
                    continue
                if path and not path.startswith(folder):
                    invalid_root.append(item)
                    continue
                movie = self.api.get_movie(tmdb_id=tmdb_id)
                if self.config.trace_mode:
                    logger.debug(f"Folder to Check: {folder}/{movie.folder}")
                if f"{folder}/{movie.folder}".lower() in arr_paths:
                    path_in_use[f"{folder}/{movie.folder}"] = tmdb_id
                    continue
                if path:
                    movies.append((movie, path))
                    path_lookup[path] = tmdb_id
                else:
                    movies.append(movie)
            except ArrException:
                invalid.append(item)
            if len(movies) == 100 or len(tmdb_ids) == i:
                mass_add()
                movies = []
        if movies:
            mass_add()
            movies = []

        if len(added) > 0:
            logger.info("")
            for movie in added:
                logger.info(f"Added to Radarr | {movie.tmdbId:<7} | {movie.title}")
                if self.config.Cache:
                    self.config.Cache.update_radarr_adds(movie.tmdbId, self.library.original_mapping_name)
            logger.info(f"{len(added)} Movie{'s' if len(added) > 1 else ''} added to Radarr")

        if len(exists) > 0 or len(skipped) > 0:
            logger.info("")
            if len(exists) > 0:
                for movie in exists:
                    logger.info(f"Already in Radarr | {movie.tmdbId:<7} | {movie.title}")
                    if self.config.Cache:
                        self.config.Cache.update_radarr_adds(movie.tmdbId, self.library.original_mapping_name)
            if len(skipped) > 0:
                for movie in skipped:
                    logger.info(f"Skipped: In Cache | {movie}")
            logger.info(f"{len(exists) + len(skipped)} Movie{'s' if len(skipped) > 1 else ''} already exist in Radarr")

        if len(mismatched) > 0:
            logger.info("")
            logger.info("Items in Plex that have already been added to Radarr but under a different TMDb ID then in Plex")
            for path, tmdb_id in mismatched.items():
                logger.info(f"Plex TMDb ID: {tmdb_id:<7} | Radarr TMDb ID: {arr_paths[path.lower()]:<7} | Path: {path}")
            logger.info(f"{len(mismatched)} Movie{'s' if len(mismatched) > 1 else ''} with mismatched TMDb IDs")

        if len(path_in_use) > 0:
            logger.info("")
            logger.info("TMDb IDs that cannot be added to Radarr because the path they will use is already in use by a different TMDb ID")
            for path, tmdb_id in path_in_use.items():
                logger.info(f"TMDb ID: {tmdb_id:<7} | Radarr TMDb ID: {arr_paths[path.lower()]:<7} | Path: {path}")
            logger.info(f"{len(path_in_use)} Movie{'s' if len(path_in_use) > 1 else ''} with paths already in use by other TMDb IDs")

        if len(invalid) > 0:
            logger.info("")
            for tmdb_id in invalid:
                logger.info(f"Invalid TMDb ID | {tmdb_id}")
            logger.info(f"{len(invalid)} Movie{'s' if len(invalid) > 1 else ''} with Invalid IDs")

        if len(invalid_root) > 0:
            logger.info("")
            for tmdb_id, path in invalid_root:
                logger.info(f"Invalid Root Folder for TMDb ID | {tmdb_id:<7} | {path}")
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
