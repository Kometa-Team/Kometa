import time
from datetime import datetime
from json import JSONDecodeError
from modules import util
from modules.request import urlparse
from modules.util import Failed, LimitReached

logger = util.logger

# --- REQUIRED MODULE ATTRIBUTES ---
builders = ["mdblist_list"]
sort_names = [
    "rank", "score", "score_average", "released", "releaseddigital", "imdbrating", "imdbvotes", "imdbpopular",
    "tmdbpopular", "rogerebert", "rtomatoes", "rtaudience", "metacritic", "myanimelist", "letterrating", "lettervotes",
    "last_air_date", "usort", "added", "runtime", "budget", " revenue", "title", "random"
]
list_sorts = [f"{s}.asc" for s in sort_names] + [f"{s}.desc" for s in sort_names]

base_url = "https://mdblist.com/lists/"
api_url = "https://api.mdblist.com/"

headers = {"User-Agent": "Kometa"}

class MDbObj:
    def __init__(self, data):
        self._data = data
        self.title = data.get("title")
        self.year = util.check_num(data.get("release_year") or data.get("year"))
        self.type = data.get("mediatype") or data.get("type")
        self.tmdbid = util.check_num(data.get("id") or data.get("tmdbid"))
        self.imdbid = data.get("imdbid")

        try:
            self.released = datetime.strptime(data["released"], "%Y-%m-%d")
        except (ValueError, TypeError):
            self.released = None
        try:
            self.released_digital = datetime.strptime(data["released_digital"], "%Y-%m-%d")
        except (ValueError, TypeError):
            self.released_digital = None

        self.traktid = util.check_num(data.get("traktid"))
        self.tmdbid = util.check_num(data.get("tmdbid"))
        self.score = util.check_num(data.get("score"))
        self.average = util.check_num(data.get("score_average"))

        self.imdb_rating = None
        self.metacritic_rating = None
        self.metacriticuser_rating = None
        self.trakt_rating = None
        self.tomatoes_rating = None
        self.tomatoesaudience_rating = None
        self.tmdb_rating = None
        self.letterboxd_rating = None
        self.myanimelist_rating = None
        for rating in data.get("ratings", []):
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
        self.content_rating = data.get("certification")
        self.commonsense = data.get("commonsense")
        self.age_rating = data.get("age_rating")

class MDBList:
    def __init__(self, requests, cache):
        self.requests = requests
        self.cache = cache
        self.apikey = None
        self.expiration = 60
        self.limit = False
        self.supporter = False
        self.patron = False
        self.api_requests = 0
        self.api_request_count = 0
        self.supporter = False
        self.rating_id_limit = 10

    def add_key(self, apikey, expiration):
        self.apikey = apikey
        logger.secret(self.apikey)
        self.expiration = expiration
        try:
            response, _ = self._request(f"{api_url}user")
            logger.trace(f"MDB response: {response}")

            self.supporter = response.get("is_supporter", False)
            logger.info(f"Supporter Key: {self.supporter}")

            self.patron = response.get("patron_status", False)
            self.api_requests = response.get("api_requests", 0)
            self.api_requests_count = response.get("api_requests_count", 0)
    
            logger.info(f"MDBList Connection Verified (Supporter: {self.supporter})")
            logger.info(f"Patron Status: {self.patron}")
            logger.info(f"Daily API Requests: {self.api_requests}")
            logger.info(f"API Requests Used Today: {self.api_requests_count}")
            
            self.get_item(imdb_id="tt0080684", ignore_cache=True)
        except LimitReached:
            logger.info(f"MDBList API limit exhausted")
            self.limit = True
        except Failed as fe:
            logger.info(f"MDBList API connection failed: {fe}")
            self.apikey = None
            raise

    @property
    def has_key(self):
        return self.apikey is not None

    def _request(self, url, params=None):
        final_params = {"apikey": self.apikey}
        if params:
            final_params.update(params)
        
        # Respect API Rate limits
        time.sleep(0.2 if self.supporter else 1.0)
        
        response = self.requests.get(url, params=final_params)
        
        if response.status_code != 200:
            raise Failed(f"MDBList Error: {response.status_code} - {response.text}")
            
        json_data = response.json()
        if isinstance(json_data, dict) and json_data.get("response") is False:
            raise Failed(f"MDBList Error: {json_data.get('error')}")
            
        return json_data, response.headers

    def get_item(self, tmdb_id, is_movie=True):
        """Fetches a single item by TMDB ID with caching."""
        m_type = "movie" if is_movie else "show"
        cache_id = f"mdblist_{m_type}_{tmdb_id}"
        
        # Check cache first
        expired, expired_bool = self.cache.query_mdblist(cache_id, self.expiration)
        if expired and not expired_bool:
            return MDbObj(expired)
        
        # Fetch from API if not in cache or expired
        res, _ = self._request(f"{api_url}{m_type}/{tmdb_id}/")
        self.cache.update_mdblist(cache_id, res, self.expiration)
        return MDbObj(res)

    def get_series(self, tmdb_id):
        return self.get_item(tmdb_id, is_movie=False)

    def get_movie(self, tmdb_id):
        return self.get_item(tmdb_id, is_movie=True)

    def get_imdb(self, imdb_id):
        """Fetches an item by IMDB ID with caching."""
        cache_id = f"mdblist_imdb_{imdb_id}"
        expired, expired_bool = self.cache.query_mdblist(cache_id, self.expiration)
        if expired and not expired_bool:
            return MDbObj(expired)

        res, _ = self._request(api_url, params={"i": imdb_id})
        data = None
        if isinstance(res, list) and len(res) > 0:
            data = res[0]
        elif isinstance(res, dict) and "id" in res:
            data = res
            
        if data:
            self.cache.update_mdblist(cache_id, data, self.expiration)
            return MDbObj(data)
        return None

    def validate_mdblist_lists(self, error_type, mdb_lists):
        valid_lists = []
        for mdb_dict in util.get_list(mdb_lists, split=False):
            if not isinstance(mdb_dict, dict):
                mdb_dict = {"url": mdb_dict}
            
            url = mdb_dict.get("url", "").strip("/")
            if not url.startswith(base_url.strip("/")):
                raise Failed(f"{error_type} Error: {url} must start with {base_url}")
            
            valid_lists.append({
                "url": url,
                "limit": int(mdb_dict.get("limit", 0)),
                "sort_by": mdb_dict.get("sort_by", "rank.asc")
            })
        return valid_lists

    def get_tmdb_ids(self, method, data, is_movie=None, filters=None):
        list_path = data["url"].split("/lists/")[-1].strip("/")
        
        total_items = 0
        try:
            meta_url = f"{api_url}lists/{list_path}"
            meta_data, _ = self._request(meta_url)
            
            target_type = "movie" if is_movie is not None and is_movie else "show"
            if isinstance(meta_data, list):
                for list_meta in meta_data:
                    if list_meta.get("mediatype") == target_type:
                        total_items = list_meta.get("items", 0)
                        break
            
            if total_items > 0:
                logger.info(f"MDBList Sync: Found {total_items} {target_type}s in '{list_path}'")
        except Exception as e:
            logger.debug(f"MDBList: Could not fetch list metadata: {e}")

        items_url = f"{api_url}lists/{list_path}/items/"
        sort, direction = data["sort_by"].split(".")
        results = []
        offset = 0
        limit_config = data.get("limit", 0)
        has_more = True

        while has_more:
            params = {
                "offset": offset,
                "limit": 1000,
                "sort": sort,
                "sortorder": direction
            }
            if is_movie is not None:
                params["mediatype"] = "movie" if is_movie else "show"

            page_data, headers = self._request(items_url, params=params)
            has_more = headers.get("X-Has-More", "false").lower() == "true"
            
            items = []
            if isinstance(page_data, dict):
                items = page_data.get("movies", page_data.get("shows", page_data.get("items", [])))
            elif isinstance(page_data, list):
                items = page_data

            if not items:
                break

            for item in items:
                if 0 < limit_config <= len(results):
                    return results

                tmdb_id = util.check_num(item.get("id") or item.get("tmdbid"))
                if tmdb_id:
                    m_type = item.get("mediatype") or item.get("type") or "movie"
                    type_key = "tmdb" if m_type.lower() == "movie" else "tmdb_show"
                    results.append((tmdb_id, type_key))

            offset += len(items)
            
            if total_items > 0:
                percent = int((len(results) / total_items) * 100)
                logger.info(f"MDBList Sync Progress: {len(results)}/{total_items} ({percent}%)")
            else:
                logger.info(f"MDBList Sync Progress: {len(results)} items processed...")

            if len(items) == 0:
                break

        return results
