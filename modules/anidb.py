import json, time
from datetime import datetime
from modules import util
from modules.util import Failed

logger = util.logger

builders = ["anidb_id", "anidb_relation", "anidb_popular", "anidb_tag"]
base_url = "https://anidb.net"
api_url = "http://api.anidb.net:9001/httpapi"
cache_url = "https://raw.githubusercontent.com/notseteve/AnimeAggregations/main/anime"
urls = {
    "anime": f"{base_url}/anime",
    "popular": f"{base_url}/latest/anime/popular/?h=1",
    "relation": "/relation/graph",
    "tag": f"{base_url}/tag",
    "login": f"{base_url}/perl-bin/animedb.pl"
}
weights = {"anidb": 1000, "anidb_3_0": 600, "anidb_2_5": 500, "anidb_2_0": 400, "anidb_1_5": 300, "anidb_1_0": 200, "anidb_0_5": 100}
LANGUAGE_MATCHER = {
    "AF" : "AFRIKAANS",
    "SQ" : "ALBANIAN",
    "AL" : "ALBANIAN",
    "AR" : "ARABIC",
    "BN" : "BENGALI",
    "BD" : "BENGALI",
    "BS" : "BOSNIAN",
    "BG" : "BULGARIAN",
    "MY" : "BURMESE",
    "ZH" : "CHINESE",
    "ZH-NAN" : "CHINESE_TAIWAN",
    "ZH-HANT" : "CHINESE_TRADITIONAL",
    "X-ZHT" : "CHINESE_TRANSLITERATED",
    "ZH-HANS" : "CHINESE_SIMPLIFIED",
    "ZH-CMN" : "CHINESE_SIMPLIFIED",
    "HR" : "CROATIAN",
    "CS" : "CZECH",
    "DA" : "DANISH",
    "NL" : "DUTCH",
    "EN" : "ENGLISH",
    "EO" : "ESPERANTO",
    "ET" : "ESTONIAN",
    "FIL" : "FILIPINO",
    "FI" : "FINNISH",
    "FR" : "FRENCH",
    "KA" : "GEORGIAN",
    "DE" : "GERMAN",
    "EL" : "GREEK",
    "GRC" : "GREEK_ANCIENT",
    "HT" : "HAITIAN",
    "HE" : "HEBREW",
    "HI" : "HINDI",
    "HU" : "HUNGARIAN",
    "IS" : "ICELANDIC",
    "ID" : "INDONESIAN",
    "IT" : "ITALIAN",
    "JA" : "JAPANESE",
    "X-JAT" : "JAPANESE_TRANSLITERATED",
    "JV" : "JAVANESE",
    "KO" : "KOREAN",
    "X-KOT" : "KOREAN_TRANSLITERATED",
    "LA" : "LATIN",
    "LV" : "LATVIAN",
    "LT" : "LITHUANIAN",
    "MS" : "MALAY",
    "MN" : "MONGOLIAN",
    "NE" : "NEPALI",
    "NO" : "NORWEGIAN",
    "FA" : "PERSIAN",
    "PL" : "POLISH",
    "PT" : "PORTUGUESE",
    "PT-BR" : "PORTUGUESE_BRAZIL",
    "RO" : "ROMANIAN",
    "RU" : "RUSSIAN",
    "SR" : "SERBIAN",
    "SI" : "SINHALA",
    "SK" : "SLOVAK",
    "SL" : "SLOVENIAN",
    "ES" : "SPANISH",
    "ES-PV" : "SPANISH_BASQUE",
    "ES-CT" : "SPANISH_CATALAN",
    "ES-CA" : "SPANISH_CATALAN",
    "ES-GA" : "SPANISH_GALICIA",
    "ES-419" : "SPANISH_LATIN",
    "SV" : "SWEDISH",
    "TL" : "TAGALOG",
    "TA" : "TAMIL",
    "TT" : "TATAR",
    "TE" : "TELUGU",
    "TH" : "THAI",
    "X-THT" : "THAI_TRANSLITERATED",
    "TR" : "TURKISH",
    "UK" : "UKRAINIAN",
    "UR" : "URDU",
    "VI" : "VIETNAMESE",
    "X-UNK" : "UNKNOWN",
    "X-OTHER" : "OTHER"
}

class AniDBObj:
    def __init__(self, anidb, anidb_id, data, from_json=False):
        self._anidb = anidb
        self.anidb_id = anidb_id
        self._data = data
        self.main_title = None
        self.titles = []
        self.official_title = None
        self.studio = None
        self.rating = None
        self.average = None
        self.score = None
        self.released = None
        self.tags = {}
        self.mal_id = None
        self.imdb_id = None
        self.tmdb_id = None
        self.tmdb_type = None

        def _parseJSON(self):
            self.all_titles = data["titles"]
            for title in self.all_titles:
                if title["type"] == "MAIN":
                    self.main_title = title["title"]
                if title["type"] == "OFFICIAL":
                    self.titles.append(title)
                if title["type"] == "OFFICIAL" and self._anidb.language and (title["language"] == self._anidb.language.upper() or title["language"] == language_matcher[self._anidb.language.upper()]):
                    self.official_title = title["title"]
            if not self.official_title:
                self.official_title = self.main_title

            if "creators" in data:
                for creator_id, creators in data["creators"].items():
                    for creator in creators:
                        if creator["type"] == "ANIMATION_WORK":
                            self.studio = creator["name"]

            if "ratings" in data and "PERMANENT" in data["ratings"]:
                self.rating = float(data["ratings"]["PERMANENT"]["rating"])
            if "ratings" in data and "TEMPORARY" in data["ratings"]:
                self.average = float(data["ratings"]["TEMPORARY"]["rating"])
            if "ratings" in data and "REVIEW" in data["ratings"]:
                self.score = float(data["ratings"]["REVIEW"]["rating"])
            if "start_date" in data:
                self.released = datetime.strptime(data["start_date"], "%Y-%m-%d")

            if "tags" in data:
                for tag_id, tag in data["tags"].items():
                    if "info_box" in tag and (tag["info_box"] or tag["info_box"] == "true"):
                        self.tags[tag["name"]] = 1001
                    elif "weight" in tag:
                        self.tags[tag["name"]] = float(tag["weight"])

            if "resources" in data and "MAL" in data["resources"]:
                self.mal_id = int(data["resources"]["MAL"][0])
            if "resources" in data and "IMDB" in data["resources"]:
                self.imdb_id = data["resources"]["IMDB"][0]
            if "resources" in data and "TMDB" in data["resources"]:
                if data["resources"]["TMDB"][0].startswith("movie/"):
                    self.tmdb_id = int(data["resources"]["TMDB"][0][6:])
                    self.tmdb_type = "movie"
                elif data["resources"]["TMDB"][0].startswith("tv/"):
                    self.tmdb_id = int(data["resources"]["TMDB"][0][3:])
                    self.tmdb_type = "show"

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

        def _parseXML(self):
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

        if from_json:
            _parseJSON(self)
        else:
            _parseXML(self)

class AniDB:
    def __init__(self, config, data):
        self.config = config
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
        if self.config.Cache:
            value1, value2, success = self.config.Cache.query_testing("anidb_login")
            if str(value1) == str(client) and str(value2) == str(version) and success:
                return
        try:
            self.get_anime(69, ignore_cache=True)
            if self.config.Cache:
                self.config.Cache.update_testing("anidb_login", self.client, self.version, "True")
        except Failed:
            self.client = None
            self.version = None
            if self.config.Cache:
                self.config.Cache.update_testing("anidb_login", self.client, self.version, "False")
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
            return self.config.post_html(url, data=data, headers=util.header(self.language))
        else:
            return self.config.get_html(url, params=params, headers=util.header(self.language))

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
        from_json = False
        if self.config.Cache and not ignore_cache:
            anidb_dict, expired = self.config.Cache.query_anidb(anidb_id, self.expiration)
        if expired or not anidb_dict:
            if not ignore_cache:
                try:
                    anidb_dict = self.config.get_json(f"{cache_url}/{anidb_id}.json")
                    if anidb_dict:
                        from_json = True
                except ValueError:
                    pass
            if not from_json:
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
        obj = AniDBObj(self, anidb_id, anidb_dict, from_json)
        if self.config.Cache and not ignore_cache:
            self.config.Cache.update_anidb(expired, anidb_id, obj, self.expiration)
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
