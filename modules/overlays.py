import os, re, time
from modules import util
from modules.builder import CollectionBuilder
from modules.util import Failed
from plexapi.exceptions import BadRequest
from plexapi.video import Movie, Show, Season, Episode
from PIL import Image, ImageFilter

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
        os.makedirs(self.library.overlay_backup, exist_ok=True)
        key_to_item = {}
        key_to_overlays = {}
        settings = {}
        if self.library.remove_overlays:
            logger.info("")
            logger.separator(f"Removing Overlays for the {self.library.name} Library")
            logger.info("")
        else:
            for overlay_file in self.library.overlay_files:
                for k, v in overlay_file.overlays.items():
                    try:
                        builder = CollectionBuilder(self.config, overlay_file, k, v, library=self.library, overlay=True)
                        logger.info("")

                        logger.separator(f"Gathering Items for {k} Overlay", space=False, border=False)

                        if builder.overlay not in settings:
                            settings[builder.overlay] = {
                                "keys": [], "suppress": [], "group": None,
                                "priority": None, "updated": False, "image": None
                            }

                        for method, value in builder.builders:
                            logger.debug("")
                            logger.debug(f"Builder: {method}: {value}")
                            logger.info("")
                            builder.filter_and_save_items(builder.gather_ids(method, value))

                        if builder.filters or builder.tmdb_filters:
                            logger.info("")
                            for filter_key, filter_value in builder.filters:
                                logger.info(f"Collection Filter {filter_key}: {filter_value}")
                            for filter_key, filter_value in builder.tmdb_filters:
                                logger.info(f"Collection Filter {filter_key}: {filter_value}")

                        added_titles = []
                        if builder.added_items:
                            for item in builder.added_items:
                                key_to_item[item.ratingKey] = item
                                added_titles.append(item.title)
                                if item.ratingKey not in settings[builder.overlay]["keys"]:
                                    settings[builder.overlay]["keys"].append(item.ratingKey)
                        if added_titles:
                            logger.debug(f"{len(added_titles)} Titles Found: {added_titles}")
                        logger.info(f"{len(added_titles) if added_titles else 'No'} Items found for {builder.overlay}")

                        if builder.suppress_overlays:
                            settings[builder.overlay]["suppress"] = builder.suppress_overlays
                    except Failed as e:
                        logger.error(e)

            overlay_groups = {}
            for overlay_name, over_attrs in settings.items():
                if over_attrs["group"]:
                    if over_attrs["group"] not in overlay_groups:
                        overlay_groups[over_attrs["group"]] = {}
                    overlay_groups[over_attrs["group"]][overlay_name] = over_attrs["priority"]
                for rk in over_attrs["keys"]:
                    for suppress_name in over_attrs["suppress"]:
                        if suppress_name in settings and rk in settings[suppress_name]["keys"]:
                            settings[suppress_name]["keys"].remove(rk)
                if not overlay_name.startswith("blur"):
                    clean_name, _ = util.validate_filename(overlay_name)
                    image_compare = None
                    if self.config.Cache:
                        _, image_compare, _ = self.config.Cache.query_image_map(overlay_name, f"{self.library.image_table_name}_overlays")
                    overlay_file = os.path.join(self.library.overlay_folder, f"{clean_name}.png")
                    overlay_size = os.stat(overlay_file).st_size
                    settings[overlay_name]["updated"] = not image_compare or str(overlay_size) != str(image_compare)
                    settings[overlay_name]["image"] = Image.open(overlay_file).convert("RGBA")
                    if self.config.Cache:
                        self.config.Cache.update_image_map(overlay_name, f"{self.library.image_table_name}_overlays", overlay_name, overlay_size)

            for overlay_name, over_attrs in settings.items():
                for over_key in over_attrs["keys"]:
                    if over_key not in key_to_overlays:
                        key_to_overlays[over_key] = (key_to_item[over_key], [])
                    key_to_overlays[over_key][1].append(overlay_name)

            for over_key, (item, over_names) in key_to_overlays.items():
                group_status = {}
                for over_name in over_names:
                    for overlay_group, group_names in overlay_groups.items():
                        if over_name in group_names:
                            if overlay_group not in group_status:
                                group_status[overlay_group] = []
                            group_status[overlay_group].append(over_name)
                for gk, gv in group_status.items():
                    if len(gv) > 1:
                        final = None
                        for v in gv:
                            if final is None or overlay_groups[gk][v] > overlay_groups[gk][final]:
                                final = v
                        for v in gv:
                            if final != v:
                                key_to_overlays[over_key][1].remove(v)

        def find_poster_url(plex_item):
            if isinstance(plex_item, Movie):
                if plex_item.ratingKey in self.library.movie_rating_key_map:
                    return self.config.TMDb.get_movie(self.library.movie_rating_key_map[plex_item.ratingKey]).poster_url
            elif isinstance(plex_item, (Show, Season, Episode)):
                check_key = plex_item.ratingKey if isinstance(plex_item, Show) else plex_item.show().ratingKey
                tmdb_id = self.config.Convert.tvdb_to_tmdb(self.library.show_rating_key_map[check_key])
                if isinstance(plex_item, Show) and plex_item.ratingKey in self.library.show_rating_key_map:
                    return self.config.TMDb.get_show(tmdb_id).poster_url
                elif isinstance(plex_item, Season):
                    return self.config.TMDb.get_season(tmdb_id, plex_item.seasonNumber).poster_url
                elif isinstance(plex_item, Episode):
                    return self.config.TMDb.get_episode(tmdb_id, plex_item.seasonNumber, plex_item.episodeNumber).still_url

        def get_overlay_items(libtype=None):
            return [o for o in self.library.search(label="Overlay", libtype=libtype) if o.ratingKey not in key_to_overlays]

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
            is_url = False
            original = None
            if poster:
                poster_location = poster.location
            elif os.path.exists(os.path.join(self.library.overlay_backup, f"{item.ratingKey}.png")):
                original = os.path.join(self.library.overlay_backup, f"{item.ratingKey}.png")
                poster_location = original
            elif os.path.exists(os.path.join(self.library.overlay_backup, f"{item.ratingKey}.jpg")):
                original = os.path.join(self.library.overlay_backup, f"{item.ratingKey}.jpg")
                poster_location = original
            else:
                is_url = True
                poster_location = find_poster_url(item)
            if poster_location:
                self.library.upload_poster(item, poster_location, url=is_url)
                self.library.edit_tags("label", item, remove_tags=["Overlay"], do_print=False)
                if original:
                    os.remove(original)
            else:
                logger.error(f"No Poster found to restore for {item.title}")
        logger.exorcise()

        if key_to_overlays:
            logger.info("")
            logger.separator(f"Applying Overlays for the {self.library.name} Library")
            logger.info("")
            for i, (over_key, (item, over_names)) in enumerate(sorted(key_to_overlays.items(), key=lambda io: io[1][0].titleSort), 1):
                util.check_time("Overlay Start Time")
                try:
                    logger.ghost(f"Overlaying: {i}/{len(key_to_overlays)} {item.title}")
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
                            if over_name not in overlay_compare or settings[over_name]["updated"]:
                                overlay_change = True

                    clean_name, _ = util.validate_filename(item.title)
                    util.check_time("Initial Bit")
                    poster, _, item_dir = self.library.find_assets(
                        name="poster" if self.library.asset_folders else clean_name,
                        folder_name=clean_name if self.library.asset_folders else None,
                        prefix=f"{item.title}'s "
                    )
                    util.check_time("Find Asset Time")

                    has_original = None
                    changed_image = False
                    new_backup = None
                    if poster:
                        if image_compare and str(poster.compare) != str(image_compare):
                            changed_image = True
                        util.check_time("Choose Image (From Assets) Time")
                    elif has_overlay:
                        test = "Backup"
                        if os.path.exists(os.path.join(self.library.overlay_backup, f"{item.ratingKey}.png")):
                            has_original = os.path.join(self.library.overlay_backup, f"{item.ratingKey}.png")
                        elif os.path.exists(os.path.join(self.library.overlay_backup, f"{item.ratingKey}.jpg")):
                            has_original = os.path.join(self.library.overlay_backup, f"{item.ratingKey}.jpg")
                        else:
                            test = "Online"
                            new_backup = find_poster_url(item)
                            if new_backup is None:
                                new_backup = item.posterUrl
                        util.check_time(f"Choose Image (From {test}) Time")
                    else:
                        new_backup = item.posterUrl
                        util.check_time("Choose Image (From Plex) Time")
                    if new_backup:
                        changed_image = True
                        image_response = self.config.get(new_backup)
                        if image_response.status_code >= 400:
                            raise Failed(f"Overlay Error: Poster Download Failed for {item.title}")
                        i_ext = "jpg" if image_response.headers["Content-Type"] == "image/jpeg" else "png"
                        backup_image_path = os.path.join(self.library.overlay_backup, f"{item.ratingKey}.{i_ext}")
                        with open(backup_image_path, "wb") as handler:
                            handler.write(image_response.content)
                        while util.is_locked(backup_image_path):
                            time.sleep(1)
                        has_original = backup_image_path
                    util.check_time("Find Image Time")

                    poster_compare = None
                    if poster is None and has_original is None:
                        logger.error(f"Overlay Error: No poster found for {item.title}")
                    elif changed_image or overlay_change:
                        new_poster = Image.open(poster.location if poster else has_original).convert("RGBA")
                        temp = os.path.join(self.library.overlay_folder, f"temp.png")
                        util.check_time("Open Image Time")
                        try:
                            blur_num = 0
                            for over_name in over_names:
                                if over_name.startswith("blur"):
                                    blur_test = int(re.search("\\(([^)]+)\\)", over_name).group(1))
                                    if blur_test > blur_num:
                                        blur_num = blur_test
                            if blur_num > 0:
                                new_poster = new_poster.filter(ImageFilter.GaussianBlur(blur_num))
                            for over_name in over_names:
                                if not over_name.startswith("blur"):
                                    new_poster = new_poster.resize(settings[over_name]["image"].size, Image.ANTIALIAS)
                                    new_poster.paste(settings[over_name]["image"], (0, 0), settings[over_name]["image"])
                            new_poster.save(temp, "PNG")
                            self.library.upload_poster(item, temp)
                            self.library.edit_tags("label", item, add_tags=["Overlay"], do_print=False)
                            self.library.reload(item)
                            poster_compare = poster.compare if poster else item.thumb
                            logger.info(f"Detail: Overlays: {', '.join(over_names)} applied to {item.title}")
                        except (OSError, BadRequest) as e:
                            logger.stacktrace()
                            raise Failed(f"Overlay Error: {e}")

                    if self.config.Cache and poster_compare:
                        self.config.Cache.update_image_map(item.ratingKey, self.library.image_table_name, item.thumb,
                                                           poster_compare, overlay=','.join(over_names))
                except Failed as e:
                    logger.error(e)
                util.check_time("Overall Overlay Time", end=True)
        logger.exorcise()
