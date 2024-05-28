import re
from modules import util
from modules.util import Failed
from retrying import retry
from tmdbapis import TMDbAPIs, TMDbException, NotFound, Movie

logger = util.logger

int_builders = [
    "tmdb_airing_today", "tmdb_popular", "tmdb_top_rated", "tmdb_now_playing", "tmdb_on_the_air",
    "tmdb_trending_daily", "tmdb_trending_weekly", "tmdb_upcoming"
]
info_builders = [
    "tmdb_actor", "tmdb_collection", "tmdb_crew", "tmdb_director", "tmdb_list",
    "tmdb_movie", "tmdb_producer", "tmdb_show", "tmdb_writer"
]
details_builders = [f"{d}_details" for d in info_builders]
builders = ["tmdb_company", "tmdb_discover", "tmdb_keyword", "tmdb_network"] \
           + int_builders + info_builders + details_builders
type_map = {
    "tmdb_actor": "Person", "tmdb_actor_details": "Person", "tmdb_crew": "Person", "tmdb_crew_details": "Person",
    "tmdb_collection": "Collection", "tmdb_collection_details": "Collection", "tmdb_company": "Company",
    "tmdb_director": "Person", "tmdb_director_details": "Person", "tmdb_keyword": "Keyword",
    "tmdb_list": "List", "tmdb_list_details": "List", "tmdb_movie": "Movie", "tmdb_movie_details": "Movie",
    "tmdb_network": "Network", "tmdb_person": "Person", "tmdb_producer": "Person", "tmdb_producer_details": "Person",
    "tmdb_show": "Show", "tmdb_show_details": "Show", "tmdb_writer": "Person", "tmdb_writer_details": "Person"
}
discover_movie_only = [
    "region", "with_cast", "with_crew", "with_people", "certification_country", "certification", "include_video", "year",
    "primary_release_year", "primary_release_date", "release_date", "include_adult", "with_release_type", "with_title_translation"
]
discover_tv_only = [
    "timezone", "screened_theatrically", "include_null_first_air_dates", "air_date", "first_air_date",
    "first_air_date_year", "with_networks", "with_status", "with_type", "with_name_translation"
]
discover_strings = [
    "with_cast", "with_crew", "with_people", "with_companies", "without_companies", "with_networks", "with_genres",
    "without_genres", "with_release_type", "with_keywords", "without_keywords", "with_original_language", "timezone",
    "with_watch_providers", "without_watch_providers", "with_overview_translation", "with_title_translation", "with_name_translation"
]
discover_ints = ["vote_count", "with_runtime"]
modifiers = [".gte", ".lte"]
discover_years = ["primary_release_year", "year", "first_air_date_year"]
discover_booleans = ["include_adult", "include_video", "include_null_first_air_dates", "screened_theatrically"]
discover_dates = ["primary_release_date", "release_date", "air_date", "first_air_date"]
date_methods = [f"{f}{m}" for f in discover_dates for m in modifiers]
discover_numbers = ["vote_average"]
discover_special = [
    "region", "sort_by", "certification_country", "certification", "certification.lte", "certification.gte",
    "watch_region", "with_watch_monetization_types", "with_status", "limit", "with_type"
]
discover_all = discover_special + discover_strings + discover_years + discover_booleans + date_methods + \
      [f"{f}{m}" for f in discover_ints for m in modifiers] + \
      [f"{f}{m}" for f in discover_numbers for m in modifiers]
discover_movie_sort = [
    "popularity.asc", "popularity.desc", "release_date.asc", "release_date.desc", "revenue.asc", "revenue.desc",
    "primary_release_date.asc", "primary_release_date.desc", "original_title.asc", "original_title.desc",
    "vote_average.asc", "vote_average.desc", "vote_count.asc", "vote_count.desc"
]
discover_tv_sort = ["vote_average.desc", "vote_average.asc", "first_air_date.desc", "first_air_date.asc", "popularity.desc", "popularity.asc"]
discover_monetization_types = ["flatrate", "free", "ads", "rent", "buy"]
discover_types = {
    "Documentary": "documentary", "News": "news", "Miniseries": "miniseries",
    "Reality": "reality", "Scripted": "scripted", "Talk Show": "talk_show", "Video": "video"
}
discover_status = {
    "Returning Series": "returning", "Planned": "planned", "In Production": "production",
    "Ended": "ended", "Canceled": "canceled", "Pilot": "pilot"
}

class TMDbCountry:
    def __init__(self, data):
        self.iso_3166_1 = data.split(":")[0] if isinstance(data, str) else data.iso_3166_1
        self.name = data.split(":")[1] if isinstance(data, str) else data.name

    def __repr__(self):
        return f"{self.iso_3166_1}:{self.name}"


class TMDbSeason:
    def __init__(self, data):
        self.season_number = int(data.split("%:%")[0]) if isinstance(data, str) else data.season_number
        self.name = data.split("%:%")[1] if isinstance(data, str) else data.name
        self.average = float(data.split("%:%")[2]) if isinstance(data, str) else data.vote_average

    def __repr__(self):
        return f"{self.season_number}%:%{self.name}%:%{self.average}"


class TMDBObj:
    def __init__(self, tmdb, tmdb_id, ignore_cache=False):
        self._tmdb = tmdb
        self.tmdb_id = tmdb_id
        self.ignore_cache = ignore_cache

    def _load(self, data):
        self.title = data["title"] if isinstance(data, dict) else data.title
        self.tagline = data["tagline"] if isinstance(data, dict) else data.tagline
        self.overview = data["overview"] if isinstance(data, dict) else data.overview
        self.imdb_id = data["imdb_id"] if isinstance(data, dict) else data.imdb_id
        self.poster_url = data["poster_url"] if isinstance(data, dict) else data.poster_url
        self.backdrop_url = data["backdrop_url"] if isinstance(data, dict) else data.backdrop_url
        self.vote_count = data["vote_count"] if isinstance(data, dict) else data.vote_count
        self.vote_average = data["vote_average"] if isinstance(data, dict) else data.vote_average
        self.language_iso = data["language_iso"] if isinstance(data, dict) else data.original_language.iso_639_1 if data.original_language else None
        self.language_name = data["language_name"] if isinstance(data, dict) else data.original_language.english_name if data.original_language else None
        self.genres = [g for g in data["genres"].split("|") if g] if isinstance(data, dict) else [g.name for g in data.genres if g]
        self.keywords = [k for k in data["keywords"].split("|") if k] if isinstance(data, dict) else [k.name for k in data.keywords if k]


class TMDbMovie(TMDBObj):
    def __init__(self, tmdb, tmdb_id, ignore_cache=False):
        super().__init__(tmdb, tmdb_id, ignore_cache=ignore_cache)
        expired = None
        data = None
        if self._tmdb.cache and not ignore_cache:
            data, expired = self._tmdb.cache.query_tmdb_movie(tmdb_id, self._tmdb.expiration)
        if expired or not data:
            data = self.load_movie()
        super()._load(data)

        self.original_title = data["original_title"] if isinstance(data, dict) else data.original_title
        self.release_date = data["release_date"] if isinstance(data, dict) else data.release_date
        self.studio = data["studio"] if isinstance(data, dict) else data.companies[0].name if data.companies else None
        self.collection_id = data["collection_id"] if isinstance(data, dict) else data.collection.id if data.collection else None
        self.collection_name = data["collection_name"] if isinstance(data, dict) else data.collection.name if data.collection else None

        if self._tmdb.cache and not ignore_cache:
            self._tmdb.cache.update_tmdb_movie(expired, self, self._tmdb.expiration)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def load_movie(self):
        try:
            return self._tmdb.TMDb.movie(self.tmdb_id, partial="external_ids,keywords")
        except NotFound:
            raise Failed(f"TMDb Error: No Movie found for TMDb ID: {self.tmdb_id}")
        except TMDbException as e:
            logger.stacktrace()
            raise TMDbException(f"TMDb Error: Unexpected Error with TMDb ID: {self.tmdb_id}: {e}")


class TMDbShow(TMDBObj):
    def __init__(self, tmdb, tmdb_id, ignore_cache=False):
        super().__init__(tmdb, tmdb_id, ignore_cache=ignore_cache)
        expired = None
        data = None
        if self._tmdb.cache and not ignore_cache:
            data, expired = self._tmdb.cache.query_tmdb_show(tmdb_id, self._tmdb.expiration)
        if expired or not data:
            data = self.load_show()
        super()._load(data)

        self.original_title = data["original_title"] if isinstance(data, dict) else data.original_name
        self.first_air_date = data["first_air_date"] if isinstance(data, dict) else data.first_air_date
        self.last_air_date = data["last_air_date"] if isinstance(data, dict) else data.last_air_date
        self.status = data["status"] if isinstance(data, dict) else data.status
        self.type = data["type"] if isinstance(data, dict) else data.type
        self.studio = data["studio"] if isinstance(data, dict) else data.networks[0].name if data.networks else None
        self.tvdb_id = data["tvdb_id"] if isinstance(data, dict) else data.tvdb_id
        loop = data.origin_countries if not isinstance(data, dict) else data["countries"].split("|") if data["countries"] else [] # noqa
        self.countries = [TMDbCountry(c) for c in loop]
        loop = data.seasons if not isinstance(data, dict) else data["seasons"].split("%|%") if data["seasons"] else [] # noqa
        self.seasons = [TMDbSeason(s) for s in loop]

        if self._tmdb.cache and not ignore_cache:
            self._tmdb.cache.update_tmdb_show(expired, self, self._tmdb.expiration)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def load_show(self):
        try:
            return self._tmdb.TMDb.tv_show(self.tmdb_id, partial="external_ids,keywords")
        except NotFound:
            raise Failed(f"TMDb Error: No Show found for TMDb ID: {self.tmdb_id}")
        except TMDbException as e:
            logger.stacktrace()
            raise TMDbException(f"TMDb Error: Unexpected Error with TMDb ID: {self.tmdb_id}: {e}")

class TMDbEpisode:
    def __init__(self, tmdb, tmdb_id, season_number, episode_number, ignore_cache=False):
        self._tmdb = tmdb
        self.tmdb_id = tmdb_id
        self.season_number = season_number
        self.episode_number = episode_number
        self.ignore_cache = ignore_cache
        expired = None
        data = None
        if self._tmdb.cache and not ignore_cache:
            data, expired = self._tmdb.cache.query_tmdb_episode(self.tmdb_id, self.season_number, self.episode_number, self._tmdb.expiration)
        if expired or not data:
            data = self.load_episode()

        self.title = data["title"] if isinstance(data, dict) else data.title
        self.air_date = data["air_date"] if isinstance(data, dict) else data.air_date
        self.overview = data["overview"] if isinstance(data, dict) else data.overview
        self.still_url = data["still_url"] if isinstance(data, dict) else data.still_url
        self.vote_count = data["vote_count"] if isinstance(data, dict) else data.vote_count
        self.vote_average = data["vote_average"] if isinstance(data, dict) else data.vote_average
        self.imdb_id = data["imdb_id"] if isinstance(data, dict) else data.imdb_id
        self.tvdb_id = data["tvdb_id"] if isinstance(data, dict) else data.tvdb_id

        if self._tmdb.cache and not ignore_cache:
            self._tmdb.cache.update_tmdb_episode(expired, self, self._tmdb.expiration)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def load_episode(self):
        try:
            return self._tmdb.TMDb.tv_episode(self.tmdb_id, self.season_number, self.episode_number)
        except NotFound as e:
            raise Failed(f"TMDb Error: No Episode found for TMDb ID {self.tmdb_id} Season {self.season_number} Episode {self.episode_number}: {e}")
        except TMDbException as e:
            logger.stacktrace()
            raise TMDbException(f"TMDb Error: Unexpected Error with TMDb ID: {self.tmdb_id}: {e}")


class TMDb:
    def __init__(self, config, params):
        self.config = config
        self.requests = self.config.Requests
        self.cache = self.config.Cache
        self.apikey = params["apikey"]
        self.language = params["language"]
        self.region = None
        self.expiration = params["expiration"]
        logger.secret(self.apikey)
        try:
            self.TMDb = TMDbAPIs(self.apikey, language=self.language, session=self.requests.session)
        except TMDbException as e:
            raise Failed(f"TMDb Error: {e}")
        self.iso_3166_1 = {iso: i.name for iso, i in self.TMDb._iso_3166_1.items()} # noqa

    def convert_from(self, tmdb_id, convert_to, is_movie):
        item = self.get_movie(tmdb_id) if is_movie else self.get_show(tmdb_id)
        check_id = item.tvdb_id if convert_to == "tvdb_id" and not is_movie else item.imdb_id
        if not check_id:
            raise Failed(f"TMDb Error: No {convert_to.upper().replace('B_', 'b ')} found for TMDb ID {tmdb_id}")
        return check_id

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def convert_tvdb_to(self, tvdb_id):
        try:
            results = self.TMDb.find_by_id(tvdb_id=tvdb_id)
            if results.tv_results:
                return results.tv_results[0].id
        except NotFound:
            pass
        raise Failed(f"TMDb Error: No TMDb ID found for TVDb ID {tvdb_id}")

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
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
        except NotFound:
            pass
        raise Failed(f"TMDb Error: No TMDb ID found for IMDb ID {imdb_id}")

    def get_movie_show_or_collection(self, tmdb_id, is_movie):
        if is_movie:
            try:                            return self.get_collection(tmdb_id)
            except Failed:
                try:                            return self.get_movie(tmdb_id)
                except Failed:                  raise Failed(f"TMDb Error: No Movie or Collection found for TMDb ID {tmdb_id}")
        else:                           return self.get_show(tmdb_id)

    def get_movie(self, tmdb_id, ignore_cache=False):
        return TMDbMovie(self, tmdb_id, ignore_cache=ignore_cache)

    def get_show(self, tmdb_id, ignore_cache=False):
        return TMDbShow(self, tmdb_id, ignore_cache=ignore_cache)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def get_season(self, tmdb_id, season_number, partial=None):
        try:                            return self.TMDb.tv_season(tmdb_id, season_number, partial=partial)
        except NotFound as e:           raise Failed(f"TMDb Error: No Season found for TMDb ID {tmdb_id} Season {season_number}: {e}")

    def get_episode(self, tmdb_id, season_number, episode_number, ignore_cache=False):
        return TMDbEpisode(self, tmdb_id, season_number, episode_number, ignore_cache=ignore_cache)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def get_collection(self, tmdb_id, partial=None):
        try:                            return self.TMDb.collection(tmdb_id, partial=partial)
        except NotFound as e:           raise Failed(f"TMDb Error: No Collection found for TMDb ID {tmdb_id}: {e}")

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def get_person(self, tmdb_id, partial=None):
        try:                            return self.TMDb.person(tmdb_id, partial=partial)
        except NotFound as e:           raise Failed(f"TMDb Error: No Person found for TMDb ID {tmdb_id}: {e}")

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def _company(self, tmdb_id, partial=None):
        try:                            return self.TMDb.company(tmdb_id, partial=partial)
        except NotFound as e:           raise Failed(f"TMDb Error: No Company found for TMDb ID {tmdb_id}: {e}")

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def _network(self, tmdb_id, partial=None):
        try:                            return self.TMDb.network(tmdb_id, partial=partial)
        except NotFound as e:           raise Failed(f"TMDb Error: No Network found for TMDb ID {tmdb_id}: {e}")

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def _keyword(self, tmdb_id):
        try:                            return self.TMDb.keyword(tmdb_id)
        except NotFound as e:           raise Failed(f"TMDb Error: No Keyword found for TMDb ID {tmdb_id}: {e}")

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def get_list(self, tmdb_id):
        try:                            return self.TMDb.list(tmdb_id)
        except NotFound as e:           raise Failed(f"TMDb Error: No List found for TMDb ID {tmdb_id}: {e}")

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def get_popular_people(self, limit):
        return {str(p.id): p.name for p in self.TMDb.popular_people().get_results(limit)}

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def search_people(self, name):
        try:                            return self.TMDb.people_search(name)
        except NotFound:                raise Failed(f"TMDb Error: Actor {name} Not Found")

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

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def get_items(self, method, data, region, is_movie, result_type):
        if method == "tmdb_popular":
            results = self.TMDb.popular_movies(region=region) if is_movie else self.TMDb.popular_tv()
        elif method == "tmdb_top_rated":
            results = self.TMDb.top_rated_movies(region=region) if is_movie else self.TMDb.top_rated_tv()
        elif method == "tmdb_now_playing":
            results = self.TMDb.now_playing_movies(region=region)
        elif method == "tmdb_upcoming":
            results = self.TMDb.upcoming_movies(region=region)
        elif method == "tmdb_airing_today":
            results = self.TMDb.tv_airing_today()
        elif method == "tmdb_on_the_air":
            results = self.TMDb.tv_on_the_air()
        else:
            results = self.TMDb.trending("movie" if is_movie else "tv", "day" if method == "tmdb_trending_daily" else "week")
        return [(i.id, result_type) for i in results.get_results(data)]

    def get_tmdb_ids(self, method, data, is_movie, region):
        if not region and self.region:
            region = self.region
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
            for date_attr in date_methods:
                if date_attr in attrs:
                    try:
                        attrs[date_attr] = util.validate_date(attrs[date_attr], return_as="%Y-%m-%d")
                    except Failed as e:
                        raise Failed(f"Collection Error: tmdb_discover attribute {date_attr}: {e}")
            if is_movie and region and "region" not in attrs:
                attrs["region"] = region
            logger.trace(f"Params: {attrs}")
            results = self.TMDb.discover_movies(**attrs) if is_movie else self.TMDb.discover_tv_shows(**attrs)
            amount = results.total_results if limit == 0 or results.total_results < limit else limit
            ids = [(i.id, result_type) for i in results.get_results(amount)]
            logger.info(f"Processing {pretty}: {amount} {media_type}{'' if amount == 1 else 's'}")
            for attr, value in attrs.items():
                logger.info(f"           {attr}: {value}")
        elif method in int_builders:
            ids = self.get_items(method, data, region, is_movie, result_type)
            logger.info(f"Processing {pretty}: {data} {media_type}{'' if data == 1 else 's'}")
        else:
            tmdb_id = int(data)
            if method == "tmdb_list":
                results = self.get_list(tmdb_id)
                tmdb_name = results.name
                ids = [(i.id, "tmdb" if isinstance(i, Movie) else "tmdb_show") for i in results.get_results()]
            elif method == "tmdb_movie":
                tmdb_name = self.get_movie(tmdb_id).title
                ids.append((tmdb_id, "tmdb"))
            elif method == "tmdb_collection":
                collection = self.get_collection(tmdb_id)
                tmdb_name = collection.name
                ids = [(t.id, "tmdb") for t in collection.movies]
            elif method == "tmdb_show":
                tmdb_name = self.get_show(tmdb_id).title
                ids.append((tmdb_id, "tmdb_show"))
            else:
                person = self.get_person(tmdb_id, partial="movie_credits,tv_credits")
                tmdb_name = person.name
                if method == "tmdb_actor":
                    ids = [(i.movie.id, "tmdb") for i in person.movie_cast]
                    ids.extend([(i.tv_show.id, "tmdb_show") for i in person.tv_cast])
                elif method == "tmdb_crew":
                    ids = [(i.movie.id, "tmdb") for i in person.movie_crew]
                    ids.extend([(i.tv_show.id, "tmdb_show") for i in person.tv_crew])
                elif method == "tmdb_director":
                    ids = [(i.movie.id, "tmdb") for i in person.movie_crew if i.department == "Directing"]
                    ids.extend([(i.tv_show.id, "tmdb_show") for i in person.tv_crew if i.department == "Directing"])
                elif method == "tmdb_writer":
                    ids = [(i.movie.id, "tmdb") for i in person.movie_crew if i.department == "Writing"]
                    ids.extend([(i.tv_show.id, "tmdb_show") for i in person.tv_crew if i.department == "Writing"])
                elif method == "tmdb_producer":
                    ids = [(i.movie.id, "tmdb") for i in person.movie_crew if i.department == "Production"]
                    ids.extend([(i.tv_show.id, "tmdb_show") for i in person.tv_crew if i.department == "Production"])
                else:
                    raise Failed(f"TMDb Error: Method {method} not supported")
            if len(ids) > 0:
                logger.info(f"Processing {pretty}: ({tmdb_id}) {tmdb_name} ({len(ids)} Item{'' if len(ids) == 1 else 's'})")
        return ids

    def get_item(self, item, tmdb_id, tvdb_id, imdb_id, is_movie=True):
        tmdb_item = None
        if tvdb_id and not tmdb_id:
            tmdb_id = self.config.Convert.tvdb_to_tmdb(tvdb_id)
        if imdb_id and not tmdb_id:
            _id, _type = self.config.Convert.imdb_to_tmdb(imdb_id)
            if _id and ((_type == "movie" and is_movie) or (_type == "show" and not is_movie)):
                tmdb_id = _id
        if tmdb_id:
            try:
                tmdb_item = self.get_movie(tmdb_id) if is_movie else self.get_show(tmdb_id)
            except Failed as e:
                logger.error(str(e))
        elif tvdb_id and not is_movie:
            logger.info(f"{item.title[:25]:<25} | No TMDb ID for TVDb ID: {tvdb_id}")
        elif imdb_id:
            logger.info(f"{item.title[:25]:<25} | No TMDb ID for IMDb ID: {imdb_id}")
        else:
            logger.info(f"{item.title[:25]:<25} | No TMDb ID for Guid: {item.guid}")
        return tmdb_item

    def item_filter(self, item, filter_attr, modifier, filter_final, filter_data, is_movie, current_time):
        if filter_attr in ["tmdb_status", "tmdb_type", "original_language"]:
            if filter_attr == "tmdb_status":
                check_value = discover_status[item.status]
            elif filter_attr == "tmdb_type":
                check_value = discover_types[item.type]
            elif filter_attr == "original_language":
                check_value = item.language_iso
            else:
                raise Failed
            if (modifier == ".not" and check_value in filter_data) or (modifier == "" and check_value not in filter_data):
                return False
        elif filter_attr in ["first_episode_aired", "last_episode_aired", "last_episode_aired_or_never"]:
            tmdb_date = None
            if filter_attr == "first_episode_aired":
                tmdb_date = item.first_air_date
            elif filter_attr in ["last_episode_aired", "last_episode_aired_or_never"]:
                tmdb_date = item.last_air_date

                # tmdb_date is empty if never aired yet
                if tmdb_date is None and filter_attr == "last_episode_aired_or_never":
                    return True
            if util.is_date_filter(tmdb_date, modifier, filter_data, filter_final, current_time):
                return False
        elif modifier in [".gt", ".gte", ".lt", ".lte"]:
            attr = None
            if filter_attr == "tmdb_vote_count":
                attr = item.vote_count
            elif filter_attr == "tmdb_vote_average":
                attr = item.vote_average
            elif filter_attr == "tmdb_year":
                attr = item.release_date.year if is_movie else item.first_air_date.year
            if util.is_number_filter(attr, modifier, filter_data):
                return False
        elif filter_attr in ["tmdb_genre", "tmdb_keyword", "origin_country"]:
            if filter_attr == "tmdb_genre":
                attrs = item.genres
            elif filter_attr == "tmdb_keyword":
                attrs = item.keywords
            elif filter_attr == "origin_country":
                attrs = [c.iso_3166_1 for c in item.countries]
            else:
                raise Failed
            if modifier == ".regex":
                has_match = False
                for reg in filter_data:
                    for name in attrs:
                        if re.compile(reg).search(name):
                            has_match = True
                if has_match is False:
                    return False
            elif modifier in [".count_gt", ".count_gte", ".count_lt", ".count_lte"]:
                test_number = len(attrs) if attrs else 0
                modifier = f".{modifier[7:]}"
                if test_number is None or util.is_number_filter(test_number, modifier, filter_data):
                    return False
            elif (not list(set(filter_data) & set(attrs)) and modifier == "") \
                    or (list(set(filter_data) & set(attrs)) and modifier == ".not"):
                return False
        elif filter_attr == "tmdb_title":
            if util.is_string_filter([item.title], modifier, filter_data):
                return False
        return True
