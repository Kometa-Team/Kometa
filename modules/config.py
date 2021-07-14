import logging, os, requests
from datetime import datetime
from lxml import html
from modules import util
from modules.anidb import AniDB
from modules.anilist import AniList
from modules.cache import Cache
from modules.convert import Convert
from modules.icheckmovies import ICheckMovies
from modules.imdb import IMDb
from modules.letterboxd import Letterboxd
from modules.mal import MyAnimeList
from modules.omdb import OMDb
from modules.plex import Plex
from modules.radarr import Radarr
from modules.sonarr import Sonarr
from modules.tautulli import Tautulli
from modules.tmdb import TMDb
from modules.trakttv import Trakt
from modules.tvdb import TVDb
from modules.util import Failed
from retrying import retry
from ruamel import yaml

logger = logging.getLogger("Plex Meta Manager")

sync_modes = {"append": "Only Add Items to the Collection", "sync": "Add & Remove Items from the Collection"}
radarr_availabilities = {
    "announced": "For Announced",
    "cinemas": "For In Cinemas",
    "released": "For Released",
    "db": "For PreDB"
}
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
mass_update_options = {"tmdb": "Use TMDb Metadata", "omdb": "Use IMDb Metadata through OMDb"}
library_types = {"movie": "For Movie Libraries", "show": "For Show Libraries"}

class Config:
    def __init__(self, default_dir, config_path=None, is_test=False, time_scheduled=None, requested_collections=None, requested_libraries=None, resume_from=None):
        logger.info("Locating config...")
        if config_path and os.path.exists(config_path):                     self.config_path = os.path.abspath(config_path)
        elif config_path and not os.path.exists(config_path):               raise Failed(f"Config Error: config not found at {os.path.abspath(config_path)}")
        elif os.path.exists(os.path.join(default_dir, "config.yml")):       self.config_path = os.path.abspath(os.path.join(default_dir, "config.yml"))
        else:                                                               raise Failed(f"Config Error: config not found at {os.path.abspath(default_dir)}")
        logger.info(f"Using {self.config_path} as config")

        self.default_dir = default_dir
        self.test_mode = is_test
        self.run_start_time = time_scheduled
        self.run_hour = datetime.strptime(time_scheduled, "%H:%M").hour
        self.requested_collections = util.get_list(requested_collections)
        self.requested_libraries = util.get_list(requested_libraries)
        self.resume_from = resume_from

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
            if "anidb" in new_config:                       new_config["anidb"] = new_config.pop("anidb")
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
            elif var_type == "url":
                if data[attribute].endswith(("\\", "/")):                           return data[attribute][:-1]
                else:                                                               return data[attribute]
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
                temp_list = [p for p in util.get_list(data[attribute], split=True) if os.path.exists(os.path.abspath(p))]
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

        self.session = requests.Session()

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
            self.TMDb = TMDb(self, self.tmdb)
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
                self.OMDb = OMDb(self, self.omdb)
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
                self.Trakt = Trakt(self, self.trakt, authorization)
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
                self.MyAnimeList = MyAnimeList(self, self.mal, authorization)
            except Failed as e:
                logger.error(e)
            logger.info(f"My Anime List Connection {'Failed' if self.MyAnimeList is None else 'Successful'}")
        else:
            logger.warning("mal attribute not found")

        util.separator()

        self.AniDB = None
        if "anidb" in self.data:
            util.separator()
            logger.info("Connecting to AniDB...")
            self.anidb = {}
            try:
                self.anidb["username"] = check_for_attribute(self.data, "username", parent="anidb", throw=True)
                self.anidb["password"] = check_for_attribute(self.data, "password", parent="anidb", throw=True)
                self.AniDB = AniDB(self, self.anidb)
            except Failed as e:
                logger.error(e)
            logger.info(f"My Anime List Connection {'Failed Continuing as Guest ' if self.MyAnimeList is None else 'Successful'}")
        if self.AniDB is None:
            self.AniDB = AniDB(self, None)

        self.TVDb = TVDb(self)
        self.IMDb = IMDb(self)
        self.Convert = Convert(self)
        self.AniList = AniList(self)
        self.Letterboxd = Letterboxd(self)
        self.ICheckMovies = ICheckMovies(self)

        util.separator()

        logger.info("Connecting to Plex Libraries...")

        self.general["plex"] = {}
        self.general["plex"]["url"] = check_for_attribute(self.data, "url", parent="plex", var_type="url", default_is_none=True)
        self.general["plex"]["token"] = check_for_attribute(self.data, "token", parent="plex", default_is_none=True)
        self.general["plex"]["timeout"] = check_for_attribute(self.data, "timeout", parent="plex", var_type="int", default=60)
        self.general["plex"]["clean_bundles"] = check_for_attribute(self.data, "clean_bundles", parent="plex", var_type="bool", default=False)
        self.general["plex"]["empty_trash"] = check_for_attribute(self.data, "empty_trash", parent="plex", var_type="bool", default=False)
        self.general["plex"]["optimize"] = check_for_attribute(self.data, "optimize", parent="plex", var_type="bool", default=False)

        self.general["radarr"] = {}
        self.general["radarr"]["url"] = check_for_attribute(self.data, "url", parent="radarr", var_type="url", default_is_none=True)
        self.general["radarr"]["token"] = check_for_attribute(self.data, "token", parent="radarr", default_is_none=True)
        self.general["radarr"]["add"] = check_for_attribute(self.data, "add", parent="radarr", var_type="bool", default=False)
        self.general["radarr"]["root_folder_path"] = check_for_attribute(self.data, "root_folder_path", parent="radarr", default_is_none=True)
        self.general["radarr"]["monitor"] = check_for_attribute(self.data, "monitor", parent="radarr", var_type="bool", default=True)
        self.general["radarr"]["availability"] = check_for_attribute(self.data, "availability", parent="radarr", test_list=radarr_availabilities, default="announced")
        self.general["radarr"]["quality_profile"] = check_for_attribute(self.data, "quality_profile", parent="radarr", default_is_none=True)
        self.general["radarr"]["tag"] = check_for_attribute(self.data, "tag", parent="radarr", var_type="lower_list", default_is_none=True)
        self.general["radarr"]["search"] = check_for_attribute(self.data, "search", parent="radarr", var_type="bool", default=False)

        self.general["sonarr"] = {}
        self.general["sonarr"]["url"] = check_for_attribute(self.data, "url", parent="sonarr", var_type="url", default_is_none=True)
        self.general["sonarr"]["token"] = check_for_attribute(self.data, "token", parent="sonarr", default_is_none=True)
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
        self.general["tautulli"]["url"] = check_for_attribute(self.data, "url", parent="tautulli", var_type="url", default_is_none=True)
        self.general["tautulli"]["apikey"] = check_for_attribute(self.data, "apikey", parent="tautulli", default_is_none=True)

        self.libraries = []
        libs = check_for_attribute(self.data, "libraries", throw=True)

        for library_name, lib in libs.items():
            if self.requested_libraries and library_name not in self.requested_libraries:
                continue
            util.separator()
            params = {}
            params["mapping_name"] = str(library_name)
            if lib and "library_name" in lib and lib["library_name"]:
                params["name"] = str(lib["library_name"])
                display_name = f"{params['name']} ({params['mapping_name']})"
            else:
                params["name"] = params["mapping_name"]
                display_name = params["mapping_name"]

            util.separator(f"{display_name} Configuration")
            logger.info("")
            logger.info(f"Connecting to {display_name} Library...")

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
                params["mass_genre_update"] = check_for_attribute(lib, "mass_genre_update", test_list=mass_update_options, default_is_none=True, save=False)
                if self.OMDb is None and params["mass_genre_update"] == "omdb":
                    params["mass_genre_update"] = None
                    logger.error("Config Error: mass_genre_update cannot be omdb without a successful OMDb Connection")
            else:
                params["mass_genre_update"] = None

            if lib and "mass_audience_rating_update" in lib and lib["mass_audience_rating_update"]:
                params["mass_audience_rating_update"] = check_for_attribute(lib, "mass_audience_rating_update", test_list=mass_update_options, default_is_none=True, save=False)
                if self.OMDb is None and params["mass_audience_rating_update"] == "omdb":
                    params["mass_audience_rating_update"] = None
                    logger.error("Config Error: mass_audience_rating_update cannot be omdb without a successful OMDb Connection")
            else:
                params["mass_audience_rating_update"] = None

            if lib and "mass_critic_rating_update" in lib and lib["mass_critic_rating_update"]:
                params["mass_critic_rating_update"] = check_for_attribute(lib, "mass_critic_rating_update", test_list=mass_update_options, default_is_none=True, save=False)
                if self.OMDb is None and params["mass_critic_rating_update"] == "omdb":
                    params["mass_critic_rating_update"] = None
                    logger.error("Config Error: mass_critic_rating_update cannot be omdb without a successful OMDb Connection")
            else:
                params["mass_critic_rating_update"] = None

            if lib and "split_duplicates" in lib and lib["split_duplicates"]:
                params["split_duplicates"] = check_for_attribute(lib, "split_duplicates", var_type="bool", default=False, save=False)
            else:
                params["split_duplicates"] = None

            if lib and "radarr_add_all" in lib and lib["radarr_add_all"]:
                params["radarr_add_all"] = check_for_attribute(lib, "radarr_add_all", var_type="bool", default=False, save=False)
            else:
                params["radarr_add_all"] = None

            if lib and "sonarr_add_all" in lib and lib["sonarr_add_all"]:
                params["sonarr_add_all"] = check_for_attribute(lib, "sonarr_add_all", var_type="bool", default=False, save=False)
            else:
                params["sonarr_add_all"] = None

            try:
                if lib and "metadata_path" in lib:
                    params["metadata_path"] = []
                    if lib["metadata_path"] is None:
                        raise Failed("Config Error: metadata_path attribute is blank")
                    paths_to_check = lib["metadata_path"] if isinstance(lib["metadata_path"], list) else [lib["metadata_path"]]
                    for path in paths_to_check:
                        if isinstance(path, dict):
                            if "url" in path:
                                if path["url"] is None:
                                    logger.error("Config Error: metadata_path url is blank")
                                else:
                                    params["metadata_path"].append(("URL", path["url"]))
                            if "git" in path:
                                if path["git"] is None:
                                    logger.error("Config Error: metadata_path git is blank")
                                else:
                                    params["metadata_path"].append(("Git", path['git']))
                            if "file" in path:
                                if path["file"] is None:
                                    logger.error("Config Error: metadata_path file is blank")
                                else:
                                    params["metadata_path"].append(("File", path['file']))
                        else:
                            params["metadata_path"].append(("File", path))
                else:
                    params["metadata_path"] = [("File", os.path.join(default_dir, f"{library_name}.yml"))]
                params["default_dir"] = default_dir
                params["plex"] = {}
                params["plex"]["url"] = check_for_attribute(lib, "url", parent="plex", var_type="url", default=self.general["plex"]["url"], req_default=True, save=False)
                params["plex"]["token"] = check_for_attribute(lib, "token", parent="plex", default=self.general["plex"]["token"], req_default=True, save=False)
                params["plex"]["timeout"] = check_for_attribute(lib, "timeout", parent="plex", var_type="int", default=self.general["plex"]["timeout"], save=False)
                params["plex"]["clean_bundles"] = check_for_attribute(lib, "clean_bundles", parent="plex", var_type="bool", default=self.general["plex"]["clean_bundles"], save=False)
                params["plex"]["empty_trash"] = check_for_attribute(lib, "empty_trash", parent="plex", var_type="bool", default=self.general["plex"]["empty_trash"], save=False)
                params["plex"]["optimize"] = check_for_attribute(lib, "optimize", parent="plex", var_type="bool", default=self.general["plex"]["optimize"], save=False)
                library = Plex(self, params)
                logger.info("")
                logger.info(f"{display_name} Library Connection Successful")
            except Failed as e:
                util.print_stacktrace()
                util.print_multiline(e, error=True)
                logger.info(f"{display_name} Library Connection Failed")
                continue

            if self.general["radarr"]["url"] or (lib and "radarr" in lib):
                logger.info("")
                util.separator("Radarr Configuration", space=False, border=False)
                logger.info("")
                logger.info(f"Connecting to {display_name} library's Radarr...")
                logger.info("")
                radarr_params = {}
                try:
                    radarr_params["url"] = check_for_attribute(lib, "url", parent="radarr", var_type="url", default=self.general["radarr"]["url"], req_default=True, save=False)
                    radarr_params["token"] = check_for_attribute(lib, "token", parent="radarr", default=self.general["radarr"]["token"], req_default=True, save=False)
                    radarr_params["add"] = check_for_attribute(lib, "add", parent="radarr", var_type="bool", default=self.general["radarr"]["add"], save=False)
                    radarr_params["root_folder_path"] = check_for_attribute(lib, "root_folder_path", parent="radarr", default=self.general["radarr"]["root_folder_path"], req_default=True, save=False)
                    radarr_params["monitor"] = check_for_attribute(lib, "monitor", parent="radarr", var_type="bool", default=self.general["radarr"]["monitor"], save=False)
                    radarr_params["availability"] = check_for_attribute(lib, "availability", parent="radarr", test_list=radarr_availabilities, default=self.general["radarr"]["availability"], save=False)
                    radarr_params["quality_profile"] = check_for_attribute(lib, "quality_profile", parent="radarr", default=self.general["radarr"]["quality_profile"], req_default=True, save=False)
                    radarr_params["tag"] = check_for_attribute(lib, "tag", parent="radarr", var_type="lower_list", default=self.general["radarr"]["tag"], default_is_none=True, save=False)
                    radarr_params["search"] = check_for_attribute(lib, "search", parent="radarr", var_type="bool", default=self.general["radarr"]["search"], save=False)
                    library.Radarr = Radarr(self, radarr_params)
                except Failed as e:
                    util.print_stacktrace()
                    util.print_multiline(e, error=True)
                    logger.info("")
                logger.info(f"{display_name} library's Radarr Connection {'Failed' if library.Radarr is None else 'Successful'}")

            if self.general["sonarr"]["url"] or (lib and "sonarr" in lib):
                logger.info("")
                util.separator("Sonarr Configuration", space=False, border=False)
                logger.info("")
                logger.info(f"Connecting to {display_name} library's Sonarr...")
                logger.info("")
                sonarr_params = {}
                try:
                    sonarr_params["url"] = check_for_attribute(lib, "url", parent="sonarr", var_type="url", default=self.general["sonarr"]["url"], req_default=True, save=False)
                    sonarr_params["token"] = check_for_attribute(lib, "token", parent="sonarr", default=self.general["sonarr"]["token"], req_default=True, save=False)
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
                    sonarr_params["tag"] = check_for_attribute(lib, "tag", parent="sonarr", var_type="lower_list", default=self.general["sonarr"]["tag"], default_is_none=True, save=False)
                    sonarr_params["search"] = check_for_attribute(lib, "search", parent="sonarr", var_type="bool", default=self.general["sonarr"]["search"], save=False)
                    sonarr_params["cutoff_search"] = check_for_attribute(lib, "cutoff_search", parent="sonarr", var_type="bool", default=self.general["sonarr"]["cutoff_search"], save=False)
                    library.Sonarr = Sonarr(self, sonarr_params)
                except Failed as e:
                    util.print_stacktrace()
                    util.print_multiline(e, error=True)
                    logger.info("")
                logger.info(f"{display_name} library's Sonarr Connection {'Failed' if library.Sonarr is None else 'Successful'}")

            if self.general["tautulli"]["url"] or (lib and "tautulli" in lib):
                logger.info("")
                util.separator("Tautulli Configuration", space=False, border=False)
                logger.info("")
                logger.info(f"Connecting to {display_name} library's Tautulli...")
                logger.info("")
                tautulli_params = {}
                try:
                    tautulli_params["url"] = check_for_attribute(lib, "url", parent="tautulli", var_type="url", default=self.general["tautulli"]["url"], req_default=True, save=False)
                    tautulli_params["apikey"] = check_for_attribute(lib, "apikey", parent="tautulli", default=self.general["tautulli"]["apikey"], req_default=True, save=False)
                    library.Tautulli = Tautulli(self, tautulli_params)
                except Failed as e:
                    util.print_stacktrace()
                    util.print_multiline(e, error=True)
                    logger.info("")
                logger.info(f"{display_name} library's Tautulli Connection {'Failed' if library.Tautulli is None else 'Successful'}")

            logger.info("")
            self.libraries.append(library)

        util.separator()

        if len(self.libraries) > 0:
            logger.info(f"{len(self.libraries)} Plex Library Connection{'s' if len(self.libraries) > 1 else ''} Successful")
        else:
            raise Failed("Plex Error: No Plex libraries were connected to")

        util.separator()

    def get_html(self, url, headers=None):
        return html.fromstring(self.get(url, headers=headers).content)

    def get_json(self, url, headers=None):
        return self.get(url, headers=headers).json()

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def get(self, url, headers=None, params=None):
        return self.session.get(url, headers=headers, params=params)

    def post_html(self, url, data=None, json=None, headers=None):
        return html.fromstring(self.post(url, data=data, json=json, headers=headers).content)

    def post_json(self, url, data=None, json=None, headers=None):
        return self.post(url, data=data, json=json, headers=headers).json()

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def post(self, url, data=None, json=None, headers=None):
        return self.session.post(url, data=data, json=json, headers=headers)
