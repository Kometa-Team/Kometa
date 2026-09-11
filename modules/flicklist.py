import time

from modules import util
from modules.request import DEFAULT_TIMEOUT
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
            elif method == "DELETE":
                # No Requests.delete() wrapper exists yet; the raw session skips the tenacity retry get()/post() carry, but the 429 loop below still applies.
                response = self.requests.session.delete(url, json=json_data, headers=headers, timeout=DEFAULT_TIMEOUT)
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
            if wait_seconds > max_retry_after_seconds:
                # FlickList's own 1,000/hr limit (documented in docs/config/flicklist.md) means a legitimate Retry-After can be up to an hour;
                # sleeping the run for that long is worse than failing fast and letting the next scheduled run pick it up.
                raise Failed(f"FlickList Error: Rate limited on {path}; server asked us to wait {wait_seconds:.0f} seconds (over the {max_retry_after_seconds:.0f}s cap) - giving up for now rather than blocking the run")
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

    def user_ratings(self, is_movie):
        """Mirrors Trakt.user_ratings: {tmdb_id: rating} for movies, {tvdb_id: rating} for shows."""
        id_type = "tmdb" if is_movie else "tvdb"
        ratings = {}
        for item in self._request_list("/sync/ratings"):
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
    def _candidate_keys(ids_block, media_type, convert):
        """Every identifier this item could plausibly be matched on, not just one 'best' key.
        The old design picked a single best key per side (tmdb first, then fldb, then imdb, then
        tvdb) and compared those. That breaks whenever the two sides expose different id types for
        the same title - e.g. a desired show whose tvdb->tmdb Convert lookup misses this run (rate
        limited or not yet cached) falls back to a bare tvdb key, while the matching FlickList item
        already carries a native tmdb id and never even looks at its own tvdb value under the old
        priority order. Two keys for the same title that never intersect reads as "not present",
        so the real item gets deleted and a duplicate gets added in its place. Returning the full
        set of candidates and matching on intersection means any single shared id is enough to
        recognize the same item on both sides, regardless of which id each side happened to key on.
        Returns an empty set only when the ids block carries nothing usable at all."""
        keys = set()
        tmdb_id = ids_block.get("tmdb")
        if tmdb_id is not None:
            keys.add((media_type, "tmdb", int(tmdb_id)))
        tvdb_id = ids_block.get("tvdb")
        if tvdb_id is not None:
            keys.add((media_type, "tvdb", tvdb_id))
            if media_type == "show" and convert is not None:
                resolved = convert.tvdb_to_tmdb(tvdb_id)
                if resolved is not None:
                    keys.add((media_type, "tmdb", int(resolved)))
        imdb_id = ids_block.get("imdb")
        if imdb_id is not None:
            keys.add((media_type, "imdb", imdb_id))
            if convert is not None:
                resolved, resolved_type = convert.imdb_to_tmdb(imdb_id)
                if resolved is not None and (resolved_type or media_type) == media_type:
                    keys.add((media_type, "tmdb", int(resolved)))
        fldb_id = ids_block.get("fldb")
        if fldb_id is not None:
            keys.add((media_type, "fldb", fldb_id))
        return keys

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

        Matching is by candidate-key-set intersection, not a single best key per item (see
        _candidate_keys). A current item is only ever removed when NONE of its candidate keys
        appear anywhere in the desired universe; the moment it shares even one id with some
        desired item, it's treated as still wanted, even if that wasn't the id either side would
        have picked as "primary" under the old single-key design. This keeps the conservative-on-
        delete guarantee (a stale entry is cheap, a wrongly deleted one is not) while
        actually covering the cases that fell through it: an unresolved tvdb->tmdb conversion on
        the desired side, and a current item keyed on fldb+imdb with no tmdb/tvdb at all.
        """
        list_id, created = self._resolve_list(list_id_or_name)
        if created and logger:
            logger.info(f"FlickList List '{list_id_or_name}' not found; created a new list (id {list_id})")
        current_items = self._request_paginated(f"/sync/lists/{list_id}/items") or []

        desired = []
        desired_keys = set()
        for ids_block, media_type in ids:
            keys = self._candidate_keys(ids_block, media_type, convert)
            if not keys:
                continue
            desired.append((keys, ids_block, media_type))
            desired_keys |= keys
        current = []
        current_keys = set()
        unmatched = 0
        for item in current_items:
            item_ids = item.get("ids") or {}
            media_type = self._media_type_of(item)
            keys = self._candidate_keys(item_ids, media_type, convert)
            if not keys:
                unmatched += 1
                continue
            current.append((keys, item_ids, media_type))
            current_keys |= keys
        if unmatched and logger:
            logger.warning(f"FlickList Warning: {unmatched} existing list item(s) had no usable id at all; leaving them in place")

        add_payloads = [{"ids": ids_block, "media_type": media_type} for keys, ids_block, media_type in desired if keys.isdisjoint(current_keys)]
        # Never remove an item this run couldn't positively rule out (no shared id with the desired universe at all) - a stale entry is cheap, a wrongly deleted one is not.
        remove_payloads = [{"ids": item_ids, "media_type": media_type} for keys, item_ids, media_type in current if keys.isdisjoint(desired_keys)]
        self._sync_batch(list_id, "add", add_payloads)
        self._sync_batch(list_id, "remove", remove_payloads)
