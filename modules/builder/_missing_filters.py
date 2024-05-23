from arrapi import ArrException
from modules.util import Failed
from plexapi.video import Movie, Show
from ._config import tmdb_filters, tvdb_filters, imdb_filters

class MissingFiltersUtil:
    def __init__(self, collectionBuilder, logger):
        self.logger = logger
        self.collectionBuilder = collectionBuilder

    def run_missing(self):
        logger = self.logger
        added_to_radarr = 0
        added_to_sonarr = 0
        if len(self.collectionBuilder.missing_movies) > 0:
            if self.collectionBuilder.details["show_missing"] is True:
                logger.info("")
                logger.separator(f"Missing Movies from Library: {self.collectionBuilder.library.name}", space=False, border=False)
                logger.info("")
            missing_movies_with_names = []
            filtered_movies_with_names = []
            for missing_id in self.collectionBuilder.missing_movies:
                try:
                    movie = self.collectionBuilder.config.TMDb.get_movie(missing_id)
                except Failed as e:
                    logger.error(e)
                    continue
                current_title = f"{movie.title} ({movie.release_date.year})" if movie.release_date else movie.title
                if self._check_missing_filters(missing_id, True, tmdb_item=movie, check_released=self.collectionBuilder.details["missing_only_released"]):
                    missing_movies_with_names.append((current_title, missing_id))
                    if self.collectionBuilder.details["show_missing"] is True:
                        logger.info(f"{self.collectionBuilder.name} {self.collectionBuilder.Type} | ? | {current_title} (TMDb: {missing_id})")
                else:
                    filtered_movies_with_names.append((current_title, missing_id))
                    if self.collectionBuilder.details["show_filtered"] is True and self.collectionBuilder.details["show_missing"] is True:
                        logger.info(f"{self.collectionBuilder.name} {self.collectionBuilder.Type} | X | {current_title} (TMDb: {missing_id})")
            logger.info("")
            logger.info(f"{len(missing_movies_with_names)} Movie{'s' if len(missing_movies_with_names) > 1 else ''} Missing")
            if len(missing_movies_with_names) > 0:
                if self.collectionBuilder.do_report:
                    self.collectionBuilder.library.add_missing(self.collectionBuilder.name, missing_movies_with_names, True)
                if self.collectionBuilder.run_again or (self.collectionBuilder.library.Radarr and (self.collectionBuilder.radarr_details["add_missing"] or "item_radarr_tag" in self.collectionBuilder.item_details)):
                    missing_tmdb_ids = [missing_id for title, missing_id in missing_movies_with_names]
                    if self.collectionBuilder.library.Radarr:
                        if self.collectionBuilder.radarr_details["add_missing"]:
                            try:
                                added = self.collectionBuilder.library.Radarr.add_tmdb(missing_tmdb_ids, **self.collectionBuilder.radarr_details)
                                self.collectionBuilder.added_to_radarr.extend([{"title": movie.title, "id": movie.tmdbId} for movie in added])
                                added_to_radarr += len(added)
                            except Failed as e:
                                logger.error(e)
                            except ArrException as e:
                                logger.stacktrace()
                                logger.error(f"Arr Error: {e}")
                        if "item_radarr_tag" in self.collectionBuilder.item_details:
                            try:
                                self.collectionBuilder.library.Radarr.edit_tags(missing_tmdb_ids, self.collectionBuilder.item_details["item_radarr_tag"], self.collectionBuilder.item_details["apply_tags"])
                            except Failed as e:
                                logger.error(e)
                            except ArrException as e:
                                logger.stacktrace()
                                logger.error(f"Arr Error: {e}")
                    if self.collectionBuilder.run_again:
                        self.collectionBuilder.run_again_movies.extend(missing_tmdb_ids)
            if len(filtered_movies_with_names) > 0 and self.collectionBuilder.do_report:
                self.collectionBuilder.library.add_filtered(self.collectionBuilder.name, filtered_movies_with_names, True)
        if len(self.collectionBuilder.missing_shows) > 0 and self.collectionBuilder.library.is_show:
            if self.collectionBuilder.details["show_missing"] is True:
                logger.info("")
                logger.separator(f"Missing Shows from Library: {self.collectionBuilder.name}", space=False, border=False)
                logger.info("")
            missing_shows_with_names = []
            filtered_shows_with_names = []
            for missing_id in self.collectionBuilder.missing_shows:
                try:
                    title = self.collectionBuilder.config.TVDb.get_tvdb_obj(missing_id).title
                except Failed as e:
                    logger.error(e)
                    continue
                if self._check_missing_filters(missing_id, False, check_released=self.collectionBuilder.details["missing_only_released"]):
                    missing_shows_with_names.append((title, missing_id))
                    if self.collectionBuilder.details["show_missing"] is True:
                        logger.info(f"{self.collectionBuilder.name} {self.collectionBuilder.Type} | ? | {title} (TVDb: {missing_id})")
                else:
                    filtered_shows_with_names.append((title, missing_id))
                    if self.collectionBuilder.details["show_filtered"] is True and self.collectionBuilder.details["show_missing"] is True:
                        logger.info(f"{self.collectionBuilder.name} {self.collectionBuilder.Type} | X | {title} (TVDb: {missing_id})")
            logger.info("")
            logger.info(f"{len(missing_shows_with_names)} Show{'s' if len(missing_shows_with_names) > 1 else ''} Missing")
            if len(missing_shows_with_names) > 0:
                if self.collectionBuilder.do_report:
                    self.collectionBuilder.library.add_missing(self.collectionBuilder.name, missing_shows_with_names, False)
                if self.collectionBuilder.run_again or (self.collectionBuilder.library.Sonarr and (self.collectionBuilder.sonarr_details["add_missing"] or "item_sonarr_tag" in self.collectionBuilder.item_details)):
                    missing_tvdb_ids = [missing_id for title, missing_id in missing_shows_with_names]
                    if self.collectionBuilder.library.Sonarr:
                        if self.collectionBuilder.sonarr_details["add_missing"]:
                            try:
                                added = self.collectionBuilder.library.Sonarr.add_tvdb(missing_tvdb_ids, **self.collectionBuilder.sonarr_details)
                                self.collectionBuilder.added_to_sonarr.extend([{"title": show.title, "id": show.tvdbId} for show in added])
                                added_to_sonarr += len(added)
                            except Failed as e:
                                logger.error(e)
                            except ArrException as e:
                                logger.stacktrace()
                                logger.error(f"Arr Error: {e}")
                        if "item_sonarr_tag" in self.collectionBuilder.item_details:
                            try:
                                self.collectionBuilder.library.Sonarr.edit_tags(missing_tvdb_ids, self.collectionBuilder.item_details["item_sonarr_tag"], self.collectionBuilder.item_details["apply_tags"])
                            except Failed as e:
                                logger.error(e)
                            except ArrException as e:
                                logger.stacktrace()
                                logger.error(f"Arr Error: {e}")
                    if self.collectionBuilder.run_again:
                        self.collectionBuilder.run_again_shows.extend(missing_tvdb_ids)
            if len(filtered_shows_with_names) > 0 and self.collectionBuilder.do_report:
                self.collectionBuilder.library.add_filtered(self.collectionBuilder.name, filtered_shows_with_names, False)
        if len(self.collectionBuilder.missing_parts) > 0 and self.collectionBuilder.library.is_show:
            if self.collectionBuilder.details["show_missing"] is True:
                for missing in self.collectionBuilder.missing_parts:
                    logger.info(f"{self.collectionBuilder.name} {self.collectionBuilder.Type} | ? | {missing}")
            if self.collectionBuilder.do_report:
                self.collectionBuilder.library.add_missing(self.collectionBuilder.name, self.collectionBuilder.missing_parts, False)
        return added_to_radarr, added_to_sonarr

    def check_filters(self, item, display):
        logger = self.logger
        final_return = True
        if self.collectionBuilder.filters and not self.collectionBuilder.details["only_filter_missing"]:
            logger.ghost(f"Filtering {display} {item.title}")
            item = self.collectionBuilder.library.reload(item)
            final_return = False
            tmdb_item = None
            tvdb_item = None
            imdb_info = None
            for filter_list in self.collectionBuilder.filters:
                tmdb_f = []
                tvdb_f = []
                imdb_f = []
                plex_f = []
                for k, v in filter_list:
                    if k.split(".")[0] in tmdb_filters:
                        tmdb_f.append((k, v))
                    elif k.split(".")[0] in tvdb_filters:
                        tvdb_f.append((k, v))
                    elif k.split(".")[0] in imdb_filters:
                        imdb_f.append((k, v))
                    else:
                        plex_f.append((k, v))
                or_result = True
                if tmdb_f:
                    if not tmdb_item and isinstance(item, (Movie, Show)):
                        if item.ratingKey not in self.collectionBuilder.library.movie_rating_key_map and item.ratingKey not in self.collectionBuilder.library.show_rating_key_map:
                            logger.warning(f"Filter Error: No {'TMDb' if self.collectionBuilder.library.is_movie else 'TVDb'} ID found for {item.title}")
                            or_result = False
                        else:
                            try:
                                if item.ratingKey in self.collectionBuilder.library.movie_rating_key_map:
                                    tmdb_item = self.collectionBuilder.config.TMDb.get_movie(self.collectionBuilder.library.movie_rating_key_map[item.ratingKey], ignore_cache=True)
                                else:
                                    tmdb_item = self.collectionBuilder.config.TMDb.get_show(self.collectionBuilder.config.Convert.tvdb_to_tmdb(self.collectionBuilder.library.show_rating_key_map[item.ratingKey], fail=True), ignore_cache=True)
                            except Failed as e:
                                logger.error(e)
                                or_result = False
                    if not tmdb_item or self._check_tmdb_filters(tmdb_item, tmdb_f, item.ratingKey in self.collectionBuilder.library.movie_rating_key_map) is False:
                        or_result = False
                if tvdb_f:
                    if not tvdb_item and isinstance(item, Show):
                        if item.ratingKey not in self.collectionBuilder.library.show_rating_key_map:
                            logger.warning(f"Filter Error: No TVDb ID found for {item.title}")
                            or_result = False
                        else:
                            try:
                                tvdb_item = self.collectionBuilder.config.TVDb.get_tvdb_obj(self.collectionBuilder.library.show_rating_key_map[item.ratingKey])
                            except Failed as e:
                                logger.error(e)
                                or_result = False
                    if not tvdb_item or self._check_tvdb_filters(tvdb_item, tvdb_f) is False:
                        or_result = False
                if imdb_f:
                    if not imdb_info and isinstance(item, (Movie, Show)):
                        if item.ratingKey not in self.collectionBuilder.library.imdb_rating_key_map:
                            logger.warning(f"Filter Error: No IMDb ID found for {item.title}")
                            or_result = False
                        else:
                            try:
                                imdb_info = self.collectionBuilder.config.IMDb.keywords(self.collectionBuilder.library.imdb_rating_key_map[item.ratingKey], self.collectionBuilder.language)
                            except Failed as e:
                                logger.error(e)
                                or_result = False
                    if not imdb_info or self.collectionBuilder.check_imdb_filters(imdb_info, imdb_f) is False:
                        or_result = False
                if plex_f and self.collectionBuilder.library.check_filters(item, plex_f, self.collectionBuilder.current_time) is False:
                    or_result = False
                if or_result:
                    final_return = True
        return final_return
    

    def _check_missing_filters(self, item_id, is_movie, tmdb_item=None, check_released=False):
        logger = self.logger
        imdb_info = None
        if self.collectionBuilder.has_tmdb_filters or self.collectionBuilder.has_imdb_filters or check_released:
            try:
                if tmdb_item is None:
                    if is_movie:
                        tmdb_item = self.collectionBuilder.config.TMDb.get_movie(item_id, ignore_cache=True)
                    else:
                        tmdb_item = self.collectionBuilder.config.TMDb.get_show(self.collectionBuilder.config.Convert.tvdb_to_tmdb(item_id, fail=True), ignore_cache=True)
            except Failed:
                return False
        if self.collectionBuilder.has_imdb_filters and tmdb_item and tmdb_item.imdb_id:
            try:
                imdb_info = self.collectionBuilder.config.IMDb.keywords(tmdb_item.imdb_id, self.collectionBuilder.language)
            except Failed as e:
                logger.error(e)
                return False
        if check_released:
            date_to_check = tmdb_item.release_date if is_movie else tmdb_item.first_air_date
            if not date_to_check or date_to_check > self.collectionBuilder.current_time:
                return False
        final_return = True
        if self.collectionBuilder.has_tmdb_filters or self.collectionBuilder.has_imdb_filters:
            final_return = False
            for filter_list in self.collectionBuilder.filters:
                tmdb_f = []
                imdb_f = []
                for k, v in filter_list:
                    if k.split(".")[0] in tmdb_filters:
                        tmdb_f.append((k, v))
                    elif k.split(".")[0] in imdb_filters:
                        imdb_f.append((k, v))
                or_result = True
                if tmdb_f:
                    if not tmdb_item or self._check_tmdb_filters(tmdb_item, tmdb_f, is_movie) is False:
                        or_result = False
                if imdb_f:
                    if not imdb_info and self._check_imdb_filters(imdb_info, imdb_f) is False:
                        or_result = False
                if or_result:
                    final_return = True
        return final_return
    
    def _check_tmdb_filters(self, tmdb_item, filters_in, is_movie):
        for filter_method, filter_data in filters_in:
            filter_attr, modifier, filter_final = self.collectionBuilder.library.split(filter_method)
            if self.collectionBuilder.config.TMDb.item_filter(tmdb_item, filter_attr, modifier, filter_final, filter_data, is_movie, self.collectionBuilder.current_time) is False:
                return False
        return True

    def _check_tvdb_filters(self, tvdb_item, filters_in):
        for filter_method, filter_data in filters_in:
            filter_attr, modifier, filter_final = self.collectionBuilder.library.split(filter_method)
            if self.collectionBuilder.config.TVDb.item_filter(tvdb_item, filter_attr, modifier, filter_final, filter_data) is False:
                return False
        return True

    def _check_imdb_filters(self, imdb_info, filters_in):
        for filter_method, filter_data in filters_in:
            filter_attr, modifier, filter_final = self.collectionBuilder.library.split(filter_method)
            if self.collectionBuilder.config.IMDb.item_filter(imdb_info, filter_attr, modifier, filter_final, filter_data) is False:
                return False
        return True