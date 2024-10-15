import time
from datetime import datetime
from json import JSONDecodeError
from modules import util
from modules.request import urlparse
from modules.util import Failed, LimitReached

logger = util.logger

builders = ["mdblist_list"]
sort_names = [
    "rank", "score", "score_average", "released", "imdbrating", "imdbvotes", "imdbpopular", "tmdbpopular",
    "rogerebert", "rtomatoes", "rtaudience", "metacritic", "myanimelist", "letterrating", "lettervotes", 
    "updated", "last_air_date", "watched", "rating", "usort", "added", "runtime", "budget", "revenue", "title"
]
list_sorts = [f"{s}.asc" for s in sort_names] + [f"{s}.desc" for s in sort_names]
base_url = "https://mdblist.com/lists"
api_url = "https://mdblist.com/api/"

headers = {"User-Agent": "Kometa"}

class MDbObj:
    def __init__(self, data):
        self._data = data
        self.title = data["title"]
        self.year = util.check_num(data["year"])
        try:
            self.released = datetime.strptime(data["released"], "%Y-%m-%d")
        except (ValueError, TypeError):
            self.released = None
        try:
            self.released_digital = datetime.strptime(data["released_digital"], "%Y-%m-%d")
        except (ValueError, TypeError):
            self.released_digital = None
        self.type = data["type"]
        self.imdbid = data["imdbid"]
        self.traktid = util.check_num(data["traktid"])
        self.tmdbid = util.check_num(data["tmdbid"])
        self.score = util.check_num(data["score"])
        self.average = util.check_num(data["score_average"])
        self.imdb_rating = None
        self.metacritic_rating = None
        self.metacriticuser_rating = None
        self.trakt_rating = None
        self.tomatoes_rating = None
        self.tomatoesaudience_rating = None
        self.tmdb_rating = None
        self.letterboxd_rating = None
        self.myanimelist_rating = None
        for rating in data["ratings"]:
            if rating["source"] == "imdb":
                self.imdb_rating = util.check_num(rating["value"], is_int=False)
            elif rating["source"] == "metacritic":
                self.metacritic_rating = util.check_num(rating["value"])
            elif rating["source"] == "metacriticuser":
                self.metacriticuser_rating = util.check_num(rating["value"], is_int=False)
            elif rating["source"] == "trakt":
                self.trakt_rating = util.check_num(rating["value"])
            elif rating["source"] == "tomatoes":
                self.tomatoes_rating = util.check_num(rating["value"])
            elif rating["source"] == "tomatoesaudience":
                self.tomatoesaudience_rating = util.check_num(rating["value"])
            elif rating["source"] == "tmdb":
                self.tmdb_rating = util.check_num(rating["value"])
            elif rating["source"] == "letterboxd":
                self.letterboxd_rating = util.check_num(rating["value"], is_int=False)
            elif rating["source"] == "myanimelist":
                self.myanimelist_rating = util.check_num(rating["value"], is_int=False)
        self.content_rating = data["certification"]
        self.commonsense = data["commonsense"]
        self.age_rating = data["age_rating"]


class MDBList:
    def __init__(self, requests, cache):
        self.requests = requests
        self.cache = cache
        self.apikey = None
        self.expiration = 60
        self.limit = False
        self.supporter = False
        self.rating_id_limit = 10

    def add_key(self, apikey, expiration):
        self.apikey = apikey
        logger.secret(self.apikey)
        self.expiration = expiration
        try:
            response = self._request(f"{api_url}user")
            self.supporter = response["limits"]["supporter"]
            self.rating_id_limit = response["limits"]["rating_ids"]
            self.get_item(imdb_id="tt0080684", ignore_cache=True)
        except LimitReached:
            self.limit = True
        except Failed:
            self.apikey = None
            raise

    @property
    def has_key(self):
        return self.apikey is not None

    def _request(self, url, params=None):
        logger.trace(url)
        final_params = {"apikey": self.apikey}
        if params:
            logger.trace(f"Params: {params}")
            for k, v in params.items():
                final_params[k] = v
        try:
            time.sleep(0.2 if self.supporter else 1)
            response = self.requests.get_json(url, params=final_params)
        except JSONDecodeError:
            raise Failed("MDBList Error: JSON Decoding Failed")
        if "response" in response and (response["response"] is False or response["response"] == "False"):
            if response["error"] in ["API Limit Reached!", "API Rate Limit Reached!"]:
                self.limit = True
                raise LimitReached(f"MDBList Error: {response['error']}")
            raise Failed(f"MDBList Error: {response['error']}")
        return response

    def get_item(self, imdb_id=None, tmdb_id=None, tvdb_id=None, is_movie=True, ignore_cache=False):
        params = {}
        if imdb_id:
            params["i"] = imdb_id
            key = imdb_id
        elif tmdb_id:
            params["tm"] = tmdb_id
            params["m"] = "movie" if is_movie else "show"
            key = f"{'tm' if is_movie else 'ts'}{tmdb_id}"
        elif tvdb_id:
            params["tv"] = tvdb_id
            params["m"] = "movie" if is_movie else "show"
            key = f"{'tvm' if is_movie else 'tvs'}{tvdb_id}"
        else:
            raise Failed("MDBList Error: Either IMDb ID, TVDb ID, or TMDb ID and TMDb Type Required")
        expired = None
        if self.cache and not ignore_cache:
            mdb_dict, expired = self.cache.query_mdb(key, self.expiration)
            if mdb_dict and expired is False:
                return MDbObj(mdb_dict)
        logger.trace(f"ID: {key}")
        mdb = MDbObj(self._request(api_url, params=params))
        if self.cache and not ignore_cache:
            self.cache.update_mdb(expired, key, mdb, self.expiration)
        return mdb

    def get_imdb(self, imdb_id):
        return self.get_item(imdb_id=imdb_id)

    def get_series(self, tvdb_id):
        return self.get_item(tvdb_id=tvdb_id, is_movie=False)

    def get_movie(self, tmdb_id):
        return self.get_item(tmdb_id=tmdb_id, is_movie=True)

    def validate_mdblist_lists(self, error_type, mdb_lists):
        valid_lists = []
        for mdb_dict in util.get_list(mdb_lists, split=False):
            if not isinstance(mdb_dict, dict):
                mdb_dict = {"url": mdb_dict}
            dict_methods = {dm.lower(): dm for dm in mdb_dict}
            if "url" not in dict_methods:
                raise Failed(f"{error_type} Error: mdb_list url attribute not found")
            elif mdb_dict[dict_methods["url"]] is None:
                raise Failed(f"{error_type} Error: mdb_list url attribute is blank")
            else:
                mdb_url = mdb_dict[dict_methods["url"]].strip()
            if not mdb_url.startswith(base_url):
                raise Failed(f"{error_type} Error: {mdb_url} must begin with: {base_url}")
            list_count = None
            if "limit" in dict_methods:
                if mdb_dict[dict_methods["limit"]] is None:
                    logger.warning(f"{error_type} Warning: mdb_list limit attribute is blank using 0 as default")
                else:
                    try:
                        value = int(str(mdb_dict[dict_methods["limit"]]))
                        if 0 <= value:
                            list_count = value
                    except ValueError:
                        pass
                if list_count is None:
                    logger.warning(f"{error_type} Warning: mdb_list limit attribute must be an integer 0 or greater using 0 as default")
            if list_count is None:
                list_count = 0
            sort_by = "rank.asc"
            if "sort_by" in dict_methods:
                if mdb_dict[dict_methods["sort_by"]] is None:
                    logger.warning(f"{error_type} Warning: mdb_list sort_by attribute is blank using score as default")
                elif mdb_dict[dict_methods["sort_by"]].lower() in sort_names:
                    logger.warning(f"{error_type} Warning: mdb_list sort_by attribute {mdb_dict[dict_methods['sort_by']]} is missing .desc or .asc defaulting to .desc")
                    sort_by = f"{mdb_dict[dict_methods['sort_by']].lower()}.desc"
                elif mdb_dict[dict_methods["sort_by"]].lower() not in list_sorts:
                    logger.warning(f"{error_type} Warning: mdb_list sort_by attribute {mdb_dict[dict_methods['sort_by']]} not valid score as default. Options: {', '.join(list_sorts)}")
                else:
                    sort_by = mdb_dict[dict_methods["sort_by"]].lower()
            valid_lists.append({"url": mdb_url, "limit": list_count, "sort_by": sort_by})
        return valid_lists

    def get_tmdb_ids(self, method, data, is_movie=None):
        if method == "mdblist_list":
            logger.info(f"Processing MDBList.com List: {data['url']}")
            logger.info(f"Sort By: {data['sort_by']}")
            sort, direction = data["sort_by"].split(".")
            params = {"sort": sort, "sortorder": direction}
            if is_movie is not None:
                params["mediatype"] = "movie" if is_movie else "show"
            if data["limit"] > 0:
                logger.info(f"Limit: {data['limit']} items")
                params["limit"] = data["limit"]
            parsed_url = urlparse(data["url"])
            url_base = str(parsed_url._replace(query=None).geturl()) # noqa
            url_base = url_base if url_base.endswith("/") else f"{url_base}/"
            url_base = url_base if url_base.endswith("json/") else f"{url_base}json/"
            try:
                response = self.requests.get_json(url_base, headers=headers, params=params)
                if (isinstance(response, dict) and "error" in response) or (isinstance(response, list) and response and "error" in response[0]):
                    err = response["error"] if isinstance(response, dict) else response[0]["error"]
                    if err in ["empty", "empty or private list"]:
                        raise Failed(f"MDBList Error: No Items Returned. Lists can take 24 hours to update so try again later.")
                    raise Failed(f"MDBList Error: Invalid Response {response}")
                results = []
                for item in response:
                    if item["mediatype"] in ["movie", "show"] and item["id"]:
                        results.append((item["id"], "tmdb" if item["mediatype"] == "movie" else "tmdb_show"))
                return results
            except JSONDecodeError:
                raise Failed(f"MDBList Error: Invalid JSON Response received")
        else:
            raise Failed(f"MDBList Error: Method {method} not supported")
