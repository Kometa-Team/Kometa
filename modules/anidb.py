import time
from datetime import datetime
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

class AniDBObj:
    def __init__(self, anidb, anidb_id, language):
        self.anidb = anidb
        self.anidb_id = anidb_id
        self.language = language
        response = self.anidb._request(f"{urls['anime']}/{anidb_id}", language=self.language)

        def parse_page(xpath, is_list=False, is_float=False, is_date=False, fail=False):
            parse_results = response.xpath(xpath)
            try:
                if len(parse_results) > 0:
                    parse_results = [r.strip() for r in parse_results if len(r) > 0]
                if parse_results:
                    if is_list:
                        return parse_results
                    elif is_float:
                        return float(parse_results[0])
                    elif is_date:
                        return datetime.strptime(parse_results[0], "%d.%m.%Y")
                    else:
                        return parse_results[0]
            except (ValueError, TypeError):
                pass
            if fail:
                raise Failed(f"AniDB Error: No Anime Found for AniDB ID: {self.anidb_id}")
            elif is_list:
                return []
            elif is_float:
                return 0
            else:
                return None

        self.official_title = parse_page(f"//th[text()='Main Title']/parent::tr/td/span/text()", fail=True)
        self.title = parse_page(f"//th[text()='Official Title']/parent::tr/td/span/span/span[text()='{self.language}']/parent::span/parent::span/parent::td/label/text()")
        self.rating = parse_page(f"//th[text()='Rating']/parent::tr/td/span/a/span/text()", is_float=True)
        self.average = parse_page(f"//th[text()='Average']/parent::tr/td/span/a/span/text()", is_float=True)
        self.released = parse_page(f"//th[text()='Year']/parent::tr/td/span/text()", is_date=True)
        self.tags = [g.capitalize() for g in parse_page("//th/a[text()='Tags']/parent::th/parent::tr/td/span/a/span/text()", is_list=True)]
        self.description = response.xpath(f"string(//div[@itemprop='description'])")


class AniDB:
    def __init__(self, config, language):
        self.config = config
        self.language = language
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

    def _request(self, url, data=None):
        if self.config.trace_mode:
            logger.debug(f"URL: {url}")
        if data:
            return self.config.post_html(url, data=data, headers=util.header(self.language))
        else:
            return self.config.get_html(url, headers=util.header(self.language))

    def _popular(self):
        response = self._request(urls["popular"])
        return util.get_int_list(response.xpath("//td[@class='name anime']/a/@href"), "AniDB ID")

    def _relations(self, anidb_id):
        response = self._request(f"{urls['anime']}/{anidb_id}{urls['relation']}")
        return util.get_int_list(response.xpath("//area/@href"), "AniDB ID")

    def _validate(self, anidb_id):
        response = self._request(f"{urls['anime']}/{anidb_id}")
        ids = response.xpath(f"//*[text()='a{anidb_id}']/text()")
        if len(ids) > 0:
            return util.regex_first_int(ids[0], "AniDB ID")
        raise Failed(f"AniDB Error: AniDB ID: {anidb_id} not found")

    def validate_anidb_ids(self, anidb_ids):
        anidb_list = util.get_int_list(anidb_ids, "AniDB ID")
        anidb_values = []
        for anidb_id in anidb_list:
            try:
                anidb_values.append(self._validate(anidb_id))
            except Failed as e:
                logger.error(e)
        if len(anidb_values) > 0:
            return anidb_values
        raise Failed(f"AniDB Error: No valid AniDB IDs in {anidb_list}")

    def _tag(self, tag, limit):
        anidb_ids = []
        current_url = f"{urls['tag']}/{tag}"
        while True:
            response = self._request(current_url)
            anidb_ids.extend(util.get_int_list(response.xpath("//td[@class='name main anime']/a/@href"), "AniDB ID"))
            next_page_list = response.xpath("//li[@class='next']/a/@href")
            if len(anidb_ids) >= limit or len(next_page_list) == 0:
                break
            time.sleep(2)
            current_url = f"{base_url}{next_page_list[0]}"
        return anidb_ids[:limit]

    def get_anime(self, anidb_id):
        return AniDBObj(self, anidb_id, self.language)

    def get_anidb_ids(self, method, data):
        anidb_ids = []
        if method == "anidb_popular":
            logger.info(f"Processing AniDB Popular: {data} Anime")
            anidb_ids.extend(self._popular()[:data])
        elif method == "anidb_tag":
            logger.info(f"Processing AniDB Tag: {data['limit'] if data['limit'] > 0 else 'All'} Anime from the Tag ID: {data['tag']}")
            anidb_ids = self._tag(data["tag"], data["limit"])
        elif method == "anidb_id":
            logger.info(f"Processing AniDB ID: {data}")
            anidb_ids.append(data)
        elif method == "anidb_relation":
            logger.info(f"Processing AniDB Relation: {data}")
            anidb_ids.extend(self._relations(data))
        else:
            raise Failed(f"AniDB Error: Method {method} not supported")
        logger.debug("")
        logger.debug(f"{len(anidb_ids)} AniDB IDs Found: {anidb_ids}")
        return anidb_ids
