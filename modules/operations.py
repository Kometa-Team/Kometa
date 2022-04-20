import os, re
from modules import util
from modules.util import Failed
from ruamel import yaml

logger = util.logger

class Operations:
    def __init__(self, config, library):
        self.config = config
        self.library = library

    def run_operations(self):
        logger.info("")
        logger.separator(f"{self.library.name} Library Operations")
        logger.info("")
        logger.debug(f"Assets For All: {self.library.assets_for_all}")
        logger.debug(f"Delete Collections With Less: {self.library.delete_collections_with_less}")
        logger.debug(f"Delete Unmanaged Collections: {self.library.delete_unmanaged_collections}")
        logger.debug(f"Mass Genre Update: {self.library.mass_genre_update}")
        logger.debug(f"Mass Audience Rating Update: {self.library.mass_audience_rating_update}")
        logger.debug(f"Mass Critic Rating Update: {self.library.mass_critic_rating_update}")
        logger.debug(f"Mass Content Rating Update: {self.library.mass_content_rating_update}")
        logger.debug(f"Mass Originally Available Update: {self.library.mass_originally_available_update}")
        logger.debug(f"Mass IMDb Parental Labels: {self.library.mass_imdb_parental_labels}")
        logger.debug(f"Mass Trakt Rating Update: {self.library.mass_trakt_rating_update}")
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
            tracks = self.library.get_all(collection_level="track")
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
            trakt_ratings = self.config.Trakt.user_ratings(self.library.is_movie) if self.library.mass_trakt_rating_update else []

            reverse_anidb = {}
            if self.library.mass_genre_update == "anidb":
                for k, v in self.library.anidb_map.items():
                    reverse_anidb[v] = k

            for i, item in enumerate(items, 1):
                logger.ghost(f"Processing: {i}/{len(items)} {item.title}")
                if self.library.assets_for_all:
                    self.library.update_asset2(item)
                tmdb_id, tvdb_id, imdb_id = self.library.get_ids(item)

                item.batchEdits()
                batch_display = "Batch Edits"

                if self.library.remove_title_parentheses:
                    if not any([f.name == "title" and f.locked for f in item.fields]) and item.title.endswith(")"):
                        new_title = re.sub(" \\(\\w+\\)$", "", item.title)
                        item.editTitle(new_title)
                        batch_display += f"\n{item.title[:25]:<25} | Title | {new_title}"

                if self.library.mass_trakt_rating_update:
                    try:
                        if self.library.is_movie and tmdb_id in trakt_ratings:
                            new_rating = trakt_ratings[tmdb_id]
                        elif self.library.is_show and tvdb_id in trakt_ratings:
                            new_rating = trakt_ratings[tvdb_id]
                        else:
                            raise Failed
                        if str(item.userRating) != str(new_rating):
                            self.library.query_data(item.rate, new_rating)
                            logger.info(f"{item.title[:25]:<25} | User Rating | {new_rating}")
                    except Failed:
                        pass

                if self.library.mass_imdb_parental_labels:
                    try:
                        parental_guide = self.config.IMDb.parental_guide(imdb_id)
                        labels = [f"{k.capitalize()}:{v}" for k, v in parental_guide.items() if self.library.mass_imdb_parental_labels == "with_none" or v != "None"]
                        batch_display += f"\n{self.library.edit_tags('label', item, add_tags=labels)}"
                    except Failed:
                        pass

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
                    if self.config.OMDb.limit is False:
                        if tmdb_id and not imdb_id:
                            imdb_id = self.config.Convert.tmdb_to_imdb(tmdb_id)
                        elif tvdb_id and not imdb_id:
                            imdb_id = self.config.Convert.tvdb_to_imdb(tvdb_id)
                        if imdb_id:
                            try:
                                omdb_item = self.config.OMDb.get_omdb(imdb_id)
                            except Failed as e:
                                logger.error(str(e))
                            except Exception:
                                logger.error(f"IMDb ID: {imdb_id}")
                                raise
                        else:
                            logger.info(f"{item.title[:25]:<25} | No IMDb ID for Guid: {item.guid}")

                tvdb_item = None
                if any([o == "tvdb" for o in self.library.meta_operations]):
                    if tvdb_id:
                        try:
                            tvdb_item = self.config.TVDb.get_item(tvdb_id, self.library.is_movie)
                        except Failed as e:
                            logger.error(str(e))
                    else:
                        logger.info(f"{item.title[:25]:<25} | No TVDb ID for Guid: {item.guid}")

                anidb_item = None
                if any([o == "anidb" for o in self.library.meta_operations]):
                    if item.ratingKey in reverse_anidb:
                        anidb_id = reverse_anidb[item.ratingKey]
                    elif tvdb_id in self.config.Convert._tvdb_to_anidb:
                        anidb_id = self.config.Convert._tvdb_to_anidb[tvdb_id]
                    elif imdb_id in self.config.Convert._imdb_to_anidb:
                        anidb_id = self.config.Convert._imdb_to_anidb[imdb_id]
                    else:
                        anidb_id = None
                        logger.info(f"{item.title[:25]:<25} | No AniDB ID for Guid: {item.guid}")
                    if anidb_id:
                        try:
                            anidb_item = self.config.AniDB.get_anime(anidb_id)
                        except Failed as e:
                            logger.error(str(e))

                mdb_item = None
                if any([o and o.startswith("mdb") for o in self.library.meta_operations]):
                    if self.config.Mdblist.limit is False:
                        if tmdb_id and not imdb_id:
                            imdb_id = self.config.Convert.tmdb_to_imdb(tmdb_id)
                        elif tvdb_id and not imdb_id:
                            imdb_id = self.config.Convert.tvdb_to_imdb(tvdb_id)
                        if imdb_id:
                            try:
                                mdb_item = self.config.Mdblist.get_imdb(imdb_id)
                            except Failed as e:
                                logger.error(str(e))
                            except Exception:
                                logger.error(f"IMDb ID: {imdb_id}")
                                raise
                        else:
                            logger.info(f"{item.title[:25]:<25} | No IMDb ID for Guid: {item.guid}")

                def get_rating(attribute):
                    if tmdb_item and attribute == "tmdb":
                        return tmdb_item.vote_average
                    elif omdb_item and attribute == "omdb":
                        return omdb_item.imdb_rating
                    elif mdb_item and attribute == "mdb":
                        return mdb_item.score / 10 if mdb_item.score else None
                    elif mdb_item and attribute == "mdb_imdb":
                        return mdb_item.imdb_rating if mdb_item.imdb_rating else None
                    elif mdb_item and attribute == "mdb_metacritic":
                        return mdb_item.metacritic_rating / 10 if mdb_item.metacritic_rating else None
                    elif mdb_item and attribute == "mdb_metacriticuser":
                        return mdb_item.metacriticuser_rating if mdb_item.metacriticuser_rating else None
                    elif mdb_item and attribute == "mdb_trakt":
                        return mdb_item.trakt_rating / 10 if mdb_item.trakt_rating else None
                    elif mdb_item and attribute == "mdb_tomatoes":
                        return mdb_item.tomatoes_rating / 10 if mdb_item.tomatoes_rating else None
                    elif mdb_item and attribute == "mdb_tomatoesaudience":
                        return mdb_item.tomatoesaudience_rating / 10 if mdb_item.tomatoesaudience_rating else None
                    elif mdb_item and attribute == "mdb_tmdb":
                        return mdb_item.tmdb_rating / 10 if mdb_item.tmdb_rating else None
                    elif mdb_item and attribute == "mdb_letterboxd":
                        return mdb_item.letterboxd_rating * 2 if mdb_item.letterboxd_rating else None
                    elif anidb_item and attribute == "anidb_rating":
                        return anidb_item.rating
                    elif anidb_item and attribute == "anidb_average":
                        return anidb_item.average
                    else:
                        raise Failed

                if self.library.mass_genre_update or self.library.genre_mapper:
                    try:
                        new_genres = []
                        if self.library.mass_genre_update:
                            if tmdb_item and self.library.mass_genre_update == "tmdb":
                                new_genres = tmdb_item.genres
                            elif omdb_item and self.library.mass_genre_update == "omdb":
                                new_genres = omdb_item.genres
                            elif tvdb_item and self.library.mass_genre_update == "tvdb":
                                new_genres = tvdb_item.genres
                            elif anidb_item and self.library.mass_genre_update == "anidb":
                                new_genres = anidb_item.tags
                            else:
                                raise Failed
                            if not new_genres:
                                logger.info(f"{item.title[:25]:<25} | No Genres Found")
                        if self.library.genre_mapper:
                            if not new_genres:
                                new_genres = [g.tag for g in item.genres]
                            mapped_genres = []
                            for genre in new_genres:
                                if genre in self.library.genre_mapper:
                                    if self.library.genre_mapper[genre]:
                                        mapped_genres.append(self.library.genre_mapper[genre])
                                else:
                                    mapped_genres.append(genre)
                            new_genres = mapped_genres
                        batch_display += f"\n{self.library.edit_tags('genre', item, sync_tags=new_genres)}"
                    except Failed:
                        pass

                if self.library.mass_audience_rating_update:
                    try:
                        new_rating = get_rating(self.library.mass_audience_rating_update)
                        if new_rating is None:
                            logger.info(f"{item.title[:25]:<25} | No Rating Found")
                        elif str(item.audienceRating) != str(new_rating):
                            item.editField("audienceRating", new_rating)
                            batch_display += f"\n{item.title[:25]:<25} | Audience Rating | {new_rating}"
                    except Failed:
                        pass

                if self.library.mass_critic_rating_update:
                    try:
                        new_rating = get_rating(self.library.mass_critic_rating_update)
                        if new_rating is None:
                            logger.info(f"{item.title[:25]:<25} | No Rating Found")
                        elif str(item.rating) != str(new_rating):
                            item.editField("rating", new_rating)
                            batch_display += f"{item.title[:25]:<25} | Critic Rating | {new_rating}"
                    except Failed:
                        pass

                if self.library.mass_content_rating_update or self.library.content_rating_mapper:
                    try:
                        new_rating = None
                        if self.library.mass_content_rating_update:
                            if omdb_item and self.library.mass_content_rating_update == "omdb":
                                new_rating = omdb_item.content_rating
                            elif mdb_item and self.library.mass_content_rating_update == "mdb":
                                new_rating = mdb_item.content_rating if mdb_item.content_rating else None
                            elif mdb_item and self.library.mass_content_rating_update == "mdb_commonsense":
                                new_rating = mdb_item.commonsense if mdb_item.commonsense else None
                            elif tmdb_item and self.library.mass_content_rating_update == "tmdb":
                                new_rating = tmdb_item.content_rating if tmdb_item.content_rating else None
                            else:
                                raise Failed
                            if new_rating is None:
                                logger.info(f"{item.title[:25]:<25} | No Content Rating Found")
                        if self.library.content_rating_mapper:
                            if new_rating is None:
                                new_rating = item.contentRating
                            if new_rating in self.library.content_rating_mapper:
                                new_rating = self.library.content_rating_mapper[new_rating]
                        if str(item.contentRating) != str(new_rating):
                            item.editContentRating(new_rating)
                            batch_display += f"\n{item.title[:25]:<25} | Content Rating | {new_rating}"
                    except Failed:
                        pass
                if self.library.mass_originally_available_update:
                    try:
                        if omdb_item and self.library.mass_originally_available_update == "omdb":
                            new_date = omdb_item.released
                        elif mdb_item and self.library.mass_originally_available_update == "mdb":
                            new_date = mdb_item.released
                        elif tvdb_item and self.library.mass_originally_available_update == "tvdb":
                            new_date = tvdb_item.released
                        elif tmdb_item and self.library.mass_originally_available_update == "tmdb":
                            new_date = tmdb_item.release_date if self.library.is_movie else tmdb_item.first_air_date
                        elif anidb_item and self.library.mass_originally_available_update == "anidb":
                            new_date = anidb_item.released
                        else:
                            raise Failed
                        if new_date is None:
                            logger.info(f"{item.title[:25]:<25} | No Originally Available Date Found")
                        elif str(item.originallyAvailableAt) != str(new_date):
                            item.editOriginallyAvailable(new_date)
                            batch_display += f"\n{item.title[:25]:<25} | Originally Available Date | {new_date.strftime('%Y-%m-%d')}"
                    except Failed:
                        pass

                item.saveEdits()

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

        if self.library.delete_collections_with_less is not None or self.library.delete_unmanaged_collections:
            logger.info("")
            print_suffix = ""
            unmanaged = ""
            if self.library.delete_collections_with_less is not None and self.library.delete_collections_with_less > 0:
                print_suffix = f" with less then {self.library.delete_collections_with_less} item{'s' if self.library.delete_collections_with_less > 1 else ''}"
            if self.library.delete_unmanaged_collections:
                if self.library.delete_collections_with_less is None:
                    unmanaged = "Unmanaged Collections "
                elif self.library.delete_collections_with_less > 0:
                    unmanaged = "Unmanaged Collections and "
            logger.separator(f"Deleting All {unmanaged}Collections{print_suffix}", space=False, border=False)
            logger.info("")
        unmanaged_collections = []
        for col in self.library.get_all_collections():
            if (self.library.delete_collections_with_less and col.childCount < self.library.delete_collections_with_less) \
                or (self.library.delete_unmanaged_collections and col.title not in self.library.collections):
                self.library.query(col.delete)
                logger.info(f"{col.title} Deleted")
            elif col.title not in self.library.collections:
                unmanaged_collections.append(col)

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

        if self.library.assets_for_all and len(unmanaged_collections) > 0:
            logger.info("")
            logger.separator(f"Unmanaged Collection Assets Check for {self.library.name} Library", space=False, border=False)
            logger.info("")
            for col in unmanaged_collections:
                self.library.update_asset2(col)
        if self.library.mass_collection_mode:
            logger.info("")
            logger.separator(f"Unmanaged Mass Collection Mode for {self.library.name} Library", space=False, border=False)
            logger.info("")
            for col in unmanaged_collections:
                self.library.collection_mode_query(col, self.library.mass_collection_mode)

        if self.library.metadata_backup:
            logger.info("")
            logger.separator(f"Metadata Backup for {self.library.name} Library", space=False, border=False)
            logger.info("")
            logger.info(f"Metadata Backup Path: {self.library.metadata_backup['path']}")
            logger.info("")
            meta = None
            if os.path.exists(self.library.metadata_backup["path"]):
                try:
                    meta, _, _ = yaml.util.load_yaml_guess_indent(open(self.library.metadata_backup["path"], encoding="utf-8"))
                except yaml.scanner.ScannerError as e:
                    logger.error(f"YAML Error: {util.tab_new_lines(e)}")
                    filename, file_extension = os.path.splitext(self.library.metadata_backup["path"])
                    i = 1
                    while os.path.exists(f"{filename}{i}{file_extension}"):
                        i += 1
                    os.rename(self.library.metadata_backup["path"], f"{filename}{i}{file_extension}")
                    logger.error(f"Backup failed to load saving copy to {filename}{i}{file_extension}")
            if not meta:
                meta = {}
            if "metadata" not in meta:
                meta["metadata"] = {}
            special_names = {}
            for mk, mv in meta["metadata"].items():
                if "title" in mv:
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
                og_dict = meta["metadata"][map_key] if map_key in meta["metadata"] and meta["metadata"][map_key] else {}
                if attrs or (self.library.metadata_backup["add_blank_entries"] and not og_dict):
                    def get_dict(attrs_dict):
                        return {ak: get_dict(av) if isinstance(av, dict) else av for ak, av in attrs_dict.items()}
                    def loop_dict(looping, dest_dict):
                        if not looping:
                            return None
                        for lk, lv in looping.items():
                            dest_dict[lk] = loop_dict(lv, dest_dict[lk] if lk in dest_dict and dest_dict[lk] else {}) if isinstance(lv, dict) else lv
                        return dest_dict
                    meta["metadata"][map_key] = loop_dict(get_dict(attrs), og_dict)
            logger.exorcise()
            try:
                yaml.round_trip_dump(meta, open(self.library.metadata_backup["path"], "w", encoding="utf-8"), block_seq_indent=2)
                logger.info(f"{len(meta['metadata'])} {self.library.type.capitalize()}{'s' if len(meta['metadata']) > 1 else ''} Backed Up")
            except yaml.scanner.ScannerError as e:
                logger.error(f"YAML Error: {util.tab_new_lines(e)}")
