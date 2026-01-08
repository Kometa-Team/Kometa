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
    "rank", "score", "score_average", "released", "releasedigital", "imdbrating", "imdbvotes", "imdbpopular", 
    "tmdbpopular", "rogerebert", "rtomatoes", "rtaudience", "metacritic", "myanimelist", "letterrating", "lettervotes",
    "last_air_date", "budget", "revenue", "runtime", "title", "sort_title", "random", "usort", "added"
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
            
            self.get_item(media_provider='imdb', media_type='movie', media_id="tt0080684", ignore_cache=True)
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
            if json_data.get('error') in ["API Limit Reached!", "API Rate Limit Reached!"]:
                self.limit = True
                raise LimitReached(f"MDBList Error: {json_data.get('error')}")
            raise Failed(f"MDBList Error: {json_data.get('error')}")
            
        return json_data, response.headers

    def get_item(self, media_provider=None, media_type=None, media_id=None, ignore_cache=False):

        is_movie = media_type == "movie"

        if media_provider == 'imdb':
            key = media_id
        elif media_provider == 'tmdb':
            key = f"{'tm' if is_movie else 'ts'}{media_id}"
        elif media_provider == 'tvdb':
            key = f"{'tvm' if is_movie else 'tvs'}{media_id}"
        else:
            raise Failed("MDBList Error: media_provider, media_type, media_id Required")

        expired = None

        item_url = f"{api_url}{media_provider}/{media_type}/{media_id}/"

        if self.cache and not ignore_cache:
            mdb_dict, expired = self.cache.query_mdb(key, self.expiration)
            if mdb_dict and expired is False:
                return MDbObj(mdb_dict)
        logger.trace(f"ID: {key}")
        mdb_tuple = self._request(item_url, params={})
        mdb = MDbObj(mdb_tuple[0])
        if self.cache and not ignore_cache:
            self.cache.update_mdb(expired, key, mdb, self.expiration)
        return mdb

    def get_imdb(self, imdb_id):
        return self.get_item(media_provider="imdb", media_type="movie", media_id=imdb_id)

    def get_series(self, tvdb_id):
        return self.get_item(media_provider="tvdb", media_type="show", media_id=tvdb_id)
 
    def get_movie(self, tmdb_id): 
        return self.get_item(media_provider="tmdb", media_type="movie", media_id=tmdb_id)

    def validate_mdblist_lists(self, error_type, mdb_lists):
        valid_lists = []
        for mdb_dict in util.get_list(mdb_lists, split=False):
            if not isinstance(mdb_dict, dict):
                mdb_dict = {"url": mdb_dict}
            
            url = mdb_dict.get("url", "").strip("/")
            if not url.startswith(base_url.strip("/")):
                raise Failed(f"{error_type} Error: {url} must start with {base_url}")

            list_object = {
                "url": url,
                "limit": int(mdb_dict.get("limit", 0))
            }

            if "sort_by" in mdb_dict:
                sort_by = mdb_dict["sort_by"]
                list_object["sort_by"] = sort_by

            valid_lists.append(list_object)

        return valid_lists

    def get_tmdb_ids(self, method, data, is_movie=None, filters=None):

        list_path = data["url"].split("/lists/")[-1].strip("/")

        external_id = list_path.split("/external/")[-1] if "/external/" in list_path else None

        total_items = 0

        items_url = f"{api_url}external/lists/{external_id}/items/" if external_id else f"{api_url}lists/{list_path}/items/"

        sort, direction = data["sort_by"].split(".") if "sort_by" in data else (None, None)
        results = []
        offset = 0
        limit_config = data.get("limit", 0)
        has_more = True

        params = {
            "limit": 1000,
        }

        if not external_id and is_movie is not None:
            items_url = f"{items_url}movie" if is_movie else f"{items_url}show"
        else:
            params["unified"] = True

        items = []

        while has_more:
            params["offset"] = offset

            if sort and direction:
                params["sort"] = sort
                params["sortorder"] = direction

            items = []

            try:
                page_data, headers = self._request(items_url, params=params)
                has_more = headers.get("X-Has-More", "false").lower() == "true"
                total_items = int(headers.get("X-Total-Items", 0))
                total_matched_items = int(headers.get("X-Matched-Items", 0))
                
                items = [] 
                if isinstance(page_data, dict):
                    if is_movie:
                        items = page_data.get("movies")
                    else:
                        items = page_data.get("shows")

                    if len(items) == 0 and "items" in page_data: # type: ignore
                        items = page_data["items"]

                elif isinstance(page_data, list):
                    items = page_data
            except Exception as e:
                raise Failed(f"MDBList Error: Could not fetch list items: {e}")

            for item in items: # type: ignore
                if 0 < limit_config <= len(results):
                    return results

                tmdb_id = util.check_num(item.get("id") or item.get("tmdbid"))
                if tmdb_id:
                    m_type = item.get("mediatype") or item.get("type") or "movie"
                    type_key = "tmdb" if m_type.lower() == "movie" else "tmdb_show"
                    results.append((tmdb_id, type_key))

            offset += len(items) # type: ignore
            
            if total_matched_items > 0:
                percent = int((len(results) / total_matched_items) * 100)
                logger.info(f"MDBList Sync Progress: {len(results)}/{total_matched_items} ({percent}%)")
            else:
                logger.info(f"MDBList Sync Progress: {len(results)} items processed...")

            if len(items) == 0: # type: ignore
                break

        return results
