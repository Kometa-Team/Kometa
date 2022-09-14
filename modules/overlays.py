import os, re, time
from datetime import datetime
from modules import plex, util, overlay
from modules.builder import CollectionBuilder
from modules.util import Failed, NonExisting, NotScheduled
from num2words import num2words
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
                        current_overlay = properties[over_name]
                        if current_overlay.name.startswith("blur"):
                            logger.info(over_name)
                            blur_test = int(re.search("\\(([^)]+)\\)", current_overlay.name).group(1))
                            if blur_test > blur_num:
                                blur_num = blur_test
                        elif current_overlay.queue:
                            if current_overlay.queue not in queue_overlays:
                                queue_overlays[current_overlay.queue] = {}
                            if current_overlay.weight in queue_overlays[current_overlay.queue]:
                                raise Failed("Overlay Error: Overlays in a queue cannot have the same weight")
                            queue_overlays[current_overlay.queue][current_overlay.weight] = over_name
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
                            current_overlay = properties[over_name]
                            if current_overlay.name.startswith("text"):
                                for cache_key, cache_value in self.config.Cache.query_overlay_special_text(item.ratingKey).items():
                                    actual = plex.attribute_translation[cache_key] if cache_key in plex.attribute_translation else cache_key
                                    if cache_value is None or not hasattr(item, actual) or getattr(item, actual) is None:
                                        continue
                                    if cache_key in overlay.float_vars:
                                        cache_value = float(cache_value)
                                    if cache_key in overlay.int_vars:
                                        cache_value = int(cache_value)

                                    if cache_key in overlay.date_vars:
                                        if getattr(item, actual).strftime("%Y-%m-%d") != cache_value:
                                            overlay_change = True
                                    elif getattr(item, actual) != cache_value:
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
                        if self.library.reset_overlays is not None:
                            if self.library.reset_overlays == "tmdb":
                                new_backup = self.find_poster_url(item)
                            else:
                                posters = item.posters()
                                if posters:
                                    new_backup = posters[0]
                        elif os.path.exists(os.path.join(self.library.overlay_backup, f"{item.ratingKey}.png")):
                            has_original = os.path.join(self.library.overlay_backup, f"{item.ratingKey}.png")
                        elif os.path.exists(os.path.join(self.library.overlay_backup, f"{item.ratingKey}.jpg")):
                            has_original = os.path.join(self.library.overlay_backup, f"{item.ratingKey}.jpg")
                        else:
                            new_backup = self.find_poster_url(item)
                    else:
                        new_backup = item.posterUrl
                    if new_backup:
                        changed_image = True
                        image_response = self.config.get(new_backup)
                        if image_response.status_code >= 400:
                            raise Failed(f"{item_title[:60]:<60} | Overlay Error: Image Download Failed")
                        if image_response.headers["Content-Type"] not in ["image/png", "image/jpeg"]:
                            raise Failed(f"{item_title[:60]:<60} | Overlay Error: Image Not JPG or PNG")
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

                            def get_text(text_overlay):
                                full_text = text_overlay.name[5:-1]
                                for format_var in overlay.vars_by_type[text_overlay.level]:
                                    if f"<<{format_var}" in full_text and format_var == "originally_available[":
                                        mod = re.search("<<originally_available\\[(.+)]>>", full_text).group(1)
                                        format_var = "originally_available"
                                    elif f"<<{format_var}>>" in full_text and format_var.endswith(tuple(m for m in overlay.double_mods)):
                                        mod = format_var[-2:]
                                        format_var = format_var[:-2]
                                    elif f"<<{format_var}>>" in full_text and format_var.endswith(tuple(m for m in overlay.single_mods)):
                                        mod = format_var[-1]
                                        format_var = format_var[:-1]
                                    elif f"<<{format_var}>>" in full_text:
                                        mod = ""
                                    else:
                                        continue
                                    if format_var == "show_title":
                                        actual_attr = "parentTitle" if text_overlay.level == "season" else "grandparentTitle"
                                    elif format_var in plex.attribute_translation:
                                        actual_attr = plex.attribute_translation[format_var]
                                    else:
                                        actual_attr = format_var
                                    if format_var == "bitrate":
                                        actual_value = None
                                        for media in item.media:
                                            current = int(media.bitrate)
                                            if actual_value is None:
                                                actual_value = current
                                                if mod == "":
                                                    break
                                            elif mod == "H" and current > actual_value:
                                                actual_value = current
                                            elif mod == "L" and current < actual_value:
                                                actual_value = current
                                    else:
                                        if not hasattr(item, actual_attr) or getattr(item, actual_attr) is None:
                                            raise Failed(f"Overlay Warning: No {full_text} found")
                                        actual_value = getattr(item, actual_attr)
                                        if format_var == "versions":
                                            actual_value = len(actual_value)
                                    if self.config.Cache:
                                        cache_store = actual_value.strftime("%Y-%m-%d") if format_var in overlay.date_vars else actual_value
                                        self.config.Cache.update_overlay_special_text(item.ratingKey, format_var, cache_store)
                                    sub_value = None
                                    if format_var == "originally_available":
                                        if mod:
                                            sub_value = "<<originally_available\\[(.+)]>>"
                                            final_value = actual_value.strftime(mod)
                                        else:
                                            final_value = actual_value.strftime("%Y-%m-%d")
                                    elif format_var == "runtime":
                                        if mod == "H":
                                            final_value = int((actual_value / 60000) // 60)
                                        elif mod == "M":
                                            final_value = int((actual_value / 60000) % 60)
                                        else:
                                            final_value = int(actual_value / 60000)
                                    elif mod == "%":
                                        final_value = int(actual_value * 10)
                                    elif mod == "#":
                                        final_value = str(actual_value)[:-2] if str(actual_value).endswith(".0") else actual_value
                                    elif mod == "W":
                                        final_value = num2words(int(actual_value))
                                    elif mod == "0":
                                        final_value = f"{int(actual_value):02}"
                                    elif mod == "00":
                                        final_value = f"{int(actual_value):03}"
                                    elif mod == "/":
                                        final_value = f"{int(actual_value) / 2:.2f}"
                                    elif mod == "U":
                                        final_value = str(actual_value).upper()
                                    elif mod == "L":
                                        final_value = str(actual_value).lower()
                                    elif mod == "P":
                                        final_value = str(actual_value).title()
                                    else:
                                        final_value = actual_value
                                    if sub_value:
                                        full_text = re.sub(sub_value, str(final_value), full_text)
                                    else:
                                        full_text = full_text.replace(f"<<{format_var}{mod}>>", str(final_value))
                                return str(full_text)

                            for over_name in applied_names:
                                current_overlay = properties[over_name]
                                if current_overlay.name.startswith("text"):
                                    if "<<" in current_overlay.name:
                                        image_box = current_overlay.image.size if current_overlay.image else None
                                        try:
                                            overlay_image, addon_box = current_overlay.get_backdrop((canvas_width, canvas_height), box=image_box, text=get_text(current_overlay))
                                        except Failed as e:
                                            logger.warning(e)
                                            continue
                                        new_poster.paste(overlay_image, (0, 0), overlay_image)
                                        if current_overlay.image:
                                            new_poster.paste(current_overlay.image, addon_box, current_overlay.image)
                                    else:
                                        overlay_image = current_overlay.landscape if isinstance(item, Episode) else current_overlay.portrait
                                        new_poster.paste(overlay_image, (0, 0), overlay_image)
                                else:
                                    if current_overlay.has_coordinates():
                                        if current_overlay.portrait is not None:
                                            overlay_image = current_overlay.landscape if isinstance(item, Episode) else current_overlay.portrait
                                            new_poster.paste(overlay_image, (0, 0), overlay_image)
                                        overlay_box = current_overlay.landscape_box if isinstance(item, Episode) else current_overlay.portrait_box
                                        new_poster.paste(current_overlay.image, overlay_box, current_overlay.image)
                                    else:
                                        new_poster = new_poster.resize(current_overlay.image.size, Image.ANTIALIAS)
                                        new_poster.paste(current_overlay.image, (0, 0), current_overlay.image)

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
                                    current_overlay = properties[over_name]
                                    if current_overlay.name.startswith("text"):
                                        image_box = current_overlay.image.size if current_overlay.image else None
                                        try:
                                            overlay_image, addon_box = current_overlay.get_backdrop((canvas_width, canvas_height), box=image_box, text=get_text(current_overlay), new_cords=cord)
                                        except Failed as e:
                                            logger.warning(e)
                                            continue
                                        new_poster.paste(overlay_image, (0, 0), overlay_image)
                                        if current_overlay.image:
                                            new_poster.paste(current_overlay.image, addon_box, current_overlay.image)
                                    else:
                                        if current_overlay.has_back:
                                            overlay_image, overlay_box = current_overlay.get_backdrop((canvas_width, canvas_height), box=current_overlay.image.size, new_cords=cord)
                                            new_poster.paste(overlay_image, (0, 0), overlay_image)
                                        else:
                                            overlay_box = current_overlay.get_coordinates((canvas_width, canvas_height), box=current_overlay.image.size, new_cords=cord)
                                        new_poster.paste(current_overlay.image, overlay_box, current_overlay.image)
                            temp = os.path.join(self.library.overlay_folder, f"temp.jpg")
                            new_poster.save(temp)
                            self.library.upload_poster(item, temp)
                            self.library.edit_tags("label", item, add_tags=["Overlay"], do_print=False)
                            self.library.reload(item, force=True)
                            poster_compare = poster.compare if poster else item.thumb
                            logger.info(f"{item_title[:60]:<60} | Overlays Applied: {', '.join(over_names)}")
                        except (OSError, BadRequest, SyntaxError) as e:
                            logger.stacktrace()
                            raise Failed(f"{item_title[:60]:<60} | Overlay Error: {e}")
                    elif self.library.show_asset_not_needed:
                        logger.info(f"{item_title[:60]:<60} | Overlay Update Not Needed")

                    if self.config.Cache and poster_compare:
                        self.config.Cache.update_image_map(item.ratingKey, f"{self.library.image_table_name}_overlays", item.thumb, poster_compare, overlay='|'.join(compare_names))
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
                    queues[k] = [overlay.parse_cords(q, f"{k} queue", required=True) for q in v]
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
                        try:
                            builder.filter_and_save_items(builder.gather_ids(method, value))
                        except NonExisting as e:
                            if builder.ignore_blank_results:
                                logger.warning("")
                                logger.warning(e)
                            else:
                                raise Failed(e)

                    added_titles = []
                    if builder.added_items:
                        for item in builder.added_items:
                            key_to_item[item.ratingKey] = item
                            added_titles.append(item)
                            if item.ratingKey not in properties[builder.overlay.mapping_name].keys:
                                properties[builder.overlay.mapping_name].keys.append(item.ratingKey)
                    if added_titles:
                        logger.debug(f"{len(added_titles)} Titles Found: {[self.library.get_item_sort_title(a, atr='title') for a in added_titles]}")
                        logger.info(f"{len(added_titles)} Items found for {builder.overlay.mapping_name} Overlay")
                    else:
                        logger.warning(f"No Items found for {builder.overlay.mapping_name} Overlay")
                    logger.info("")
                except NotScheduled as e:
                    logger.info(e)
                except Failed as e:
                    logger.stacktrace()
                    logger.error(e)
                    logger.info("")

        for overlay_name, over_obj in properties.items():
            if over_obj.group:
                if over_obj.group not in overlay_groups:
                    overlay_groups[over_obj.group] = {}
                overlay_groups[over_obj.group][overlay_name] = over_obj.weight

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
            for over_name in over_names:
                for suppress_name in properties[over_name].suppress:
                    if suppress_name in over_names:
                        key_to_overlays[over_key][1].remove(suppress_name)
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
