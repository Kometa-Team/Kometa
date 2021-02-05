import glob, json, logging, os, re, requests
from datetime import datetime, timedelta
from modules import util
from modules.anidb import AniDBAPI
from modules.cache import Cache
from modules.imdb import IMDbAPI
from modules.plex import PlexAPI
from modules.mal import MyAnimeListAPI
from modules.mal import MyAnimeListIDList
from modules.tmdb import TMDbAPI
from modules.trakt import TraktAPI
from modules.tvdb import TVDbAPI
from modules.util import Failed
from ruamel import yaml

logger = logging.getLogger("Plex Meta Manager")

class Config:
    def __init__(self, default_dir, config_path=None):
        logger.info("Locating config...")
        if config_path and os.path.exists(config_path):                     self.config_path = os.path.abspath(config_path)
        elif config_path and not os.path.exists(config_path):               raise Failed("Config Error: config not found at {}".format(os.path.abspath(config_path)))
        elif os.path.exists(os.path.join(default_dir, "config.yml")):       self.config_path = os.path.abspath(os.path.join(default_dir, "config.yml"))
        else:                                                               raise Failed("Config Error: config not found at {}".format(os.path.abspath(default_dir)))
        logger.info("Using {} as config".format(self.config_path))

        yaml.YAML().allow_duplicate_keys = True
        try:                                                                self.data, ind, bsi = yaml.util.load_yaml_guess_indent(open(self.config_path))
        except yaml.scanner.ScannerError as e:                              raise Failed("YAML Error: {}".format(str(e).replace("\n", "\n|\t      ")))

        def check_for_attribute(data, attribute, parent=None, test_list=None, options="", default=None, do_print=True, default_is_none=False, var_type="str", throw=False, save=True):
            message = ""
            endline = ""
            data = data if parent is None else data[parent]
            text = "{} attribute".format(attribute) if parent is None else "{} sub-attribute {}".format(parent, attribute)
            if data is None or attribute not in data:
                message = "Config Error: {} not found".format(text)
                if parent and save is True:
                    new_config, ind, bsi = yaml.util.load_yaml_guess_indent(open(self.config_path))
                    endline = "\n| {} sub-attribute {} added to config".format(parent, attribute)
                    if parent not in new_config:                                        new_config = {parent: {attribute: default}}
                    elif not new_config[parent]:                                        new_config[parent] = {attribute: default}
                    elif attribute not in new_config[parent]:                           new_config[parent][attribute] = default
                    else:                                                               endLine = ""
                    yaml.round_trip_dump(new_config, open(self.config_path, "w"), indent=ind, block_seq_indent=bsi)
            elif not data[attribute] and data[attribute] != False:              message = "Config Error: {} is blank".format(text)
            elif var_type == "bool":
                if isinstance(data[attribute], bool):                               return data[attribute]
                else:                                                               message = "Config Error: {} must be either true or false".format(text)
            elif var_type == "int":
                if isinstance(data[attribute], int) and data[attribute] > 0:        return data[attribute]
                else:                                                               message = "Config Error: {} must an integer > 0".format(text)
            elif var_type == "path":
                if os.path.exists(os.path.abspath(data[attribute])):                return data[attribute]
                else:                                                               message = "Config Error: {} could not be found".format(text)
                if default and os.path.exists(os.path.abspath(default)):
                    return default
                elif default:
                    default = None
                    default_is_none = True
                    message = "Config Error: neither {} or the default path {} could be found".format(data[attribute], default)
            elif test_list is None or data[attribute] in test_list:             return data[attribute]
            else:                                                               message = "Config Error: {}: {} is an invalid input".format(text, data[attribute])
            if default is not None or default_is_none:
                message = message + " using {} as default".format(default)
            message = message + endline
            if (default is None and not default_is_none) or throw:
                if len(options) > 0:
                    message = message + "\n" + options
                raise Failed(message)
            if do_print:
                util.print_multiline(message)
                if attribute in data and data[attribute] and test_list is not None and data[attribute] not in test_list:
                    util.print_multiline(options)
            return default

        self.general = {}
        self.general["cache"] = check_for_attribute(self.data, "cache", parent="cache", options="| \ttrue (Create a cache to store ids)\n| \tfalse (Do not create a cache to store ids)", var_type="bool", default=True) if "cache" in self.data else True
        self.general["cache_expiration"] = check_for_attribute(self.data, "cache_expiration", parent="cache", var_type="int", default=60) if "cache" in self.data else 60
        if self.general["cache"]:
            util.seperator()
            self.Cache = Cache(self.config_path, self.general["cache_expiration"])
        else:
            self.Cache = None

        util.seperator()

        self.TMDb = None
        if "tmdb" in self.data:
            logger.info("Connecting to TMDb...")
            self.tmdb = {}
            self.tmdb["apikey"] = check_for_attribute(self.data, "apikey", parent="tmdb", throw=True)
            self.tmdb["language"] = check_for_attribute(self.data, "language", parent="tmdb", default="en")
            self.TMDb = TMDbAPI(self.tmdb)
            logger.info("TMDb Connection {}".format("Failed" if self.TMDb is None else "Successful"))
        else:
            raise Failed("Config Error: tmdb attribute not found")

        util.seperator()

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
            logger.info("Trakt Connection {}".format("Failed" if self.Trakt is None else "Successful"))
        else:
            logger.warning("trakt attribute not found")

        util.seperator()

        self.MyAnimeList = None
        self.MyAnimeListIDList = MyAnimeListIDList()
        if "mal" in self.data:
            logger.info("Connecting to My Anime List...")
            self.mal = {}
            try:
                self.mal["client_id"] = check_for_attribute(self.data, "client_id", parent="mal", throw=True)
                self.mal["client_secret"] = check_for_attribute(self.data, "client_secret", parent="mal", throw=True)
                self.mal["config_path"] = self.config_path
                authorization = self.data["mal"]["authorization"] if "authorization" in self.data["mal"] and self.data["mal"]["authorization"] else None
                self.MyAnimeList = MyAnimeListAPI(self.mal, self.MyAnimeListIDList, authorization)
            except Failed as e:
                logger.error(e)
            logger.info("My Anime List Connection {}".format("Failed" if self.Trakt is None else "Successful"))
        else:
            logger.warning("mal attribute not found")

        self.TVDb = TVDbAPI(Cache=self.Cache, TMDb=self.TMDb, Trakt=self.Trakt)
        self.IMDb = IMDbAPI(Cache=self.Cache, TMDb=self.TMDb, Trakt=self.Trakt, TVDb=self.TVDb) if self.TMDb or self.Trakt else None
        self.AniDB = AniDBAPI(Cache=self.Cache, TMDb=self.TMDb, Trakt=self.Trakt)

        self.general["plex"] = {}
        self.general["plex"]["url"] = check_for_attribute(self.data, "url", parent="plex", default_is_none=True) if "plex" in self.data else None
        self.general["plex"]["token"] = check_for_attribute(self.data, "token", parent="plex", default_is_none=True) if "plex" in self.data else None
        self.general["plex"]["asset_directory"] = check_for_attribute(self.data, "asset_directory", parent="plex", var_type="path", default=os.path.join(default_dir, "assets")) if "plex" in self.data else os.path.join(default_dir, "assets")
        self.general["plex"]["sync_mode"] = check_for_attribute(self.data, "sync_mode", parent="plex", default="append", test_list=["append", "sync"], options="| \tappend (Only Add Items to the Collection)\n| \tsync (Add & Remove Items from the Collection)") if "plex" in self.data else "append"

        self.general["radarr"] = {}
        self.general["radarr"]["url"] = check_for_attribute(self.data, "url", parent="radarr", default_is_none=True) if "radarr" in self.data else None
        self.general["radarr"]["version"] = check_for_attribute(self.data, "version", parent="radarr", test_list=["v2", "v3"], options="| \tv2 (For Radarr 0.2)\n| \tv3 (For Radarr 3.0)", default="v2") if "radarr" in self.data else "v2"
        self.general["radarr"]["token"] = check_for_attribute(self.data, "token", parent="radarr", default_is_none=True) if "radarr" in self.data else None
        self.general["radarr"]["quality_profile"] = check_for_attribute(self.data, "quality_profile", parent="radarr", default_is_none=True) if "radarr" in self.data else None
        self.general["radarr"]["root_folder_path"] = check_for_attribute(self.data, "root_folder_path", parent="radarr", default_is_none=True) if "radarr" in self.data else None
        self.general["radarr"]["add"] = check_for_attribute(self.data, "add", parent="radarr", var_type="bool", default=False) if "radarr" in self.data else False
        self.general["radarr"]["search"] = check_for_attribute(self.data, "search", parent="radarr", var_type="bool", default=False) if "radarr" in self.data else False

        self.general["sonarr"] = {}
        self.general["sonarr"]["url"] = check_for_attribute(self.data, "url", parent="sonarr", default_is_none=True) if "sonarr" in self.data else None
        self.general["sonarr"]["token"] = check_for_attribute(self.data, "token", parent="sonarr", default_is_none=True) if "sonarr" in self.data else None
        self.general["sonarr"]["version"] = check_for_attribute(self.data, "version", parent="sonarr", test_list=["v2", "v3"], options="| \tv2 (For Sonarr 0.2)\n| \tv3 (For Sonarr 3.0)", default="v2") if "sonarr" in self.data else "v2"
        self.general["sonarr"]["quality_profile"] = check_for_attribute(self.data, "quality_profile", parent="sonarr", default_is_none=True) if "sonarr" in self.data else None
        self.general["sonarr"]["root_folder_path"] = check_for_attribute(self.data, "root_folder_path", parent="sonarr", default_is_none=True) if "sonarr" in self.data else None
        self.general["sonarr"]["add"] = check_for_attribute(self.data, "add", parent="sonarr", var_type="bool", default=False) if "sonarr" in self.data else False
        self.general["sonarr"]["search"] = check_for_attribute(self.data, "search", parent="sonarr", var_type="bool", default=False) if "sonarr" in self.data else False

        self.general["tautulli"] = {}
        self.general["tautulli"]["url"] = check_for_attribute(self.data, "url", parent="tautulli", default_is_none=True) if "tautulli" in self.data else None
        self.general["tautulli"]["apikey"] = check_for_attribute(self.data, "apikey", parent="tautulli", default_is_none=True) if "tautulli" in self.data else None

        util.seperator()

        logger.info("Connecting to Plex Libraries...")

        self.libraries = []
        libs = check_for_attribute(self.data, "libraries", throw=True)
        for lib in libs:
            util.seperator()
            params = {}
            if "library_name" in libs[lib] and libs[lib]["library_name"]:
                params["name"] = str(libs[lib]["library_name"])
                logger.info("Connecting to {} ({}) Library...".format(params["name"], lib))
            else:
                params["name"] = str(lib)
                logger.info("Connecting to {} Library...".format(params["name"]))
            default_lib = os.path.join(default_dir, "{}.yml".format(lib))
            try:
                if "metadata_path" in libs[lib]:
                    if libs[lib]["metadata_path"]:
                        if os.path.exists(libs[lib]["metadata_path"]):              params["metadata_path"] = libs[lib]["metadata_path"]
                        else:                                                       raise Failed("metadata_path not found at {}".format(libs[lib]["metadata_path"]))
                    else:                                                       raise Failed("metadata_path attribute is blank")
                else:
                    if os.path.exists(default_lib):                             params["metadata_path"] = os.path.abspath(default_lib)
                    else:                                                       raise Failed("default metadata_path not found at {}".format(os.path.abspath(os.path.join(default_dir, "{}.yml".format(params["name"])))))

                if "library_type" in libs[lib]:
                    if libs[lib]["library_type"]:
                        if libs[lib]["library_type"] in ["movie", "show"]:          params["library_type"] = libs[lib]["library_type"]
                        else:                                                       raise Failed("library_type attribute must be either 'movie' or 'show'")
                    else:                                                       raise Failed("library_type attribute is blank")
                else:                                                       raise Failed("library_type attribute is required")

                params["plex"] = {}
                if "plex" in libs[lib] and libs[lib]["plex"] and "url" in libs[lib]["plex"]:
                    if libs[lib]["plex"]["url"]:                                params["plex"]["url"] = libs[lib]["plex"]["url"]
                    else:                                                       raise Failed("url library attribute is blank")
                elif self.general["plex"]["url"]:                           params["plex"]["url"] = self.general["plex"]["url"]
                else:                                                       raise Failed("url attribute must be set under plex or under this specific Library")

                if "plex" in libs[lib] and libs[lib]["plex"] and "token" in libs[lib]["plex"]:
                    if libs[lib]["plex"]["token"]:                              params["plex"]["token"] = libs[lib]["plex"]["token"]
                    else:                                                       raise Failed("token library attribute is blank")
                elif self.general["plex"]["token"]:                         params["plex"]["token"] = self.general["plex"]["token"]
                else:                                                       raise Failed("token attribute must be set under plex or under this specific Library")
            except Failed as e:
                logger.error("Config Error: Skipping {} Library {}".format(str(lib), e))
                continue

            params["asset_directory"] = None

            if "plex" in libs[lib] and "asset_directory" in libs[lib]["plex"]:
                if libs[lib]["plex"]["asset_directory"]:
                    if os.path.exists(libs[lib]["plex"]["asset_directory"]):
                        params["asset_directory"] = libs[lib]["plex"]["asset_directory"]
                    else:
                        logger.warning("Config Warning: Assets will not be used asset_directory not found at {}".format(libs[lib]["plex"]["asset_directory"]))
                else:
                   logger.warning("Config Warning: Assets will not be used asset_directory library attribute is blank")
            elif self.general["plex"]["asset_directory"]:
                params["asset_directory"] = self.general["plex"]["asset_directory"]
            else:
                logger.warning("Config Warning: Assets will not be used asset_directory attribute must be set under config or under this specific Library")

            params["sync_mode"] = self.general["plex"]["sync_mode"]
            if "plex" in libs[lib] and "sync_mode" in libs[lib]["plex"]:
                if libs[lib]["plex"]["sync_mode"]:
                    if libs[lib]["plex"]["sync_mode"] in ["append", "sync"]:
                        params["sync_mode"] = libs[lib]["plex"]["sync_mode"]
                    else:
                        logger.warning("Config Warning: sync_mode attribute must be either 'append' or 'sync' using general value: {}".format(self.general["plex"]["sync_mode"]))
                else:
                    logger.warning("Config Warning: sync_mode attribute is blank using general value: {}".format(self.general["plex"]["sync_mode"]))

            params["tmdb"] = self.TMDb
            params["tvdb"] = self.TVDb

            params["radarr"] = self.general["radarr"].copy()
            if "radarr" in libs[lib] and libs[lib]["radarr"]:
                if "url" in libs[lib]["radarr"]:
                    if libs[lib]["radarr"]["url"]:
                        params["radarr"]["url"] = libs[lib]["radarr"]["url"]
                    else:
                        logger.warning("Config Warning: radarr sub-attribute url is blank using general value: {}".format(self.general["radarr"]["url"]))

                if "token" in libs[lib]["radarr"]:
                    if libs[lib]["radarr"]["token"]:
                        params["radarr"]["token"] = libs[lib]["radarr"]["token"]
                    else:
                        logger.warning("Config Warning: radarr sub-attribute token is blank using general value: {}".format(self.general["radarr"]["token"]))

                if "version" in libs[lib]["radarr"]:
                    if libs[lib]["radarr"]["version"]:
                        if libs[lib]["radarr"]["version"] in ["v2", "v3"]:
                            params["radarr"]["version"] = libs[lib]["radarr"]["version"]
                        else:
                            logger.warning("Config Warning: radarr sub-attribute version must be either 'v2' or 'v3' using general value: {}".format(self.general["radarr"]["version"]))
                    else:
                        logger.warning("Config Warning: radarr sub-attribute version is blank using general value: {}".format(self.general["radarr"]["version"]))

                if "quality_profile" in libs[lib]["radarr"]:
                    if libs[lib]["radarr"]["quality_profile"]:
                        params["radarr"]["quality_profile"] = libs[lib]["radarr"]["quality_profile"]
                    else:
                        logger.warning("Config Warning: radarr sub-attribute quality_profile is blank using general value: {}".format(self.general["radarr"]["quality_profile"]))

                if "root_folder_path" in libs[lib]["radarr"]:
                    if libs[lib]["radarr"]["root_folder_path"]:
                        params["radarr"]["root_folder_path"] = libs[lib]["radarr"]["root_folder_path"]
                    else:
                        logger.warning("Config Warning: radarr sub-attribute root_folder_path is blank using general value: {}".format(self.general["radarr"]["root_folder_path"]))

                if "add" in libs[lib]["radarr"]:
                    if libs[lib]["radarr"]["add"]:
                        if isinstance(libs[lib]["radarr"]["add"], bool):
                            params["radarr"]["add"] = libs[lib]["radarr"]["add"]
                        else:
                            logger.warning("Config Warning: radarr sub-attribute add must be either true or false using general value: {}".format(self.general["radarr"]["add"]))
                    else:
                        logger.warning("Config Warning: radarr sub-attribute add is blank using general value: {}".format(self.general["radarr"]["add"]))

                if "search" in libs[lib]["radarr"]:
                    if libs[lib]["radarr"]["search"]:
                        if isinstance(libs[lib]["radarr"]["search"], bool):
                            params["radarr"]["search"] = libs[lib]["radarr"]["search"]
                        else:
                            logger.warning("Config Warning: radarr sub-attribute search must be either true or false using general value: {}".format(self.general["radarr"]["search"]))
                    else:
                        logger.warning("Config Warning: radarr sub-attribute search is blank using general value: {}".format(self.general["radarr"]["search"]))

            if not params["radarr"]["url"] or not params["radarr"]["token"] or not params["radarr"]["quality_profile"] or not params["radarr"]["root_folder_path"]:
                params["radarr"] = None

            params["sonarr"] = self.general["sonarr"].copy()
            if "sonarr" in libs[lib] and libs[lib]["sonarr"]:
                if "url" in libs[lib]["sonarr"]:
                    if libs[lib]["sonarr"]["url"]:
                        params["sonarr"]["url"] = libs[lib]["sonarr"]["url"]
                    else:
                        logger.warning("Config Warning: sonarr sub-attribute url is blank using general value: {}".format(self.general["sonarr"]["url"]))

                if "token" in libs[lib]["sonarr"]:
                    if libs[lib]["sonarr"]["token"]:
                        params["sonarr"]["token"] = libs[lib]["sonarr"]["token"]
                    else:
                        logger.warning("Config Warning: sonarr sub-attribute token is blank using general value: {}".format(self.general["sonarr"]["token"]))

                if "version" in libs[lib]["sonarr"]:
                    if libs[lib]["sonarr"]["version"]:
                        if libs[lib]["sonarr"]["version"] in ["v2", "v3"]:
                            params["sonarr"]["version"] = libs[lib]["sonarr"]["version"]
                        else:
                            logger.warning("Config Warning: sonarr sub-attribute version must be either 'v2' or 'v3' using general value: {}".format(self.general["sonarr"]["version"]))
                    else:
                        logger.warning("Config Warning: sonarr sub-attribute version is blank using general value: {}".format(self.general["sonarr"]["version"]))

                if "quality_profile" in libs[lib]["sonarr"]:
                    if libs[lib]["sonarr"]["quality_profile"]:
                        params["sonarr"]["quality_profile"] = libs[lib]["sonarr"]["quality_profile"]
                    else:
                        logger.warning("Config Warning: sonarr sub-attribute quality_profile is blank using general value: {}".format(self.general["sonarr"]["quality_profile"]))

                if "root_folder_path" in libs[lib]["sonarr"]:
                    if libs[lib]["sonarr"]["root_folder_path"]:
                        params["sonarr"]["root_folder_path"] = libs[lib]["sonarr"]["root_folder_path"]
                    else:
                        logger.warning("Config Warning: sonarr sub-attribute root_folder_path is blank using general value: {}".format(self.general["sonarr"]["root_folder_path"]))

                if "add" in libs[lib]["sonarr"]:
                    if libs[lib]["sonarr"]["add"]:
                        if isinstance(libs[lib]["sonarr"]["add"], bool):
                            params["sonarr"]["add"] = libs[lib]["sonarr"]["add"]
                        else:
                            logger.warning("Config Warning: sonarr sub-attribute add must be either true or false using general value: {}".format(self.general["sonarr"]["add"]))
                    else:
                        logger.warning("Config Warning: sonarr sub-attribute add is blank using general value: {}".format(self.general["sonarr"]["add"]))

                if "search" in libs[lib]["sonarr"]:
                    if libs[lib]["sonarr"]["search"]:
                        if isinstance(libs[lib]["sonarr"]["search"], bool):
                            params["sonarr"]["search"] = libs[lib]["sonarr"]["search"]
                        else:
                            logger.warning("Config Warning: sonarr sub-attribute search must be either true or false using general value: {}".format(self.general["sonarr"]["search"]))
                    else:
                        logger.warning("Config Warning: sonarr sub-attribute search is blank using general value: {}".format(self.general["sonarr"]["search"]))

            if not params["sonarr"]["url"] or not params["sonarr"]["token"] or not params["sonarr"]["quality_profile"] or not params["sonarr"]["root_folder_path"] or params["library_type"] == "movie":
                params["sonarr"] = None


            params["tautulli"] = self.general["tautulli"].copy()
            if "tautulli" in libs[lib] and libs[lib]["tautulli"]:
                if "url" in libs[lib]["tautulli"]:
                    if libs[lib]["tautulli"]["url"]:
                        params["tautulli"]["url"] = libs[lib]["tautulli"]["url"]
                    else:
                        logger.warning("Config Warning: tautulli sub-attribute url is blank using general value: {}".format(self.general["tautulli"]["url"]))

                if "apikey" in libs[lib]["tautulli"]:
                    if libs[lib]["tautulli"]["apikey"]:
                        params["tautulli"]["apikey"] = libs[lib]["tautulli"]["apikey"]
                    else:
                        logger.warning("Config Warning: tautulli sub-attribute apikey is blank using general value: {}".format(self.general["tautulli"]["apikey"]))

            if not params["tautulli"]["url"] or not params["tautulli"]["apikey"] :
                params["tautulli"] = None

            try:
                self.libraries.append(PlexAPI(params))
                logger.info("{} Library Connection Successful".format(params["name"]))
            except Failed as e:
                logger.error(e)
                logger.info("{} Library Connection Failed".format(params["name"]))
                continue

        util.seperator()

        if len(self.libraries) > 0:
            logger.info("{} Plex Library Connection{} Successful".format(len(self.libraries), "s" if len(self.libraries) > 1 else ""))
        else:
            raise Failed("Plex Error: No Plex libraries were found")

        util.seperator()

    def update_libraries(self):
        for library in self.libraries:
            logger.info("")
            util.seperator("{} Library".format(library.name))
            try:                        library.update_metadata(self.TMDb)
            except Failed as e:         logger.error(e)
            logger.info("")
            util.seperator("{} Library Collections".format(library.name))
            collections = library.collections
            if collections:
                logger.info("")
                util.seperator("Mapping {} Library".format(library.name))
                logger.info("")
                movie_map, show_map = self.map_guids(library)
                for c in collections:
                    try:
                        logger.info("")
                        util.seperator("{} Collection".format(c))
                        logger.info("")

                        map = {}
                        details = {}
                        methods = []
                        filters = []
                        posters_found = []
                        backgrounds_found = []
                        collectionless = "plex_collectionless" in collections[c]
                        skip_collection = True

                        if "schedule" not in collections[c]:
                            skip_collection = False
                        elif not collections[c]["schedule"]:
                            logger.error("Collection Error: schedule attribute is blank. Running daily")
                            skip_collection = False
                        else:
                            schedule_list = util.get_list(collections[c]["schedule"])
                            current_time = datetime.now()
                            next_month = current_time.replace(day=28) + timedelta(days=4)
                            last_day = next_month - timedelta(days=next_month.day)
                            for schedule in schedule_list:
                                run_time = str(schedule).lower()
                                if run_time.startswith("day") or run_time.startswith("daily"):
                                    skip_collection = False
                                    break
                                if run_time.startswith("week") or run_time.startswith("month") or run_time.startswith("year"):
                                    match = re.search("\\(([^)]+)\\)", run_time)
                                    if match:
                                        param = match.group(1)
                                        if run_time.startswith("week"):
                                            if param.lower() in util.days_alias:
                                                weekday = util.days_alias[param.lower()]
                                                logger.info("Scheduled weekly on {}".format(util.pretty_days[weekday]))
                                                if weekday == current_time.weekday():
                                                    skip_collection = False
                                                    break
                                            else:
                                                logger.error("Collection Error: weekly schedule attribute {} invalid must be a day of the weeek i.e. weekly(Monday)".format(schedule))
                                        elif run_time.startswith("month"):
                                            try:
                                                if 1 <= int(param) <= 31:
                                                    logger.info("Scheduled monthly on the {}".format(util.make_ordinal(param)))
                                                    if current_time.day == int(param) or (current_time.day == last_day.day and int(param) > last_day.day):
                                                        skip_collection = False
                                                        break
                                                else:
                                                    logger.error("Collection Error: monthly schedule attribute {} invalid must be between 1 and 31".format(schedule))
                                            except ValueError:
                                                logger.error("Collection Error: monthly schedule attribute {} invalid must be an integer".format(schedule))
                                        elif run_time.startswith("year"):
                                            match = re.match("^(1[0-2]|0?[1-9])/(3[01]|[12][0-9]|0?[1-9])$", param)
                                            if match:
                                                month = int(match.group(1))
                                                day = int(match.group(2))
                                                logger.info("Scheduled yearly on {} {}".format(util.pretty_months[month], util.make_ordinal(day)))
                                                if current_time.month == month and (current_time.day == day or (current_time.day == last_day.day and day > last_day.day)):
                                                    skip_collection = False
                                                    break
                                            else:
                                                logger.error("Collection Error: yearly schedule attribute {} invalid must be in the MM/DD format i.e. yearly(11/22)".format(schedule))
                                    else:
                                        logger.error("Collection Error: failed to parse schedule: {}".format(schedule))
                                else:
                                    logger.error("Collection Error: schedule attribute {} invalid".format(schedule))
                        if skip_collection:
                            logger.info("Skipping Collection {}".format(c))
                            continue

                        try:
                            collection_obj = library.get_collection(c)
                            collection_name = collection_obj.title
                        except Failed as e:
                            collection_obj = None
                            collection_name = c

                        sync_collection = library.sync_mode == "sync"
                        if "sync_mode" in collections[c]:
                            if not collections[c]["sync_mode"]:                                     logger.warning("Collection Warning: sync_mode attribute is blank using general: {}".format(library.sync_mode))
                            elif collections[c]["sync_mode"] not in ["append", "sync"]:             logger.warning("Collection Warning: {} sync_mode invalid using general: {}".format(library.sync_mode, collections[c]["sync_mode"]))
                            else:                                                                   sync_collection = collections[c]["sync_mode"] == "sync"
                        if sync_collection or collectionless:
                            logger.info("Sync Mode: sync")
                            if collection_obj:
                                for item in collection_obj.items():
                                    map[item.ratingKey] = item
                        else:
                            logger.info("Sync Mode: append")

                        if "tmdb_person" in collections[c]:
                            if collections[c]["tmdb_person"]:
                                valid_names = []
                                for tmdb_id in util.get_int_list(collections[c]["tmdb_person"], "TMDb Person ID"):
                                    try:
                                        person = self.TMDb.get_person(tmdb_id)
                                        valid_names.append(person.name)
                                        if "summary" not in details and hasattr(person, "biography") and person.biography:
                                            details["summary"] = person.biography
                                        if "poster" not in details and hasattr(person, "profile_path") and person.profile_path:
                                            details["poster"] = ("url", "{}{}".format(self.TMDb.image_url, person.profile_path), "tmdb_person")
                                    except Failed as e:
                                        util.print_stacktrace()
                                        logger.error(e)
                                if len(valid_names) > 0:                                                details["tmdb_person"] = valid_names
                                else:                                                                   logger.error("Collection Error: No valid TMDb Person IDs in {}".format(collections[c]["tmdb_person"]))
                            else:
                                logger.error("Collection Error: tmdb_person attribute is blank")

                        for m in collections[c]:
                            try:
                                if "tmdb" in m and not self.TMDb:
                                    logger.info("Collection Error: {} skipped. TMDb must be configured".format(m))
                                    map = {}
                                elif "trakt" in m and not self.Trakt:
                                    logger.info("Collection Error: {} skipped. Trakt must be configured".format(m))
                                    map = {}
                                elif "imdb" in m and not self.IMDb:
                                    logger.info("Collection Error: {} skipped. TMDb or Trakt must be configured".format(m))
                                    map = {}
                                elif "tautulli" in m and not library.Tautulli:
                                    logger.info("Collection Error: {} skipped. Tautulli must be configured".format(m))
                                    map = {}
                                elif "mal" in m and not self.MyAnimeList:
                                    logger.info("Collection Error: {} skipped. MyAnimeList must be configured".format(m))
                                    map = {}
                                elif collections[c][m] is not None:
                                    if m in util.method_alias:
                                        method_name = util.method_alias[m]
                                        logger.warning("Collection Warning: {} attribute will run as {}".format(m, method_name))
                                    else:
                                        method_name = m
                                    if method_name in util.show_only_lists and library.is_movie:        raise Failed("Collection Error: {} attribute only works for show libraries".format(method_name))
                                    elif method_name in util.movie_only_lists and library.is_show:      raise Failed("Collection Error: {} attribute only works for movie libraries".format(method_name))
                                    elif method_name in util.movie_only_searches and library.is_show:   raise Failed("Collection Error: {} plex search only works for movie libraries".format(method_name))
                                    elif method_name not in util.collectionless_lists and collectionless: raise Failed("Collection Error: {} attribute does not work for Collectionless collection".format(method_name))
                                    elif method_name == "tmdb_summary":                                 details["summary"] = self.TMDb.get_movie_show_or_collection(util.regex_first_int(collections[c][m], "TMDb ID"), library.is_movie).overview
                                    elif method_name == "tmdb_description":                             details["summary"] = self.TMDb.get_list(util.regex_first_int(collections[c][m], "TMDb List ID")).description
                                    elif method_name == "tmdb_biography":                               details["summary"] = self.TMDb.get_person(util.regex_first_int(collections[c][m], "TMDb Person ID")).biography
                                    elif method_name == "collection_mode":
                                        if collections[c][m] in ["default", "hide", "hide_items", "show_items", "hideItems", "showItems"]:
                                            if collections[c][m] == "hide_items":                               details[method_name] = "hideItems"
                                            elif collections[c][m] == "show_items":                             details[method_name] = "showItems"
                                            else:                                                               details[method_name] = collections[c][m]
                                        else:                                                               raise Failed("Collection Error: {} collection_mode Invalid\n| \tdefault (Library default)\n| \thide (Hide Collection)\n| \thide_items (Hide Items in this Collection)\n| \tshow_items (Show this Collection and its Items)".format(collections[c][m]))
                                    elif method_name == "collection_order":
                                        if collections[c][m] in ["release", "alpha"]:                       details[method_name] = collections[c][m]
                                        else:                                                               raise Failed("Collection Error: {} collection_order Invalid\n| \trelease (Order Collection by release dates)\n| \talpha (Order Collection Alphabetically)".format(collections[c][m]))
                                    elif method_name == "url_poster":                                   posters_found.append(("url", collections[c][m], method_name))
                                    elif method_name == "tmdb_poster":                                  posters_found.append(("url", "{}{}".format(self.TMDb.image_url, self.TMDb.get_movie_show_or_collection(util.regex_first_int(collections[c][m], "TMDb ID"), library.is_movie).poster_path), method_name))
                                    elif method_name == "tmdb_profile":                                 posters_found.append(("url", "{}{}".format(self.TMDb.image_url, self.TMDb.get_person(util.regex_first_int(collections[c][m], "TMDb Person ID")).profile_path), method_name))
                                    elif method_name == "file_poster":
                                        if os.path.exists(collections[c][m]):                               posters_found.append(("file", os.path.abspath(collections[c][m]), method_name))
                                        else:                                                               raise Failed("Collection Error: Poster Path Does Not Exist: {}".format(os.path.abspath(collections[c][m])))
                                    elif method_name == "url_background":                               backgrounds_found.append(("url", collections[c][m], method_name))
                                    elif method_name == "tmdb_background":                              backgrounds_found.append(("url", "{}{}".format(self.TMDb.image_url, self.get_movie_show_or_collection(util.regex_first_int(collections[c][m], "TMDb ID"), library.is_movie).poster_path), method_name))
                                    elif method_name == "file_background":
                                        if os.path.exists(collections[c][m]):                               backgrounds_found.append(("file", os.path.abspath(collections[c][m]), method_name))
                                        else:                                                               raise Failed("Collection Error: Background Path Does Not Exist: {}".format(os.path.abspath(collections[c][m])))
                                    elif method_name == "add_to_arr":
                                        if isinstance(collections[c][m], bool):                             details[method_name] = collections[c][m]
                                        else:                                                               raise Failed("Collection Error: add_to_arr must be either true or false")
                                    elif method_name in util.all_details:                               details[method_name] = collections[c][m]
                                    elif method_name in ["year", "year.not"]:                           methods.append(("plex_search", [[(method_name, util.get_year_list(collections[c][m], method_name))]]))
                                    elif method_name in ["decade", "decade.not"]:                       methods.append(("plex_search", [[(method_name, util.get_int_list(collections[c][m], util.remove_not(method_name)))]]))
                                    elif method_name in util.tmdb_searches:
                                        final_values = []
                                        for value in util.get_list(collections[c][m]):
                                            if value.lower() == "tmdb" and "tmdb_person" in details:
                                                for name in details["tmdb_person"]:
                                                    final_values.append(name)
                                            else:
                                                final_values.append(value)
                                        methods.append(("plex_search", [[(method_name, final_values)]]))
                                    elif method_name in util.plex_searches:                             methods.append(("plex_search", [[(method_name, util.get_list(collections[c][m]))]]))
                                    elif method_name == "plex_all":                                     methods.append((method_name, [""]))
                                    elif method_name == "plex_collection":                              methods.append((method_name, library.validate_collections(collections[c][m] if isinstance(collections[c][m], list) else [collections[c][m]])))
                                    elif method_name == "anidb_popular":
                                        list_count = util.regex_first_int(collections[c][m], "List Size", default=40)
                                        if 1 <= list_count <= 30:
                                            methods.append((method_name, [list_count]))
                                        else:
                                            logger.error("Collection Error: anidb_popular must be an integer between 1 and 30 defaulting to 30")
                                            methods.append((method_name, [30]))
                                    elif method_name == "mal_id":                                       methods.append((method_name, util.get_int_list(collections[c][m], "MyAnimeList ID")))
                                    elif method_name in ["anidb_id", "anidb_relation"]:                 methods.append((method_name, self.AniDB.validate_anidb_list(util.get_int_list(collections[c][m], "AniDB ID"), library.Plex.language)))
                                    elif method_name == "trakt_list":                                   methods.append((method_name, self.Trakt.validate_trakt_list(util.get_list(collections[c][m]))))
                                    elif method_name == "trakt_watchlist":                              methods.append((method_name, self.Trakt.validate_trakt_watchlist(util.get_list(collections[c][m]), library.is_movie)))
                                    elif method_name == "imdb_list":
                                        new_list = []
                                        for imdb_list in util.get_list(collections[c][m]):
                                            new_dictionary = {}
                                            if isinstance(imdb_list, dict):
                                                if "url" in imdb_list and imdb_list["url"]:                         imdb_url = imdb_list["url"]
                                                else:                                                               raise Failed("Collection Error: No I")
                                                if "limit" in imdb_list and imdb_list["limit"]:                     list_count = util.regex_first_int(imdb_list["limit"], "List Limit", default=0)
                                                else:                                                               list_count = 0
                                            else:
                                                imdb_url = str(imdb_list)
                                                list_count = 0
                                            new_list.append({"url": imdb_url, "limit": list_count})
                                        methods.append((method_name, new_list))
                                    elif method_name in util.dictionary_lists:
                                        if isinstance(collections[c][m], dict):
                                            def get_int(parent, method, data, default, min=1, max=None):
                                                if method not in data:                                                  logger.warning("Collection Warning: {} {} attribute not found using {} as default".format(parent, method, default))
                                                elif not data[method]:                                                  logger.warning("Collection Warning: {} {} attribute is blank using {} as default".format(parent, method, default))
                                                elif isinstance(data[method], int) and data[method] >= min:
                                                    if max is None or data[method] <= max:                                  return data[method]
                                                    else:                                                                   logger.warning("Collection Warning: {} {} attribute {} invalid must an integer <= {} using {} as default".format(parent, method, data[method], max, default))
                                                else:                                                                   logger.warning("Collection Warning: {} {} attribute {} invalid must an integer >= {} using {} as default".format(parent, method, data[method], min, default))
                                                return default
                                            if method_name == "filters":
                                                for filter in collections[c][m]:
                                                    if filter in util.method_alias or (filter.endswith(".not") and filter[:-4] in util.method_alias):
                                                        final_filter = (util.method_alias[filter[:-4]] + filter[-4:]) if filter.endswith(".not") else util.method_alias[filter]
                                                        logger.warning("Collection Warning: {} filter will run as {}".format(filter, final_filter))
                                                    else:
                                                        final_filter = filter
                                                    if final_filter in util.movie_only_filters and library.is_show:
                                                        logger.error("Collection Error: {} filter only works for movie libraries".format(final_filter))
                                                    elif final_filter in util.all_filters:
                                                        filters.append((final_filter, collections[c][m][filter]))
                                                    else:
                                                        logger.error("Collection Error: {} filter not supported".format(filter))
                                            elif method_name == "plex_collectionless":
                                                new_dictionary = {}

                                                prefix_list = []
                                                if "exclude_prefix" in collections[c][m] and collections[c][m]["exclude_prefix"]:
                                                    if isinstance(collections[c][m]["exclude_prefix"], list):
                                                        prefix_list.extend(collections[c][m]["exclude_prefix"])
                                                    else:
                                                        prefix_list.append("{}".format(collections[c][m]["exclude_prefix"]))

                                                exact_list = []
                                                if "exclude" in collections[c][m] and collections[c][m]["exclude"]:
                                                    if isinstance(collections[c][m]["exclude"], list):
                                                        exact_list.extend(collections[c][m]["exclude"])
                                                    else:
                                                        exact_list.append("{}".format(collections[c][m]["exclude"]))

                                                if len(prefix_list) == 0 and len(exact_list) == 0:
                                                    raise Failed("Collection Error: you must have at least one exclusion")
                                                details["add_to_arr"] = False
                                                details["collection_mode"] = "hide"
                                                new_dictionary["exclude_prefix"] = prefix_list
                                                new_dictionary["exclude"] = exact_list
                                                methods.append((method_name, [new_dictionary]))
                                            elif method_name == "plex_search":
                                                search = []
                                                searches_used = []
                                                for search_attr in collections[c][m]:
                                                    if search_attr in util.method_alias or (search_attr.endswith(".not") and search_attr[:-4] in util.method_alias):
                                                        final_attr = (util.method_alias[search_attr[:-4]] + search_attr[-4:]) if search_attr.endswith(".not") else util.method_alias[search_attr]
                                                        logger.warning("Collection Warning: {} plex search attribute will run as {}".format(search_attr, final_attr))
                                                    else:
                                                        final_attr = search_attr
                                                    if final_attr in util.movie_only_searches and library.is_show:
                                                        logger.error("Collection Error: {} plex search attribute only works for movie libraries".format(final_attr))
                                                    elif util.remove_not(final_attr) in searches_used:
                                                        logger.error("Collection Error: Only one instance of {} can be used try using it as a filter instead".format(final_attr))
                                                    elif final_attr in ["year", "year.not"]:
                                                        years = util.get_year_list(collections[c][m][search_attr], final_attr)
                                                        if len(years) > 0:
                                                            searches_used.append(util.remove_not(final_attr))
                                                            search.append((final_attr, util.get_int_list(collections[c][m][search_attr], util.remove_not(final_attr))))
                                                    elif final_attr in util.plex_searches:
                                                        if final_attr.startswith("tmdb_"):
                                                            final_attr = final_attr[5:]
                                                        searches_used.append(util.remove_not(final_attr))
                                                        search.append((final_attr, util.get_list(collections[c][m][search_attr])))
                                                    else:
                                                        logger.error("Collection Error: {} plex search attribute not supported".format(search_attr))
                                                methods.append((method_name, [search]))
                                            elif method_name == "tmdb_discover":
                                                new_dictionary = {"limit": 100}
                                                for attr in collections[c][m]:
                                                    if collections[c][m][attr]:
                                                        attr_data = collections[c][m][attr]
                                                        if (library.is_movie and attr in util.discover_movie) or (library.is_show and attr in util.discover_tv):
                                                            if attr == "language":
                                                                if re.compile("([a-z]{2})-([A-Z]{2})").match(str(attr_data)):
                                                                    new_dictionary[attr] = str(attr_data)
                                                                else:
                                                                    logger.error("Collection Error: Skipping {} attribute {}: {} must match pattern ([a-z]{2})-([A-Z]{2}) e.g. en-US".format(m, attr, attr_data))
                                                            elif attr == "region":
                                                                if re.compile("^[A-Z]{2}$").match(str(attr_data)):
                                                                    new_dictionary[attr] = str(attr_data)
                                                                else:
                                                                    logger.error("Collection Error: Skipping {} attribute {}: {} must match pattern ^[A-Z]{2}$ e.g. US".format(m, attr, attr_data))
                                                            elif attr == "sort_by":
                                                                if (library.is_movie and attr_data in util.discover_movie_sort) or (library.is_show and attr_data in util.discover_tv_sort):
                                                                    new_dictionary[attr] = attr_data
                                                                else:
                                                                    logger.error("Collection Error: Skipping {} attribute {}: {} is invalid".format(m, attr, attr_data))
                                                            elif attr == "certification_country":
                                                                if "certification" in collections[c][m] or "certification.lte" in collections[c][m] or "certification.gte" in collections[c][m]:
                                                                    new_dictionary[attr] = attr_data
                                                                else:
                                                                    logger.error("Collection Error: Skipping {} attribute {}: must be used with either certification, certification.lte, or certification.gte".format(m, attr))
                                                            elif attr in ["certification", "certification.lte", "certification.gte"]:
                                                                if "certification_country" in collections[c][m]:
                                                                    new_dictionary[attr] = attr_data
                                                                else:
                                                                    logger.error("Collection Error: Skipping {} attribute {}: must be used with certification_country".format(m, attr))
                                                            elif attr in ["include_adult", "include_null_first_air_dates", "screened_theatrically"]:
                                                                if attr_data is True:
                                                                    new_dictionary[attr] = attr_data
                                                            elif attr in ["primary_release_date.gte", "primary_release_date.lte", "release_date.gte", "release_date.lte", "air_date.gte", "air_date.lte", "first_air_date.gte", "first_air_date.lte"]:
                                                                if re.compile("[0-1]?[0-9][/-][0-3]?[0-9][/-][1-2][890][0-9][0-9]").match(str(attr_data)):
                                                                    the_date = str(attr_data).split("/") if "/" in str(attr_data) else str(attr_data).split("-")
                                                                    new_dictionary[attr] = "{}-{}-{}".format(the_date[2], the_date[0], the_date[1])
                                                                elif re.compile("[1-2][890][0-9][0-9][/-][0-1]?[0-9][/-][0-3]?[0-9]").match(str(attr_data)):
                                                                    the_date = str(attr_data).split("/") if "/" in str(attr_data) else str(attr_data).split("-")
                                                                    new_dictionary[attr] = "{}-{}-{}".format(the_date[0], the_date[1], the_date[2])
                                                                else:
                                                                    logger.error("Collection Error: Skipping {} attribute {}: {} must match pattern MM/DD/YYYY e.g. 12/25/2020".format(m, attr, attr_data))
                                                            elif attr in ["primary_release_year", "year", "first_air_date_year"]:
                                                                if isinstance(attr_data, int) and 1800 < attr_data and attr_data < 2200:
                                                                    new_dictionary[attr] = attr_data
                                                                else:
                                                                    logger.error("Collection Error: Skipping {} attribute {}: must be a valid year e.g. 1990".format(m, attr))
                                                            elif attr in ["vote_count.gte", "vote_count.lte", "vote_average.gte", "vote_average.lte", "with_runtime.gte", "with_runtime.lte"]:
                                                                if (isinstance(attr_data, int) or isinstance(attr_data, float)) and 0 < attr_data:
                                                                    new_dictionary[attr] = attr_data
                                                                else:
                                                                    logger.error("Collection Error: Skipping {} attribute {}: must be a valid number greater then 0".format(m, attr))
                                                            elif attr in ["with_cast", "with_crew", "with_people", "with_companies", "with_networks", "with_genres", "without_genres", "with_keywords", "without_keywords", "with_original_language", "timezone"]:
                                                                new_dictionary[attr] = attr_data
                                                            else:
                                                                logger.error("Collection Error: {} attribute {} not supported".format(m, attr))
                                                        elif attr == "limit":
                                                            if isinstance(attr_data, int) and attr_data > 0:
                                                                new_dictionary[attr] = attr_data
                                                            else:
                                                                logger.error("Collection Error: Skipping {} attribute {}: must be a valid number greater then 0".format(m, attr))
                                                        else:
                                                            logger.error("Collection Error: {} attribute {} not supported".format(m, attr))
                                                    else:
                                                        logger.error("Collection Error: {} parameter {} is blank".format(m, attr))
                                                if len(new_dictionary) > 1:
                                                    methods.append((method_name, [new_dictionary]))
                                                else:
                                                    logger.error("Collection Error: {} had no valid fields".format(m))
                                            elif "tautulli" in method_name:
                                                new_dictionary = {}
                                                if method_name == "tautulli_popular":                                   new_dictionary["list_type"] = "popular"
                                                elif method_name == "tautulli_watched":                                 new_dictionary["list_type"] = "watched"
                                                else:                                                                   raise Failed("Collection Error: {} attribute not supported".format(method_name))
                                                new_dictionary["list_days"] = get_int(method_name, "list_days", collections[c][m], 30)
                                                new_dictionary["list_size"] = get_int(method_name, "list_size", collections[c][m], 10)
                                                new_dictionary["list_buffer"] = get_int(method_name, "list_buffer", collections[c][m], 20)
                                                methods.append((method_name, [new_dictionary]))
                                            elif method_name == "mal_season":
                                                new_dictionary = {"sort_by": "anime_num_list_users"}
                                                current_time = datetime.now()
                                                if current_time.month in [1, 2, 3]:                                     new_dictionary["season"] = "winter"
                                                elif current_time.month in [4, 5, 6]:                                   new_dictionary["season"] = "spring"
                                                elif current_time.month in [7, 8, 9]:                                   new_dictionary["season"] = "summer"
                                                elif current_time.month in [10, 11, 12]:                                new_dictionary["season"] = "fall"
                                                new_dictionary["year"] = get_int(method_name, "year", collections[c][m], current_time.year, min=1917, max=current_time.year + 1)
                                                new_dictionary["limit"] = get_int(method_name, "limit", collections[c][m], 100, max=500)
                                                if "sort_by" not in collections[c][m]:                                  logger.warning("Collection Error: mal_season sort_by attribute not found using members as default")
                                                elif not collections[c][m]["sort_by"]:                                  logger.warning("Collection Error: mal_season sort_by attribute is blank using members as default")
                                                elif collections[c][m]["sort_by"] not in util.mal_season_sort:          logger.warning("Collection Error: mal_season sort_by attribute {} invalid must be either 'members' or 'score' using members as default".format(collections[c][m]["sort_by"]))
                                                else:                                                                   new_dictionary["sort_by"] = util.mal_season_sort[collections[c][m]["sort_by"]]
                                                if "season" not in collections[c][m]:                                   logger.warning("Collection Error: mal_season season attribute not found using the current season: {} as default".format(new_dictionary["season"]))
                                                elif not collections[c][m]["season"]:                                   logger.warning("Collection Error: mal_season season attribute is blank using the current season: {} as default".format(new_dictionary["season"]))
                                                elif collections[c][m]["season"] not in util.pretty_seasons:            logger.warning("Collection Error: mal_season season attribute {} invalid must be either 'winter', 'spring', 'summer' or 'fall' using the current season: {} as default".format(collections[c][m]["season"], new_dictionary["season"]))
                                                else:                                                                   new_dictionary["season"] = collections[c][m]["season"]
                                                methods.append((method_name, [new_dictionary]))
                                            elif method_name == "mal_userlist":
                                                new_dictionary = {"status": "all", "sort_by": "list_score"}
                                                if "username" not in collections[c][m]:                                 raise Failed("Collection Error: mal_userlist username attribute is required")
                                                elif not collections[c][m]["username"]:                                 raise Failed("Collection Error: mal_userlist username attribute is blank")
                                                else:                                                                   new_dictionary["username"] = collections[c][m]["username"]
                                                if "status" not in collections[c][m]:                                   logger.warning("Collection Error: mal_season status attribute not found using all as default")
                                                elif not collections[c][m]["status"]:                                   logger.warning("Collection Error: mal_season status attribute is blank using all as default")
                                                elif collections[c][m]["status"] not in util.mal_userlist_status:       logger.warning("Collection Error: mal_season status attribute {} invalid must be either 'all', 'watching', 'completed', 'on_hold', 'dropped' or 'plan_to_watch' using all as default".format(collections[c][m]["status"]))
                                                else:                                                                   new_dictionary["status"] = util.mal_userlist_status[collections[c][m]["status"]]
                                                if "sort_by" not in collections[c][m]:                                  logger.warning("Collection Error: mal_season sort_by attribute not found using score as default")
                                                elif not collections[c][m]["sort_by"]:                                  logger.warning("Collection Error: mal_season sort_by attribute is blank using score as default")
                                                elif collections[c][m]["sort_by"] not in util.mal_userlist_sort:        logger.warning("Collection Error: mal_season sort_by attribute {} invalid must be either 'score', 'last_updated', 'title' or 'start_date' using score as default".format(collections[c][m]["sort_by"]))
                                                else:                                                                   new_dictionary["sort_by"] = util.mal_userlist_sort[collections[c][m]["sort_by"]]
                                                new_dictionary["limit"] = get_int(method_name, "limit", collections[c][m], 100, max=1000)
                                                methods.append((method_name, [new_dictionary]))
                                        else:
                                            logger.error("Collection Error: {} attribute is not a dictionary: {}".format(m, collections[c][m]))
                                    elif method_name in util.count_lists:
                                        list_count = util.regex_first_int(collections[c][m], "List Size", default=20)
                                        if list_count > 0:
                                            methods.append((method_name, [list_count]))
                                        else:
                                            logger.error("Collection Error: {} must be an integer greater then 0 defaulting to 20".format(method_name))
                                            methods.append((method_name, [20]))
                                    elif method_name in util.tmdb_lists:
                                        values = self.TMDb.validate_tmdb_list(util.get_int_list(collections[c][m], "TMDb {} ID".format(util.tmdb_type[method_name])), util.tmdb_type[method_name])
                                        if method_name[-8:] == "_details":
                                            if method_name in ["tmdb_collection_details", "tmdb_movie_details", "tmdb_show_details"]:
                                                item = self.TMDb.get_movie_show_or_collection(values[0], library.is_movie)
                                                if "summary" not in details and hasattr(item, "overview") and item.overview:
                                                    details["summary"] = item.overview
                                                if "background" not in details and hasattr(item, "backdrop_path") and item.backdrop_path:
                                                    details["background"] = ("url", "{}{}".format(self.TMDb.image_url, item.backdrop_path), method_name[:-8])
                                                if "poster" not in details and hasattr(item, "poster_path") and item.poster_path:
                                                    details["poster"] = ("url", "{}{}".format(self.TMDb.image_url, item.poster_path), method_name[:-8])
                                            else:
                                                item = self.TMDb.get_list(values[0])
                                                if "summary" not in details and hasattr(item, "description") and item.description:
                                                    details["summary"] = item.description
                                            methods.append((method_name[:-8], values))
                                        else:
                                            methods.append((method_name, values))
                                    elif method_name in util.all_lists:                                 methods.append((method_name, util.get_list(collections[c][m])))
                                    elif method_name not in ["sync_mode", "schedule", "tmdb_person"]:   logger.error("Collection Error: {} attribute not supported".format(method_name))
                                else:
                                    logger.error("Collection Error: {} attribute is blank".format(m))
                            except Failed as e:
                                logger.error(e)

                        for i, f in enumerate(filters):
                            if i == 0:
                                logger.info("")
                            logger.info("Collection Filter {}: {}".format(f[0], f[1]))

                        do_arr = False
                        if library.Radarr:
                            do_arr = details["add_to_arr"] if "add_to_arr" in details else library.Radarr.add
                        if library.Sonarr:
                            do_arr = details["add_to_arr"] if "add_to_arr" in details else library.Sonarr.add


                        items_found = 0
                        library.clear_collection_missing(collection_name)

                        for method, values in methods:
                            pretty = util.pretty_names[method] if method in util.pretty_names else method
                            for value in values:
                                items = []
                                missing_movies = []
                                missing_shows = []
                                def check_map(input_ids):
                                    movie_ids, show_ids = input_ids
                                    items_found_inside = 0
                                    if len(movie_ids) > 0:
                                        items_found_inside += len(movie_ids)
                                        for movie_id in movie_ids:
                                            if movie_id in movie_map:                           items.append(movie_map[movie_id])
                                            else:                                               missing_movies.append(movie_id)
                                    if len(show_ids) > 0:
                                        items_found_inside += len(show_ids)
                                        for show_id in show_ids:
                                            if show_id in show_map:                             items.append(show_map[show_id])
                                            else:                                               missing_shows.append(show_id)
                                    return items_found_inside
                                logger.info("")
                                if method == "plex_all":
                                    logger.info("Processing {} {}".format(pretty, "Movies" if library.is_movie else "Shows"))
                                    items = library.Plex.all()
                                    items_found += len(items)
                                elif method == "plex_collection":
                                    items = value.items()
                                    items_found += len(items)
                                elif method == "plex_search":
                                    search_terms = {}
                                    output = ""
                                    for i, attr_pair in enumerate(value):
                                        search_list = attr_pair[1]
                                        final_method = attr_pair[0][:-4] + "!" if attr_pair[0][-4:] == ".not" else attr_pair[0]
                                        if library.is_show:
                                            final_method = "show." + final_method
                                        search_terms[final_method] = search_list
                                        ors = ""
                                        for o, param in enumerate(attr_pair[1]):
                                            ors += "{}{}".format(" OR " if o > 0 else "{}(".format(attr_pair[0]), param)
                                        logger.info("\t\t      AND {})".format(ors) if i > 0 else "Processing {}: {})".format(pretty, ors))
                                    items = library.Plex.search(**search_terms)
                                    items_found += len(items)
                                elif method == "plex_collectionless":
                                    good_collections = []
                                    for col in library.get_all_collections():
                                        keep_collection = True
                                        for pre in value["exclude_prefix"]:
                                            if col.title.startswith(pre) or (col.titleSort and col.titleSort.startswith(pre)):
                                                keep_collection = False
                                                break
                                        for ext in value["exclude"]:
                                            if col.title == ext or (col.titleSort and col.titleSort == ext):
                                                keep_collection = False
                                                break
                                        if keep_collection:
                                            good_collections.append(col.title.lower())

                                    all_items = library.Plex.all()
                                    length = 0
                                    for i, item in enumerate(all_items, 1):
                                        length = util.print_return(length, "Processing: {}/{} {}".format(i, len(all_items), item.title))
                                        add_item = True
                                        for collection in item.collections:
                                            if collection.tag.lower() in good_collections:
                                                add_item = False
                                                break
                                        if add_item:
                                            items.append(item)
                                    items_found += len(items)
                                    util.print_end(length, "Processed {} {}".format(len(all_items), "Movies" if library.is_movie else "Shows"))
                                elif "tautulli" in method:
                                    items = library.Tautulli.get_items(library, time_range=value["list_days"], stats_count=value["list_size"], list_type=value["list_type"], stats_count_buffer=value["list_buffer"])
                                    items_found += len(items)
                                elif "anidb" in method:                             items_found += check_map(self.AniDB.get_items(method, value, library.Plex.language))
                                elif "mal" in method:                               items_found += check_map(self.MyAnimeList.get_items(method, value))
                                elif "tvdb" in method:                              items_found += check_map(self.TVDb.get_items(method, value, library.Plex.language))
                                elif "imdb" in method:                              items_found += check_map(self.IMDb.get_items(method, value, library.Plex.language))
                                elif "tmdb" in method:                              items_found += check_map(self.TMDb.get_items(method, value, library.is_movie))
                                elif "trakt" in method:                             items_found += check_map(self.Trakt.get_items(method, value, library.is_movie))
                                else:                                               logger.error("Collection Error: {} method not supported".format(method))

                                if len(items) > 0:                                  map = library.add_to_collection(collection_obj if collection_obj else collection_name, items, filters, map=map)
                                else:                                               logger.error("No items found to add to this collection ")

                                if len(missing_movies) > 0 or len(missing_shows) > 0:
                                    logger.info("")
                                    if len(missing_movies) > 0:
                                        missing_movies_with_names = []
                                        for missing_id in missing_movies:
                                            try:
                                                title = str(self.TMDb.get_movie(missing_id).title)
                                                missing_movies_with_names.append((title, missing_id))
                                                logger.info("{} Collection | ? | {} (TMDB: {})".format(collection_name, title, missing_id))
                                            except Failed as e:
                                                logger.error(e)
                                        logger.info("{} Movie{} Missing".format(len(missing_movies), "s" if len(missing_movies) > 1 else ""))
                                        library.save_missing(collection_name, missing_movies_with_names, True)
                                        if do_arr and library.Radarr:
                                            library.Radarr.add_tmdb(missing_movies)
                                    if len(missing_shows) > 0 and library.is_show:
                                        missing_shows_with_names = []
                                        for missing_id in missing_shows:
                                            try:
                                                title = str(self.TVDb.get_series(library.Plex.language, tvdb_id=missing_id).title.encode("ascii", "replace").decode())
                                                missing_shows_with_names.append((title, missing_id))
                                                logger.info("{} Collection | ? | {} (TVDB: {})".format(collection_name, title, missing_id))
                                            except Failed as e:
                                                logger.error(e)
                                        logger.info("{} Show{} Missing".format(len(missing_shows), "s" if len(missing_shows) > 1 else ""))
                                        library.save_missing(c, missing_shows_with_names, False)
                                        if do_arr and library.Sonarr:
                                            library.Sonarr.add_tvdb(missing_shows)

                        library.del_collection_if_empty(collection_name)

                        if (sync_collection or collectionless) and items_found > 0:
                            logger.info("")
                            count_removed = 0
                            for ratingKey, item in map.items():
                                if item is not None:
                                    logger.info("{} Collection | - | {}".format(collection_name, item.title))
                                    item.removeCollection(collection_name)
                                    count_removed += 1
                            logger.info("{} {}{} Removed".format(count_removed, "Movie" if library.is_movie else "Show", "s" if count_removed == 1 else ""))
                        logger.info("")

                        try:
                            plex_collection = library.get_collection(collection_name)
                        except Failed as e:
                            logger.debug(e)
                            continue

                        edits = {}
                        if "sort_title" in details:
                            edits["titleSort.value"] = details["sort_title"]
                            edits["titleSort.locked"] = 1
                        if "content_rating" in details:
                            edits["contentRating.value"] = details["content_rating"]
                            edits["contentRating.locked"] = 1
                        if "summary" in details:
                            edits["summary.value"] = details["summary"]
                            edits["summary.locked"] = 1
                        if len(edits) > 0:
                            plex_collection.edit(**edits)
                            plex_collection.reload()
                            logger.info("Details: have been updated")
                            logger.debug(edits)
                        if "collection_mode" in details:
                            plex_collection.modeUpdate(mode=details["collection_mode"])
                        if "collection_order" in details:
                            plex_collection.sortUpdate(sort=details["collection_order"])

                        if library.asset_directory:
                            name_mapping = c
                            if "name_mapping" in collections[c]:
                                if collections[c]["name_mapping"]:                                  name_mapping = collections[c]["name_mapping"]
                                else:                                                               logger.error("Collection Error: name_mapping attribute is blank")
                            path = os.path.join(library.asset_directory, "{}".format(name_mapping), "poster.*")
                            matches = glob.glob(path)
                            if len(matches) > 0:
                                for match in matches:                                               posters_found.append(("file", os.path.abspath(match), "asset_directory"))
                            elif len(posters_found) == 0 and "poster" not in details:           logger.warning("poster not found at: {}".format(os.path.abspath(path)))
                            path = os.path.join(library.asset_directory, "{}".format(name_mapping), "background.*")
                            matches = glob.glob(path)
                            if len(matches) > 0:
                                for match in matches:                                               backgrounds_found.append(("file", os.path.abspath(match), "asset_directory"))
                            elif len(backgrounds_found) == 0 and "background" not in details:   logger.warning("background not found at: {}".format(os.path.abspath(path)))

                        poster = util.choose_from_list(posters_found, "poster", list_type="tuple")
                        if not poster and "poster" in details:                  poster = details["poster"]
                        if poster:
                            if poster[0] == "url":                                  plex_collection.uploadPoster(url=poster[1])
                            else:                                                   plex_collection.uploadPoster(filepath=poster[1])
                            logger.info("Detail: {} updated poster to [{}] {}".format(poster[2], poster[0], poster[1]))

                        background = util.choose_from_list(backgrounds_found, "background", list_type="tuple")
                        if not background and "background" in details:          background = details["background"]
                        if background:
                            if background[0] == "url":                              plex_collection.uploadArt(url=background[1])
                            else:                                                   plex_collection.uploadArt(filepath=background[1])
                            logger.info("Detail: {} updated background to [{}] {}".format(background[2], background[0], background[1]))
                    except Exception as e:
                        util.print_stacktrace()
                        logger.error("Unknown Error: {}".format(e))

                logger.info("")
                util.seperator("Unmanaged Collections in {} Library".format(library.name))
                logger.info("")
                unmanaged_count = 0
                collections_in_plex = [str(pcol) for pcol in collections]
                for col in library.get_all_collections():
                     if col.title not in collections_in_plex:
                         logger.info(col.title)
                         unmanaged_count += 1
                logger.info("{} Unmanaged Collections".format(unmanaged_count))
            else:
                logger.error("No collection to update")

    def map_guids(self, library):
        movie_map = {}
        show_map = {}
        length = 0
        count = 0
        logger.info("Mapping {} Library: {}".format("Movie" if library.is_movie else "Show", library.name))
        items = library.Plex.all()
        for i, item in enumerate(items, 1):
            length = util.print_return(length, "Processing: {}/{} {}".format(i, len(items), item.title))
            id_type, main_id = self.get_id(item, library, length)
            if id_type == "movie":
                movie_map[main_id] = item.ratingKey
            elif id_type == "show":
                show_map[main_id] = item.ratingKey
        util.print_end(length, "Processed {} {}".format(len(items), "Movies" if library.is_movie else "Shows"))
        return movie_map, show_map

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

            if item_type == "plex" and library.is_movie:
                for guid_tag in item.guids:
                    url_parsed = requests.utils.urlparse(guid_tag.id)
                    if url_parsed.scheme == "tmdb":                 tmdb_id = url_parsed.netloc
                    elif url_parsed.scheme == "imdb":               imdb_id = url_parsed.netloc
            elif item_type == "imdb":                       imdb_id = check_id
            elif item_type == "thetvdb":                    tvdb_id = check_id
            elif item_type == "themoviedb":                 tmdb_id = check_id
            elif item_type == "hama":
                if check_id.startswith("tvdb"):             tvdb_id = re.search("-(.*)", check_id).group(1)
                elif check_id.startswith("anidb"):          anidb_id = re.search("-(.*)", check_id).group(1)
                else:                                       error_message = "Hama Agent ID: {} not supported".format(check_id)
            elif item_type == "myanimelist":                mal_id = check_id
            elif item_type == "local":                      error_message = "No match in Plex"
            else:                                           error_message = "Agent {} not supported".format(item_type)

            if not error_message:
                if anidb_id and not tvdb_id:
                    try:                                            tvdb_id = self.AniDB.convert_anidb_to_tvdb(anidb_id)
                    except Failed:                                  pass
                if anidb_id and not imdb_id:
                    try:                                            imdb_id = self.AniDB.convert_anidb_to_imdb(anidb_id)
                    except Failed:                                  pass
                if mal_id:
                    try:
                        ids = self.MyAnimeListIDList.find_mal_ids(mal_id)
                        if "thetvdb_id" in ids and int(ids["thetvdb_id"]) > 0:                  tvdb_id = int(ids["thetvdb_id"])
                        elif "themoviedb_id" in ids and int(ids["themoviedb_id"]) > 0:          tmdb_id = int(ids["themoviedb_id"])
                        else:                                                                   raise Failed("MyAnimeList Error: MyAnimeList ID: {} has no other IDs associated with it".format(mal_id))
                    except Failed:
                        pass
                if mal_id and not tvdb_id:
                    try:                                            tvdb_id = self.MyAnimeListIDList.convert_mal_to_tvdb(mal_id)
                    except Failed:                                  pass
                if mal_id and not tmdb_id:
                    try:                                            tmdb_id = self.MyAnimeListIDList.convert_mal_to_tmdb(mal_id)
                    except Failed:                                  pass
                if not tmdb_id and imdb_id and self.TMDb:
                    try:                                            tmdb_id = self.TMDb.convert_imdb_to_tmdb(imdb_id)
                    except Failed:                                  pass
                if not tmdb_id and imdb_id and self.Trakt:
                    try:                                            tmdb_id = self.Trakt.convert_imdb_to_tmdb(imdb_id)
                    except Failed:                                  pass
                if not tmdb_id and tvdb_id and self.TMDb:
                    try:                                            tmdb_id = self.TMDb.convert_tvdb_to_tmdb(tvdb_id)
                    except Failed:                                  pass
                if not tmdb_id and tvdb_id and self.Trakt:
                    try:                                            tmdb_id = self.Trakt.convert_tvdb_to_tmdb(tvdb_id)
                    except Failed:                                  pass
                if not imdb_id and tmdb_id and self.TMDb:
                    try:                                            imdb_id = self.TMDb.convert_tmdb_to_imdb(tmdb_id)
                    except Failed:                                  pass
                if not imdb_id and tmdb_id and self.Trakt:
                    try:                                            imdb_id = self.Trakt.convert_tmdb_to_imdb(tmdb_id)
                    except Failed:                                  pass
                if not imdb_id and tvdb_id and self.Trakt:
                    try:                                            imdb_id = self.Trakt.convert_tmdb_to_imdb(tmdb_id)
                    except Failed:                                  pass
                if not tvdb_id and tmdb_id and self.TMDb and library.is_show:
                    try:                                            tvdb_id = self.TMDb.convert_tmdb_to_tvdb(tmdb_id)
                    except Failed:                                  pass
                if not tvdb_id and tmdb_id and self.Trakt and library.is_show:
                    try:                                            tvdb_id = self.Trakt.convert_tmdb_to_tvdb(tmdb_id)
                    except Failed:                                  pass
                if not tvdb_id and imdb_id and self.Trakt and library.is_show:
                    try:                                            tvdb_id = self.Trakt.convert_imdb_to_tvdb(imdb_id)
                    except Failed:                                  pass
                if tvdb_id and not anidb_id:
                    try:                                            anidb_id = self.AniDB.convert_tvdb_to_anidb(tvdb_id)
                    except Failed:                                  pass
                if imdb_id and not anidb_id:
                    try:                                            anidb_id = self.AniDB.convert_imdb_to_anidb(imdb_id)
                    except Failed:                                  pass
                if tvdb_id and not mal_id:
                    try:                                            mal_id = self.MyAnimeListIDList.convert_tvdb_to_mal(tvdb_id)
                    except Failed:                                  pass
                if tmdb_id and not mal_id:
                    try:                                            mal_id = self.MyAnimeListIDList.convert_tmdb_to_mal(tmdb_id)
                    except Failed:                                  pass

                if (not tmdb_id and library.is_movie) or (not tvdb_id and not ((anidb_id or mal_id) and tmdb_id) and library.is_show):
                    service_name = "TMDb ID" if library.is_movie else "TVDb ID"

                    if self.TMDb and self.Trakt:                    api_name = "TMDb or Trakt"
                    elif self.TMDb:                                 api_name = "TMDb"
                    elif self.Trakt:                                api_name = "Trakt"
                    else:                                           api_name = None

                    if tmdb_id and imdb_id:                         id_name = "TMDb ID: {} or IMDb ID: {}".format(tmdb_id, imdb_id)
                    elif imdb_id and tvdb_id:                       id_name = "IMDb ID: {} or TVDb ID: {}".format(imdb_id, tvdb_id)
                    elif tmdb_id:                                   id_name = "TMDb ID: {}".format(tmdb_id)
                    elif imdb_id:                                   id_name = "IMDb ID: {}".format(imdb_id)
                    elif tvdb_id:                                   id_name = "TVDb ID: {}".format(tvdb_id)
                    else:                                           id_name = None

                    if anidb_id and not tmdb_id and not tvdb_id:    error_message = "Unable to convert AniDb ID: {} to TMDb ID or TVDb ID".format(anidb_id)
                    elif mal_id and not tmdb_id and not tvdb_id:    error_message = "Unable to convert MyAnimeList ID: {} to TMDb ID or TVDb ID".format(mal_id)
                    elif id_name and api_name:                      error_message = "Unable to convert {} to {} using {}".format(id_name, service_name, api_name)
                    elif id_name:                                   error_message = "Configure TMDb or Trakt to covert {} to {}".format(id_name, service_name)
                    else:                                           error_message = "No ID to convert to {}".format(service_name)
            if self.Cache and (tmdb_id and library.is_movie) or ((tvdb_id or ((anidb_id or mal_id) and tmdb_id)) and library.is_show):
                util.print_end(length, "Cache | {} | {:<46} | {:<6} | {:<10} | {:<6} | {:<5} | {:<5} | {}".format("^" if expired is True else "+", item.guid, tmdb_id if tmdb_id else "None", imdb_id if imdb_id else "None", tvdb_id if tvdb_id else "None", anidb_id if anidb_id else "None", mal_id if mal_id else "None", item.title))
                self.Cache.update_guid("movie" if library.is_movie else "show", item.guid, tmdb_id, imdb_id, tvdb_id, anidb_id, mal_id, expired)
        if tmdb_id and library.is_movie:                return "movie", tmdb_id
        elif tvdb_id and library.is_show:               return "show", tvdb_id
        elif (anidb_id or mal_id) and tmdb_id:          return "movie", tmdb_id
        else:
            util.print_end(length, "{} {:<46} | {} for {}".format("Cache | ! |" if self.Cache else "Mapping Error:", item.guid, error_message, item.title))
            return None, None
