import os, re
from datetime import datetime
from modules import plex, util, anidb
from modules.util import Failed, LimitReached, YAML
from plexapi.exceptions import NotFound

logger = util.logger

meta_operations = [
    "mass_audience_rating_update", "mass_user_rating_update", "mass_critic_rating_update",
    "mass_episode_audience_rating_update", "mass_episode_user_rating_update", "mass_episode_critic_rating_update",
    "mass_genre_update", "mass_content_rating_update", "mass_originally_available_update", "mass_original_title_update",
    "mass_poster_update", "mass_background_update", "mass_studio_update"
]
name_display = {
    "audienceRating": "Audience Rating",
    "rating": "Critic Rating",
    "userRating": "User Rating",
    "originallyAvailableAt": "Originally Available Date",
    "contentRating": "Content Rating"
}

class Operations:
    def __init__(self, config, library):
        self.config = config
        self.library = library

    def run_operations(self):
        operation_start = datetime.now()
        logger.info("")
        logger.separator(f"{self.library.name} Library Operations")
        logger.info("")
        logger.debug(f"Assets For All: {self.library.assets_for_all}")
        logger.debug(f"Delete Collections: {self.library.delete_collections}")
        logger.debug(f"Show Unmanaged Collections: {self.library.show_unmanaged}")
        logger.debug(f"Show Unconfigured Collections: {self.library.show_unconfigured}")
        logger.debug(f"Mass Genre Update: {self.library.mass_genre_update}")
        logger.debug(f"Mass Audience Rating Update: {self.library.mass_audience_rating_update}")
        logger.debug(f"Mass Critic Rating Update: {self.library.mass_critic_rating_update}")
        logger.debug(f"Mass User Rating Update: {self.library.mass_user_rating_update}")
        logger.debug(f"Mass Episode Audience Rating Update: {self.library.mass_episode_audience_rating_update}")
        logger.debug(f"Mass Episode Critic Rating Update: {self.library.mass_episode_critic_rating_update}")
        logger.debug(f"Mass Episode User Rating Update: {self.library.mass_episode_user_rating_update}")
        logger.debug(f"Mass Content Rating Update: {self.library.mass_content_rating_update}")
        logger.debug(f"Mass Original Title Update: {self.library.mass_original_title_update}")
        logger.debug(f"Mass Originally Available Update: {self.library.mass_originally_available_update}")
        logger.debug(f"Mass IMDb Parental Labels: {self.library.mass_imdb_parental_labels}")
        logger.debug(f"Mass Poster Update: {self.library.mass_poster_update}")
        logger.debug(f"Mass Background Update: {self.library.mass_background_update}")
        logger.debug(f"Mass Collection Mode Update: {self.library.mass_collection_mode}")
        logger.debug(f"Split Duplicates: {self.library.split_duplicates}")
        logger.debug(f"Radarr Add All Existing: {self.library.radarr_add_all_existing}")
        logger.debug(f"Radarr Remove by Tag: {self.library.radarr_remove_by_tag}")
        logger.debug(f"Sonarr Add All Existing: {self.library.sonarr_add_all_existing}")
        logger.debug(f"Sonarr Remove by Tag: {self.library.sonarr_remove_by_tag}")
        logger.debug(f"Update Blank Track Titles: {self.library.update_blank_track_titles}")
        logger.debug(f"Update Remove Title Parentheses: {self.library.remove_title_parentheses}")
        logger.debug(f"Genre Mapper: {self.library.genre_mapper}")
        logger.debug(f"Content Rating Mapper: {self.library.content_rating_mapper}")
        logger.debug(f"Metadata Backup: {self.library.metadata_backup}")
        logger.debug(f"Item Operation: {self.library.items_library_operation}")
        logger.debug("")

        if self.library.split_duplicates:
            items = self.library.search(**{"duplicate": True})
            for item in items:
                item.split()
                logger.info(f"{item.title[:25]:<25} | Splitting")

        if self.library.update_blank_track_titles:
            tracks = self.library.get_all(builder_level="track")
            num_edited = 0
            for i, track in enumerate(tracks, 1):
                logger.ghost(f"Processing Track: {i}/{len(tracks)} {track.title}")
                if not track.title and track.titleSort:
                    track.editTitle(track.titleSort)
                    num_edited += 1
                    logger.info(f"Track: {track.titleSort} was updated with sort title")
            logger.info(f"{len(tracks)} Tracks Processed; {num_edited} Blank Track Titles Updated")

        if self.library.items_library_operation:
            items = self.library.get_all()
            radarr_adds = []
            sonarr_adds = []
            label_edits = {"add": {}, "remove": {}}
            rating_edits = {"audienceRating": {}, "rating": {}, "userRating": {}}
            genre_edits = {"add": {}, "remove": {}}
            content_edits = {}
            studio_edits = {}
            available_edits = {}
            remove_edits = {}
            reset_edits = {}
            lock_edits = {}
            unlock_edits = {}
            ep_rating_edits = {"audienceRating": {}, "rating": {}, "userRating": {}}
            ep_remove_edits = {}
            ep_reset_edits = {}
            ep_lock_edits = {}
            ep_unlock_edits = {}

            trakt_ratings = self.config.Trakt.user_ratings(self.library.is_movie) if any([o == "trakt_user" for o in self.library.meta_operations]) else []

            reverse_anidb = {}
            for k, v in self.library.anidb_map.items():
                reverse_anidb[v] = k
            reverse_mal = {}
            for k, v in self.library.mal_map.items():
                reverse_mal[v] = k

            if self.library.assets_for_all and not self.library.asset_directory:
                logger.error("Asset Error: No Asset Directory for Assets For All")

            for i, item in enumerate(items, 1):
                logger.info("")
                logger.info(f"Processing: {i}/{len(items)} {item.title}")
                try:
                    item = self.library.reload(item)
                except Failed as e:
                    logger.error(e)
                    continue
                current_labels = [la.tag for la in self.library.item_labels(item)] if self.library.label_operations else []

                if self.library.assets_for_all and self.library.asset_directory:
                    self.library.find_and_upload_assets(item, current_labels)

                locked_fields = [f.name for f in item.fields if f.locked]

                tmdb_id, tvdb_id, imdb_id = self.library.get_ids(item)

                item_edits = ""

                if self.library.remove_title_parentheses:
                    if not any([f.name == "title" and f.locked for f in item.fields]) and item.title.endswith(")"):
                        new_title = re.sub(" \\(\\w+\\)$", "", item.title)
                        item.editTitle(new_title)
                        item_edits += f"\nUpdated Title: {item.title[:25]:<25} | {new_title}"

                if self.library.mass_imdb_parental_labels:
                    try:
                        if self.library.mass_imdb_parental_labels == "remove":
                            parental_labels = []
                        else:
                            parental_guide = self.config.IMDb.parental_guide(imdb_id)
                            parental_labels = [f"{k.capitalize()}:{v}" for k, v in parental_guide.items() if v not in util.parental_levels[self.library.mass_imdb_parental_labels]]
                        add_labels = [la for la in parental_labels if la not in current_labels]
                        remove_labels = [la for la in current_labels if la in util.parental_labels and la not in parental_labels]
                        for label_list, edit_type in [(add_labels, "add"), (remove_labels, "remove")]:
                            if label_list:
                                for label in label_list:
                                    if label not in label_edits[edit_type]:
                                        label_edits[edit_type][label] = []
                                    label_edits[edit_type][label].append(item.ratingKey)
                                item_edits += f"\n{edit_type.capitalize()} IMDb Parental Labels (Batched) | {', '.join(label_list)}"
                    except Failed:
                        pass
                if item.locations:
                    path = os.path.dirname(str(item.locations[0])) if self.library.is_movie else str(item.locations[0])
                    if self.library.Radarr and self.library.radarr_add_all_existing and tmdb_id:
                        path = path.replace(self.library.Radarr.plex_path, self.library.Radarr.radarr_path)
                        path = path[:-1] if path.endswith(('/', '\\')) else path
                        radarr_adds.append((tmdb_id, path))
                    if self.library.Sonarr and self.library.sonarr_add_all_existing and tvdb_id:
                        path = path.replace(self.library.Sonarr.plex_path, self.library.Sonarr.sonarr_path)
                        path = path[:-1] if path.endswith(("/", "\\")) else path
                        sonarr_adds.append((tvdb_id, path))

                tmdb_item = None
                if any([o == "tmdb" for o in self.library.meta_operations]):
                    try:
                        tmdb_item = self.config.TMDb.get_item(item, tmdb_id, tvdb_id, imdb_id, is_movie=self.library.is_movie)
                    except Failed as e:
                        logger.error(str(e))

                omdb_item = None
                if any([o == "omdb" for o in self.library.meta_operations]):
                    if self.config.OMDb.limit is not False:
                        logger.error("Daily OMDb Limit Reached")
                    elif not imdb_id:
                        logger.info(f" No IMDb ID for Guid: {item.guid}")
                    else:
                        try:
                            omdb_item = self.config.OMDb.get_omdb(imdb_id)
                        except Failed as e:
                            logger.error(str(e))
                        except Exception:
                            logger.error(f"IMDb ID: {imdb_id}")
                            raise

                tvdb_item = None
                if any([o == "tvdb" for o in self.library.meta_operations]):
                    if tvdb_id:
                        try:
                            tvdb_item = self.config.TVDb.get_tvdb_obj(tvdb_id, is_movie=self.library.is_movie)
                        except Failed as e:
                            logger.error(str(e))
                    else:
                        logger.info(f"No TVDb ID for Guid: {item.guid}")

                anidb_item = None
                mal_item = None
                if any([o.startswith("anidb") or o.startswith("mal") for o in self.library.meta_operations]):
                    if item.ratingKey in reverse_anidb:
                        anidb_id = reverse_anidb[item.ratingKey]
                    elif tvdb_id in self.config.Convert._tvdb_to_anidb:
                        anidb_id = self.config.Convert._tvdb_to_anidb[tvdb_id]
                    elif imdb_id in self.config.Convert._imdb_to_anidb:
                        anidb_id = self.config.Convert._imdb_to_anidb[imdb_id]
                    else:
                        anidb_id = None
                    if any([o.startswith("anidb") for o in self.library.meta_operations]):
                        if anidb_id:
                            try:
                                anidb_item = self.config.AniDB.get_anime(anidb_id)
                            except Failed as e:
                                logger.error(str(e))
                        else:
                            logger.warning(f"No AniDB ID for Guid: {item.guid}")
                    if any([o.startswith("mal") for o in self.library.meta_operations]):
                        if item.ratingKey in reverse_mal:
                            mal_id = reverse_mal[item.ratingKey]
                        elif not anidb_id:
                            logger.warning(f"Convert Warning: No AniDB ID to Convert to MyAnimeList ID for Guid: {item.guid}")
                            mal_id = None
                        elif anidb_id not in self.config.Convert._anidb_to_mal:
                            logger.warning(f"Convert Warning: No MyAnimeList Found for AniDB ID: {anidb_id} of Guid: {item.guid}")
                            mal_id = None
                        else:
                            mal_id = self.config.Convert._anidb_to_mal[anidb_id]
                        if mal_id:
                            try:
                                mal_item = self.config.MyAnimeList.get_anime(mal_id)
                            except Failed as e:
                                logger.error(str(e))

                mdb_item = None
                if any([o and o.startswith("mdb") for o in self.library.meta_operations]):
                    if self.config.Mdblist.limit is False:
                        try:
                            if self.library.is_show and tvdb_id and mdb_item is None:
                                try:
                                    mdb_item = self.config.Mdblist.get_series(tvdb_id)
                                except Failed as e:
                                    logger.trace(str(e))
                                except Exception:
                                    logger.trace(f"TVDb ID: {tvdb_id}")
                                    raise
                            if tmdb_id and mdb_item is None:
                                try:
                                    mdb_item = self.config.Mdblist.get_movie(tmdb_id)
                                except LimitReached as e:
                                    logger.debug(e)
                                except Failed as e:
                                    logger.trace(str(e))
                                except Exception:
                                    logger.trace(f"TMDb ID: {tmdb_id}")
                                    raise
                            if imdb_id and mdb_item is None:
                                try:
                                    mdb_item = self.config.Mdblist.get_imdb(imdb_id)
                                except LimitReached as e:
                                    logger.debug(e)
                                except Failed as e:
                                    logger.trace(str(e))
                                except Exception:
                                    logger.trace(f"IMDb ID: {imdb_id}")
                                    raise
                            if mdb_item is None:
                                logger.warning(f"No MdbItem for {item.title} (Guid: {item.guid})")
                        except LimitReached as e:
                            logger.debug(e)
                for attribute, item_attr in [
                    (self.library.mass_audience_rating_update, "audienceRating"),
                    (self.library.mass_critic_rating_update, "rating"),
                    (self.library.mass_user_rating_update, "userRating")
                ]:
                    if attribute:
                        current = getattr(item, item_attr)
                        if attribute == "remove" and current is not None:
                            if item_attr not in remove_edits:
                                remove_edits[item_attr] = []
                            remove_edits[item_attr].append(item.ratingKey)
                            item_edits += f"\nRemove {name_display[item_attr]} (Batched)"
                        elif attribute == "reset" and current is not None:
                            if item_attr not in reset_edits:
                                reset_edits[item_attr] = []
                            reset_edits[item_attr].append(item.ratingKey)
                            item_edits += f"\nReset {name_display[item_attr]} (Batched)"
                        elif attribute in ["unlock", "reset"] and item_attr in locked_fields:
                            if item_attr not in unlock_edits:
                                unlock_edits[item_attr] = []
                            unlock_edits[item_attr].append(item.ratingKey)
                            item_edits += f"\nUnlock {name_display[item_attr]} (Batched)"
                        elif attribute in ["lock", "remove"] and item_attr not in locked_fields:
                            if item_attr not in lock_edits:
                                lock_edits[item_attr] = []
                            lock_edits[item_attr].append(item.ratingKey)
                            item_edits += f"\nLock {name_display[item_attr]} (Batched)"
                        elif attribute not in ["lock", "unlock", "remove", "reset"]:
                            if tmdb_item and attribute == "tmdb":
                                found_rating = tmdb_item.vote_average
                            elif imdb_id and attribute == "imdb":
                                found_rating = self.config.IMDb.get_rating(imdb_id)
                            elif attribute == "trakt_user" and self.library.is_movie and tmdb_id in trakt_ratings:
                                found_rating = trakt_ratings[tmdb_id]
                            elif attribute == "trakt_user" and self.library.is_show and tvdb_id in trakt_ratings:
                                found_rating = trakt_ratings[tvdb_id]
                            elif omdb_item and attribute == "omdb":
                                found_rating = omdb_item.imdb_rating
                            elif mdb_item and attribute == "mdb":
                                found_rating = mdb_item.score / 10 if mdb_item.score else None
                            elif mdb_item and attribute == "mdb_average":
                                found_rating = mdb_item.average / 10 if mdb_item.average else None
                            elif mdb_item and attribute == "mdb_imdb":
                                found_rating = mdb_item.imdb_rating if mdb_item.imdb_rating else None
                            elif mdb_item and attribute == "mdb_metacritic":
                                found_rating = mdb_item.metacritic_rating / 10 if mdb_item.metacritic_rating else None
                            elif mdb_item and attribute == "mdb_metacriticuser":
                                found_rating = mdb_item.metacriticuser_rating if mdb_item.metacriticuser_rating else None
                            elif mdb_item and attribute == "mdb_trakt":
                                found_rating = mdb_item.trakt_rating / 10 if mdb_item.trakt_rating else None
                            elif mdb_item and attribute == "mdb_tomatoes":
                                found_rating = mdb_item.tomatoes_rating / 10 if mdb_item.tomatoes_rating else None
                            elif mdb_item and attribute == "mdb_tomatoesaudience":
                                found_rating = mdb_item.tomatoesaudience_rating / 10 if mdb_item.tomatoesaudience_rating else None
                            elif mdb_item and attribute == "mdb_tmdb":
                                found_rating = mdb_item.tmdb_rating / 10 if mdb_item.tmdb_rating else None
                            elif mdb_item and attribute == "mdb_letterboxd":
                                found_rating = mdb_item.letterboxd_rating * 2 if mdb_item.letterboxd_rating else None
                            elif mdb_item and attribute == "mdb_myanimelist":
                                found_rating = mdb_item.myanimelist_rating if mdb_item.myanimelist_rating else None
                            elif anidb_item and attribute == "anidb_rating":
                                found_rating = anidb_item.rating
                            elif anidb_item and attribute == "anidb_average":
                                found_rating = anidb_item.average
                            elif anidb_item and attribute == "anidb_score":
                                found_rating = anidb_item.score
                            elif mal_item and attribute == "mal":
                                found_rating = mal_item.score
                            else:
                                found_rating = None

                            if found_rating and float(found_rating) > 0:
                                found_rating = f"{float(found_rating):.1f}"
                                if str(current) != found_rating:
                                    if found_rating not in rating_edits[item_attr]:
                                        rating_edits[item_attr][found_rating] = []
                                    rating_edits[item_attr][found_rating].append(item.ratingKey)
                                    item_edits += f"\nUpdate {name_display[item_attr]} (Batched) | {found_rating}"
                            else:
                                logger.info(f"No {name_display[item_attr]} Found")

                if self.library.mass_genre_update or self.library.genre_mapper:
                    try:
                        new_genres = []
                        if self.library.mass_genre_update and self.library.mass_genre_update not in ["lock", "unlock", "remove", "reset"]:
                            if tmdb_item and self.library.mass_genre_update == "tmdb":
                                new_genres = tmdb_item.genres
                            elif imdb_id and self.library.mass_genre_update == "imdb" and imdb_id in self.config.IMDb.genres:
                                new_genres = self.config.IMDb.genres[imdb_id]
                            elif omdb_item and self.library.mass_genre_update == "omdb":
                                new_genres = omdb_item.genres
                            elif tvdb_item and self.library.mass_genre_update == "tvdb":
                                new_genres = tvdb_item.genres
                            elif anidb_item and self.library.mass_genre_update in anidb.weights:
                                logger.trace(anidb_item.main_title)
                                logger.trace(anidb_item.tags)
                                new_genres = [str(t).title() for t, w in anidb_item.tags.items() if w >= anidb.weights[self.library.mass_genre_update]]
                            elif mal_item and self.library.mass_genre_update == "mal":
                                new_genres = mal_item.genres
                            else:
                                raise Failed
                            if not new_genres:
                                logger.info("No Genres Found")
                        if self.library.genre_mapper or self.library.mass_genre_update in ["lock", "unlock"]:
                            if not new_genres and self.library.mass_genre_update not in ["remove", "reset"]:
                                new_genres = [g.tag for g in item.genres]
                            if self.library.genre_mapper:
                                mapped_genres = []
                                for genre in new_genres:
                                    if genre in self.library.genre_mapper:
                                        if self.library.genre_mapper[genre]:
                                            mapped_genres.append(self.library.genre_mapper[genre])
                                    else:
                                        mapped_genres.append(genre)
                                new_genres = mapped_genres
                        item_genres = [g.tag for g in item.genres]
                        _add = list(set(new_genres) - set(item_genres))
                        _remove = list(set(item_genres) - set(new_genres))
                        for genre_list, edit_type in [(_add, "add"), (_remove, "remove")]:
                            if genre_list:
                                for g in genre_list:
                                    if g not in genre_edits[edit_type]:
                                        genre_edits[edit_type][g] = []
                                    genre_edits[edit_type][g].append(item.ratingKey)
                                item_edits += f"\n{edit_type.capitalize()} Genres (Batched) | {', '.join(genre_list)}"
                        if self.library.mass_genre_update in ["unlock", "reset"] and ("genre" in locked_fields or _add or _remove):
                            if "genre" not in unlock_edits:
                                unlock_edits["genre"] = []
                            unlock_edits["genre"].append(item.ratingKey)
                            item_edits += "\nUnlock Genre (Batched)"
                        elif self.library.mass_genre_update in ["lock", "remove"] and "genre" not in locked_fields and not _add and not _remove:
                            if "genre" not in lock_edits:
                                lock_edits["genre"] = []
                            lock_edits["genre"].append(item.ratingKey)
                            item_edits += "\nLock Genre (Batched)"
                    except Failed:
                        pass

                if self.library.mass_content_rating_update or self.library.content_rating_mapper:
                    try:
                        new_rating = None
                        if self.library.mass_content_rating_update and self.library.mass_content_rating_update not in ["lock", "unlock", "remove", "reset"]:
                            if omdb_item and self.library.mass_content_rating_update == "omdb":
                                new_rating = omdb_item.content_rating
                            elif mdb_item and self.library.mass_content_rating_update == "mdb":
                                new_rating = mdb_item.content_rating if mdb_item.content_rating else None
                            elif mdb_item and self.library.mass_content_rating_update == "mdb_commonsense":
                                new_rating = mdb_item.commonsense if mdb_item.commonsense else None
                            elif mdb_item and self.library.mass_content_rating_update == "mdb_commonsense0":
                                new_rating = str(mdb_item.commonsense).rjust(2, "0") if mdb_item.commonsense else None
                            elif mal_item and self.library.mass_content_rating_update == "mal":
                                new_rating = mal_item.rating
                            else:
                                raise Failed
                            if new_rating is None:
                                logger.info("No Content Rating Found")
                            else:
                                new_rating = str(new_rating)

                        is_none = False
                        current_rating = item.contentRating
                        if not new_rating:
                            new_rating = current_rating
                        if self.library.content_rating_mapper:
                            if new_rating in self.library.content_rating_mapper:
                                new_rating = self.library.content_rating_mapper[new_rating]
                                if not new_rating:
                                    is_none = True
                        has_edit = False
                        if (is_none or self.library.mass_content_rating_update == "remove") and current_rating:
                            if "contentRating" not in remove_edits:
                                remove_edits["contentRating"] = []
                            remove_edits["contentRating"].append(item.ratingKey)
                            item_edits += "\nRemove Content Rating (Batched)"
                        elif self.library.mass_content_rating_update == "reset" and current_rating:
                            if "contentRating" not in reset_edits:
                                reset_edits["contentRating"] = []
                            reset_edits["contentRating"].append(item.ratingKey)
                            item_edits += "\nReset Content Rating (Batched)"
                        elif new_rating and new_rating != current_rating:
                            if new_rating not in content_edits:
                                content_edits[new_rating] = []
                            content_edits[new_rating].append(item.ratingKey)
                            item_edits += f"\nUpdate Content Rating (Batched) | {new_rating}"
                            has_edit = True

                        if self.library.mass_content_rating_update in ["unlock", "reset"] and ("contentRating" in locked_fields or has_edit):
                            if "contentRating" not in unlock_edits:
                                unlock_edits["contentRating"] = []
                            unlock_edits["contentRating"].append(item.ratingKey)
                            item_edits += "\nUnlock Content Rating (Batched)"
                        elif self.library.mass_content_rating_update in ["lock", "remove"] and "contentRating" not in locked_fields and not has_edit:
                            if "contentRating" not in lock_edits:
                                lock_edits["contentRating"] = []
                            lock_edits["contentRating"].append(item.ratingKey)
                            item_edits += "\nLock Content Rating (Batched)"
                    except Failed:
                        pass

                if self.library.mass_original_title_update:
                    current_original = item.originalTitle
                    has_edit = False
                    if self.library.mass_original_title_update == "remove" and current_original:
                        if "originalTitle" not in remove_edits:
                            remove_edits["originalTitle"] = []
                        remove_edits["originalTitle"].append(item.ratingKey)
                        item_edits += "\nRemove Original Title (Batched)"
                    elif self.library.mass_original_title_update == "reset" and current_original:
                        if "originalTitle" not in reset_edits:
                            reset_edits["originalTitle"] = []
                        reset_edits["originalTitle"].append(item.ratingKey)
                        item_edits += "\nReset Original Title (Batched)"
                    elif self.library.mass_original_title_update not in ["lock", "unlock", "remove", "reset"]:
                        try:
                            if anidb_item and self.library.mass_original_title_update == "anidb":
                                new_original_title = anidb_item.main_title
                            elif anidb_item and self.library.mass_original_title_update == "anidb_official":
                                new_original_title = anidb_item.official_title
                            elif mal_item and self.library.mass_original_title_update == "mal":
                                new_original_title = mal_item.title
                            elif mal_item and self.library.mass_original_title_update == "mal_english":
                                new_original_title = mal_item.title_english
                            elif mal_item and self.library.mass_original_title_update == "mal_japanese":
                                new_original_title = mal_item.title_japanese
                            else:
                                raise Failed
                            if not new_original_title:
                                logger.info("No Original Title Found")
                            elif str(current_original) != str(new_original_title):
                                item.editOriginalTitle(new_original_title)
                                item_edits += f"\nUpdated Original Title | {new_original_title}"
                                has_edit = True
                        except Failed:
                            pass
                    if self.library.mass_original_title_update in ["unlock", "reset"] and ("originalTitle" in locked_fields or has_edit):
                        if "originalTitle" not in unlock_edits:
                            unlock_edits["originalTitle"] = []
                        unlock_edits["originalTitle"].append(item.ratingKey)
                        item_edits += "\nUnlock Original Title (Batched)"
                    elif self.library.mass_original_title_update in ["lock", "remove"] and "originalTitle" not in locked_fields and not has_edit:
                        if "originalTitle" not in lock_edits:
                            lock_edits["originalTitle"] = []
                        lock_edits["originalTitle"].append(item.ratingKey)
                        item_edits += "\nLock Original Title (Batched)"

                if self.library.mass_studio_update:
                    current_studio = item.studio
                    has_edit = False
                    if self.library.mass_studio_update == "remove" and current_studio:
                        if "studio" not in remove_edits:
                            remove_edits["studio"] = []
                        remove_edits["studio"].append(item.ratingKey)
                        item_edits += "\nRemove Studio (Batched)"
                    elif self.library.mass_studio_update == "reset" and current_studio:
                        if "studio" not in reset_edits:
                            reset_edits["studio"] = []
                        reset_edits["studio"].append(item.ratingKey)
                        item_edits += "\nReset Studio (Batched)"
                    elif self.library.mass_studio_update not in ["lock", "unlock", "remove", "reset"]:
                        try:
                            if anidb_item and self.library.mass_studio_update == "anidb":
                                new_studio = anidb_item.studio
                            elif mal_item and self.library.mass_studio_update == "mal":
                                new_studio = mal_item.studio
                            elif tmdb_item and self.library.mass_studio_update == "tmdb":
                                new_studio = tmdb_item.studio
                            else:
                                raise Failed
                            if not new_studio:
                                logger.info("No Studio Found")
                            elif str(current_studio) != str(new_studio):
                                if new_studio not in studio_edits:
                                    studio_edits[new_studio] = []
                                studio_edits[new_studio].append(item.ratingKey)
                                item_edits += f"\nUpdate Studio (Batched) | {new_studio}"
                                has_edit = True
                        except Failed:
                            pass

                    if self.library.mass_studio_update in ["unlock", "reset"] and ("studio" in locked_fields or has_edit):
                        if "studio" not in unlock_edits:
                            unlock_edits["studio"] = []
                        unlock_edits["studio"].append(item.ratingKey)
                        item_edits += "\nUnlock Studio (Batched)"
                    elif self.library.mass_studio_update in ["lock", "remove"] and "studio" not in locked_fields and not has_edit:
                        if "studio" not in lock_edits:
                            lock_edits["studio"] = []
                        lock_edits["studio"].append(item.ratingKey)
                        item_edits += "\nLock Studio (Batched)"

                if self.library.mass_originally_available_update:
                    current_available = item.originallyAvailableAt
                    if current_available:
                        current_available = current_available.strftime("%Y-%m-%d")
                    has_edit = False
                    if self.library.mass_originally_available_update == "remove" and current_available:
                        if "originallyAvailableAt" not in remove_edits:
                            remove_edits["originallyAvailableAt"] = []
                        remove_edits["originallyAvailableAt"].append(item.ratingKey)
                        item_edits += "\nRemove Originally Available Date (Batched)"
                    elif self.library.mass_originally_available_update == "reset" and current_available:
                        if "originallyAvailableAt" not in reset_edits:
                            reset_edits["originallyAvailableAt"] = []
                        reset_edits["originallyAvailableAt"].append(item.ratingKey)
                        item_edits += "\nReset Originally Available Date (Batched)"
                    elif self.library.mass_originally_available_update not in ["lock", "unlock", "remove", "reset"]:
                        try:
                            if omdb_item and self.library.mass_originally_available_update == "omdb":
                                new_available = omdb_item.released
                            elif mdb_item and self.library.mass_originally_available_update == "mdb":
                                new_available = mdb_item.released
                            elif tvdb_item and self.library.mass_originally_available_update == "tvdb":
                                new_available = tvdb_item.release_date
                            elif tmdb_item and self.library.mass_originally_available_update == "tmdb":
                                new_available = tmdb_item.release_date if self.library.is_movie else tmdb_item.first_air_date
                            elif anidb_item and self.library.mass_originally_available_update == "anidb":
                                new_available = anidb_item.released
                            elif mal_item and self.library.mass_originally_available_update == "mal":
                                new_available = mal_item.aired
                            else:
                                raise Failed
                            if new_available:
                                new_available = new_available.strftime("%Y-%m-%d")
                                if current_available != new_available:
                                    if new_available not in available_edits:
                                        available_edits[new_available] = []
                                    available_edits[new_available].append(item.ratingKey)
                                    item_edits += f"\nUpdate Originally Available Date (Batched) | {new_available}"
                                    has_edit = True
                            else:
                                logger.info("No Originally Available Date Found")
                        except Failed:
                            pass

                    if self.library.mass_originally_available_update in ["unlock", "reset"] and ("originallyAvailableAt" in locked_fields or has_edit):
                        if "originallyAvailableAt" not in unlock_edits:
                            unlock_edits["originallyAvailableAt"] = []
                        unlock_edits["originallyAvailableAt"].append(item.ratingKey)
                        item_edits += "\nUnlock Originally Available Date (Batched)"
                    elif self.library.mass_originally_available_update in ["lock", "remove"] and "originallyAvailableAt" not in locked_fields and not has_edit:
                        if "originallyAvailableAt" not in lock_edits:
                            lock_edits["originallyAvailableAt"] = []
                        lock_edits["originallyAvailableAt"].append(item.ratingKey)
                        item_edits += "\nLock Originally Available Date (Batched)"

                if len(item_edits) > 0:
                    logger.info(f"Item Edits{item_edits}")
                else:
                    logger.info("No Item Edits")

                if self.library.mass_poster_update or self.library.mass_background_update:
                    try:
                        new_poster, new_background, item_dir, name = self.library.find_item_assets(item)
                    except Failed:
                        item_dir = None
                        name = None
                        new_poster = None
                        new_background = None
                    if self.library.mass_poster_update:
                        self.library.poster_update(item, new_poster, tmdb=tmdb_item.poster_url if tmdb_item else None, title=item.title)
                    if self.library.mass_background_update:
                        self.library.background_update(item, new_background, tmdb=tmdb_item.backdrop_url if tmdb_item else None, title=item.title)

                    if self.library.is_show and (
                            (self.library.mass_poster_update and
                                (self.library.mass_poster_update["seasons"] or self.library.mass_poster_update["episodes"])) or
                            (self.library.mass_background_update and
                                (self.library.mass_background_update["seasons"] or self.library.mass_background_update["episodes"]))
                    ):
                        real_show = None
                        try:
                            real_show = tmdb_item.load_show() if tmdb_item else None
                        except Failed as e:
                            logger.error(e)
                        tmdb_seasons = {s.season_number: s for s in real_show.seasons} if real_show else {}
                        for season in self.library.query(item.seasons):
                            if (self.library.mass_poster_update and self.library.mass_poster_update["seasons"]) or \
                                    (self.library.mass_background_update and self.library.mass_background_update["seasons"]):
                                try:
                                    season_poster, season_background, _, _ = self.library.find_item_assets(season, item_asset_directory=item_dir, folder_name=name)
                                except Failed:
                                    season_poster = None
                                    season_background = None
                                season_title = f"S{season.seasonNumber} {season.title}"
                                tmdb_poster = tmdb_seasons[season.seasonNumber].poster_url if season.seasonNumber in tmdb_seasons else None
                                if self.library.mass_poster_update and self.library.mass_poster_update["seasons"]:
                                    self.library.poster_update(season, season_poster, tmdb=tmdb_poster, title=season_title if season else None)
                                if self.library.mass_background_update and self.library.mass_background_update["seasons"]:
                                    self.library.background_update(season, season_background, title=season_title if season else None)

                            if (self.library.mass_poster_update and self.library.mass_poster_update["episodes"]) or \
                                    (self.library.mass_background_update and self.library.mass_background_update["episodes"]):
                                tmdb_episodes = {}
                                if season.seasonNumber in tmdb_seasons:
                                    for episode in tmdb_seasons[season.seasonNumber].episodes:
                                        episode._partial = False
                                        try:
                                            tmdb_episodes[episode.episode_number] = episode
                                        except NotFound:
                                            logger.error(f"TMDb Error: An Episode of Season {season.seasonNumber} was Not Found")

                                for episode in self.library.query(season.episodes):
                                    try:
                                        episode_poster, episode_background, _, _ = self.library.find_item_assets(episode, item_asset_directory=item_dir, folder_name=name)
                                    except Failed:
                                        episode_poster = None
                                        episode_background = None
                                    episode_title = f"S{season.seasonNumber}E{episode.episodeNumber} {episode.title}"
                                    tmdb_poster = tmdb_episodes[episode.episodeNumber].still_url if episode.episodeNumber in tmdb_episodes else None
                                    if self.library.mass_poster_update and self.library.mass_poster_update["episodes"]:
                                        self.library.poster_update(episode, episode_poster, tmdb=tmdb_poster, title=episode_title if episode else None)
                                    if self.library.mass_background_update and self.library.mass_background_update["episodes"]:
                                        self.library.background_update(episode, episode_background, title=episode_title if episode else None)

                episode_ops = [
                    (self.library.mass_episode_audience_rating_update, "audienceRating"),
                    (self.library.mass_episode_critic_rating_update, "rating"),
                    (self.library.mass_episode_user_rating_update, "userRating")
                ]

                if any([x is not None for x, _ in episode_ops]):

                    if any([x == "imdb" for x, _ in episode_ops]) and not imdb_id:
                        logger.info(f"No IMDb ID for Guid: {item.guid}")

                    for ep in item.episodes():
                        ep = self.library.reload(ep)
                        item_title = self.library.get_item_sort_title(ep, atr="title")
                        logger.info("")
                        logger.info(f"Processing {item_title}")
                        episode_locked_fields = [f.name for f in ep.fields if f.locked]

                        for attribute, item_attr in episode_ops:
                            if attribute:
                                current = getattr(ep, item_attr)
                                if attribute == "remove" and current is not None:
                                    if item_attr not in ep_remove_edits:
                                        ep_remove_edits[item_attr] = []
                                    ep_remove_edits[item_attr].append(ep)
                                    item_edits += f"\nRemove {name_display[item_attr]} (Batched)"
                                elif attribute == "reset" and current is not None:
                                    if item_attr not in ep_reset_edits:
                                        ep_reset_edits[item_attr] = []
                                    ep_reset_edits[item_attr].append(ep)
                                    item_edits += f"\nReset {name_display[item_attr]} (Batched)"
                                elif attribute in ["unlock", "reset"] and item_attr in episode_locked_fields:
                                    if item_attr not in ep_unlock_edits:
                                        ep_unlock_edits[item_attr] = []
                                    ep_unlock_edits[item_attr].append(ep)
                                    item_edits += f"\nUnlock {name_display[item_attr]} (Batched)"
                                elif attribute in ["lock", "remove"] and item_attr not in episode_locked_fields:
                                    if item_attr not in ep_lock_edits:
                                        ep_lock_edits[item_attr] = []
                                    ep_lock_edits[item_attr].append(ep)
                                    item_edits += f"\nLock {name_display[item_attr]} (Batched)"
                                elif attribute not in ["lock", "unlock", "remove", "reset"]:
                                    found_rating = None
                                    if tmdb_item and attribute == "tmdb":
                                        try:
                                            found_rating = self.config.TMDb.get_episode(tmdb_item.tmdb_id, ep.seasonNumber, ep.episodeNumber).vote_average
                                        except Failed as er:
                                            logger.error(er)
                                    elif imdb_id and attribute == "imdb":
                                        found_rating = self.config.IMDb.get_episode_rating(imdb_id, ep.seasonNumber, ep.episodeNumber)

                                    if found_rating and float(found_rating) > 0:
                                        found_rating = f"{float(found_rating):.1f}"
                                        if str(current) != found_rating:
                                            if found_rating not in ep_rating_edits[item_attr]:
                                                ep_rating_edits[item_attr][found_rating] = []
                                            ep_rating_edits[item_attr][found_rating].append(ep)
                                            item_edits += f"\nUpdate {name_display[item_attr]} (Batched) | {found_rating}"
                                    else:
                                        logger.info(f"No {name_display[item_attr]} Found")

                        if len(item_edits) > 0:
                            logger.info(f"Item Edits:{item_edits}")

            logger.info("")
            logger.separator("Batch Updates", space=False, border=False)
            logger.info("")

            def get_batch_info(placement, total, display_attr, total_count, display_value=None, is_episode=False, out_type=None, tag_type=None):
                return f"Batch {name_display[display_attr] if display_attr in name_display else display_attr.capitalize()} Update ({placement}/{total}): " \
                       f"{f'{out_type.capitalize()}ing ' if out_type else ''}" \
                       f"{f'Adding {display_value} to ' if tag_type == 'add' else f'Removing {display_value} from ' if tag_type == 'remove' else ''}" \
                       f"{total_count} {'Episode' if is_episode else 'Movie' if self.library.is_movie else 'Show'}" \
                       f"{'s' if total_count > 1 else ''}{'' if out_type or tag_type else f' updated to {display_value}'}"

            for tag_attribute, edit_dict in [("Label", label_edits), ("Genre", genre_edits)]:
                for edit_type, batch_edits in edit_dict.items():
                    _size = len(batch_edits.items())
                    for i, (tag_name, rating_keys) in enumerate(sorted(batch_edits.items()), 1):
                        logger.info(get_batch_info(i, _size, tag_attribute, len(rating_keys), display_value=tag_name, tag_type=edit_type))
                        self.library.Plex.batchMultiEdits(self.library.load_list_from_cache(rating_keys))
                        getattr(self.library.Plex, f"{edit_type}{tag_attribute}")(tag_name)
                        self.library.Plex.saveMultiEdits()

            for item_attr, _edits in rating_edits.items():
                _size = len(rating_edits.items())
                for i, (new_rating, rating_keys) in enumerate(sorted(_edits.items()), 1):
                    logger.info(get_batch_info(i, _size, item_attr, len(rating_keys), display_value=new_rating))
                    self.library.Plex.batchMultiEdits(self.library.load_list_from_cache(rating_keys))
                    self.library.Plex.editField(item_attr, new_rating)
                    self.library.Plex.saveMultiEdits()

            _size = len(content_edits.items())
            for i, (new_rating, rating_keys) in enumerate(sorted(content_edits.items()), 1):
                logger.info(get_batch_info(i, _size, "contentRating", len(rating_keys), display_value=new_rating))
                self.library.Plex.batchMultiEdits(self.library.load_list_from_cache(rating_keys))
                self.library.Plex.editContentRating(new_rating)
                self.library.Plex.saveMultiEdits()

            _size = len(studio_edits.items())
            for i, (new_studio, rating_keys) in enumerate(sorted(studio_edits.items()), 1):
                logger.info(get_batch_info(i, _size, "studio", len(rating_keys), display_value=new_studio))
                self.library.Plex.batchMultiEdits(self.library.load_list_from_cache(rating_keys))
                self.library.Plex.editStudio(new_studio)
                self.library.Plex.saveMultiEdits()

            _size = len(available_edits.items())
            for i, (new_available, rating_keys) in enumerate(sorted(available_edits.items()), 1):
                logger.info(get_batch_info(i, _size, "originallyAvailableAt", len(rating_keys), display_value=new_available))
                self.library.Plex.batchMultiEdits(self.library.load_list_from_cache(rating_keys))
                self.library.Plex.editOriginallyAvailable(new_available)
                self.library.Plex.saveMultiEdits()

            _size = len(remove_edits.items())
            for i, (field_attr, rating_keys) in enumerate(remove_edits.items(), 1):
                logger.info(get_batch_info(i, _size, field_attr, len(rating_keys), out_type="remov"))
                self.library.Plex.batchMultiEdits(self.library.load_list_from_cache(rating_keys))
                self.library.Plex.editField(field_attr, None, locked=True)
                self.library.Plex.saveMultiEdits()

            _size = len(reset_edits.items())
            for i, (field_attr, rating_keys) in enumerate(reset_edits.items(), 1):
                logger.info(get_batch_info(i, _size, field_attr, len(rating_keys), out_type="reset"))
                self.library.Plex.batchMultiEdits(self.library.load_list_from_cache(rating_keys))
                self.library.Plex.editField(field_attr, None, locked=False)
                self.library.Plex.saveMultiEdits()

            _size = len(lock_edits.items())
            for i, (field_attr, rating_keys) in enumerate(lock_edits.items(), 1):
                logger.info(get_batch_info(i, _size, field_attr, len(rating_keys), out_type="lock"))
                self.library.Plex.batchMultiEdits(self.library.load_list_from_cache(rating_keys))
                self.library.Plex._edit(**{f"{field_attr}.locked": 1})
                self.library.Plex.saveMultiEdits()

            _size = len(unlock_edits.items())
            for i, (field_attr, rating_keys) in enumerate(unlock_edits.items(), 1):
                logger.info(get_batch_info(i, _size, field_attr, len(rating_keys), out_type="unlock"))
                self.library.Plex.batchMultiEdits(self.library.load_list_from_cache(rating_keys))
                self.library.Plex._edit(**{f"{field_attr}.locked": 0})
                self.library.Plex.saveMultiEdits()

            for item_attr, _edits in ep_rating_edits.items():
                _size = len(_edits.items())
                for i, (new_rating, rating_keys) in enumerate(sorted(_edits.items()), 1):
                    logger.info(get_batch_info(i, _size, item_attr, len(rating_keys), display_value=new_rating, is_episode=True))
                    self.library.Plex.batchMultiEdits(rating_keys)
                    self.library.Plex.editField(item_attr, new_rating)
                    self.library.Plex.saveMultiEdits()

            _size = len(ep_remove_edits.items())
            for i, (field_attr, rating_keys) in enumerate(ep_remove_edits.items(), 1):
                logger.info(get_batch_info(i, _size, field_attr, len(rating_keys), is_episode=True, out_type="remov"))
                self.library.Plex.batchMultiEdits(rating_keys)
                self.library.Plex.editField(field_attr, None, locked=True)
                self.library.Plex.saveMultiEdits()

            _size = len(ep_reset_edits.items())
            for i, (field_attr, rating_keys) in enumerate(ep_reset_edits.items(), 1):
                logger.info(get_batch_info(i, _size, field_attr, len(rating_keys), is_episode=True, out_type="reset"))
                self.library.Plex.batchMultiEdits(rating_keys)
                self.library.Plex.editField(field_attr, None, locked=False)
                self.library.Plex.saveMultiEdits()

            _size = len(ep_lock_edits.items())
            for i, (field_attr, rating_keys) in enumerate(ep_lock_edits.items(), 1):
                logger.info(get_batch_info(i, _size, field_attr, len(rating_keys), is_episode=True, out_type="lock"))
                self.library.Plex.batchMultiEdits(rating_keys)
                self.library.Plex._edit(**{f"{field_attr}.locked": 1})
                self.library.Plex.saveMultiEdits()

            _size = len(ep_unlock_edits.items())
            for i, (field_attr, rating_keys) in enumerate(ep_unlock_edits.items(), 1):
                logger.info(get_batch_info(i, _size, field_attr, len(rating_keys), is_episode=True, out_type="unlock"))
                self.library.Plex.batchMultiEdits(rating_keys)
                self.library.Plex._edit(**{f"{field_attr}.locked": 0})
                self.library.Plex.saveMultiEdits()

            if self.library.Radarr and self.library.radarr_add_all_existing:
                logger.info("")
                logger.separator(f"Radarr Add All Existing: {len(radarr_adds)} Movies", space=False, border=False)
                logger.info("")
                try:
                    self.library.Radarr.add_tmdb(radarr_adds)
                except Failed as e:
                    logger.error(e)

            if self.library.Sonarr and self.library.sonarr_add_all_existing:
                logger.info("")
                logger.separator(f"Sonarr Add All Existing: {len(sonarr_adds)} Shows", space=False, border=False)
                logger.info("")
                try:
                    self.library.Sonarr.add_tvdb(sonarr_adds)
                except Failed as e:
                    logger.error(e)

        if self.library.radarr_remove_by_tag:
            logger.info("")
            logger.separator(f"Radarr Remove {len(self.library.radarr_remove_by_tag)} Movies with Tags: {', '.join(self.library.radarr_remove_by_tag)}", space=False, border=False)
            logger.info("")
            self.library.Radarr.remove_all_with_tags(self.library.radarr_remove_by_tag)
        if self.library.sonarr_remove_by_tag:
            logger.info("")
            logger.separator(f"Sonarr Remove {len(self.library.sonarr_remove_by_tag)} Shows with Tags: {', '.join(self.library.sonarr_remove_by_tag)}", space=False, border=False)
            logger.info("")
            self.library.Sonarr.remove_all_with_tags(self.library.sonarr_remove_by_tag)

        if self.library.delete_collections or self.library.show_unmanaged or self.library.show_unconfigured or self.library.assets_for_all or self.library.mass_collection_mode:
            logger.info("")
            logger.separator("Collection Operations", space=False, border=False)
            logger.info("")

            if self.library.delete_collections:
                logger.info("")
                logger.separator("Deleting Collections", space=False, border=False)
                logger.info("")

            less = self.library.delete_collections["less"] if self.library.delete_collections and self.library.delete_collections["less"] is not None else None
            managed = self.library.delete_collections["managed"] if self.library.delete_collections else None
            configured = self.library.delete_collections["configured"] if self.library.delete_collections else None
            unmanaged_collections = []
            unconfigured_collections = []
            all_collections = self.library.get_all_collections()
            for i, col in enumerate(all_collections, 1):
                logger.ghost(f"Reading Collection: {i}/{len(all_collections)} {col.title}")
                labels = [la.tag for la in self.library.item_labels(col)]
                if (less is not None or managed is not None or configured is not None) \
                        and (less is None or col.childCount < less) \
                        and (managed is None
                             or (managed is True and "PMM" in labels)
                             or (managed is False and "PMM" not in labels)) \
                        and (configured is None
                             or (configured is True and col.title in self.library.collections)
                             or (configured is False and col.title not in self.library.collections)):
                    try:
                        self.library.delete(col)
                        logger.info(f"{col.title} Deleted")
                    except Failed as e:
                        logger.error(e)
                else:
                    if "PMM" not in labels:
                        unmanaged_collections.append(col)
                    if col.title not in self.library.collection_names:
                        unconfigured_collections.append(col)

            if self.library.show_unmanaged and len(unmanaged_collections) > 0:
                logger.info("")
                logger.separator(f"Unmanaged Collections in {self.library.name} Library", space=False, border=False)
                logger.info("")
                for col in unmanaged_collections:
                    logger.info(col.title)
                logger.info("")
                logger.info(f"{len(unmanaged_collections)} Unmanaged Collection{'s' if len(unmanaged_collections) > 1 else ''}")
            elif self.library.show_unmanaged:
                logger.info("")
                logger.separator(f"No Unmanaged Collections in {self.library.name} Library", space=False, border=False)
                logger.info("")

            if self.library.show_unconfigured and len(unconfigured_collections) > 0:
                logger.info("")
                logger.separator(f"Unconfigured Collections in {self.library.name} Library", space=False, border=False)
                logger.info("")
                for col in unconfigured_collections:
                    logger.info(col.title)
                logger.info("")
                logger.info(f"{len(unconfigured_collections)} Unconfigured Collection{'s' if len(unconfigured_collections) > 1 else ''}")
            elif self.library.show_unconfigured:
                logger.info("")
                logger.separator(f"No Unconfigured Collections in {self.library.name} Library", space=False, border=False)
                logger.info("")

            if self.library.assets_for_all_collections and len(unconfigured_collections) > 0:
                logger.info("")
                logger.separator(f"Unconfigured Collection Assets Check for {self.library.name} Library", space=False, border=False)
                logger.info("")
                for col in unconfigured_collections:
                    try:
                        poster, background, item_dir, name = self.library.find_item_assets(col)
                        if poster or background:
                            self.library.upload_images(col, poster=poster, background=background)
                        elif self.library.show_missing_assets:
                            logger.warning(f"Asset Warning: No poster or background found in an assets folder for '{name}'")
                    except Failed as e:
                        logger.warning(e)

            if self.library.mass_collection_mode:
                logger.info("")
                logger.separator(f"Unconfigured Mass Collection Mode to {self.library.mass_collection_mode} for {self.library.name} Library", space=False, border=False)
                logger.info("")
                for col in unconfigured_collections:
                    if int(col.collectionMode) not in plex.collection_mode_keys \
                            or plex.collection_mode_keys[int(col.collectionMode)] != self.library.mass_collection_mode:
                        self.library.collection_mode_query(col, self.library.mass_collection_mode)
                        logger.info(f"{col.title} Collection Mode Updated")

        if self.library.metadata_backup:
            logger.info("")
            logger.separator(f"Metadata Backup for {self.library.name} Library", space=False, border=False)
            logger.info("")
            logger.info(f"Metadata Backup Path: {self.library.metadata_backup['path']}")
            logger.info("")
            yaml = None
            if os.path.exists(self.library.metadata_backup["path"]):
                try:
                    yaml = YAML(path=self.library.metadata_backup["path"])
                except Failed as e:
                    logger.error(e)
                    filename, file_extension = os.path.splitext(self.library.metadata_backup["path"])
                    i = 1
                    while os.path.exists(f"{filename}{i}{file_extension}"):
                        i += 1
                    os.rename(self.library.metadata_backup["path"], f"{filename}{i}{file_extension}")
                    logger.error(f"Backup failed to load saving copy to {filename}{i}{file_extension}")
            if not yaml:
                yaml = YAML(path=self.library.metadata_backup["path"], create=True)
            if "metadata" not in yaml.data or not isinstance(yaml.data["metadata"], dict):
                yaml.data["metadata"] = {}
            special_names = {}
            for mk, mv in yaml.data["metadata"].items():
                if mv and "title" in mv:
                    special_names[mv["title"]] = mk
                    if "year" in mv:
                        special_names[f"{mv['title']} ({mv['year']})"] = mk
            items = self.library.get_all(load=True)
            titles = [i.title for i in items]
            for i, item in enumerate(items, 1):
                logger.ghost(f"Processing: {i}/{len(items)} {item.title}")
                map_key, attrs = self.library.get_locked_attributes(item, titles)
                if map_key in special_names:
                    map_key = special_names[map_key]
                og_dict = yaml.data["metadata"][map_key] if map_key in yaml.data["metadata"] and yaml.data["metadata"][map_key] and isinstance(yaml.data["metadata"][map_key], dict) else {}
                if attrs or (self.library.metadata_backup["add_blank_entries"] and not og_dict):

                    def loop_dict(looping, dest_dict):
                        if not looping:
                            return None
                        for lk, lv in looping.items():
                            if isinstance(lv, dict) and lk in dest_dict and dest_dict[lk] and isinstance(dest_dict[lk], dict):
                                dest_dict[lk] = loop_dict(lv, dest_dict[lk])
                            else:
                                dest_dict[lk] = lv
                        return dest_dict

                    yaml.data["metadata"][map_key] = loop_dict(attrs, og_dict)
            logger.exorcise()
            yaml.save()
            logger.info(f"{len(yaml.data['metadata'])} {self.library.type}{'s' if len(yaml.data['metadata']) > 1 else ''} Backed Up")

        operation_run_time = str(datetime.now() - operation_start).split('.')[0]
        logger.info("")
        logger.separator(f"Finished {self.library.name} Library Operations\nOperations Run Time: {operation_run_time}")
        return operation_run_time
