import glob, logging, os, re, requests, time
from modules import util
from modules.anidb import AniDBAPI
from modules.anilist import AniListAPI
from modules.arms import ArmsAPI
from modules.builder import CollectionBuilder
from modules.cache import Cache
from modules.imdb import IMDbAPI
from modules.letterboxd import LetterboxdAPI
from modules.mal import MyAnimeListAPI
from modules.omdb import OMDbAPI
from modules.plex import PlexAPI
from modules.radarr import RadarrAPI
from modules.sonarr import SonarrAPI
from modules.tautulli import TautulliAPI
from modules.tmdb import TMDbAPI
from modules.trakttv import TraktAPI
from modules.tvdb import TVDbAPI
from modules.util import Failed
from plexapi.exceptions import BadRequest
from retrying import retry
from ruamel import yaml

logger = logging.getLogger("Plex Meta Manager")

sync_modes = {"append": "Only Add Items to the Collection", "sync": "Add & Remove Items from the Collection"}
radarr_versions = {"v2": "For Radarr 0.2", "v3": "For Radarr 3.0"}
radarr_availabilities = {
    "announced": "For Announced",
    "cinemas": "For In Cinemas",
    "released": "For Released",
    "db": "For PreDB"
}
sonarr_versions = {"v2": "For Sonarr 0.2", "v3": "For Sonarr 3.0"}
sonarr_monitors = {
    "all": "Monitor all episodes except specials",
    "future": "Monitor episodes that have not aired yet",
    "missing": "Monitor episodes that do not have files or have not aired yet",
    "existing": "Monitor episodes that have files or have not aired yet",
    "pilot": "Monitor the first episode. All other episodes will be ignored",
    "first": "Monitor all episodes of the first season. All other seasons will be ignored",
    "latest": "Monitor all episodes of the latest season and future seasons",
    "none": "No episodes will be monitored"
}
sonarr_series_types = {
    "standard": "Episodes released with SxxEyy pattern",
    "daily": "Episodes released daily or less frequently that use year-month-day (2017-05-25)",
    "anime": "Episodes released using an absolute episode number"
}
mass_genre_update_options = {"tmdb": "Use TMDb Metadata", "omdb": "Use IMDb Metadata through OMDb"}
library_types = {"movie": "For Movie Libraries", "show": "For Show Libraries"}

class Config:
    def __init__(self, default_dir, config_path=None, libraries_to_run=None):
        logger.info("Locating config...")
        if config_path and os.path.exists(config_path):                     self.config_path = os.path.abspath(config_path)
        elif config_path and not os.path.exists(config_path):               raise Failed(f"Config Error: config not found at {os.path.abspath(config_path)}")
        elif os.path.exists(os.path.join(default_dir, "config.yml")):       self.config_path = os.path.abspath(os.path.join(default_dir, "config.yml"))
        else:                                                               raise Failed(f"Config Error: config not found at {os.path.abspath(default_dir)}")
        logger.info(f"Using {self.config_path} as config")

        yaml.YAML().allow_duplicate_keys = True
        try:
            new_config, ind, bsi = yaml.util.load_yaml_guess_indent(open(self.config_path, encoding="utf-8"))
            def replace_attr(all_data, attr, par):
                if "settings" not in all_data:
                    all_data["settings"] = {}
                if par in all_data and all_data[par] and attr in all_data[par] and attr not in all_data["settings"]:
                    all_data["settings"][attr] = all_data[par][attr]
                    del all_data[par][attr]
            if "libraries" not in new_config:
                new_config["libraries"] = {}
            if "settings" not in new_config:
                new_config["settings"] = {}
            if "tmdb" not in new_config:
                new_config["tmdb"] = {}
            replace_attr(new_config, "cache", "cache")
            replace_attr(new_config, "cache_expiration", "cache")
            if "config" in new_config:
                del new_config["cache"]
            replace_attr(new_config, "asset_directory", "plex")
            replace_attr(new_config, "sync_mode", "plex")
            replace_attr(new_config, "show_unmanaged", "plex")
            replace_attr(new_config, "show_filtered", "plex")
            replace_attr(new_config, "show_missing", "plex")
            replace_attr(new_config, "save_missing", "plex")
            if new_config["libraries"]:
                for library in new_config["libraries"]:
                    if new_config["libraries"][library] and "plex" in new_config["libraries"][library]:
                        replace_attr(new_config["libraries"][library], "asset_directory", "plex")
                        replace_attr(new_config["libraries"][library], "sync_mode", "plex")
                        replace_attr(new_config["libraries"][library], "show_unmanaged", "plex")
                        replace_attr(new_config["libraries"][library], "show_filtered", "plex")
                        replace_attr(new_config["libraries"][library], "show_missing", "plex")
                        replace_attr(new_config["libraries"][library], "save_missing", "plex")
            if "libraries" in new_config:                   new_config["libraries"] = new_config.pop("libraries")
            if "settings" in new_config:                    new_config["settings"] = new_config.pop("settings")
            if "plex" in new_config:                        new_config["plex"] = new_config.pop("plex")
            if "tmdb" in new_config:                        new_config["tmdb"] = new_config.pop("tmdb")
            if "tautulli" in new_config:                    new_config["tautulli"] = new_config.pop("tautulli")
            if "radarr" in new_config:                      new_config["radarr"] = new_config.pop("radarr")
            if "sonarr" in new_config:                      new_config["sonarr"] = new_config.pop("sonarr")
            if "omdb" in new_config:                        new_config["omdb"] = new_config.pop("omdb")
            if "trakt" in new_config:                       new_config["trakt"] = new_config.pop("trakt")
            if "mal" in new_config:                         new_config["mal"] = new_config.pop("mal")
            yaml.round_trip_dump(new_config, open(self.config_path, "w", encoding="utf-8"), indent=ind, block_seq_indent=bsi)
            self.data = new_config
        except yaml.scanner.ScannerError as e:
            raise Failed(f"YAML Error: {util.tab_new_lines(e)}")
        except Exception as e:
            util.print_stacktrace()
            raise Failed(f"YAML Error: {e}")

        def check_for_attribute(data, attribute, parent=None, test_list=None, default=None, do_print=True, default_is_none=False, req_default=False, var_type="str", throw=False, save=True):
            endline = ""
            if parent is not None:
                if data and parent in data:
                    data = data[parent]
                else:
                    data = None
                    do_print = False
                    save = False
            text = f"{attribute} attribute" if parent is None else f"{parent} sub-attribute {attribute}"
            if data is None or attribute not in data:
                message = f"{text} not found"
                if parent and save is True:
                    loaded_config, ind_in, bsi_in = yaml.util.load_yaml_guess_indent(open(self.config_path))
                    endline = f"\n{parent} sub-attribute {attribute} added to config"
                    if parent not in loaded_config or not loaded_config[parent]:        loaded_config[parent] = {attribute: default}
                    elif attribute not in loaded_config[parent]:                        loaded_config[parent][attribute] = default
                    else:                                                               endline = ""
                    yaml.round_trip_dump(loaded_config, open(self.config_path, "w"), indent=ind_in, block_seq_indent=bsi_in)
            elif data[attribute] is None:
                if default_is_none is True:                                         return None
                else:                                                               message = f"{text} is blank"
            elif var_type == "bool":
                if isinstance(data[attribute], bool):                               return data[attribute]
                else:                                                               message = f"{text} must be either true or false"
            elif var_type == "int":
                if isinstance(data[attribute], int) and data[attribute] >= 0:       return data[attribute]
                else:                                                               message = f"{text} must an integer >= 0"
            elif var_type == "path":
                if os.path.exists(os.path.abspath(data[attribute])):                return data[attribute]
                else:                                                               message = f"Path {os.path.abspath(data[attribute])} does not exist"
            elif var_type == "list":                                            return util.get_list(data[attribute])
            elif var_type == "list_path":
                temp_list = [path for path in util.get_list(data[attribute], split=True) if os.path.exists(os.path.abspath(path))]
                if len(temp_list) > 0:                                              return temp_list
                else:                                                               message = "No Paths exist"
            elif var_type == "lower_list":                                      return util.get_list(data[attribute], lower=True)
            elif test_list is None or data[attribute] in test_list:             return data[attribute]
            else:                                                               message = f"{text}: {data[attribute]} is an invalid input"
            if var_type == "path" and default and os.path.exists(os.path.abspath(default)):
                return default
            elif var_type == "path" and default:
                if data and attribute in data and data[attribute]:
                    message = f"neither {data[attribute]} or the default path {default} could be found"
                else:
                    message = f"no {text} found and the default path {default} could not be found"
                default = None
            if default is not None or default_is_none:
                message = message + f" using {default} as default"
            message = message + endline
            if req_default and default is None:
                raise Failed(f"Config Error: {attribute} attribute must be set under {parent} globally or under this specific Library")
            options = ""
            if test_list:
                for option, description in test_list.items():
                    if len(options) > 0:
                        options = f"{options}\n"
                    options = f"{options}    {option} ({description})"
            if (default is None and not default_is_none) or throw:
                if len(options) > 0:
                    message = message + "\n" + options
                raise Failed(f"Config Error: {message}")
            if do_print:
                util.print_multiline(f"Config Warning: {message}")
                if attribute in data and data[attribute] and test_list is not None and data[attribute] not in test_list:
                    util.print_multiline(options)
            return default

        self.general = {}
        self.general["cache"] = check_for_attribute(self.data, "cache", parent="settings", var_type="bool", default=True)
        self.general["cache_expiration"] = check_for_attribute(self.data, "cache_expiration", parent="settings", var_type="int", default=60)
        if self.general["cache"]:
            util.separator()
            self.Cache = Cache(self.config_path, self.general["cache_expiration"])
        else:
            self.Cache = None
        self.general["asset_directory"] = check_for_attribute(self.data, "asset_directory", parent="settings", var_type="list_path", default=[os.path.join(default_dir, "assets")])
        self.general["asset_folders"] = check_for_attribute(self.data, "asset_folders", parent="settings", var_type="bool", default=True)
        self.general["assets_for_all"] = check_for_attribute(self.data, "assets_for_all", parent="settings", var_type="bool", default=False)
        self.general["sync_mode"] = check_for_attribute(self.data, "sync_mode", parent="settings", default="append", test_list=sync_modes)
        self.general["run_again_delay"] = check_for_attribute(self.data, "run_again_delay", parent="settings", var_type="int", default=0)
        self.general["show_unmanaged"] = check_for_attribute(self.data, "show_unmanaged", parent="settings", var_type="bool", default=True)
        self.general["show_filtered"] = check_for_attribute(self.data, "show_filtered", parent="settings", var_type="bool", default=False)
        self.general["show_missing"] = check_for_attribute(self.data, "show_missing", parent="settings", var_type="bool", default=True)
        self.general["save_missing"] = check_for_attribute(self.data, "save_missing", parent="settings", var_type="bool", default=True)

        util.separator()

        self.TMDb = None
        if "tmdb" in self.data:
            logger.info("Connecting to TMDb...")
            self.tmdb = {}
            try:                                self.tmdb["apikey"] = check_for_attribute(self.data, "apikey", parent="tmdb", throw=True)
            except Failed as e:                 raise Failed(e)
            self.tmdb["language"] = check_for_attribute(self.data, "language", parent="tmdb", default="en")
            self.TMDb = TMDbAPI(self.tmdb)
            logger.info(f"TMDb Connection {'Failed' if self.TMDb is None else 'Successful'}")
        else:
            raise Failed("Config Error: tmdb attribute not found")

        util.separator()

        self.OMDb = None
        if "omdb" in self.data:
            logger.info("Connecting to OMDb...")
            self.omdb = {}
            try:
                self.omdb["apikey"] = check_for_attribute(self.data, "apikey", parent="omdb", throw=True)
                self.OMDb = OMDbAPI(self.omdb, Cache=self.Cache)
            except Failed as e:
                logger.error(e)
            logger.info(f"OMDb Connection {'Failed' if self.OMDb is None else 'Successful'}")
        else:
            logger.warning("omdb attribute not found")

        util.separator()

        self.Trakt = None
        if "trakt" in self.data:
            logger.info("Connecting to Trakt...")
            self.trakt = {}
            try:
                self.trakt["client_id"] = check_for_attribute(self.data, "client_id", parent="trakt", throw=True)
                self.trakt["client_secret"] = check_for_attribute(self.data, "client_secret", parent="trakt", throw=True)
                self.trakt["config_path"] = self.config_path
                authorization = self.data["trakt"]["authorization"] if "authorization" in self.data["trakt"] and self.data["trakt"]["authorization"] else None
                self.Trakt = TraktAPI(self.trakt, authorization)
            except Failed as e:
                logger.error(e)
            logger.info(f"Trakt Connection {'Failed' if self.Trakt is None else 'Successful'}")
        else:
            logger.warning("trakt attribute not found")

        util.separator()

        self.MyAnimeList = None
        if "mal" in self.data:
            logger.info("Connecting to My Anime List...")
            self.mal = {}
            try:
                self.mal["client_id"] = check_for_attribute(self.data, "client_id", parent="mal", throw=True)
                self.mal["client_secret"] = check_for_attribute(self.data, "client_secret", parent="mal", throw=True)
                self.mal["config_path"] = self.config_path
                authorization = self.data["mal"]["authorization"] if "authorization" in self.data["mal"] and self.data["mal"]["authorization"] else None
                self.MyAnimeList = MyAnimeListAPI(self.mal, self, authorization)
            except Failed as e:
                logger.error(e)
            logger.info(f"My Anime List Connection {'Failed' if self.MyAnimeList is None else 'Successful'}")
        else:
            logger.warning("mal attribute not found")

        self.TVDb = TVDbAPI(self)
        self.IMDb = IMDbAPI(self)
        self.AniDB = AniDBAPI(self)
        self.Arms = ArmsAPI(self)
        self.AniDBIDs = self.AniDB.get_AniDB_IDs()
        self.AniList = AniListAPI(self)
        self.Letterboxd = LetterboxdAPI(self)

        util.separator()

        logger.info("Connecting to Plex Libraries...")

        self.general["plex"] = {}
        self.general["plex"]["url"] = check_for_attribute(self.data, "url", parent="plex", default_is_none=True)
        self.general["plex"]["token"] = check_for_attribute(self.data, "token", parent="plex", default_is_none=True)
        self.general["plex"]["timeout"] = check_for_attribute(self.data, "timeout", parent="plex", var_type="int", default=60)

        self.general["radarr"] = {}
        self.general["radarr"]["url"] = check_for_attribute(self.data, "url", parent="radarr", default_is_none=True)
        self.general["radarr"]["token"] = check_for_attribute(self.data, "token", parent="radarr", default_is_none=True)
        self.general["radarr"]["version"] = check_for_attribute(self.data, "version", parent="radarr", test_list=radarr_versions, default="v3")
        self.general["radarr"]["add"] = check_for_attribute(self.data, "add", parent="radarr", var_type="bool", default=False)
        self.general["radarr"]["root_folder_path"] = check_for_attribute(self.data, "root_folder_path", parent="radarr", default_is_none=True)
        self.general["radarr"]["monitor"] = check_for_attribute(self.data, "monitor", parent="radarr", var_type="bool", default=True)
        self.general["radarr"]["availability"] = check_for_attribute(self.data, "availability", parent="radarr", test_list=radarr_availabilities, default="announced")
        self.general["radarr"]["quality_profile"] = check_for_attribute(self.data, "quality_profile", parent="radarr", default_is_none=True)
        self.general["radarr"]["tag"] = check_for_attribute(self.data, "tag", parent="radarr", var_type="lower_list", default_is_none=True)
        self.general["radarr"]["search"] = check_for_attribute(self.data, "search", parent="radarr", var_type="bool", default=False)

        self.general["sonarr"] = {}
        self.general["sonarr"]["url"] = check_for_attribute(self.data, "url", parent="sonarr", default_is_none=True)
        self.general["sonarr"]["token"] = check_for_attribute(self.data, "token", parent="sonarr", default_is_none=True)
        self.general["sonarr"]["version"] = check_for_attribute(self.data, "version", parent="sonarr", test_list=sonarr_versions, default="v3")
        self.general["sonarr"]["add"] = check_for_attribute(self.data, "add", parent="sonarr", var_type="bool", default=False)
        self.general["sonarr"]["root_folder_path"] = check_for_attribute(self.data, "root_folder_path", parent="sonarr", default_is_none=True)
        self.general["sonarr"]["monitor"] = check_for_attribute(self.data, "monitor", parent="sonarr", test_list=sonarr_monitors, default="all")
        self.general["sonarr"]["quality_profile"] = check_for_attribute(self.data, "quality_profile", parent="sonarr", default_is_none=True)
        self.general["sonarr"]["language_profile"] = check_for_attribute(self.data, "language_profile", parent="sonarr", default_is_none=True)
        self.general["sonarr"]["series_type"] = check_for_attribute(self.data, "series_type", parent="sonarr", test_list=sonarr_series_types, default="standard")
        self.general["sonarr"]["season_folder"] = check_for_attribute(self.data, "season_folder", parent="sonarr", var_type="bool", default=True)
        self.general["sonarr"]["tag"] = check_for_attribute(self.data, "tag", parent="sonarr", var_type="lower_list", default_is_none=True)
        self.general["sonarr"]["search"] = check_for_attribute(self.data, "search", parent="sonarr", var_type="bool", default=False)
        self.general["sonarr"]["cutoff_search"] = check_for_attribute(self.data, "cutoff_search", parent="sonarr", var_type="bool", default=False)

        self.general["tautulli"] = {}
        self.general["tautulli"]["url"] = check_for_attribute(self.data, "url", parent="tautulli", default_is_none=True)
        self.general["tautulli"]["apikey"] = check_for_attribute(self.data, "apikey", parent="tautulli", default_is_none=True)

        self.libraries = []
        try:                            libs = check_for_attribute(self.data, "libraries", throw=True)
        except Failed as e:             raise Failed(e)
        requested_libraries = util.get_list(libraries_to_run) if libraries_to_run else None
        for library_name, lib in libs.items():
            if requested_libraries and library_name not in requested_libraries:
                continue
            util.separator()
            params = {}
            logger.info("")
            if lib and "library_name" in lib and lib["library_name"]:
                params["name"] = str(lib["library_name"])
                logger.info(f"Connecting to {params['name']} ({library_name}) Library...")
            else:
                params["name"] = str(library_name)
                logger.info(f"Connecting to {params['name']} Library...")

            params["asset_directory"] = check_for_attribute(lib, "asset_directory", parent="settings", var_type="list_path", default=self.general["asset_directory"], default_is_none=True, save=False)
            if params["asset_directory"] is None:
                logger.warning("Config Warning: Assets will not be used asset_directory attribute must be set under config or under this specific Library")

            if lib and "settings" in lib and lib["settings"] and "asset_folders" in lib["settings"]:
                params["asset_folders"] = check_for_attribute(lib, "asset_folders", parent="settings", var_type="bool", default=self.general["asset_folders"], do_print=False, save=False)
            else:
                params["asset_folders"] = check_for_attribute(lib, "asset_folders", var_type="bool", default=self.general["asset_folders"], do_print=False, save=False)

            if lib and "settings" in lib and lib["settings"] and "assets_for_all" in lib["settings"]:
                params["assets_for_all"] = check_for_attribute(lib, "assets_for_all", parent="settings", var_type="bool", default=self.general["assets_for_all"], do_print=False, save=False)
            else:
                params["assets_for_all"] = check_for_attribute(lib, "assets_for_all", var_type="bool", default=self.general["assets_for_all"], do_print=False, save=False)

            if lib and "settings" in lib and lib["settings"] and "sync_mode" in lib["settings"]:
                params["sync_mode"] = check_for_attribute(lib, "sync_mode", parent="settings", test_list=sync_modes, default=self.general["sync_mode"], do_print=False, save=False)
            else:
                params["sync_mode"] = check_for_attribute(lib, "sync_mode", test_list=sync_modes, default=self.general["sync_mode"], do_print=False, save=False)

            if lib and "settings" in lib and lib["settings"] and "show_unmanaged" in lib["settings"]:
                params["show_unmanaged"] = check_for_attribute(lib, "show_unmanaged", parent="settings", var_type="bool", default=self.general["show_unmanaged"], do_print=False, save=False)
            else:
                params["show_unmanaged"] = check_for_attribute(lib, "show_unmanaged", var_type="bool", default=self.general["show_unmanaged"], do_print=False, save=False)

            if lib and "settings" in lib and lib["settings"] and "show_filtered" in lib["settings"]:
                params["show_filtered"] = check_for_attribute(lib, "show_filtered", parent="settings", var_type="bool", default=self.general["show_filtered"], do_print=False, save=False)
            else:
                params["show_filtered"] = check_for_attribute(lib, "show_filtered", var_type="bool", default=self.general["show_filtered"], do_print=False, save=False)

            if lib and "settings" in lib and lib["settings"] and "show_missing" in lib["settings"]:
                params["show_missing"] = check_for_attribute(lib, "show_missing", parent="settings", var_type="bool", default=self.general["show_missing"], do_print=False, save=False)
            else:
                params["show_missing"] = check_for_attribute(lib, "show_missing", var_type="bool", default=self.general["show_missing"], do_print=False, save=False)

            if lib and "settings" in lib and lib["settings"] and "save_missing" in lib["settings"]:
                params["save_missing"] = check_for_attribute(lib, "save_missing", parent="settings", var_type="bool", default=self.general["save_missing"], do_print=False, save=False)
            else:
                params["save_missing"] = check_for_attribute(lib, "save_missing", var_type="bool", default=self.general["save_missing"], do_print=False, save=False)

            if lib and "mass_genre_update" in lib and lib["mass_genre_update"]:
                params["mass_genre_update"] = check_for_attribute(lib, "mass_genre_update", test_list=mass_genre_update_options, default_is_none=True, save=False)
            else:
                params["mass_genre_update"] = None

            if params["mass_genre_update"] == "omdb" and self.OMDb is None:
                params["mass_genre_update"] = None
                logger.error("Config Error: mass_genre_update cannot be omdb without a successful OMDb Connection")

            try:
                params["metadata_path"] = check_for_attribute(lib, "metadata_path", var_type="path", default=os.path.join(default_dir, f"{library_name}.yml"), throw=True)
                params["plex"] = {}
                params["plex"]["url"] = check_for_attribute(lib, "url", parent="plex", default=self.general["plex"]["url"], req_default=True, save=False)
                params["plex"]["token"] = check_for_attribute(lib, "token", parent="plex", default=self.general["plex"]["token"], req_default=True, save=False)
                params["plex"]["timeout"] = check_for_attribute(lib, "timeout", parent="plex", var_type="int", default=self.general["plex"]["timeout"], save=False)
                library = PlexAPI(params, self.TMDb, self.TVDb)
                logger.info(f"{params['name']} Library Connection Successful")
            except Failed as e:
                util.print_multiline(e, error=True)
                logger.info(f"{params['name']} Library Connection Failed")
                continue

            if self.general["radarr"]["url"] or (lib and "radarr" in lib):
                logger.info("")
                logger.info(f"Connecting to {params['name']} library's Radarr...")
                radarr_params = {}
                try:
                    radarr_params["url"] = check_for_attribute(lib, "url", parent="radarr", default=self.general["radarr"]["url"], req_default=True, save=False)
                    radarr_params["token"] = check_for_attribute(lib, "token", parent="radarr", default=self.general["radarr"]["token"], req_default=True, save=False)
                    radarr_params["version"] = check_for_attribute(lib, "version", parent="radarr", test_list=radarr_versions, default=self.general["radarr"]["version"], save=False)
                    radarr_params["add"] = check_for_attribute(lib, "add", parent="radarr", var_type="bool", default=self.general["radarr"]["add"], save=False)
                    radarr_params["root_folder_path"] = check_for_attribute(lib, "root_folder_path", parent="radarr", default=self.general["radarr"]["root_folder_path"], req_default=True, save=False)
                    radarr_params["monitor"] = check_for_attribute(lib, "monitor", parent="radarr", var_type="bool", default=self.general["radarr"]["monitor"], save=False)
                    radarr_params["availability"] = check_for_attribute(lib, "availability", parent="radarr", test_list=radarr_availabilities, default=self.general["radarr"]["availability"], save=False)
                    radarr_params["quality_profile"] = check_for_attribute(lib, "quality_profile", parent="radarr", default=self.general["radarr"]["quality_profile"], req_default=True, save=False)
                    radarr_params["tag"] = check_for_attribute(lib, "search", parent="radarr", var_type="lower_list", default=self.general["radarr"]["tag"], default_is_none=True, save=False)
                    radarr_params["search"] = check_for_attribute(lib, "search", parent="radarr", var_type="bool", default=self.general["radarr"]["search"], save=False)
                    library.Radarr = RadarrAPI(radarr_params)
                except Failed as e:
                    util.print_multiline(e, error=True)
                logger.info(f"{params['name']} library's Radarr Connection {'Failed' if library.Radarr is None else 'Successful'}")

            if self.general["sonarr"]["url"] or (lib and "sonarr" in lib):
                logger.info("")
                logger.info(f"Connecting to {params['name']} library's Sonarr...")
                sonarr_params = {}
                try:
                    sonarr_params["url"] = check_for_attribute(lib, "url", parent="sonarr", default=self.general["sonarr"]["url"], req_default=True, save=False)
                    sonarr_params["token"] = check_for_attribute(lib, "token", parent="sonarr", default=self.general["sonarr"]["token"], req_default=True, save=False)
                    sonarr_params["version"] = check_for_attribute(lib, "version", parent="sonarr", test_list=sonarr_versions, default=self.general["sonarr"]["version"], save=False)
                    sonarr_params["add"] = check_for_attribute(lib, "add", parent="sonarr", var_type="bool", default=self.general["sonarr"]["add"], save=False)
                    sonarr_params["root_folder_path"] = check_for_attribute(lib, "root_folder_path", parent="sonarr", default=self.general["sonarr"]["root_folder_path"], req_default=True, save=False)
                    sonarr_params["monitor"] = check_for_attribute(lib, "monitor", parent="sonarr", test_list=sonarr_monitors, default=self.general["sonarr"]["monitor"], save=False)
                    sonarr_params["quality_profile"] = check_for_attribute(lib, "quality_profile", parent="sonarr", default=self.general["sonarr"]["quality_profile"], req_default=True, save=False)
                    if self.general["sonarr"]["language_profile"]:
                        sonarr_params["language_profile"] = check_for_attribute(lib, "language_profile", parent="sonarr", default=self.general["sonarr"]["language_profile"], save=False)
                    else:
                        sonarr_params["language_profile"] = check_for_attribute(lib, "language_profile", parent="sonarr", default_is_none=True, save=False)
                    sonarr_params["series_type"] = check_for_attribute(lib, "series_type", parent="sonarr", test_list=sonarr_series_types, default=self.general["sonarr"]["series_type"], save=False)
                    sonarr_params["season_folder"] = check_for_attribute(lib, "season_folder", parent="sonarr", var_type="bool", default=self.general["sonarr"]["season_folder"], save=False)
                    sonarr_params["tag"] = check_for_attribute(lib, "search", parent="sonarr", var_type="lower_list", default=self.general["sonarr"]["tag"], default_is_none=True, save=False)
                    sonarr_params["search"] = check_for_attribute(lib, "search", parent="sonarr", var_type="bool", default=self.general["sonarr"]["search"], save=False)
                    sonarr_params["cutoff_search"] = check_for_attribute(lib, "cutoff_search", parent="sonarr", var_type="bool", default=self.general["sonarr"]["cutoff_search"], save=False)
                    library.Sonarr = SonarrAPI(sonarr_params, library.Plex.language)
                except Failed as e:
                    util.print_multiline(e, error=True)
                logger.info(f"{params['name']} library's Sonarr Connection {'Failed' if library.Sonarr is None else 'Successful'}")

            if self.general["tautulli"]["url"] or (lib and "tautulli" in lib):
                logger.info("")
                logger.info(f"Connecting to {params['name']} library's Tautulli...")
                tautulli_params = {}
                try:
                    tautulli_params["url"] = check_for_attribute(lib, "url", parent="tautulli", default=self.general["tautulli"]["url"], req_default=True, save=False)
                    tautulli_params["apikey"] = check_for_attribute(lib, "apikey", parent="tautulli", default=self.general["tautulli"]["apikey"], req_default=True, save=False)
                    library.Tautulli = TautulliAPI(tautulli_params)
                except Failed as e:
                    util.print_multiline(e, error=True)
                logger.info(f"{params['name']} library's Tautulli Connection {'Failed' if library.Tautulli is None else 'Successful'}")

            logger.info("")
            self.libraries.append(library)

        util.separator()

        if len(self.libraries) > 0:
            logger.info(f"{len(self.libraries)} Plex Library Connection{'s' if len(self.libraries) > 1 else ''} Successful")
        else:
            raise Failed("Plex Error: No Plex libraries were connected to")

        util.separator()

    def update_libraries(self, test, requested_collections, resume_from):
        for library in self.libraries:
            os.environ["PLEXAPI_PLEXAPI_TIMEOUT"] = str(library.timeout)
            logger.info("")
            util.separator(f"{library.name} Library")
            logger.info("")
            util.separator(f"Mapping {library.name} Library")
            logger.info("")
            movie_map, show_map = self.map_guids(library)
            if not test and not resume_from:
                if library.mass_genre_update:
                    self.mass_metadata(library, movie_map, show_map)
                try:                        library.update_metadata(self.TMDb, test)
                except Failed as e:         logger.error(e)
            logger.info("")
            util.separator(f"{library.name} Library {'Test ' if test else ''}Collections")
            collections = {c: library.collections[c] for c in util.get_list(requested_collections) if c in library.collections} if requested_collections else library.collections
            if resume_from and resume_from not in collections:
                logger.warning(f"Collection: {resume_from} not in {library.name}")
                continue
            if collections:
                for mapping_name, collection_attrs in collections.items():
                    if test and ("test" not in collection_attrs or collection_attrs["test"] is not True):
                        no_template_test = True
                        if "template" in collection_attrs and collection_attrs["template"]:
                            for data_template in util.get_list(collection_attrs["template"], split=False):
                                if "name" in data_template \
                                    and data_template["name"] \
                                    and library.templates \
                                    and data_template["name"] in library.templates \
                                    and library.templates[data_template["name"]] \
                                    and "test" in library.templates[data_template["name"]] \
                                    and library.templates[data_template["name"]]["test"] is True:
                                    no_template_test = False
                        if no_template_test:
                            continue
                    try:
                        if resume_from and resume_from != mapping_name:
                            continue
                        elif resume_from == mapping_name:
                            resume_from = None
                            logger.info("")
                            util.separator(f"Resuming Collections")

                        logger.info("")
                        util.separator(f"{mapping_name} Collection")
                        logger.info("")

                        rating_key_map = {}
                        try:
                            builder = CollectionBuilder(self, library, mapping_name, collection_attrs)
                        except Failed as ef:
                            util.print_multiline(ef, error=True)
                            continue
                        except Exception as ee:
                            util.print_stacktrace()
                            logger.error(ee)
                            continue

                        try:
                            collection_obj = library.get_collection(mapping_name)
                            collection_name = collection_obj.title
                        except Failed:
                            collection_obj = None
                            collection_name = mapping_name

                        if len(builder.schedule) > 0:
                            util.print_multiline(builder.schedule, info=True)

                        logger.info("")
                        if builder.sync:
                            logger.info("Sync Mode: sync")
                            if collection_obj:
                                for item in collection_obj.items():
                                    rating_key_map[item.ratingKey] = item
                        else:
                            logger.info("Sync Mode: append")

                        for i, f in enumerate(builder.filters):
                            if i == 0:
                                logger.info("")
                            logger.info(f"Collection Filter {f[0]}: {f[1]}")

                        builder.run_methods(collection_obj, collection_name, rating_key_map, movie_map, show_map)

                        try:
                            plex_collection = library.get_collection(collection_name)
                        except Failed as e:
                            logger.debug(e)
                            continue

                        builder.update_details(plex_collection)

                        if builder.run_again and (len(builder.missing_movies) > 0 or len(builder.missing_shows) > 0):
                            library.run_again.append(builder)

                    except Exception as e:
                        util.print_stacktrace()
                        logger.error(f"Unknown Error: {e}")

                if library.assets_for_all is True and not test and not requested_collections:
                    logger.info("")
                    util.separator(f"All {'Movies' if library.is_movie else 'Shows'} Assets Check for {library.name} Library")
                    logger.info("")
                    for item in library.get_all():
                        folder = os.path.basename(os.path.dirname(item.locations[0]) if library.is_movie else item.locations[0])
                        for ad in library.asset_directory:
                            if library.asset_folders:
                                poster_path = os.path.join(ad, folder, "poster.*")
                            else:
                                poster_path = os.path.join(ad, f"{folder}.*")
                            matches = glob.glob(poster_path)
                            if len(matches) > 0:
                                item.uploadPoster(filepath=os.path.abspath(matches[0]))
                                logger.info(f"Detail: asset_directory updated {item.title}'s poster to [file] {os.path.abspath(matches[0])}")
                            if library.asset_folders:
                                matches = glob.glob(os.path.join(ad, folder, "background.*"))
                                if len(matches) > 0:
                                    item.uploadArt(filepath=os.path.abspath(matches[0]))
                                    logger.info(f"Detail: asset_directory updated {item.title}'s background to [file] {os.path.abspath(matches[0])}")
                                if library.is_show:
                                    for season in item.seasons():
                                        matches = glob.glob(os.path.join(ad, folder, f"Season{'0' if season.seasonNumber < 10 else ''}{season.seasonNumber}.*"))
                                        if len(matches) > 0:
                                            season_path = os.path.abspath(matches[0])
                                            season.uploadPoster(filepath=season_path)
                                            logger.info(f"Detail: asset_directory updated {item.title} Season {season.seasonNumber}'s poster to [file] {season_path}")
                                        for episode in season.episodes():
                                            matches = glob.glob(os.path.join(ad, folder, f"{episode.seasonEpisode.upper()}.*"))
                                            if len(matches) > 0:
                                                episode_path = os.path.abspath(matches[0])
                                                episode.uploadPoster(filepath=episode_path)
                                                logger.info(f"Detail: asset_directory updated {item.title} {episode.seasonEpisode.upper()}'s poster to [file] {episode_path}")

                if library.show_unmanaged is True and not test and not requested_collections:
                    logger.info("")
                    util.separator(f"Unmanaged Collections in {library.name} Library")
                    logger.info("")
                    unmanaged_count = 0
                    collections_in_plex = [str(plex_col) for plex_col in collections]
                    for col in library.get_all_collections():
                        if col.title not in collections_in_plex:
                            logger.info(col.title)
                            unmanaged_count += 1
                    logger.info("{} Unmanaged Collections".format(unmanaged_count))
            else:
                logger.info("")
                logger.error("No collection to update")

        has_run_again = False
        for library in self.libraries:
            if library.run_again:
                has_run_again = True
                break

        if has_run_again:
            logger.info("")
            util.separator("Run Again")
            logger.info("")
            length = 0
            for x in range(1, self.general["run_again_delay"] + 1):
                length = util.print_return(length, f"Waiting to run again in {self.general['run_again_delay'] - x + 1} minutes")
                for y in range(60):
                    time.sleep(1)
            util.print_end(length)
            for library in self.libraries:
                if library.run_again:
                    os.environ["PLEXAPI_PLEXAPI_TIMEOUT"] = str(library.timeout)
                    logger.info("")
                    util.separator(f"{library.name} Library Run Again")
                    logger.info("")
                    collections = {c: library.collections[c] for c in util.get_list(requested_collections) if c in library.collections} if requested_collections else library.collections
                    if collections:
                        util.separator(f"Mapping {library.name} Library")
                        logger.info("")
                        movie_map, show_map = self.map_guids(library)
                        for builder in library.run_again:
                            logger.info("")
                            util.separator(f"{builder.name} Collection")
                            logger.info("")
                            try:
                                collection_obj = library.get_collection(builder.name)
                            except Failed as e:
                                util.print_multiline(e, error=True)
                                continue
                            builder.run_collections_again(collection_obj, movie_map, show_map)

    def mass_metadata(self, library, movie_map, show_map):
        length = 0
        logger.info("")
        util.separator(f"Mass Editing {'Movie' if library.is_movie else 'Show'} Library: {library.name}")
        logger.info("")
        items = library.Plex.all()
        for i, item in enumerate(items, 1):
            length = util.print_return(length, f"Processing: {i}/{len(items)} {item.title}")
            ids = {}
            if self.Cache:
                ids, expired = self.Cache.get_ids("movie" if library.is_movie else "show", plex_guid=item.guid)
            elif library.is_movie:
                for tmdb, rating_keys in movie_map.items():
                    if item.ratingKey in rating_keys:
                        ids["tmdb"] = tmdb
                        break
            else:
                for tvdb, rating_keys in show_map.items():
                    if item.ratingKey in rating_keys:
                        ids["tvdb"] = tvdb
                        break

            if library.mass_genre_update:
                if library.mass_genre_update == "tmdb":
                    if "tmdb" not in ids:
                        util.print_end(length, f"{item.title[:25]:<25} | No TMDb for Guid: {item.guid}")
                        continue
                    try:
                        tmdb_item = self.TMDb.get_movie(ids["tmdb"]) if library.is_movie else self.TMDb.get_show(ids["tmdb"])
                    except Failed as e:
                        util.print_end(length, str(e))
                        continue
                    new_genres = [genre.name for genre in tmdb_item.genres]
                elif library.mass_genre_update in ["omdb", "imdb"]:
                    if self.OMDb.limit is True:
                        break
                    if "imdb" not in ids:
                        util.print_end(length, f"{item.title[:25]:<25} | No IMDb for Guid: {item.guid}")
                        continue
                    try:
                        omdb_item = self.OMDb.get_omdb(ids["imdb"])
                    except Failed as e:
                        util.print_end(length, str(e))
                        continue
                    new_genres = omdb_item.genres
                else:
                    raise Failed
                item_genres = [genre.tag for genre in item.genres]
                display_str = ""
                for genre in (g for g in item_genres if g not in new_genres):
                    item.removeGenre(genre)
                    display_str += f"{', ' if len(display_str) > 0 else ''}-{genre}"
                for genre in (g for g in new_genres if g not in item_genres):
                    item.addGenre(genre)
                    display_str += f"{', ' if len(display_str) > 0 else ''}+{genre}"
                if len(display_str) > 0:
                    util.print_end(length, f"{item.title[:25]:<25} | Genres | {display_str}")

    def map_guids(self, library):
        movie_map = {}
        show_map = {}
        length = 0
        logger.info(f"Mapping {'Movie' if library.is_movie else 'Show'} Library: {library.name}")
        items = library.Plex.all()
        for i, item in enumerate(items, 1):
            length = util.print_return(length, f"Processing: {i}/{len(items)} {item.title}")
            try:
                id_type, main_id = self.get_id(item, library, length)
            except BadRequest:
                util.print_stacktrace()
                util.print_end(length, f"{'Cache | ! |' if self.Cache else 'Mapping Error:'} | {item.guid} for {item.title} not found")
                continue
            if isinstance(main_id, list):
                if id_type == "movie":
                    for m in main_id:
                        if m in movie_map:
                            movie_map[m].append(item.ratingKey)
                        else:
                            movie_map[m] = [item.ratingKey]
                elif id_type == "show":
                    for m in main_id:
                        if m in show_map:
                            show_map[m].append(item.ratingKey)
                        else:
                            show_map[m] = [item.ratingKey]
            else:
                if id_type == "movie":
                    if main_id in movie_map:
                        movie_map[main_id].append(item.ratingKey)
                    else:
                        movie_map[main_id] = [item.ratingKey]
                elif id_type == "show":
                    if main_id in show_map:
                        show_map[main_id].append(item.ratingKey)
                    else:
                        show_map[main_id] = [item.ratingKey]
        util.print_end(length, f"Processed {len(items)} {'Movies' if library.is_movie else 'Shows'}")
        return movie_map, show_map

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def get_guids(self, item):
        return item.guids

    def get_id(self, item, library, length):
        expired = None
        tmdb_id = None
        imdb_id = None
        tvdb_id = None
        anidb_id = None
        mal_id = None
        error_message = None
        if self.Cache:
            if library.is_movie:                            tmdb_id, expired = self.Cache.get_tmdb_id("movie", plex_guid=item.guid)
            else:                                           tvdb_id, expired = self.Cache.get_tvdb_id("show", plex_guid=item.guid)
            if not tvdb_id and library.is_show:
                tmdb_id, expired = self.Cache.get_tmdb_id("show", plex_guid=item.guid)
                anidb_id, expired = self.Cache.get_anidb_id("show", plex_guid=item.guid)
        if expired or (not tmdb_id and library.is_movie) or (not tvdb_id and not tmdb_id and library.is_show):
            guid = requests.utils.urlparse(item.guid)
            item_type = guid.scheme.split(".")[-1]
            check_id = guid.netloc

            if item_type == "plex":
                tmdb_id = []
                imdb_id = []
                tvdb_id = []
                if check_id == "movie":
                    try:
                        for guid_tag in self.get_guids(item):
                            url_parsed = requests.utils.urlparse(guid_tag.id)
                            if url_parsed.scheme == "tmdb":                 tmdb_id.append(int(url_parsed.netloc))
                            elif url_parsed.scheme == "imdb":               imdb_id.append(url_parsed.netloc)
                    except requests.exceptions.ConnectionError:
                        util.print_stacktrace()
                        logger.error(f"{'Cache | ! |' if self.Cache else 'Mapping Error:'} {item.guid:<46} | No External GUIDs found for {item.title}")
                        return None, None
                elif check_id == "show":
                    try:
                        for guid_tag in self.get_guids(item):
                            url_parsed = requests.utils.urlparse(guid_tag.id)
                            if url_parsed.scheme == "tvdb":                 tvdb_id.append(int(url_parsed.netloc))
                            elif url_parsed.scheme == "imdb":               imdb_id.append(url_parsed.netloc)
                            elif url_parsed.scheme == "tmdb":               tmdb_id.append(int(url_parsed.netloc))
                    except requests.exceptions.ConnectionError:
                        util.print_stacktrace()
                        logger.error(f"{'Cache | ! |' if self.Cache else 'Mapping Error:'} {item.guid:<46} | No External GUIDs found for {item.title}")
                        return None, None
            elif item_type == "imdb":                       imdb_id = check_id
            elif item_type == "thetvdb":                    tvdb_id = int(check_id)
            elif item_type == "themoviedb":                 tmdb_id = int(check_id)
            elif item_type == "hama":
                if check_id.startswith("tvdb"):             tvdb_id = int(re.search("-(.*)", check_id).group(1))
                elif check_id.startswith("anidb"):          anidb_id = re.search("-(.*)", check_id).group(1)
                else:                                       error_message = f"Hama Agent ID: {check_id} not supported"
            elif item_type == "myanimelist":                mal_id = check_id
            elif item_type == "local":                      error_message = "No match in Plex"
            else:                                           error_message = f"Agent {item_type} not supported"

            if not error_message:
                if mal_id and not anidb_id:
                    try:                                            anidb_id = self.Arms.mal_to_anidb(mal_id)
                    except Failed:                                  pass
                if anidb_id and not tvdb_id:
                    try:                                            tvdb_id = self.Arms.anidb_to_tvdb(anidb_id)
                    except Failed:                                  pass
                if anidb_id and not imdb_id:
                    try:                                            imdb_id = self.Arms.anidb_to_imdb(anidb_id)
                    except Failed:                                  pass
                if not tmdb_id and imdb_id:
                    if isinstance(imdb_id, list):
                        tmdb_id = []
                        new_imdb_id = []
                        for imdb in imdb_id:
                            try:
                                tmdb_id.append(self.TMDb.convert_imdb_to_tmdb(imdb))
                                new_imdb_id.append(imdb)
                            except Failed:
                                if self.Trakt:
                                    try:
                                        tmdb_id.append(self.Trakt.convert_imdb_to_tmdb(imdb))
                                        new_imdb_id.append(imdb)
                                    except Failed:
                                        continue
                                else:
                                    continue
                        imdb_id = new_imdb_id
                    else:
                        try:                                            tmdb_id = self.TMDb.convert_imdb_to_tmdb(imdb_id)
                        except Failed:                                  pass
                        if not tmdb_id and self.Trakt:
                            try:                                            tmdb_id = self.Trakt.convert_imdb_to_tmdb(imdb_id)
                            except Failed:                                  pass
                if not tmdb_id and tvdb_id and library.is_show:
                    try:                                            tmdb_id = self.TMDb.convert_tvdb_to_tmdb(tvdb_id)
                    except Failed:                                  pass
                    if not tmdb_id and self.Trakt:
                        try:                                            tmdb_id = self.Trakt.convert_tvdb_to_tmdb(tvdb_id)
                        except Failed:                                  pass
                if not imdb_id and tmdb_id and library.is_movie:
                    try:                                            imdb_id = self.TMDb.convert_tmdb_to_imdb(tmdb_id)
                    except Failed:                                  pass
                    if not imdb_id and self.Trakt:
                        try:                                            imdb_id = self.Trakt.convert_tmdb_to_imdb(tmdb_id)
                        except Failed:                                  pass
                if not imdb_id and tvdb_id and library.is_show:
                    try:                                            imdb_id = self.TMDb.convert_tvdb_to_imdb(tvdb_id)
                    except Failed:                                  pass
                    if not imdb_id and self.Trakt:
                        try:                                            imdb_id = self.Trakt.convert_tvdb_to_imdb(tvdb_id)
                        except Failed:                                  pass
                if not tvdb_id and library.is_show:
                    if tmdb_id:
                        try:                                            tvdb_id = self.TMDb.convert_tmdb_to_tvdb(tmdb_id)
                        except Failed:                                  pass
                        if not tvdb_id and self.Trakt:
                            try:                                            tvdb_id = self.Trakt.convert_tmdb_to_tvdb(tmdb_id)
                            except Failed:                                  pass
                    if not tvdb_id and imdb_id:
                        try:                                            tvdb_id = self.TMDb.convert_imdb_to_tvdb(imdb_id)
                        except Failed:                                  pass
                        if not tvdb_id and self.Trakt:
                            try:                                            tvdb_id = self.Trakt.convert_imdb_to_tvdb(tmdb_id)
                            except Failed:                                  pass

                if (not tmdb_id and library.is_movie) or (not tvdb_id and not (anidb_id and tmdb_id) and library.is_show):
                    service_name = "TMDb ID" if library.is_movie else "TVDb ID"

                    if self.Trakt:                                  api_name = "TMDb or Trakt"
                    else:                                           api_name = "TMDb"

                    if tmdb_id and imdb_id:                         id_name = f"TMDb ID: {tmdb_id} or IMDb ID: {imdb_id}"
                    elif imdb_id and tvdb_id:                       id_name = f"IMDb ID: {imdb_id} or TVDb ID: {tvdb_id}"
                    elif tmdb_id:                                   id_name = f"TMDb ID: {tmdb_id}"
                    elif imdb_id:                                   id_name = f"IMDb ID: {imdb_id}"
                    elif tvdb_id:                                   id_name = f"TVDb ID: {tvdb_id}"
                    else:                                           id_name = None

                    if anidb_id and not tmdb_id and not tvdb_id:    error_message = f"Unable to convert AniDB ID: {anidb_id} to TMDb ID or TVDb ID"
                    elif id_name:                                   error_message = f"Unable to convert {id_name} to {service_name} using {api_name}"
                    else:                                           error_message = f"No ID to convert to {service_name}"
            if self.Cache and ((tmdb_id and library.is_movie) or ((tvdb_id or (anidb_id and tmdb_id)) and library.is_show)):
                if not isinstance(tmdb_id, list):               tmdb_id = [tmdb_id]
                if not isinstance(imdb_id, list):               imdb_id = [imdb_id]
                for i in range(len(tmdb_id)):
                    try:                                            imdb_value = imdb_id[i]
                    except IndexError:                              imdb_value = None
                    util.print_end(length, f"Cache | {'^' if expired is True else '+'} | {item.guid:<46} | {tmdb_id[i] if tmdb_id[i] else 'None':<6} | {imdb_value if imdb_value else 'None':<10} | {tvdb_id if tvdb_id else 'None':<6} | {anidb_id if anidb_id else 'None':<5} | {item.title}")
                    self.Cache.update_guid("movie" if library.is_movie else "show", item.guid, tmdb_id[i], imdb_value, tvdb_id, anidb_id, expired)

        if tmdb_id and library.is_movie:                return "movie", tmdb_id
        elif tvdb_id and library.is_show:               return "show", tvdb_id
        elif anidb_id and tmdb_id:                      return "movie", tmdb_id
        else:
            util.print_end(length, f"{'Cache | ! |' if self.Cache else 'Mapping Error:'} {item.guid:<46} | {error_message} for {item.title}")
            return None, None
