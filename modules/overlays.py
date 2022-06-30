import os, re, time
from datetime import datetime
from modules import plex, util
from modules.builder import CollectionBuilder
from modules.util import Failed, NotScheduled
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
        overlay_start = datetime.now()
        logger.info("")
        logger.separator(f"{self.library.name} Library Overlays")
        logger.info("")
        os.makedirs(self.library.overlay_backup, exist_ok=True)

        old_overlays = [la for la in self.library.Plex.listFilterChoices("label") if str(la.title).lower().endswith(" overlay")]
        if old_overlays:
            logger.info("")
            logger.separator(f"Removing Old Overlays for the {self.library.name} Library")
            logger.info("")
            for old_overlay in old_overlays:
                label_items = self.get_overlay_items(label=old_overlay)
                if label_items:
                    logger.info("")
                    logger.separator(f"Removing {old_overlay.title}")
                    logger.info("")
                    for i, item in enumerate(label_items, 1):
                        item_title = self.library.get_item_sort_title(item, atr="title")
                        logger.ghost(f"Restoring {old_overlay.title}: {i}/{len(label_items)} {item_title}")
                        self.remove_overlay(item, item_title, old_overlay.title, [
                            os.path.join(self.library.overlay_folder, old_overlay.title[:-8], f"{item.ratingKey}.png")
                        ])

        key_to_overlays = {}
        queues = {}
        properties = None
        if not self.library.remove_overlays:
            key_to_overlays, properties, queues = self.compile_overlays()
        ignore_list = [rk for rk in key_to_overlays]

        remove_overlays = self.get_overlay_items(ignore=ignore_list)
        if self.library.is_show:
            remove_overlays.extend(self.get_overlay_items(libtype="episode", ignore=ignore_list))
            remove_overlays.extend(self.get_overlay_items(libtype="season", ignore=ignore_list))
        elif self.library.is_music:
            remove_overlays.extend(self.get_overlay_items(libtype="album", ignore=ignore_list))

        logger.info("")
        if remove_overlays:
            logger.separator(f"Removing Overlays for the {self.library.name} Library")
            for i, item in enumerate(remove_overlays, 1):
                item_title = self.library.get_item_sort_title(item, atr="title")
                logger.ghost(f"Restoring: {i}/{len(remove_overlays)} {item_title}")
                self.remove_overlay(item, item_title, "Overlay", [
                    os.path.join(self.library.overlay_backup, f"{item.ratingKey}.png"),
                    os.path.join(self.library.overlay_backup, f"{item.ratingKey}.jpg")
                ])
            logger.exorcise()
        else:
            logger.separator(f"No Overlays to Remove for the {self.library.name} Library")
        logger.info("")
        if not self.library.remove_overlays:
            logger.info("")
            logger.separator(f"{'Re-' if self.library.reapply_overlays else ''}Applying Overlays for the {self.library.name} Library")
            logger.info("")
            for i, (over_key, (item, over_names)) in enumerate(sorted(key_to_overlays.items(), key=lambda io: self.library.get_item_sort_title(io[1][0])), 1):
                try:
                    item_title = self.library.get_item_sort_title(item, atr="title")
                    logger.ghost(f"Overlaying: {i}/{len(key_to_overlays)} {item_title}")
                    image_compare = None
                    overlay_compare = None
                    poster = None
                    if self.config.Cache:
                        image, image_compare, overlay_compare = self.config.Cache.query_image_map(item.ratingKey, f"{self.library.image_table_name}_overlays")

                    overlay_compare = [] if overlay_compare is None else util.get_list(overlay_compare, split="|")
                    has_overlay = any([item_tag.tag.lower() == "overlay" for item_tag in self.library.item_labels(item)])

                    compare_names = {properties[ov].get_overlay_compare(): ov for ov in over_names}
                    blur_num = 0
                    applied_names = []
                    queue_overlays = {}
                    for over_name in over_names:
                        overlay = properties[over_name]
                        if overlay.name.startswith("blur"):
                            logger.info(over_name)
                            blur_test = int(re.search("\\(([^)]+)\\)", overlay.name).group(1))
                            if blur_test > blur_num:
                                blur_num = blur_test
                        elif overlay.queue:
                            if overlay.queue not in queue_overlays:
                                queue_overlays[overlay.queue] = {}
                            if overlay.weight in queue_overlays[overlay.queue]:
                                raise Failed("Overlay Error: Overlays in a queue cannot have the same weight")
                            queue_overlays[overlay.queue][overlay.weight] = over_name
                        else:
                            applied_names.append(over_name)

                    overlay_change = False if has_overlay else True
                    if not overlay_change:
                        for oc in overlay_compare:
                            if oc not in compare_names:
                                overlay_change = True

                    if not overlay_change:
                        for compare_name, original_name in compare_names.items():
                            if compare_name not in overlay_compare or properties[original_name].updated:
                                overlay_change = True

                    if self.config.Cache:
                        for over_name in over_names:
                            overlay = properties[over_name]
                            if overlay.name in util.special_text_overlays:
                                rating_type = overlay.name[5:-1]
                                if rating_type.endswith(tuple(util.rating_mods)):
                                    rating_type = rating_type[:-1]
                                cache_rating = self.config.Cache.query_overlay_ratings(item.ratingKey, rating_type)
                                actual = plex.attribute_translation[rating_type]
                                if not hasattr(item, actual) or getattr(item, actual) is None:
                                    continue
                                if getattr(item, actual) != cache_rating:
                                    overlay_change = True

                    try:
                        poster, background, item_dir, name = self.library.find_item_assets(item)
                        if not poster and self.library.assets_for_all:
                            if (isinstance(item, Episode) and self.library.show_missing_episode_assets) or \
                                    (isinstance(item, Season) and self.library.show_missing_season_assets) or \
                                    (not isinstance(item, (Episode, Season)) and self.library.show_missing_assets):
                                if self.library.asset_folders:
                                    logger.warning(f"Asset Warning: No poster found for '{item_title}' in the assets folder '{item_dir}'")
                                else:
                                    logger.warning(f"Asset Warning: No poster '{name}' found in the assets folders")
                        if background:
                            self.library.upload_images(item, background=background)
                    except Failed as e:
                        if self.library.assets_for_all and self.library.show_missing_assets:
                            logger.warning(e)

                    has_original = None
                    changed_image = False
                    new_backup = None
                    if poster:
                        if image_compare and str(poster.compare) != str(image_compare):
                            changed_image = True
                    elif has_overlay:
                        if os.path.exists(os.path.join(self.library.overlay_backup, f"{item.ratingKey}.png")):
                            has_original = os.path.join(self.library.overlay_backup, f"{item.ratingKey}.png")
                        elif os.path.exists(os.path.join(self.library.overlay_backup, f"{item.ratingKey}.jpg")):
                            has_original = os.path.join(self.library.overlay_backup, f"{item.ratingKey}.jpg")
                        else:
                            new_backup = self.find_poster_url(item)
                            if new_backup is None:
                                new_backup = item.posterUrl
                    else:
                        new_backup = item.posterUrl
                    if new_backup:
                        changed_image = True
                        image_response = self.config.get(new_backup)
                        if image_response.status_code >= 400:
                            raise Failed(f"{item_title[:60]:<60} | Overlay Error: Poster Download Failed")
                        i_ext = "jpg" if image_response.headers["Content-Type"] == "image/jpeg" else "png"
                        backup_image_path = os.path.join(self.library.overlay_backup, f"{item.ratingKey}.{i_ext}")
                        with open(backup_image_path, "wb") as handler:
                            handler.write(image_response.content)
                        while util.is_locked(backup_image_path):
                            time.sleep(1)
                        has_original = backup_image_path

                    poster_compare = None
                    if poster is None and has_original is None:
                        logger.error(f"{item_title[:60]:<60} | Overlay Error: No poster found")
                    elif self.library.reapply_overlays or changed_image or overlay_change:
                        try:
                            canvas_width = 1920 if isinstance(item, Episode) else 1000
                            canvas_height = 1080 if isinstance(item, Episode) else 1500

                            new_poster = Image.open(poster.location if poster else has_original) \
                                .convert("RGB").resize((canvas_width, canvas_height), Image.ANTIALIAS)
                            if blur_num > 0:
                                new_poster = new_poster.filter(ImageFilter.GaussianBlur(blur_num))

                            def get_text(text):
                                text = text[5:-1]
                                if f"text({text})" in util.special_text_overlays:
                                    rating_code = text[-1:]
                                    text_rating_type = text[:-1] if rating_code in util.rating_mods else text
                                    text_actual = plex.attribute_translation[text_rating_type]
                                    if not hasattr(item, text_actual) or getattr(item, text_actual) is None:
                                        raise Failed(f"Overlay Warning: No {text_rating_type} found")
                                    text = getattr(item, text_actual)
                                    if self.config.Cache:
                                        self.config.Cache.update_overlay_ratings(item.ratingKey, text_rating_type, text)
                                    if rating_code in ["%", "0"]:
                                        text = f"{int(text * 10)}{'%' if rating_code == '%' else ''}"
                                    if rating_code == "#" and str(text).endswith(".0"):
                                        text = str(text)[:-2]
                                return str(text)

                            for over_name in applied_names:
                                overlay = properties[over_name]
                                if overlay.name.startswith("text"):
                                    if overlay.name in util.special_text_overlays:
                                        image_box = overlay.image.size if overlay.image else None
                                        try:
                                            overlay_image, addon_box = overlay.get_backdrop((canvas_width, canvas_height), box=image_box, text=get_text(overlay.name))
                                        except Failed as e:
                                            logger.warning(e)
                                            continue
                                        new_poster.paste(overlay_image, (0, 0), overlay_image)
                                        if overlay.image:
                                            new_poster.paste(overlay.image, addon_box, overlay.image)
                                    else:
                                        overlay_image = overlay.landscape if isinstance(item, Episode) else overlay.portrait
                                        new_poster.paste(overlay_image, (0, 0), overlay_image)
                                else:
                                    if overlay.has_coordinates():
                                        if overlay.portrait is not None:
                                            overlay_image = overlay.landscape if isinstance(item, Episode) else overlay.portrait
                                            new_poster.paste(overlay_image, (0, 0), overlay_image)
                                        overlay_box = overlay.landscape_box if isinstance(item, Episode) else overlay.portrait_box
                                        new_poster.paste(overlay.image, overlay_box, overlay.image)
                                    else:
                                        new_poster = new_poster.resize(overlay.image.size, Image.ANTIALIAS)
                                        new_poster.paste(overlay.image, (0, 0), overlay.image)

                            for queue, weights in queue_overlays.items():
                                if queue not in queues:
                                    logger.error(f"Overlay Error: no queue {queue} found")
                                    continue
                                cords = queues[queue]
                                sorted_weights = sorted(weights.items(), reverse=True)
                                for o, cord in enumerate(cords):
                                    if len(sorted_weights) <= o:
                                        break
                                    over_name = sorted_weights[o][1]
                                    overlay = properties[over_name]
                                    if overlay.name.startswith("text"):
                                        image_box = overlay.image.size if overlay.image else None
                                        try:
                                            overlay_image, addon_box = overlay.get_backdrop((canvas_width, canvas_height), box=image_box, text=get_text(overlay.name), new_cords=cord)
                                        except Failed as e:
                                            logger.warning(e)
                                            continue
                                        new_poster.paste(overlay_image, (0, 0), overlay_image)
                                        if overlay.image:
                                            new_poster.paste(overlay.image, addon_box, overlay.image)
                                    else:
                                        if overlay.has_back:
                                            overlay_image, overlay_box = overlay.get_backdrop((canvas_width, canvas_height), box=overlay.image.size, new_cords=cord)
                                            new_poster.paste(overlay_image, (0, 0), overlay_image)
                                        else:
                                            overlay_box = overlay.get_coordinates((canvas_width, canvas_height), box=overlay.image.size, new_cords=cord)
                                        new_poster.paste(overlay.image, overlay_box, overlay.image)
                            temp = os.path.join(self.library.overlay_folder, f"temp.png")
                            new_poster.save(temp, "PNG")
                            self.library.upload_poster(item, temp)
                            self.library.edit_tags("label", item, add_tags=["Overlay"], do_print=False)
                            self.library.reload(item, force=True)
                            poster_compare = poster.compare if poster else item.thumb
                            logger.info(f"{item_title[:60]:<60} | Overlays Applied: {', '.join(over_names)}")
                        except (OSError, BadRequest) as e:
                            logger.stacktrace()
                            raise Failed(f"{item_title[:60]:<60} | Overlay Error: {e}")
                    elif self.library.show_asset_not_needed:
                        logger.info(f"{item_title[:60]:<60} | Overlay Update Not Needed")

                    if self.config.Cache and poster_compare:
                        self.config.Cache.update_image_map(item.ratingKey, f"{self.library.image_table_name}_overlays",
                                                           item.thumb, poster_compare, overlay='|'.join(compare_names))
                except Failed as e:
                    logger.error(e)
        logger.exorcise()
        overlay_run_time = str(datetime.now() - overlay_start).split('.')[0]
        logger.info("")
        logger.separator(f"Finished {self.library.name} Library Overlays\nOverlays Run Time: {overlay_run_time}")
        return overlay_run_time

    def compile_overlays(self):
        key_to_item = {}
        properties = {}
        overlay_groups = {}
        key_to_overlays = {}
        queues = {}

        for overlay_file in self.library.overlay_files:
            for k, v in overlay_file.queues.items():
                if not isinstance(v, list):
                    raise Failed(f"Overlay Error: Queue: {k} must be a list")
                try:
                    queues[k] = [util.parse_cords(q, f"{k} queue", required=True) for q in v]
                except Failed as e:
                    logger.error(e)
            for k, v in overlay_file.overlays.items():
                try:
                    builder = CollectionBuilder(self.config, overlay_file, k, v, library=self.library, overlay=True)
                    logger.info("")

                    logger.separator(f"Gathering Items for {k} Overlay", space=False, border=False)

                    if builder.overlay.mapping_name in properties:
                        raise Failed(f"Overlay Error: Overlay {builder.overlay.mapping_name} already exists")
                    properties[builder.overlay.mapping_name] = builder.overlay

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
                            added_titles.append(item)
                            if item.ratingKey not in properties[builder.overlay.mapping_name].keys:
                                properties[builder.overlay.mapping_name].keys.append(item.ratingKey)
                    if added_titles:
                        logger.debug(f"{len(added_titles)} Titles Found: {[self.library.get_item_sort_title(a, atr='title') for a in added_titles]}")
                    logger.info(f"{len(added_titles) if added_titles else 'No'} Items found for {builder.overlay.mapping_name}")
                except NotScheduled as e:
                    logger.info(e)
                except Failed as e:
                    logger.stacktrace()
                    logger.error(e)

        for overlay_name, over_obj in properties.items():
            if over_obj.group:
                if over_obj.group not in overlay_groups:
                    overlay_groups[over_obj.group] = {}
                overlay_groups[over_obj.group][overlay_name] = over_obj.weight
            for rk in over_obj.keys:
                for suppress_name in over_obj.suppress:
                    if suppress_name in properties and rk in properties[suppress_name].keys:
                        properties[suppress_name].keys.remove(rk)

        for overlay_name, over_obj in properties.items():
            for over_key in over_obj.keys:
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
        return key_to_overlays, properties, queues

    def find_poster_url(self, item):
        try:
            if isinstance(item, Movie):
                if item.ratingKey in self.library.movie_rating_key_map:
                    return self.config.TMDb.get_movie(self.library.movie_rating_key_map[item.ratingKey]).poster_url
            elif isinstance(item, (Show, Season, Episode)):
                check_key = item.ratingKey if isinstance(item, Show) else item.show().ratingKey
                if check_key in self.library.show_rating_key_map:
                    tmdb_id = self.config.Convert.tvdb_to_tmdb(self.library.show_rating_key_map[check_key])
                    if isinstance(item, Show) and item.ratingKey in self.library.show_rating_key_map:
                        return self.config.TMDb.get_show(tmdb_id).poster_url
                    elif isinstance(item, Season):
                        return self.config.TMDb.get_season(tmdb_id, item.seasonNumber).poster_url
                    elif isinstance(item, Episode):
                        return self.config.TMDb.get_episode(tmdb_id, item.seasonNumber, item.episodeNumber).still_url
        except Failed as e:
            logger.error(e)

    def get_overlay_items(self, label="Overlay", libtype=None, ignore=None):
        items = self.library.search(label=label, libtype=libtype)
        return items if not ignore else [o for o in items if o.ratingKey not in ignore]

    def remove_overlay(self, item, item_title, label, locations):
        try:
            poster, _, _, _ = self.library.find_item_assets(item)
        except Failed:
            poster = None
        is_url = False
        original = None
        if poster:
            poster_location = poster.location
        elif any([os.path.exists(loc) for loc in locations]):
            original = next((loc for loc in locations if os.path.exists(loc)))
            poster_location = original
        else:
            is_url = True
            poster_location = self.find_poster_url(item)
        if poster_location:
            self.library.upload_poster(item, poster_location, url=is_url)
            self.library.edit_tags("label", item, remove_tags=[label], do_print=False)
            if original:
                os.remove(original)
        else:
            logger.error(f"No Poster found to restore for {item_title}")
