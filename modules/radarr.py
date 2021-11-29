import logging
from modules import util
from modules.util import Failed
from arrapi import RadarrAPI
from arrapi.exceptions import ArrException, Invalid

logger = logging.getLogger("Plex Meta Manager")

availability_translation = {"announced": "announced", "cinemas": "inCinemas", "released": "released", "db": "preDB"}
apply_tags_translation = {"": "add", "sync": "replace", "remove": "remove"}
availability_descriptions = {"announced": "For Announced", "cinemas": "For In Cinemas", "released": "For Released", "db": "For PreDB"}

class Radarr:
    def __init__(self, config, library, params):
        self.config = config
        self.library = library
        self.url = params["url"]
        self.token = params["token"]
        try:
            self.api = RadarrAPI(self.url, self.token, session=self.config.session)
            self.api.respect_list_exclusions_when_adding()
        except ArrException as e:
            raise Failed(e)
        self.add = params["add"]
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
        logger.info("")
        util.separator("Adding to Radarr", space=False, border=False)
        logger.debug("")
        for tmdb_id in tmdb_ids:
            logger.debug(tmdb_id)
        folder = options["folder"] if "folder" in options else self.root_folder_path
        monitor = options["monitor"] if "monitor" in options else self.monitor
        availability = availability_translation[options["availability"] if "availability" in options else self.availability]
        quality_profile = options["quality"] if "quality" in options else self.quality_profile
        tags = options["tag"] if "tag" in options else self.tag
        search = options["search"] if "search" in options else self.search

        added = []
        exists = []
        invalid = []
        movies = []
        for i, item in enumerate(tmdb_ids, 1):
            path = item[1] if isinstance(item, tuple) else None
            tmdb_id = item[0] if isinstance(item, tuple) else item
            util.print_return(f"Loading TMDb ID {i}/{len(tmdb_ids)} ({tmdb_id})")
            if self.config.Cache:
                _id = self.config.Cache.query_radarr_adds(tmdb_id, self.library.original_mapping_name)
                if _id:
                    exists.append(item)
                    continue
            try:
                movie = self.api.get_movie(tmdb_id=tmdb_id)
                movies.append((movie, path) if path else movie)
            except ArrException:
                invalid.append(item)
            if len(movies) == 100 or len(tmdb_ids) == i:
                try:
                    _a, _e, _i = self.api.add_multiple_movies(movies, folder, quality_profile, monitor, search,
                                                              availability, tags, per_request=100)
                    added.extend(_a)
                    exists.extend(_e)
                    invalid.extend(_i)
                    movies = []
                except Invalid as e:
                    raise Failed(f"Radarr Error: {e}")

        if len(added) > 0:
            logger.info("")
            for movie in added:
                logger.info(f"Added to Radarr | {movie.tmdbId:<6} | {movie.title}")
                if self.config.Cache:
                    self.config.Cache.update_radarr_adds(movie.tmdbId, self.library.original_mapping_name)
            logger.info(f"{len(added)} Movie{'s' if len(added) > 1 else ''} added to Radarr")

        if len(exists) > 0:
            logger.info("")
            for movie in exists:
                logger.info(f"Already in Radarr | {movie.tmdbId:<6} | {movie.title}")
                if self.config.Cache:
                    self.config.Cache.update_radarr_adds(movie.tmdbId, self.library.original_mapping_name)
            logger.info(f"{len(exists)} Movie{'s' if len(exists) > 1 else ''} already existing in Radarr")

        if len(invalid) > 0:
            logger.info("")
            for tmdb_id in invalid:
                logger.info(f"Invalid TMDb ID | {tmdb_id}")

        return len(added)

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
