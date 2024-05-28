import os, time
from abc import ABC, abstractmethod
from modules import util
from modules.meta import MetadataFile, OverlayFile
from modules.operations import Operations
from modules.poster import ImageData
from modules.util import Failed, NotScheduled
from PIL import Image

logger = util.logger

class Library(ABC):
    def __init__(self, config, params):
        self.Radarr = None
        self.Sonarr = None
        self.Tautulli = None
        self.Webhooks = None
        self.Operations = Operations(config, self)
        self.Overlays = None
        self.collections = []
        self.collection_names = []
        self.metadatas = []
        self.queues = {}
        self.image_styles = {}
        self.collection_images = {}
        self.queue_current = 0
        self.collection_files = []
        self.metadata_files = []
        self.overlay_files = []
        self.images_files = []
        self.movie_map = {}
        self.show_map = {}
        self.imdb_map = {}
        self.anidb_map = {}
        self.reverse_anidb = {}
        self.mal_map = {}
        self.reverse_mal = {}
        self.movie_rating_key_map = {}
        self.show_rating_key_map = {}
        self.imdb_rating_key_map = {}
        self.cached_items = {}
        self.run_again = []
        self.type = ""
        self.config = config
        self.name = params["name"]
        self.original_mapping_name = params["mapping_name"]
        self.scanned_collection_files = params["collection_files"]
        self.scanned_metadata_files = params["metadata_files"]
        self.scanned_overlay_files = params["overlay_files"]
        self.scanned_image_files = params["image_files"]
        self.skip_library = params["skip_library"]
        self.asset_depth = params["asset_depth"]
        self.asset_directory = params["asset_directory"] if params["asset_directory"] else []
        self.default_dir = params["default_dir"]
        self.mapping_name, output = util.validate_filename(self.original_mapping_name)
        self.image_table_name = self.config.Cache.get_image_table_name(self.original_mapping_name) if self.config.Cache else None
        self.overlay_folder = os.path.join(self.config.default_dir, "overlays")
        self.overlay_backup = os.path.join(self.overlay_folder, f"{self.mapping_name} Original Posters")
        self.report_path = params["report_path"] if params["report_path"] else os.path.join(self.default_dir, f"{self.mapping_name}_report.yml")
        self.report_data = {}
        self.run_order = params["run_order"]
        self.asset_folders = params["asset_folders"]
        self.create_asset_folders = params["create_asset_folders"]
        self.dimensional_asset_rename = params["dimensional_asset_rename"]
        self.prioritize_assets = params["prioritize_assets"]
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
        self.show_unconfigured = params["show_unconfigured"]
        self.show_filtered = params["show_filtered"]
        self.show_options = params["show_options"]
        self.show_missing = params["show_missing"]
        self.show_missing_assets = params["show_missing_assets"]
        self.save_report = params["save_report"]
        self.only_filter_missing = params["only_filter_missing"]
        self.ignore_ids = params["ignore_ids"]
        self.ignore_imdb_ids = params["ignore_imdb_ids"]
        self.overlay_artwork_quality = params["overlay_artwork_quality"]
        self.overlay_artwork_filetype = params["overlay_artwork_filetype"]
        self.assets_for_all = params["assets_for_all"]
        self.assets_for_all_collections = False
        self.delete_collections = params["delete_collections"]
        self.mass_studio_update = params["mass_studio_update"]
        self.mass_genre_update = params["mass_genre_update"]
        self.mass_audience_rating_update = params["mass_audience_rating_update"]
        self.mass_critic_rating_update = params["mass_critic_rating_update"]
        self.mass_user_rating_update = params["mass_user_rating_update"]
        self.mass_episode_audience_rating_update = params["mass_episode_audience_rating_update"]
        self.mass_episode_critic_rating_update = params["mass_episode_critic_rating_update"]
        self.mass_episode_user_rating_update = params["mass_episode_user_rating_update"]
        self.mass_content_rating_update = params["mass_content_rating_update"]
        self.mass_original_title_update = params["mass_original_title_update"]
        self.mass_originally_available_update = params["mass_originally_available_update"]
        self.mass_added_at_update = params["mass_added_at_update"]
        self.mass_imdb_parental_labels = params["mass_imdb_parental_labels"]
        self.mass_poster_update = params["mass_poster_update"]
        self.mass_background_update = params["mass_background_update"]
        self.radarr_add_all_existing = params["radarr_add_all_existing"]
        self.radarr_remove_by_tag = params["radarr_remove_by_tag"]
        self.sonarr_add_all_existing = params["sonarr_add_all_existing"]
        self.sonarr_remove_by_tag = params["sonarr_remove_by_tag"]
        self.update_blank_track_titles = params["update_blank_track_titles"]
        self.remove_title_parentheses = params["remove_title_parentheses"]
        self.remove_overlays = params["remove_overlays"]
        self.reapply_overlays = params["reapply_overlays"]
        self.reset_overlays = params["reset_overlays"]
        self.mass_collection_mode = params["mass_collection_mode"]
        self.metadata_backup = params["metadata_backup"]
        self.genre_mapper = params["genre_mapper"]
        self.content_rating_mapper = params["content_rating_mapper"]
        self.changes_webhooks = params["changes_webhooks"]
        self.split_duplicates = params["split_duplicates"] # TODO: Here or just in Plex?
        self.clean_bundles = params["plex"]["clean_bundles"] # TODO: Here or just in Plex?
        self.empty_trash = params["plex"]["empty_trash"] # TODO: Here or just in Plex?
        self.optimize = params["plex"]["optimize"] # TODO: Here or just in Plex?
        self.stats = {"created": 0, "modified": 0, "deleted": 0, "added": 0, "unchanged": 0, "removed": 0, "radarr": 0, "sonarr": 0, "names": []}
        self.status = {}

        self.items_library_operation = True if self.assets_for_all or self.mass_genre_update or self.remove_title_parentheses \
                                               or self.mass_audience_rating_update or self.mass_critic_rating_update or self.mass_user_rating_update \
                                               or self.mass_episode_audience_rating_update or self.mass_episode_critic_rating_update or self.mass_episode_user_rating_update \
                                               or self.mass_content_rating_update or self.mass_originally_available_update or self.mass_added_at_update or self.mass_original_title_update\
                                               or self.mass_imdb_parental_labels or self.genre_mapper or self.content_rating_mapper or self.mass_studio_update\
                                               or self.radarr_add_all_existing or self.sonarr_add_all_existing or self.mass_poster_update or self.mass_background_update else False
        self.library_operation = True if self.items_library_operation or self.delete_collections or self.mass_collection_mode \
                                         or self.radarr_remove_by_tag or self.sonarr_remove_by_tag or self.show_unmanaged or self.show_unconfigured \
                                         or self.metadata_backup or self.update_blank_track_titles else False
        self.label_operations = True if self.assets_for_all or self.mass_imdb_parental_labels else False

        if self.asset_directory:
            logger.info("")
            for ad in self.asset_directory:
                logger.info(f"Using Asset Directory: {ad}")

        if output:
            logger.info("")
            logger.info(output)

    def scan_files(self, operations_only, overlays_only, collection_only, metadata_only):
        if not operations_only and not overlays_only and not metadata_only:
            for file_type, metadata_file, temp_vars, asset_directory in self.scanned_collection_files:
                try:
                    meta_obj = MetadataFile(self.config, self, file_type, metadata_file, temp_vars, asset_directory, "collection")
                    if meta_obj.collections:
                        self.collections.extend([c for c in meta_obj.collections])
                    self.collection_files.append(meta_obj)
                except Failed as e:
                    logger.error(e)
                    logger.info("Collection File Failed To Load")
                except NotScheduled as e:
                    logger.info("")
                    logger.separator(f"Skipping {e} Collection File")
        if not operations_only and not overlays_only and not collection_only:
            for file_type, metadata_file, temp_vars, asset_directory in self.scanned_metadata_files:
                try:
                    meta_obj = MetadataFile(self.config, self, file_type, metadata_file, temp_vars, asset_directory, "metadata")
                    if meta_obj.metadata:
                        self.metadatas.extend([m for m in meta_obj.metadata])
                    self.metadata_files.append(meta_obj)
                except Failed as e:
                    logger.error(e)
                    logger.info("Metadata File Failed To Load")
                except NotScheduled as e:
                    logger.info("")
                    logger.separator(f"Skipping {e} Metadata File")
        if not operations_only and not collection_only and not metadata_only:
            for file_type, overlay_file, temp_vars, asset_directory in self.scanned_overlay_files:
                try:
                    overlay_obj = OverlayFile(self.config, self, file_type, overlay_file, temp_vars, asset_directory, self.queue_current)
                    self.overlay_files.append(overlay_obj)
                    for qk, qv in overlay_obj.queues.items():
                        self.queues[self.queue_current] = qv
                        self.queue_current += 1
                except Failed as e:
                    logger.error(e)
                    logger.info("Overlay File Failed To Load")
                except NotScheduled as e:
                    logger.info("")
                    logger.separator(f"Skipping {e} Overlay File")
        if not operations_only and not overlays_only and not collection_only:
            for file_type, images_file, temp_vars, asset_directory in self.scanned_image_files:
                try:
                    images_obj = MetadataFile(self.config, self, file_type, images_file, temp_vars, asset_directory, "image")
                    self.images_files.append(images_obj)
                except Failed as e:
                    logger.error(e)
                    logger.info("Image File Failed To Load")
                except NotScheduled as e:
                    logger.info("")
                    logger.separator(f"Skipping {e} Image File")

    def upload_images(self, item, poster=None, background=None, overlay=False):
        poster_uploaded = False
        if poster is not None:
            try:
                image_compare = None
                if self.config.Cache:
                    _, image_compare, _ = self.config.Cache.query_image_map(item.ratingKey, self.image_table_name)
                if not image_compare or str(poster.compare) != str(image_compare):
                    if overlay:
                        self.reload(item, force=True)
                        if overlay and "Overlay" in [la.tag for la in self.item_labels(item)]:
                            item.removeLabel("Overlay")
                    self._upload_image(item, poster)
                    poster_uploaded = True
                    logger.info(f"Metadata: {poster.attribute} updated {poster.message}")
                elif self.show_asset_not_needed:
                    logger.info(f"Metadata: {poster.prefix}poster update not needed")
            except Failed:
                logger.stacktrace()
                logger.error(f"Metadata: {poster.attribute} failed to update {poster.message}")

        background_uploaded = False
        if background is not None:
            try:
                image_compare = None
                if self.config.Cache:
                    _, image_compare, _ = self.config.Cache.query_image_map(item.ratingKey, f"{self.image_table_name}_backgrounds")
                if not image_compare or str(background.compare) != str(image_compare):
                    self._upload_image(item, background)
                    background_uploaded = True
                    logger.info(f"Metadata: {background.attribute} updated {background.message}")
                elif self.show_asset_not_needed:
                    logger.info(f"Metadata: {background.prefix}background update not needed")
            except Failed:
                logger.stacktrace()
                logger.error(f"Metadata: {background.attribute} failed to update {background.message}")
        if self.config.Cache:
            if poster_uploaded:
                self.config.Cache.update_image_map(item.ratingKey, self.image_table_name, "", poster.compare if poster else "")
            if background_uploaded:
                self.config.Cache.update_image_map(item.ratingKey, f"{self.image_table_name}_backgrounds", "", background.compare)

        return poster_uploaded, background_uploaded

    def get_id_from_maps(self, key):
        key = int(key)
        if key in self.movie_rating_key_map:
            return self.movie_rating_key_map[key]
        elif key in self.show_rating_key_map:
            return self.show_rating_key_map[key]

    @abstractmethod
    def notify(self, text, collection=None, critical=True):
        pass

    @abstractmethod
    def notify_delete(self, message):
        pass

    @abstractmethod
    def _upload_image(self, item, image):
        pass

    @abstractmethod
    def upload_poster(self, item, image, url=False):
        pass

    def poster_update(self, item, image, tmdb=None, title=None):
        return self.image_update(item, image, tmdb=tmdb, title=title)

    def background_update(self, item, image, tmdb=None, title=None):
        return self.image_update(item, image, tmdb=tmdb, title=title, poster=False)

    @abstractmethod
    def image_update(self, item, image, tmdb=None, title=None, poster=True):
        pass

    def pick_image(self, title, images, prioritize_assets, download_url_assets, item_dir, is_poster=True, image_name=None):
        image_type = "poster" if is_poster else "background"
        if image_name is None:
            image_name = image_type
        if images:
            logger.debug(f"{len(images)} {image_type}{'s' if len(images) > 1 else ''} found:")
            for i in images:
                logger.debug(f"Method: {i} {image_type.capitalize()}: {images[i]}")
            if prioritize_assets and "asset_directory" in images:
                return images["asset_directory"]
            for attr in ["style_data", f"url_{image_type}", f"file_{image_type}", f"tmdb_{image_type}", "tmdb_profile",
                         "tmdb_list_poster", "tvdb_list_poster", f"tvdb_{image_type}", "asset_directory",
                         f"pmm_{image_type}",
                         "tmdb_person", "tmdb_collection_details", "tmdb_actor_details", "tmdb_crew_details",
                         "tmdb_director_details",
                         "tmdb_producer_details", "tmdb_writer_details", "tmdb_movie_details", "tmdb_list_details",
                         "tvdb_list_details", "tvdb_movie_details", "tvdb_show_details", "tmdb_show_details"]:
                if attr in images:
                    if attr in ["style_data", f"url_{image_type}"] and download_url_assets and item_dir:
                        if "asset_directory" in images:
                            return images["asset_directory"]
                        else:
                            try:
                                return self.config.Requests.download_image(title, images[attr], item_dir, is_poster=is_poster, filename=image_name)
                            except Failed as e:
                                logger.error(e)
                    if attr in ["asset_directory", f"pmm_{image_type}"]:
                        return images[attr]
                    return ImageData(attr, images[attr], is_poster=is_poster, is_url=attr != f"file_{image_type}")

    @abstractmethod
    def reload(self, item, force=False):
        pass

    @abstractmethod
    def edit_tags(self, attr, obj, add_tags=None, remove_tags=None, sync_tags=None, do_print=True, locked=True, is_locked=None):
        pass

    @abstractmethod
    def item_labels(self, item):
        pass

    @abstractmethod
    def find_poster_url(self, item):
        pass

    def check_image_for_overlay(self, image_url, image_path, remove=False):
        image_path = self.config.Requests.download_image("", image_url, image_path).location
        while util.is_locked(image_path):
            time.sleep(1)
        with Image.open(image_path) as image:
            exif_tags = image.getexif()
        if 0x04bc in exif_tags and exif_tags[0x04bc] == "overlay":
            os.remove(image_path)
            raise Failed("This item's poster already has an Overlay. There is no Kometa setting to change; manual attention required.")
        if remove:
            os.remove(image_path)
        else:
            return image_path

    @abstractmethod
    def item_posters(self, item, providers=None):
        pass

    @abstractmethod
    def get_all(self, builder_level=None, load=False):
        pass

    def add_additions(self, collection, items, is_movie):
        self._add_to_file("Added", collection, items, is_movie)

    def add_missing(self, collection, items, is_movie):
        self._add_to_file("Missing", collection, items, is_movie)

    def add_removed(self, collection, items, is_movie):
        self._add_to_file("Removed", collection, items, is_movie)

    def add_filtered(self, collection, items, is_movie):
        self._add_to_file("Filtered", collection, items, is_movie)

    def _add_to_file(self, file_type, collection, items, is_movie):
        if collection not in self.report_data:
            self.report_data[collection] = {}
        parts = isinstance(items[0], str)
        if parts:
            other = f"Parts {file_type}"
            section = other
        elif is_movie:
            other = f"Movies {file_type}"
            section = f"{other} (TMDb IDs)"
        else:
            other = f"Shows {file_type}"
            section = f"{other} (TVDb IDs)"
        if section not in self.report_data[collection]:
            self.report_data[collection][section] = [] if parts else {}
        if parts:
            self.report_data[collection][section].extend(items)
        else:
            for title, item_id in items:
                if item_id:
                    self.report_data[collection][section][int(item_id)] = title
                else:
                    if other not in self.report_data[collection]:
                        self.report_data[collection][other] = []
                    self.report_data[collection][other].append(title)

        yaml = self.config.Requests.file_yaml(self.report_path, start_empty=True)
        yaml.data = self.report_data
        yaml.save()

    def cache_items(self):
        logger.info("")
        logger.separator(f"Caching {self.name} Library Items", space=False, border=False)
        logger.info("")
        items = self.get_all()
        for item in items:
            self.cached_items[item.ratingKey] = (item, False)
        return items

    def map_guids(self, items):
        for i, item in enumerate(items, 1):
            if isinstance(item, tuple):
                logger.ghost(f"Processing: {i}/{len(items)}")
                key, guid = item
            else:
                logger.ghost(f"Processing: {i}/{len(items)} {item.title}")
                key = item.ratingKey
                guid = item.guid
            if key not in self.movie_rating_key_map and key not in self.show_rating_key_map:
                if isinstance(item, tuple):
                    item_type, check_id = self.config.Convert.scan_guid(guid)
                    id_type, main_id, imdb_id, _ = self.config.Convert.ids_from_cache(key, guid, item_type, check_id, self)
                else:
                    id_type, main_id, imdb_id = self.config.Convert.get_id(item, self)
                if main_id:
                    if id_type == "movie":
                        if len(main_id) > 1:
                            for _id in main_id:
                                try:
                                    self.config.TMDb.get_movie(_id)
                                    self.movie_rating_key_map[key] = _id
                                    break
                                except Failed:
                                    pass
                        else:
                            self.movie_rating_key_map[key] = main_id[0]
                        util.add_dict_list(main_id, key, self.movie_map)
                    elif id_type == "show":
                        if len(main_id) > 1:
                            for _id in main_id:
                                try:
                                    self.config.Convert.tvdb_to_tmdb(_id, fail=True)
                                    self.show_rating_key_map[key] = _id
                                    break
                                except Failed:
                                    pass
                        else:
                            self.show_rating_key_map[key] = main_id[0]
                        util.add_dict_list(main_id, key, self.show_map)
                if imdb_id:
                    self.imdb_rating_key_map[key] = imdb_id[0]
                    util.add_dict_list(imdb_id, key, self.imdb_map)
        self.reverse_anidb = {}
        for k, v in self.anidb_map.items():
            self.reverse_anidb[v] = k
        self.reverse_mal = {}
        for k, v in self.mal_map.items():
            self.reverse_mal[v] = k
        logger.info("")
        logger.info(f"Processed {len(items)} {self.type}s")
