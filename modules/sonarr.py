from modules import util
from modules.util import Failed, Continue
from arrapi import SonarrAPI
from arrapi.exceptions import ArrException

logger = util.logger

builders = ["sonarr_all", "sonarr_taglist"]
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
    def __init__(self, requests, cache, library, params):
        self.requests = requests
        self.cache = cache
        self.library = library
        self.url = params["url"]
        self.token = params["token"]
        logger.secret(self.url)
        logger.secret(self.token)
        try:
            self.api = SonarrAPI(self.url, self.token, session=self.requests.session)
            self.api.respect_list_exclusions_when_adding()
            self.api._validate_add_options(params["root_folder_path"], params["quality_profile"], params["language_profile"]) # noqa
            self.profiles = self.api.quality_profile()
        except ArrException as e:
            raise Failed(e)
        self.add_missing = params["add_missing"]
        self.add_existing = params["add_existing"]
        self.upgrade_existing = params["upgrade_existing"]
        self.monitor_existing = params["monitor_existing"]
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
        self.ignore_cache = params["ignore_cache"]

    def add_tvdb(self, tvdb_ids, **options):
        _ids = []
        _paths = []
        for tvdb_id in tvdb_ids:
            if isinstance(tvdb_id, tuple):
                _paths.append(tvdb_id)
            else:
                _ids.append(tvdb_id)
        logger.info("")
        logger.separator(f"Adding {'Missing' if _ids else 'Existing'} to Sonarr", space=False, border=False)
        logger.debug("")
        logger.debug(f"Sonarr Adds: {_ids if _ids else ''}")
        for tvdb_id in _paths:
            logger.debug(tvdb_id)
        upgrade_existing = options["upgrade_existing"] if "upgrade_existing" in options else self.upgrade_existing
        monitor_existing = options["monitor_existing"] if "monitor_existing" in options else self.monitor_existing
        ignore_cache = options["ignore_cache"] if "ignore_cache" in options else self.ignore_cache
        folder = options["folder"] if "folder" in options else self.root_folder_path
        monitor = monitor_translation[options["monitor"] if "monitor" in options else self.monitor]
        quality_profile = options["quality"] if "quality" in options else self.quality_profile
        language_profile = options["language"] if "language" in options else self.language_profile
        language_profile = language_profile if self.api._raw.v3 else 1 # noqa
        series_type = options["series"] if "series" in options else self.series_type
        season = options["season"] if "season" in options else self.season_folder
        tags = options["tag"] if "tag" in options else self.tag
        search = options["search"] if "search" in options else self.search
        cutoff_search = options["cutoff_search"] if "cutoff_search" in options else self.cutoff_search
        logger.trace(f"Upgrade Existing: {upgrade_existing}")
        logger.trace(f"Monitor Existing: {monitor_existing}")
        logger.trace(f"Ignore Cache: {ignore_cache}")
        logger.trace(f"Folder: {folder}")
        logger.trace(f"Monitor: {monitor}")
        logger.trace(f"Quality Profile: {quality_profile}")
        logger.trace(f"Language Profile: {language_profile}")
        logger.trace(f"Series Type: {series_type}")
        logger.trace(f"Season: {season}")
        logger.trace(f"Tags: {tags}")
        logger.trace(f"Search: {search}")
        logger.trace(f"Cutoff Search: {cutoff_search}")

        arr_paths = {}
        arr_ids = {}
        for series in self.api.all_series():
            if series.path:
                arr_paths[series.path[:-1].lower() if series.path.endswith(("/", "\\")) else series.path.lower()] = series.tvdbId
            arr_ids[series.tvdbId] = series
        logger.trace(arr_paths)
        logger.trace(arr_ids)

        added = []
        exists = []
        skipped = []
        invalid = []
        excluded = []
        invalid_root = []
        shows = []
        path_lookup = {}
        mismatched = {}
        path_in_use = {}

        for i, item in enumerate(tvdb_ids, 1):
            path = item[1] if isinstance(item, tuple) else None
            tvdb_id = item[0] if isinstance(item, tuple) else item
            logger.ghost(f"Loading TVDb ID {i}/{len(tvdb_ids)} ({tvdb_id})")
            try:
                if self.cache and not ignore_cache:
                    _id = self.cache.query_sonarr_adds(tvdb_id, self.library.original_mapping_name)
                    if _id:
                        skipped.append(item)
                        raise Continue
                if tvdb_id in arr_ids:
                    exists.append(arr_ids[tvdb_id])
                    raise Continue
                if path and path.lower() in arr_paths:
                    mismatched[path] = tvdb_id
                    raise Continue
                if path and not path.startswith(folder):
                    invalid_root.append(item)
                    raise Continue
                show = self.api.get_series(tvdb_id=tvdb_id)
                logger.trace(f"Folder to Check: {folder}/{show.folder}")
                if f"{folder}/{show.folder}".lower() in arr_paths:
                    path_in_use[f"{folder}/{show.folder}"] = tvdb_id
                    raise Continue
                if path:
                    shows.append((show, path))
                    path_lookup[path] = tvdb_id
                else:
                    shows.append(show)
            except ArrException:
                invalid.append(item)
            except Continue:
                pass
            if shows and (len(shows) == 100 or len(tvdb_ids) == i):
                try:
                    _a, _e, _i, _x = self.api.add_multiple_series(shows, folder, quality_profile, language_profile, monitor,
                                                                  season, search, cutoff_search, series_type, tags, per_request=100)
                    added.extend(_a)
                    exists.extend(_e)
                    invalid.extend(_i)
                    excluded.extend(_x)
                    shows = []
                except ArrException as e:
                    logger.stacktrace()
                    raise Failed(f"Sonarr Error: {e}")

        qp = None
        for profile in self.profiles:
            if (isinstance(quality_profile, int) and profile.id == quality_profile) or profile.name == quality_profile:
                qp = profile

        if len(added) > 0:
            logger.info("")
            for series in added:
                logger.info(f"Added to Sonarr | {series.tvdbId:<7} | {series.title}")
                if self.cache:
                    self.cache.update_sonarr_adds(series.tvdbId, self.library.original_mapping_name)
            logger.info(f"{len(added)} Series added to Sonarr")

        if len(exists) > 0 or len(skipped) > 0:
            logger.info("")
            if len(exists) > 0:
                upgrade_qp = []
                remonitor = []
                for series in exists:
                    if monitor_existing or (series.qualityProfileId != qp.id and upgrade_existing):
                        if monitor_existing:
                            remonitor.append(series)
                        if series.qualityProfileId != qp.id and upgrade_existing:
                            upgrade_qp.append(series)
                    else:
                        logger.info(f"Already in Sonarr | {series.tvdbId:<7} | {series.title}")
                    if self.cache:
                        self.cache.update_sonarr_adds(series.tvdbId, self.library.original_mapping_name)
                if upgrade_qp:
                    self.api.edit_multiple_series(upgrade_qp, quality_profile=qp)
                    for series in upgrade_qp:
                        logger.info(f"Quality Upgraded To {qp.name} | {series.tvdbId:<7} | {series.title}")
                if remonitor:
                    self.api.edit_multiple_series(remonitor, monitor=monitor)
                    for series in remonitor:
                        logger.info(f"Monitored: {monitor} in Sonarr | {series.tvdbId:<7} | {series.title}")
            if len(skipped) > 0:
                logger.info(f"Skipped In Cache: {skipped}")
            logger.info("")
            logger.info(f"{len(exists) + len(skipped)} Series already exist in Sonarr")

        if len(mismatched) > 0:
            logger.info("")
            logger.info("Items in Plex that have already been added to Sonarr but under a different TVDb ID then in Plex")
            for path, tmdb_id in mismatched.items():
                logger.info(f"Plex TVDb ID: {tmdb_id:<7} | Sonarr TVDb ID: {arr_paths[path.lower()]:<7} | Path: {path}")
            logger.info("")
            logger.info(f"{len(mismatched)} Series with mismatched TVDb IDs")

        if len(path_in_use) > 0:
            logger.info("")
            logger.info("TVDb IDs that cannot be added to Sonarr because the path they will use is already in use by a different TVDb ID")
            for path, tvdb_id in path_in_use.items():
                logger.info(f"TVDb ID: {tvdb_id:<7} | Sonarr TVDb ID: {arr_paths[path.lower()]:<7} | Path: {path}")
            logger.info("")
            logger.info(f"{len(path_in_use)} Series with paths already in use by other TVDb IDs")

        if len(invalid) > 0:
            logger.info("")
            logger.info(f"Invalid TVDb IDs: {invalid}")
            logger.info("")
            logger.info(f"{len(invalid)} Series with Invalid IDs")

        if len(excluded) > 0:
            logger.info("")
            logger.info(f"Excluded TVDb IDs: {excluded}")
            logger.info("")
            logger.info(f"{len(excluded)} Series ignored by Sonarr's Exclusion List")

        if len(invalid_root) > 0:
            logger.info("")
            for tvdb_id, path in invalid_root:
                logger.info(f"Invalid Root Folder for TVDb ID | {tvdb_id:<7} | {path}")
            logger.info("")
            logger.info(f"{len(invalid_root)} Series with Invalid Paths")

        return added

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

    def get_tvdb_ids(self, method, data):
        ids = []
        allowed = [t.id for t in self.api.all_tags() if t.label.lower() in data] if method == "sonarr_taglist" else []
        for series in self.api.all_series():
            append = False
            if method == "sonarr_all":
                append = True
            elif method == "sonarr_taglist":
                if data:
                    for tag in series.tags:
                        if tag.id in allowed:
                            append = True
                            break
                elif not series.tags:
                    append = True
            if append:
                ids.append((series.tvdbId, "tvdb"))
        return ids
