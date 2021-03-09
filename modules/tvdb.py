import logging, requests
from lxml import html
from modules import util
from modules.util import Failed
from retrying import retry

logger = logging.getLogger("Plex Meta Manager")

class TVDbObj:
    def __init__(self, tvdb_url, language, is_movie, TVDb):
        tvdb_url = tvdb_url.strip()
        if not is_movie and tvdb_url.startswith((TVDb.series_url, TVDb.alt_series_url, TVDb.series_id_url)):
            self.media_type = "Series"
        elif is_movie and tvdb_url.startswith((TVDb.movies_url, TVDb.alt_movies_url, TVDb.movie_id_url)):
            self.media_type = "Movie"
        else:
            raise Failed(f"TVDb Error: {tvdb_url} must begin with {TVDb.movies_url if is_movie else TVDb.series_url}")

        response = TVDb.send_request(tvdb_url, language)
        results = response.xpath(f"//*[text()='TheTVDB.com {self.media_type} ID']/parent::node()/span/text()")
        if len(results) > 0:
            self.id = int(results[0])
        elif tvdb_url.startswith(TVDb.movie_id_url):
            raise Failed(f"TVDb Error: Could not find a TVDb Movie using TVDb Movie ID: {tvdb_url[len(TVDb.movie_id_url):]}")
        elif tvdb_url.startswith(TVDb.series_id_url):
            raise Failed(f"TVDb Error: Could not find a TVDb Series using TVDb Series ID: {tvdb_url[len(TVDb.series_id_url):]}")
        else:
            raise Failed(f"TVDb Error: Could not find a TVDb {self.media_type} ID at the URL {tvdb_url}")

        results = response.xpath("//div[@class='change_translation_text' and @data-language='eng']/@data-title")
        if len(results) > 0 and len(results[0]) > 0:
            self.title = results[0]
        else:
            raise Failed(f"TVDb Error: Name not found from TVDb URL: {tvdb_url}")

        results = response.xpath("//div[@class='row hidden-xs hidden-sm']/div/img/@src")
        self.poster_path = results[0] if len(results) > 0 and len(results[0]) > 0 else None

        results = response.xpath("(//h2[@class='mt-4' and text()='Backgrounds']/following::div/a/@href)[1]")
        self.background_path = results[0] if len(results) > 0 and len(results[0]) > 0 else None

        results = response.xpath("//div[@class='block']/div[not(@style='display:none')]/p/text()")
        self.summary = results[0] if len(results) > 0 and len(results[0]) > 0 else None

        tmdb_id = None
        if is_movie:
            results = response.xpath("//*[text()='TheMovieDB.com']/@href")
            if len(results) > 0:
                try:                                                    tmdb_id = util.regex_first_int(results[0], "TMDb ID")
                except Failed as e:                                     logger.error(e)
            if not tmdb_id:
                results = response.xpath("//*[text()='IMDB']/@href")
                if len(results) > 0:
                    try:                                                tmdb_id, _ = TVDb.config.convert_from_imdb(util.get_id_from_imdb_url(results[0]), language)
                    except Failed as e:                                 logger.error(e)
        self.tmdb_id = tmdb_id
        self.tvdb_url = tvdb_url
        self.language = language
        self.is_movie = is_movie
        self.TVDb = TVDb

class TVDbAPI:
    def __init__(self, config):
        self.config = config
        self.site_url = "https://www.thetvdb.com"
        self.alt_site_url = "https://thetvdb.com"
        self.list_url = f"{self.site_url}/lists/"
        self.alt_list_url = f"{self.alt_site_url}/lists/"
        self.series_url = f"{self.site_url}/series/"
        self.alt_series_url = f"{self.alt_site_url}/series/"
        self.movies_url = f"{self.site_url}/movies/"
        self.alt_movies_url = f"{self.alt_site_url}/movies/"
        self.series_id_url = f"{self.site_url}/dereferrer/series/"
        self.movie_id_url = f"{self.site_url}/dereferrer/movie/"

    def get_movie_or_series(self, language, tvdb_url, is_movie):
        return self.get_movie(language, tvdb_url) if is_movie else self.get_series(language, tvdb_url)

    def get_series(self, language, tvdb_url):
        try:
            tvdb_url = f"{self.series_id_url}{int(tvdb_url)}"
        except ValueError:
            pass
        return TVDbObj(tvdb_url, language, False, self)

    def get_movie(self, language, tvdb_url):
        try:
            tvdb_url = f"{self.movie_id_url}{int(tvdb_url)}"
        except ValueError:
            pass
        return TVDbObj(tvdb_url, language, True, self)

    def get_list_description(self, tvdb_url, language):
        description = self.send_request(tvdb_url, language).xpath("//div[@class='block']/div[not(@style='display:none')]/p/text()")
        return description[0] if len(description) > 0 and len(description[0]) > 0 else ""

    def get_tvdb_ids_from_url(self, tvdb_url, language):
        show_ids = []
        movie_ids = []
        tvdb_url = tvdb_url.strip()
        if tvdb_url.startswith((self.list_url, self.alt_list_url)):
            try:
                items = self.send_request(tvdb_url, language).xpath("//div[@class='col-xs-12 col-sm-12 col-md-8 col-lg-8 col-md-pull-4']/div[@class='row']")
                for item in items:
                    title = item.xpath(".//div[@class='col-xs-12 col-sm-9 mt-2']//a/text()")[0]
                    item_url = item.xpath(".//div[@class='col-xs-12 col-sm-9 mt-2']//a/@href")[0]
                    if item_url.startswith("/series/"):
                        try:                                                    show_ids.append(self.get_series(language, f"{self.site_url}{item_url}").id)
                        except Failed as e:                                     logger.error(f"{e} for series {title}")
                    elif item_url.startswith("/movies/"):
                        try:
                            tmdb_id = self.get_movie(language, f"{self.site_url}{item_url}").tmdb_id
                            if tmdb_id:                                             movie_ids.append(tmdb_id)
                            else:                                                   raise Failed(f"TVDb Error: TMDb ID not found from TVDb URL: {tvdb_url}")
                        except Failed as e:
                            logger.error(f"{e} for series {title}")
                    else:
                        logger.error(f"TVDb Error: Skipping Movie: {title}")
                if len(show_ids) > 0 or len(movie_ids) > 0:
                    return movie_ids, show_ids
                raise Failed(f"TVDb Error: No TVDb IDs found at {tvdb_url}")
            except requests.exceptions.MissingSchema:
                util.print_stacktrace()
                raise Failed(f"TVDb Error: URL Lookup Failed for {tvdb_url}")
        else:
            raise Failed(f"TVDb Error: {tvdb_url} must begin with {self.list_url}")

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def send_request(self, url, language):
        return html.fromstring(requests.get(url, headers={"Accept-Language": language}).content)

    def get_items(self, method, data, language, status_message=True):
        pretty = util.pretty_names[method] if method in util.pretty_names else method
        show_ids = []
        movie_ids = []
        if status_message:
            logger.info(f"Processing {pretty}: {data}")
        if method == "tvdb_show":
            show_ids.append(self.get_series(language, data).id)
        elif method == "tvdb_movie":
            movie_ids.append(self.get_movie(language, data).id)
        elif method == "tvdb_list":
            tmdb_ids, tvdb_ids = self.get_tvdb_ids_from_url(data, language)
            movie_ids.extend(tmdb_ids)
            show_ids.extend(tvdb_ids)
        else:
            raise Failed(f"TVDb Error: Method {method} not supported")
        if status_message:
            logger.debug(f"TMDb IDs Found: {movie_ids}")
            logger.debug(f"TVDb IDs Found: {show_ids}")
        return movie_ids, show_ids
