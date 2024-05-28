import json, time
from datetime import datetime
from modules import util
from modules.util import Failed

logger = util.logger

builders = ["anidb_id", "anidb_relation", "anidb_popular", "anidb_tag"]
base_url = "https://anidb.net"
api_url = "http://api.anidb.net:9001/httpapi"
urls = {
    "anime": f"{base_url}/anime",
    "popular": f"{base_url}/latest/anime/popular/?h=1",
    "relation": "/relation/graph",
    "tag": f"{base_url}/tag",
    "login": f"{base_url}/perl-bin/animedb.pl"
}
weights = {"anidb": 1000, "anidb_3_0": 600, "anidb_2_5": 500, "anidb_2_0": 400, "anidb_1_5": 300, "anidb_1_0": 200, "anidb_0_5": 100}

class AniDBObj:
    def __init__(self, anidb, anidb_id, data):
        self._anidb = anidb
        self.anidb_id = anidb_id
        self._data = data

        def _parse(attr, xpath, is_list=False, is_dict=False, is_int=False, is_float=False, is_date=False, fail=False):
            try:
                if isinstance(data, dict):
                    if is_list:
                        return data[attr].split("|") if data[attr] else []
                    elif is_dict:
                        return json.loads(data[attr])
                    elif is_int or is_float:
                        return util.check_num(data[attr], is_int=is_int)
                    elif is_date:
                        return datetime.strptime(data[attr], "%Y-%m-%d")
                    else:
                        return data[attr]
                parse_results = data.xpath(xpath)
                if attr == "tags":
                    return {ta.xpath("name/text()")[0]: 1001 if ta.get("infobox") else int(ta.get("weight")) for ta in parse_results}
                elif attr == "titles":
                    return {ta.get("xml:lang"): ta.text_content() for ta in parse_results}
                elif len(parse_results) > 0:
                    parse_results = [r.strip() for r in parse_results if len(r) > 0]
                if parse_results:
                    if is_list:
                        return parse_results
                    elif is_int or is_float:
                        return util.check_num(parse_results[0], is_int=is_int)
                    elif is_date:
                        return datetime.strptime(parse_results[0], "%Y-%m-%d")
                    else:
                        return parse_results[0]
            except (ValueError, TypeError):
                pass
            if fail:
                raise Failed(f"AniDB Error: No Anime Found for AniDB ID: {self.anidb_id}")
            elif is_list:
                return []
            elif is_dict:
                return {}
            else:
                return None

        self.main_title = _parse("main_title", "//anime/titles/title[@type='main']/text()", fail=True)
        self.titles = _parse("titles", "//anime/titles/title[@type='official']", is_dict=True)
        self.official_title = self.titles[self._anidb.language] if self._anidb.language in self.titles else self.main_title
        self.studio = _parse("studio", "//anime/creators/name[@type='Animation Work']/text()")
        self.rating = _parse("rating", "//anime/ratings/permanent/text()", is_float=True)
        self.average = _parse("average", "//anime/ratings/temporary/text()", is_float=True)
        self.score = _parse("score", "//anime/ratings/review/text()", is_float=True)
        self.released = _parse("released", "//anime/startdate/text()", is_date=True)
        self.tags = _parse("tags", "//anime/tags/tag", is_dict=True)
        self.mal_id = _parse("mal_id", "//anime/resources/resource[@type='2']/externalentity/identifier/text()", is_int=True)
        self.imdb_id = _parse("imdb_id", "//anime/resources/resource[@type='43']/externalentity/identifier/text()")
        if isinstance(data, dict):
            self.tmdb_id = _parse("tmdb_id", "", is_int=True)
            self.tmdb_type = _parse("tmdb_type", "")
        else:
            tmdb = _parse("tmdb", "//anime/resources/resource[@type='44']/externalentity/identifier/text()", is_list=True)
            self.tmdb_id = None
            self.tmdb_type = None
            for i in tmdb:
                try:
                    self.tmdb_id = int(i)
                except ValueError:
                    self.tmdb_type = i


class AniDB:
    def __init__(self, requests, cache, data):
        self.requests = requests
        self.cache = cache
        self.language = data["language"]
        self.expiration = 60
        self.client = None
        self.version = None
        self.username = None
        self.password = None
        self._delay = None

    def authorize(self, client, version, expiration):
        self.client = client
        self.version = version
        self.expiration = expiration
        logger.secret(self.client)
        if self.cache:
            value1, value2, success = self.cache.query_testing("anidb_login")
            if str(value1) == str(client) and str(value2) == str(version) and success:
                return
        try:
            self.get_anime(69, ignore_cache=True)
            if self.cache:
                self.cache.update_testing("anidb_login", self.client, self.version, "True")
        except Failed:
            self.client = None
            self.version = None
            if self.cache:
                self.cache.update_testing("anidb_login", self.client, self.version, "False")
            raise

    @property
    def is_authorized(self):
        return self.client is not None

    def login(self, username, password):
        logger.secret(username)
        logger.secret(password)
        data = {"show": "main", "xuser": username, "xpass": password, "xdoautologin": "on"}
        if not self._request(urls["login"], data=data).xpath("//li[@class='sub-menu my']/@title"):
            raise Failed("AniDB Error: Login failed")
        self.username = username
        self.password = password

    def _request(self, url, params=None, data=None):
        logger.trace(f"URL: {url}")
        if params:
            logger.trace(f"Params: {params}")
        if data:
            return self.requests.post_html(url, data=data, language=self.language)
        else:
            return self.requests.get_html(url, params=params, language=self.language)

    def _popular(self):
        response = self._request(urls["popular"])
        return util.get_int_list(response.xpath("//td[@class='thumb anime']/a/@href"), "AniDB ID")

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

    def get_anime(self, anidb_id, ignore_cache=False):
        expired = None
        anidb_dict = None
        if self.cache and not ignore_cache:
            anidb_dict, expired = self.cache.query_anidb(anidb_id, self.expiration)
        if expired or not anidb_dict:
            time_check = time.time()
            if self._delay is not None:
                while time_check - self._delay < 2:
                    time_check = time.time()
            anidb_dict = self._request(api_url, params={
                "client": self.client,
                "clientver": self.version,
                "protover": 1,
                "request": "anime",
                "aid": anidb_id
            })
            self._delay = time.time()
        obj = AniDBObj(self, anidb_id, anidb_dict)
        if self.cache and not ignore_cache:
            self.cache.update_anidb(expired, anidb_id, obj, self.expiration)
        return obj

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
        logger.debug(f"{len(anidb_ids)} AniDB IDs Found")
        logger.trace(f"IDs: {anidb_ids}")
        return anidb_ids
