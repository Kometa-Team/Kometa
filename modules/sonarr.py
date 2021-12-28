import logging
from modules import util
from modules.util import Failed
from arrapi import SonarrAPI
from arrapi.exceptions import ArrException, Invalid

logger = logging.getLogger("Plex Meta Manager")

series_types = ["standard", "daily", "anime"]
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
    def __init__(self, config, library, params):
        self.config = config
        self.library = library
        self.url = params["url"]
        self.token = params["token"]
        try:
            self.api = SonarrAPI(self.url, self.token, session=self.config.session)
            self.api.respect_list_exclusions_when_adding()
            self.api._validate_add_options(params["root_folder_path"], params["quality_profile"], params["language_profile"])
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
        self.sonarr_path = params["sonarr_path"] if params["sonarr_path"] and params["plex_path"] else ""
        self.plex_path = params["plex_path"] if params["sonarr_path"] and params["plex_path"] else ""

    def add_tvdb(self, tvdb_ids, **options):
        logger.info("")
        util.separator("Adding to Sonarr", space=False, border=False)
        logger.debug("")
        _ids = []
        _paths = []
        for tvdb_id in tvdb_ids:
            if isinstance(tvdb_id, tuple):
                _paths.append(tvdb_id)
            else:
                _ids.append(tvdb_id)
        logger.debug(f"Sonarr Adds: {_ids if _ids else ''}")
        for tvdb_id in _paths:
            logger.debug(tvdb_id)
        folder = options["folder"] if "folder" in options else self.root_folder_path
        monitor = monitor_translation[options["monitor"] if "monitor" in options else self.monitor]
        quality_profile = options["quality"] if "quality" in options else self.quality_profile
        language_profile = options["language"] if "language" in options else self.language_profile
        language_profile = language_profile if self.api._raw.v3 else 1
        series_type = options["series"] if "series" in options else self.series_type
        season = options["season"] if "season" in options else self.season_folder
        tags = options["tag"] if "tag" in options else self.tag
        search = options["search"] if "search" in options else self.search
        cutoff_search = options["cutoff_search"] if "cutoff_search" in options else self.cutoff_search

        arr_paths = {}
        arr_ids = {}
        for series in self.api.all_series():
            if series.path:
                arr_paths[series.path[:-1].lower() if series.path.endswith(("/", "\\")) else series.path.lower()] = series.tvdbId
            arr_ids[series.tvdbId] = series
        if self.config.trace_mode:
            logger.debug(arr_paths)
            logger.debug(arr_ids)

        added = []
        exists = []
        skipped = []
        invalid = []
        shows = []
        path_lookup = {}
        mismatched = {}
        path_in_use = {}
        for i, item in enumerate(tvdb_ids, 1):
            path = item[1] if isinstance(item, tuple) else None
            tvdb_id = item[0] if isinstance(item, tuple) else item
            util.print_return(f"Loading TVDb ID {i}/{len(tvdb_ids)} ({tvdb_id})")
            if self.config.Cache:
                _id = self.config.Cache.query_sonarr_adds(tvdb_id, self.library.original_mapping_name)
                if _id:
                    skipped.append(item)
                    continue
            try:
                if tvdb_id in arr_ids:
                    exists.append(arr_ids[tvdb_id])
                    continue
                if path.lower() in arr_paths:
                    mismatched[path] = tvdb_id
                    continue
                show = self.api.get_series(tvdb_id=tvdb_id)
                if f"{folder}/{show.folder}".lower() in arr_paths:
                    path_in_use[f"{folder}/{show.folder}"] = tvdb_id
                    continue
                if path:
                    shows.append((show, path))
                    path_lookup[path] = tvdb_id
                else:
                    shows.append(show)
            except ArrException:
                invalid.append(item)
            if len(shows) == 100 or len(tvdb_ids) == i:
                try:
                    _a, _e, _i = self.api.add_multiple_series(shows, folder, quality_profile, language_profile, monitor,
                                                              season, search, cutoff_search, series_type, tags, per_request=100)
                    added.extend(_a)
                    exists.extend(_e)
                    invalid.extend(_i)
                    shows = []
                except Invalid as e:
                    raise Failed(f"Sonarr Error: {e}")

        if len(added) > 0:
            logger.info("")
            for series in added:
                logger.info(f"Added to Sonarr | {series.tvdbId:<6} | {series.title}")
                if self.config.Cache:
                    self.config.Cache.update_sonarr_adds(series.tvdbId, self.library.original_mapping_name)
            logger.info(f"{len(added)} Series added to Sonarr")

        if len(exists) > 0 or len(skipped) > 0:
            logger.info("")
            if len(exists) > 0:
                for series in exists:
                    logger.info(f"Already in Sonarr | {series.tvdbId:<6} | {series.title}")
                    if self.config.Cache:
                        self.config.Cache.update_sonarr_adds(series.tvdbId, self.library.original_mapping_name)
            if len(skipped) > 0:
                for series in skipped:
                    logger.info(f"Skipped: In Cache | {series}")
            logger.info(f"{len(exists) + len(skipped)} Series already exist in Sonarr")

        if len(mismatched) > 0:
            logger.info("")
            logger.info("Items in Plex that have already been added to Sonarr but under a different TVDb ID then in Plex")
            for path, tmdb_id in mismatched.items():
                logger.info(f"Plex TVDb ID: {tmdb_id:<7} | Sonarr TVDb ID: {arr_paths[path.lower()]:<7} | Path: {path}")
            logger.info(f"{len(mismatched)} Series with mismatched TVDb IDs")

        if len(path_in_use) > 0:
            logger.info("")
            logger.info("TVDb IDs that cannot be added to Sonarr because the path they will use is already in use by a different TVDb ID")
            for path, tvdb_id in path_in_use.items():
                logger.info(f"TVDb ID: {tvdb_id:<7} | Sonarr TVDb ID: {arr_paths[path.lower()]:<7} | Path: {path}")
            logger.info(f"{len(path_in_use)} Series with paths already in use by other TVDb IDs")

        if len(invalid) > 0:
            for tvdb_id in invalid:
                logger.info("")
                logger.info(f"Invalid TVDb ID | {tvdb_id}")
            logger.info(f"{len(invalid)} Series with Invalid IDs")

        return len(added)

    def edit_tags(self, tvdb_ids, tags, apply_tags):
        logger.info("")
        logger.info(f"{apply_tags_translation[apply_tags].capitalize()} Sonarr Tags: {tags}")

        edited, not_exists = self.api.edit_multiple_series(tvdb_ids, tags=tags, apply_tags=apply_tags_translation[apply_tags], per_request=100)

        if len(edited) > 0:
            logger.info("")
            for series in edited:
                logger.info(f"Sonarr Tags | {series.title:<25} | {series.tags}")
            logger.info(f"{len(edited)} Series edited in Sonarr")

        if len(not_exists) > 0:
            logger.info("")
            for tvdb_id in not_exists:
                logger.info(f"TVDb ID Not in Sonarr | {tvdb_id}")

    def remove_all_with_tags(self, tags):
        lower_tags = [_t.lower() for _t in tags]
        remove_items = []
        for series in self.api.all_series():
            tag_strs = [_t.label.lower() for _t in series.tags]
            remove = True
            for tag in lower_tags:
                if tag not in tag_strs:
                    remove = False
                    break
            if remove:
                remove_items.append(series)
        if remove_items:
            self.api.delete_multiple_series(remove_items)
