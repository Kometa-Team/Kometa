import logging, tmdbv3api
from modules import util
from modules.util import Failed
from retrying import retry
from tmdbv3api.exceptions import TMDbException

logger = logging.getLogger("Plex Meta Manager")

class TMDbAPI:
    def __init__(self, params):
        self.TMDb = tmdbv3api.TMDb()
        self.TMDb.api_key = params["apikey"]
        self.TMDb.language = params["language"]
        response = tmdbv3api.Configuration().info()
        if hasattr(response, "status_message"):
            raise Failed(f"TMDb Error: {response.status_message}")
        self.apikey = params["apikey"]
        self.language = params["language"]
        self.Movie = tmdbv3api.Movie()
        self.TV = tmdbv3api.TV()
        self.Discover = tmdbv3api.Discover()
        self.Trending = tmdbv3api.Trending()
        self.Keyword = tmdbv3api.Keyword()
        self.List = tmdbv3api.List()
        self.Company = tmdbv3api.Company()
        self.Network = tmdbv3api.Network()
        self.Collection = tmdbv3api.Collection()
        self.Person = tmdbv3api.Person()
        self.image_url = "https://image.tmdb.org/t/p/original"

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def convert_from_tmdb(self, tmdb_id, convert_to, is_movie):
        try:
            id_to_return = self.Movie.external_ids(tmdb_id)[convert_to] if is_movie else self.TV.external_ids(tmdb_id)[convert_to]
            if not id_to_return or (convert_to == "tvdb_id" and id_to_return == 0):
                raise Failed(f"TMDb Error: No {convert_to.upper().replace('B_', 'b ')} found for TMDb ID {tmdb_id}")
            return id_to_return
        except TMDbException:
            raise Failed(f"TMDb Error: {'Movie' if is_movie else 'Show'} TMDb ID: {tmdb_id} not found")

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def convert_to_tmdb(self, external_id, external_source, is_movie):
        search_results = self.Movie.external(external_id=external_id, external_source=external_source)
        search = search_results["movie_results" if is_movie else "tv_results"]
        if len(search) == 1:        return int(search[0]["id"])
        else:                       raise Failed(f"TMDb Error: No TMDb ID found for {external_source.upper().replace('B_', 'b ')} {external_id}")

    def convert_tmdb_to_imdb(self, tmdb_id, is_movie=True):         return self.convert_from_tmdb(tmdb_id, "imdb_id", is_movie)
    def convert_imdb_to_tmdb(self, imdb_id, is_movie=True):         return self.convert_to_tmdb(imdb_id, "imdb_id", is_movie)
    def convert_tmdb_to_tvdb(self, tmdb_id):                        return self.convert_from_tmdb(tmdb_id, "tvdb_id", False)
    def convert_tvdb_to_tmdb(self, tvdb_id):                        return self.convert_to_tmdb(tvdb_id, "tvdb_id", False)
    def convert_tvdb_to_imdb(self, tvdb_id):                        return self.convert_tmdb_to_imdb(self.convert_tvdb_to_tmdb(tvdb_id), False)
    def convert_imdb_to_tvdb(self, imdb_id):                        return self.convert_tmdb_to_tvdb(self.convert_imdb_to_tmdb(imdb_id, False))

    def get_movie_show_or_collection(self, tmdb_id, is_movie):
        if is_movie:
            try:                            return self.get_collection(tmdb_id)
            except Failed:
                try:                            return self.get_movie(tmdb_id)
                except Failed:                  raise Failed(f"TMDb Error: No Movie or Collection found for TMDb ID {tmdb_id}")
        else:                           return self.get_show(tmdb_id)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def get_movie(self, tmdb_id):
        try:                            return self.Movie.details(tmdb_id)
        except TMDbException as e:      raise Failed(f"TMDb Error: No Movie found for TMDb ID {tmdb_id}: {e}")

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def get_show(self, tmdb_id):
        try:                            return self.TV.details(tmdb_id)
        except TMDbException as e:      raise Failed(f"TMDb Error: No Show found for TMDb ID {tmdb_id}: {e}")

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def get_collection(self, tmdb_id):
        try:                            return self.Collection.details(tmdb_id)
        except TMDbException as e:      raise Failed(f"TMDb Error: No Collection found for TMDb ID {tmdb_id}: {e}")

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def get_person(self, tmdb_id):
        try:                            return self.Person.details(tmdb_id)
        except TMDbException as e:      raise Failed(f"TMDb Error: No Person found for TMDb ID {tmdb_id}: {e}")

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def get_company(self, tmdb_id):
        try:                            return self.Company.details(tmdb_id)
        except TMDbException as e:      raise Failed(f"TMDb Error: No Company found for TMDb ID {tmdb_id}: {e}")

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def get_network(self, tmdb_id):
        try:                            return self.Network.details(tmdb_id)
        except TMDbException as e:      raise Failed(f"TMDb Error: No Network found for TMDb ID {tmdb_id}: {e}")

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def get_keyword(self, tmdb_id):
        try:                            return self.Keyword.details(tmdb_id)
        except TMDbException as e:      raise Failed(f"TMDb Error: No Keyword found for TMDb ID {tmdb_id}: {e}")

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def get_list(self, tmdb_id):
        try:                            return self.List.details(tmdb_id, all_details=True)
        except TMDbException as e:      raise Failed(f"TMDb Error: No List found for TMDb ID {tmdb_id}: {e}")

    def get_pagenation(self, method, amount, is_movie):
        ids = []
        count = 0
        for x in range(int(amount / 20) + 1):
            if method == "tmdb_popular":                        tmdb_items = self.Movie.popular(x + 1) if is_movie else self.TV.popular(x + 1)
            elif method == "tmdb_top_rated":                    tmdb_items = self.Movie.top_rated(x + 1) if is_movie else self.TV.top_rated(x + 1)
            elif method == "tmdb_now_playing" and is_movie:     tmdb_items = self.Movie.now_playing(x + 1)
            elif method == "tmdb_trending_daily":               tmdb_items = self.Trending.movie_day(x + 1) if is_movie else self.Trending.tv_day(x + 1)
            elif method == "tmdb_trending_weekly":              tmdb_items = self.Trending.movie_week(x + 1) if is_movie else self.Trending.tv_week(x + 1)
            else:                                               raise Failed(f"TMDb Error: {method} method not supported")
            for tmdb_item in tmdb_items:
                try:
                    ids.append(tmdb_item.id if is_movie else self.convert_tmdb_to_tvdb(tmdb_item.id))
                    count += 1
                except Failed:
                    pass
                if count == amount: break
            if count == amount: break
        return ids

    def get_discover(self, attrs, amount, is_movie):
        ids = []
        count = 0
        self.Discover.discover_movies(attrs) if is_movie else self.Discover.discover_tv_shows(attrs)
        total_pages = int(self.TMDb.total_pages)
        total_results = int(self.TMDb.total_results)
        amount = total_results if amount == 0 or total_results < amount else amount
        for x in range(total_pages):
            attrs["page"] = x + 1
            tmdb_items = self.Discover.discover_movies(attrs) if is_movie else self.Discover.discover_tv_shows(attrs)
            for tmdb_item in tmdb_items:
                try:
                    ids.append(tmdb_item.id if is_movie else self.convert_tmdb_to_tvdb(tmdb_item.id))
                    count += 1
                except Failed:
                    pass
                if count == amount: break
            if count == amount: break
        return ids, amount

    def get_items(self, method, data, is_movie, status_message=True):
        if status_message:
            logger.debug(f"Data: {data}")
        pretty = util.pretty_names[method] if method in util.pretty_names else method
        media_type = "Movie" if is_movie else "Show"
        movie_ids = []
        show_ids = []
        if method in ["tmdb_discover", "tmdb_company", "tmdb_keyword"] or (method == "tmdb_network" and not is_movie):
            attrs = None
            tmdb_id = ""
            tmdb_name = ""
            if method in ["tmdb_company", "tmdb_network", "tmdb_keyword"]:
                tmdb_id = int(data)
                if method == "tmdb_company":
                    tmdb_name = str(self.get_company(tmdb_id).name)
                    attrs = {"with_companies": tmdb_id}
                elif method == "tmdb_network":
                    tmdb_name = str(self.get_network(tmdb_id).name)
                    attrs = {"with_networks": tmdb_id}
                elif method == "tmdb_keyword":
                    tmdb_name = str(self.get_keyword(tmdb_id).name)
                    attrs = {"with_keywords": tmdb_id}
                limit = 0
            else:
                attrs = data.copy()
                limit = int(attrs.pop("limit"))
            if is_movie:                    movie_ids, amount = self.get_discover(attrs, limit, is_movie)
            else:                           show_ids, amount = self.get_discover(attrs, limit, is_movie)
            if status_message:
                if method in ["tmdb_company", "tmdb_network", "tmdb_keyword"]:
                    logger.info(f"Processing {pretty}: ({tmdb_id}) {tmdb_name} ({amount} {media_type}{'' if amount == 1 else 's'})")
                elif method == "tmdb_discover":
                    logger.info(f"Processing {pretty}: {amount} {media_type}{'' if amount == 1 else 's'}")
                    for attr, value in attrs.items():
                        logger.info(f"           {attr}: {value}")
        elif method in ["tmdb_popular", "tmdb_top_rated", "tmdb_now_playing", "tmdb_trending_daily", "tmdb_trending_weekly"]:
            if is_movie:                    movie_ids = self.get_pagenation(method, data, is_movie)
            else:                           show_ids = self.get_pagenation(method, data, is_movie)
            if status_message:
                logger.info(f"Processing {pretty}: {data} {media_type}{'' if data == 1 else 's'}")
        else:
            tmdb_id = int(data)
            if method == "tmdb_list":
                tmdb_list = self.get_list(tmdb_id)
                tmdb_name = tmdb_list.name
                for tmdb_item in tmdb_list.items:
                    if tmdb_item.media_type == "movie":
                        movie_ids.append(tmdb_item.id)
                    elif tmdb_item.media_type == "tv":
                        try:                    show_ids.append(self.convert_tmdb_to_tvdb(tmdb_item.id))
                        except Failed:          pass
            elif method == "tmdb_movie":
                tmdb_name = str(self.get_movie(tmdb_id).title)
                movie_ids.append(tmdb_id)
            elif method == "tmdb_collection":
                tmdb_items = self.get_collection(tmdb_id)
                tmdb_name = str(tmdb_items.name)
                for tmdb_item in tmdb_items.parts:
                    movie_ids.append(tmdb_item["id"])
            elif method == "tmdb_show":
                tmdb_name = str(self.get_show(tmdb_id).name)
                try:                    show_ids.append(self.convert_tmdb_to_tvdb(tmdb_id))
                except Failed:          pass
            else:
                raise Failed(f"TMDb Error: Method {method} not supported")
            if status_message and len(movie_ids) > 0:
                logger.info(f"Processing {pretty}: ({tmdb_id}) {tmdb_name} ({len(movie_ids)} Movie{'' if len(movie_ids) == 1 else 's'})")
            if status_message and len(show_ids) > 0:
                logger.info(f"Processing {pretty}: ({tmdb_id}) {tmdb_name} ({len(show_ids)} Show{'' if len(show_ids) == 1 else 's'})")
        if status_message:
            logger.debug(f"TMDb IDs Found: {movie_ids}")
            logger.debug(f"TVDb IDs Found: {show_ids}")
        return movie_ids, show_ids

    def validate_tmdb_list(self, tmdb_list, tmdb_type):
        tmdb_values = []
        for tmdb_id in tmdb_list:
            try:                                        tmdb_values.append(self.validate_tmdb(tmdb_id, tmdb_type))
            except Failed as e:                         logger.error(e)
        if len(tmdb_values) == 0:                   raise Failed(f"TMDb Error: No valid TMDb IDs in {tmdb_list}")
        return tmdb_values

    def validate_tmdb(self, tmdb_id, tmdb_type):
        if tmdb_type == "Movie":                    self.get_movie(tmdb_id)
        elif tmdb_type == "Show":                   self.get_show(tmdb_id)
        elif tmdb_type == "Collection":             self.get_collection(tmdb_id)
        elif tmdb_type == "Person":                 self.get_person(tmdb_id)
        elif tmdb_type == "Company":                self.get_company(tmdb_id)
        elif tmdb_type == "Network":                self.get_network(tmdb_id)
        elif tmdb_type == "List":                   self.get_list(tmdb_id)
        return tmdb_id
