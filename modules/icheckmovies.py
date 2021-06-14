import logging, requests
from lxml import html
from modules import util
from modules.util import Failed
from retrying import retry

logger = logging.getLogger("Plex Meta Manager")

builders = ["icheckmovies_list"]

class ICheckMovies:
    def __init__(self, config):
        self.config = config
        self.list_url = "https://www.icheckmovies.com/lists/"

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def _request(self, url, language):
        return html.fromstring(requests.get(url, headers={"Accept-Language": language, "User-Agent": "Mozilla/5.0 x64"}).content)

    def _parse_list(self, list_url, language):
        response = self._request(list_url, language)
        imdb_urls = response.xpath("//a[@class='optionIcon optionIMDB external']/@href")
        return [t[t.find("/tt") + 1:-1] for t in imdb_urls]

    def validate_icheckmovies_list(self, list_url, language):
        list_url = list_url.strip()
        if not list_url.startswith(self.list_url):
            raise Failed(f"ICheckMovies Error: {list_url} must begin with: {self.list_url}")
        if len(self._parse_list(list_url, language)) > 0:
            return list_url
        raise Failed(f"ICheckMovies Error: {list_url} failed to parse")

    def get_items(self, method, data, language):
        pretty = util.pretty_names[method] if method in util.pretty_names else method
        movie_ids = []
        if method == "icheckmovies_list":
            logger.info(f"Processing {pretty}: {data}")
            imdb_ids = self._parse_list(data, language)
            total_ids = len(imdb_ids)
            for i, imdb_id in enumerate(imdb_ids, 1):
                try:
                    util.print_return(f"Converting IMDb ID {i}/{total_ids}")
                    movie_ids.append(self.config.Convert.imdb_to_tmdb(imdb_id))
                except Failed as e:
                    logger.error(e)
            logger.info(util.adjust_space(f"Processed {total_ids} IMDb IDs"))
        else:
            raise Failed(f"ICheckMovies Error: Method {method} not supported")
        logger.debug("")
        logger.debug(f"TMDb IDs Found: {movie_ids}")
        return movie_ids, []
