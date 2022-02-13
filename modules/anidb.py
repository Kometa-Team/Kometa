import time
from modules import util
from modules.util import Failed

logger = util.logger

builders = ["anidb_id", "anidb_relation", "anidb_popular", "anidb_tag"]
base_url = "https://anidb.net"
urls = {
    "anime": f"{base_url}/anime",
    "popular": f"{base_url}/latest/anime/popular/?h=1",
    "relation": "/relation/graph",
    "tag": f"{base_url}/tag",
    "login": f"{base_url}/perl-bin/animedb.pl"
}

class AniDB:
    def __init__(self, config):
        self.config = config
        self.username = None
        self.password = None

    def login(self, username, password):
        self.username = username
        self.password = password
        logger.secret(self.username)
        logger.secret(self.password)
        data = {"show": "main", "xuser": self.username, "xpass": self.password, "xdoautologin": "on"}
        if not self._request(urls["login"], data=data).xpath("//li[@class='sub-menu my']/@title"):
            raise Failed("AniDB Error: Login failed")

    def _request(self, url, language=None, data=None):
        if self.config.trace_mode:
            logger.debug(f"URL: {url}")
        if data:
            return self.config.post_html(url, data=data, headers=util.header(language))
        else:
            return self.config.get_html(url, headers=util.header(language))

    def _popular(self, language):
        response = self._request(urls["popular"], language=language)
        return util.get_int_list(response.xpath("//td[@class='name anime']/a/@href"), "AniDB ID")

    def _relations(self, anidb_id, language):
        response = self._request(f"{urls['anime']}/{anidb_id}{urls['relation']}", language=language)
        return util.get_int_list(response.xpath("//area/@href"), "AniDB ID")

    def _validate(self, anidb_id, language):
        response = self._request(f"{urls['anime']}/{anidb_id}", language=language)
        ids = response.xpath(f"//*[text()='a{anidb_id}']/text()")
        if len(ids) > 0:
            return util.regex_first_int(ids[0], "AniDB ID")
        raise Failed(f"AniDB Error: AniDB ID: {anidb_id} not found")

    def validate_anidb_ids(self, anidb_ids, language):
        anidb_list = util.get_int_list(anidb_ids, "AniDB ID")
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
        current_url = f"{urls['tag']}/{tag}"
        while True:
            response = self._request(current_url, language=language)
            anidb_ids.extend(util.get_int_list(response.xpath("//td[@class='name main anime']/a/@href"), "AniDB ID"))
            next_page_list = response.xpath("//li[@class='next']/a/@href")
            if len(anidb_ids) >= limit or len(next_page_list) == 0:
                break
            time.sleep(2)
            current_url = f"{base_url}{next_page_list[0]}"
        return anidb_ids[:limit]

    def get_anidb_ids(self, method, data, language):
        anidb_ids = []
        if method == "anidb_popular":
            logger.info(f"Processing AniDB Popular: {data} Anime")
            anidb_ids.extend(self._popular(language)[:data])
        elif method == "anidb_tag":
            logger.info(f"Processing AniDB Tag: {data['limit'] if data['limit'] > 0 else 'All'} Anime from the Tag ID: {data['tag']}")
            anidb_ids = self._tag(data["tag"], data["limit"], language)
        elif method == "anidb_id":
            logger.info(f"Processing AniDB ID: {data}")
            anidb_ids.append(data)
        elif method == "anidb_relation":
            logger.info(f"Processing AniDB Relation: {data}")
            anidb_ids.extend(self._relations(data, language))
        else:
            raise Failed(f"AniDB Error: Method {method} not supported")
        logger.debug("")
        logger.debug(f"{len(anidb_ids)} AniDB IDs Found: {anidb_ids}")
        return anidb_ids
