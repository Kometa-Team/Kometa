import os, re
from datetime import datetime
from modules import util, radarr, sonarr, operations
from modules.anidb import AniDB
from modules.anilist import AniList
from modules.cache import Cache
from modules.convert import Convert
from modules.ergast import Ergast
from modules.icheckmovies import ICheckMovies
from modules.imdb import IMDb
from modules.github import GitHub
from modules.letterboxd import Letterboxd
from modules.mal import MyAnimeList
from modules.meta import PlaylistFile
from modules.mojo import BoxOfficeMojo
from modules.notifiarr import Notifiarr
from modules.gotify import Gotify
from modules.omdb import OMDb
from modules.overlays import Overlays
from modules.plex import Plex
from modules.radarr import Radarr
from modules.sonarr import Sonarr
from modules.reciperr import Reciperr
from modules.mdblist import MDBList
from modules.tautulli import Tautulli
from modules.tmdb import TMDb
from modules.trakt import Trakt
from modules.tvdb import TVDb
from modules.util import Failed, NotScheduled, NotScheduledRange
from modules.webhooks import Webhooks

logger = util.logger

mediastingers_url = "https://raw.githubusercontent.com/Kometa-Team/Mediastingers/master/stingers.yml"
run_order_options = {
    "collections": "Represents Collection Updates",
    "metadata": "Represents Metadata Updates",
    "overlays": "Represents Overlay Updates",
    "operations": "Represents Operations Updates"
}
sync_modes = {"append": "Only Add Items to the Collection or Playlist", "sync": "Add & Remove Items from the Collection or Playlist"}
filetype_list = {
    "jpg": "Use JPG files for saving Overlays",
    "png": "Use PNG files for saving Overlays",
    "webp_lossy": "Use Lossy WEBP files for saving Overlays",
    "webp_lossless": "Use Lossless WEBP files for saving Overlays"
}
imdb_label_options = {
    "remove": "Remove All IMDb Parental Labels",
    "none": "Add IMDb Parental Labels for None, Mild, Moderate, or Severe",
    "mild": "Add IMDb Parental Labels for Mild, Moderate, or Severe",
    "moderate": "Add IMDb Parental Labels for Moderate or Severe",
    "severe": "Add IMDb Parental Labels for Severe"
}
mass_genre_options = {
    "lock": "Lock Genre", "unlock": "Unlock Genre", "remove": "Remove and Lock Genre", "reset": "Remove and Unlock Genre",
    "tmdb": "Use TMDb Genres", "imdb": "Use IMDb Genres", "omdb": "Use IMDb Genres through OMDb", "tvdb": "Use TVDb Genres",
    "mal": "Use MyAnimeList Genres", "anidb": "Use AniDB Main Tags",
    "anidb_3_0": "Use AniDB Main Tags and All 3 Star Tags and above", "anidb_2_5": "Use AniDB Main Tags and All 2.5 Star Tags and above",
    "anidb_2_0": "Use AniDB Main Tags and All 2 Star Tags and above", "anidb_1_5": "Use AniDB Main Tags and All 1.5 Star Tags and above",
    "anidb_1_0": "Use AniDB Main Tags and All 1 Star Tags and above", "anidb_0_5": "Use AniDB Main Tags and All 0.5 Star Tags and above"
}
mass_content_options = {
    "lock": "Lock Rating", "unlock": "Unlock Rating", "remove": "Remove and Lock Rating", "reset": "Remove and Unlock Rating",
    "omdb": "Use IMDb Rating through OMDb", "mdb": "Use MDBList Rating",
    "mdb_commonsense": "Use Commonsense Rating through MDBList", "mdb_commonsense0": "Use Commonsense Rating with Zero Padding through MDBList",
    "mdb_age_rating": "Use MDBList Age Rating", "mdb_age_rating0": "Use MDBList Age Rating with Zero Padding",
    "mal": "Use MyAnimeList Rating"
}
mass_collection_content_options = {
    "lock": "Lock Rating", "unlock": "Unlock Rating", "remove": "Remove and Lock Rating", "reset": "Remove and Unlock Rating",
    "highest": "Highest Rating in the collection", "lowest": "Lowest Rating in the collection",
    "average": "Highest Rating in the collection"
}
content_rating_default = {
    1: [

    ]

}
mass_studio_options = {
    "lock": "Lock Rating", "unlock": "Unlock Rating", "remove": "Remove and Lock Rating", "reset": "Remove and Unlock Rating",
    "tmdb": "Use TMDb Studio", "anidb": "Use AniDB Animation Work", "mal": "Use MyAnimeList Studio"
}
mass_original_title_options = {
    "lock": "Lock Original Title", "unlock": "Unlock Original Title", "remove": "Remove and Lock Original Title", "reset": "Remove and Unlock Original Title",
    "anidb": "Use AniDB Main Title", "anidb_official": "Use AniDB Official Title based on the language attribute in the config file",
    "mal": "Use MyAnimeList Main Title", "mal_english": "Use MyAnimeList English Title", "mal_japanese": "Use MyAnimeList Japanese Title",
}
mass_available_options = {
    "lock": "Lock Originally Available", "unlock": "Unlock Originally Available", "remove": "Remove and Lock Originally Available", "reset": "Remove and Unlock Originally Available",
    "tmdb": "Use TMDb Release", "omdb": "Use IMDb Release through OMDb", "mdb": "Use MDBList Release", "mdb_digital": "Use MDBList Digital Release", "tvdb": "Use TVDb Release",
    "anidb": "Use AniDB Release", "mal": "Use MyAnimeList Release"
}
mass_image_options = {
    "lock": "Lock Image", "unlock": "Unlock Image", "plex": "Use Plex Images", "tmdb": "Use TMDb Images"
}
mass_episode_rating_options = {
    "lock": "Lock Rating", "unlock": "Unlock Rating", "remove": "Remove and Lock Rating", "reset": "Remove and Unlock Rating",
    "tmdb": "Use TMDb Rating", "imdb": "Use IMDb Rating"
}
mass_rating_options = {
    "lock": "Lock Rating",
    "unlock": "Unlock Rating",
    "remove": "Remove and Lock Rating",
    "reset": "Remove and Unlock Rating",
    "tmdb": "Use TMDb Rating",
    "imdb": "Use IMDb Rating",
    "trakt_user": "Use Trakt User Rating",
    "omdb": "Use IMDb Rating through OMDb",
    "mdb": "Use MDBList Score",
    "mdb_average": "Use MDBList Average Score",
    "mdb_imdb": "Use IMDb Rating through MDBList",
    "mdb_metacritic": "Use Metacritic Rating through MDBList",
    "mdb_metacriticuser": "Use Metacritic User Rating through MDBList",
    "mdb_trakt": "Use Trakt Rating through MDBList",
    "mdb_tomatoes": "Use Rotten Tomatoes Rating through MDBList",
    "mdb_tomatoesaudience": "Use Rotten Tomatoes Audience Rating through MDBList",
    "mdb_tmdb": "Use TMDb Rating through MDBList",
    "mdb_letterboxd": "Use Letterboxd Rating through MDBList",
    "mdb_myanimelist": "Use MyAnimeList Rating through MDBList",
    "anidb_rating": "Use AniDB Rating",
    "anidb_average": "Use AniDB Average",
    "anidb_score": "Use AniDB Review Dcore",
    "mal": "Use MyAnimeList Rating"
}
reset_overlay_options = {"tmdb": "Reset to TMDb poster", "plex": "Reset to Plex Poster"}
library_operations = {
    "assets_for_all": "bool", "split_duplicates": "bool", "update_blank_track_titles": "bool", "remove_title_parentheses": "bool",
    "radarr_add_all_existing": "bool", "radarr_remove_by_tag": "str", "sonarr_add_all_existing": "bool", "sonarr_remove_by_tag": "str",
    "mass_content_rating_update": mass_content_options, "mass_collection_content_rating_update": "dict",
    "mass_genre_update": mass_genre_options, "mass_studio_update": mass_studio_options,
    "mass_audience_rating_update": mass_rating_options, "mass_episode_audience_rating_update": mass_episode_rating_options,
    "mass_critic_rating_update": mass_rating_options, "mass_episode_critic_rating_update": mass_episode_rating_options,
    "mass_user_rating_update": mass_rating_options, "mass_episode_user_rating_update": mass_episode_rating_options,
    "mass_original_title_update": mass_original_title_options, "mass_imdb_parental_labels": imdb_label_options,
    "mass_originally_available_update": mass_available_options, "mass_added_at_update": mass_available_options,
    "mass_collection_mode": "mass_collection_mode", "mass_poster_update": "dict", "mass_background_update": "dict",
    "metadata_backup": "dict", "delete_collections": "dict", "genre_mapper": "dict", "content_rating_mapper": "dict",
}

class ConfigFile:
    def __init__(self, in_request, default_dir, attrs, secrets):
        logger.info("Locating config...")
        config_file = attrs["config_file"]
        if config_file and os.path.exists(config_file):                     self.config_path = os.path.abspath(config_file)
        elif config_file and not os.path.exists(config_file):               raise Failed(f"Config Error: config not found at {os.path.abspath(config_file)}")
        elif os.path.exists(os.path.join(default_dir, "config.yml")):       self.config_path = os.path.abspath(os.path.join(default_dir, "config.yml"))
        else:                                                               raise Failed(f"Config Error: config not found at {os.path.abspath(default_dir)}")
        logger.info(f"Using {self.config_path} as config")
        logger.clear_errors()

        self._mediastingers = None
        self.Requests = in_request
        self.default_dir = default_dir
        self.secrets = secrets
        self.read_only = attrs["read_only"] if "read_only" in attrs else False
        self.no_missing = attrs["no_missing"] if "no_missing" in attrs else None
        self.no_report = attrs["no_report"] if "no_report" in attrs else None
        self.ignore_schedules = attrs["ignore_schedules"] if "ignore_schedules" in attrs else False
        self.start_time = attrs["time_obj"]
        self.run_hour = datetime.strptime(attrs["time"], "%H:%M").hour
        self.requested_collections = None
        if "collections" in attrs and attrs["collections"]:
            self.requested_collections = [s.strip() for s in attrs["collections"].split("|")]
        self.requested_libraries = None
        if "libraries" in attrs and attrs["libraries"]:
            self.requested_libraries = [s.strip() for s in attrs["libraries"].split("|")]
        self.requested_files = None
        if "files" in attrs and attrs["files"]:
            self.requested_files = []
            for s in attrs["files"].split("|"):
                s = s.strip()
                if s:
                    if s.endswith(".yml"):
                        self.requested_files.append(s[:-4])
                    elif s.endswith(".yaml"):
                        self.requested_files.append(s[:-5])
                    else:
                        self.requested_files.append(s)
        self.collection_only = attrs["collection_only"] if "collection_only" in attrs else False
        self.metadata_only = attrs["metadata_only"] if "metadata_only" in attrs else False
        self.operations_only = attrs["operations_only"] if "operations_only" in attrs else False
        self.overlays_only = attrs["overlays_only"] if "overlays_only" in attrs else False
        self.env_plex_url = attrs["plex_url"] if "plex_url" in attrs else ""
        self.env_plex_token = attrs["plex_token"] if "plex_token" in attrs else ""
        self.tpdb_timer = None
        current_time = datetime.now()

        with open(self.config_path, encoding="utf-8") as fp:
            logger.separator("Redacted Config", space=False, border=False, debug=True)
            for line in fp.readlines():
                logger.debug(re.sub(r"(token|client.*|url|api_*key|secret|error|delete|run_start|run_end|version|changes|username|password): .+", r"\1: (redacted)", line.strip("\r\n")))
            logger.debug("")

        self.data = self.Requests.file_yaml(self.config_path).data

        def replace_attr(all_data, in_attr, par):
            if "settings" not in all_data:
                all_data["settings"] = {}
            if par in all_data and all_data[par] and in_attr in all_data[par] and in_attr not in all_data["settings"]:
                all_data["settings"][in_attr] = all_data[par][in_attr]
                del all_data[par][in_attr]
        if "libraries" not in self.data:
            self.data["libraries"] = {}
        if "settings" not in self.data:
            self.data["settings"] = {}
        if "tmdb" not in self.data:
            self.data["tmdb"] = {}
        replace_attr(self.data, "cache", "cache")
        replace_attr(self.data, "cache_expiration", "cache")
        if "config" in self.data:
            del self.data["cache"]
        replace_attr(self.data, "asset_directory", "plex")
        replace_attr(self.data, "sync_mode", "plex")
        replace_attr(self.data, "show_unmanaged", "plex")
        replace_attr(self.data, "show_filtered", "plex")
        replace_attr(self.data, "show_missing", "plex")
        replace_attr(self.data, "save_missing", "plex")
        if self.data["libraries"]:
            for library in self.data["libraries"]:
                if not self.data["libraries"][library]:
                    continue
                if "metadata_path" in self.data["libraries"][library]:
                    logger.warning("Config Warning: metadata_path has been deprecated and split into collection_files and metadata_files, Please visit the wiki to learn more about this transition.")
                    path_dict = self.data["libraries"][library].pop("metadata_path")
                    if "collection_files" not in self.data["libraries"][library]:
                        self.data["libraries"][library]["collection_files"] = path_dict
                    if "metadata_files" not in self.data["libraries"][library]:
                        self.data["libraries"][library]["metadata_files"] = path_dict
                if "overlay_path" in self.data["libraries"][library]:
                    logger.warning("Config Warning: overlay_path has been deprecated in favor of overlay_files, Please visit the wiki to learn more about this transition.")
                    self.data["libraries"][library]["overlay_files"] = self.data["libraries"][library].pop("overlay_path")
                if "radarr_add_all" in self.data["libraries"][library]:
                    self.data["libraries"][library]["radarr_add_all_existing"] = self.data["libraries"][library].pop("radarr_add_all")
                if "sonarr_add_all" in self.data["libraries"][library]:
                    self.data["libraries"][library]["sonarr_add_all_existing"] = self.data["libraries"][library].pop("sonarr_add_all")
                if "plex" in self.data["libraries"][library] and self.data["libraries"][library]["plex"]:
                    replace_attr(self.data["libraries"][library], "asset_directory", "plex")
                    replace_attr(self.data["libraries"][library], "sync_mode", "plex")
                    replace_attr(self.data["libraries"][library], "show_unmanaged", "plex")
                    replace_attr(self.data["libraries"][library], "show_filtered", "plex")
                    replace_attr(self.data["libraries"][library], "show_missing", "plex")
                    replace_attr(self.data["libraries"][library], "save_missing", "plex")
                if "settings" in self.data["libraries"][library] and self.data["libraries"][library]["settings"]:
                    if "collection_minimum" in self.data["libraries"][library]["settings"]:
                        self.data["libraries"][library]["settings"]["minimum_items"] = self.data["libraries"][library]["settings"].pop("collection_minimum")
                    if "save_missing" in self.data["libraries"][library]["settings"]:
                        self.data["libraries"][library]["settings"]["save_report"] = self.data["libraries"][library]["settings"].pop("save_missing")
                if "radarr" in self.data["libraries"][library] and self.data["libraries"][library]["radarr"]:
                    if "monitor" in self.data["libraries"][library]["radarr"] and isinstance(self.data["libraries"][library]["radarr"]["monitor"], bool):
                        self.data["libraries"][library]["radarr"]["monitor"] = True if self.data["libraries"][library]["radarr"]["monitor"] else False
                    if "add" in self.data["libraries"][library]["radarr"]:
                        self.data["libraries"][library]["radarr"]["add_missing"] = self.data["libraries"][library]["radarr"].pop("add")
                if "sonarr" in self.data["libraries"][library] and self.data["libraries"][library]["sonarr"]:
                    if "add" in self.data["libraries"][library]["sonarr"]:
                        self.data["libraries"][library]["sonarr"]["add_missing"] = self.data["libraries"][library]["sonarr"].pop("add")
                if "operations" in self.data["libraries"][library] and self.data["libraries"][library]["operations"]:
                    if "radarr_add_all" in self.data["libraries"][library]["operations"]:
                        self.data["libraries"][library]["operations"]["radarr_add_all_existing"] = self.data["libraries"][library]["operations"].pop("radarr_add_all")
                    if "sonarr_add_all" in self.data["libraries"][library]["operations"]:
                        self.data["libraries"][library]["operations"]["sonarr_add_all_existing"] = self.data["libraries"][library]["operations"].pop("sonarr_add_all")
                    if "mass_imdb_parental_labels" in self.data["libraries"][library]["operations"] and self.data["libraries"][library]["operations"]["mass_imdb_parental_labels"]:
                        if self.data["libraries"][library]["operations"]["mass_imdb_parental_labels"] == "with_none":
                            self.data["libraries"][library]["operations"]["mass_imdb_parental_labels"] = "none"
                        elif self.data["libraries"][library]["operations"]["mass_imdb_parental_labels"] == "without_none":
                            self.data["libraries"][library]["operations"]["mass_imdb_parental_labels"] = "mild"
                if "webhooks" in self.data["libraries"][library] and self.data["libraries"][library]["webhooks"] and "collection_changes" not in self.data["libraries"][library]["webhooks"]:
                    changes = []
                    def hooks(hook_attr):
                        if hook_attr in self.data["libraries"][library]["webhooks"]:
                            changes.extend([w for w in util.get_list(self.data["libraries"][library]["webhooks"].pop(hook_attr), split=False) if w not in changes])
                    hooks("collection_creation")
                    hooks("collection_addition")
                    hooks("collection_removal")
                    hooks("collection_changes")
                    self.data["libraries"][library]["webhooks"]["changes"] = None if not changes else changes if len(changes) > 1 else changes[0]
        if "libraries" in self.data:                   self.data["libraries"] = self.data.pop("libraries")
        if "playlist_files" in self.data:              self.data["playlist_files"] = self.data.pop("playlist_files")
        if "settings" in self.data:
            temp = self.data.pop("settings")
            if "collection_minimum" in temp:
                temp["minimum_items"] = temp.pop("collection_minimum")
            if "playlist_sync_to_user" in temp:
                temp["playlist_sync_to_users"] = temp.pop("playlist_sync_to_user")
            if "save_missing" in temp:
                temp["save_report"] = temp.pop("save_missing")
            self.data["settings"] = temp
        if "webhooks" in self.data:
            temp = self.data.pop("webhooks")
            if "changes" not in temp:
                changes = []
                def hooks(hook_attr):
                    if hook_attr in temp:
                        items = util.get_list(temp.pop(hook_attr), split=False)
                        if items:
                            changes.extend([w for w in items if w not in changes])
                hooks("collection_creation")
                hooks("collection_addition")
                hooks("collection_removal")
                hooks("collection_changes")
                temp["changes"] = None if not changes else changes if len(changes) > 1 else changes[0]
            self.data["webhooks"] = temp
        if "github" in self.data:                      self.data["github"] = self.data.pop("github")
        if "plex" in self.data:                        self.data["plex"] = self.data.pop("plex")
        if "tmdb" in self.data:                        self.data["tmdb"] = self.data.pop("tmdb")
        if "tautulli" in self.data:                    self.data["tautulli"] = self.data.pop("tautulli")
        if "omdb" in self.data:                        self.data["omdb"] = self.data.pop("omdb")
        if "mdblist" in self.data:                     self.data["mdblist"] = self.data.pop("mdblist")
        if "notifiarr" in self.data:                   self.data["notifiarr"] = self.data.pop("notifiarr")
        if "gotify" in self.data:                      self.data["gotify"] = self.data.pop("gotify")
        if "anidb" in self.data:                       self.data["anidb"] = self.data.pop("anidb")
        if "radarr" in self.data:
            if "monitor" in self.data["radarr"] and isinstance(self.data["radarr"]["monitor"], bool):
                self.data["radarr"]["monitor"] = True if self.data["radarr"]["monitor"] else False
            temp = self.data.pop("radarr")
            if temp and "add" in temp:
                temp["add_missing"] = temp.pop("add")
            self.data["radarr"] = temp
        if "sonarr" in self.data:
            temp = self.data.pop("sonarr")
            if temp and "add" in temp:
                temp["add_missing"] = temp.pop("add")
            self.data["sonarr"] = temp
        if "trakt" in self.data:                       self.data["trakt"] = self.data.pop("trakt")
        if "mal" in self.data:                         self.data["mal"] = self.data.pop("mal")

        def check_next(next_data):
            if isinstance(next_data, dict):
                for d in next_data:
                    out = check_next(next_data[d])
                    if out:
                        next_data[d] = out
            elif isinstance(next_data, list):
                for d in next_data:
                    check_next(d)
            else:
                for secret, secret_value in self.secrets.items():
                    for test in [secret, secret.upper().replace("-", "_")]:
                        if f"<<{test}>>" in str(next_data):
                            return str(next_data).replace(f"<<{test}>>", secret_value)
                return next_data
        if self.secrets:
            check_next(self.data)

        def check_for_attribute(data, attribute, parent=None, test_list=None, translations=None, default=None, do_print=True, default_is_none=False, req_default=False, var_type="str", throw=False, save=True, int_min=0, int_max=None):
            endline = ""
            if parent is not None:
                if data and parent in data:
                    data = data[parent]
                else:
                    data = None
                    do_print = False
                    save = False
            final_value = data[attribute] if data and attribute in data else None
            if translations and final_value in translations:
                final_value = translations[final_value]
            if self.read_only:
                save = False
            text = f"{attribute} attribute" if parent is None else f"{parent} sub-attribute {attribute}"
            if data is None or attribute not in data:
                message = f"{text} not found"
                if parent and save is True:
                    yaml = self.Requests.file_yaml(self.config_path)
                    endline = f"\n{parent} sub-attribute {attribute} added to config"
                    if parent not in yaml.data or not yaml.data[parent]:                yaml.data[parent] = {attribute: default}
                    elif attribute not in yaml.data[parent]:                            yaml.data[parent][attribute] = default
                    else:                                                               endline = ""
                    yaml.save()
                if default_is_none and var_type in ["list", "int_list", "lower_list", "list_path"]: return default if default else []
            elif final_value is None:
                if default_is_none and var_type in ["list", "int_list", "lower_list", "list_path"]: return default if default else []
                elif default_is_none:                                               return None
                else:                                                               message = f"{text} is blank"
            elif var_type == "url":
                if final_value.endswith(("\\", "/")):                               return final_value[:-1]
                else:                                                               return final_value
            elif var_type == "bool":
                if isinstance(final_value, bool):                                   return final_value
                else:                                                               message = f"{text} must be either true or false"
            elif var_type == "int":
                if isinstance(final_value, int) and final_value >= int_min and (not int_max or final_value <= int_max):
                    return final_value
                else:
                    message = f"{text} must an integer greater than or equal to {int_min}{f' and less than or equal to {int_max}'}"
            elif var_type == "path":
                if os.path.exists(os.path.abspath(final_value)):                    return final_value
                else:                                                               message = f"Path {os.path.abspath(final_value)} does not exist"
            elif var_type in ["list", "lower_list", "int_list"]:
                output_list = []
                for output_item in util.get_list(final_value, lower=var_type == "lower_list", split=var_type != "list", int_list=var_type == "int_list"):
                    if output_item not in output_list:
                        output_list.append(output_item)
                failed_items = [o for o in output_list if o not in test_list] if test_list else []
                if failed_items:
                    message = f"{text}: {', '.join(failed_items)} is an invalid input"
                else:
                    return output_list
            elif var_type == "list_path":
                temp_list = []
                warning_message = ""
                for p in util.get_list(final_value, split=False):
                    if os.path.exists(os.path.abspath(p)):
                        temp_list.append(p)
                    else:
                        if len(warning_message) > 0:
                            warning_message += "\n"
                        warning_message += f"Config Warning: Path does not exist: {os.path.abspath(p)}"
                if do_print and warning_message:
                    logger.warning(warning_message)
                if len(temp_list) > 0:                                              return temp_list
                else:                                                               message = "No Paths exist"
            elif test_list is None or final_value in test_list:                 return final_value
            else:                                                               message = f"{text}: {final_value} is an invalid input"
            if var_type == "path" and default and os.path.exists(os.path.abspath(default)):
                return default
            elif var_type == "path" and default:
                if final_value:
                    message = f"neither {final_value} or the default path {default} could be found"
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
                for test_option, test_description in test_list.items():
                    if len(options) > 0:
                        options = f"{options}\n"
                    options = f"{options}    {test_option} ({test_description})"
            if (default is None and not default_is_none) or throw:
                if len(options) > 0:
                    message = message + "\n" + options
                raise Failed(f"Config Error: {message}")
            if do_print:
                logger.warning(f"Config Warning: {message}")
                if final_value and test_list is not None and final_value not in test_list:
                    logger.warning(options)
            return default

        self.general = {
            "run_order": check_for_attribute(self.data, "run_order", parent="settings", var_type="lower_list", test_list=run_order_options, default=["operations", "metadata", "collections", "overlays"]),
            "cache": check_for_attribute(self.data, "cache", parent="settings", var_type="bool", default=True),
            "cache_expiration": check_for_attribute(self.data, "cache_expiration", parent="settings", var_type="int", default=60, int_min=1),
            "asset_directory": check_for_attribute(self.data, "asset_directory", parent="settings", var_type="list_path", default_is_none=True),
            "asset_folders": check_for_attribute(self.data, "asset_folders", parent="settings", var_type="bool", default=True),
            "asset_depth": check_for_attribute(self.data, "asset_depth", parent="settings", var_type="int", default=0),
            "create_asset_folders": check_for_attribute(self.data, "create_asset_folders", parent="settings", var_type="bool", default=False),
            "prioritize_assets": check_for_attribute(self.data, "prioritize_assets", parent="settings", var_type="bool", default=False),
            "dimensional_asset_rename": check_for_attribute(self.data, "dimensional_asset_rename", parent="settings", var_type="bool", default=False),
            "download_url_assets": check_for_attribute(self.data, "download_url_assets", parent="settings", var_type="bool", default=False),
            "show_missing_assets": check_for_attribute(self.data, "show_missing_assets", parent="settings", var_type="bool", default=True),
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
            "show_unconfigured": check_for_attribute(self.data, "show_unconfigured", parent="settings", var_type="bool", default=True),
            "show_filtered": check_for_attribute(self.data, "show_filtered", parent="settings", var_type="bool", default=False),
            "show_options": check_for_attribute(self.data, "show_options", parent="settings", var_type="bool", default=False),
            "show_missing": check_for_attribute(self.data, "show_missing", parent="settings", var_type="bool", default=True),
            "save_report": check_for_attribute(self.data, "save_report", parent="settings", var_type="bool", default=False),
            "tvdb_language": check_for_attribute(self.data, "tvdb_language", parent="settings", default="default"),
            "ignore_ids": check_for_attribute(self.data, "ignore_ids", parent="settings", var_type="int_list", default_is_none=True),
            "ignore_imdb_ids": check_for_attribute(self.data, "ignore_imdb_ids", parent="settings", var_type="lower_list", default_is_none=True),
            "playlist_sync_to_users": check_for_attribute(self.data, "playlist_sync_to_users", parent="settings", default="all", default_is_none=True),
            "playlist_exclude_users": check_for_attribute(self.data, "playlist_exclude_users", parent="settings", default_is_none=True),
            "playlist_report": check_for_attribute(self.data, "playlist_report", parent="settings", var_type="bool", default=True),
            "verify_ssl": check_for_attribute(self.data, "verify_ssl", parent="settings", var_type="bool", default=True, save=False),
            "custom_repo": check_for_attribute(self.data, "custom_repo", parent="settings", default_is_none=True),
            "overlay_artwork_filetype": check_for_attribute(self.data, "overlay_artwork_filetype", parent="settings", test_list=filetype_list, translations={"webp": "webp_lossy"}, default="jpg"),
            "overlay_artwork_quality": check_for_attribute(self.data, "overlay_artwork_quality", parent="settings", var_type="int", default_is_none=True, int_min=1, int_max=100),
            "assets_for_all": check_for_attribute(self.data, "assets_for_all", parent="settings", var_type="bool", default=False, save=False, do_print=False)
        }
        self.custom_repo = None
        if self.general["custom_repo"]:
            repo = self.general["custom_repo"]
            if "https://github.com/" in repo:
                repo = repo.replace("https://github.com/", "https://raw.githubusercontent.com/").replace("/tree/", "/")
            self.custom_repo = repo

        if not self.general["verify_ssl"]:
            self.Requests.no_verify_ssl()

        add_operations = True if "operations" not in self.general["run_order"] else False
        add_metadata = True if "metadata" not in self.general["run_order"] else False
        add_collection = True if "collections" not in self.general["run_order"] else False
        add_overlays = True if "overlays" not in self.general["run_order"] else False
        if add_operations or add_metadata or add_collection or add_overlays:
            new_run_order = []
            for run_order in self.general["run_order"]:
                if add_operations and not new_run_order:
                    new_run_order.append("operations")
                    if add_metadata:
                        new_run_order.append("metadata")
                        if add_collection:
                            new_run_order.append("collections")
                new_run_order.append(run_order)
                if add_metadata and run_order == "operations":
                    new_run_order.append("metadata")
                if add_collection and (run_order == "metadata" or (run_order == "operations" and add_metadata)):
                    new_run_order.append("collections")
            if add_overlays:
                new_run_order.append("overlays")
            self.general["run_order"] = new_run_order

            config_yaml = self.Requests.file_yaml(self.config_path)
            if "settings" not in config_yaml.data or not config_yaml.data["settings"]:
                config_yaml.data["settings"] = {}
            config_yaml.data["settings"]["run_order"] = new_run_order
            config_yaml.save()

        if self.general["cache"]:
            logger.separator()
            self.Cache = Cache(self.config_path, self.general["cache_expiration"])
        else:
            self.Cache = None
        self.GitHub = GitHub(self.Requests, {
            "token": check_for_attribute(self.data, "token", parent="github", default_is_none=True)
        })

        logger.separator()

        self.NotifiarrFactory = None
        if "notifiarr" in self.data:
            logger.info("Connecting to Notifiarr...")
            try:
                self.NotifiarrFactory = Notifiarr(self.Requests, {
                    "apikey": check_for_attribute(self.data, "apikey", parent="notifiarr", throw=True)
                })
            except Failed as e:
                if str(e).endswith("is blank"):
                    logger.warning(e)
                else:
                    logger.stacktrace()
                    logger.error(e)
            logger.info(f"Notifiarr Connection {'Failed' if self.NotifiarrFactory is None else 'Successful'}")
        else:
            logger.info("notifiarr attribute not found")

        self.GotifyFactory = None
        if "gotify" in self.data:
            logger.info("Connecting to Gotify...")
            try:
                self.GotifyFactory = Gotify(self.Requests, {
                    "url": check_for_attribute(self.data, "url", parent="gotify", throw=True),
                    "token": check_for_attribute(self.data, "token", parent="gotify", throw=True)
                })
            except Failed as e:
                if str(e).endswith("is blank"):
                    logger.warning(e)
                else:
                    logger.stacktrace()
                    logger.error(e)
            logger.info(f"Gotify Connection {'Failed' if self.GotifyFactory is None else 'Successful'}")
        else:
            logger.info("gotify attribute not found")

        self.webhooks = {
            "error": check_for_attribute(self.data, "error", parent="webhooks", var_type="list", default_is_none=True),
            "version": check_for_attribute(self.data, "version", parent="webhooks", var_type="list", default_is_none=True),
            "run_start": check_for_attribute(self.data, "run_start", parent="webhooks", var_type="list", default_is_none=True),
            "run_end": check_for_attribute(self.data, "run_end", parent="webhooks", var_type="list", default_is_none=True),
            "changes": check_for_attribute(self.data, "changes", parent="webhooks", var_type="list", default_is_none=True),
            "delete": check_for_attribute(self.data, "delete", parent="webhooks", var_type="list", default_is_none=True)
        }
        self.Webhooks = Webhooks(self, self.webhooks, notifiarr=self.NotifiarrFactory, gotify=self.GotifyFactory)
        try:
            self.Webhooks.start_time_hooks(self.start_time)
            if self.Requests.has_new_version():
                self.Webhooks.version_hooks()
        except Failed as e:
            logger.stacktrace()
            logger.error(f"Webhooks Error: {e}")

        logger.save_errors = True
        logger.separator()

        try:
            self.TMDb = None
            if "tmdb" in self.data:
                logger.info("Connecting to TMDb...")
                self.TMDb = TMDb(self, {
                    "apikey": check_for_attribute(self.data, "apikey", parent="tmdb", throw=True),
                    "language": check_for_attribute(self.data, "language", parent="tmdb", default="en"),
                    "expiration": check_for_attribute(self.data, "cache_expiration", parent="tmdb", var_type="int", default=60, int_min=1)
                })
                regions = {k.upper(): v for k, v in self.TMDb.iso_3166_1.items()}
                region = check_for_attribute(self.data, "region", parent="tmdb", test_list=regions, default_is_none=True)
                self.TMDb.region = str(region).upper() if region else region
                logger.info(f"TMDb Connection {'Failed' if self.TMDb is None else 'Successful'}")
            else:
                raise Failed("Config Error: tmdb attribute not found")

            logger.separator()

            self.OMDb = None
            if "omdb" in self.data:
                logger.info("Connecting to OMDb...")
                try:
                    self.OMDb = OMDb(self.Requests, self.Cache, {
                        "apikey": check_for_attribute(self.data, "apikey", parent="omdb", throw=True),
                        "expiration": check_for_attribute(self.data, "cache_expiration", parent="omdb", var_type="int", default=60, int_min=1)
                    })
                except Failed as e:
                    if str(e).endswith("is blank"):
                        logger.warning(e)
                    else:
                        logger.error(e)
                logger.info(f"OMDb Connection {'Failed' if self.OMDb is None else 'Successful'}")
            else:
                logger.info("omdb attribute not found")

            logger.separator()

            self.MDBList = MDBList(self.Requests, self.Cache)
            if "mdblist" in self.data:
                logger.info("Connecting to MDBList...")
                try:
                    self.MDBList.add_key(
                        check_for_attribute(self.data, "apikey", parent="mdblist", throw=True),
                        check_for_attribute(self.data, "cache_expiration", parent="mdblist", var_type="int", default=60, int_min=1)
                    )
                    logger.info("MDBList Connection Successful")
                except Failed as e:
                    if str(e).endswith("is blank"):
                        logger.warning(e)
                    else:
                        logger.error(e)
                    logger.info("MDBList Connection Failed")
            else:
                logger.info("mdblist attribute not found")

            logger.separator()

            self.Trakt = None
            if "trakt" in self.data:
                logger.info("Connecting to Trakt...")
                try:
                    self.Trakt = Trakt(self.Requests, self.read_only, {
                        "client_id": check_for_attribute(self.data, "client_id", parent="trakt", throw=True),
                        "client_secret": check_for_attribute(self.data, "client_secret", parent="trakt", throw=True),
                        "pin":  check_for_attribute(self.data, "pin", parent="trakt", default_is_none=True),
                        "config_path": self.config_path,
                        "authorization": self.data["trakt"]["authorization"] if "authorization" in self.data["trakt"] else None
                    })
                except Failed as e:
                    if str(e).endswith("is blank"):
                        logger.warning(e)
                    else:
                        logger.error(e)
                logger.info(f"Trakt Connection {'Failed' if self.Trakt is None else 'Successful'}")
            else:
                logger.info("trakt attribute not found")

            logger.separator()

            self.MyAnimeList = None
            if "mal" in self.data:
                logger.info("Connecting to My Anime List...")
                try:
                    self.MyAnimeList = MyAnimeList(self.Requests, self.Cache, self.read_only, {
                        "client_id": check_for_attribute(self.data, "client_id", parent="mal", throw=True),
                        "client_secret": check_for_attribute(self.data, "client_secret", parent="mal", throw=True),
                        "localhost_url": check_for_attribute(self.data, "localhost_url", parent="mal", default_is_none=True),
                        "cache_expiration": check_for_attribute(self.data, "cache_expiration", parent="mal", var_type="int", default=60, int_min=1),
                        "config_path": self.config_path,
                        "authorization": self.data["mal"]["authorization"] if "authorization" in self.data["mal"] else None
                    })
                except Failed as e:
                    if str(e).endswith("is blank"):
                        logger.warning(e)
                    else:
                        logger.error(e)
                logger.info(f"My Anime List Connection {'Failed' if self.MyAnimeList is None else 'Successful'}")
            else:
                logger.info("mal attribute not found")

            self.AniDB = AniDB(self.Requests, self.Cache, {
                "language": check_for_attribute(self.data, "language", parent="anidb", default="en")
            })
            if "anidb" in self.data:
                logger.separator()
                logger.info("Connecting to AniDB...")
                try:
                    self.AniDB.authorize(
                        check_for_attribute(self.data, "client", parent="anidb", throw=True),
                        check_for_attribute(self.data, "version", parent="anidb", var_type="int", throw=True),
                        check_for_attribute(self.data, "cache_expiration", parent="anidb", var_type="int", default=60, int_min=1)
                    )
                except Failed as e:
                    if str(e).endswith("is blank"):
                        logger.warning(e)
                    else:
                        logger.error(e)
                logger.info(f"AniDB API Connection {'Successful' if self.AniDB.is_authorized else 'Failed'}")
                try:
                    self.AniDB.login(
                        check_for_attribute(self.data, "username", parent="anidb", throw=True),
                        check_for_attribute(self.data, "password", parent="anidb", throw=True)
                    )
                except Failed as e:
                    if str(e).endswith("is blank"):
                        logger.warning(e)
                    else:
                        logger.error(e)
                logger.info(f"AniDB Login {'Successful' if self.AniDB.username else 'Failed Continuing as Guest'}")

            logger.separator()

            self.playlist_names = []
            self.playlist_files = []
            if "playlist_files" not in self.data:
                logger.info("playlist_files attribute not found")
            elif not self.data["playlist_files"]:
                logger.info("playlist_files attribute is blank")
            else:
                logger.info("")
                logger.info("Reading in Playlist Files")
                files, had_scheduled = util.load_files(self.data["playlist_files"], "playlist_files", schedule=(current_time, self.run_hour, self.ignore_schedules))
                if not files and not had_scheduled:
                    raise Failed("Config Error: No Paths Found for playlist_files")
                for file_type, playlist_file, temp_vars, asset_directory in files:
                    try:
                        playlist_obj = PlaylistFile(self, file_type, playlist_file, temp_vars, asset_directory)
                        self.playlist_names.extend([p for p in playlist_obj.playlists])
                        self.playlist_files.append(playlist_obj)
                    except Failed as e:
                        logger.info("Playlist File Failed To Load")
                        logger.error(e)
                    except NotScheduled as e:
                        logger.info("")
                        logger.separator(f"Skipping {e} Playlist File")

            self.TVDb = TVDb(self.Requests, self.Cache, self.general["tvdb_language"], self.general["cache_expiration"])
            self.IMDb = IMDb(self.Requests, self.Cache, self.default_dir)
            self.Convert = Convert(self.Requests, self.Cache, self.TMDb)
            self.AniList = AniList(self.Requests)
            self.ICheckMovies = ICheckMovies(self.Requests)
            self.Letterboxd = Letterboxd(self.Requests, self.Cache)
            self.BoxOfficeMojo = BoxOfficeMojo(self.Requests, self.Cache)
            self.Reciperr = Reciperr(self.Requests)
            self.Ergast = Ergast(self.Requests, self.Cache)

            logger.separator()

            logger.info("Connecting to Plex Libraries...")

            self.general["plex"] = {
                "url": check_for_attribute(self.data, "url", parent="plex", var_type="url", default_is_none=True),
                "token": check_for_attribute(self.data, "token", parent="plex", default_is_none=True),
                "timeout": check_for_attribute(self.data, "timeout", parent="plex", var_type="int", default=60),
                "verify_ssl": check_for_attribute(self.data, "verify_ssl", parent="plex", var_type="bool", default_is_none=True),
                "db_cache": check_for_attribute(self.data, "db_cache", parent="plex", var_type="int", default_is_none=True)
            }
            for attr in ["clean_bundles", "empty_trash", "optimize"]:
                try:
                    self.general["plex"][attr] = check_for_attribute(self.data, attr, parent="plex", var_type="bool", default=False, throw=True)
                except Failed as e:
                    if "plex" in self.data and attr in self.data["plex"] and self.data["plex"][attr]:
                        self.general["plex"][attr] = self.data["plex"][attr]
                    else:
                        self.general["plex"][attr] = False
                        logger.warning(str(e).replace("Error", "Warning"))
            self.general["radarr"] = {
                "url": check_for_attribute(self.data, "url", parent="radarr", var_type="url", default_is_none=True),
                "token": check_for_attribute(self.data, "token", parent="radarr", default_is_none=True),
                "add_missing": check_for_attribute(self.data, "add_missing", parent="radarr", var_type="bool", default=False),
                "add_existing": check_for_attribute(self.data, "add_existing", parent="radarr", var_type="bool", default=False),
                "upgrade_existing": check_for_attribute(self.data, "upgrade_existing", parent="radarr", var_type="bool", default=False),
                "monitor_existing": check_for_attribute(self.data, "monitor_existing", parent="radarr", var_type="bool", default=False),
                "ignore_cache": check_for_attribute(self.data, "ignore_cache", parent="radarr", var_type="bool", default=False),
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
                "upgrade_existing": check_for_attribute(self.data, "upgrade_existing", parent="sonarr", var_type="bool", default=False),
                "monitor_existing": check_for_attribute(self.data, "monitor_existing", parent="sonarr", var_type="bool", default=False),
                "ignore_cache": check_for_attribute(self.data, "ignore_cache", parent="sonarr", var_type="bool", default=False),
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

            for library_name, lib in libs.items():
                if self.requested_libraries and library_name not in self.requested_libraries:
                    continue
                params = {o: None for o in library_operations}
                params["mapping_name"] = str(library_name)
                params["name"] = str(lib["library_name"]) if lib and "library_name" in lib and lib["library_name"] else str(library_name)
                display_name = f"{params['name']} ({params['mapping_name']})" if lib and "library_name" in lib and lib["library_name"] else params["mapping_name"]

                logger.separator(f"{display_name} Configuration")
                logger.info("")
                logger.info(f"Connecting to {display_name} Library...")

                params["run_order"] = check_for_attribute(lib, "run_order", parent="settings", var_type="lower_list", default=self.general["run_order"], do_print=False, save=False)
                params["asset_directory"] = check_for_attribute(lib, "asset_directory", parent="settings", var_type="list_path", default=self.general["asset_directory"], default_is_none=True, do_print=False, save=False)
                params["asset_folders"] = check_for_attribute(lib, "asset_folders", parent="settings", var_type="bool", default=self.general["asset_folders"], do_print=False, save=False)
                params["asset_depth"] = check_for_attribute(lib, "asset_depth", parent="settings", var_type="int", default=self.general["asset_depth"], do_print=False, save=False)
                params["sync_mode"] = check_for_attribute(lib, "sync_mode", parent="settings", test_list=sync_modes, default=self.general["sync_mode"], do_print=False, save=False)
                params["default_collection_order"] = check_for_attribute(lib, "default_collection_order", parent="settings", default=self.general["default_collection_order"], default_is_none=True, do_print=False, save=False)
                params["show_unmanaged"] = check_for_attribute(lib, "show_unmanaged", parent="settings", var_type="bool", default=self.general["show_unmanaged"], do_print=False, save=False)
                params["show_unconfigured"] = check_for_attribute(lib, "show_unconfigured", parent="settings", var_type="bool", default=self.general["show_unconfigured"], do_print=False, save=False)
                params["show_filtered"] = check_for_attribute(lib, "show_filtered", parent="settings", var_type="bool", default=self.general["show_filtered"], do_print=False, save=False)
                params["show_options"] = check_for_attribute(lib, "show_options", parent="settings", var_type="bool", default=self.general["show_options"], do_print=False, save=False)
                params["show_missing"] = check_for_attribute(lib, "show_missing", parent="settings", var_type="bool", default=self.general["show_missing"], do_print=False, save=False)
                params["show_missing_assets"] = check_for_attribute(lib, "show_missing_assets", parent="settings", var_type="bool", default=self.general["show_missing_assets"], do_print=False, save=False)
                params["save_report"] = check_for_attribute(lib, "save_report", parent="settings", var_type="bool", default=self.general["save_report"], do_print=False, save=False)
                params["missing_only_released"] = check_for_attribute(lib, "missing_only_released", parent="settings", var_type="bool", default=self.general["missing_only_released"], do_print=False, save=False)
                params["only_filter_missing"] = check_for_attribute(lib, "only_filter_missing", parent="settings", var_type="bool", default=self.general["only_filter_missing"], do_print=False, save=False)
                params["create_asset_folders"] = check_for_attribute(lib, "create_asset_folders", parent="settings", var_type="bool", default=self.general["create_asset_folders"], do_print=False, save=False)
                params["dimensional_asset_rename"] = check_for_attribute(lib, "dimensional_asset_rename", parent="settings", var_type="bool", default=self.general["dimensional_asset_rename"], do_print=False, save=False)
                params["prioritize_assets"] = check_for_attribute(lib, "prioritize_assets", parent="settings", var_type="bool", default=self.general["prioritize_assets"], do_print=False, save=False)
                params["download_url_assets"] = check_for_attribute(lib, "download_url_assets", parent="settings", var_type="bool", default=self.general["download_url_assets"], do_print=False, save=False)
                params["show_missing_season_assets"] = check_for_attribute(lib, "show_missing_season_assets", parent="settings", var_type="bool", default=self.general["show_missing_season_assets"], do_print=False, save=False)
                params["show_missing_episode_assets"] = check_for_attribute(lib, "show_missing_episode_assets", parent="settings", var_type="bool", default=self.general["show_missing_episode_assets"], do_print=False, save=False)
                params["show_asset_not_needed"] = check_for_attribute(lib, "show_asset_not_needed", parent="settings", var_type="bool", default=self.general["show_asset_not_needed"], do_print=False, save=False)
                params["minimum_items"] = check_for_attribute(lib, "minimum_items", parent="settings", var_type="int", default=self.general["minimum_items"], do_print=False, save=False)
                params["item_refresh_delay"] = check_for_attribute(lib, "item_refresh_delay", parent="settings", var_type="int", default=self.general["item_refresh_delay"], do_print=False, save=False)
                params["delete_below_minimum"] = check_for_attribute(lib, "delete_below_minimum", parent="settings", var_type="bool", default=self.general["delete_below_minimum"], do_print=False, save=False)
                params["delete_not_scheduled"] = check_for_attribute(lib, "delete_not_scheduled", parent="settings", var_type="bool", default=self.general["delete_not_scheduled"], do_print=False, save=False)
                params["ignore_ids"] = check_for_attribute(lib, "ignore_ids", parent="settings", var_type="int_list", default_is_none=True, do_print=False, save=False)
                params["ignore_ids"].extend([i for i in self.general["ignore_ids"] if i not in params["ignore_ids"]])
                params["ignore_imdb_ids"] = check_for_attribute(lib, "ignore_imdb_ids", parent="settings", var_type="lower_list", default_is_none=True, do_print=False, save=False)
                params["ignore_imdb_ids"].extend([i for i in self.general["ignore_imdb_ids"] if i not in params["ignore_imdb_ids"]])
                params["overlay_artwork_filetype"] = check_for_attribute(lib, "overlay_artwork_filetype", parent="settings", test_list=filetype_list, translations={"webp": "webp_lossy"}, default=self.general["overlay_artwork_filetype"], do_print=False, save=False)
                params["overlay_artwork_quality"] = check_for_attribute(lib, "overlay_artwork_quality", parent="settings", var_type="int", default=self.general["overlay_artwork_quality"], default_is_none=True, int_min=1, int_max=100, do_print=False, save=False)
                params["changes_webhooks"] = check_for_attribute(lib, "changes", parent="webhooks", var_type="list", default=self.webhooks["changes"], do_print=False, save=False, default_is_none=True)
                params["report_path"] = None
                if lib and "report_path" in lib and lib["report_path"]:
                    if os.path.exists(os.path.dirname(os.path.abspath(lib["report_path"]))):
                        params["report_path"] = lib["report_path"]
                    else:
                        logger.error(f"Config Error: Folder {os.path.dirname(os.path.abspath(lib['report_path']))} does not exist")
                if lib and "operations" in lib and lib["operations"]:
                    final_operations = {}
                    logger.separator("Operation Configuration", space=False, border=False)
                    config_ops = util.parse("Config", "operations", lib["operations"], datatype="listdict")
                    op_size = len(config_ops)
                    for i, config_op in enumerate(config_ops, 1):
                        logger.info("")
                        logger.info(f"Operation {i}/{op_size}")
                        for k, v in config_op.items():
                            logger.info(f"    {k}: {v}")
                        if "schedule" in config_op and not self.ignore_schedules:
                            if not config_op["schedule"]:
                                logger.error("Config Error: schedule attribute is blank")
                            else:
                                try:
                                    util.schedule_check("schedule", config_op["schedule"], current_time, self.run_hour)
                                except NotScheduled:
                                    logger.info(f"Skipping Operation Not Scheduled for {config_op['schedule']}")
                                    continue
                        if "delete_collections" not in config_op and ("delete_unmanaged_collections" in config_op or "delete_collections_with_less" in config_op):
                            config_op["delete_collections"] = {}
                            if "delete_unmanaged_collections" in config_op:
                                config_op["delete_collections"]["unmanaged"] = check_for_attribute(config_op, "delete_unmanaged_collections", var_type="bool", default=False, save=False)
                            if "delete_collections_with_less" in config_op:
                                config_op["delete_collections"]["less"] = check_for_attribute(config_op, "delete_collections_with_less", var_type="int", default_is_none=True, save=False)
                        section_final = {}
                        for op, data_type in library_operations.items():
                            if op not in config_op:
                                continue
                            if op == "mass_imdb_parental_labels":
                                section_final[op] = check_for_attribute(config_op, op, test_list=data_type, default_is_none=True, save=False)
                            elif isinstance(data_type, dict):
                                try:
                                    if not config_op[op]:
                                        raise Failed("is blank")
                                    input_list = config_op[op] if isinstance(config_op[op], list) else [config_op[op]]
                                    final_list = []
                                    for list_attr in input_list:
                                        if not list_attr:
                                            raise Failed(f"has a blank value")
                                        if str(list_attr).lower() in data_type:
                                            final_list.append(str(list_attr).lower())
                                        elif op in ["mass_content_rating_update", "mass_studio_update", "mass_original_title_update"]:
                                            final_list.append(str(list_attr))
                                        elif op == "mass_genre_update":
                                            final_list.append(list_attr if isinstance(list_attr, list) else [list_attr])
                                        elif op in ["mass_originally_available_update", "mass_added_at_update"]:
                                            final_list.append(util.validate_date(list_attr))
                                        elif op.endswith("rating_update"):
                                            final_list.append(util.check_int(list_attr, datatype="float", minimum=0, maximum=10, throw=True))
                                        else:
                                            raise Failed(f"has an invalid value: {list_attr}")
                                    section_final[op] = final_list
                                except Failed as e:
                                    logger.error(f"Config Error: {op} {e}")
                            elif op == "mass_collection_mode":
                                section_final[op] = util.check_collection_mode(config_op[op])
                            elif data_type == "dict":
                                input_dict = config_op[op]
                                if op in ["mass_poster_update", "mass_background_update", "mass_collection_content_rating_update"] and input_dict and not isinstance(input_dict, dict):
                                    input_dict = {"source": input_dict}

                                if not input_dict or not isinstance(input_dict, dict):
                                    raise Failed(f"Config Error: {op} must be a dictionary")
                                elif op in ["mass_poster_update", "mass_background_update"]:
                                    section_final[op] = {
                                        "source": check_for_attribute(input_dict, "source", test_list=mass_image_options, default_is_none=True, save=False),
                                        "seasons": check_for_attribute(input_dict, "seasons", var_type="bool", default=True, save=False),
                                        "episodes": check_for_attribute(input_dict, "episodes", var_type="bool", default=True, save=False),
                                    }
                                elif op == "metadata_backup":
                                    default_path = os.path.join(default_dir, f"{str(library_name)}_Metadata_Backup.yml")
                                    if "path" not in input_dict:
                                        logger.warning(f"Config Warning: path attribute not found using default: {default_path}")
                                    elif "path" in input_dict and not input_dict["path"]:
                                        logger.warning(f"Config Warning: path attribute blank using default: {default_path}")
                                    else:
                                        default_path = input_dict["path"]
                                    section_final[op] = {
                                        "path": default_path,
                                        "exclude": check_for_attribute(input_dict, "exclude", var_type="lower_list", default_is_none=True, save=False),
                                        "sync_tags": check_for_attribute(input_dict, "sync_tags", var_type="bool", default=False, save=False),
                                        "add_blank_entries": check_for_attribute(input_dict, "add_blank_entries", var_type="bool", default=True, save=False)
                                    }
                                elif "mapper" in op:
                                    section_final[op] = {}
                                    for old_value, new_value in input_dict.items():
                                        if not old_value:
                                            logger.warning("Config Warning: The key cannot be empty")
                                        elif new_value and str(old_value) == str(new_value):
                                            logger.warning(f"Config Warning: {op} value '{new_value}' ignored as it cannot be mapped to itself")
                                        else:
                                            section_final[op][str(old_value)] = str(new_value) if new_value else None # noqa
                                elif op == "delete_collections":
                                    section_final[op] = {
                                        "managed": check_for_attribute(input_dict, "managed", var_type="bool", default_is_none=True, save=False),
                                        "configured": check_for_attribute(input_dict, "configured", var_type="bool", default_is_none=True, save=False),
                                        "less": check_for_attribute(input_dict, "less", var_type="int", default_is_none=True, save=False, int_min=1),
                                    }
                                elif op == "mass_collection_content_rating_update":
                                    section_final[op] = {
                                        "source": check_for_attribute(input_dict, "source", test_list=mass_collection_content_options, default_is_none=True, save=False),
                                        "ranking": check_for_attribute(input_dict, "ranking", var_type="list", default=content_rating_default, save=False),
                                    }
                            else:
                                section_final[op] = check_for_attribute(config_op, op, var_type=data_type, default=False, save=False)

                        for k, v in section_final.items():
                            if k not in final_operations:
                                final_operations[k] = v
                            else:
                                logger.warning(f"Config Warning: Operation {k} already scheduled")
                    for k, v in final_operations.items():
                        params[k] = v

                for mass_key in operations.meta_operations:
                    if not params[mass_key]:
                        continue
                    sources = params[mass_key]["source"] if isinstance(params[mass_key], dict) else params[mass_key]
                    if not isinstance(sources, list):
                        sources = [sources]
                    try:
                        for source in sources:
                            if source and source == "omdb" and self.OMDb is None:
                                raise Failed(f"{source} without a successful OMDb Connection")
                            if source and str(source).startswith("mdb") and not self.MDBList.has_key:
                                raise Failed(f"{source} without a successful MDBList Connection")
                            if source and str(source).startswith("anidb") and not self.AniDB.is_authorized:
                                raise Failed(f"{source} without a successful AniDB Connection")
                            if source and str(source).startswith("mal") and self.MyAnimeList is None:
                                raise Failed(f"{source} without a successful MyAnimeList Connection")
                            if source and str(source).startswith("trakt") and self.Trakt is None:
                                raise Failed(f"{source} without a successful Trakt Connection")
                    except Failed as e:
                        logger.error(f"Config Error: {mass_key} cannot use {e}")
                        params[mass_key] = None

                lib_vars = {}
                if lib and "template_variables" in lib and lib["template_variables"] and isinstance(lib["template_variables"], dict):
                    lib_vars = lib["template_variables"]

                params["collection_files"] = []
                try:
                    if lib and "collection_files" in lib:
                        logger.info("")
                        logger.info("Reading in Collection Files")
                        if not lib["collection_files"]:
                            raise Failed("Config Error: collection_files attribute is blank")
                        files, had_scheduled = util.load_files(lib["collection_files"], "collection_files", schedule=(current_time, self.run_hour, self.ignore_schedules), lib_vars=lib_vars)
                        if files:
                            params["collection_files"] = files
                        elif not had_scheduled:
                            raise Failed("Config Error: No Paths Found for collection_files")
                except Failed as e:
                    logger.error(e)

                params["metadata_files"] = []
                try:
                    if lib and "metadata_files" in lib:
                        logger.info("")
                        logger.info("Reading in Metadata Files")
                        if not lib["metadata_files"]:
                            raise Failed("Config Error: metadata_files attribute is blank")
                        files, had_scheduled = util.load_files(lib["metadata_files"], "metadata_files", schedule=(current_time, self.run_hour, self.ignore_schedules), lib_vars=lib_vars)
                        if files:
                            params["metadata_files"] = files
                        elif not had_scheduled:
                            raise Failed("Config Error: No Paths Found for metadata_files")
                except Failed as e:
                    logger.error(e)
                params["default_dir"] = default_dir

                params["skip_library"] = False
                if lib and "schedule" in lib and not self.requested_libraries and not self.ignore_schedules:
                    if not lib["schedule"]:
                        logger.error(f"Config Error: schedule attribute is blank")
                    else:
                        logger.debug(f"Value: {lib['schedule']}")
                        try:
                            util.schedule_check("schedule", lib["schedule"], current_time, self.run_hour)
                        except NotScheduled:
                            params["skip_library"] = True

                old_reset = None
                old_schedule = None
                params["overlay_files"] = []
                params["remove_overlays"] = False
                params["reapply_overlays"] = False
                params["reset_overlays"] = None
                if lib and "overlay_files" in lib:
                    try:
                        logger.info("")
                        logger.info("Reading in Overlay Files")
                        if not lib["overlay_files"]:
                            raise Failed("Config Error: overlay_files attribute is blank")
                        files, _ = util.load_files(lib["overlay_files"], "overlay_files", lib_vars=lib_vars)
                        for file in util.get_list(lib["overlay_files"], split=False):
                            if isinstance(file, dict):
                                if ("remove_overlays" in file and file["remove_overlays"] is True) \
                                        or ("remove_overlay" in file and file["remove_overlay"] is True) \
                                        or ("revert_overlays" in file and file["revert_overlays"] is True):
                                    logger.warning("Config Warning: remove_overlays under overlay_files is deprecated it now goes directly under the library attribute.")
                                    params["remove_overlays"] = True
                                if ("reapply_overlays" in file and file["reapply_overlays"] is True) \
                                        or ("reapply_overlay" in file and file["reapply_overlay"] is True):
                                    logger.warning("Config Warning: reapply_overlays under overlay_files is deprecated it now goes directly under the library attribute.")
                                    params["reapply_overlays"] = True
                                if "reset_overlays" in file or "reset_overlay" in file:
                                    attr = f"reset_overlay{'s' if 'reset_overlays' in file else ''}"
                                    logger.warning("Config Warning: reset_overlays under overlay_files is deprecated it now goes directly under the library attribute.")
                                    old_reset = file[attr]
                                if "schedule" in file and file["schedule"]:
                                    logger.warning("Config Warning: schedule under overlay_files is deprecated it now goes directly under the library attribute as schedule_overlays.")
                                    old_schedule = file["schedule"]
                        params["overlay_files"] = files
                    except Failed as e:
                        logger.error(e)

                if lib:
                    if ("remove_overlays" in lib and lib["remove_overlays"] is True) \
                            or ("remove_overlay" in lib and lib["remove_overlay"] is True) \
                            or ("revert_overlays" in lib and lib["revert_overlays"] is True):
                        params["remove_overlays"] = True
                    if ("reapply_overlays" in lib and lib["reapply_overlays"] is True) \
                            or ("reapply_overlay" in lib and lib["reapply_overlay"] is True):
                        params["reapply_overlays"] = True
                    if "reset_overlays" in lib or "reset_overlay" in lib:
                        attr = f"reset_overlay{'s' if 'reset_overlays' in lib else ''}"
                        old_reset = lib[attr]
                    if old_reset is not None:
                        reset_options = old_reset if isinstance(old_reset, list) else [old_reset]
                        final_list = []
                        for reset_option in reset_options:
                            if reset_option and reset_option in reset_overlay_options:
                                final_list.append(reset_option)
                            else:
                                final_text = f"Config Error: reset_overlays attribute {reset_option} invalid. Options: "
                                for option, description in reset_overlay_options.items():
                                    final_text = f"{final_text}\n    {option} ({description})"
                                logger.error(final_text)
                        if final_list:
                            params["reset_overlays"] = final_list
                        else:
                            final_text = f"Config Error: No proper reset_overlays option found. {old_reset}. Options: "
                            for option, description in reset_overlay_options.items():
                                final_text = f"{final_text}\n    {option} ({description})"
                            logger.error(final_text)
                    if "schedule_overlays" in lib or "schedule_overlay" in lib:
                        attr = f"schedule_overlay{'s' if 'schedule_overlays' in lib else ''}"
                        old_schedule = lib[attr]
                    if old_schedule is not None:
                        logger.debug(f"Value: {old_schedule}")
                        err = None
                        try:
                            util.schedule_check("schedule_overlays", old_schedule, current_time, self.run_hour)
                        except NotScheduledRange as e:
                            err = e
                        except NotScheduled as e:
                            if not self.ignore_schedules:
                                err = e
                        if err:
                            logger.info("")
                            logger.info(f"Overlay Schedule:{err}\n\nOverlays not scheduled to run")
                            params["overlay_files"] = []
                            params["remove_overlays"] = False

                if lib and "overlay_files" in lib and not params["overlay_files"] and params["remove_overlays"] is False and params["reset_overlays"] is False:
                    logger.error("Config Error: No Paths Found for overlay_files")

                params["image_files"] = []
                try:
                    if lib and "image_files" in lib:
                        if not lib["image_files"]:
                            raise Failed("Config Error: image_files attribute is blank")
                        files, _ = util.load_files(lib["image_files"], "image_files")
                        if not files:
                            raise Failed("Config Error: No Paths Found for image_files")
                        params["image_files"] = files
                except Failed as e:
                    logger.error(e)

                try:
                    logger.info("")
                    logger.separator("Plex Configuration", space=False, border=False)
                    params["plex"] = {
                        "url": check_for_attribute(lib, "url", parent="plex", var_type="url", default=self.general["plex"]["url"], req_default=True, save=False),
                        "token": check_for_attribute(lib, "token", parent="plex", default=self.general["plex"]["token"], req_default=True, save=False),
                        "timeout": check_for_attribute(lib, "timeout", parent="plex", var_type="int", default=self.general["plex"]["timeout"], save=False),
                        "verify_ssl": check_for_attribute(lib, "verify_ssl", parent="plex", var_type="bool", default=self.general["plex"]["verify_ssl"], default_is_none=True, save=False),
                        "db_cache": check_for_attribute(lib, "db_cache", parent="plex", var_type="int", default=self.general["plex"]["db_cache"], default_is_none=True, save=False)
                    }
                    for attr in ["clean_bundles", "empty_trash", "optimize"]:
                        try:
                            params["plex"][attr] = check_for_attribute(lib, attr, parent="plex", var_type="bool", save=False, throw=True)
                        except Failed:
                            test_attr = lib["plex"][attr] if "plex" in lib and attr in lib["plex"] and lib["plex"][attr] else self.general["plex"][attr]
                            params["plex"][attr] = False
                            if test_attr is not True and test_attr is not False:
                                try:
                                    util.schedule_check(attr, test_attr, current_time, self.run_hour)
                                    params["plex"][attr] = True
                                except NotScheduled:
                                    logger.info(f"Skipping Operation Not Scheduled for {test_attr}")

                    if params["plex"]["url"].lower() == "env":
                        params["plex"]["url"] = self.env_plex_url
                    if params["plex"]["token"].lower() == "env":
                        params["plex"]["token"] = self.env_plex_token
                    library = Plex(self, params)
                    logger.info("")
                    logger.info(f"{display_name} Library Connection Successful")
                    logger.info("")
                    logger.separator("Scanning Files", space=False, border=False)
                    library.scan_files(self.operations_only, self.overlays_only, self.collection_only, self.metadata_only)
                    if not library.collection_files and not library.metadata_files and not library.overlay_files and not library.library_operation and not library.images_files and not self.playlist_files:
                        raise Failed("Config Error: No valid collection file, metadata file, overlay file, image file, playlist file, or library operations found")
                except Failed as e:
                    logger.stacktrace()
                    logger.error(e)
                    logger.info("")
                    logger.info(f"{display_name} Library Connection Failed")
                    continue

                if self.general["radarr"]["url"] or (lib and "radarr" in lib):
                    logger.info("")
                    logger.separator("Radarr Configuration", space=False, border=False)
                    logger.info("")
                    logger.info(f"Connecting to {display_name} library's Radarr...")
                    logger.info("")
                    try:
                        library.Radarr = Radarr(self.Requests, self.Cache, library, {
                            "url": check_for_attribute(lib, "url", parent="radarr", var_type="url", default=self.general["radarr"]["url"], req_default=True, save=False),
                            "token": check_for_attribute(lib, "token", parent="radarr", default=self.general["radarr"]["token"], req_default=True, save=False),
                            "add_missing": check_for_attribute(lib, "add_missing", parent="radarr", var_type="bool", default=self.general["radarr"]["add_missing"], save=False),
                            "add_existing": check_for_attribute(lib, "add_existing", parent="radarr", var_type="bool", default=self.general["radarr"]["add_existing"], save=False),
                            "upgrade_existing": check_for_attribute(lib, "upgrade_existing", parent="radarr", var_type="bool", default=self.general["radarr"]["upgrade_existing"], save=False),
                            "monitor_existing": check_for_attribute(lib, "monitor_existing", parent="radarr", var_type="bool", default=self.general["radarr"]["monitor_existing"], save=False),
                            "ignore_cache": check_for_attribute(lib, "ignore_cache", parent="radarr", var_type="bool", default=self.general["radarr"]["ignore_cache"], save=False),
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
                        logger.stacktrace()
                        logger.error(e)
                        logger.info("")
                    logger.info(f"{display_name} library's Radarr Connection {'Failed' if library.Radarr is None else 'Successful'}")

                if self.general["sonarr"]["url"] or (lib and "sonarr" in lib):
                    logger.info("")
                    logger.separator("Sonarr Configuration", space=False, border=False)
                    logger.info("")
                    logger.info(f"Connecting to {display_name} library's Sonarr...")
                    logger.info("")
                    try:
                        library.Sonarr = Sonarr(self.Requests, self.Cache, library, {
                            "url": check_for_attribute(lib, "url", parent="sonarr", var_type="url", default=self.general["sonarr"]["url"], req_default=True, save=False),
                            "token": check_for_attribute(lib, "token", parent="sonarr", default=self.general["sonarr"]["token"], req_default=True, save=False),
                            "add_missing": check_for_attribute(lib, "add_missing", parent="sonarr", var_type="bool", default=self.general["sonarr"]["add_missing"], save=False),
                            "add_existing": check_for_attribute(lib, "add_existing", parent="sonarr", var_type="bool", default=self.general["sonarr"]["add_existing"], save=False),
                            "upgrade_existing": check_for_attribute(lib, "upgrade_existing", parent="sonarr", var_type="bool", default=self.general["sonarr"]["upgrade_existing"], save=False),
                            "monitor_existing": check_for_attribute(lib, "monitor_existing", parent="sonarr", var_type="bool", default=self.general["sonarr"]["monitor_existing"], save=False),
                            "ignore_cache": check_for_attribute(lib, "ignore_cache", parent="sonarr", var_type="bool", default=self.general["sonarr"]["ignore_cache"], save=False),
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
                        logger.stacktrace()
                        logger.error(e)
                        logger.info("")
                    logger.info(f"{display_name} library's Sonarr Connection {'Failed' if library.Sonarr is None else 'Successful'}")

                if self.general["tautulli"]["url"] or (lib and "tautulli" in lib):
                    logger.info("")
                    logger.separator("Tautulli Configuration", space=False, border=False)
                    logger.info("")
                    logger.info(f"Connecting to {display_name} library's Tautulli...")
                    logger.info("")
                    try:
                        library.Tautulli = Tautulli(self.Requests, library, {
                            "url": check_for_attribute(lib, "url", parent="tautulli", var_type="url", default=self.general["tautulli"]["url"], req_default=True, save=False),
                            "apikey": check_for_attribute(lib, "apikey", parent="tautulli", default=self.general["tautulli"]["apikey"], req_default=True, save=False)
                        })
                    except Failed as e:
                        logger.stacktrace()
                        logger.error(e)
                        logger.info("")
                    logger.info(f"{display_name} library's Tautulli Connection {'Failed' if library.Tautulli is None else 'Successful'}")

                library.Webhooks = Webhooks(self, {}, library=library, notifiarr=self.NotifiarrFactory, gotify=self.GotifyFactory)
                library.Overlays = Overlays(self, library)

                logger.info("")
                self.libraries.append(library)

            logger.separator()

            self.library_map = {_l.original_mapping_name: _l for _l in self.libraries}

            if len(self.libraries) > 0:
                logger.info(f"{len(self.libraries)} Plex Library Connection{'s' if len(self.libraries) > 1 else ''} Successful")
            else:
                raise Failed("Config Error: No libraries were found in config")

            logger.separator()

            if logger.saved_errors:
                self.notify(logger.saved_errors)
        except Exception as e:
            logger.stacktrace()
            self.notify(logger.saved_errors + [e])
            logger.save_errors = False
            logger.clear_errors()
            raise

    def notify(self, text, server=None, library=None, collection=None, playlist=None, critical=True):
        for error in util.get_list(text, split=False):
            try:
                self.Webhooks.error_hooks(error, server=server, library=library, collection=collection, playlist=playlist, critical=critical)
            except Failed as e:
                logger.stacktrace()
                logger.error(f"Webhooks Error: {e}")

    def notify_delete(self, message, server=None, library=None):
        try:
            self.Webhooks.delete_hooks(message, server=server, library=library)
        except Failed as e:
            logger.stacktrace()
            logger.error(f"Webhooks Error: {e}")

    @property
    def mediastingers(self):
        if self._mediastingers is None:
            self._mediastingers = self.Requests.get_yaml(mediastingers_url)
        return self._mediastingers
