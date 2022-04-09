import os, shutil, time
from abc import ABC, abstractmethod
from modules import util
from modules.meta import MetadataFile
from modules.util import Failed
from PIL import Image
from plexapi.exceptions import BadRequest
from ruamel import yaml

logger = util.logger

class Library(ABC):
    def __init__(self, config, params):
        self.Radarr = None
        self.Sonarr = None
        self.Tautulli = None
        self.Webhooks = None
        self.Notifiarr = None
        self.collections = []
        self.metadatas = []
        self.metadata_files = []
        self.missing = {}
        self.movie_map = {}
        self.show_map = {}
        self.imdb_map = {}
        self.anidb_map = {}
        self.mal_map = {}
        self.movie_rating_key_map = {}
        self.show_rating_key_map = {}
        self.run_again = []
        self.overlays = []
        self.type = ""
        self.config = config
        self.name = params["name"]
        self.original_mapping_name = params["mapping_name"]
        self.metadata_path = params["metadata_path"]
        self.skip_library = params["skip_library"]
        self.asset_depth = params["asset_depth"]
        self.asset_directory = params["asset_directory"] if params["asset_directory"] else []
        self.default_dir = params["default_dir"]
        self.mapping_name, output = util.validate_filename(self.original_mapping_name)
        self.image_table_name = self.config.Cache.get_image_table_name(self.original_mapping_name) if self.config.Cache else None
        self.missing_path = params["missing_path"] if params["missing_path"] else os.path.join(self.default_dir, f"{self.mapping_name}_missing.yml")
        self.asset_folders = params["asset_folders"]
        self.create_asset_folders = params["create_asset_folders"]
        self.dimensional_asset_rename = params["dimensional_asset_rename"]
        self.download_url_assets = params["download_url_assets"]
        self.show_missing_season_assets = params["show_missing_season_assets"]
        self.show_missing_episode_assets = params["show_missing_episode_assets"]
        self.show_asset_not_needed = params["show_asset_not_needed"]
        self.sync_mode = params["sync_mode"]
        self.default_collection_order = params["default_collection_order"]
        self.minimum_items = params["minimum_items"]
        self.item_refresh_delay = params["item_refresh_delay"]
        self.delete_below_minimum = params["delete_below_minimum"]
        self.delete_not_scheduled = params["delete_not_scheduled"]
        self.missing_only_released = params["missing_only_released"]
        self.show_unmanaged = params["show_unmanaged"]
        self.show_filtered = params["show_filtered"]
        self.show_options = params["show_options"]
        self.show_missing = params["show_missing"]
        self.show_missing_assets = params["show_missing_assets"]
        self.save_missing = params["save_missing"]
        self.only_filter_missing = params["only_filter_missing"]
        self.ignore_ids = params["ignore_ids"]
        self.ignore_imdb_ids = params["ignore_imdb_ids"]
        self.assets_for_all = params["assets_for_all"]
        self.delete_unmanaged_collections = params["delete_unmanaged_collections"]
        self.delete_collections_with_less = params["delete_collections_with_less"]
        self.mass_genre_update = params["mass_genre_update"]
        self.mass_audience_rating_update = params["mass_audience_rating_update"]
        self.mass_critic_rating_update = params["mass_critic_rating_update"]
        self.mass_content_rating_update = params["mass_content_rating_update"]
        self.mass_originally_available_update = params["mass_originally_available_update"]
        self.mass_imdb_parental_labels = params["mass_imdb_parental_labels"]
        self.mass_trakt_rating_update = params["mass_trakt_rating_update"]
        self.radarr_add_all_existing = params["radarr_add_all_existing"]
        self.radarr_remove_by_tag = params["radarr_remove_by_tag"]
        self.sonarr_add_all_existing = params["sonarr_add_all_existing"]
        self.sonarr_remove_by_tag = params["sonarr_remove_by_tag"]
        self.update_blank_track_titles = params["update_blank_track_titles"]
        self.remove_title_parentheses = params["remove_title_parentheses"]
        self.mass_collection_mode = params["mass_collection_mode"]
        self.metadata_backup = params["metadata_backup"]
        self.tmdb_collections = params["tmdb_collections"]
        self.genre_collections = params["genre_collections"]
        self.genre_mapper = params["genre_mapper"]
        self.content_rating_mapper = params["content_rating_mapper"]
        self.error_webhooks = params["error_webhooks"]
        self.changes_webhooks = params["changes_webhooks"]
        self.split_duplicates = params["split_duplicates"] # TODO: Here or just in Plex?
        self.clean_bundles = params["plex"]["clean_bundles"] # TODO: Here or just in Plex?
        self.empty_trash = params["plex"]["empty_trash"] # TODO: Here or just in Plex?
        self.optimize = params["plex"]["optimize"] # TODO: Here or just in Plex?
        self.stats = {"created": 0, "modified": 0, "deleted": 0, "added": 0, "unchanged": 0, "removed": 0, "radarr": 0, "sonarr": 0, "names": []}
        self.status = {}

        self.items_library_operation = True if self.assets_for_all or self.mass_genre_update or self.mass_audience_rating_update or self.remove_title_parentheses \
                                       or self.mass_critic_rating_update or self.mass_content_rating_update or self.mass_originally_available_update or self.mass_imdb_parental_labels or self.mass_trakt_rating_update \
                                       or self.genre_mapper or self.content_rating_mapper or self.tmdb_collections or self.radarr_add_all_existing or self.sonarr_add_all_existing else False
        self.library_operation = True if self.items_library_operation or self.delete_unmanaged_collections or self.delete_collections_with_less \
                                 or self.radarr_remove_by_tag or self.sonarr_remove_by_tag or self.mass_collection_mode or self.genre_collections \
                                 or self.show_unmanaged or self.metadata_backup or self.update_blank_track_titles else False
        self.meta_operations = [self.mass_genre_update, self.mass_audience_rating_update, self.mass_critic_rating_update, self.mass_content_rating_update, self.mass_originally_available_update]

        if self.asset_directory:
            logger.info("")
            for ad in self.asset_directory:
                logger.info(f"Using Asset Directory: {ad}")

        if output:
            logger.info("")
            logger.info(output)

    def scan_metadata_files(self):
        metadata = []
        for file_type, metadata_file, temp_vars in self.metadata_path:
            if file_type == "Folder":
                if os.path.isdir(metadata_file):
                    yml_files = util.glob_filter(os.path.join(metadata_file, "*.yml"))
                    if yml_files:
                        metadata.extend([("File", yml, temp_vars) for yml in yml_files])
                    else:
                        logger.error(f"Config Error: No YAML (.yml) files found in {metadata_file}")
                else:
                    logger.error(f"Config Error: Folder not found: {metadata_file}")
            else:
                metadata.append((file_type, metadata_file, temp_vars))
        for file_type, metadata_file, temp_vars in metadata:
            try:
                meta_obj = MetadataFile(self.config, self, file_type, metadata_file, temp_vars)
                if meta_obj.collections:
                    self.collections.extend([c for c in meta_obj.collections])
                if meta_obj.metadata:
                    self.metadatas.extend([c for c in meta_obj.metadata])
                self.metadata_files.append(meta_obj)
            except Failed as e:
                logger.error(e)

        if len(self.metadata_files) == 0 and not self.library_operation and not self.config.playlist_files:
            logger.info("")
            raise Failed("Config Error: No valid metadata files, playlist files, or library operations found")

    def upload_images(self, item, poster=None, background=None, overlay=None):
        image = None
        image_compare = None
        poster_uploaded = False
        if self.config.Cache:
            image, image_compare = self.config.Cache.query_image_map(item.ratingKey, self.image_table_name)

        if poster is not None:
            try:
                if image_compare and str(poster.compare) != str(image_compare):
                    image = None
                if image is None or image != item.thumb:
                    self._upload_image(item, poster)
                    poster_uploaded = True
                    logger.info(f"Detail: {poster.attribute} updated {poster.message}")
                elif self.show_asset_not_needed:
                    logger.info(f"Detail: {poster.prefix}poster update not needed")
            except Failed:
                logger.stacktrace()
                logger.error(f"Detail: {poster.attribute} failed to update {poster.message}")

        if overlay is not None:
            overlay_name, overlay_folder, overlay_image = overlay
            self.reload(item)
            item_labels = {item_tag.tag.lower(): item_tag.tag for item_tag in item.labels}
            for item_label in item_labels:
                if item_label.endswith(" overlay") and item_label != f"{overlay_name.lower()} overlay":
                    raise Failed(f"Overlay Error: Poster already has an existing Overlay: {item_labels[item_label]}")
            if poster_uploaded or image is None or image != item.thumb or f"{overlay_name.lower()} overlay" not in item_labels:
                if not item.posterUrl:
                    raise Failed(f"Overlay Error: No existing poster to Overlay for {item.title}")
                response = self.config.get(item.posterUrl)
                if response.status_code >= 400:
                    raise Failed(f"Overlay Error: Overlay Failed for {item.title}")
                og_image = response.content
                ext = "jpg" if response.headers["Content-Type"] == "image/jpegss" else "png"
                temp_image = os.path.join(overlay_folder, f"temp.{ext}")
                with open(temp_image, "wb") as handler:
                    handler.write(og_image)
                shutil.copyfile(temp_image, os.path.join(overlay_folder, f"{item.ratingKey}.{ext}"))
                while util.is_locked(temp_image):
                    time.sleep(1)
                try:
                    new_poster = Image.open(temp_image).convert("RGBA")
                    new_poster = new_poster.resize(overlay_image.size, Image.ANTIALIAS)
                    new_poster.paste(overlay_image, (0, 0), overlay_image)
                    new_poster.save(temp_image)
                    self.upload_file_poster(item, temp_image)
                    self.edit_tags("label", item, add_tags=[f"{overlay_name} Overlay"])
                    poster_uploaded = True
                    logger.info(f"Detail: Overlay: {overlay_name} applied to {item.title}")
                except (OSError, BadRequest) as e:
                    logger.stacktrace()
                    raise Failed(f"Overlay Error: {e}")

        background_uploaded = False
        if background is not None:
            try:
                image = None
                if self.config.Cache:
                    image, image_compare = self.config.Cache.query_image_map(item.ratingKey, f"{self.image_table_name}_backgrounds")
                    if str(background.compare) != str(image_compare):
                        image = None
                if image is None or image != item.art:
                    self._upload_image(item, background)
                    background_uploaded = True
                    logger.info(f"Detail: {background.attribute} updated {background.message}")
                elif self.show_asset_not_needed:
                    logger.info(f"Detail: {background.prefix}background update not needed")
            except Failed:
                logger.stacktrace()
                logger.error(f"Detail: {background.attribute} failed to update {background.message}")

        if self.config.Cache:
            if poster_uploaded:
                self.config.Cache.update_image_map(item.ratingKey, self.image_table_name, item.thumb, poster.compare if poster else "")
            if background_uploaded:
                self.config.Cache.update_image_map(item.ratingKey, f"{self.image_table_name}_backgrounds", item.art, background.compare)

    @abstractmethod
    def notify(self, text, collection=None, critical=True):
        pass

    @abstractmethod
    def _upload_image(self, item, image):
        pass

    @abstractmethod
    def upload_file_poster(self, item, image):
        pass

    @abstractmethod
    def reload(self, item):
        pass

    @abstractmethod
    def edit_tags(self, attr, obj, add_tags=None, remove_tags=None, sync_tags=None, do_print=True):
        pass

    @abstractmethod
    def get_all(self, collection_level=None, load=False):
        pass

    def add_missing(self, collection, items, is_movie):
        if collection not in self.missing:
            self.missing[collection] = {}
        section = "Movies Missing (TMDb IDs)" if is_movie else "Shows Missing (TVDb IDs)"
        if section not in self.missing[collection]:
            self.missing[collection][section] = {}
        for title, item_id in items:
            self.missing[collection][section][int(item_id)] = title
        with open(self.missing_path, "w"): pass
        try:
            yaml.round_trip_dump(self.missing, open(self.missing_path, "w", encoding="utf-8"))
        except yaml.scanner.ScannerError as e:
            logger.error(f"YAML Error: {util.tab_new_lines(e)}")

    def map_guids(self):
        items = self.get_all()
        logger.info(f"Mapping {self.type} Library: {self.name}")
        logger.info("")
        for i, item in enumerate(items, 1):
            logger.ghost(f"Processing: {i}/{len(items)} {item.title}")
            if item.ratingKey not in self.movie_rating_key_map and item.ratingKey not in self.show_rating_key_map:
                id_type, main_id, imdb_id = self.config.Convert.get_id(item, self)
                if main_id:
                    if id_type == "movie":
                        self.movie_rating_key_map[item.ratingKey] = main_id[0]
                        util.add_dict_list(main_id, item.ratingKey, self.movie_map)
                    elif id_type == "show":
                        self.show_rating_key_map[item.ratingKey] = main_id[0]
                        util.add_dict_list(main_id, item.ratingKey, self.show_map)
                if imdb_id:
                    util.add_dict_list(imdb_id, item.ratingKey, self.imdb_map)
        logger.info("")
        logger.info(f"Processed {len(items)} {self.type}s")
        return items
