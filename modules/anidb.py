import logging, requests
from lxml import html
from modules import util
from modules.util import Failed
from retrying import retry

logger = logging.getLogger("Plex Meta Manager")

builders = ["anidb_id", "anidb_relation", "anidb_popular"]

class AniDBAPI:
    def __init__(self, config):
        self.config = config
        self.urls = {
            "anime": "https://anidb.net/anime",
            "popular": "https://anidb.net/latest/anime/popular/?h=1",
            "relation": "/relation/graph"
        }

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def send_request(self, url, language):
        return html.fromstring(requests.get(url, headers={"Accept-Language": language, "User-Agent": "Mozilla/5.0 x64"}).content)

    def get_popular(self, language):
        response = self.send_request(self.urls["popular"], language)
        return util.get_int_list(response.xpath("//td[@class='name anime']/a/@href"), "AniDB ID")

    def validate_anidb_id(self, anidb_id, language):
        response = self.send_request(f"{self.urls['anime']}/{anidb_id}", language)
        ids = response.xpath(f"//*[text()='a{anidb_id}']/text()")
        if len(ids) > 0:
            return util.regex_first_int(ids[0], "AniDB ID")
        raise Failed(f"AniDB Error: AniDB ID: {anidb_id} not found")

    def get_anidb_relations(self, anidb_id, language):
        response = self.send_request(f"{self.urls['anime']}/{anidb_id}{self.urls['relation']}", language)
        return util.get_int_list(response.xpath("//area/@href"), "AniDB ID")

    def validate_anidb_list(self, anidb_list, language):
        anidb_values = []
        for anidb_id in anidb_list:
            try:
                anidb_values.append(self.validate_anidb_id(anidb_id, language))
            except Failed as e:
                logger.error(e)
        if len(anidb_values) > 0:
            return anidb_values
        raise Failed(f"AniDB Error: No valid AniDB IDs in {anidb_list}")

    def get_items(self, method, data, language, status_message=True):
        pretty = util.pretty_names[method] if method in util.pretty_names else method
        if status_message:
            logger.debug(f"Data: {data}")
        anidb_ids = []
        if method == "anidb_popular":
            if status_message:
                logger.info(f"Processing {pretty}: {data} Anime")
            anidb_ids.extend(self.get_popular(language)[:data])
        else:
            if status_message:                                  logger.info(f"Processing {pretty}: {data}")
            if method == "anidb_id":                            anidb_ids.append(data)
            elif method == "anidb_relation":                    anidb_ids.extend(self.get_anidb_relations(data, language))
            else:                                               raise Failed(f"AniDB Error: Method {method} not supported")
        movie_ids, show_ids = self.config.Arms.anidb_to_ids(anidb_ids, language)
        if status_message:
            logger.debug(f"AniDB IDs Found: {anidb_ids}")
            logger.debug(f"TMDb IDs Found: {movie_ids}")
            logger.debug(f"TVDb IDs Found: {show_ids}")
        return movie_ids, show_ids
