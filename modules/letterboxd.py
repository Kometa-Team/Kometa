import logging, math, re, requests
from lxml import html
from modules import util
from modules.util import Failed
from retrying import retry

logger = logging.getLogger("Plex Meta Manager")

class LetterboxdAPI:
    def __init__(self):
        self.url = "https://letterboxd.com"

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def send_request(self, url, header):
        return html.fromstring(requests.get(url, headers=header).content)

    def parse_list_for_slugs(self, list_url, language):
        response = self.send_request(list_url, header={"Accept-Language": language, "User-Agent": "Mozilla/5.0 x64"})
        slugs = response.xpath("//div[@class='poster film-poster really-lazy-load']/@data-film-slug")
        next_url = response.xpath("//a[@class='next']/@href")
        if len(next_url) > 0:
            slugs.extend(self.parse_list_for_slugs(f"{self.url}{next_url[0]}", language))
        return slugs

    def get_tmdb_from_slug(self, slug, language):
        return self.get_tmdb(f"{self.url}{slug}", language)

    def get_tmdb(self, letterboxd_url, language):
        response = self.send_request(letterboxd_url, header={"Accept-Language": language, "User-Agent": "Mozilla/5.0 x64"})
        ids = response.xpath("//body/@data-tmdb-id")
        if len(ids) > 0:
            return int(ids[0])
        raise Failed(f"Letterboxd Error: TMDb ID not found at {letterboxd_url}")

    def get_items(self, method, data, language, status_message=True):
        pretty = util.pretty_names[method] if method in util.pretty_names else method
        movie_ids = []
        if status_message:
            logger.info(f"Processing {pretty}: {data}")
        slugs = self.parse_list_for_slugs(data, language)
        total_slugs = len(slugs)
        if total_slugs == 0:
            raise Failed(f"Letterboxd Error: No List Items found in {data}")
        length = 0
        for i, slug in enumerate(slugs, 1):
            length = util.print_return(length, f"Finding TMDb ID {i}/{total_slugs}")
            try:
                movie_ids.append(self.get_tmdb(slug, language))
            except Failed as e:
                logger.error(e)
        util.print_end(length, f"Processed {total_slugs} TMDb IDs")
        if status_message:
            logger.debug(f"TMDb IDs Found: {movie_ids}")
        return movie_ids, []
