import base64, logging, os, requests
from datetime import datetime
from lxml import html
from modules import util, radarr, sonarr
from modules.anidb import AniDB
from modules.anilist import AniList
from modules.cache import Cache
from modules.convert import Convert
from modules.flixpatrol import FlixPatrol
from modules.icheckmovies import ICheckMovies
from modules.imdb import IMDb
from modules.letterboxd import Letterboxd
from modules.mal import MyAnimeList
from modules.meta import PlaylistFile
from modules.notifiarr import Notifiarr
from modules.omdb import OMDb
from modules.plex import Plex
from modules.radarr import Radarr
from modules.sonarr import Sonarr
from modules.stevenlu import StevenLu
from modules.mdblist import Mdblist
from modules.tautulli import Tautulli
from modules.tmdb import TMDb
from modules.trakt import Trakt
from modules.tvdb import TVDb
from modules.util import Failed, NotScheduled
from modules.webhooks import Webhooks
from retrying import retry
from ruamel import yaml

logger = logging.getLogger("Plex Meta Manager")

sync_modes = {"append": "Only Add Items to the Collection or Playlist", "sync": "Add & Remove Items from the Collection or Playlist"}
mass_update_options = {"tmdb": "Use TMDb Metadata", "omdb": "Use IMDb Metadata through OMDb"}
mass_content_options = {"omdb": "Use IMDb Metadata through OMDb", "mdb": "Use MdbList Metadata", "mdb_commonsense": "Use Commonsense Rating through MDbList"}
mass_rating_options = {
    "tmdb": "Use TMDb Rating",
    "omdb": "Use IMDb Rating through OMDb",
    "mdb": "Use MdbList Average Score",
    "mdb_imdb": "Use IMDb Rating through MDbList",
    "mdb_metacritic": "Use Metacritic Rating through MDbList",
    "mdb_metacriticuser": "Use Metacritic User Rating through MDbList",
    "mdb_trakt": "Use Trakt Rating through MDbList",
    "mdb_tomatoes": "Use Rotten Tomatoes Rating through MDbList",
    "mdb_tomatoesaudience": "Use Rotten Tomatoes Audience Rating through MDbList",
    "mdb_tmdb": "Use TMDb Rating through MDbList",
    "mdb_letterboxd": "Use Letterboxd Rating through MDbList"
}

class ConfigFile:
    def __init__(self, default_dir, attrs, read_only):
        logger.info("Locating config...")
        config_file = attrs["config_file"]
        if config_file and os.path.exists(config_file):                     self.config_path = os.path.abspath(config_file)
        elif config_file and not os.path.exists(config_file):               raise Failed(f"Config Error: config not found at {os.path.abspath(config_file)}")
        elif os.path.exists(os.path.join(default_dir, "config.yml")):       self.config_path = os.path.abspath(os.path.join(default_dir, "config.yml"))
        else:                                                               raise Failed(f"Config Error: config not found at {os.path.abspath(default_dir)}")
        logger.info(f"Using {self.config_path} as config")

        self.default_dir = default_dir
        self.read_only = read_only
        self.test_mode = attrs["test"] if "test" in attrs else False
        self.trace_mode = attrs["trace"] if "trace" in attrs else False
        self.delete_collections = attrs["delete"] if "delete" in attrs else False
        self.ignore_schedules = attrs["ignore_schedules"] if "ignore_schedules" in attrs else False
        self.library_first = attrs["library_first"] if "library_first" in attrs else False
        self.start_time = attrs["time_obj"]
        self.run_hour = datetime.strptime(attrs["time"], "%H:%M").hour
        self.requested_collections = util.get_list(attrs["collections"]) if "collections" in attrs else None
        self.requested_libraries = util.get_list(attrs["libraries"]) if "libraries" in attrs else None
        self.requested_metadata_files = util.get_list(attrs["metadata_files"]) if "metadata_files" in attrs else None
        self.resume_from = attrs["resume"] if "resume" in attrs else None

        yaml.YAML().allow_duplicate_keys = True
        try:
            new_config, _, _ = yaml.util.load_yaml_guess_indent(open(self.config_path, encoding="utf-8"))
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
                    if not new_config["libraries"][library]:
                        continue
                    if "radarr_add_all" in new_config["libraries"][library]:
                        new_config["libraries"][library]["radarr_add_all_existing"] = new_config["libraries"][library].pop("radarr_add_all")
                    if "sonarr_add_all" in new_config["libraries"][library]:
                        new_config["libraries"][library]["sonarr_add_all_existing"] = new_config["libraries"][library].pop("sonarr_add_all")
                    if "plex" in new_config["libraries"][library] and new_config["libraries"][library]["plex"]:
                        replace_attr(new_config["libraries"][library], "asset_directory", "plex")
                        replace_attr(new_config["libraries"][library], "sync_mode", "plex")
                        replace_attr(new_config["libraries"][library], "show_unmanaged", "plex")
                        replace_attr(new_config["libraries"][library], "show_filtered", "plex")
                        replace_attr(new_config["libraries"][library], "show_missing", "plex")
                        replace_attr(new_config["libraries"][library], "save_missing", "plex")
                    if "settings" in new_config["libraries"][library] and new_config["libraries"][library]["settings"]:
                        if "collection_minimum" in new_config["libraries"][library]["settings"]:
                            new_config["libraries"][library]["settings"]["minimum_items"] = new_config["libraries"][library]["settings"].pop("collection_minimum")
                    if "radarr" in new_config["libraries"][library] and new_config["libraries"][library]["radarr"]:
                        if "add" in new_config["libraries"][library]["radarr"]:
                            new_config["libraries"][library]["radarr"]["add_missing"] = new_config["libraries"][library]["radarr"].pop("add")
                    if "sonarr" in new_config["libraries"][library] and new_config["libraries"][library]["sonarr"]:
                        if "add" in new_config["libraries"][library]["sonarr"]:
                            new_config["libraries"][library]["sonarr"]["add_missing"] = new_config["libraries"][library]["sonarr"].pop("add")
                    if "operations" in new_config["libraries"][library] and new_config["libraries"][library]["operations"]:
                        if "radarr_add_all" in new_config["libraries"][library]["operations"]:
                            new_config["libraries"][library]["operations"]["radarr_add_all_existing"] = new_config["libraries"][library]["operations"].pop("radarr_add_all")
                        if "sonarr_add_all" in new_config["libraries"][library]["operations"]:
                            new_config["libraries"][library]["operations"]["sonarr_add_all_existing"] = new_config["libraries"][library]["operations"].pop("sonarr_add_all")
                    if "webhooks" in new_config["libraries"][library] and new_config["libraries"][library]["webhooks"] and "collection_changes" not in new_config["libraries"][library]["webhooks"]:
                        changes = []
                        def hooks(attr):
                            if attr in new_config["libraries"][library]["webhooks"]:
                                changes.extend([w for w in util.get_list(new_config["libraries"][library]["webhooks"].pop(attr), split=False) if w not in changes])
                        hooks("collection_creation")
                        hooks("collection_addition")
                        hooks("collection_removal")
                        hooks("collection_changes")
                        new_config["libraries"][library]["webhooks"]["changes"] = None if not changes else changes if len(changes) > 1 else changes[0]
            if "libraries" in new_config:                   new_config["libraries"] = new_config.pop("libraries")
            if "playlists" in new_config:                   new_config["playlists"] = new_config.pop("playlists")
            if "settings" in new_config:
                temp = new_config.pop("settings")
                if "collection_minimum" in temp:
                    temp["minimum_items"] = temp.pop("collection_minimum")
                if "playlist_sync_to_user" in temp:
                    temp["playlist_sync_to_users"] = temp.pop("playlist_sync_to_user")
                new_config["settings"] = temp
            if "webhooks" in new_config:
                temp = new_config.pop("webhooks")
                if "changes" not in temp:
                    changes = []
                    def hooks(attr):
                        if attr in temp:
                            items = util.get_list(temp.pop(attr), split=False)
                            if items:
                                changes.extend([w for w in items if w not in changes])
                    hooks("collection_creation")
                    hooks("collection_addition")
                    hooks("collection_removal")
                    hooks("collection_changes")
                    temp["changes"] = None if not changes else changes if len(changes) > 1 else changes[0]
                new_config["webhooks"] = temp
            if "plex" in new_config:                        new_config["plex"] = new_config.pop("plex")
            if "tmdb" in new_config:                        new_config["tmdb"] = new_config.pop("tmdb")
            if "tautulli" in new_config:                    new_config["tautulli"] = new_config.pop("tautulli")
            if "omdb" in new_config:                        new_config["omdb"] = new_config.pop("omdb")
            if "mdblist" in new_config:                     new_config["mdblist"] = new_config.pop("mdblist")
            if "notifiarr" in new_config:                   new_config["notifiarr"] = new_config.pop("notifiarr")
            if "anidb" in new_config:                       new_config["anidb"] = new_config.pop("anidb")
            if "radarr" in new_config:
                temp = new_config.pop("radarr")
                if temp and "add" in temp:
                    temp["add_missing"] = temp.pop("add")
                new_config["radarr"] = temp
            if "sonarr" in new_config:
                temp = new_config.pop("sonarr")
                if temp and "add" in temp:
                    temp["add_missing"] = temp.pop("add")
                new_config["sonarr"] = temp
            if "trakt" in new_config:                       new_config["trakt"] = new_config.pop("trakt")
            if "mal" in new_config:                         new_config["mal"] = new_config.pop("mal")
            if not self.read_only:
                yaml.round_trip_dump(new_config, open(self.config_path, "w", encoding="utf-8"), indent=None, block_seq_indent=2)
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
            if self.read_only:
                save = False
            text = f"{attribute} attribute" if parent is None else f"{parent} sub-attribute {attribute}"
            if data is None or attribute not in data:
                message = f"{text} not found"
                if parent and save is True:
                    loaded_config, _, _ = yaml.util.load_yaml_guess_indent(open(self.config_path))
                    endline = f"\n{parent} sub-attribute {attribute} added to config"
                    if parent not in loaded_config or not loaded_config[parent]:        loaded_config[parent] = {attribute: default}
                    elif attribute not in loaded_config[parent]:                        loaded_config[parent][attribute] = default
                    else:                                                               endline = ""
                    yaml.round_trip_dump(loaded_config, open(self.config_path, "w"), indent=None, block_seq_indent=2)
                if default_is_none and var_type in ["list", "int_list", "comma_list"]: return default if default else []
            elif data[attribute] is None:
                if default_is_none and var_type in ["list", "int_list", "comma_list"]: return default if default else []
                elif default_is_none:                                               return None
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
            elif var_type == "list":                                            return util.get_list(data[attribute], split=False)
            elif var_type == "comma_list":                                      return util.get_list(data[attribute])
            elif var_type == "int_list":                                        return util.get_list(data[attribute], int_list=True)
            elif var_type == "list_path":
                temp_list = []
                warning_message = ""
                for p in util.get_list(data[attribute], split=False):
                    if os.path.exists(os.path.abspath(p)):
                        temp_list.append(p)
                    else:
                        if len(warning_message) > 0:
                            warning_message += "\n"
                        warning_message += f"Config Warning: Path does not exist: {os.path.abspath(p)}"
                if do_print and warning_message:
                    util.print_multiline(warning_message)
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
                if data and attribute in data and data[attribute] and test_list is not None and data[attribute] not in test_list:
                    util.print_multiline(options)
            return default

        self.general = {
            "cache": check_for_attribute(self.data, "cache", parent="settings", var_type="bool", default=True),
            "cache_expiration": check_for_attribute(self.data, "cache_expiration", parent="settings", var_type="int", default=60),
            "asset_directory": check_for_attribute(self.data, "asset_directory", parent="settings", var_type="list_path", default=[os.path.join(default_dir, "assets")], default_is_none=True),
            "asset_folders": check_for_attribute(self.data, "asset_folders", parent="settings", var_type="bool", default=True),
            "asset_depth": check_for_attribute(self.data, "asset_depth", parent="settings", var_type="int", default=0),
            "create_asset_folders": check_for_attribute(self.data, "create_asset_folders", parent="settings", var_type="bool", default=False),
            "dimensional_asset_rename": check_for_attribute(self.data, "dimensional_asset_rename", parent="settings", var_type="bool", default=False),
            "download_url_assets": check_for_attribute(self.data, "download_url_assets", parent="settings", var_type="bool", default=False),
            "show_missing_season_assets": check_for_attribute(self.data, "show_missing_season_assets", parent="settings", var_type="bool", default=False),
            "show_missing_episode_assets": check_for_attribute(self.data, "show_missing_episode_assets", parent="settings", var_type="bool", default=False),
            "show_asset_not_needed": check_for_attribute(self.data, "show_asset_not_needed", parent="settings", var_type="bool", default=True),
            "sync_mode": check_for_attribute(self.data, "sync_mode", parent="settings", default="append", test_list=sync_modes),
            "default_collection_order": check_for_attribute(self.data, "default_collection_order", parent="settings", default_is_none=True),
            "minimum_items": check_for_attribute(self.data, "minimum_items", parent="settings", var_type="int", default=1),
            "item_refresh_delay": check_for_attribute(self.data, "item_refresh_delay", parent="settings", var_type="int", default=0),
            "delete_below_minimum": check_for_attribute(self.data, "delete_below_minimum", parent="settings", var_type="bool", default=False),
            "delete_not_scheduled": check_for_attribute(self.data, "delete_not_scheduled", parent="settings", var_type="bool", default=False),
            "run_again_delay": check_for_attribute(self.data, "run_again_delay", parent="settings", var_type="int", default=0),
            "missing_only_released": check_for_attribute(self.data, "missing_only_released", parent="settings", var_type="bool", default=False),
            "only_filter_missing": check_for_attribute(self.data, "only_filter_missing", parent="settings", var_type="bool", default=False),
            "show_unmanaged": check_for_attribute(self.data, "show_unmanaged", parent="settings", var_type="bool", default=True),
            "show_filtered": check_for_attribute(self.data, "show_filtered", parent="settings", var_type="bool", default=False),
            "show_options": check_for_attribute(self.data, "show_options", parent="settings", var_type="bool", default=False),
            "show_missing": check_for_attribute(self.data, "show_missing", parent="settings", var_type="bool", default=True),
            "show_missing_assets": check_for_attribute(self.data, "show_missing_assets", parent="settings", var_type="bool", default=True),
            "save_missing": check_for_attribute(self.data, "save_missing", parent="settings", var_type="bool", default=True),
            "tvdb_language": check_for_attribute(self.data, "tvdb_language", parent="settings", default="default"),
            "ignore_ids": check_for_attribute(self.data, "ignore_ids", parent="settings", var_type="int_list", default_is_none=True),
            "ignore_imdb_ids": check_for_attribute(self.data, "ignore_imdb_ids", parent="settings", var_type="list", default_is_none=True),
            "playlist_sync_to_users": check_for_attribute(self.data, "playlist_sync_to_users", parent="settings", default="all", default_is_none=True),
            "verify_ssl": check_for_attribute(self.data, "verify_ssl", parent="settings", var_type="bool", default=True),
            "custom_repo": check_for_attribute(self.data, "custom_repo", parent="settings", default_is_none=True),
            "assets_for_all": check_for_attribute(self.data, "assets_for_all", parent="settings", var_type="bool", default=False, save=False, do_print=False)
        }
        self.custom_repo = self.general["custom_repo"]

        self.session = requests.Session()
        if not self.general["verify_ssl"]:
            self.session.verify = False
            if self.session.verify is False:
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.webhooks = {
            "error": check_for_attribute(self.data, "error", parent="webhooks", var_type="list", default_is_none=True),
            "run_start": check_for_attribute(self.data, "run_start", parent="webhooks", var_type="list", default_is_none=True),
            "run_end": check_for_attribute(self.data, "run_end", parent="webhooks", var_type="list", default_is_none=True),
            "changes": check_for_attribute(self.data, "changes", parent="webhooks", var_type="list", default_is_none=True)
        }
        if self.general["cache"]:
            util.separator()
            self.Cache = Cache(self.config_path, self.general["cache_expiration"])
        else:
            self.Cache = None

        util.separator()

        self.NotifiarrFactory = None
        if "notifiarr" in self.data:
            logger.info("Connecting to Notifiarr...")
            try:
                self.NotifiarrFactory = Notifiarr(self, {
                    "apikey": check_for_attribute(self.data, "apikey", parent="notifiarr", throw=True),
                    "develop": check_for_attribute(self.data, "develop", parent="notifiarr", var_type="bool", default=False, do_print=False, save=False),
                    "test": check_for_attribute(self.data, "test", parent="notifiarr", var_type="bool", default=False, do_print=False, save=False)
                })
            except Failed as e:
                util.print_stacktrace()
                logger.error(e)
            logger.info(f"Notifiarr Connection {'Failed' if self.NotifiarrFactory is None else 'Successful'}")
        else:
            logger.warning("notifiarr attribute not found")

        self.Webhooks = Webhooks(self, self.webhooks, notifiarr=self.NotifiarrFactory)
        try:
            self.Webhooks.start_time_hooks(self.start_time)
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Webhooks Error: {e}")

        self.errors = []

        util.separator()

        try:
            self.TMDb = None
            if "tmdb" in self.data:
                logger.info("Connecting to TMDb...")
                self.TMDb = TMDb(self, {
                    "apikey": check_for_attribute(self.data, "apikey", parent="tmdb", throw=True),
                    "language": check_for_attribute(self.data, "language", parent="tmdb", default="en")
                })
                logger.info(f"TMDb Connection {'Failed' if self.TMDb is None else 'Successful'}")
            else:
                raise Failed("Config Error: tmdb attribute not found")

            util.separator()

            self.OMDb = None
            if "omdb" in self.data:
                logger.info("Connecting to OMDb...")
                try:
                    self.OMDb = OMDb(self, {"apikey": check_for_attribute(self.data, "apikey", parent="omdb", throw=True)})
                except Failed as e:
                    self.errors.append(e)
                    logger.error(e)
                logger.info(f"OMDb Connection {'Failed' if self.OMDb is None else 'Successful'}")
            else:
                logger.warning("omdb attribute not found")

            util.separator()

            self.Mdblist = Mdblist(self)
            if "mdblist" in self.data:
                logger.info("Connecting to Mdblist...")
                try:
                    self.Mdblist.add_key(check_for_attribute(self.data, "apikey", parent="mdblist", throw=True))
                    logger.info("Mdblist Connection Successful")
                except Failed as e:
                    self.errors.append(e)
                    logger.error(e)
                    logger.info("Mdblist Connection Failed")
            else:
                logger.warning("mdblist attribute not found")

            util.separator()

            self.Trakt = None
            if "trakt" in self.data:
                logger.info("Connecting to Trakt...")
                try:
                    self.Trakt = Trakt(self, {
                        "client_id": check_for_attribute(self.data, "client_id", parent="trakt", throw=True),
                        "client_secret": check_for_attribute(self.data, "client_secret", parent="trakt", throw=True),
                        "config_path": self.config_path,
                        "authorization": self.data["trakt"]["authorization"] if "authorization" in self.data["trakt"] else None
                    })
                except Failed as e:
                    self.errors.append(e)
                    logger.error(e)
                logger.info(f"Trakt Connection {'Failed' if self.Trakt is None else 'Successful'}")
            else:
                logger.warning("trakt attribute not found")

            util.separator()

            self.MyAnimeList = None
            if "mal" in self.data:
                logger.info("Connecting to My Anime List...")
                try:
                    self.MyAnimeList = MyAnimeList(self, {
                        "client_id": check_for_attribute(self.data, "client_id", parent="mal", throw=True),
                        "client_secret": check_for_attribute(self.data, "client_secret", parent="mal", throw=True),
                        "config_path": self.config_path,
                        "authorization": self.data["mal"]["authorization"] if "authorization" in self.data["mal"] else None
                    })
                except Failed as e:
                    self.errors.append(e)
                    logger.error(e)
                logger.info(f"My Anime List Connection {'Failed' if self.MyAnimeList is None else 'Successful'}")
            else:
                logger.warning("mal attribute not found")

            self.AniDB = None
            if "anidb" in self.data:
                util.separator()
                logger.info("Connecting to AniDB...")
                try:
                    self.AniDB = AniDB(self, {
                        "username": check_for_attribute(self.data, "username", parent="anidb", throw=True),
                        "password": check_for_attribute(self.data, "password", parent="anidb", throw=True)
                    })
                except Failed as e:
                    self.errors.append(e)
                    logger.error(e)
                logger.info(f"AniDB Connection {'Failed Continuing as Guest ' if self.MyAnimeList is None else 'Successful'}")
            if self.AniDB is None:
                self.AniDB = AniDB(self, None)

            util.separator()

            self.playlist_names = []
            self.playlist_files = []
            playlists_pairs = []
            if "playlist_files" in self.data:
                logger.info("Reading in Playlist Files")
                if self.data["playlist_files"] is None:
                    raise Failed("Config Error: playlist_files attribute is blank")
                paths_to_check = self.data["playlist_files"] if isinstance(self.data["playlist_files"], list) else [self.data["playlist_files"]]
                for path in paths_to_check:
                    if isinstance(path, dict):
                        def check_dict(attr):
                            if attr in path:
                                if path[attr] is None:
                                    err = f"Config Error: playlist_files {attr} is blank"
                                    self.errors.append(err)
                                    logger.error(err)
                                else:
                                    return path[attr]

                        url = check_dict("url")
                        if url:
                            playlists_pairs.append(("URL", url))
                        git = check_dict("git")
                        if git:
                            playlists_pairs.append(("Git", git))
                        repo = check_dict("repo")
                        if repo:
                            playlists_pairs.append(("Repo", repo))
                        file = check_dict("file")
                        if file:
                            playlists_pairs.append(("File", file))
                        folder = check_dict("folder")
                        if folder:
                            if os.path.isdir(folder):
                                yml_files = util.glob_filter(os.path.join(folder, "*.yml"))
                                if yml_files:
                                    playlists_pairs.extend([("File", yml) for yml in yml_files])
                                else:
                                    logger.error(f"Config Error: No YAML (.yml) files found in {folder}")
                            else:
                                logger.error(f"Config Error: Folder not found: {folder}")
                    else:
                        playlists_pairs.append(("File", path))
            else:
                default_playlist_file = os.path.abspath(os.path.join(self.default_dir, "playlists.yml"))
                if os.path.exists(default_playlist_file):
                    playlists_pairs.append(("File", default_playlist_file))
                    logger.warning(f"playlist_files attribute not found using {default_playlist_file} as default")
                else:
                    logger.warning("playlist_files attribute not found")
            for file_type, playlist_file in playlists_pairs:
                try:
                    playlist_obj = PlaylistFile(self, file_type, playlist_file)
                    self.playlist_names.extend([p for p in playlist_obj.playlists])
                    self.playlist_files.append(playlist_obj)
                except Failed as e:
                    util.print_multiline(e, error=True)

            self.TVDb = TVDb(self, self.general["tvdb_language"])
            self.IMDb = IMDb(self)
            self.Convert = Convert(self)
            self.AniList = AniList(self)
            self.FlixPatrol = FlixPatrol(self)
            self.ICheckMovies = ICheckMovies(self)
            self.Letterboxd = Letterboxd(self)
            self.StevenLu = StevenLu(self)

            util.separator()

            logger.info("Connecting to Plex Libraries...")

            self.general["plex"] = {
                "url": check_for_attribute(self.data, "url", parent="plex", var_type="url", default_is_none=True),
                "token": check_for_attribute(self.data, "token", parent="plex", default_is_none=True),
                "timeout": check_for_attribute(self.data, "timeout", parent="plex", var_type="int", default=60),
                "clean_bundles": check_for_attribute(self.data, "clean_bundles", parent="plex", var_type="bool", default=False),
                "empty_trash": check_for_attribute(self.data, "empty_trash", parent="plex", var_type="bool", default=False),
                "optimize": check_for_attribute(self.data, "optimize", parent="plex", var_type="bool", default=False)
            }
            self.general["radarr"] = {
                "url": check_for_attribute(self.data, "url", parent="radarr", var_type="url", default_is_none=True),
                "token": check_for_attribute(self.data, "token", parent="radarr", default_is_none=True),
                "add_missing": check_for_attribute(self.data, "add_missing", parent="radarr", var_type="bool", default=False),
                "add_existing": check_for_attribute(self.data, "add_existing", parent="radarr", var_type="bool", default=False),
                "root_folder_path": check_for_attribute(self.data, "root_folder_path", parent="radarr", default_is_none=True),
                "monitor": check_for_attribute(self.data, "monitor", parent="radarr", var_type="bool", default=True),
                "availability": check_for_attribute(self.data, "availability", parent="radarr", test_list=radarr.availability_descriptions, default="announced"),
                "quality_profile": check_for_attribute(self.data, "quality_profile", parent="radarr", default_is_none=True),
                "tag": check_for_attribute(self.data, "tag", parent="radarr", var_type="lower_list", default_is_none=True),
                "search": check_for_attribute(self.data, "search", parent="radarr", var_type="bool", default=False),
                "radarr_path": check_for_attribute(self.data, "radarr_path", parent="radarr", default_is_none=True),
                "plex_path": check_for_attribute(self.data, "plex_path", parent="radarr", default_is_none=True)
            }
            self.general["sonarr"] = {
                "url": check_for_attribute(self.data, "url", parent="sonarr", var_type="url", default_is_none=True),
                "token": check_for_attribute(self.data, "token", parent="sonarr", default_is_none=True),
                "add_missing": check_for_attribute(self.data, "add_missing", parent="sonarr", var_type="bool", default=False),
                "add_existing": check_for_attribute(self.data, "add_existing", parent="sonarr", var_type="bool", default=False),
                "root_folder_path": check_for_attribute(self.data, "root_folder_path", parent="sonarr", default_is_none=True),
                "monitor": check_for_attribute(self.data, "monitor", parent="sonarr", test_list=sonarr.monitor_descriptions, default="all"),
                "quality_profile": check_for_attribute(self.data, "quality_profile", parent="sonarr", default_is_none=True),
                "language_profile": check_for_attribute(self.data, "language_profile", parent="sonarr", default_is_none=True),
                "series_type": check_for_attribute(self.data, "series_type", parent="sonarr", test_list=sonarr.series_type_descriptions, default="standard"),
                "season_folder": check_for_attribute(self.data, "season_folder", parent="sonarr", var_type="bool", default=True),
                "tag": check_for_attribute(self.data, "tag", parent="sonarr", var_type="lower_list", default_is_none=True),
                "search": check_for_attribute(self.data, "search", parent="sonarr", var_type="bool", default=False),
                "cutoff_search": check_for_attribute(self.data, "cutoff_search", parent="sonarr", var_type="bool", default=False),
                "sonarr_path": check_for_attribute(self.data, "sonarr_path", parent="sonarr", default_is_none=True),
                "plex_path": check_for_attribute(self.data, "plex_path", parent="sonarr", default_is_none=True)
            }
            self.general["tautulli"] = {
                "url": check_for_attribute(self.data, "url", parent="tautulli", var_type="url", default_is_none=True),
                "apikey": check_for_attribute(self.data, "apikey", parent="tautulli", default_is_none=True)
            }

            self.libraries = []
            libs = check_for_attribute(self.data, "libraries", throw=True)

            current_time = datetime.now()

            for library_name, lib in libs.items():
                if self.requested_libraries and library_name not in self.requested_libraries:
                    continue
                params = {
                    "mapping_name": str(library_name),
                    "name": str(lib["library_name"]) if lib and "library_name" in lib and lib["library_name"] else str(library_name),
                    "tmdb_collections": None,
                    "genre_mapper": None,
                    "radarr_remove_by_tag": None,
                    "sonarr_remove_by_tag": None,
                    "mass_collection_mode": None,
                    "metadata_backup": None,
                    "genre_collections": None,
                    "update_blank_track_titles": None
                }
                display_name = f"{params['name']} ({params['mapping_name']})" if lib and "library_name" in lib and lib["library_name"] else params["mapping_name"]

                util.separator(f"{display_name} Configuration")
                logger.info("")
                logger.info(f"Connecting to {display_name} Library...")
                logger.info("")

                params["asset_directory"] = check_for_attribute(lib, "asset_directory", parent="settings", var_type="list_path", default=self.general["asset_directory"], default_is_none=True, save=False)
                if params["asset_directory"] is None:
                    logger.warning("Config Warning: Assets will not be used asset_directory attribute must be set under config or under this specific Library")

                params["asset_folders"] = check_for_attribute(lib, "asset_folders", parent="settings", var_type="bool", default=self.general["asset_folders"], do_print=False, save=False)
                params["asset_depth"] = check_for_attribute(lib, "asset_depth", parent="settings", var_type="int", default=self.general["asset_depth"], do_print=False, save=False)
                params["sync_mode"] = check_for_attribute(lib, "sync_mode", parent="settings", test_list=sync_modes, default=self.general["sync_mode"], do_print=False, save=False)
                params["default_collection_order"] = check_for_attribute(lib, "default_collection_order", parent="settings", default=self.general["default_collection_order"], default_is_none=True, do_print=False, save=False)
                params["show_unmanaged"] = check_for_attribute(lib, "show_unmanaged", parent="settings", var_type="bool", default=self.general["show_unmanaged"], do_print=False, save=False)
                params["show_filtered"] = check_for_attribute(lib, "show_filtered", parent="settings", var_type="bool", default=self.general["show_filtered"], do_print=False, save=False)
                params["show_options"] = check_for_attribute(lib, "show_options", parent="settings", var_type="bool", default=self.general["show_options"], do_print=False, save=False)
                params["show_missing"] = check_for_attribute(lib, "show_missing", parent="settings", var_type="bool", default=self.general["show_missing"], do_print=False, save=False)
                params["show_missing_assets"] = check_for_attribute(lib, "show_missing_assets", parent="settings", var_type="bool", default=self.general["show_missing_assets"], do_print=False, save=False)
                params["save_missing"] = check_for_attribute(lib, "save_missing", parent="settings", var_type="bool", default=self.general["save_missing"], do_print=False, save=False)
                params["missing_only_released"] = check_for_attribute(lib, "missing_only_released", parent="settings", var_type="bool", default=self.general["missing_only_released"], do_print=False, save=False)
                params["only_filter_missing"] = check_for_attribute(lib, "only_filter_missing", parent="settings", var_type="bool", default=self.general["only_filter_missing"], do_print=False, save=False)
                params["create_asset_folders"] = check_for_attribute(lib, "create_asset_folders", parent="settings", var_type="bool", default=self.general["create_asset_folders"], do_print=False, save=False)
                params["dimensional_asset_rename"] = check_for_attribute(lib, "dimensional_asset_rename", parent="settings", var_type="bool", default=self.general["dimensional_asset_rename"], do_print=False, save=False)
                params["download_url_assets"] = check_for_attribute(lib, "download_url_assets", parent="settings", var_type="bool", default=self.general["download_url_assets"], do_print=False, save=False)
                params["show_missing_season_assets"] = check_for_attribute(lib, "show_missing_season_assets", parent="settings", var_type="bool", default=self.general["show_missing_season_assets"], do_print=False, save=False)
                params["show_missing_episode_assets"] = check_for_attribute(lib, "show_missing_episode_assets", parent="settings", var_type="bool", default=self.general["show_missing_episode_assets"], do_print=False, save=False)
                params["show_asset_not_needed"] = check_for_attribute(lib, "show_asset_not_needed", parent="settings", var_type="bool", default=self.general["show_asset_not_needed"], do_print=False, save=False)
                params["minimum_items"] = check_for_attribute(lib, "minimum_items", parent="settings", var_type="int", default=self.general["minimum_items"], do_print=False, save=False)
                params["item_refresh_delay"] = check_for_attribute(lib, "item_refresh_delay", parent="settings", var_type="int", default=self.general["item_refresh_delay"], do_print=False, save=False)
                params["delete_below_minimum"] = check_for_attribute(lib, "delete_below_minimum", parent="settings", var_type="bool", default=self.general["delete_below_minimum"], do_print=False, save=False)
                params["delete_not_scheduled"] = check_for_attribute(lib, "delete_not_scheduled", parent="settings", var_type="bool", default=self.general["delete_not_scheduled"], do_print=False, save=False)
                params["delete_unmanaged_collections"] = check_for_attribute(lib, "delete_unmanaged_collections", parent="settings", var_type="bool", default=False, do_print=False, save=False)
                params["delete_collections_with_less"] = check_for_attribute(lib, "delete_collections_with_less", parent="settings", var_type="int", default_is_none=True, do_print=False, save=False)
                params["ignore_ids"] = check_for_attribute(lib, "ignore_ids", parent="settings", var_type="int_list", default_is_none=True, do_print=False, save=False)
                params["ignore_ids"].extend([i for i in self.general["ignore_ids"] if i not in params["ignore_ids"]])
                params["ignore_imdb_ids"] = check_for_attribute(lib, "ignore_imdb_ids", parent="settings", var_type="list", default_is_none=True, do_print=False, save=False)
                params["ignore_imdb_ids"].extend([i for i in self.general["ignore_imdb_ids"] if i not in params["ignore_imdb_ids"]])
                params["error_webhooks"] = check_for_attribute(lib, "error", parent="webhooks", var_type="list", default=self.webhooks["error"], do_print=False, save=False, default_is_none=True)
                params["changes_webhooks"] = check_for_attribute(lib, "changes", parent="webhooks", var_type="list", default=self.webhooks["changes"], do_print=False, save=False, default_is_none=True)
                params["assets_for_all"] = check_for_attribute(lib, "assets_for_all", parent="settings", var_type="bool", default=self.general["assets_for_all"], do_print=False, save=False)
                params["mass_genre_update"] = check_for_attribute(lib, "mass_genre_update", test_list=mass_update_options, default_is_none=True, save=False, do_print=False)
                params["mass_audience_rating_update"] = check_for_attribute(lib, "mass_audience_rating_update", test_list=mass_rating_options, default_is_none=True, save=False, do_print=False)
                params["mass_critic_rating_update"] = check_for_attribute(lib, "mass_critic_rating_update", test_list=mass_rating_options, default_is_none=True, save=False, do_print=False)
                params["mass_trakt_rating_update"] = check_for_attribute(lib, "mass_trakt_rating_update", var_type="bool", default=False, save=False, do_print=False)
                params["split_duplicates"] = check_for_attribute(lib, "split_duplicates", var_type="bool", default=False, save=False, do_print=False)
                params["radarr_add_all_existing"] = check_for_attribute(lib, "radarr_add_all_existing", var_type="bool", default=False, save=False, do_print=False)
                params["sonarr_add_all_existing"] = check_for_attribute(lib, "sonarr_add_all_existing", var_type="bool", default=False, save=False, do_print=False)
                params["missing_path"] = check_for_attribute(lib, "missing_path", var_type="path", default_is_none=True, save=False)

                if lib and "operations" in lib and lib["operations"]:
                    if isinstance(lib["operations"], dict):
                        if "assets_for_all" in lib["operations"]:
                            params["assets_for_all"] = check_for_attribute(lib["operations"], "assets_for_all", var_type="bool", default=False, save=False)
                        if "delete_unmanaged_collections" in lib["operations"]:
                            params["delete_unmanaged_collections"] = check_for_attribute(lib["operations"], "delete_unmanaged_collections", var_type="bool", default=False, save=False)
                        if "delete_collections_with_less" in lib["operations"]:
                            params["delete_collections_with_less"] = check_for_attribute(lib["operations"], "delete_collections_with_less", var_type="int", default_is_none=True, save=False)
                        if "mass_genre_update" in lib["operations"]:
                            params["mass_genre_update"] = check_for_attribute(lib["operations"], "mass_genre_update", test_list=mass_update_options, default_is_none=True, save=False)
                        if "mass_audience_rating_update" in lib["operations"]:
                            params["mass_audience_rating_update"] = check_for_attribute(lib["operations"], "mass_audience_rating_update", test_list=mass_rating_options, default_is_none=True, save=False)
                        if "mass_critic_rating_update" in lib["operations"]:
                            params["mass_critic_rating_update"] = check_for_attribute(lib["operations"], "mass_critic_rating_update", test_list=mass_rating_options, default_is_none=True, save=False)
                        if "mass_content_rating_update" in lib["operations"]:
                            params["mass_content_rating_update"] = check_for_attribute(lib["operations"], "mass_content_rating_update", test_list=mass_content_options, default_is_none=True, save=False)
                        if "mass_trakt_rating_update" in lib["operations"]:
                            params["mass_trakt_rating_update"] = check_for_attribute(lib["operations"], "mass_trakt_rating_update", var_type="bool", default=False, save=False)
                        if "split_duplicates" in lib["operations"]:
                            params["split_duplicates"] = check_for_attribute(lib["operations"], "split_duplicates", var_type="bool", default=False, save=False)
                        if "radarr_add_all_existing" in lib["operations"]:
                            params["radarr_add_all_existing"] = check_for_attribute(lib["operations"], "radarr_add_all_existing", var_type="bool", default=False, save=False)
                        if "radarr_remove_by_tag" in lib["operations"]:
                            params["radarr_remove_by_tag"] = check_for_attribute(lib["operations"], "radarr_remove_by_tag", var_type="comma_list", default=False, save=False)
                        if "sonarr_add_all_existing" in lib["operations"]:
                            params["sonarr_add_all_existing"] = check_for_attribute(lib["operations"], "sonarr_add_all_existing", var_type="bool", default=False, save=False)
                        if "sonarr_remove_by_tag" in lib["operations"]:
                            params["sonarr_remove_by_tag"] = check_for_attribute(lib["operations"], "sonarr_remove_by_tag", var_type="comma_list", default=False, save=False)
                        if "update_blank_track_titles" in lib["operations"]:
                            params["update_blank_track_titles"] = check_for_attribute(lib["operations"], "update_blank_track_titles", var_type="bool", default=False, save=False)
                        if "mass_collection_mode" in lib["operations"]:
                            try:
                                params["mass_collection_mode"] = util.check_collection_mode(lib["operations"]["mass_collection_mode"])
                            except Failed as e:
                                logger.error(e)
                        if "metadata_backup" in lib["operations"]:
                            params["metadata_backup"] = {
                                "path": os.path.join(default_dir, f"{str(library_name)}_Metadata_Backup.yml"),
                                "exclude": [],
                                "sync_tags": False,
                                "add_blank_entries": True
                            }
                            if lib["operations"]["metadata_backup"] and isinstance(lib["operations"]["metadata_backup"], dict):
                                params["metadata_backup"]["path"] = check_for_attribute(lib["operations"]["metadata_backup"], "path", var_type="path", default=params["metadata_backup"]["path"], save=False)
                                params["metadata_backup"]["exclude"] = check_for_attribute(lib["operations"]["metadata_backup"], "exclude", var_type="comma_list", default_is_none=True, save=False)
                                params["metadata_backup"]["sync_tags"] = check_for_attribute(lib["operations"]["metadata_backup"], "sync_tags", var_type="bool", default=False, save=False)
                                params["metadata_backup"]["add_blank_entries"] = check_for_attribute(lib["operations"]["metadata_backup"], "add_blank_entries", var_type="bool", default=True, save=False)
                        if "tmdb_collections" in lib["operations"]:
                            params["tmdb_collections"] = {
                                "exclude_ids": [],
                                "remove_suffix": [],
                                "dictionary_variables": {},
                                "template": {"tmdb_collection_details": "<<collection_id>>"}
                            }
                            if lib["operations"]["tmdb_collections"] and isinstance(lib["operations"]["tmdb_collections"], dict):
                                params["tmdb_collections"]["exclude_ids"] = check_for_attribute(lib["operations"]["tmdb_collections"], "exclude_ids", var_type="int_list", default_is_none=True, save=False)
                                params["tmdb_collections"]["remove_suffix"] = check_for_attribute(lib["operations"]["tmdb_collections"], "remove_suffix", var_type="comma_list", default_is_none=True, save=False)
                                if "dictionary_variables" in lib["operations"]["tmdb_collections"] and lib["operations"]["tmdb_collections"]["dictionary_variables"] and isinstance(lib["operations"]["tmdb_collections"]["dictionary_variables"], dict):
                                    for key, value in lib["operations"]["tmdb_collections"]["dictionary_variables"].items():
                                        if isinstance(value, dict):
                                            params["tmdb_collections"]["dictionary_variables"][key] = value
                                        else:
                                            logger.warning(f"Config Warning: tmdb_collections dictionary_variables {key} must be a dictionary")
                                if "template" in lib["operations"]["tmdb_collections"] and lib["operations"]["tmdb_collections"]["template"] and isinstance(lib["operations"]["tmdb_collections"]["template"], dict):
                                    params["tmdb_collections"]["template"] = lib["operations"]["tmdb_collections"]["template"]
                                else:
                                    logger.warning("Config Warning: Using default template for tmdb_collections")
                            else:
                                logger.error("Config Error: tmdb_collections blank using default settings")
                        if "genre_mapper" in lib["operations"]:
                            if lib["operations"]["genre_mapper"] and isinstance(lib["operations"]["genre_mapper"], dict):
                                params["genre_mapper"] = {}
                                for new_genre, old_genres in lib["operations"]["genre_mapper"].items():
                                    if old_genres is None:
                                        params["genre_mapper"][new_genre] = old_genres
                                    else:
                                        for old_genre in util.get_list(old_genres):
                                            if old_genre == new_genre:
                                                logger.error("Config Error: genres cannot be mapped to themselves")
                                            else:
                                                params["genre_mapper"][old_genre] = new_genre
                            else:
                                logger.error("Config Error: genre_mapper is blank")
                        if "genre_collections" in lib["operations"]:
                            params["genre_collections"] = {
                                "exclude_genres": [],
                                "dictionary_variables": {},
                                "title_format": "Top <<genre>> <<library_type>>s",
                                "template": {"smart_filter": {"limit": 50, "sort_by": "critic_rating.desc", "all": {"genre": "<<genre>>"}}}
                            }
                            if lib["operations"]["genre_collections"] and isinstance(lib["operations"]["genre_collections"], dict):
                                params["genre_collections"]["exclude_genres"] = check_for_attribute(lib["operations"]["genre_collections"], "exclude_genres", var_type="comma_list", default_is_none=True, save=False)
                                title_format = check_for_attribute(lib["operations"]["genre_collections"], "title_format", default=params["genre_collections"]["title_format"], save=False)
                                if "<<genre>>" in title_format:
                                    params["genre_collections"]["title_format"] = title_format
                                else:
                                    logger.error(f"Config Error: using default title_format. <<genre>> not in title_format attribute: {title_format} ")
                                if "dictionary_variables" in lib["operations"]["genre_collections"] and lib["operations"]["genre_collections"]["dictionary_variables"] and isinstance(lib["operations"]["genre_collections"]["dictionary_variables"], dict):
                                    for key, value in lib["operations"]["genre_collections"]["dictionary_variables"].items():
                                        if isinstance(value, dict):
                                            params["genre_collections"]["dictionary_variables"][key] = value
                                        else:
                                            logger.warning(f"Config Warning: genre_collections dictionary_variables {key} must be a dictionary")
                                if "template" in lib["operations"]["genre_collections"] and lib["operations"]["genre_collections"]["template"] and isinstance(lib["operations"]["genre_collections"]["template"], dict):
                                    params["genre_collections"]["template"] = lib["operations"]["genre_collections"]["template"]
                                else:
                                    logger.warning("Config Warning: Using default template for genre_collections")
                            else:
                                logger.error("Config Error: genre_collections blank using default settings")
                    else:
                        logger.error("Config Error: operations must be a dictionary")

                def error_check(attr, service):
                    err = f"Config Error: {attr} cannot be {params[attr]} without a successful {service} Connection"
                    params[attr] = None
                    self.errors.append(err)
                    logger.error(err)

                if self.OMDb is None and params["mass_genre_update"] == "omdb":
                    error_check("mass_genre_update", "OMDb")
                if self.OMDb is None and params["mass_audience_rating_update"] == "omdb":
                    error_check("mass_audience_rating_update", "OMDb")
                if self.OMDb is None and params["mass_critic_rating_update"] == "omdb":
                    error_check("mass_critic_rating_update", "OMDb")
                if self.OMDb is None and params["mass_content_rating_update"] == "omdb":
                    error_check("mass_content_rating_update", "OMDb")
                if not self.Mdblist.has_key and params["mass_audience_rating_update"] in util.mdb_types:
                    error_check("mass_audience_rating_update", "MdbList API")
                if not self.Mdblist.has_key and params["mass_critic_rating_update"] in util.mdb_types:
                    error_check("mass_critic_rating_update", "MdbList API")
                if not self.Mdblist.has_key and params["mass_content_rating_update"] in ["mdb", "mdb_commonsense"]:
                    error_check("mass_content_rating_update", "MdbList API")
                if self.Trakt is None and params["mass_trakt_rating_update"]:
                    error_check("mass_trakt_rating_update", "Trakt")

                try:
                    if lib and "metadata_path" in lib:
                        params["metadata_path"] = []
                        if lib["metadata_path"] is None:
                            raise Failed("Config Error: metadata_path attribute is blank")
                        paths_to_check = lib["metadata_path"] if isinstance(lib["metadata_path"], list) else [lib["metadata_path"]]
                        for path in paths_to_check:
                            if isinstance(path, dict):
                                def check_dict(attr, name):
                                    if attr in path:
                                        if path[attr] is None:
                                            err = f"Config Error: metadata_path {attr} is blank"
                                            self.errors.append(err)
                                            logger.error(err)
                                        else:
                                            params["metadata_path"].append((name, path[attr]))
                                check_dict("url", "URL")
                                check_dict("git", "Git")
                                check_dict("repo", "Repo")
                                check_dict("file", "File")
                                check_dict("folder", "Folder")
                            else:
                                params["metadata_path"].append(("File", path))
                    else:
                        params["metadata_path"] = [("File", os.path.join(default_dir, f"{library_name}.yml"))]
                    params["default_dir"] = default_dir

                    params["skip_library"] = False
                    if lib and "schedule" in lib and not self.requested_libraries and not self.ignore_schedules:
                        if not lib["schedule"]:
                            raise Failed(f"Config Error: schedule attribute is blank")
                        else:
                            logger.debug(f"Value: {lib['schedule']}")
                            try:
                                util.schedule_check("schedule", lib["schedule"], current_time, self.run_hour)
                            except NotScheduled:
                                params["skip_library"] = True

                    logger.info("")
                    util.separator("Plex Configuration", space=False, border=False)
                    params["plex"] = {
                        "url": check_for_attribute(lib, "url", parent="plex", var_type="url", default=self.general["plex"]["url"], req_default=True, save=False),
                        "token": check_for_attribute(lib, "token", parent="plex", default=self.general["plex"]["token"], req_default=True, save=False),
                        "timeout": check_for_attribute(lib, "timeout", parent="plex", var_type="int", default=self.general["plex"]["timeout"], save=False),
                        "clean_bundles": check_for_attribute(lib, "clean_bundles", parent="plex", var_type="bool", default=self.general["plex"]["clean_bundles"], save=False),
                        "empty_trash": check_for_attribute(lib, "empty_trash", parent="plex", var_type="bool", default=self.general["plex"]["empty_trash"], save=False),
                        "optimize": check_for_attribute(lib, "optimize", parent="plex", var_type="bool", default=self.general["plex"]["optimize"], save=False)
                    }
                    library = Plex(self, params)
                    logger.info(f"{display_name} Library Connection Successful")
                except Failed as e:
                    self.errors.append(e)
                    util.print_stacktrace()
                    util.print_multiline(e, error=True)
                    logger.info("")
                    logger.info(f"{display_name} Library Connection Failed")
                    continue
                try:
                    logger.info("")
                    util.separator("Scanning Metadata Files", space=False, border=False)
                    library.scan_metadata_files()
                except Failed as e:
                    self.errors.append(e)
                    util.print_stacktrace()
                    util.print_multiline(e, error=True)
                    logger.info("")
                    logger.info(f"{display_name} Metadata Failed to Load")
                    continue

                if self.general["radarr"]["url"] or (lib and "radarr" in lib):
                    logger.info("")
                    util.separator("Radarr Configuration", space=False, border=False)
                    logger.info("")
                    logger.info(f"Connecting to {display_name} library's Radarr...")
                    logger.info("")
                    try:
                        library.Radarr = Radarr(self, library, {
                            "url": check_for_attribute(lib, "url", parent="radarr", var_type="url", default=self.general["radarr"]["url"], req_default=True, save=False),
                            "token": check_for_attribute(lib, "token", parent="radarr", default=self.general["radarr"]["token"], req_default=True, save=False),
                            "add_missing": check_for_attribute(lib, "add_missing", parent="radarr", var_type="bool", default=self.general["radarr"]["add_missing"], save=False),
                            "add_existing": check_for_attribute(lib, "add_existing", parent="radarr", var_type="bool", default=self.general["radarr"]["add_existing"], save=False),
                            "root_folder_path": check_for_attribute(lib, "root_folder_path", parent="radarr", default=self.general["radarr"]["root_folder_path"], req_default=True, save=False),
                            "monitor": check_for_attribute(lib, "monitor", parent="radarr", var_type="bool", default=self.general["radarr"]["monitor"], save=False),
                            "availability": check_for_attribute(lib, "availability", parent="radarr", test_list=radarr.availability_descriptions, default=self.general["radarr"]["availability"], save=False),
                            "quality_profile": check_for_attribute(lib, "quality_profile", parent="radarr", default=self.general["radarr"]["quality_profile"], req_default=True, save=False),
                            "tag": check_for_attribute(lib, "tag", parent="radarr", var_type="lower_list", default=self.general["radarr"]["tag"], default_is_none=True, save=False),
                            "search": check_for_attribute(lib, "search", parent="radarr", var_type="bool", default=self.general["radarr"]["search"], save=False),
                            "radarr_path": check_for_attribute(lib, "radarr_path", parent="radarr", default=self.general["radarr"]["radarr_path"], default_is_none=True, save=False),
                            "plex_path": check_for_attribute(lib, "plex_path", parent="radarr", default=self.general["radarr"]["plex_path"], default_is_none=True, save=False)
                        })
                    except Failed as e:
                        self.errors.append(e)
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
                    try:
                        library.Sonarr = Sonarr(self, library, {
                            "url": check_for_attribute(lib, "url", parent="sonarr", var_type="url", default=self.general["sonarr"]["url"], req_default=True, save=False),
                            "token": check_for_attribute(lib, "token", parent="sonarr", default=self.general["sonarr"]["token"], req_default=True, save=False),
                            "add_missing": check_for_attribute(lib, "add_missing", parent="sonarr", var_type="bool", default=self.general["sonarr"]["add_missing"], save=False),
                            "add_existing": check_for_attribute(lib, "add_existing", parent="sonarr", var_type="bool", default=self.general["sonarr"]["add_existing"], save=False),
                            "root_folder_path": check_for_attribute(lib, "root_folder_path", parent="sonarr", default=self.general["sonarr"]["root_folder_path"], req_default=True, save=False),
                            "monitor": check_for_attribute(lib, "monitor", parent="sonarr", test_list=sonarr.monitor_descriptions, default=self.general["sonarr"]["monitor"], save=False),
                            "quality_profile": check_for_attribute(lib, "quality_profile", parent="sonarr", default=self.general["sonarr"]["quality_profile"], req_default=True, save=False),
                            "language_profile": check_for_attribute(lib, "language_profile", parent="sonarr", default=self.general["sonarr"]["language_profile"], save=False) if self.general["sonarr"]["language_profile"] else check_for_attribute(lib, "language_profile", parent="sonarr", default_is_none=True, save=False),
                            "series_type": check_for_attribute(lib, "series_type", parent="sonarr", test_list=sonarr.series_type_descriptions, default=self.general["sonarr"]["series_type"], save=False),
                            "season_folder": check_for_attribute(lib, "season_folder", parent="sonarr", var_type="bool", default=self.general["sonarr"]["season_folder"], save=False),
                            "tag": check_for_attribute(lib, "tag", parent="sonarr", var_type="lower_list", default=self.general["sonarr"]["tag"], default_is_none=True, save=False),
                            "search": check_for_attribute(lib, "search", parent="sonarr", var_type="bool", default=self.general["sonarr"]["search"], save=False),
                            "cutoff_search": check_for_attribute(lib, "cutoff_search", parent="sonarr", var_type="bool", default=self.general["sonarr"]["cutoff_search"], save=False),
                            "sonarr_path": check_for_attribute(lib, "sonarr_path", parent="sonarr", default=self.general["sonarr"]["sonarr_path"], default_is_none=True, save=False),
                            "plex_path": check_for_attribute(lib, "plex_path", parent="sonarr", default=self.general["sonarr"]["plex_path"], default_is_none=True, save=False)
                        })
                    except Failed as e:
                        self.errors.append(e)
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
                    try:
                        library.Tautulli = Tautulli(self, library, {
                            "url": check_for_attribute(lib, "url", parent="tautulli", var_type="url", default=self.general["tautulli"]["url"], req_default=True, save=False),
                            "apikey": check_for_attribute(lib, "apikey", parent="tautulli", default=self.general["tautulli"]["apikey"], req_default=True, save=False)
                        })
                    except Failed as e:
                        self.errors.append(e)
                        util.print_stacktrace()
                        util.print_multiline(e, error=True)
                        logger.info("")
                    logger.info(f"{display_name} library's Tautulli Connection {'Failed' if library.Tautulli is None else 'Successful'}")

                library.Webhooks = Webhooks(self, {"error_webhooks": library.error_webhooks}, library=library, notifiarr=self.NotifiarrFactory)

                logger.info("")
                self.libraries.append(library)

            util.separator()

            if len(self.libraries) > 0:
                logger.info(f"{len(self.libraries)} Plex Library Connection{'s' if len(self.libraries) > 1 else ''} Successful")
            else:
                raise Failed("Plex Error: No Plex libraries were connected to")

            util.separator()

            if self.errors:
                self.notify(self.errors)
        except Exception as e:
            self.notify(e)
            raise

    def notify(self, text, server=None, library=None, collection=None, playlist=None, critical=True):
        for error in util.get_list(text, split=False):
            try:
                self.Webhooks.error_hooks(error, server=server, library=library, collection=collection, playlist=playlist, critical=critical)
            except Failed as e:
                util.print_stacktrace()
                logger.error(f"Webhooks Error: {e}")

    def get_html(self, url, headers=None, params=None):
        return html.fromstring(self.get(url, headers=headers, params=params).content)

    def get_json(self, url, json=None, headers=None, params=None):
        return self.get(url, json=json, headers=headers, params=params).json()

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def get(self, url, json=None, headers=None, params=None):
        return self.session.get(url, json=json, headers=headers, params=params)

    def get_image_encoded(self, url):
        return base64.b64encode(self.get(url).content).decode('utf-8')

    def post_html(self, url, data=None, json=None, headers=None):
        return html.fromstring(self.post(url, data=data, json=json, headers=headers).content)

    def post_json(self, url, data=None, json=None, headers=None):
        return self.post(url, data=data, json=json, headers=headers).json()

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def post(self, url, data=None, json=None, headers=None):
        return self.session.post(url, data=data, json=json, headers=headers)
