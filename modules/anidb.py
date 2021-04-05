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
        self.id_list = html.fromstring(requests.get("https://raw.githubusercontent.com/Anime-Lists/anime-lists/master/anime-list-master.xml").content)

    def convert_anidb_to_tvdb(self, anidb_id):          return self.convert_anidb(anidb_id, "anidbid", "tvdbid")
    def convert_anidb_to_imdb(self, anidb_id):          return self.convert_anidb(anidb_id, "anidbid", "imdbid")
    def convert_tvdb_to_anidb(self, tvdb_id):           return self.convert_anidb(tvdb_id, "tvdbid", "anidbid")
    def convert_imdb_to_anidb(self, imdb_id):           return self.convert_anidb(imdb_id, "imdbid", "anidbid")
    def convert_anidb(self, input_id, from_id, to_id):
        ids = self.id_list.xpath(f"//anime[contains(@{from_id}, '{input_id}')]/@{to_id}")
        if len(ids) > 0:
            if from_id == "tvdbid":                             return [int(i) for i in ids]
            if len(ids[0]) > 0:
                try:                                                return ids[0].split(",") if to_id == "imdbid" else int(ids[0])
                except ValueError:                                  raise Failed(f"AniDB Error: No {util.pretty_ids[to_id]} ID found for {util.pretty_ids[from_id]} ID: {input_id}")
            else:                                               raise Failed(f"AniDB Error: No {util.pretty_ids[to_id]} ID found for {util.pretty_ids[from_id]} ID: {input_id}")
        else:                                               raise Failed(f"AniDB Error: {util.pretty_ids[from_id]} ID: {input_id} not found")

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
        anime_ids = []
        if method == "anidb_popular":
            if status_message:
                logger.info(f"Processing {pretty}: {data} Anime")
            anime_ids.extend(self.get_popular(language)[:data])
        else:
            if status_message:                                  logger.info(f"Processing {pretty}: {data}")
            if method == "anidb_id":                            anime_ids.append(data)
            elif method == "anidb_relation":                    anime_ids.extend(self.get_anidb_relations(data, language))
            else:                                               raise Failed(f"AniDB Error: Method {method} not supported")
        show_ids = []
        movie_ids = []
        for anidb_id in anime_ids:
            try:
                for imdb_id in self.convert_anidb_to_imdb(anidb_id):
                    tmdb_id, _ = self.config.convert_from_imdb(imdb_id, language)
                    if tmdb_id:                                         movie_ids.append(tmdb_id)
                    else:                                               raise Failed
            except Failed:
                try:                                                show_ids.append(self.convert_anidb_to_tvdb(anidb_id))
                except Failed:                                      logger.error(f"AniDB Error: No TVDb ID or IMDb ID found for AniDB ID: {anidb_id}")
        if status_message:
            logger.debug(f"AniDB IDs Found: {anime_ids}")
            logger.debug(f"TMDb IDs Found: {movie_ids}")
            logger.debug(f"TVDb IDs Found: {show_ids}")
        return movie_ids, show_ids
