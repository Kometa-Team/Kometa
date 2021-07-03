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

class Radarr:
    def __init__(self, params):
        self.url = params["url"]
        self.token = params["token"]
        try:
            self.api = RadarrAPI(self.url, self.token)
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
        util.separator(f"Adding to Radarr", space=False, border=False)
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

        for movie in invalid:
            logger.info("")
            logger.info(f"Invalid TMDb ID | {movie}")
