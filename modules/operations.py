import os, re
from datetime import datetime
from modules import plex, util
from modules.util import Failed, LimitReached, YAML

logger = util.logger

meta_operations = [
    "mass_audience_rating_update", "mass_user_rating_update", "mass_critic_rating_update",
    "mass_episode_audience_rating_update", "mass_episode_user_rating_update", "mass_episode_critic_rating_update",
    "mass_genre_update", "mass_content_rating_update", "mass_originally_available_update", "mass_original_title_update",
    "mass_poster_update", "mass_background_update"
]

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
                try:
                    item = self.library.reload(item)
                except Failed as e:
                    logger.error(e)
                    continue
                logger.info("")
                logger.info(f"Processing: {i}/{len(items)} {item.title}")
                current_labels = [la.tag for la in self.library.item_labels(item)] if self.library.assets_for_all or self.library.mass_imdb_parental_labels else []

                if self.library.assets_for_all and self.library.asset_directory:
                    self.library.find_and_upload_assets(item, current_labels)

                locked_fields = [f.name for f in item.fields if f.locked]

                tmdb_id, tvdb_id, imdb_id = self.library.get_ids(item)

                item.batchEdits()
                batch_display = ""

                if self.library.remove_title_parentheses:
                    if not any([f.name == "title" and f.locked for f in item.fields]) and item.title.endswith(")"):
                        new_title = re.sub(" \\(\\w+\\)$", "", item.title)
                        item.editTitle(new_title)
                        batch_display += f"\n{item.title[:25]:<25} | Title | {new_title}"

                if self.library.mass_imdb_parental_labels:
                    try:
                        parental_guide = self.config.IMDb.parental_guide(imdb_id)
                        parental_labels = [f"{k.capitalize()}:{v}" for k, v in parental_guide.items() if self.library.mass_imdb_parental_labels == "with_none" or v != "None"]
                        add_labels = [la for la in parental_labels if la not in current_labels]
                        remove_labels = [la for la in current_labels if la in util.parental_labels and la not in parental_labels]
                        if add_labels or remove_labels:
                            batch_display += f"\n{self.library.edit_tags('label', item, add_tags=add_labels, remove_tags=remove_labels, do_print=False)}"
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
                    tmdb_item = self.config.TMDb.get_item(item, tmdb_id, tvdb_id, imdb_id, is_movie=self.library.is_movie)

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
                        elif not anidb_id or anidb_id not in self.config.Convert._anidb_to_mal:
                            logger.warning(f"No AniDB ID to Convert to MyAnimeList ID for Guid: {item.guid}")
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
                                logger.warning(f"No MdbItem for Guid: {item.guid}")
                        except LimitReached as e:
                            logger.debug(e)

                def update_rating(attribute, item_attr, display):
                    current = getattr(item, item_attr)
                    if attribute in ["remove", "reset"] and current is not None:
                        item.editField(item_attr, None, locked=attribute == "remove")
                        return f"\n{display} | None"
                    elif attribute in ["unlock", "reset"] and item_attr in locked_fields:
                        self.library.edit_query(item, {f"{item_attr}.locked": 0})
                        return f"\n{display} | Unlocked"
                    elif attribute in ["lock", "remove"] and item_attr not in locked_fields:
                        self.library.edit_query(item, {f"{item_attr}.locked": 1})
                        return f"\n{display} | Locked"
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

                        if found_rating is None:
                            logger.info(f"No {display} Found")
                        elif str(current) != str(found_rating):
                            item.editField(item_attr, found_rating)
                            return f"\n{display} | {found_rating}"
                    return ""

                if self.library.mass_audience_rating_update:
                    batch_display += update_rating(self.library.mass_audience_rating_update, "audienceRating", "Audience Rating")

                if self.library.mass_critic_rating_update:
                    batch_display += update_rating(self.library.mass_critic_rating_update, "rating", "Critic Rating")

                if self.library.mass_user_rating_update:
                    batch_display += update_rating(self.library.mass_user_rating_update, "userRating", "User Rating")

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
                            elif anidb_item and self.library.mass_genre_update == "anidb":
                                new_genres = [str(t).title() for t in anidb_item.tags]
                            elif mal_item and self.library.mass_genre_update == "mal":
                                new_genres = mal_item.genres
                            else:
                                raise Failed
                            if not new_genres:
                                logger.info(f"No Genres Found")
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
                        temp_display = self.library.edit_tags("genre", item, sync_tags=new_genres, do_print=False,
                                                              locked=False if self.library.mass_genre_update in ["unlock", "reset"] else True,
                                                              is_locked="genre" in locked_fields)
                        if temp_display:
                            batch_display += f"\n{temp_display}"
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
                            if not new_rating:
                                logger.info(f"No Content Rating Found")

                        is_none = False
                        if self.library.content_rating_mapper or self.library.mass_content_rating_update in ["lock", "unlock"]:
                            if not new_rating and self.library.mass_content_rating_update not in ["remove", "reset"]:
                                new_rating = item.contentRating
                            if self.library.content_rating_mapper and new_rating in self.library.content_rating_mapper:
                                new_rating = self.library.content_rating_mapper[new_rating]
                                if not new_rating:
                                    is_none = True
                        if (is_none or self.library.mass_content_rating_update in ["remove", "reset"]) and item.contentRating:
                            item.editField("contentRating", None, locked=self.library.mass_content_rating_update == "remove")
                            batch_display += f"\nContent Rating | None"
                        elif not new_rating and self.library.mass_content_rating_update not in ["lock", "unlock", "remove", "reset"]:
                            logger.info(f"No Content Rating Found")
                        elif str(item.contentRating) != str(new_rating):
                            item.editContentRating(new_rating)
                            batch_display += f"\nContent Rating | {new_rating}"
                        elif self.library.mass_content_rating_update in ["unlock", "reset"] and "contentRating" in locked_fields:
                            self.library.edit_query(item, {"contentRating.locked": 0})
                            batch_display += f"\nContent Rating | Unlocked"
                        elif self.library.mass_content_rating_update in ["lock", "remove"] and "contentRating" not in locked_fields:
                            self.library.edit_query(item, {"contentRating.locked": 1})
                            batch_display += f"\nContent Rating | Locked"
                    except Failed:
                        pass

                if self.library.mass_original_title_update:
                    if self.library.mass_original_title_update in ["remove", "reset"] and item.originalTitle:
                        item.editField("originalTitle", None, locked=self.library.mass_original_title_update == "remove")
                        batch_display += f"\nOriginal Title | None"
                    elif self.library.mass_original_title_update in ["unlock", "reset"] and "originalTitle" in locked_fields:
                        self.library.edit_query(item, {"originalTitle.locked": 0})
                        batch_display += f"\nOriginal Title | Unlocked"
                    elif self.library.mass_original_title_update in ["lock", "remove"] and "originalTitle" not in locked_fields:
                        self.library.edit_query(item, {"originalTitle.locked": 1})
                        batch_display += f"\nOriginal Title | Locked"
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
                                logger.info(f"No Original Title Found")
                            elif str(item.originalTitle) != str(new_original_title):
                                item.editOriginalTitle(new_original_title)
                                batch_display += f"\nOriginal Title | {new_original_title}"
                        except Failed:
                            pass

                if self.library.mass_originally_available_update:
                    if self.library.mass_originally_available_update in ["remove", "reset"] and item.originallyAvailableAt:
                        item.editField("originallyAvailableAt", None, locked=self.library.mass_originally_available_update == "remove")
                        batch_display += f"\nOriginally Available Date | None"
                    elif self.library.mass_originally_available_update in ["unlock", "reset"] and "originallyAvailableAt" in locked_fields:
                        self.library.edit_query(item, {"originallyAvailableAt.locked": 0})
                        batch_display += f"\nOriginally Available Date | Unlocked"
                    elif self.library.mass_originally_available_update in ["lock", "remove"] and "originallyAvailableAt" not in locked_fields:
                        self.library.edit_query(item, {"originallyAvailableAt.locked": 1})
                        batch_display += f"\nOriginally Available Date | Locked"
                    elif self.library.mass_originally_available_update not in ["lock", "unlock", "remove", "reset"]:
                        try:
                            if omdb_item and self.library.mass_originally_available_update == "omdb":
                                new_date = omdb_item.released
                            elif mdb_item and self.library.mass_originally_available_update == "mdb":
                                new_date = mdb_item.released
                            elif tvdb_item and self.library.mass_originally_available_update == "tvdb":
                                new_date = tvdb_item.release_date
                            elif tmdb_item and self.library.mass_originally_available_update == "tmdb":
                                new_date = tmdb_item.release_date if self.library.is_movie else tmdb_item.first_air_date
                            elif anidb_item and self.library.mass_originally_available_update == "anidb":
                                new_date = anidb_item.released
                            elif mal_item and self.library.mass_originally_available_update == "mal":
                                new_date = mal_item.aired
                            else:
                                raise Failed
                            if not new_date:
                                logger.info(f"No Originally Available Date Found")
                            elif str(item.originallyAvailableAt) != str(new_date):
                                item.editOriginallyAvailable(new_date)
                                batch_display += f"\nOriginally Available Date | {new_date.strftime('%Y-%m-%d')}"
                        except Failed:
                            pass

                if len(batch_display) > 0:
                    item.saveEdits()
                    logger.info(f"Batch Edits{batch_display}")

                if self.library.mass_poster_update or self.library.mass_background_update:
                    try:
                        new_poster, new_background, item_dir, name = self.library.find_item_assets(item)
                    except Failed:
                        item_dir = None
                        name = None
                        new_poster = None
                        new_background = None
                    if self.library.mass_poster_update:
                        if self.library.mass_poster_update == "lock":
                            self.library.query(item.lockPoster)
                            logger.info("Poster | Locked")
                        elif self.library.mass_poster_update == "unlock":
                            self.library.query(item.unlockPoster)
                            logger.info("Poster | Unlocked")
                        else:
                            poster_location = "the Assets Directory" if new_poster else ""
                            poster_url = False if new_poster else True
                            new_poster = new_poster.location if new_poster else None
                            if not new_poster:
                                if self.library.mass_poster_update == "tmdb" and tmdb_item:
                                    new_poster = tmdb_item.poster_url
                                    poster_location = "TMDb"
                                if not new_poster:
                                    poster = next((p for p in item.posters() if p.provider == "local"), None)
                                    if poster:
                                        new_poster = f"{self.library.url}{poster.key}&X-Plex-Token={self.library.token}"
                                        poster_location = "Plex"
                            if new_poster:
                                self.library.upload_poster(item, new_poster, url=poster_url)
                                logger.info(f"Poster | Reset from {poster_location}")
                                if "Overlay" in [la.tag for la in self.library.item_labels(item)]:
                                    logger.info(self.library.edit_tags("label", item, remove_tags="Ovelray", do_print=False))
                            else:
                                logger.info("Poster | No Reset Image Found")

                    if self.library.mass_background_update:
                        if self.library.mass_background_update == "lock":
                            self.library.query(item.lockArt)
                            logger.info(f"Background | Locked")
                        elif self.library.mass_background_update == "unlock":
                            self.library.query(item.unlockArt)
                            logger.info(f"Background | Unlocked")
                        else:
                            background_location = "the Assets Directory" if new_background else ""
                            background_url = False if new_background else True
                            new_background = new_background.location if new_background else None
                            if not new_background:
                                if self.library.mass_background_update == "tmdb" and tmdb_item:
                                    new_background = tmdb_item.backdrop_url
                                    background_location = "TMDb"
                                if not new_background:
                                    background = next((p for p in item.arts() if p.provider == "local"), None)
                                    if background:
                                        new_background = f"{self.library.url}{background.key}&X-Plex-Token={self.library.token}"
                                        background_location = "Plex"
                            if new_background:
                                self.library.upload_background(item, new_background, url=background_url)
                                logger.info(f"Background | Reset from {background_location}")
                            else:
                                logger.info(f"Background | No Reset Image Found")

                    if self.library.is_show:
                        real_show = tmdb_item.load_show()  if tmdb_item else None
                        tmdb_seasons = {s.season_number: s for s in real_show.seasons} if real_show else {}
                        for season in self.library.query(item.seasons):
                            try:
                                season_poster, season_background, _, _ = self.library.find_item_assets(season, item_asset_directory=item_dir, folder_name=name)
                            except Failed:
                                season_poster = None
                                season_background = None

                            if self.library.mass_poster_update:
                                if self.library.mass_poster_update == "lock":
                                    self.library.query(season.lockPoster)
                                    logger.info(f"{season.title} Poster | Locked")
                                elif self.library.mass_poster_update == "unlock":
                                    self.library.query(season.unlockPoster)
                                    logger.info(f"{season.title} Poster | Unlocked")
                                else:
                                    poster_location = "the Assets Directory" if season_poster else ""
                                    poster_url = False if season_poster else True
                                    season_poster = season_poster.location if season_poster else None
                                    if not season_poster:
                                        if self.library.mass_poster_update == "tmdb" and season.seasonNumber in tmdb_seasons:
                                            season_poster = tmdb_seasons[season.seasonNumber].poster_url
                                            poster_location = "TMDb"
                                        if not season_poster:
                                            poster = next((p for p in season.posters() if p.provider == "local"), None)
                                            if poster:
                                                season_poster = f"{self.library.url}{poster.key}&X-Plex-Token={self.library.token}"
                                                poster_location = "Plex"
                                    if season_poster:
                                        self.library.upload_poster(season, season_poster, url=poster_url)
                                        logger.info(f"{season.title} Poster | Reset from {poster_location}")
                                        if "Overlay" in [la.tag for la in self.library.item_labels(season)]:
                                            logger.info(self.library.edit_tags("label", season, remove_tags="Ovelray", do_print=False))
                                    else:
                                        logger.info(f"{season.title} Poster | No Reset Image Found")
                            if self.library.mass_background_update:
                                if self.library.mass_background_update == "lock":
                                    self.library.query(season.lockArt)
                                    logger.info(f"{season.title} Background | Locked")
                                elif self.library.mass_background_update == "unlock":
                                    self.library.query(season.unlockArt)
                                    logger.info(f"{season.title} Background | Unlocked")
                                else:
                                    background_location = "the Assets Directory" if season_background else ""
                                    background_url = False if season_background else True
                                    season_background = season_background.location if season_background else None
                                    if not season_background:
                                        background = next((p for p in item.arts() if p.provider == "local"), None)
                                        if background:
                                            season_background = f"{self.library.url}{background.key}&X-Plex-Token={self.library.token}"
                                            background_location = "Plex"
                                    if season_background:
                                        self.library.upload_background(item, season_background, url=background_url)
                                        logger.info(f"{season.title} Background | Reset from {background_location}")
                                    else:
                                        logger.info(f"{season.title} Background | No Reset Image Found")

                            tmdb_episodes = {e.episode_number: e for e in tmdb_seasons[season.seasonNumber].episodes} if season.seasonNumber in tmdb_seasons else {}

                            for episode in self.library.query(season.episodes):
                                try:
                                    episode_poster, episode_background, _, _ = self.library.find_item_assets(episode, item_asset_directory=item_dir, folder_name=name)
                                except Failed:
                                    episode_poster = None
                                    episode_background = None

                                if self.library.mass_poster_update:
                                    if self.library.mass_poster_update == "lock":
                                        self.library.query(episode.lockPoster)
                                        logger.info(f"{episode.title} Poster | Locked")
                                    elif self.library.mass_poster_update == "unlock":
                                        self.library.query(episode.unlockPoster)
                                        logger.info(f"{episode.title} Poster | Unlocked")
                                    else:
                                        poster_location = "the Assets Directory" if episode_poster else ""
                                        poster_url = False if episode_poster else True
                                        episode_poster = episode_poster.location if episode_poster else None
                                        if not episode_poster:
                                            if self.library.mass_poster_update == "tmdb" and episode.episodeNumber in tmdb_episodes:
                                                episode_poster = tmdb_episodes[episode.episodeNumber].still_url
                                                poster_location = "TMDb"
                                            if not episode_poster:
                                                poster = next((p for p in episode.posters() if p.provider == "local"), None)
                                                if poster:
                                                    episode_poster = f"{self.library.url}{poster.key}&X-Plex-Token={self.library.token}"
                                                    poster_location = "Plex"
                                        if episode_poster:
                                            self.library.upload_poster(episode, episode_poster, url=poster_url)
                                            logger.info(f"{episode.title} Poster | Reset from {poster_location}")
                                            if "Overlay" in [la.tag for la in self.library.item_labels(episode)]:
                                                logger.info(self.library.edit_tags("label", episode, remove_tags="Ovelray", do_print=False))
                                        else:
                                            logger.info(f"{episode.title} Poster | No Reset Image Found")
                                if self.library.mass_background_update:
                                    if self.library.mass_background_update == "lock":
                                        self.library.query(episode.lockArt)
                                        logger.info(f"{episode.title} Background | Locked")
                                    elif self.library.mass_background_update == "unlock":
                                        self.library.query(episode.unlockArt)
                                        logger.info(f"{episode.title} Background | Unlocked")
                                    else:
                                        background_location = "the Assets Directory" if episode_background else ""
                                        background_url = False if episode_background else True
                                        episode_background = episode_background.location if episode_background else None
                                        if not episode_background:
                                            background = next((p for p in item.arts() if p.provider == "local"), None)
                                            if background:
                                                episode_background = f"{self.library.url}{background.key}&X-Plex-Token={self.library.token}"
                                                background_location = "Plex"
                                        if episode_background:
                                            self.library.upload_background(item, episode_background, url=background_url)
                                            logger.info(f"{episode.title} Background | Reset from {background_location}")
                                        else:
                                            logger.info(f"{episode.title} Background | No Reset Image Found")

                episode_ops = [self.library.mass_episode_audience_rating_update, self.library.mass_episode_critic_rating_update, self.library.mass_episode_user_rating_update]

                if any([x is not None for x in episode_ops]):

                    if any([x == "imdb" for x in episode_ops]) and not imdb_id:
                        logger.info(f"No IMDb ID for Guid: {item.guid}")

                    for ep in item.episodes():
                        ep.batchEdits()
                        batch_display = ""
                        item_title = self.library.get_item_sort_title(ep, atr="title")
                        logger.info("")
                        logger.info(f"Processing {item_title}")
                        episode_locked_fields = [f.name for f in ep.fields if f.locked]

                        def update_episode_rating(attribute, item_attr, display):
                            current = getattr(ep, item_attr)
                            if attribute in ["remove", "reset"] and current:
                                ep.editField(item_attr, None, locked=attribute == "remove")
                                return f"\n{display} | None"
                            elif attribute in ["unlock", "reset"] and item_attr in episode_locked_fields:
                                self.library.edit_query(ep, {f"{item_attr}.locked": 0})
                                return f"\n{display} | Unlocked"
                            elif attribute in ["lock", "remove"] and item_attr not in episode_locked_fields:
                                self.library.edit_query(ep, {f"{item_attr}.locked": 1})
                                return f"\n{display} | Locked"
                            elif attribute not in ["lock", "unlock", "remove", "reset"]:
                                found_rating = None
                                if tmdb_item and attribute == "tmdb":
                                    try:
                                        found_rating = self.config.TMDb.get_episode(tmdb_item.tmdb_id, ep.seasonNumber, ep.episodeNumber).vote_average
                                    except Failed as er:
                                        logger.error(er)
                                elif imdb_id and attribute == "imdb":
                                    found_rating = self.config.IMDb.get_episode_rating(imdb_id, ep.seasonNumber, ep.episodeNumber)

                                if found_rating is None:
                                    logger.info(f"No {display} Found")
                                elif str(current) != str(found_rating):
                                    ep.editField(item_attr, found_rating)
                                    return f"\n{display} | {found_rating}"
                            return ""

                        if self.library.mass_episode_audience_rating_update:
                            batch_display += update_episode_rating(self.library.mass_episode_audience_rating_update, "audienceRating", "Audience Rating")

                        if self.library.mass_episode_critic_rating_update:
                            batch_display += update_episode_rating(self.library.mass_episode_critic_rating_update, "rating", "Critic Rating")

                        if self.library.mass_episode_user_rating_update:
                            batch_display += update_episode_rating(self.library.mass_episode_user_rating_update, "userRating", "User Rating")

                        if len(batch_display) > 0:
                            ep.saveEdits()
                            logger.info(f"Batch Edits:{batch_display}")

            if self.library.Radarr and self.library.radarr_add_all_existing:
                try:
                    self.library.Radarr.add_tmdb(radarr_adds)
                except Failed as e:
                    logger.error(e)

            if self.library.Sonarr and self.library.sonarr_add_all_existing:
                try:
                    self.library.Sonarr.add_tvdb(sonarr_adds)
                except Failed as e:
                    logger.error(e)

        if self.library.radarr_remove_by_tag:
            self.library.Radarr.remove_all_with_tags(self.library.radarr_remove_by_tag)
        if self.library.sonarr_remove_by_tag:
            self.library.Sonarr.remove_all_with_tags(self.library.sonarr_remove_by_tag)

        if self.library.delete_collections:
            logger.info("")
            logger.separator(f"Deleting Collections", space=False, border=False)
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
                         or (managed is False and "PMM" in labels)
                         or (managed is True and "PMM" not in labels)) \
                    and (configured is None
                         or (configured is False and col.title in self.library.collections)
                         or (configured is True and col.title not in self.library.collections)):
                self.library.query(col.delete)
                logger.info(f"{col.title} Deleted")
            else:
                if "PMM" not in labels:
                    unmanaged_collections.append(col)
                if col.title not in self.library.collections:
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

        if self.library.assets_for_all and len(unconfigured_collections) > 0:
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
            if "metadata" not in yaml.data:
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
