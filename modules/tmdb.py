import logging
from modules import util
from modules.util import Failed
from tmdbapis import TMDbAPIs, TMDbException, NotFound

logger = logging.getLogger("Plex Meta Manager")

builders = [
    "tmdb_actor", "tmdb_actor_details", "tmdb_collection", "tmdb_collection_details", "tmdb_company",
    "tmdb_crew", "tmdb_crew_details", "tmdb_director", "tmdb_director_details", "tmdb_discover",
    "tmdb_keyword", "tmdb_list", "tmdb_list_details", "tmdb_movie", "tmdb_movie_details", "tmdb_network",
    "tmdb_now_playing", "tmdb_popular", "tmdb_producer", "tmdb_producer_details", "tmdb_show", "tmdb_show_details",
    "tmdb_top_rated", "tmdb_trending_daily", "tmdb_trending_weekly", "tmdb_writer", "tmdb_writer_details"
]
type_map = {
    "tmdb_actor": "Person", "tmdb_actor_details": "Person", "tmdb_crew": "Person", "tmdb_crew_details": "Person",
    "tmdb_collection": "Collection", "tmdb_collection_details": "Collection", "tmdb_company": "Company",
    "tmdb_director": "Person", "tmdb_director_details": "Person", "tmdb_keyword": "Keyword",
    "tmdb_list": "List", "tmdb_list_details": "List", "tmdb_movie": "Movie", "tmdb_movie_details": "Movie",
    "tmdb_network": "Network", "tmdb_person": "Person", "tmdb_producer": "Person", "tmdb_producer_details": "Person",
    "tmdb_show": "Show", "tmdb_show_details": "Show", "tmdb_writer": "Person", "tmdb_writer_details": "Person"
}
discover_all = [
    "language", "with_original_language", "region", "sort_by", "with_cast", "with_crew", "with_people",
    "certification_country", "certification", "certification.lte", "certification.gte",
    "year", "primary_release_year", "primary_release_date.gte", "primary_release_date.lte",
    "release_date.gte", "release_date.lte", "vote_count.gte", "vote_count.lte",
    "vote_average.gte", "vote_average.lte", "with_runtime.gte", "with_runtime.lte",
    "with_companies", "without_companies ", "with_genres", "without_genres", "with_keywords", "without_keywords",
    "with_watch_providers", "without_watch_providers", "watch_region", "with_watch_monetization_types", "with_status",
    "include_adult", "include_video", "timezone", "screened_theatrically", "include_null_first_air_dates", "limit", "with_type",
    "air_date.gte", "air_date.lte", "first_air_date.gte", "first_air_date.lte", "first_air_date_year", "with_networks", "with_release_type"
]
discover_movie_only = [
    "region", "with_cast", "with_crew", "with_people", "certification_country", "certification", "include_video",
    "year", "primary_release_year", "primary_release_date", "release_date", "include_adult", "with_release_type"
]
discover_tv_only = [
    "timezone", "screened_theatrically", "include_null_first_air_dates", "air_date",
    "first_air_date", "first_air_date_year", "with_networks", "with_status", "with_type",
]
discover_strings = [
    "with_cast", "with_crew", "with_people", "with_companies", "with_networks", "with_genres", "without_genres", "with_release_type",
    "with_keywords", "without_keywords", "with_original_language", "timezone", "with_watch_providers", "without_watch_providers"
]
discover_ints = ["vote_count", "with_runtime"]
discover_years = ["primary_release_year", "year", "first_air_date_year"]
discover_booleans = ["include_adult", "include_video", "include_null_first_air_dates", "screened_theatrically"]
discover_dates = [
    "primary_release_date.gte", "primary_release_date.lte", "release_date.gte", "release_date.lte",
    "air_date.gte", "air_date.lte", "first_air_date.gte", "first_air_date.lte"
]
discover_movie_sort = [
    "popularity.asc", "popularity.desc", "release_date.asc", "release_date.desc", "revenue.asc", "revenue.desc",
    "primary_release_date.asc", "primary_release_date.desc", "original_title.asc", "original_title.desc",
    "vote_average.asc", "vote_average.desc", "vote_count.asc", "vote_count.desc"
]
discover_tv_sort = ["vote_average.desc", "vote_average.asc", "first_air_date.desc", "first_air_date.asc", "popularity.desc", "popularity.asc"]
discover_monetization_types = ["flatrate", "free", "ads", "rent", "buy"]

class TMDb:
    def __init__(self, config, params):
        self.config = config
        self.apikey = params["apikey"]
        self.language = params["language"]
        try:
            self.TMDb = TMDbAPIs(self.apikey, language=self.language, session=self.config.session)
        except TMDbException as e:
            raise Failed(f"TMDb Error: {e}")

    def convert_from(self, tmdb_id, convert_to, is_movie):
        item = self.get_movie(tmdb_id) if is_movie else self.get_show(tmdb_id)
        check_id = item.tvdb_id if convert_to == "tvdb_id" and not is_movie else item.imdb_id
        if not check_id:
            raise Failed(f"TMDb Error: No {convert_to.upper().replace('B_', 'b ')} found for TMDb ID {tmdb_id}")
        return check_id

    def convert_tvdb_to(self, tvdb_id):
        results = self.TMDb.find_by_id(tvdb_id=tvdb_id)
        if not results.tv_results:
            raise Failed(f"TMDb Error: No TMDb ID found for TVDb ID {tvdb_id}")
        return results.tv_results[0].id

    def convert_imdb_to(self, imdb_id):
        try:
            results = self.TMDb.find_by_id(imdb_id=imdb_id)
            if results.movie_results:
                return results.movie_results[0].id, "movie"
            elif results.tv_results:
                return results.tv_results[0].id, "show"
            elif results.tv_episode_results:
                item = results.tv_episode_results[0]
                return f"{item.tv_id}_{item.season_number}_{item.episode_number}", "episode"
            else:
                raise NotFound
        except NotFound:
            raise Failed(f"TMDb Error: No TMDb ID found for IMDb ID {imdb_id}")

    def get_movie_show_or_collection(self, tmdb_id, is_movie):
        if is_movie:
            try:                            return self.get_collection(tmdb_id)
            except Failed:
                try:                            return self.get_movie(tmdb_id)
                except Failed:                  raise Failed(f"TMDb Error: No Movie or Collection found for TMDb ID {tmdb_id}")
        else:                           return self.get_show(tmdb_id)

    def get_movie(self, tmdb_id):
        try:                            return self.TMDb.movie(tmdb_id)
        except TMDbException as e:      raise Failed(f"TMDb Error: No Movie found for TMDb ID {tmdb_id}: {e}")

    def get_show(self, tmdb_id):
        try:                            return self.TMDb.tv_show(tmdb_id)
        except TMDbException as e:      raise Failed(f"TMDb Error: No Show found for TMDb ID {tmdb_id}: {e}")

    def get_collection(self, tmdb_id):
        try:                            return self.TMDb.collection(tmdb_id)
        except TMDbException as e:      raise Failed(f"TMDb Error: No Collection found for TMDb ID {tmdb_id}: {e}")

    def get_person(self, tmdb_id):
        try:                            return self.TMDb.person(tmdb_id)
        except TMDbException as e:      raise Failed(f"TMDb Error: No Person found for TMDb ID {tmdb_id}: {e}")

    def _company(self, tmdb_id):
        try:                            return self.TMDb.company(tmdb_id)
        except TMDbException as e:      raise Failed(f"TMDb Error: No Company found for TMDb ID {tmdb_id}: {e}")

    def _network(self, tmdb_id):
        try:                            return self.TMDb.network(tmdb_id)
        except TMDbException as e:      raise Failed(f"TMDb Error: No Network found for TMDb ID {tmdb_id}: {e}")

    def _keyword(self, tmdb_id):
        try:                            return self.TMDb.keyword(tmdb_id)
        except TMDbException as e:      raise Failed(f"TMDb Error: No Keyword found for TMDb ID {tmdb_id}: {e}")

    def get_list(self, tmdb_id):
        try:                            return self.TMDb.list(tmdb_id)
        except TMDbException as e:      raise Failed(f"TMDb Error: No List found for TMDb ID {tmdb_id}: {e}")

    def validate_tmdb_ids(self, tmdb_ids, tmdb_method):
        tmdb_list = util.get_int_list(tmdb_ids, f"TMDb {type_map[tmdb_method]} ID")
        tmdb_values = []
        for tmdb_id in tmdb_list:
            try:                                        tmdb_values.append(self.validate_tmdb(tmdb_id, tmdb_method))
            except Failed as e:                         logger.error(e)
        if len(tmdb_values) == 0:                   raise Failed(f"TMDb Error: No valid TMDb IDs in {tmdb_list}")
        return tmdb_values

    def validate_tmdb(self, tmdb_id, tmdb_method):
        tmdb_type = type_map[tmdb_method]
        if tmdb_type == "Movie":                    self.get_movie(tmdb_id)
        elif tmdb_type == "Show":                   self.get_show(tmdb_id)
        elif tmdb_type == "Collection":             self.get_collection(tmdb_id)
        elif tmdb_type == "Person":                 self.get_person(tmdb_id)
        elif tmdb_type == "Company":                self._company(tmdb_id)
        elif tmdb_type == "Network":                self._network(tmdb_id)
        elif tmdb_type == "Keyword":                self._keyword(tmdb_id)
        elif tmdb_type == "List":                   self.get_list(tmdb_id)
        return tmdb_id

    def get_tmdb_ids(self, method, data, is_movie):
        pretty = method.replace("_", " ").title().replace("Tmdb", "TMDb")
        media_type = "Movie" if is_movie else "Show"
        result_type = "tmdb" if is_movie else "tmdb_show"
        ids = []
        if method in ["tmdb_network", "tmdb_company", "tmdb_keyword"]:
            if method == "tmdb_company":
                item = self._company(int(data))
            elif method == "tmdb_network":
                item = self._network(int(data))
            else:
                item = self._keyword(int(data))
            results = item.movies if is_movie else item.tv_shows
            ids = [(i.id, result_type) for i in results.get_results(results.total_results)]
            logger.info(f"Processing {pretty}: ({data}) {item.name} ({len(results)} {media_type}{'' if len(results) == 1 else 's'})")
        elif method == "tmdb_discover":
            attrs = data.copy()
            limit = int(attrs.pop("limit"))
            for date_attr in discover_dates:
                if date_attr in attrs:
                    attrs[date_attr] = util.validate_date(attrs[date_attr], f"tmdb_discover attribute {date_attr}", return_as="%Y-%m-%d")
            if self.config.trace_mode:
                logger.debug(f"Params: {attrs}")
            results = self.TMDb.discover_movies(**attrs) if is_movie else self.TMDb.discover_tv_shows(**attrs)
            amount = results.total_results if limit == 0 or results.total_results < limit else limit
            ids = [(i.id, result_type) for i in results.get_results(amount)]
            logger.info(f"Processing {pretty}: {amount} {media_type}{'' if amount == 1 else 's'}")
            for attr, value in attrs.items():
                logger.info(f"           {attr}: {value}")
        elif method in ["tmdb_popular", "tmdb_top_rated", "tmdb_now_playing", "tmdb_trending_daily", "tmdb_trending_weekly"]:
            if method == "tmdb_popular":
                results = self.TMDb.popular_movies() if is_movie else self.TMDb.popular_tv()
            elif method == "tmdb_top_rated":
                results = self.TMDb.top_rated_movies() if is_movie else self.TMDb.top_rated_tv()
            elif method == "tmdb_now_playing":
                results = self.TMDb.now_playing_movies()
            else:
                results = self.TMDb.trending("movie" if is_movie else "tv", "day" if method == "tmdb_trending_daily" else "week")
            ids = [(i.id, result_type) for i in results.get_results(data)]
            logger.info(f"Processing {pretty}: {data} {media_type}{'' if data == 1 else 's'}")
        else:
            tmdb_id = int(data)
            if method == "tmdb_list":
                results = self.get_list(tmdb_id)
                tmdb_name = results.name
                ids = [(i.id, result_type) for i in results.get_results(results.total_results)]
            elif method == "tmdb_movie":
                tmdb_name = self.get_movie(tmdb_id).title
                ids.append((tmdb_id, "tmdb"))
            elif method == "tmdb_collection":
                collection = self.get_collection(tmdb_id)
                tmdb_name = collection.name
                ids = [(t.id, "tmdb") for t in collection.movies]
            elif method == "tmdb_show":
                tmdb_name = self.get_show(tmdb_id).name
                ids.append((tmdb_id, "tmdb_show"))
            else:
                person = self.get_person(tmdb_id)
                tmdb_name = person.name
                if method == "tmdb_actor":
                    ids = [(i.id, "tmdb") for i in person.movie_cast]
                    ids.extend([(i.id, "tmdb_show") for i in person.tv_cast])
                elif method == "tmdb_crew":
                    ids = [(i.id, "tmdb") for i in person.movie_crew]
                    ids.extend([(i.id, "tmdb_show") for i in person.tv_crew])
                elif method == "tmdb_director":
                    ids = [(i.id, "tmdb") for i in person.movie_crew if i.department == "Directing"]
                    ids.extend([(i.id, "tmdb_show") for i in person.tv_crew])
                elif method == "tmdb_writer":
                    ids = [(i.id, "tmdb") for i in person.movie_crew if i.department == "Writing"]
                    ids.extend([(i.id, "tmdb_show") for i in person.tv_crew])
                elif method == "tmdb_producer":
                    ids = [(i.id, "tmdb") for i in person.movie_crew if i.department == "Production"]
                    ids.extend([(i.id, "tmdb_show") for i in person.tv_crew])
                else:
                    raise Failed(f"TMDb Error: Method {method} not supported")
            if len(ids) > 0:
                logger.info(f"Processing {pretty}: ({tmdb_id}) {tmdb_name} ({len(ids)} Item{'' if len(ids) == 1 else 's'})")
        return ids
