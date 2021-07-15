import logging
from modules import util
from modules.util import Failed
from arrapi import RadarrAPI
from arrapi.exceptions import ArrException, Invalid

logger = logging.getLogger("Plex Meta Manager")

availability_translation = {
    "announced": "announced",
    "cinemas": "inCinemas",
    "released": "released",
    "db": "preDB"
}
apply_tags_translation = {
    "": "add",
    "sync": "replace",
    "remove": "remove"
}

class Radarr:
    def __init__(self, config, params):
        self.config = config
        self.url = params["url"]
        self.token = params["token"]
        try:
            self.api = RadarrAPI(self.url, self.token, session=self.config.session)
        except ArrException as e:
            raise Failed(e)
        self.add = params["add"]
        self.root_folder_path = params["root_folder_path"]
        self.monitor = params["monitor"]
        self.availability = params["availability"]
        self.quality_profile = params["quality_profile"]
        self.tag = params["tag"]
        self.search = params["search"]

    def add_tmdb(self, tmdb_ids, **options):
        logger.info("")
        util.separator("Adding to Radarr", space=False, border=False)
        logger.debug("")
        logger.debug(f"TMDb IDs: {tmdb_ids}")
        folder = options["folder"] if "folder" in options else self.root_folder_path
        monitor = options["monitor"] if "monitor" in options else self.monitor
        availability = availability_translation[options["availability"] if "availability" in options else self.availability]
        quality_profile = options["quality"] if "quality" in options else self.quality_profile
        tags = options["tag"] if "tag" in options else self.tag
        search = options["search"] if "search" in options else self.search
        try:
            added, exists, invalid = self.api.add_multiple_movies(tmdb_ids, folder, quality_profile, monitor, search, availability, tags)
        except Invalid as e:
            raise Failed(f"Radarr Error: {e}")

        if len(added) > 0:
            logger.info("")
            for movie in added:
                logger.info(f"Added to Radarr | {movie.tmdbId:<6} | {movie.title}")
            logger.info(f"{len(added)} Movie{'s' if len(added) > 1 else ''} added to Radarr")

        if len(exists) > 0:
            logger.info("")
            for movie in exists:
                logger.info(f"Already in Radarr | {movie.tmdbId:<6} | {movie.title}")
            logger.info(f"{len(exists)} Movie{'s' if len(exists) > 1 else ''} already existing in Radarr")

        if len(invalid) > 0:
            logger.info("")
            for tmdb_id in invalid:
                logger.info(f"Invalid TMDb ID | {tmdb_id}")

    def edit_tags(self, tmdb_ids, tags, apply_tags):
        logger.info("")
        logger.info(f"{apply_tags_translation[apply_tags].capitalize()} Radarr Tags: {tags}")

        edited, not_exists = self.api.edit_multiple_movies(tmdb_ids, tags=tags, apply_tags=apply_tags_translation[apply_tags])

        if len(edited) > 0:
            logger.info("")
            for movie in edited:
                logger.info(f"Radarr Tags | {movie.title:<25} | {movie.tags}")
            logger.info(f"{len(edited)} Movie{'s' if len(edited) > 1 else ''} edited in Radarr")

        if len(not_exists) > 0:
            logger.info("")
            for tmdb_id in not_exists:
                logger.info(f"TMDb ID Not in Radarr | {tmdb_id}")
