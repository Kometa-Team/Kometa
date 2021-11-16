import logging, os, requests, shutil, time
from abc import ABC, abstractmethod
from modules import util
from modules.meta import Metadata
from modules.util import Failed, ImageData
from PIL import Image
from ruamel import yaml

logger = logging.getLogger("Plex Meta Manager")

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
        self.run_sort = []
        self.overlays = []
        self.type = ""
        self.config = config
        self.name = params["name"]
        self.original_mapping_name = params["mapping_name"]
        self.metadata_path = params["metadata_path"]
        self.asset_directory = params["asset_directory"]
        self.default_dir = params["default_dir"]
        self.mapping_name, output = util.validate_filename(self.original_mapping_name)
        self.image_table_name = self.config.Cache.get_image_table_name(self.original_mapping_name) if self.config.Cache else None
        self.missing_path = os.path.join(self.default_dir, f"{self.original_mapping_name}_missing.yml")
        self.asset_folders = params["asset_folders"]
        self.sync_mode = params["sync_mode"]
        self.show_unmanaged = params["show_unmanaged"]
        self.show_filtered = params["show_filtered"]
        self.show_missing = params["show_missing"]
        self.show_missing_assets = params["show_missing_assets"]
        self.save_missing = params["save_missing"]
        self.missing_only_released = params["missing_only_released"]
        self.create_asset_folders = params["create_asset_folders"]
        self.assets_for_all = params["assets_for_all"]
        self.delete_unmanaged_collections = params["delete_unmanaged_collections"]
        self.delete_collections_with_less = params["delete_collections_with_less"]
        self.mass_genre_update = params["mass_genre_update"]
        self.mass_audience_rating_update = params["mass_audience_rating_update"]
        self.mass_critic_rating_update = params["mass_critic_rating_update"]
        self.mass_trakt_rating_update = params["mass_trakt_rating_update"]
        self.radarr_add_all = params["radarr_add_all"]
        self.sonarr_add_all = params["sonarr_add_all"]
        self.collection_minimum = params["collection_minimum"]
        self.delete_below_minimum = params["delete_below_minimum"]
        self.error_webhooks = params["error_webhooks"]
        self.collection_creation_webhooks = params["collection_creation_webhooks"]
        self.collection_addition_webhooks = params["collection_addition_webhooks"]
        self.collection_removal_webhooks = params["collection_removal_webhooks"]
        self.split_duplicates = params["split_duplicates"] # TODO: Here or just in Plex?
        self.clean_bundles = params["plex"]["clean_bundles"] # TODO: Here or just in Plex?
        self.empty_trash = params["plex"]["empty_trash"] # TODO: Here or just in Plex?
        self.optimize = params["plex"]["optimize"] # TODO: Here or just in Plex?

        metadata = []
        for file_type, metadata_file in self.metadata_path:
            if file_type == "Folder":
                if os.path.isdir(metadata_file):
                    yml_files = util.glob_filter(os.path.join(metadata_file, "*.yml"))
                    if yml_files:
                        metadata.extend([("File", yml) for yml in yml_files])
                    else:
                        logger.error(f"Config Error: No YAML (.yml) files found in {metadata_file}")
                else:
                    logger.error(f"Config Error: Folder not found: {metadata_file}")
            else:
                metadata.append((file_type, metadata_file))
        for file_type, metadata_file in metadata:
            try:
                meta_obj = Metadata(config, self, file_type, metadata_file)
                if meta_obj.collections:
                    self.collections.extend([c for c in meta_obj.collections])
                if meta_obj.metadata:
                    self.metadatas.extend([c for c in meta_obj.metadata])
                self.metadata_files.append(meta_obj)
            except Failed as e:
                util.print_multiline(e, error=True)

        if len(self.metadata_files) == 0:
            logger.info("")
            raise Failed("Metadata File Error: No valid metadata files found")

        if self.asset_directory:
            logger.info("")
            for ad in self.asset_directory:
                logger.info(f"Using Asset Directory: {ad}")

        if output:
            logger.info(output)

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
                else:
                    logger.info(f"Detail: {poster.prefix}poster update not needed")
            except Failed:
                util.print_stacktrace()
                logger.error(f"Detail: {poster.attribute} failed to update {poster.message}")

        if overlay is not None:
            overlay_name, overlay_folder, overlay_image, temp_image = overlay
            self.reload(item)
            item_labels = {item_tag.tag.lower(): item_tag.tag for item_tag in item.labels}
            for item_label in item_labels:
                if item_label.endswith(" overlay") and item_label != f"{overlay_name.lower()} overlay":
                    raise Failed(f"Overlay Error: Poster already has an existing Overlay: {item_labels[item_label]}")
            if poster_uploaded or image is None or image != item.thumb or f"{overlay_name.lower()} overlay" not in item_labels:
                if not item.posterUrl:
                    raise Failed(f"Overlay Error: No existing poster to Overlay for {item.title}")
                response = requests.get(item.posterUrl)
                if response.status_code >= 400:
                    raise Failed(f"Overlay Error: Overlay Failed for {item.title}")
                og_image = response.content
                with open(temp_image, "wb") as handler:
                    handler.write(og_image)
                shutil.copyfile(temp_image, os.path.join(overlay_folder, f"{item.ratingKey}.png"))
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
                except OSError as e:
                    util.print_stacktrace()
                    logger.error(f"Overlay Error: {e}")

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
                else:
                    logger.info(f"Detail: {background.prefix}background update not needed")
            except Failed:
                util.print_stacktrace()
                logger.error(f"Detail: {background.attribute} failed to update {background.message}")

        if self.config.Cache:
            if poster_uploaded:
                self.config.Cache.update_image_map(item.ratingKey, self.image_table_name, item.thumb, poster.compare if poster else "")
            if background_uploaded:
                self.config.Cache.update_image_map(item.ratingKey, f"{self.image_table_name}_backgrounds", item.art, background.compare)

    def notify(self, text, collection=None, critical=True):
        for error in util.get_list(text, split=False):
            self.Webhooks.error_hooks(error, library=self, collection=collection, critical=critical)

        self.config.notify(text, library=self, collection=collection, critical=critical)

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
    def edit_tags(self, attr, obj, add_tags=None, remove_tags=None, sync_tags=None):
        pass

    @abstractmethod
    def get_all(self):
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
            util.print_multiline(f"YAML Error: {util.tab_new_lines(e)}", error=True)

    def map_guids(self):
        items = self.get_all()
        logger.info(f"Mapping {self.type} Library: {self.name}")
        logger.info("")
        for i, item in enumerate(items, 1):
            util.print_return(f"Processing: {i}/{len(items)} {item.title}")
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
        logger.info(util.adjust_space(f"Processed {len(items)} {self.type}s"))
        return items

    def find_collection_assets(self, item, name=None, create=False):
        if name is None:
            name = item.title
        for ad in self.asset_directory:
            poster = None
            background = None
            if self.asset_folders:
                if not os.path.isdir(os.path.join(ad, name)):
                    continue
                poster_filter = os.path.join(ad, name, "poster.*")
                background_filter = os.path.join(ad, name, "background.*")
            else:
                poster_filter = os.path.join(ad, f"{name}.*")
                background_filter = os.path.join(ad, f"{name}_background.*")
            matches = util.glob_filter(poster_filter)
            if len(matches) > 0:
                poster = ImageData("asset_directory", os.path.abspath(matches[0]), prefix=f"{item.title}'s ", is_url=False)
            matches = util.glob_filter(background_filter)
            if len(matches) > 0:
                background = ImageData("asset_directory", os.path.abspath(matches[0]), prefix=f"{item.title}'s ", is_poster=False, is_url=False)
            if poster or background:
                return poster, background
        if create and self.asset_folders and not os.path.isdir(os.path.join(self.asset_directory[0], name)):
            os.makedirs(os.path.join(self.asset_directory[0], name), exist_ok=True)
            logger.info(f"Asset Directory Created: {os.path.join(self.asset_directory[0], name)}")
        return None, None
