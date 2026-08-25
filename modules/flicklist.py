import time

from modules import util
from modules.util import Failed

logger = util.logger

base_url = "https://flicklist.tv/api/v3"
builders = [
    "flicklist_list",
    "flicklist_list_details",
    "flicklist_user_lists",
    "flicklist_watchlist",
    "flicklist_favorites",
    "flicklist_watched",
    "flicklist_ratings",
    "flicklist_up_next",
    "flicklist_tracked",
]
show_only_methods = ["flicklist_up_next", "flicklist_tracked"]


class FlickList:
    def __init__(self, requests, read_only, params):
        self.requests = requests
        self.read_only = read_only
        self.api_key = params["api_key"]
        if logger:
            logger.secret(self.api_key)
        self.user_agent = f"Kometa/{self.requests.local} (+https://kometa.wiki)"
        self._me = None
        # No network I/O here; modules/config.py calls test_connection() separately so a failed connect can be neutered without a half-built object.

    def test_connection(self):
        me = self._request("/me")
        self._me = me if isinstance(me, dict) else {}
        username = self._me.get("username")
        if logger:
            logger.info(f"FlickList Connected as {username}" if username else "FlickList Connection Successful")

    def _headers(self, anonymous=False):
        headers = {"Content-Type": "application/json", "User-Agent": self.user_agent}
        if not anonymous:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    @staticmethod
    def _parse_error_body(response):
        try:
            payload = response.json()
            return payload.get("detail") or payload.get("error") or response.reason
        except ValueError:
            return response.text[:200] if response.text else response.reason

    def _send(self, path, url, headers, params, json_data, method):
        attempts = 0
        while True:
            if method == "POST":
                response = self.requests.post(url, json=json_data, headers=headers)
            else:
                response = self.requests.get(url, headers=headers, params=params)
            if response.status_code != 429:
                return response
            attempts += 1
            if attempts >= 3:
                raise Failed(f"FlickList Error: Rate limited on {path} after 3 attempts this run; giving up for now")
            retry_after = response.headers.get("Retry-After")
            try:
                wait_seconds = float(retry_after)
            except (TypeError, ValueError):
                wait_seconds = 60.0
            if logger:
                logger.warning(f"FlickList Warning: Rate limited on {path}; waiting {wait_seconds} seconds")
            time.sleep(wait_seconds)

    def _raise_for_status(self, path, response, ignore_404):
        if response.status_code == 401:
            raise Failed("FlickList Error: API key was rejected; it may have been revoked. Mint a new one and update your config.")
        if response.status_code == 403:
            raise Failed(f"FlickList Error: API key is missing a required scope for {path}")
        if response.status_code == 404 and ignore_404:
            return True
        if response.status_code >= 400:
            raise Failed(f"FlickList Error: ({response.status_code}) {self._parse_error_body(response)}")
        return False

    def _request_raw(self, path, params=None, json_data=None, method="GET", anonymous=False, ignore_404=False):
        """Single call, no pagination. Returns whatever the endpoint sends back (dict, list, or None on a swallowed 404)."""
        url = f"{base_url}{path}"
        if logger:
            logger.trace(f"URL: {url}")
            if params:
                logger.trace(f"Params: {params}")
            if json_data is not None:
                logger.trace(f"JSON: {json_data}")
        headers = self._headers(anonymous=anonymous)
        response = self._send(path, url, headers, params, json_data, method)
        if self._raise_for_status(path, response, ignore_404):
            return None
        if response.status_code == 204 or not response.content:
            return None
        try:
            return response.json()
        except ValueError:
            raise Failed(f"FlickList Error: {path} returned a non-JSON response body")

    def _request(self, path, params=None, json_data=None, method="GET", anonymous=False, ignore_404=False):
        """Single-call request against an object-returning endpoint. Always returns a dict, or None when ignore_404 swallowed a 404."""
        data = self._request_raw(path, params=params, json_data=json_data, method=method, anonymous=anonymous, ignore_404=ignore_404)
        if data is None:
            return None
        return data if isinstance(data, dict) else {}

    def _request_list(self, path, params=None, anonymous=False):
        """Single-call request against an array-returning endpoint (the un-paginated 'None' family). Always returns a list; a 404/204/empty body is treated as an empty list."""
        data = self._request_raw(path, params=params, anonymous=anonymous)
        return data if isinstance(data, list) else []

    def _request_paginated(self, path, params=None, anonymous=False, ignore_404=False):
        """Multi-page request against the header-paginated family. Always returns a list, or None when ignore_404 swallowed a 404."""
        url = f"{base_url}{path}"
        if logger:
            logger.trace(f"URL: {url}")
            if params:
                logger.trace(f"Params: {params}")
        headers = self._headers(anonymous=anonymous)
        results = []
        page = 1
        page_count = 1
        while page <= page_count:
            call_params = dict(params) if params else None
            if page > 1:
                call_params = call_params or {}
                call_params["page"] = page
            response = self._send(path, url, headers, call_params, None, "GET")
            if self._raise_for_status(path, response, ignore_404):
                return None
            if response.status_code == 204 or not response.content:
                return []
            try:
                data = response.json()
            except ValueError:
                raise Failed(f"FlickList Error: {path} returned a non-JSON response body")
            if isinstance(data, list):
                results.extend(data)
            elif isinstance(data, dict):
                results.append(data)
            if page == 1:
                if logger:
                    logger.trace(f"Limit: {response.headers.get('X-FlickList-Limit')}")
                try:
                    page_count = int(response.headers.get("X-FlickList-Page-Count", 1))
                except (TypeError, ValueError):
                    page_count = 1
            page += 1
        return results

    def _parse_ids(self, items, is_movie=None):
        ids = []
        seen = set()
        for item in items or []:
            ids_block = item.get("ids") or {}
            media_type = str(item.get("media_type") or "").lower()
            is_show = media_type in ("tv", "show")
            is_item_movie = media_type == "movie"
            if is_movie is True and not is_item_movie:
                continue
            if is_movie is False and not is_show:
                continue
            tmdb_id = ids_block.get("tmdb")
            tvdb_id = ids_block.get("tvdb")
            imdb_id = ids_block.get("imdb")
            fldb_id = ids_block.get("fldb")
            if is_item_movie and tmdb_id:
                key = (int(tmdb_id), "tmdb")
            elif is_show and tmdb_id:
                key = (int(tmdb_id), "tmdb_show")
            elif is_show and tvdb_id:
                key = (int(tvdb_id), "tvdb")
            elif imdb_id:
                # Kometa's Convert layer resolves imdb-only ids downstream; a GET /v3/find/{id} call here would spend the one genuinely expensive read on every read, not just unresolved ones.
                key = (str(imdb_id), "imdb")
            else:
                title = item.get("title") or item.get("name") or fldb_id or "Unknown"
                if logger:
                    logger.warning(f"FlickList Warning: No usable ID found for {title}; skipping")
                continue
            dedupe_key = fldb_id or key
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            ids.append(key)
        return ids

    @staticmethod
    def _normalize_watched_movie(item):
        """WatchedMovie carries a top-level `ids` block but no `media_type` field at all - the
        endpoint is movie-only by construction, so the schema omits it. _parse_ids relies on
        `media_type` to classify each item, so every watched movie was silently dropped (matched
        neither the movie nor show branch) until this tagged it explicitly."""
        item = dict(item)
        item["media_type"] = "movie"
        return item

    @staticmethod
    def _normalize_watched_show(item):
        """WatchedShow has no top-level `media_type` OR `ids` - both live one level down, under
        `show` ({"show": {"title": ..., "ids": {...}}, "plays": ..., "seasons": [...]}). Unwrap it
        and tag the type so _parse_ids has an `ids` block to look at at all, not just a type to
        classify it by - without this every watched show was silently dropped twice over."""
        show = dict(item.get("show") or {})
        show["media_type"] = "tv"
        return show

    @staticmethod
    def _parse_list_id(value):
        if isinstance(value, bool):
            raise Failed(f"FlickList Error: Could not parse a list id from {value}")
        if isinstance(value, int):
            return value
        text = str(value).strip()
        if text.isdigit():
            return int(text)
        candidate = text.rstrip("/").rsplit("/", 1)[-1]
        if candidate.isdigit():
            return int(candidate)
        raise Failed(f"FlickList Error: Could not parse a list id from {value}")

    def validate_lists(self, err_type, method_data):
        valid_ids = []
        for value in util.get_list(method_data, split=False, return_none=False):
            if isinstance(value, dict):
                raise Failed(f"{err_type} Error: FlickList List cannot be a dictionary")
            valid_ids.append(self._parse_list_id(value))
        if not valid_ids:
            raise Failed(f"{err_type} Error: No valid FlickList Lists")
        return valid_ids

    @staticmethod
    def validate_username(err_type, method_data):
        if isinstance(method_data, dict) or not str(method_data).strip():
            raise Failed(f"{err_type} Error: flicklist_user_lists requires a username")
        return str(method_data).strip()

    @staticmethod
    def validate_flag(err_type, method_name, method_data):
        """True/blank enables the builder; explicit false just leaves it out, same as omitting the
        attribute - erroring on `method_name: false` punished a value config.yml owners can reach
        for naturally (e.g. templating a shared block where one library sets a flag off)."""
        if method_data is None:
            return True
        return util.parse(err_type, method_name, method_data, datatype="bool", default=True)

    @staticmethod
    def validate_up_next(err_type, method_data):
        if method_data is None or isinstance(method_data, bool):
            return None
        try:
            limit = int(method_data)
        except (TypeError, ValueError):
            raise Failed(f"{err_type} Error: flicklist_up_next must be blank, true, or an integer limit")
        if limit < 1:
            raise Failed(f"{err_type} Error: flicklist_up_next limit must be a positive integer")
        return limit

    @staticmethod
    def validate_ratings(err_type, method_data):
        def to_float(value, label):
            try:
                return float(value)
            except (TypeError, ValueError):
                raise Failed(f"{err_type} Error: flicklist_ratings {label} must be a number")

        if method_data is None or isinstance(method_data, bool):
            return {"minimum": None, "maximum": None}
        if isinstance(method_data, dict):
            dict_methods = {dm.lower(): dm for dm in method_data}
            minimum = to_float(method_data[dict_methods["minimum"]], "minimum") if "minimum" in dict_methods else None
            maximum = to_float(method_data[dict_methods["maximum"]], "maximum") if "maximum" in dict_methods else None
            return {"minimum": minimum, "maximum": maximum}
        return {"minimum": to_float(method_data, "minimum"), "maximum": None}

    def _list_items(self, list_id):
        return self._request_paginated(f"/lists/{list_id}/items")

    def list_description(self, list_id):
        data = self._request(f"/lists/{list_id}") or {}
        return data.get("description") or ""

    def _user_lists_ids(self, username, is_movie):
        lists = self._request_paginated(f"/users/{username}/lists", anonymous=True, ignore_404=True)
        if lists is None:
            raise Failed(f"FlickList Error: User {username} not found")
        if not lists:
            raise Failed(f"FlickList Error: User {username} has no public lists")
        if logger:
            logger.info(f"Processing FlickList User Lists: {len(lists)} lists from {username}")
        ids = []
        seen = set()
        for entry in lists:
            list_id = entry.get("id")
            if list_id is None:
                continue
            for item_id in self._parse_ids(self._list_items(list_id), is_movie=is_movie):
                if item_id not in seen:
                    seen.add(item_id)
                    ids.append(item_id)
        return ids

    @staticmethod
    def _log_info(message):
        if logger:
            logger.info(message)

    def get_flicklist_ids(self, method, value, is_movie):
        pretty = method.replace("_", " ").title()
        if method in ("flicklist_list", "flicklist_list_details"):
            self._log_info(f"Processing {pretty}: {value}")
            return self._parse_ids(self._list_items(value), is_movie=is_movie)
        if method == "flicklist_user_lists":
            return self._user_lists_ids(value, is_movie)
        if method == "flicklist_watchlist":
            self._log_info(f"Processing {pretty}")
            return self._parse_ids(self._request_list("/sync/watchlist"), is_movie=is_movie)
        if method == "flicklist_favorites":
            self._log_info(f"Processing {pretty}")
            return self._parse_ids(self._request_list("/sync/favorites"), is_movie=is_movie)
        if method == "flicklist_watched":
            self._log_info(f"Processing {pretty}")
            items = []
            if is_movie is not False:
                items.extend(self._normalize_watched_movie(item) for item in self._request_list("/sync/watched/movies"))
            if is_movie is not True:
                items.extend(self._normalize_watched_show(item) for item in self._request_list("/sync/watched/shows"))
            return self._parse_ids(items, is_movie=is_movie)
        if method == "flicklist_ratings":
            self._log_info(f"Processing {pretty}")
            minimum = value.get("minimum") if isinstance(value, dict) else None
            maximum = value.get("maximum") if isinstance(value, dict) else None
            filtered = []
            for item in self._request_list("/sync/ratings"):
                rating = item.get("rating")
                if rating is None:
                    continue
                if minimum is not None and rating < minimum:
                    continue
                if maximum is not None and rating > maximum:
                    continue
                filtered.append(item)
            return self._parse_ids(filtered, is_movie=is_movie)
        if method == "flicklist_up_next":
            self._log_info(f"Processing {pretty}")
            params = {"limit": value} if value else None
            return self._parse_ids(self._request_list("/sync/up_next", params=params), is_movie=False)
        if method == "flicklist_tracked":
            self._log_info(f"Processing {pretty}")
            return self._parse_ids(self._request_list("/sync/tracked"), is_movie=False)
        raise Failed(f"FlickList Error: Method {method} not supported")
