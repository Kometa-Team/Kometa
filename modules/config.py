import glob, logging, os, re, requests
from modules import util
from modules.anidb import AniDBAPI
from modules.builder import CollectionBuilder
from modules.cache import Cache
from modules.imdb import IMDbAPI
from modules.plex import PlexAPI
from modules.mal import MyAnimeListAPI
from modules.mal import MyAnimeListIDList
from modules.tmdb import TMDbAPI
from modules.trakt import TraktAPI
from modules.tvdb import TVDbAPI
from modules.util import Failed
from plexapi.exceptions import BadRequest
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
            elif not data[attribute] and data[attribute] != False:
                if default_is_none is True:                                         return None
                else:                                                               message = "Config Error: {} is blank".format(text)
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
            logger.info("My Anime List Connection {}".format("Failed" if self.MyAnimeList is None else "Successful"))
        else:
            logger.warning("mal attribute not found")

        self.TVDb = TVDbAPI(Cache=self.Cache, TMDb=self.TMDb, Trakt=self.Trakt)
        self.IMDb = IMDbAPI(Cache=self.Cache, TMDb=self.TMDb, Trakt=self.Trakt, TVDb=self.TVDb) if self.TMDb or self.Trakt else None
        self.AniDB = AniDBAPI(Cache=self.Cache, TMDb=self.TMDb, Trakt=self.Trakt)

        util.seperator()

        logger.info("Connecting to Plex Libraries...")

        self.general["plex"] = {}
        self.general["plex"]["url"] = check_for_attribute(self.data, "url", parent="plex", default_is_none=True) if "plex" in self.data else None
        self.general["plex"]["token"] = check_for_attribute(self.data, "token", parent="plex", default_is_none=True) if "plex" in self.data else None
        self.general["plex"]["asset_directory"] = check_for_attribute(self.data, "asset_directory", parent="plex", var_type="path", default=os.path.join(default_dir, "assets")) if "plex" in self.data else os.path.join(default_dir, "assets")
        self.general["plex"]["sync_mode"] = check_for_attribute(self.data, "sync_mode", parent="plex", default="append", test_list=["append", "sync"], options="| \tappend (Only Add Items to the Collection)\n| \tsync (Add & Remove Items from the Collection)") if "plex" in self.data else "append"
        self.general["plex"]["show_unmanaged"] = check_for_attribute(self.data, "show_unmanaged", parent="plex", var_type="bool", default=True) if "plex" in self.data else True
        self.general["plex"]["show_filtered"] = check_for_attribute(self.data, "show_filtered", parent="plex", var_type="bool", default=False) if "plex" in self.data else False

        self.general["radarr"] = {}
        self.general["radarr"]["url"] = check_for_attribute(self.data, "url", parent="radarr", default_is_none=True) if "radarr" in self.data else None
        self.general["radarr"]["version"] = check_for_attribute(self.data, "version", parent="radarr", test_list=["v2", "v3"], options="| \tv2 (For Radarr 0.2)\n| \tv3 (For Radarr 3.0)", default="v2") if "radarr" in self.data else "v2"
        self.general["radarr"]["token"] = check_for_attribute(self.data, "token", parent="radarr", default_is_none=True) if "radarr" in self.data else None
        self.general["radarr"]["quality_profile"] = check_for_attribute(self.data, "quality_profile", parent="radarr", default_is_none=True) if "radarr" in self.data else None
        self.general["radarr"]["root_folder_path"] = check_for_attribute(self.data, "root_folder_path", parent="radarr", default_is_none=True) if "radarr" in self.data else None
        self.general["radarr"]["add"] = check_for_attribute(self.data, "add", parent="radarr", var_type="bool", default=False) if "radarr" in self.data else False
        self.general["radarr"]["search"] = check_for_attribute(self.data, "search", parent="radarr", var_type="bool", default=False) if "radarr" in self.data else False
        self.general["radarr"]["tag"] = util.get_list(check_for_attribute(self.data, "tag", parent="radarr", default_is_none=True), lower=True) if "radarr" in self.data else None

        self.general["sonarr"] = {}
        self.general["sonarr"]["url"] = check_for_attribute(self.data, "url", parent="sonarr", default_is_none=True) if "sonarr" in self.data else None
        self.general["sonarr"]["token"] = check_for_attribute(self.data, "token", parent="sonarr", default_is_none=True) if "sonarr" in self.data else None
        self.general["sonarr"]["version"] = check_for_attribute(self.data, "version", parent="sonarr", test_list=["v2", "v3"], options="| \tv2 (For Sonarr 0.2)\n| \tv3 (For Sonarr 3.0)", default="v2") if "sonarr" in self.data else "v2"
        self.general["sonarr"]["quality_profile"] = check_for_attribute(self.data, "quality_profile", parent="sonarr", default_is_none=True) if "sonarr" in self.data else None
        self.general["sonarr"]["root_folder_path"] = check_for_attribute(self.data, "root_folder_path", parent="sonarr", default_is_none=True) if "sonarr" in self.data else None
        self.general["sonarr"]["add"] = check_for_attribute(self.data, "add", parent="sonarr", var_type="bool", default=False) if "sonarr" in self.data else False
        self.general["sonarr"]["search"] = check_for_attribute(self.data, "search", parent="sonarr", var_type="bool", default=False) if "sonarr" in self.data else False
        self.general["sonarr"]["tag"] = util.get_list(check_for_attribute(self.data, "tag", parent="sonarr", default_is_none=True), lower=True) if "sonarr" in self.data else None

        self.general["tautulli"] = {}
        self.general["tautulli"]["url"] = check_for_attribute(self.data, "url", parent="tautulli", default_is_none=True) if "tautulli" in self.data else None
        self.general["tautulli"]["apikey"] = check_for_attribute(self.data, "apikey", parent="tautulli", default_is_none=True) if "tautulli" in self.data else None


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

            params["show_unmanaged"] = self.general["plex"]["show_unmanaged"]
            if "plex" in libs[lib] and "show_unmanaged" in libs[lib]["plex"]:
                if libs[lib]["plex"]["show_unmanaged"]:
                    if isinstance(libs[lib]["plex"]["show_unmanaged"], bool):
                        params["plex"]["show_unmanaged"] = libs[lib]["plex"]["show_unmanaged"]
                    else:
                        logger.warning("Config Warning: plex sub-attribute show_unmanaged must be either true or false using general value: {}".format(self.general["plex"]["show_unmanaged"]))
                else:
                    logger.warning("Config Warning: plex sub-attribute show_unmanaged is blank using general value: {}".format(self.general["plex"]["show_unmanaged"]))

            params["show_filtered"] = self.general["plex"]["show_filtered"]
            if "plex" in libs[lib] and "show_filtered" in libs[lib]["plex"]:
                if libs[lib]["plex"]["show_filtered"]:
                    if isinstance(libs[lib]["plex"]["show_filtered"], bool):
                        params["plex"]["show_filtered"] = libs[lib]["plex"]["show_filtered"]
                    else:
                        logger.warning("Config Warning: plex sub-attribute show_filtered must be either true or false using general value: {}".format(self.general["plex"]["show_filtered"]))
                else:
                    logger.warning("Config Warning: plex sub-attribute show_filtered is blank using general value: {}".format(self.general["plex"]["show_filtered"]))

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

                if "tag" in libs[lib]["radarr"]:
                    if libs[lib]["radarr"]["tag"]:
                        params["radarr"]["tag"] = util.get_list(libs[lib]["radarr"]["tag"], lower=True)
                    else:
                        logger.warning("Config Warning: radarr sub-attribute tag is blank using general value: {}".format(self.general["radarr"]["tag"]))

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

                if "tag" in libs[lib]["sonarr"]:
                    if libs[lib]["sonarr"]["tag"]:
                        params["sonarr"]["tag"] = util.get_list(libs[lib]["sonarr"]["tag"], lower=True)
                    else:
                        logger.warning("Config Warning: sonarr sub-attribute tag is blank using general value: {}".format(self.general["sonarr"]["tag"]))

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

    def update_libraries(self, test, requested_collections):
        for library in self.libraries:
            logger.info("")
            util.seperator("{} Library".format(library.name))
            try:                        library.update_metadata(self.TMDb, test)
            except Failed as e:         logger.error(e)
            logger.info("")
            util.seperator("{} Library {}Collections".format(library.name, "Test " if test else ""))
            collections = {c: library.collections[c] for c in util.get_list(requested_collections) if c in library.collections} if requested_collections else library.collections
            if collections:
                logger.info("")
                util.seperator("Mapping {} Library".format(library.name))
                logger.info("")
                movie_map, show_map = self.map_guids(library)
                for c in collections:
                    if test and ("test" not in collections[c] or collections[c]["test"] is not True):
                        continue
                    try:
                        logger.info("")
                        util.seperator("{} Collection".format(c))
                        logger.info("")

                        map = {}
                        try:
                            builder = CollectionBuilder(self, library, c, collections[c])
                        except Exception as e:
                            util.print_stacktrace()
                            logger.error(e)
                            continue

                        try:
                            collection_obj = library.get_collection(c)
                            collection_name = collection_obj.title
                        except Failed as e:
                            collection_obj = None
                            collection_name = c

                        if builder.schedule is not None:
                            print_multiline(builder.schedule, info=True)

                        logger.info("")
                        if builder.sync:
                            logger.info("Sync Mode: sync")
                            if collection_obj:
                                for item in collection_obj.items():
                                    map[item.ratingKey] = item
                        else:
                            logger.info("Sync Mode: append")

                        for i, f in enumerate(builder.filters):
                            if i == 0:
                                logger.info("")
                            logger.info("Collection Filter {}: {}".format(f[0], f[1]))

                        builder.run_methods(collection_obj, collection_name, map, movie_map, show_map)

                        try:
                            plex_collection = library.get_collection(collection_name)
                        except Failed as e:
                            logger.debug(e)
                            continue

                        builder.update_details(plex_collection)

                    except Exception as e:
                        util.print_stacktrace()
                        logger.error("Unknown Error: {}".format(e))
                if library.show_unmanaged is True and not test and not requested_collections:
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
                logger.info("")
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
            try:
                id_type, main_id = self.get_id(item, library, length)
            except BadRequest:
                util.print_stacktrace()
                util.print_end(length, "{} {:<46} | {} for {}".format("Cache | ! |" if self.Cache else "Mapping Error:", item.guid, error_message, item.title))
                continue
            if isinstance(main_id, list):
                if id_type == "movie":
                    for m in main_id:                               movie_map[m] = item.ratingKey
                elif id_type == "show":
                    for m in main_id:                               show_map[m] = item.ratingKey
            else:
                if id_type == "movie":                          movie_map[main_id] = item.ratingKey
                elif id_type == "show":                         show_map[main_id] = item.ratingKey
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
                    if url_parsed.scheme == "tmdb":                 tmdb_id = int(url_parsed.netloc)
                    elif url_parsed.scheme == "imdb":               imdb_id = url_parsed.netloc
            elif item_type == "imdb":                       imdb_id = check_id
            elif item_type == "thetvdb":                    tvdb_id = int(check_id)
            elif item_type == "themoviedb":                 tmdb_id = int(check_id)
            elif item_type == "hama":
                if check_id.startswith("tvdb"):             tvdb_id = int(re.search("-(.*)", check_id).group(1))
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
                if not tmdb_id and imdb_id and isinstance(imdb_id, list) and self.TMDb:
                    tmdb_id = []
                    new_imdb_id = []
                    for imdb in imdb_id:
                        try:
                            temp_tmdb_id = self.TMDb.convert_imdb_to_tmdb(imdb)
                            tmdb_id.append(temp_tmdb_id)
                            new_imdb_id.append(imdb)
                        except Failed:
                            continue
                    imdb_id = new_imdb_id
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
                if isinstance(tmdb_id, list):
                    for i in range(len(tmdb_id)):
                        util.print_end(length, "Cache | {} | {:<46} | {:<6} | {:<10} | {:<6} | {:<5} | {:<5} | {}".format("^" if expired is True else "+", item.guid, tmdb_id[i] if tmdb_id[i] else "None", imdb_id[i] if imdb_id[i] else "None", tvdb_id if tvdb_id else "None", anidb_id if anidb_id else "None", mal_id if mal_id else "None", item.title))
                        self.Cache.update_guid("movie" if library.is_movie else "show", item.guid, tmdb_id[i], imdb_id[i], tvdb_id, anidb_id, mal_id, expired)
                else:
                    util.print_end(length, "Cache | {} | {:<46} | {:<6} | {:<10} | {:<6} | {:<5} | {:<5} | {}".format("^" if expired is True else "+", item.guid, tmdb_id if tmdb_id else "None", imdb_id if imdb_id else "None", tvdb_id if tvdb_id else "None", anidb_id if anidb_id else "None", mal_id if mal_id else "None", item.title))
                    self.Cache.update_guid("movie" if library.is_movie else "show", item.guid, tmdb_id, imdb_id, tvdb_id, anidb_id, mal_id, expired)
        if tmdb_id and library.is_movie:                return "movie", tmdb_id
        elif tvdb_id and library.is_show:               return "show", tvdb_id
        elif (anidb_id or mal_id) and tmdb_id:          return "movie", tmdb_id
        else:
            util.print_end(length, "{} {:<46} | {} for {}".format("Cache | ! |" if self.Cache else "Mapping Error:", item.guid, error_message, item.title))
            return None, None
