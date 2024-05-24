import os, re, time
from arrapi import ArrException
from datetime import datetime
from modules import plex, tmdb, util
from modules.util import Failed, FilterFailed,  NotScheduled, Deleted
from .overlay_config import OverlayConfig
from modules.poster import KometaImage
from plexapi.audio import Artist, Album, Track
from plexapi.exceptions import NotFound
from plexapi.video import Movie, Show, Season, Episode
from urllib.parse import quote
from ._config import *
from ._attribute_setter import BuilderAttributeSetter
from ._validate_methods import BuilderMethodValidator
from ._missing_filters import MissingFiltersUtil

logger = util.logger

__all__ = ["CollectionBuilder", "OverlayConfig"]

class CollectionBuilder:
    def __init__(self, config, metadata, name, data, library=None, overlay=None, extra=None):
        self.config = config
        self.metadata = metadata
        self.mapping_name = name
        self.data = data
        self.library = library
        self.libraries = []
        self.summaries = {}
        self.playlist = library is None
        self.overlay = overlay
        methods = {m.lower(): m for m in self.data}
        if self.playlist:
            self.type = "playlist"
        elif self.overlay:
            self.type = "overlay"
        else:
            self.type = "collection"
        self.Type = self.type.capitalize()

        logger.separator(f"{self.mapping_name} {self.Type}{f' in {self.library.name}' if self.library else ''}")
        logger.info("")
        if extra:
            logger.info(extra)
            logger.info("")

        if f"{self.type}_name" in methods:
            logger.warning(f"Config Warning: Running {self.type}_name as name")
            self.data["name"] = self.data[methods[f"{self.type}_name"]]
            methods["name"] = "name"

        if "template" in methods:
            logger.separator(f"Building Definition From Templates", space=False, border=False)
            logger.debug("")
            named_templates = []
            for original_variables in util.get_list(self.data[methods["template"]], split=False):
                if not isinstance(original_variables, dict):
                    raise Failed(f"{self.Type} Error: template attribute is not a dictionary")
                elif "name" not in original_variables:
                    raise Failed(f"{self.Type} Error: template sub-attribute name is required")
                elif not original_variables["name"]:
                    raise Failed(f"{self.Type} Error: template sub-attribute name cannot be blank")
                named_templates.append(original_variables["name"])
            logger.debug(f"Templates Called: {', '.join(named_templates)}")
            logger.debug("")
            new_variables = {}
            if "variables" in methods:
                logger.debug("")
                logger.debug("Validating Method: variables")
                if not isinstance(self.data[methods["variables"]], dict):
                    raise Failed(f"{self.Type} Error: variables must be a dictionary (key: value pairs)")
                logger.trace(self.data[methods["variables"]])
                new_variables = self.data[methods["variables"]]
            name = self.data[methods["name"]] if "name" in methods else None
            new_attributes = self.metadata.apply_template(name, self.mapping_name, self.data, self.data[methods["template"]], new_variables)
            for attr in new_attributes:
                if attr.lower() not in methods:
                    self.data[attr] = new_attributes[attr]
                    methods[attr.lower()] = attr

        logger.separator(f"Validating {self.mapping_name} Attributes", space=False, border=False)

        self.builder_language = self.metadata.language
        if "language" in methods:
            logger.debug("")
            logger.debug("Validating Method: language")
            if not self.data[methods["language"]]:
                raise Failed(f"{self.Type} Error: language attribute is blank")
            logger.debug(f"Value: {self.data[methods['language']]}")
            if str(self.data[methods["language"]]).lower() not in self.config.GitHub.translation_keys:
                logger.warning(f"Config Error: Language: {str(self.data[methods['language']]).lower()} Not Found using {self.builder_language}. Options: {', '.join(self.config.GitHub.translation_keys)}")
            else:
                self.builder_language = str(self.data[methods["language"]]).lower()

        self.name = None
        if "name" in methods:
            logger.debug("")
            logger.debug("Validating Method: name")
            if not self.data[methods["name"]]:
                raise Failed(f"{self.Type} Error: name attribute is blank")
            logger.debug(f"Value: {self.data[methods['name']]}")
            self.name = str(self.data[methods["name"]])

        english = None
        translations = None

        self.limit = 0
        if "limit" in methods:
            logger.debug("")
            logger.debug("Validating Method: limit")
            if not self.data[methods["limit"]]:
                raise Failed(f"{self.Type} Error: limit attribute is blank")
            self.limit = util.parse(self.Type, "limit", self.data[methods["limit"]], datatype="int", minimum=1)

        en_key = None
        trans_key = None
        if "key_name" in methods:
            english = self.config.GitHub.translation_yaml("en")
            translations = self.config.GitHub.translation_yaml(self.builder_language)
            logger.debug("")
            logger.debug("Validating Method: key_name")
            if not self.data[methods["key_name"]]:
                raise Failed(f"{self.Type} Error: key_name attribute is blank")
            en_key = str(self.data[methods["key_name"]])
            trans_key = en_key
            if self.builder_language != "en":
                key_name_key = None
                for k, v in english["key_names"].items():
                    if en_key == v:
                        key_name_key = k
                        break
                if key_name_key and key_name_key in translations["key_names"]:
                    trans_key = translations["key_names"][key_name_key]
            logger.debug(f"Value: {trans_key}")
        self.key_name = trans_key

        en_name = None
        en_summary = None
        trans_name = None
        trans_summary = None
        if "translation_key" in methods:
            if not english:
                english = self.config.GitHub.translation_yaml("en")
            if not translations:
                translations = self.config.GitHub.translation_yaml(self.builder_language)
            logger.debug("")
            logger.debug("Validating Method: translation_key")
            if not self.data[methods["translation_key"]]:
                raise Failed(f"{self.Type} Error: translation_key attribute is blank")
            logger.debug(f"Value: {self.data[methods['translation_key']]}")
            translation_key = str(self.data[methods["translation_key"]])
            if translation_key not in english["collections"]:
                raise Failed(f"{self.Type} Error: translation_key: {translation_key} is invalid")

            en_name = english["collections"][translation_key]["name"]
            en_summary = english["collections"][translation_key]["summary"]
            if translation_key in translations["collections"]:
                if "name" in translations["collections"][translation_key]:
                    trans_name = translations["collections"][translation_key]["name"]
                if "summary" in translations["collections"][translation_key]:
                    trans_summary = translations["collections"][translation_key]["summary"]
            if "translation_prefix" in methods and self.data[methods["translation_prefix"]]:
                logger.debug("")
                logger.debug("Validating Method: translation_prefix")
                logger.debug(f"Value: {self.data[methods['translation_prefix']]}")
                en_name = f"{self.data[methods['translation_prefix']]}{en_name}"
                trans_name = f"{self.data[methods['translation_prefix']]}{trans_name}"

        if self.name or en_name or trans_name:
            if not english:
                english = self.config.GitHub.translation_yaml("en")
            if not translations:
                translations = self.config.GitHub.translation_yaml(self.builder_language)
            lib_type = self.library.type.lower() if self.library else "item"
            en_vars = {k: v[lib_type] for k, v in english["variables"].items() if lib_type in v and v[lib_type]}
            trans_vars = {k: v[lib_type] for k, v in translations["variables"].items() if lib_type in v and v[lib_type]}
            for k, v in en_vars.items():
                if k not in trans_vars:
                    trans_vars[k] = v

            def apply_vars(input_str, var_set, var_key, var_limit):
                input_str = str(input_str)
                if "<<library_type>>" in input_str:
                    input_str = input_str.replace("<<library_type>>", "<<library_translation>>")
                if "<<library_typeU>>" in input_str:
                    input_str = input_str.replace("<<library_typeU>>", "<<library_translationU>>")
                for ik, iv in var_set.items():
                    if f"<<{ik}>>" in input_str:
                        input_str = input_str.replace(f"<<{ik}>>", str(iv))
                    if f"<<{ik}U>>" in input_str:
                        input_str = input_str.replace(f"<<{ik}U>>", str(iv).capitalize())
                if var_key and "<<key_name>>" in input_str:
                    input_str = input_str.replace("<<key_name>>", str(var_key))
                if var_limit and "<<limit>>" in input_str:
                    input_str = input_str.replace("<<limit>>", str(var_limit))
                return input_str

            if self.name:
                self.name = apply_vars(self.name, trans_vars, trans_key, self.limit)
            if en_name:
                en_name = apply_vars(en_name, en_vars, en_key, self.limit)
            if trans_name:
                trans_name = apply_vars(trans_name, trans_vars, trans_key, self.limit)
            if en_summary:
                en_summary = apply_vars(en_summary, en_vars, en_key, self.limit)
            if trans_summary:
                trans_summary = apply_vars(trans_summary, trans_vars, trans_key, self.limit)

            delete_cols = []
            if (self.name and self.name != en_name) or (not self.name and trans_name and en_name != trans_name):
                delete_cols.append(en_name)
            if self.name and self.name != trans_name and en_name != trans_name:
                delete_cols.append(trans_name)

            if delete_cols:
                if "delete_collections_named" not in methods:
                    self.data["delete_collections_named"] = delete_cols
                    methods["delete_collections_named"] = "delete_collections_named"
                elif not self.data[methods["delete_collections_named"]]:
                    self.data[methods["delete_collections_named"]] = delete_cols
                elif not isinstance(self.data[methods["delete_collections_named"]], list):
                    if self.data[methods["delete_collections_named"]] not in delete_cols:
                        delete_cols.append(self.data[methods["delete_collections_named"]])
                    self.data[methods["delete_collections_named"]] = delete_cols
                else:
                    self.data[methods["delete_collections_named"]].extend([d for d in delete_cols if d not in self.data[methods["delete_collections_named"]]])

            if not self.name:
                self.name = trans_name if trans_name else en_name
            logger.info(f"Final Name: {self.name}")
            if en_summary or trans_summary:
                self.summaries["translation"] = trans_summary if trans_summary else en_summary

        if not self.name:
            self.name = self.mapping_name

        if self.library and self.name not in self.library.collections:
            self.library.collections.append(self.name)

        if self.playlist:
            if "libraries" not in methods:
                raise Failed("Playlist Error: libraries attribute is required")
            logger.debug("")
            logger.debug("Validating Method: libraries")
            if not self.data[methods["libraries"]]:
                raise Failed(f"{self.Type} Error: libraries attribute is blank")
            logger.debug(f"Value: {self.data[methods['libraries']]}")
            for pl_library in util.get_list(self.data[methods["libraries"]]):
                if str(pl_library) not in config.library_map:
                    raise Failed(f"Playlist Error: Library: {pl_library} not defined")
                self.libraries.append(config.library_map[pl_library])
            self.library = self.libraries[0]

        try:
            self.obj = self.library.get_playlist(self.name) if self.playlist else self.library.get_collection(self.name, force_search=True)
        except Failed:
            self.obj = None

        self.only_run_on_create = False
        if "only_run_on_create" in methods and not self.playlist:
            logger.debug("")
            logger.debug("Validating Method: only_run_on_create")
            logger.debug(f"Value: {data[methods['only_run_on_create']]}")
            self.only_run_on_create = util.parse(self.Type, "only_run_on_create", self.data, datatype="bool", methods=methods, default=False)
        if self.obj and self.only_run_on_create:
            raise NotScheduled("Skipped because only_run_on_create is True and the collection already exists")

        if "allowed_library_types" in methods and "run_definition" not in methods:
            logger.warning(f"{self.Type} Warning: allowed_library_types will run as run_definition")
            methods["run_definition"] = methods["allowed_library_types"]

        if "run_definition" in methods:
            logger.debug("")
            logger.debug("Validating Method: run_definition")
            if self.data[methods["run_definition"]] is None:
                raise NotScheduled("Skipped because run_definition has no value")
            logger.debug(f"Value: {self.data[methods['run_definition']]}")
            valid_options = ["true", "false"] + plex.library_types
            for library_type in util.get_list(self.data[methods["run_definition"]], lower=True):
                if library_type not in valid_options:
                    raise Failed(f"{self.Type} Error: {library_type} is invalid. Options: true, false, {', '.join(plex.library_types)}")
                elif library_type == "false":
                    raise NotScheduled(f"Skipped because run_definition is false")
                elif library_type != "true" and self.library and library_type != self.library.Plex.type:
                    raise NotScheduled(f"Skipped because run_definition library_type: {library_type} doesn't match")

        if self.playlist:               self.builder_level = "item"
        elif self.library.is_show:      self.builder_level = "show"
        elif self.library.is_music:     self.builder_level = "artist"
        else:                           self.builder_level = "movie"
        level = None
        for level_attr in ["builder_level", "collection_level", "overlay_level"]:
            if level_attr in methods:
                level = self.data[methods[level_attr]]
                if level_attr != "builder_level":
                    logger.warning(f"Collection Warning: {level_attr} attribute will run as builder_level")
                break

        if level and not self.playlist and not self.library.is_movie:
            logger.debug("")
            logger.debug("Validating Method: builder_level")
            if level is None:
                logger.error(f"{self.Type} Error: builder_level attribute is blank")
            else:
                logger.debug(f"Value: {level}")
                level = level.lower()
                if (self.library.is_show and level in plex.builder_level_show_options) or (self.library.is_music and level in plex.builder_level_music_options):
                    self.builder_level = level
                elif (self.library.is_show and level != "show") or (self.library.is_music and level != "artist"):
                    if self.library.is_show:
                        options = "\n\tseason (Collection at the Season Level)\n\tepisode (Collection at the Episode Level)"
                    else:
                        options = "\n\talbum (Collection at the Album Level)\n\ttrack (Collection at the Track Level)"
                    raise Failed(f"{self.Type} Error: {self.data[methods['builder_level']]} builder_level invalid{options}")
        self.parts_collection = self.builder_level in plex.builder_level_options

        self.posters = {}
        self.backgrounds = {}
        if not self.overlay and "kometa_poster" in methods:
            logger.debug("")
            logger.debug("Validating Method: kometa_poster")
            if self.data[methods["kometa_poster"]] is None:
                logger.error(f"{self.Type} Error: kometa_poster attribute is blank")
            logger.debug(f"Value: {data[methods['kometa_poster']]}")
            try:
                self.posters["kometa_poster"] = KometaImage(self.config, self.data[methods["kometa_poster"]], "kometa_poster", playlist=self.playlist)
            except Failed as e:
                logger.error(e)

        if self.overlay:
            if "overlay" in methods:
                overlay_data = data[methods["overlay"]]
            else:
                overlay_data = str(self.mapping_name)
                logger.warning(f"{self.Type} Warning: No overlay attribute using mapping name {self.mapping_name} as the overlay name")
            suppress = []
            if "suppress_overlays" in methods:
                logger.debug("")
                logger.debug("Validating Method: suppress_overlays")
                logger.debug(f"Value: {data[methods['suppress_overlays']]}")
                if data[methods["suppress_overlays"]]:
                    suppress = util.get_list(data[methods["suppress_overlays"]])
                else:
                    logger.error(f"Overlay Error: suppress_overlays attribute is blank")
            self.overlay = OverlayConfig(config, library, metadata, str(self.mapping_name), overlay_data, suppress, self.builder_level)

        self.sync_to_users = None
        self.exclude_users = None
        self.valid_users = []
        if self.playlist:
            if "sync_to_users" in methods or "sync_to_user" in methods:
                s_attr = f"sync_to_user{'s' if 'sync_to_users' in methods else ''}"
                logger.debug("")
                logger.debug(f"Validating Method: {s_attr}")
                logger.debug(f"Value: {self.data[methods[s_attr]]}")
                self.sync_to_users = self.data[methods[s_attr]]
            else:
                self.sync_to_users = config.general["playlist_sync_to_users"]
                logger.warning(f"Playlist Warning: sync_to_users attribute not found defaulting to playlist_sync_to_users: {self.sync_to_users}")

            if "exclude_users" in methods or "exclude_user" in methods:
                s_attr = f"exclude_user{'s' if 'exclude_users' in methods else ''}"
                logger.debug("")
                logger.debug(f"Validating Method: {s_attr}")
                logger.debug(f"Value: {self.data[methods[s_attr]]}")
                self.exclude_users = self.data[methods[s_attr]]
            elif config.general["playlist_exclude_users"]:
                self.exclude_users = config.general["playlist_exclude_users"]
                logger.warning(f"Playlist Warning: exclude_users attribute not found defaulting to playlist_exclude_users: {self.exclude_users}")

            plex_users = self.library.users + [self.library.account.username]

            self.exclude_users = util.get_list(self.exclude_users) if self.exclude_users else []
            for user in self.exclude_users:
                if user not in plex_users:
                    raise Failed(f"Playlist Error: User: {user} not found in plex\nOptions: {plex_users}")

            if self.sync_to_users:
                if str(self.sync_to_users) == "all":
                    self.valid_users = [p for p in plex_users if p not in self.exclude_users]
                else:
                    user_list = self.sync_to_users if isinstance(self.sync_to_users, list) else util.get_list(self.sync_to_users)
                    for user in user_list:
                        if user not in plex_users:
                            raise Failed(f"Playlist Error: User: {user} not found in plex\nOptions: {plex_users}")
                        if user not in self.exclude_users:
                            self.valid_users.append(user)

            if "delete_playlist" in methods:
                logger.debug("")
                logger.debug("Validating Method: delete_playlist")
                logger.debug(f"Value: {data[methods['delete_playlist']]}")
                if util.parse(self.Type, "delete_playlist", self.data, datatype="bool", methods=methods, default=False):
                    for getter in [self.library.get_playlist, self.library.get_playlist_from_users]:
                        try:
                            self.obj = getter(self.name)
                            break
                        except Failed as e:
                            error = e
                    else:
                        logger.error(error)
                    raise Deleted(self.delete())
        else:
            self.libraries.append(self.library)

        self.asset_directory = metadata.asset_directory if metadata.asset_directory else self.library.asset_directory

        self.language = self.library.Plex.language
        self.details = {
            "show_filtered": self.library.show_filtered,
            "show_options": self.library.show_options,
            "show_missing": self.library.show_missing,
            "save_report": self.library.save_report,
            "missing_only_released": self.library.missing_only_released,
            "only_filter_missing": False if self.overlay else self.library.only_filter_missing,
            "asset_folders": self.library.asset_folders,
            "create_asset_folders": self.library.create_asset_folders,
            "delete_below_minimum": self.library.delete_below_minimum,
            "delete_not_scheduled": self.library.delete_not_scheduled,
            "changes_webhooks": self.library.changes_webhooks,
            "cache_builders": 0
        }
        if self.library.mass_collection_mode:
            self.details["collection_mode"] = self.library.mass_collection_mode
        self.item_details = {}
        self.radarr_details = {}
        self.sonarr_details = {}
        self.missing_movies = []
        self.missing_shows = []
        self.missing_parts = []
        self.added_to_radarr = []
        self.added_to_sonarr = []
        self.builders = []
        self.filters = []
        self.has_tmdb_filters = False
        self.has_imdb_filters = False
        self.found_items = []
        self.filtered_items = []
        self.filtered_keys = {}
        self.run_again_movies = []
        self.run_again_shows = []
        self.notification_additions = []
        self.notification_removals = []
        self.items = []
        self.remove_item_map = {}
        self.schedule = ""
        self.beginning_count = 0
        self.default_percent = 50
        self.minimum = self.library.minimum_items
        self.tmdb_region = None
        self.ignore_ids = [i for i in self.library.ignore_ids]
        self.ignore_imdb_ids = [i for i in self.library.ignore_imdb_ids]
        self.server_preroll = None
        self.current_time = datetime.now()
        self.current_year = self.current_time.year
        self.url_theme = None
        self.file_theme = None
        self.sync_to_trakt_list = None
        self.sync_missing_to_trakt_list = False
        self.collection_poster = None
        self.collection_background = None
        self.exists = False
        self.non_existing = False
        self.created = False
        self.deleted = False

        if self.playlist:
            server_check = None
            for pl_library in self.libraries:
                if server_check:
                    if pl_library.PlexServer.machineIdentifier != server_check:
                        raise Failed("Playlist Error: All defined libraries must be on the same server")
                else:
                    server_check = pl_library.PlexServer.machineIdentifier

        BuilderMethodValidator().validate_methods(self, methods, logger)

        attributeSetter = BuilderAttributeSetter()
        attributeSetter.set_attributes(self, methods, logger)

        if "append_label" in methods and not self.playlist and not self.overlay:
            logger.debug("")
            logger.debug("Validating Method: append_label")
            logger.debug(f"Value: {data[methods['append_label']]}")
            append_labels = util.get_list(data[methods["append_label"]])
            if "label.sync" in self.details:
                self.details["label.sync"].extend(append_labels)
            elif "label" in self.details:
                self.details["label"].extend(append_labels)
            else:
                self.details["label"] = append_labels

        if not self.server_preroll and not self.smart_url and not self.blank_collection and len(self.builders) == 0:
            raise Failed(f"{self.Type} Error: No builders were found")

        if self.blank_collection and len(self.builders) > 0:
            raise Failed(f"{self.Type} Error: No builders allowed with blank_collection")

        if not isinstance(self.custom_sort, list) and self.custom_sort and (len(self.builders) > 1 or self.builders[0][0] not in custom_sort_builders):
            raise Failed(f"{self.Type} Error: " + ('Playlists' if self.playlist else 'collection_order: custom') +
                         (f" can only be used with a single builder per {self.type}" if len(self.builders) > 1 else f" cannot be used with {self.builders[0][0]}"))

        if "add_missing" not in self.radarr_details:
            self.radarr_details["add_missing"] = self.library.Radarr.add_missing if self.library.Radarr else False
        if "add_existing" not in self.radarr_details:
            self.radarr_details["add_existing"] = self.library.Radarr.add_existing if self.library.Radarr else False

        if "add_missing" not in self.sonarr_details:
            self.sonarr_details["add_missing"] = self.library.Sonarr.add_missing if self.library.Sonarr else False
        if "add_existing" not in self.sonarr_details:
            self.sonarr_details["add_existing"] = self.library.Sonarr.add_existing if self.library.Sonarr else False

        if self.smart_url or self.collectionless or self.library.is_music:
            self.radarr_details["add_missing"] = False
            self.radarr_details["add_existing"] = False
            self.sonarr_details["add_missing"] = False
            self.sonarr_details["add_existing"] = False

        if (self.radarr_details["add_existing"] or self.sonarr_details["add_existing"]) and not self.parts_collection:
            self.item_details["add_existing"] = True

        if self.collectionless:
            self.details["collection_mode"] = "hide"
            self.sync = True

        if self.smart_url:
            self.sync = False

        self.do_report = not self.config.no_report and (self.details["save_report"])
        self.do_missing = not self.config.no_missing and (self.details["show_missing"] or self.do_report
                                                          or (self.library.Radarr and self.radarr_details["add_missing"])
                                                          or (self.library.Sonarr and self.sonarr_details["add_missing"]))
        if self.build_collection:
            if self.obj and ((self.smart and not self.obj.smart) or (not self.smart and self.obj.smart)):
                logger.info("")
                logger.error(f"{self.Type} Error: Converting {self.obj.title} to a {'smart' if self.smart else 'normal'} collection")
                self.library.delete(self.obj)
                self.obj = None
            if self.smart:
                check_url = self.smart_url if self.smart_url else self.smart_label_url
                if self.obj:
                    if check_url != self.library.smart_filter(self.obj):
                        self.library.update_smart_collection(self.obj, check_url)
                        logger.info(f"Metadata: Smart Collection updated to {check_url}")
                self.beginning_count = len(self.library.fetchItems(check_url)) if check_url else 0
            if self.obj:
                self.exists = True
                if self.sync or self.playlist:
                    self.remove_item_map = {i.ratingKey: i for i in self.library.get_collection_items(self.obj, self.smart_label_collection)}
                if not self.smart:
                    self.beginning_count = len(self.remove_item_map) if self.playlist else self.obj.childCount
        else:
            self.obj = None
            if self.sync:
                logger.warning(f"{self.Type} Error: Sync Mode can only be append when using build_collection: false")
                self.sync = False
            self.run_again = False
        if self.non_existing is not False and self.obj:
            raise NotScheduled(self.non_existing)

        logger.info("")
        logger.info("Validation Successful")
        self.missing_filters_util = MissingFiltersUtil(self, logger)

    def gather_ids(self, method, value):
        expired = None
        list_key = None
        if self.config.Cache and self.details["cache_builders"]:
            list_key, expired = self.config.Cache.query_list_cache(f"{self.library.type}:{method}", str(value), self.details["cache_builders"])
            if list_key and expired is False:
                logger.info(f"Builder: {method} loaded from Cache")
                return self.config.Cache.query_list_ids(list_key)
        if "plex" in method:
            ids = self.library.get_rating_keys(method, value, self.playlist)
        elif "tautulli" in method:
            ids = self.library.Tautulli.get_rating_keys(value, self.playlist)
        elif "anidb" in method:
            anidb_ids = self.config.AniDB.get_anidb_ids(method, value)
            ids = self.config.Convert.anidb_to_ids(anidb_ids, self.library)
        elif "anilist" in method:
            anilist_ids = self.config.AniList.get_anilist_ids(method, value)
            ids = self.config.Convert.anilist_to_ids(anilist_ids, self.library)
        elif "mal" in method:
            mal_ids = self.config.MyAnimeList.get_mal_ids(method, value)
            ids = self.config.Convert.myanimelist_to_ids(mal_ids, self.library)
        elif "tvdb" in method:
            ids = self.config.TVDb.get_tvdb_ids(method, value)
        elif "imdb" in method:
            ids = self.config.IMDb.get_imdb_ids(method, value, self.language)
        elif "icheckmovies" in method:
            ids = self.config.ICheckMovies.get_imdb_ids(method, value, self.language)
        elif "letterboxd" in method:
            ids = self.config.Letterboxd.get_tmdb_ids(method, value, self.language)
        elif "reciperr" in method or "stevenlu" in method:
            ids = self.config.Reciperr.get_imdb_ids(method, value)
        elif "mojo" in method:
            ids = self.config.BoxOfficeMojo.get_imdb_ids(method, value)
        elif "mdblist" in method:
            ids = self.config.MDBList.get_tmdb_ids(method, value, self.library.is_movie if not self.playlist else None)
        elif "tmdb" in method:
            ids = self.config.TMDb.get_tmdb_ids(method, value, self.library.is_movie, self.tmdb_region)
        elif "trakt" in method:
            ids = self.config.Trakt.get_trakt_ids(method, value, self.library.is_movie)
        elif "radarr" in method:
            ids = self.library.Radarr.get_tmdb_ids(method, value)
        elif "sonarr" in method:
            ids = self.library.Sonarr.get_tvdb_ids(method, value)
        else:
            ids = []
            logger.error(f"{self.Type} Error: {method} method not supported")
        if self.config.Cache and self.details["cache_builders"] and ids:
            if list_key:
                self.config.Cache.delete_list_ids(list_key)
            list_key = self.config.Cache.update_list_cache(f"{self.library.type}:{method}", str(value), expired, self.details["cache_builders"])
            self.config.Cache.update_list_ids(list_key, ids)
        return ids

    def filter_and_save_items(self, ids):
        items = []
        if len(ids) > 0:
            total_ids = len(ids)
            logger.debug("")
            logger.debug(f"{total_ids} IDs Found")
            logger.trace(f"IDs: {ids}")
            logger.debug("")
            for i, input_data in enumerate(ids, 1):
                input_id, id_type = input_data
                logger.ghost(f"Parsing ID {i}/{total_ids}")
                rating_keys = []
                if id_type == "ratingKey":
                    rating_keys = int(input_id)
                elif id_type == "imdb":
                    if input_id not in self.ignore_imdb_ids:
                        found = False
                        for pl_library in self.libraries:
                            if input_id in pl_library.imdb_map:
                                found = True
                                rating_keys = pl_library.imdb_map[input_id]
                                break
                        if not found and (self.builder_level == "episode" or self.playlist or self.do_missing):
                            try:
                                _id, tmdb_type = self.config.Convert.imdb_to_tmdb(input_id, fail=True)
                                if tmdb_type == "episode" and (self.builder_level == "episode" or self.playlist):
                                    try:
                                        tmdb_id, season_num, episode_num = _id.split("_")
                                        tvdb_id = self.config.Convert.tmdb_to_tvdb(tmdb_id, fail=True)
                                        tvdb_id = int(tvdb_id)
                                    except Failed as e:
                                        try:
                                            if not self.config.OMDb:
                                                raise Failed("")
                                            if self.config.OMDb.limit:
                                                raise Failed(" and OMDb limit reached.")
                                            omdb_item = self.config.OMDb.get_omdb(input_id)
                                            tvdb_id = omdb_item.series_id
                                            season_num = omdb_item.season_num
                                            episode_num = omdb_item.episode_num
                                            if not tvdb_id or not season_num or not episode_num:
                                                raise Failed(f" and OMDb metadata lookup Failed for IMDb ID: {input_id}")
                                        except Failed as ee:
                                            logger.error(f"{e}{ee}")
                                            continue
                                    for pl_library in self.libraries:
                                        if tvdb_id in pl_library.show_map:
                                            found = True
                                            show_item = pl_library.fetch_item(pl_library.show_map[tvdb_id][0])
                                            try:
                                                items.append(show_item.episode(season=int(season_num), episode=int(episode_num)))
                                            except NotFound:
                                                self.missing_parts.append(f"{show_item.title} Season: {season_num} Episode: {episode_num} Missing")
                                            break
                                    if not found and tvdb_id not in self.missing_shows and self.do_missing:
                                        self.missing_shows.append(tvdb_id)
                                elif tmdb_type == "movie" and self.do_missing and _id not in self.missing_movies:
                                    self.missing_movies.append(_id)
                                elif tmdb_type in ["show", "episode"] and self.do_missing:
                                    if tmdb_type == "episode":
                                        tmdb_id, _, _ = _id.split("_")
                                    else:
                                        tmdb_id = _id
                                    tvdb_id = self.config.Convert.tmdb_to_tvdb(tmdb_id, fail=True)
                                    if tvdb_id not in self.missing_shows:
                                        self.missing_shows.append(tvdb_id)
                            except Failed as e:
                                logger.warning(e)
                                continue
                elif id_type == "tmdb" and not self.parts_collection:
                    input_id = int(input_id)
                    if input_id not in self.ignore_ids:
                        found = False
                        for pl_library in self.libraries:
                            if input_id in pl_library.movie_map:
                                found = True
                                rating_keys = pl_library.movie_map[input_id]
                                break
                        if not found and input_id not in self.missing_movies:
                            self.missing_movies.append(input_id)
                elif id_type == "tvdb_season" and (self.builder_level == "season" or self.playlist):
                    tvdb_id, season_num = input_id.split("_")
                    tvdb_id = int(tvdb_id)
                    found = False
                    for pl_library in self.libraries:
                        if tvdb_id in pl_library.show_map:
                            found = True
                            show_item = pl_library.fetch_item(pl_library.show_map[tvdb_id][0])
                            try:
                                season_obj = show_item.season(season=int(season_num))
                                if self.playlist:
                                    items.extend(season_obj.episodes())
                                else:
                                    items.append(season_obj)
                            except NotFound:
                                self.missing_parts.append(f"{show_item.title} Season: {season_num} Missing")
                            break
                    if not found and tvdb_id not in self.missing_shows:
                        self.missing_shows.append(tvdb_id)
                elif id_type == "tvdb_episode" and (self.builder_level == "episode" or self.playlist):
                    tvdb_id, season_num, episode_num = input_id.split("_")
                    tvdb_id = int(tvdb_id)
                    found = False
                    for pl_library in self.libraries:
                        if tvdb_id in pl_library.show_map:
                            found = True
                            show_item = pl_library.fetch_item(pl_library.show_map[tvdb_id][0])
                            try:
                                items.append(show_item.episode(season=int(season_num), episode=int(episode_num)))
                            except NotFound:
                                self.missing_parts.append(f"{show_item.title} Season: {season_num} Episode: {episode_num} Missing")
                    if not found and tvdb_id not in self.missing_shows and self.do_missing:
                        self.missing_shows.append(tvdb_id)
                elif id_type in ["tvdb", "tmdb_show", "tvdb_season", "tvdb_episode"]:
                    tvdb_season = None
                    if id_type == "tmdb_show":
                        try:
                            tvdb_id = self.config.Convert.tmdb_to_tvdb(input_id, fail=True)
                        except Failed as e:
                            logger.warning(e)
                            continue
                    elif id_type == "tvdb_season":
                        tvdb_id, tvdb_season = input_id.split("_")
                        tvdb_id = int(tvdb_id)
                        tvdb_season = int(tvdb_season)
                    elif id_type == "tvdb_episode":
                        tvdb_id, _, _ = input_id.split("_")
                        tvdb_id = int(tvdb_id)
                    else:
                        tvdb_id = int(input_id)
                    if tvdb_id not in self.ignore_ids:
                        found_keys = None
                        for pl_library in self.libraries:
                            if tvdb_id in pl_library.show_map:
                                found_keys = pl_library.show_map[tvdb_id]
                                break
                        if not found_keys and tvdb_id not in self.missing_shows:
                            self.missing_shows.append(tvdb_id)
                        if found_keys:
                            if self.parts_collection:
                                rating_keys = []
                                for rk in found_keys:
                                    try:
                                        item = self.library.fetch_item(rk)
                                        if self.builder_level == "episode" and isinstance(item, Show):
                                            if tvdb_season is not None:
                                                item = item.season(season=tvdb_season)
                                            rating_keys.extend([k.ratingKey for k in item.episodes()])
                                        elif self.builder_level == "season" and isinstance(item, Show):
                                            rating_keys.extend([k.ratingKey for k in item.seasons()])
                                    except Failed as e:
                                        logger.error(e)
                            else:
                                rating_keys = found_keys
                else:
                    continue

                if not isinstance(rating_keys, list):
                    rating_keys = [rating_keys]
                for rk in rating_keys:
                    try:
                        item = self.library.fetch_item(rk)
                        if self.playlist and isinstance(item, (Show, Season)):
                            items.extend(item.episodes())
                        elif self.builder_level == "movie" and not isinstance(item, Movie):
                            logger.info(f"Item: {item} is not an Movie")
                        elif self.builder_level == "show" and not isinstance(item, Show):
                            logger.info(f"Item: {item} is not an Show")
                        elif self.builder_level == "episode" and not isinstance(item, Episode):
                            logger.info(f"Item: {item} is not an Episode")
                        elif self.builder_level == "season" and not isinstance(item, Season):
                            logger.info(f"Item: {item} is not a Season")
                        elif self.builder_level == "artist" and not isinstance(item, Artist):
                            logger.info(f"Item: {item} is not an Artist")
                        elif self.builder_level == "album" and not isinstance(item, Album):
                            logger.info(f"Item: {item} is not an Album")
                        elif self.builder_level == "track" and not isinstance(item, Track):
                            logger.info(f"Item: {item} is not a Track")
                        else:
                            items.append(item)
                    except Failed as e:
                        logger.error(e)
            logger.exorcise()
        if not items:
            return None
        name = self.obj.title if self.obj else self.name
        total = len(items)
        max_length = len(str(total))
        if self.filters and self.details["show_filtered"] is True:
            logger.info("")
            logger.info("Filtering Builders:")
        filtered_items = []
        for i, item in enumerate(items, 1):
            if not isinstance(item, (Movie, Show, Season, Episode, Artist, Album, Track)):
                logger.error(f"{self.Type} Error: Item: {item} is an invalid type")
                continue
            if item not in self.found_items:
                if item.ratingKey in self.filtered_keys:
                    if self.details["show_filtered"] is True:
                        logger.info(f"{name} {self.Type} | X | {self.filtered_keys[item.ratingKey]}")
                else:
                    current_title = util.item_title(item)
                    if self.check_filters(item, f"{(' ' * (max_length - len(str(i))))}{i}/{total}"):
                        self.found_items.append(item)
                    else:
                        filtered_items.append(item)
                        self.filtered_keys[item.ratingKey] = current_title
                        if self.details["show_filtered"] is True:
                            logger.info(f"{name} {self.Type} | X | {current_title}")
        if self.do_report and filtered_items:
            self.library.add_filtered(self.name, [(i.title, self.library.get_id_from_maps(i.ratingKey)) for i in filtered_items], self.library.is_movie)

    def build_filter(self, method, plex_filter, display=False, default_sort=None):
        if display:
            logger.info("")
            logger.info(f"Validating Method: {method}")
        if plex_filter is None:
            raise Failed(f"{self.Type} Error: {method} attribute is blank")
        if not isinstance(plex_filter, dict):
            raise Failed(f"{self.Type} Error: {method} must be a dictionary: {plex_filter}")
        if display:
            logger.debug(f"Value: {plex_filter}")

        filter_alias = {m.lower(): m for m in plex_filter}

        if "any" in filter_alias and "all" in filter_alias:
            raise Failed(f"{self.Type} Error: Cannot have more then one base")

        if self.builder_level == "item":
            if "type" in filter_alias:
                if plex_filter[filter_alias["type"]] is None:
                    raise Failed(f"{self.Type} Error: type attribute is blank")
                if plex_filter[filter_alias["type"]] not in plex.sort_types:
                    raise Failed(f"{self.Type} Error: type: {plex_filter[filter_alias['type']]} is invalid. Options: {', '.join(plex.sort_types)}")
                sort_type = plex_filter[filter_alias["type"]]
            elif self.library.is_show:
                sort_type = "show"
            elif self.library.is_music:
                sort_type = "artist"
            else:
                sort_type = "movie"
        else:
            sort_type = self.builder_level

        ms = method.split("_")
        filter_details = f"{ms[0].capitalize()} {sort_type.capitalize()} {ms[1].capitalize()}\n"
        type_default_sort, type_key, sorts = plex.sort_types[sort_type]

        sort = []
        if "sort_by" in filter_alias:
            test_sorts = plex_filter[filter_alias["sort_by"]]
            if test_sorts is None:
                raise Failed(f"{self.Type} Error: sort_by attribute is blank")
            if not isinstance(test_sorts, list):
                test_sorts = [test_sorts]
            for test_sort in test_sorts:
                if test_sort not in sorts:
                    raise Failed(f"{self.Type} Error: sort_by: {test_sort} is invalid. Options: {', '.join(sorts)}")
                sort.append(test_sort)
        if not sort:
            sort.append(default_sort if default_sort else type_default_sort)
        filter_details += f"Sort By: {sort}\n"

        limit = None
        if "limit" in filter_alias:
            if plex_filter[filter_alias["limit"]] is None:
                raise Failed(f"{self.Type} Error: limit attribute is blank")
            elif str(plex_filter[filter_alias["limit"]]).lower() == "all":
                filter_details += "Limit: all\n"
            else:
                try:
                    if int(plex_filter[filter_alias["limit"]]) < 1:
                        raise ValueError
                    else:
                        limit = int(plex_filter[filter_alias["limit"]])
                        filter_details += f"Limit: {limit}\n"
                except ValueError:
                    raise Failed(f"{self.Type} Error: limit attribute must be an integer greater than 0")

        validate = True
        if "validate" in filter_alias:
            if plex_filter[filter_alias["validate"]] is None:
                raise Failed(f"{self.Type} Error: validate attribute is blank")
            if not isinstance(plex_filter[filter_alias["validate"]], bool):
                raise Failed(f"{self.Type} Error: validate attribute must be either true or false")
            validate = plex_filter[filter_alias["validate"]]
            filter_details += f"Validate: {validate}\n"

        def _filter(filter_dict, is_all=True, level=1):
            output = ""
            display_out = f"\n{'  ' * level}Match {'all' if is_all else 'any'} of the following:"
            level += 1
            indent = f"\n{'  ' * level}"
            conjunction = f"{'and' if is_all else 'or'}=1&"
            for _key, _data in filter_dict.items():
                attr, modifier, final_attr = self.library.split(_key)

                def build_url_arg(arg, mod=None, arg_s=None, mod_s=None):
                    arg_key = plex.search_translation[attr] if attr in plex.search_translation else attr
                    arg_key = plex.show_translation[arg_key] if self.library.is_show and arg_key in plex.show_translation else arg_key
                    if mod is None:
                        mod = plex.modifier_translation[modifier] if modifier in plex.modifier_translation else modifier
                    if arg_s is None:
                        arg_s = arg
                    if attr in plex.string_attributes and modifier in ["", ".not"]:
                        mod_s = "does not contain" if modifier == ".not" else "contains"
                    elif mod_s is None:
                        mod_s = util.mod_displays[modifier]
                    param_s = plex.search_display[attr] if attr in plex.search_display else attr.title().replace('_', ' ')
                    display_line = f"{indent}{param_s} {mod_s} {arg_s}"
                    return f"{arg_key}{mod}={arg}&", display_line

                error = None
                if final_attr not in plex.searches and not final_attr.startswith(("any", "all")):
                    error = f"{self.Type} Error: {final_attr} is not a valid {method} attribute"
                elif self.library.is_show and final_attr in plex.movie_only_searches:
                    error = f"{self.Type} Error: {final_attr} {method} attribute only works for movie libraries"
                elif self.library.is_movie and final_attr in plex.show_only_searches:
                    error = f"{self.Type} Error: {final_attr} {method} attribute only works for show libraries"
                elif self.library.is_music and final_attr not in plex.music_searches + ["all", "any"]:
                    error = f"{self.Type} Error: {final_attr} {method} attribute does not work for music libraries"
                elif not self.library.is_music and final_attr in plex.music_searches:
                    error = f"{self.Type} Error: {final_attr} {method} attribute only works for music libraries"
                elif _data is not False and _data != 0 and not _data:
                    error = f"{self.Type} Error: {final_attr} {method} attribute is blank"
                else:
                    if final_attr.startswith(("any", "all")):
                        dicts = util.get_list(_data)
                        results = ""
                        display_add = ""
                        for dict_data in dicts:
                            if not isinstance(dict_data, dict):
                                raise Failed(f"{self.Type} Error: {attr} must be either a dictionary or list of dictionaries")
                            inside_filter, inside_display = _filter(dict_data, is_all=attr == "all", level=level)
                            if len(inside_filter) > 0:
                                display_add += inside_display
                                results += f"{conjunction if len(results) > 0 else ''}push=1&{inside_filter}pop=1&"
                    else:
                        validation = self.validate_attribute(attr, modifier, final_attr, _data, validate, plex_search=True)
                        if validation is not False and validation != 0 and not validation:
                            continue
                        elif attr in plex.date_attributes and modifier in ["", ".not"]:
                            last_text = "is not in the last" if modifier == ".not" else "is in the last"
                            last_mod = "%3E%3E" if modifier == "" else "%3C%3C"
                            search_mod = validation[-1]
                            if search_mod == "o":
                                validation = f"{validation[:-1]}mon"
                            results, display_add = build_url_arg(f"-{validation}", mod=last_mod, arg_s=f"{validation} {plex.date_sub_mods[search_mod]}", mod_s=last_text)
                        elif attr == "duration" and modifier in [".gt", ".gte", ".lt", ".lte"]:
                            results, display_add = build_url_arg(validation * 60000)
                        elif modifier == ".rated":
                            results, display_add = build_url_arg(-1, mod="!" if validation else "", arg_s="Rated", mod_s="is" if validation else "is not")
                        elif attr in plex.boolean_attributes:
                            bool_mod = "" if validation else "!"
                            bool_arg = "true" if validation else "false"
                            results, display_add = build_url_arg(1, mod=bool_mod, arg_s=bool_arg, mod_s="is")
                        elif (attr in plex.tag_attributes + plex.string_attributes + plex.year_attributes) and modifier in ["", ".is", ".isnot", ".not", ".begins", ".ends", ".regex"]:
                            results = ""
                            display_add = ""
                            for og_value, result in validation:
                                built_arg = build_url_arg(quote(str(result)) if attr in plex.string_attributes else result, arg_s=og_value)
                                display_add += built_arg[1]
                                results += f"{conjunction if len(results) > 0 else ''}{built_arg[0]}"
                        else:
                            results, display_add = build_url_arg(validation)
                    display_out += display_add
                    output += f"{conjunction if len(output) > 0 else ''}{results}"
                if error:
                    if validate:
                        raise Failed(error)
                    else:
                        logger.error(error)
                        continue
            return output, display_out

        if "any" not in filter_alias and "all" not in filter_alias:
            base_dict = {}
            any_dicts = []
            for alias_key, alias_value in filter_alias.items():
                _, _, final = self.library.split(alias_key)
                if final in plex.and_searches:
                    base_dict[alias_value[:-4]] = plex_filter[alias_value]
                elif final in plex.or_searches:
                    any_dicts.append({alias_value: plex_filter[alias_value]})
                elif final in plex.searches:
                    base_dict[alias_value] = plex_filter[alias_value]
            if len(any_dicts) > 0:
                base_dict["any"] = any_dicts
            base_all = True
            if len(base_dict) == 0:
                raise Failed(f"{self.Type} Error: Must have either any or all as a base for {method}")
        else:
            base = "all" if "all" in filter_alias else "any"
            base_all = base == "all"
            if plex_filter[filter_alias[base]] is None:
                raise Failed(f"{self.Type} Error: {base} attribute is blank")
            if not isinstance(plex_filter[filter_alias[base]], dict):
                raise Failed(f"{self.Type} Error: {base} must be a dictionary: {plex_filter[filter_alias[base]]}")
            base_dict = plex_filter[filter_alias[base]]
        built_filter, filter_text = _filter(base_dict, is_all=base_all)
        filter_details = f"{filter_details}Filter:{filter_text}"
        if len(built_filter) > 0:
            final_filter = built_filter[:-1] if base_all else f"push=1&{built_filter}pop=1"
            filter_url = f"?type={type_key}&{f'limit={limit}&' if limit else ''}sort={'%2C'.join([sorts[s] for s in sort])}&{final_filter}"
        else:
            raise FilterFailed(f"{self.Type} Error: No Plex Filter Created")

        if display:
            logger.debug(f"Smart URL: {filter_url}")
        return type_key, filter_details, filter_url

    def validate_attribute(self, attribute, modifier, final, data, validate, plex_search=False):
        def smart_pair(list_to_pair):
            return [(t, t) for t in list_to_pair] if plex_search else list_to_pair
        if attribute in tag_attributes and modifier in [".regex"]:
            _, names = self.library.get_search_choices(attribute, title=not plex_search, name_pairs=True)
            valid_list = []
            used = []
            for reg in util.validate_regex(data, self.Type, validate=validate):
                for name, key in names:
                    if name not in used and re.compile(reg).search(name):
                        used.append(name)
                        valid_list.append((name, key) if plex_search else name)
            if not valid_list:
                error = f"Plex Error: {attribute}: No matches found with regex pattern {data}"
                if self.details["show_options"]:
                    error += f"\nOptions: {names}"
                if validate:
                    raise Failed(error)
                else:
                    logger.error(error)
            return valid_list
        elif modifier == ".regex":
            return util.validate_regex(data, self.Type, validate=validate)
        elif attribute in string_attributes and modifier in ["", ".not", ".is", ".isnot", ".begins", ".ends"]:
            return smart_pair(util.get_list(data, split=False))
        elif attribute in year_attributes and modifier in ["", ".not", ".gt", ".gte", ".lt", ".lte"]:
            if modifier in ["", ".not"]:
                final_years = []
                values = util.get_list(data)
                for value in values:
                    if str(value).startswith("current_year"):
                        year_values = str(value).split("-")
                        try:
                            final_years.append(datetime.now().year - (0 if len(year_values) == 1 else int(year_values[1].strip())))
                        except ValueError:
                            raise Failed(f"{self.Type} Error: {final} attribute modifier invalid '{year_values[1]}'")
                    else:
                        final_years.append(util.parse(self.Type, final, value, datatype="int"))
                return smart_pair(final_years)
            else:
                if str(data).startswith("current_year"):
                    year_values = str(data).split("-")
                    try:
                        return datetime.now().year - (0 if len(year_values) == 1 else int(year_values[1].strip()))
                    except ValueError:
                        raise Failed(f"{self.Type} Error: {final} attribute modifier invalid '{year_values[1]}'")
                return util.parse(self.Type, final, data, datatype="int", minimum=0)
        elif (attribute in number_attributes and modifier in ["", ".not", ".gt", ".gte", ".lt", ".lte"]) \
                or (attribute in tag_attributes and modifier in [".count_gt", ".count_gte", ".count_lt", ".count_lte"]):
            return util.parse(self.Type, final, data, datatype="int", minimum=0)
        elif attribute == "origin_country":
            return util.get_list(data, upper=True)
        elif attribute in ["original_language", "tmdb_keyword"]:
            return util.get_list(data, lower=True)
        elif attribute in ["tmdb_genre", "tvdb_genre"]:
            return util.get_list(data)
        elif attribute == "history":
            try:
                return util.parse(self.Type, final, data, datatype="int", maximum=30)
            except Failed:
                if str(data).lower() in ["day", "month"]:
                    return data.lower()
                else:
                    raise Failed(f"{self.Type} Error: history attribute invalid: {data} must be a number between 1-30, day, or month")
        elif attribute == "tmdb_type":
            return util.parse(self.Type, final, data, datatype="commalist", options=[v for k, v in tmdb.discover_types.items()])
        elif attribute == "tmdb_status":
            return util.parse(self.Type, final, data, datatype="commalist", options=[v for k, v in tmdb.discover_status.items()])
        elif attribute == "imdb_keyword":
            new_dictionary = {"minimum_votes": 0, "minimum_relevant": 0, "minimum_percentage": 0}
            if isinstance(data, dict) and "keyword" not in data:
                raise Failed(f"{self.Type} Error: imdb_keyword requires the keyword attribute")
            elif isinstance(data, dict):
                dict_methods = {dm.lower(): dm for dm in data}
                new_dictionary["keywords"] = util.parse(self.Type, "keyword", data, methods=dict_methods, parent=attribute, datatype="lowerlist")
                new_dictionary["minimum_votes"] = util.parse(self.Type, "minimum_votes", data, methods=dict_methods, parent=attribute, datatype="int", minimum=0)
                new_dictionary["minimum_relevant"] = util.parse(self.Type, "minimum_relevant", data, methods=dict_methods, parent=attribute, datatype="int", minimum=0)
                new_dictionary["minimum_percentage"] = util.parse(self.Type, "minimum_percentage", data, methods=dict_methods, parent=attribute, datatype="int", minimum=0, maximum=100)
            else:
                new_dictionary["keywords"] = util.parse(self.Type, final, data, datatype="lowerlist")
            return new_dictionary
        elif attribute in tag_attributes and modifier in ["", ".not"]:
            if attribute in plex.tmdb_attributes:
                final_values = []
                for value in util.get_list(data):
                    if value.lower() == "tmdb" and "tmdb_person" in self.details:
                        for name in self.details["tmdb_person"]:
                            final_values.append(name)
                    else:
                        final_values.append(value)
            else:
                final_values = util.get_list(data, trim=False)
            search_choices, names = self.library.get_search_choices(attribute, title=not plex_search)
            valid_list = []
            for fvalue in final_values:
                if str(fvalue) in search_choices or str(fvalue).lower() in search_choices:
                    valid_value = search_choices[str(fvalue) if str(fvalue) in search_choices else str(fvalue).lower()]
                    valid_list.append((fvalue, valid_value) if plex_search else valid_value)
                else:
                    actor_id = None
                    if attribute in ["actor", "director", "producer", "writer"]:
                        actor_id = self.library.get_actor_id(fvalue)
                        if actor_id:
                            if plex_search:
                                valid_list.append((fvalue, actor_id))
                            else:
                                valid_list.append(actor_id)
                    if not actor_id:
                        error = f"Plex Error: {attribute}: {fvalue} not found"
                        if self.details["show_options"]:
                            error += f"\nOptions: {names}"
                        if validate:
                            raise FilterFailed(error)
                        elif not self.ignore_blank_results:
                            logger.error(error)
            return valid_list
        elif attribute in date_attributes and modifier in [".before", ".after"]:
            try:
                return util.validate_date(datetime.now() if data == "today" else data, return_as="%Y-%m-%d")
            except Failed as e:
                raise Failed(f"{self.Type} Error: {final}: {e}")
        elif attribute in date_attributes and modifier in ["", ".not"]:
            search_mod = "d"
            if plex_search and data and str(data)[-1] in ["s", "m", "h", "d", "w", "o", "y"]:
                search_mod = str(data)[-1]
                data = str(data)[:-1]
            search_data = util.parse(self.Type, final, data, datatype="int", minimum=0)
            return f"{search_data}{search_mod}" if plex_search else search_data
        elif attribute in float_attributes and modifier in ["", ".not", ".gt", ".gte", ".lt", ".lte"]:
            return util.parse(self.Type, final, data, datatype="float", minimum=0, maximum=None if attribute == "duration" else 10)
        elif attribute in boolean_attributes or (attribute in float_attributes and modifier in [".rated"]):
            return util.parse(self.Type, attribute, data, datatype="bool")
        elif attribute in ["seasons", "episodes", "albums", "tracks"]:
            if isinstance(data, dict) and data:
                percentage = self.default_percent
                if "percentage" in data:
                    if data["percentage"] is None:
                        logger.warning(f"{self.Type} Warning: percentage filter attribute is blank using {self.default_percent} as default")
                    else:
                        maybe = util.check_num(data["percentage"])
                        if maybe < 0 or maybe > 100:
                            logger.warning(f"{self.Type} Warning: percentage filter attribute must be a number 0-100 using {self.default_percent} as default")
                        else:
                            percentage = maybe
                final_filters = {"percentage": percentage}
                for filter_method, filter_data in data.items():
                    filter_attr, filter_modifier, filter_final = self.library.split(filter_method)
                    message = None
                    if filter_final == "percentage":
                        continue
                    if filter_final not in all_filters:
                        message = f"{self.Type} Error: {filter_final} is not a valid filter attribute"
                    elif filter_attr not in filters[attribute[:-1]] or filter_attr in ["seasons", "episodes", "albums", "tracks"]:
                        message = f"{self.Type} Error: {filter_final} is not a valid {attribute[:-1]} filter attribute"
                    elif filter_final is None:
                        message = f"{self.Type} Error: {filter_final} filter attribute is blank"
                    else:
                        final_filters[filter_final] = self.validate_attribute(filter_attr, filter_modifier, f"{attribute} {filter_final} filter", filter_data, validate)
                    if message:
                        if validate:
                            raise Failed(message)
                        else:
                            logger.error(message)
                if not final_filters:
                    raise Failed(f"{self.Type} Error: no filters found under {attribute}")
                return final_filters
            else:
                raise Failed(f"{self.Type} Error: {final} attribute must be a dictionary")
        else:
            raise Failed(f"{self.Type} Error: {final} attribute not supported")

    def add_to_collection(self):
        logger.info("")
        logger.separator(f"Adding to {self.name} {self.Type}", space=False, border=False)
        logger.info("")
        name, collection_items = self.library.get_collection_name_and_items(self.obj if self.obj else self.name, self.smart_label_collection)
        total = self.limit if self.limit and len(self.found_items) > self.limit else len(self.found_items)
        spacing = len(str(total)) * 2 + 1
        amount_added = 0
        amount_unchanged = 0
        items_added = []
        for i, item in enumerate(self.found_items, 1):
            if self.limit and amount_added + self.beginning_count - len([r for _, r in self.remove_item_map.items() if r is not None]) >= self.limit:
                logger.info(f"{self.Type} Limit reached")
                self.found_items = self.found_items[:i - 1]
                break
            current_operation = "=" if item in collection_items else "+"
            number_text = f"{i}/{total}"
            logger.info(f"{number_text:>{spacing}} | {name} {self.Type} | {current_operation} | {util.item_title(item)}")
            if item in collection_items:
                self.remove_item_map[item.ratingKey] = None
                amount_unchanged += 1
            else:
                items_added.append(item)
                amount_added += 1
                if self.details["changes_webhooks"]:
                    self.notification_additions.append(util.item_set(item, self.library.get_id_from_maps(item.ratingKey)))
        if self.playlist and items_added and not self.obj:
            self.obj = self.library.create_playlist(self.name, items_added)
            logger.info("")
            logger.info(f"Playlist: {self.name} created")
        elif self.playlist and items_added:
            self.obj.addItems(items_added)
        elif items_added:
            self.library.alter_collection(items_added, name, smart_label_collection=self.smart_label_collection)
        if self.do_report and items_added:
            self.library.add_additions(self.name, [(i.title, self.library.get_id_from_maps(i.ratingKey)) for i in items_added], self.library.is_movie)
        logger.exorcise()
        logger.info("")
        item_label = f"{self.builder_level.capitalize()}{'s' if total > 1 else ''}"
        logger.info(f"{total} {item_label} Processed {amount_added} {item_label} Added")
        return amount_added, amount_unchanged

    def sync_collection(self):
        amount_removed = 0
        items_removed = []
        items = [item for _, item in self.remove_item_map.items() if item is not None]
        if items:
            logger.info("")
            logger.separator(f"Removed from {self.name} {self.Type}", space=False, border=False)
            logger.info("")
            total = len(items)
            spacing = len(str(total)) * 2 + 1
            for i, item in enumerate(items, 1):
                number_text = f"{i}/{total}"
                logger.info(f"{number_text:>{spacing}} | {self.name} {self.Type} | - | {util.item_title(item)}")
                items_removed.append(item)
                amount_removed += 1
                if self.details["changes_webhooks"]:
                    self.notification_removals.append(util.item_set(item, self.library.get_id_from_maps(item.ratingKey)))
            if self.playlist and items_removed:
                self.library._reload(self.obj)
                self.obj.removeItems(items_removed)
            elif items_removed:
                self.library.alter_collection(items_removed, self.name, smart_label_collection=self.smart_label_collection, add=False)
            if self.do_report and items_removed:
                self.library.add_removed(self.name, [(i.title, self.library.get_id_from_maps(i.ratingKey)) for i in items_removed], self.library.is_movie)
            logger.info("")
            logger.info(f"{amount_removed} {self.builder_level.capitalize()}{'s' if amount_removed == 1 else ''} Removed")
        return amount_removed

    def check_filters(self, item, display):
        return self.missing_filters_util.check_filters(item, display)

    def log_filters(self):
        if self.filters:
            for filter_list in self.filters:
                logger.info("")
                for filter_key, filter_value in filter_list:
                    logger.info(f"Collection Filter {filter_key}: {filter_value}") 

    def run_missing(self):
        return self.missing_filters_util.run_missing()
    
    def load_collection_items(self):
        if self.build_collection and self.obj:
            self.items = self.library.get_collection_items(self.obj, self.smart_label_collection)
        elif not self.build_collection:
            logger.info("")
            logger.separator(f"Items Found for {self.name} {self.Type}", space=False, border=False)
            logger.info("")
            self.items = self.found_items
        if not self.items:
            raise Failed(f"Plex Error: No {self.Type} items found")

    def update_item_details(self):
        logger.info("")
        logger.separator(f"Updating Metadata of the Items in {self.name} {self.Type}", space=False, border=False)
        logger.info("")

        add_tags = self.item_details["item_label"] if "item_label" in self.item_details else None
        remove_tags = self.item_details["item_label.remove"] if "item_label.remove" in self.item_details else None
        sync_tags = self.item_details["item_label.sync"] if "item_label.sync" in self.item_details else None

        add_genres = self.item_details["item_genre"] if "item_genre" in self.item_details else None
        remove_genres = self.item_details["item_genre.remove"] if "item_genre.remove" in self.item_details else None
        sync_genres = self.item_details["item_genre.sync"] if "item_genre.sync" in self.item_details else None

        if "non_item_remove_label" in self.item_details:
            rk_compare = [item.ratingKey for item in self.items]
            for non_item in self.library.search(label=self.item_details["non_item_remove_label"], libtype=self.builder_level):
                if non_item.ratingKey not in rk_compare:
                    self.library.edit_tags("label", non_item, remove_tags=self.item_details["non_item_remove_label"])

        tmdb_paths = []
        tvdb_paths = []
        for item in self.items:
            item = self.library.reload(item)
            current_labels = [la.tag for la in self.library.item_labels(item)]
            if "item_assets" in self.item_details and self.asset_directory and "Overlay" not in current_labels:
                self.library.find_and_upload_assets(item, current_labels, asset_directory=self.asset_directory)
            self.library.edit_tags("label", item, add_tags=add_tags, remove_tags=remove_tags, sync_tags=sync_tags)
            self.library.edit_tags("genre", item, add_tags=add_genres, remove_tags=remove_genres, sync_tags=sync_genres)
            if "item_edition" in self.item_details and item.editionTitle != self.item_details["item_edition"]:
                self.library.query_data(item.editEditionTitle, self.item_details["item_edition"])
                logger.info(f"{item.title[:25]:<25} | Edition | {self.item_details['item_edition']}")
            path = None
            if "item_radarr_tag" in self.item_details or self.radarr_details["add_existing"] or "item_sonarr_tag" in self.item_details or self.sonarr_details["add_existing"]:
                if item.locations:
                    if self.library.is_movie:
                        path = os.path.dirname(str(item.locations[0]))
                    elif self.library.is_show:
                        path = str(item.locations[0])
                if not path:
                    logger.error(f"Plex Error: No location found for {item.title}: {item.locations}")
            if path and self.library.Radarr and item.ratingKey in self.library.movie_rating_key_map:
                path = path.replace(self.library.Radarr.plex_path, self.library.Radarr.radarr_path)
                path = path[:-1] if path.endswith(('/', '\\')) else path
                tmdb_paths.append((self.library.movie_rating_key_map[item.ratingKey], path))
            if path and self.library.Sonarr and item.ratingKey in self.library.show_rating_key_map:
                path = path.replace(self.library.Sonarr.plex_path, self.library.Sonarr.sonarr_path)
                path = path[:-1] if path.endswith(('/', '\\')) else path
                tvdb_paths.append((self.library.show_rating_key_map[item.ratingKey], path))
            if any([mn in plex.item_advance_keys for mn in self.item_details]) and hasattr(item, "preferences"):
                advance_edits = {}
                prefs = [p.id for p in item.preferences()]
                for method_name, method_data in self.item_details.items():
                    if method_name in plex.item_advance_keys:
                        key, options = plex.item_advance_keys[method_name]
                        if key in prefs and getattr(item, key) != options[method_data]:
                            advance_edits[key] = options[method_data]
                if advance_edits:
                    logger.debug(f"Metadata Update: {advance_edits}")
                    if self.library.edit_advance(item, advance_edits):
                        logger.info(f"{item.title} Advanced Metadata Update Successful")
                    else:
                        logger.error(f"{item.title} Advanced Metadata Update Failed")

            if "item_tmdb_season_titles" in self.item_details and item.ratingKey in self.library.show_rating_key_map:
                try:
                    tmdb_id = self.config.Convert.tvdb_to_tmdb(self.library.show_rating_key_map[item.ratingKey])
                    names = {s.season_number: s.name for s in self.config.TMDb.get_show(tmdb_id).seasons}
                    for season in self.library.query(item.seasons):
                        if season.index in names and season.title != names[season.index]:
                            season.editTitle(names[season.index])
                except Failed as e:
                    logger.error(e)

            # Locking should come before refreshing since refreshing can change metadata (i.e. if specified to both lock
            # background/poster and also refreshing, assume that the item background/poster should be kept)
            if "item_lock_background" in self.item_details:
                self.library.query(item.lockArt if self.item_details["item_lock_background"] else item.unlockArt)
            if "item_lock_poster" in self.item_details:
                self.library.query(item.lockPoster if self.item_details["item_lock_poster"] else item.unlockPoster)
            if "item_lock_title" in self.item_details:
                self.library.edit_query(item, {"title.locked": 1 if self.item_details["item_lock_title"] else 0})
            if "item_refresh" in self.item_details:
                delay = self.item_details["item_refresh_delay"] if "item_refresh_delay" in self.item_details else self.library.item_refresh_delay
                if delay > 0:
                    time.sleep(delay)
                self.library.query(item.refresh)

        if self.library.Radarr and tmdb_paths:
            try:
                if "item_radarr_tag" in self.item_details:
                    self.library.Radarr.edit_tags([t[0] if isinstance(t, tuple) else t for t in tmdb_paths], self.item_details["item_radarr_tag"], self.item_details["apply_tags"])
                if self.radarr_details["add_existing"]:
                    added = self.library.Radarr.add_tmdb(tmdb_paths, **self.radarr_details)
                    self.added_to_radarr.extend([{"title": movie.title, "id": movie.tmdbId} for movie in added])
            except Failed as e:
                logger.error(e)
            except ArrException as e:
                logger.stacktrace()
                logger.error(f"Arr Error: {e}")

        if self.library.Sonarr and tvdb_paths:
            try:
                if "item_sonarr_tag" in self.item_details:
                    self.library.Sonarr.edit_tags([t[0] if isinstance(t, tuple) else t for t in tvdb_paths], self.item_details["item_sonarr_tag"], self.item_details["apply_tags"])
                if self.sonarr_details["add_existing"]:
                    added = self.library.Sonarr.add_tvdb(tvdb_paths, **self.sonarr_details)
                    self.added_to_sonarr.extend([{"title": show.title, "id": show.tvdbId} for show in added])
            except Failed as e:
                logger.error(e)
            except ArrException as e:
                logger.stacktrace()
                logger.error(f"Arr Error: {e}")

    def load_collection(self):
        if self.obj is None and self.smart_url:
            self.library.create_smart_collection(self.name, self.smart_type_key, self.smart_url, self.ignore_blank_results)
            logger.debug(f"Smart Collection Created: {self.smart_url}")
        elif self.obj is None and self.blank_collection:
            self.library.create_blank_collection(self.name)
        elif self.smart_label_collection:
            try:
                if not self.library.smart_label_check(self.name):
                    raise Failed
                smart_type, _, self.smart_url = self.build_filter("smart_label", self.smart_label, default_sort="random")
                if not self.obj:
                    self.library.create_smart_collection(self.name, smart_type, self.smart_url, self.ignore_blank_results)
            except Failed:
                raise Failed(f"{self.Type} Error: Label: {self.name} was not added to any items in the Library")
        self.obj = self.library.get_playlist(self.name) if self.playlist else self.library.get_collection(self.name, force_search=True)
        if not self.exists:
            self.created = True

    def update_details(self):
        updated_details = []
        logger.info("")
        logger.separator(f"Updating Metadata of {self.name} {self.Type}", space=False, border=False)
        logger.info("")
        if "summary" in self.summaries:                     summary = ("summary", self.summaries["summary"])
        elif "translation" in self.summaries:               summary = ("translation", self.summaries["translation"])
        elif "tmdb_description" in self.summaries:          summary = ("tmdb_description", self.summaries["tmdb_description"])
        elif "tvdb_description" in self.summaries:          summary = ("tvdb_description", self.summaries["tvdb_description"])
        elif "letterboxd_description" in self.summaries:    summary = ("letterboxd_description", self.summaries["letterboxd_description"])
        elif "tmdb_summary" in self.summaries:              summary = ("tmdb_summary", self.summaries["tmdb_summary"])
        elif "tvdb_summary" in self.summaries:              summary = ("tvdb_summary", self.summaries["tvdb_summary"])
        elif "tmdb_biography" in self.summaries:            summary = ("tmdb_biography", self.summaries["tmdb_biography"])
        elif "tmdb_person" in self.summaries:               summary = ("tmdb_person", self.summaries["tmdb_person"])
        elif "tmdb_collection_details" in self.summaries:   summary = ("tmdb_collection_details", self.summaries["tmdb_collection_details"])
        elif "trakt_list_details" in self.summaries:        summary = ("trakt_list_details", self.summaries["trakt_list_details"])
        elif "tmdb_list_details" in self.summaries:         summary = ("tmdb_list_details", self.summaries["tmdb_list_details"])
        elif "tvdb_list_details" in self.summaries:         summary = ("tvdb_list_details", self.summaries["tvdb_list_details"])
        elif "letterboxd_list_details" in self.summaries:   summary = ("letterboxd_list_details", self.summaries["letterboxd_list_details"])
        elif "icheckmovies_list_details" in self.summaries: summary = ("icheckmovies_list_details", self.summaries["icheckmovies_list_details"])
        elif "tmdb_actor_details" in self.summaries:        summary = ("tmdb_actor_details", self.summaries["tmdb_actor_details"])
        elif "tmdb_crew_details" in self.summaries:         summary = ("tmdb_crew_details", self.summaries["tmdb_crew_details"])
        elif "tmdb_director_details" in self.summaries:     summary = ("tmdb_director_details", self.summaries["tmdb_director_details"])
        elif "tmdb_producer_details" in self.summaries:     summary = ("tmdb_producer_details", self.summaries["tmdb_producer_details"])
        elif "tmdb_writer_details" in self.summaries:       summary = ("tmdb_writer_details", self.summaries["tmdb_writer_details"])
        elif "tmdb_movie_details" in self.summaries:        summary = ("tmdb_movie_details", self.summaries["tmdb_movie_details"])
        elif "tvdb_movie_details" in self.summaries:        summary = ("tvdb_movie_details", self.summaries["tvdb_movie_details"])
        elif "tvdb_show_details" in self.summaries:         summary = ("tvdb_show_details", self.summaries["tvdb_show_details"])
        elif "tmdb_show_details" in self.summaries:         summary = ("tmdb_show_details", self.summaries["tmdb_show_details"])
        else:                                               summary = (None, None)

        if self.playlist:
            if summary[1]:
                if str(summary[1]) != str(self.obj.summary):
                    try:
                        self.obj.editSummary(str(summary[1]))
                        logger.info(f"Summary ({summary[0]}) | {summary[1]:<25}")
                        logger.info("Metadata: Update Completed")
                        updated_details.append("Metadata")
                    except NotFound:
                        logger.error("Metadata: Failed to Update Please delete the collection and run again")
                    logger.info("")
        else:
            self.library._reload(self.obj)
            #self.obj.batchEdits()
            batch_display = "Collection Metadata Edits"
            if summary[1] and str(summary[1]) != str(self.obj.summary):
                self.obj.editSummary(summary[1])
                batch_display += f"\nSummary ({summary[0]}) | {summary[1]:<25}"

            if "sort_title" in self.details:
                new_sort_title = str(self.details["sort_title"])
                if "<<title>>" in new_sort_title:
                    title = self.name
                    for op in ["The ", "A ", "An "]:
                        if title.startswith(f"{op} "):
                            title = f"{title[len(op):].strip()}, {op.strip()}"
                            break
                    new_sort_title = new_sort_title.replace("<<title>>", title)
                if new_sort_title != str(self.obj.titleSort):
                    self.obj.editSortTitle(new_sort_title)
                    batch_display += f"\nSort Title | {new_sort_title}"

            if "content_rating" in self.details and str(self.details["content_rating"]) != str(self.obj.contentRating):
                self.obj.editContentRating(self.details["content_rating"])
                batch_display += f"\nContent Rating | {self.details['content_rating']}"

            add_tags = self.details["label"] if "label" in self.details else []
            remove_tags = self.details["label.remove"] if "label.remove" in self.details else None
            sync_tags = self.details["label.sync"] if "label.sync" in self.details else None
            if sync_tags:
                sync_tags.append("Kometa")
            else:
                add_tags.append("Kometa")
            tag_results = self.library.edit_tags('label', self.obj, add_tags=add_tags, remove_tags=remove_tags, sync_tags=sync_tags, do_print=False)
            if tag_results:
                batch_display += f"\n{tag_results}"

            logger.info(batch_display)
            if len(batch_display) > 25:
                try:
                    #self.obj.saveEdits()
                    logger.info("Metadata: Update Completed")
                    updated_details.append("Metadata")
                except NotFound:
                    logger.error("Metadata: Failed to Update Please delete the collection and run again")
                logger.info("")

            advance_update = False
            if "collection_mode" in self.details:
                if (self.blank_collection and self.created) or int(self.obj.collectionMode) not in plex.collection_mode_keys \
                        or plex.collection_mode_keys[int(self.obj.collectionMode)] != self.details["collection_mode"]:
                    if self.blank_collection and self.created:
                        self.library.collection_mode_query(self.obj, "hide")
                        logger.info(f"Collection Mode | hide")
                        self.library.collection_mode_query(self.obj, "default")
                        logger.info(f"Collection Mode | default")
                    self.library.collection_mode_query(self.obj, self.details["collection_mode"])
                    logger.info(f"Collection Mode | {self.details['collection_mode']}")
                    advance_update = True

            if "collection_filtering" in self.details:
                try:
                    self.library.edit_query(self.obj, {"collectionFilterBasedOnUser": 0 if self.details["collection_filtering"] == "admin" else 1}, advanced=True)
                    advance_update = True
                except NotFound:
                    logger.error("Collection Error: collection_filtering requires a more recent version of Plex Media Server")

            if "collection_order" in self.details:
                if int(self.obj.collectionSort) not in plex.collection_order_keys \
                        or plex.collection_order_keys[int(self.obj.collectionSort)] != self.details["collection_order"]:
                    self.library.collection_order_query(self.obj, self.details["collection_order"])
                    logger.info(f"Collection Order | {self.details['collection_order']}")
                    advance_update = True

            if "visible_library" in self.details or "visible_home" in self.details or "visible_shared" in self.details:
                visibility = self.library.collection_visibility(self.obj)
                visible_library = None
                visible_home = None
                visible_shared = None

                if "visible_library" in self.details and self.details["visible_library"] != visibility["library"]:
                    visible_library = self.details["visible_library"]

                if "visible_home" in self.details and self.details["visible_home"] != visibility["home"]:
                    visible_home = self.details["visible_home"]

                if "visible_shared" in self.details and self.details["visible_shared"] != visibility["shared"]:
                    visible_shared = self.details["visible_shared"]

                if visible_library is not None or visible_home is not None or visible_shared is not None:
                    self.library.collection_visibility_update(self.obj, visibility=visibility, library=visible_library, home=visible_home, shared=visible_shared)
                    advance_update = True
                    logger.info("Collection Visibility Updated")

            if advance_update and "Metadata" not in updated_details:
                updated_details.append("Metadata")

        asset_location = None
        if self.asset_directory:
            name_mapping = self.name
            if "name_mapping" in self.details:
                if self.details["name_mapping"]:                    name_mapping = self.details["name_mapping"]
                else:                                               logger.error(f"{self.Type} Error: name_mapping attribute is blank")
            try:
                asset_poster, asset_background, asset_location, _ = self.library.find_item_assets(name_mapping, asset_directory=self.asset_directory)
                if asset_poster:
                    self.posters["asset_directory"] = asset_poster
                if asset_background:
                    self.backgrounds["asset_directory"] = asset_background
            except Failed as e:
                if self.library.asset_folders and (self.library.show_missing_assets or self.library.create_asset_folders):
                    logger.warning(e)
        if self.mapping_name in self.library.collection_images or self.name in self.library.collection_images:
            style_data = self.library.collection_images[self.mapping_name if self.mapping_name in self.library.collection_images else self.name]
            if style_data and "url_poster" in style_data and style_data["url_poster"]:
                self.posters["style_data"] = style_data["url_poster"]
            elif style_data and "tpdb_poster" in style_data and style_data["tpdb_poster"]:
                self.posters["style_data"] = f"https://theposterdb.com/api/assets/{style_data['tpdb_poster']}"
            if style_data and "url_background" in style_data and style_data["url_background"]:
                self.backgrounds["style_data"] = style_data["url_background"]
            elif style_data and "tpdb_background" in style_data and style_data["tpdb_background"]:
                self.backgrounds["style_data"] = f"https://theposterdb.com/api/assets/{style_data['tpdb_background']}"

        self.collection_poster = util.pick_image(self.obj.title, self.posters, self.library.prioritize_assets, self.library.download_url_assets, asset_location)
        self.collection_background = util.pick_image(self.obj.title, self.backgrounds, self.library.prioritize_assets, self.library.download_url_assets, asset_location, is_poster=False)

        clean_temp = False
        if isinstance(self.collection_poster, KometaImage):
            clean_temp = True
            item_vars = {"title": self.name, "titleU": self.name.upper(), "titleL": self.name.lower()}
            self.collection_poster = self.collection_poster.save(item_vars)

        if self.collection_poster or self.collection_background:
            pu, bu = self.library.upload_images(self.obj, poster=self.collection_poster, background=self.collection_background)
            if pu or bu:
                updated_details.append("Image")

        if clean_temp:
            code_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            posters_dir = os.path.join(code_base, "defaults", "posters")
            for filename in os.listdir(posters_dir):
                if "temp" in filename:
                    os.remove(os.path.join(posters_dir, filename))

        if self.url_theme:  # TODO: cache theme path to not constantly upload
            self.library.upload_theme(self.obj, url=self.url_theme)
        elif self.file_theme:
            self.library.upload_theme(self.obj, filepath=self.file_theme)
        return updated_details

    def sort_collection(self):
        logger.info("")
        logger.separator(f"Sorting {self.name} {self.Type}", space=False, border=False)
        logger.info("")
        if not isinstance(self.custom_sort, list):
            items = self.found_items
            if self.custom_sort == "custom.desc":
                items = items[::-1]
        else:
            plex_search = {"sort_by": self.custom_sort}
            if self.builder_level in ["season", "episode"]:
                plex_search["type"] = f"{self.builder_level}s"
                plex_search["any"] = {f"{self.builder_level}_collection": [self.name]} # noqa
            else:
                plex_search["any"] = {"collection": [self.name]}
            try:
                search_data = self.build_filter("plex_search", plex_search)
            except FilterFailed as e:
                if self.ignore_blank_results:
                    raise
                else:
                    raise Failed(str(e))
            items = self.library.fetchItems(search_data[2])
        previous = None
        sort_edit = False
        for i, item in enumerate(items, 0):
            try:
                if len(self.items) <= i or item.ratingKey != self.items[i].ratingKey:
                    text = f"after {util.item_title(previous)}" if previous else "to the beginning"
                    self.library.moveItem(self.obj, item, previous)
                    logger.info(f"Moving {util.item_title(item)} {text}")
                    sort_edit = True
                previous = item
            except Failed:
                logger.error(f"Failed to Move {util.item_title(item)}")
                sort_edit = True
        if not sort_edit:
            logger.info("No Sorting Required")

    def sync_trakt_list(self):
        logger.info("")
        logger.separator(f"Syncing {self.name} {self.Type} to Trakt List {self.sync_to_trakt_list}", space=False, border=False)
        logger.info("")
        if self.obj:
            self.library._reload(self.obj)
        self.load_collection_items()
        current_ids = []
        for item in self.items:
            for pl_library in self.libraries:
                new_id = None
                if isinstance(item, Movie) and item.ratingKey in pl_library.movie_rating_key_map:
                    new_id = (pl_library.movie_rating_key_map[item.ratingKey], "tmdb")
                elif isinstance(item, Show) and item.ratingKey in pl_library.show_rating_key_map:
                    new_id = (pl_library.show_rating_key_map[item.ratingKey], "tvdb")
                elif isinstance(item, Season) and item.parentRatingKey in pl_library.show_rating_key_map:
                    new_id = (f"{pl_library.show_rating_key_map[item.parentRatingKey]}_{item.seasonNumber}", "tvdb_season")
                elif isinstance(item, Episode) and item.grandparentRatingKey in pl_library.show_rating_key_map:
                    new_id = (f"{pl_library.show_rating_key_map[item.grandparentRatingKey]}_{item.seasonNumber}_{item.episodeNumber}", "tvdb_episode")
                if new_id:
                    current_ids.append(new_id)
                    break
        if self.sync_missing_to_trakt_list:
            current_ids.extend([(mm, "tmdb") for mm in self.missing_movies])
            current_ids.extend([(ms, "tvdb") for ms in self.missing_shows])
        self.config.Trakt.sync_list(self.sync_to_trakt_list, current_ids)

    def delete(self):
        title = self.obj.title if self.obj else self.name
        if self.playlist:
            output = f"Deleting {self.Type} {title}"
        elif self.obj:
            output = f"{self.Type} {self.obj.title} deleted"
            if self.smart_label_collection:
                for item in self.library.search(label=self.name, libtype=self.builder_level):
                    self.library.edit_tags("label", item, remove_tags=self.name)
        else:
            output = ""

        if self.playlist:
            for user in self.valid_users:
                try:
                    if user == self.library.account.username:
                        _ = self.library.get_playlist(title)  # Verify if this playlist exists in Admin to avoid log confusion
                        self.library.delete(self.obj)
                    else:
                        self.library.delete_user_playlist(title, user)
                    output += f"\nPlaylist deleted on User {user}"
                except Failed:
                    output += f"\nPlaylist not found on User {user}"
        elif self.obj:
            self.library.delete(self.obj)
        return output

    def sync_playlist(self):
        if self.obj and self.valid_users:
            logger.info("")
            logger.separator(f"Syncing Playlist to Users", space=False, border=False)
            logger.info("")
            for user in self.valid_users:
                try:
                    self.library.delete_user_playlist(self.obj.title, user)
                except Failed:
                    pass
                if user != self.library.account.username:
                    self.obj.copyToUser(user).editSummary(summary=self.obj.summary).reload()
                    logger.info(f"Playlist: {self.name} synced to {user}")

    def exclude_admin_from_playlist(self):
        if self.obj and (self.exclude_users is not None and self.library.account.username in self.exclude_users):
            logger.info("")
            logger.separator(f"Excluding Admin from Playlist", space=False, border=False)
            logger.info("")
            try:
                self.library.delete(self.obj)
                logger.info(f"Playlist: {self.name} deleted on User {self.library.account.username}")
            except Failed:
                logger.info(f"Playlist: {self.name} not found on User {self.library.account.username}")

    def send_notifications(self, playlist=False):
        if self.obj and self.details["changes_webhooks"] and \
                (self.created or len(self.notification_additions) > 0 or len(self.notification_removals) > 0):
            self.library._reload(self.obj)
            try:
                self.library.Webhooks.collection_hooks(
                    self.details["changes_webhooks"],
                    self.obj,
                    poster_url=self.collection_poster.location if self.collection_poster and self.collection_poster.is_url else None,
                    background_url=self.collection_background.location if self.collection_background and self.collection_background.is_url else None,
                    created=self.created,
                    additions=self.notification_additions,
                    removals=self.notification_removals,
                    radarr=self.added_to_radarr,
                    sonarr=self.added_to_sonarr,
                    playlist=playlist
                )
            except Failed as e:
                logger.stacktrace()
                logger.error(f"Webhooks Error: {e}")

    def run_collections_again(self):
        self.obj = self.library.get_collection(self.name, force_search=True)
        name, collection_items = self.library.get_collection_name_and_items(self.obj, self.smart_label_collection)
        self.created = False
        rating_keys = []
        amount_added = 0
        self.notification_additions = []
        self.added_to_radarr = []
        self.added_to_sonarr = []
        for mm in self.run_again_movies:
            if mm in self.library.movie_map:
                rating_keys.extend(self.library.movie_map[mm])
        if self.library.is_show:
            for sm in self.run_again_shows:
                if sm in self.library.show_map:
                    rating_keys.extend(self.library.show_map[sm])
        if len(rating_keys) > 0:
            for rating_key in rating_keys:
                try:
                    current = self.library.fetch_item(int(rating_key))
                except Failed as e:
                    logger.error(e)
                    continue
                if current in collection_items:
                    logger.info(f"{name} {self.Type} | = | {util.item_title(current)}")
                else:
                    self.library.alter_collection(current, name, smart_label_collection=self.smart_label_collection)
                    amount_added += 1
                    logger.info(f"{name} {self.Type} | + | {util.item_title(current)}")
                    if self.library.is_movie and current.ratingKey in self.library.movie_rating_key_map:
                        add_id = self.library.movie_rating_key_map[current.ratingKey]
                    elif self.library.is_show and current.ratingKey in self.library.show_rating_key_map:
                        add_id = self.library.show_rating_key_map[current.ratingKey]
                    else:
                        add_id = None
                    self.notification_additions.append(util.item_set(current, add_id))
            self.send_notifications()
            logger.info(f"{len(rating_keys)} {self.builder_level.capitalize()}{'s' if len(rating_keys) > 1 else ''} Processed")

        if len(self.run_again_movies) > 0:
            logger.info("")
            for missing_id in self.run_again_movies:
                if missing_id not in self.library.movie_map:
                    try:
                        movie = self.config.TMDb.get_movie(missing_id)
                    except Failed as e:
                        logger.error(e)
                        continue
                    if self.details["show_missing"] is True:
                        current_title = f"{movie.title} ({movie.release_date.year})" if movie.release_date else movie.title
                        logger.info(f"{name} {self.Type} | ? | {current_title} (TMDb: {missing_id})")
            logger.info("")
            logger.info(f"{len(self.run_again_movies)} Movie{'s' if len(self.run_again_movies) > 1 else ''} Missing")

        if len(self.run_again_shows) > 0 and self.library.is_show:
            logger.info("")
            for missing_id in self.run_again_shows:
                if missing_id not in self.library.show_map:
                    try:
                        title = self.config.TVDb.get_tvdb_obj(missing_id).title
                    except Failed as e:
                        logger.error(e)
                        continue
                    if self.details["show_missing"] is True:
                        logger.info(f"{name} {self.Type} | ? | {title} (TVDb: {missing_id})")
            logger.info(f"{len(self.run_again_shows)} Show{'s' if len(self.run_again_shows) > 1 else ''} Missing")

        return amount_added
