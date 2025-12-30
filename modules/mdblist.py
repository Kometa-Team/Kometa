import time
from modules import util
from modules.util import Failed, LimitReached

logger = util.logger

# --- REQUIRED MODULE ATTRIBUTES ---
builders = ["mdblist_list"]
sort_names = [
    "rank", "score", "score_average", "released", "releaseddigital", "imdbrating", "imdbvotes", "imdbpopular",
    "tmdbpopular", "rogerebert", "rtomatoes", "rtaudience", "metacritic", "myanimelist", "letterrating", "lettervotes",
    "last_air_date", "budget", " revenue", "usort", "added", "runtime", "title", "random"
]
list_sorts = [f"{s}.asc" for s in sort_names] + [f"{s}.desc" for s in sort_names]


# --- CORRECT FQDN ---
api_url = "https://api.mdblist.com/"
base_url = "https://mdblist.com/lists/"

class MDbObj:
    def __init__(self, data):
        self._data = data
        self.title = data.get("title")
        self.year = util.check_num(data.get("release_year") or data.get("year"))
        self.type = data.get("mediatype") or data.get("type")
        self.tmdbid = util.check_num(data.get("id") or data.get("tmdbid"))
        self.imdbid = data.get("imdbid")

class MDBList:
    def __init__(self, requests, cache):
        self.requests = requests
        self.cache = cache
        self.apikey = None
        self.expiration = 60
        self.supporter = False
        self.patron = False
        self.api_requests = 0
        self.api_request_count = 0

    def add_key(self, apikey, expiration):
        self.apikey = apikey
        self.expiration = expiration
        try:
            # Verified FQDN for user check
            res, _ = self._request(f"{api_url}user")
            self.supporter = res.get("is_supporter", False)
            self.patron = res.get("patron_status", False)
            self.api_requests = res.get("api_requests", 0)
            self.api_requests_count = res.get("api_requests_count", 0)
    
            logger.info(f"MDBList Connection Verified (Supporter: {self.supporter})")
            logger.info(f"Patron Status: {self.patron}")
            logger.info(f"Daily API Requests: {self.api_requests}")
            logger.info(f"API Requests Used Today: {self.api_requests_count}")
            
        except Exception as e:
            self.apikey = None
            raise Failed(f"MDBList Key Initialization Failed: {e}")

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
