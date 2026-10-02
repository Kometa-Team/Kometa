from modules import tracker, util
from modules.util import Failed

logger = util.logger

base_url = "https://flicklist.tv/api/v3"
sync_batch_size = 1000
max_retry_after_seconds = 120.0
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


class FlickList(tracker.TrackerAPI):
    service = "FlickList"
    base_url = base_url
    page_count_header = "X-FlickList-Page-Count"

    def __init__(self, requests, read_only, params):
        super().__init__(requests, read_only)
        self.api_key = params["api_key"]
        if logger:
            logger.secret(self.api_key)
        self.user_agent = f"Kometa/{self.requests.local} (+https://kometa.wiki)"
        self._me = None
        self._ratings = None
        self._ratings_error = None
        self._user_ratings = {}
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

    def _raise_for_status(self, path, response, ignore_404):
        if response.status_code == 401:
            raise Failed("FlickList Error: API key was rejected; it may have been revoked. Mint a new one and update your config.")
        if response.status_code == 403:
            raise Failed(f"FlickList Error: API key is missing a required scope for {path}")
        return super()._raise_for_status(path, response, ignore_404)

    @staticmethod
    def _type_of(item):
        raw = str(item.get("media_type") or "").lower()
        if raw == "movie":
            return "movie"
        if raw in ("tv", "show"):
            return "show"
        return None

    def _parse_ids(self, items, is_movie=None):
        return tracker.parse_ids(
            items,
            is_movie,
            service=self.service,
            type_of=self._type_of,
            native_id_of=lambda item: (item.get("ids") or {}).get("fldb"),
        )

    @staticmethod
    def _candidate_keys(ids_block, media_type, convert):
        return tracker.candidate_keys(ids_block, media_type, convert, native=("fldb", ids_block.get("fldb")))

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
        return tracker.validate_flag(err_type, method_name, method_data)

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
        return tracker.validate_rating_range(err_type, "flicklist_ratings", method_data)

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
            for item in self._all_ratings():
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

    def _all_ratings(self):
        # One /sync/ratings read per run (a failed read is remembered too), so mass ratings never re-download the list per item.
        if self._ratings_error is not None:
            raise self._ratings_error
        ratings = self._ratings
        if ratings is None:
            try:
                ratings = self._request_list("/sync/ratings")
            except Failed as e:
                self._ratings_error = e
                raise
            self._ratings = ratings
        return ratings

    def user_ratings(self, is_movie):
        """Return ratings keyed by TMDb ID for movies and TVDb ID for shows."""
        if is_movie in self._user_ratings:
            return self._user_ratings[is_movie]
        id_type = "tmdb" if is_movie else "tvdb"
        ratings = {}
        for item in self._all_ratings():
            item_media = str(item.get("media_type") or "").lower()
            if is_movie and item_media != "movie":
                continue
            if not is_movie and item_media not in ("tv", "show"):
                continue
            rating = item.get("rating")
            item_id = (item.get("ids") or {}).get(id_type)
            if rating is None or not item_id:
                continue
            ratings[int(item_id)] = rating
        self._user_ratings[is_movie] = ratings
        return ratings

    def _resolve_list(self, list_id_or_name):
        """Returns (list_id, created). Matches an existing list by numeric id or exact name; creates one if no match."""
        as_id = None
        if isinstance(list_id_or_name, int) and not isinstance(list_id_or_name, bool):
            as_id = list_id_or_name
        else:
            text = str(list_id_or_name).strip()
            if text.isdigit():
                as_id = int(text)
        own_lists = self._request_paginated("/sync/lists") or []
        if as_id is not None:
            for entry in own_lists:
                if entry.get("id") == as_id:
                    return as_id, False
            raise Failed(f"FlickList Error: List id {as_id} not found among your own lists")
        name = str(list_id_or_name).strip()
        for entry in own_lists:
            if str(entry.get("name") or "").strip() == name:
                return entry.get("id"), False
        created = self._request("/sync/lists", json_data={"name": name, "privacy": "private"}, method="POST")
        new_id = created.get("id") if created else None
        if new_id is None:
            raise Failed(f"FlickList Error: Could not create list '{name}'")
        return new_id, True

    @staticmethod
    def _media_type_of(item):
        raw = str(item.get("media_type") or "").lower()
        return "show" if raw in ("tv", "show") else "movie"

    def _sync_batch(self, list_id, action, payloads):
        if not payloads:
            return
        method = "POST" if action == "add" else "DELETE"
        not_found_total = 0
        for start in range(0, len(payloads), sync_batch_size):
            chunk = payloads[start : start + sync_batch_size]
            results = self._request(f"/sync/lists/{list_id}/items", json_data={"items": chunk}, method=method) or {}
            existing_items = results.get("existing") or []
            not_found_items = results.get("not_found") or []
            not_found_total += len(not_found_items)
            # `added`/`removed` counts from the API are not reliable net-new/net-removed totals (duplicate submissions in one batch double-count) - the batch size below is the trustworthy number.
            if existing_items and logger:
                logger.debug(f"FlickList List: {len(existing_items)} item(s) in this batch were already present: {existing_items}")
            if not_found_items and logger:
                shown, remaining = not_found_items[:20], len(not_found_items) - 20
                suffix = f" (+{remaining} more)" if remaining > 0 else ""
                logger.error(f"FlickList Error: {len(not_found_items)} item(s) not found while syncing: {shown}{suffix}")
        if logger:
            verb = "add" if action == "add" else "remove"
            logger.info(f"FlickList List: submitted {len(payloads)} item(s) to {verb} ({not_found_total} not found)")

    def sync_list(self, convert, list_id_or_name, ids):
        """ids: iterable of (ids_block, media_type) pairs, e.g. ({"tmdb": 550}, "movie").

        Matching is by candidate-key-set intersection via tracker.plan_list_sync - see its
        docstring for why. This method keeps list resolution, the current-items fetch, logging
        and batching; the diff itself lives in the shared layer.
        """
        list_id, created = self._resolve_list(list_id_or_name)
        if created and logger:
            logger.info(f"FlickList List '{list_id_or_name}' not found; created a new list (id {list_id})")
        current_items = self._request_paginated(f"/sync/lists/{list_id}/items") or []
        add, remove, unmatched = tracker.plan_list_sync(
            ids,
            current_items,
            convert,
            ids_of=lambda item: item.get("ids") or {},
            type_of=self._media_type_of,
            native_id_of=lambda ids_block: ("fldb", ids_block.get("fldb")),
        )
        if unmatched and logger:
            logger.warning(f"FlickList Warning: {unmatched} existing list item(s) had no usable id at all; leaving them in place")
        add_payloads = [{"ids": ids_block, "media_type": media_type} for ids_block, media_type in add]
        remove_payloads = [{"ids": item_ids, "media_type": media_type} for item_ids, media_type in remove]
        self._sync_batch(list_id, "add", add_payloads)
        self._sync_batch(list_id, "remove", remove_payloads)
