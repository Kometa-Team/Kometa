import os, time
from modules import util
from modules.builder import CollectionBuilder
from modules.util import Failed
from plexapi.exceptions import BadRequest
from plexapi.video import Show, Season, Episode
from PIL import Image

logger = util.logger

class Overlays:
    def __init__(self, config, library):
        self.config = config
        self.library = library
        self.overlays = []

    def run_overlays(self):
        logger.info("")
        logger.separator(f"{self.library.name} Library Overlays")
        logger.info("")
        overlay_rating_keys = {}
        item_keys = {}
        os.makedirs(self.library.overlay_backup, exist_ok=True)
        overlay_updated = {}
        overlay_images = {}
        item_overlays = {}
        if not self.library.remove_overlays:
            for overlay_file in self.library.overlay_files:
                for k, v in overlay_file.overlays.items():
                    builder = CollectionBuilder(self.config, overlay_file, k, v, library=self.library, overlay=True)
                    logger.info("")

                    logger.separator(f"Running {k} Overlay", space=False, border=False)

                    if builder.filters or builder.tmdb_filters:
                        logger.info("")
                        for filter_key, filter_value in builder.filters:
                            logger.info(f"Collection Filter {filter_key}: {filter_value}")
                        for filter_key, filter_value in builder.tmdb_filters:
                            logger.info(f"Collection Filter {filter_key}: {filter_value}")

                    for method, value in builder.builders:
                        logger.debug("")
                        logger.debug(f"Builder: {method}: {value}")
                        logger.info("")
                        builder.filter_and_save_items(builder.gather_ids(method, value))
                        if builder.added_items:
                            if builder.overlay not in overlay_rating_keys:
                                overlay_rating_keys[builder.overlay] = []
                            for item in builder.added_items:
                                item_keys[item.ratingKey] = item
                                if item.ratingKey not in overlay_rating_keys[builder.overlay]:
                                    overlay_rating_keys[builder.overlay].append(item.ratingKey)

            for overlay_name, over_keys in overlay_rating_keys.items():
                clean_name, _ = util.validate_filename(overlay_name)
                image_compare = None
                if self.config.Cache:
                    _, image_compare, _ = self.config.Cache.query_image_map(overlay_name, f"{self.library.image_table_name}_overlays")
                overlay_file = os.path.join(self.library.overlay_folder, f"{clean_name}.png")
                overlay_size = os.stat(overlay_file).st_size
                overlay_updated[overlay_name] = not image_compare or str(overlay_size) != str(image_compare)
                overlay_images[overlay_name] = Image.open(overlay_file).convert("RGBA")
                for over_key in over_keys:
                    if over_key not in item_overlays:
                        item_overlays[over_key] = []
                    item_overlays[over_key].append(overlay_name)
                if self.config.Cache:
                    self.config.Cache.update_image_map(overlay_name, f"{self.library.image_table_name}_overlays", overlay_name, overlay_size)

        def get_overlay_items(libtype=None):
            return [o for o in self.library.search(label="Overlay", libtype=libtype) if o.ratingKey not in item_overlays]

        remove_overlays = get_overlay_items()
        if self.library.is_show:
            remove_overlays.extend(get_overlay_items(libtype="episode"))
            remove_overlays.extend(get_overlay_items(libtype="season"))
        elif self.library.is_music:
            remove_overlays.extend(get_overlay_items(libtype="album"))

        for i, item in enumerate(remove_overlays, 1):
            logger.ghost(f"Restoring: {i}/{len(remove_overlays)} {item.title}")
            clean_name, _ = util.validate_filename(item.title)
            poster, _, item_dir = self.library.find_assets(
                name="poster" if self.library.asset_folders else clean_name,
                folder_name=clean_name if self.library.asset_folders else None,
                prefix=f"{item.title}'s "
            )
            poster_location = None
            is_url = False
            if poster:
                poster_location = poster.location
            elif os.path.exists(os.path.join(self.library.overlay_backup, f"{item.ratingKey}.png")):
                poster_location = os.path.join(self.library.overlay_backup, f"{item.ratingKey}.png")
            elif os.path.exists(os.path.join(self.library.overlay_backup, f"{item.ratingKey}.jpg")):
                poster_location = os.path.join(self.library.overlay_backup, f"{item.ratingKey}.jpg")
            else:
                is_url = True
                if self.library.is_movie:
                    if item.ratingKey in self.library.movie_rating_key_map:
                        poster_location = self.config.TMDb.get_movie(self.library.movie_rating_key_map[item.ratingKey]).poster_url
                elif self.library.is_show:
                    if item.ratingKey in self.library.show_rating_key_map:
                        poster_location = self.config.TMDb.get_show(self.config.Convert.tvdb_to_tmdb(self.library.show_rating_key_map[item.ratingKey])).poster_url
            if poster_location:
                self.library.upload_poster(item, poster_location, url=is_url)
                self.library.edit_tags("label", item, remove_tags=["Overlay"])
            else:
                logger.error(f"No Poster found to restore for {item.title}")
        logger.exorcise()

        for i, (over_key, over_names) in enumerate(item_overlays.items(), 1):
            try:
                item = item_keys[over_key]
                logger.ghost(f"Overlaying: {i}/{len(item_overlays)} {item.title}")
                image_compare = None
                overlay_compare = None
                if self.config.Cache:
                    image, image_compare, _ = self.config.Cache.query_image_map(item.ratingKey, f"{self.library.image_table_name}_overlays")
                overlay_compare = [] if overlay_compare is None else util.get_list(overlay_compare)
                has_overlay = any([item_tag.tag.lower() == "overlay" for item_tag in item.labels])

                overlay_change = False if has_overlay else True
                if not overlay_change:
                    for oc in overlay_compare:
                        if oc not in over_names:
                            overlay_change = True
                if not overlay_change:
                    for over_name in over_names:
                        if over_name not in overlay_compare or overlay_updated[over_name]:
                            overlay_change = True

                clean_name, _ = util.validate_filename(item.title)
                poster, _, item_dir = self.library.find_assets(
                    name="poster" if self.library.asset_folders else clean_name,
                    folder_name=clean_name if self.library.asset_folders else None,
                    prefix=f"{item.title}'s "
                )
                has_original = False
                changed_image = False
                if poster:
                    if image_compare and str(poster.compare) != str(image_compare):
                        changed_image = True
                else:
                    if os.path.exists(os.path.join(self.library.overlay_backup, f"{item.ratingKey}.png")):
                        has_original = os.path.join(self.library.overlay_backup, f"{item.ratingKey}.png")
                    elif os.path.exists(os.path.join(self.library.overlay_backup, f"{item.ratingKey}.jpg")):
                        has_original = os.path.join(self.library.overlay_backup, f"{item.ratingKey}.jpg")
                    else:
                        changed_image = True
                        self.library.reload(item)
                        poster_url = item.posterUrl
                        if has_overlay:
                            if self.library.is_movie:
                                if item.ratingKey in self.library.movie_rating_key_map:
                                    poster_url = self.config.TMDb.get_movie(self.library.movie_rating_key_map[item.ratingKey]).poster_url
                            elif self.library.is_show:
                                check_key = item.ratingKey if isinstance(item, Show) else item.show().ratingKey
                                tmdb_id = self.config.Convert.tvdb_to_tmdb(self.library.show_rating_key_map[check_key])
                                if isinstance(item, Show) and item.ratingKey in self.library.show_rating_key_map:
                                    poster_url = self.config.TMDb.get_show(tmdb_id).poster_url
                                elif isinstance(item, Season):
                                    poster_url = self.config.TMDb.get_season(tmdb_id, item.seasonNumber).poster_url
                                elif isinstance(item, Episode):
                                    poster_url = self.config.TMDb.get_episode(tmdb_id, item.seasonNumber, item.episodeNumber).still_url
                        response = self.config.get(poster_url)
                        if response.status_code >= 400:
                            raise Failed(f"Overlay Error: Poster Download Failed for {item.title}")
                        ext = "jpg" if response.headers["Content-Type"] == "image/jpeg" else "png"
                        backup_image = os.path.join(self.library.overlay_backup, f"{item.ratingKey}.{ext}")
                        with open(backup_image, "wb") as handler:
                            handler.write(response.content)
                        while util.is_locked(backup_image):
                            time.sleep(1)
                        has_original = backup_image

                poster_uploaded = False
                if changed_image or overlay_change:
                    new_poster = Image.open(poster.location if poster else has_original).convert("RGBA")
                    temp = os.path.join(self.library.overlay_folder, f"temp.png")
                    try:
                        for over_name in over_names:
                            new_poster = new_poster.resize(overlay_images[over_name].size, Image.ANTIALIAS)
                            new_poster.paste(overlay_images[over_name], (0, 0), overlay_images[over_name])
                        new_poster.save(temp, "PNG")
                        self.library.upload_poster(item, temp)
                        self.library.edit_tags("label", item, add_tags=["Overlay"])
                        self.library.reload(item)
                        poster_uploaded = True
                        logger.info(f"Detail: Overlays: {', '.join(over_names)} applied to {item.title}")
                    except (OSError, BadRequest) as e:
                        logger.stacktrace()
                        raise Failed(f"Overlay Error: {e}")

                if self.config.Cache:
                    if poster_uploaded:
                        self.config.Cache.update_image_map(
                            item.ratingKey, self.library.image_table_name, item.thumb,
                            poster.compare if poster else item.thumb, overlay=','.join(over_names)
                        )
            except Failed as e:
                logger.error(e)
        logger.exorcise()
