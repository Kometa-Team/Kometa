import logging, time
from modules import util
from modules.util import Failed

logger = logging.getLogger("Plex Meta Manager")

builders = ["letterboxd_list", "letterboxd_list_details"]
base_url = "https://letterboxd.com"

class Letterboxd:
    def __init__(self, config):
        self.config = config

    def _parse_list(self, list_url, language):
        response = self.config.get_html(list_url, headers=util.header(language))
        letterboxd_ids = response.xpath("//li[contains(@class, 'poster-container')]/div/@data-film-id")
        items = []
        for letterboxd_id in letterboxd_ids:
            slugs = response.xpath(f"//div[@data-film-id='{letterboxd_id}']/@data-film-slug")
            items.append((letterboxd_id, slugs[0]))
        next_url = response.xpath("//a[@class='next']/@href")
        if len(next_url) > 0:
            time.sleep(2)
            items.extend(self._parse_list(f"{base_url}{next_url[0]}", language))
        return items

    def _tmdb(self, letterboxd_url, language):
        response = self.config.get_html(letterboxd_url, headers=util.header(language))
        ids = response.xpath("//a[@data-track-action='TMDb']/@href")
        if len(ids) > 0 and ids[0]:
            if "themoviedb.org/movie" in ids[0]:
                return util.regex_first_int(ids[0], "TMDB Movie ID")
            raise Failed(f"Letterboxd Error: TMDb Movie ID not found in {ids[0]}")
        raise Failed(f"Letterboxd Error: TMDb Movie ID not found at {letterboxd_url}")

    def get_list_description(self, list_url, language):
        response = self.config.get_html(list_url, headers=util.header(language))
        descriptions = response.xpath("//meta[@property='og:description']/@content")
        return descriptions[0] if len(descriptions) > 0 and len(descriptions[0]) > 0 else None

    def get_items(self, method, data, language):
        pretty = util.pretty_names[method] if method in util.pretty_names else method
        movie_ids = []
        logger.info(f"Processing {pretty}: {data}")
        items = self._parse_list(data, language)
        total_items = len(items)
        if total_items > 0:
            for i, item in enumerate(items, 1):
                letterboxd_id, slug = item
                util.print_return(f"Finding TMDb ID {i}/{total_items}")
                tmdb_id = None
                expired = None
                if self.config.Cache:
                    tmdb_id, expired = self.config.Cache.query_letterboxd_map(letterboxd_id)
                if not tmdb_id or expired is not False:
                    try:
                        tmdb_id = self._tmdb(f"{base_url}{slug}", language)
                    except Failed as e:
                        logger.error(e)
                        continue
                    if self.config.Cache:
                        self.config.Cache.update_letterboxd_map(expired, letterboxd_id, tmdb_id)
                movie_ids.append(tmdb_id)
            logger.info(util.adjust_space(f"Processed {total_items} TMDb IDs"))
        else:
            logger.error(f"Letterboxd Error: No List Items found in {data}")
        logger.debug("")
        logger.debug(f"{len(movie_ids)} TMDb IDs Found: {movie_ids}")
        return movie_ids, []
