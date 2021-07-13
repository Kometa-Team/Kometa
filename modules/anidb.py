import logging, requests, time
from lxml import html
from modules import util
from modules.util import Failed
from retrying import retry

logger = logging.getLogger("Plex Meta Manager")

builders = ["anidb_id", "anidb_relation", "anidb_popular", "anidb_tag"]

class AniDB:
    def __init__(self, params, config):
        self.config = config

        self.urls = {
            "anime": "https://anidb.net/anime",
            "popular": "https://anidb.net/latest/anime/popular/?h=1",
            "relation": "/relation/graph",
            "anidb_tag": "https://anidb.net/tag",
            "login": "https://anidb.net/perl-bin/animedb.pl"
        }
        if params:
            if not self._login(params["username"], params["password"]).xpath("//li[@class='sub-menu my']/@title"):
                raise Failed("AniDB Error: Login failed")

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def _request(self, url, language):
        return html.fromstring(self.config.session.get(url, headers={"Accept-Language": language, "User-Agent": "Mozilla/5.0 x64"}).content)

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def _login(self, username, password):
        data = {
            "show": "main",
            "xuser": username,
            "xpass": password,
            "xdoautologin": "on"
        }
        return html.fromstring(self.config.session.post(self.urls["login"], data, headers={"Accept-Language": "en-US,en;q=0.5", "User-Agent": "Mozilla/5.0 x64"}).content)

    def _popular(self, language):
        response = self._request(self.urls["popular"], language)
        return util.get_int_list(response.xpath("//td[@class='name anime']/a/@href"), "AniDB ID")

    def _relations(self, anidb_id, language):
        response = self._request(f"{self.urls['anime']}/{anidb_id}{self.urls['relation']}", language)
        return util.get_int_list(response.xpath("//area/@href"), "AniDB ID")

    def _validate(self, anidb_id, language):
        response = self._request(f"{self.urls['anime']}/{anidb_id}", language)
        ids = response.xpath(f"//*[text()='a{anidb_id}']/text()")
        if len(ids) > 0:
            return util.regex_first_int(ids[0], "AniDB ID")
        raise Failed(f"AniDB Error: AniDB ID: {anidb_id} not found")

    def validate_anidb_list(self, anidb_list, language):
        anidb_values = []
        for anidb_id in anidb_list:
            try:
                anidb_values.append(self._validate(anidb_id, language))
            except Failed as e:
                logger.error(e)
        if len(anidb_values) > 0:
            return anidb_values
        raise Failed(f"AniDB Error: No valid AniDB IDs in {anidb_list}")

    def _tag(self, tag, limit, language):
        anidb_ids = []
        current_url = f"{self.urls['anidb_tag']}/{tag}"
        while True:
            response = self._request(current_url, language)
            int_list = util.get_int_list(response.xpath("//td[@class='name main anime']/a/@href"), "AniDB ID")
            anidb_ids.extend(int_list)
            next_page_list = response.xpath("//li[@class='next']/a/@href")
            if len(anidb_ids) >= limit or len(next_page_list) == 0:
                break
            time.sleep(2)
            current_url = f"https://anidb.net{next_page_list[0]}"
        return anidb_ids[:limit]

    def get_items(self, method, data, language):
        pretty = util.pretty_names[method] if method in util.pretty_names else method
        anidb_ids = []
        if method == "anidb_popular":
            logger.info(f"Processing {pretty}: {data} Anime")
            anidb_ids.extend(self._popular(language)[:data])
        elif method == "anidb_tag":
            anidb_ids = self._tag(data["tag"], data["limit"], language)
            logger.info(f"Processing {pretty}: {data['limit'] if data['limit'] > 0 else 'All'} Anime from the Tag ID: {data['tag']}")
        else:
            logger.info(f"Processing {pretty}: {data}")
            if method == "anidb_id":                            anidb_ids.append(data)
            elif method == "anidb_relation":                    anidb_ids.extend(self._relations(data, language))
            else:                                               raise Failed(f"AniDB Error: Method {method} not supported")
        movie_ids, show_ids = self.config.Convert.anidb_to_ids(anidb_ids)
        logger.debug("")
        logger.debug(f"{len(anidb_ids)} AniDB IDs Found: {anidb_ids}")
        logger.debug(f"{len(movie_ids)} TMDb IDs Found: {movie_ids}")
        logger.debug(f"{len(show_ids)} TVDb IDs Found: {show_ids}")
        return movie_ids, show_ids
