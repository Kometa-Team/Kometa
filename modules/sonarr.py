import logging
from modules import util
from modules.util import Failed
from arrapi import SonarrAPI
from arrapi.exceptions import ArrException, Invalid

logger = logging.getLogger("Plex Meta Manager")

series_type = ["standard", "daily", "anime"]
monitor_translation = {
    "all": "all", "future": "future", "missing": "missing", "existing": "existing",
    "pilot": "pilot", "first": "firstSeason", "latest": "latestSeason", "none": "none"
}
series_type_descriptions = {
    "standard": "Episodes released with SxxEyy pattern",
    "daily": "Episodes released daily or less frequently that use year-month-day (2017-05-25)",
    "anime": "Episodes released using an absolute episode number"
}
monitor_descriptions = {
    "all": "Monitor all episodes except specials",
    "future": "Monitor episodes that have not aired yet",
    "missing": "Monitor episodes that do not have files or have not aired yet",
    "existing": "Monitor episodes that have files or have not aired yet",
    "pilot": "Monitor the first episode. All other episodes will be ignored",
    "first": "Monitor all episodes of the first season. All other seasons will be ignored",
    "latest": "Monitor all episodes of the latest season and future seasons",
    "none": "No episodes will be monitored"
}
apply_tags_translation = {"": "add", "sync": "replace", "remove": "remove"}

class Sonarr:
    def __init__(self, config, params):
        self.config = config
        self.url = params["url"]
        self.token = params["token"]
        try:
            self.api = SonarrAPI(self.url, self.token, session=self.config.session)
        except ArrException as e:
            raise Failed(e)
        self.add = params["add"]
        self.add_existing = params["add_existing"]
        self.root_folder_path = params["root_folder_path"]
        self.monitor = params["monitor"]
        self.quality_profile = params["quality_profile"]
        self.language_profile_id = None
        self.language_profile = params["language_profile"]
        self.series_type = params["series_type"]
        self.season_folder = params["season_folder"]
        self.tag = params["tag"]
        self.search = params["search"]
        self.cutoff_search = params["cutoff_search"]

    def add_tvdb(self, tvdb_ids, **options):
        logger.info("")
        util.separator("Adding to Sonarr", space=False, border=False)
        logger.debug("")
        logger.debug(f"TVDb IDs: {tvdb_ids}")
        folder = options["folder"] if "folder" in options else self.root_folder_path
        monitor = monitor_translation[options["monitor"] if "monitor" in options else self.monitor]
        quality_profile = options["quality"] if "quality" in options else self.quality_profile
        language_profile = options["language"] if "language" in options else self.language_profile
        language_profile = language_profile if self.api.v3 else 1
        series = options["series"] if "series" in options else self.series_type
        season = options["season"] if "season" in options else self.season_folder
        tags = options["tag"] if "tag" in options else self.tag
        search = options["search"] if "search" in options else self.search
        cutoff_search = options["cutoff_search"] if "cutoff_search" in options else self.cutoff_search
        try:
            added, exists, invalid = self.api.add_multiple_series(tvdb_ids, folder, quality_profile, language_profile, monitor, season, search, cutoff_search, series, tags)
        except Invalid as e:
            raise Failed(f"Sonarr Error: {e}")

        if len(added) > 0:
            logger.info("")
            for series in added:
                logger.info(f"Added to Sonarr | {series.tvdbId:<6} | {series.title}")
            logger.info(f"{len(added)} Series added to Sonarr")

        if len(exists) > 0:
            logger.info("")
            for series in exists:
                logger.info(f"Already in Sonarr | {series.tvdbId:<6} | {series.title}")
            logger.info(f"{len(exists)} Series already existing in Sonarr")

        if len(invalid) > 0:
            for tvdb_id in invalid:
                logger.info("")
                logger.info(f"Invalid TVDb ID | {tvdb_id}")

    def edit_tags(self, tvdb_ids, tags, apply_tags):
        logger.info("")
        logger.info(f"{apply_tags_translation[apply_tags].capitalize()} Sonarr Tags: {tags}")

        edited, not_exists = self.api.edit_multiple_series(tvdb_ids, tags=tags, apply_tags=apply_tags_translation[apply_tags])

        if len(edited) > 0:
            logger.info("")
            for series in edited:
                logger.info(f"Sonarr Tags | {series.title:<25} | {series.tags}")
            logger.info(f"{len(edited)} Series edited in Sonarr")

        if len(not_exists) > 0:
            logger.info("")
            for tvdb_id in not_exists:
                logger.info(f"TVDb ID Not in Sonarr | {tvdb_id}")
