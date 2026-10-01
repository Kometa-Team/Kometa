import time

from modules import util
from modules.request import DEFAULT_TIMEOUT
from modules.util import Failed

logger = util.logger


class TrackerAPI:
    """Shared HTTP transport, pagination and error handling for tracker connectors (FlickList,
    WeTrakr, ...). Holds no config, no connection and no state of its own - each connector still
    owns its own auth, config wiring and business logic. See TRACKER-SHARED-LAYER-PLAN.md."""

    service = "Tracker"
    base_url = ""
    max_retry_after_seconds = 120.0
    max_429_attempts = 3
    default_retry_wait = 60.0
    page_count_header = ""
    page_params = None

    def __init__(self, requests, read_only):
        self.requests = requests
        self.read_only = read_only

    def _headers(self, anonymous=False):
        # Override per provider - the auth scheme and required headers differ.
        raise NotImplementedError

    def _base_params(self):
        # Merged into every request's params when it returns a dict; None is a no-op. Simkl needs client_id/app-name/app-version on every call.
        return None

    def _retry_wait(self, response):
        retry_after = response.headers.get("Retry-After")
        try:
            return float(retry_after)
        except (TypeError, ValueError):
            return self.default_retry_wait

    @staticmethod
    def _parse_error_body(response):
        try:
            payload = response.json()
        except ValueError:
            return response.text[:200] if response.text else response.reason
        if not isinstance(payload, dict):
            return response.reason
        if payload.get("detail"):
            return payload["detail"]
        if payload.get("message"):
            return payload["message"]
        error = payload.get("error")
        if isinstance(error, str) and error:
            return error
        if isinstance(error, dict):
            return error.get("message") or error.get("code") or response.reason
        if payload.get("reason"):
            return payload["reason"]
        return response.reason

    def _raise_for_status(self, path, response, ignore_404):
        """Generic >=400 handling. Subclasses handle their own status codes first, then call super() for this."""
        if response.status_code == 404 and ignore_404:
            return True
        if response.status_code >= 400:
            raise Failed(f"{self.service} Error: ({response.status_code}) {self._parse_error_body(response)}")
        return False

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
            if attempts >= self.max_429_attempts:
                raise Failed(f"{self.service} Error: Rate limited on {path} after {self.max_429_attempts} attempts this run; giving up for now")
            wait_seconds = self._retry_wait(response)
            if wait_seconds > self.max_retry_after_seconds:
                raise Failed(f"{self.service} Error: Rate limited on {path}; server asked us to wait {wait_seconds:.0f} seconds (over the {self.max_retry_after_seconds:.0f}s cap) - giving up for now rather than blocking the run")
            if logger:
                logger.warning(f"{self.service} Warning: Rate limited on {path}; waiting {wait_seconds} seconds")
            time.sleep(wait_seconds)

    def _merge_base_params(self, params):
        base = self._base_params()
        if not base:
            return dict(params) if params else params
        merged = dict(base)
        if params:
            merged.update(params)
        return merged

    def _request_raw(self, path, params=None, json_data=None, method="GET", anonymous=False, ignore_404=False):
        """Single call, no pagination. Returns whatever the endpoint sends back (dict, list, or None on a swallowed 404)."""
        url = f"{self.base_url}{path}"
        if logger:
            logger.trace(f"URL: {url}")
            if params:
                logger.trace(f"Params: {params}")
            if json_data is not None:
                logger.trace(f"JSON: {json_data}")
        headers = self._headers(anonymous=anonymous)
        call_params = self._merge_base_params(params)
        response = self._send(path, url, headers, call_params, json_data, method)
        if self._raise_for_status(path, response, ignore_404):
            return None
        if response.status_code == 204 or not response.content:
            return None
        try:
            return response.json()
        except ValueError:
            raise Failed(f"{self.service} Error: {path} returned a non-JSON response body")

    def _request(self, path, params=None, json_data=None, method="GET", anonymous=False, ignore_404=False):
        """Single-call request against an object-returning endpoint. Always returns a dict, or None when ignore_404 swallowed a 404."""
        data = self._request_raw(path, params=params, json_data=json_data, method=method, anonymous=anonymous, ignore_404=ignore_404)
        if data is None:
            return None
        return data if isinstance(data, dict) else {}

    def _request_list(self, path, params=None, anonymous=False):
        """Single-call request against an array-returning endpoint. Always returns a list; a 404/204/empty body is treated as an empty list."""
        data = self._request_raw(path, params=params, anonymous=anonymous)
        return data if isinstance(data, list) else []

    def _request_paginated(self, path, params=None, anonymous=False, ignore_404=False):
        """Multi-page request against the header-paginated family. Always returns a list, or None when ignore_404 swallowed a 404."""
        url = f"{self.base_url}{path}"
        if logger:
            logger.trace(f"URL: {url}")
            if params:
                logger.trace(f"Params: {params}")
        headers = self._headers(anonymous=anonymous)
        results = []
        page = 1
        page_count = 1
        while page <= page_count:
            call_params = self._merge_base_params(params)
            if page == 1 and self.page_params:
                call_params = call_params or {}
                call_params.update(self.page_params)
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
                raise Failed(f"{self.service} Error: {path} returned a non-JSON response body")
            if isinstance(data, list):
                results.extend(data)
            elif isinstance(data, dict):
                results.append(data)
            if page == 1:
                try:
                    page_count = int(response.headers.get(self.page_count_header, 1)) if self.page_count_header else 1
                except (TypeError, ValueError):
                    page_count = 1
            page += 1
        return results


def parse_ids(items, is_movie, *, service, type_of, native_id_of):
    """FlickList._parse_ids, generalised. type_of(item) -> "movie"/"show"/None classifies the item;
    native_id_of(item) -> a hashable provider-native id (FlickList: ids.fldb) or None, used only to
    dedupe repeats of the same title - falls back to the computed key when there isn't one."""
    ids = []
    seen = set()
    for item in items or []:
        ids_block = item.get("ids") or {}
        media_type = type_of(item)
        is_show = media_type == "show"
        is_item_movie = media_type == "movie"
        if is_movie is True and not is_item_movie:
            continue
        if is_movie is False and not is_show:
            continue
        tmdb_id = ids_block.get("tmdb")
        tvdb_id = ids_block.get("tvdb")
        imdb_id = ids_block.get("imdb")
        native_id = native_id_of(item)
        if is_item_movie and tmdb_id:
            key = (int(tmdb_id), "tmdb")
        elif is_show and tmdb_id:
            key = (int(tmdb_id), "tmdb_show")
        elif is_show and tvdb_id:
            key = (int(tvdb_id), "tvdb")
        elif imdb_id:
            key = (str(imdb_id), "imdb")
        else:
            title = item.get("title") or item.get("name") or native_id or "Unknown"
            if logger:
                logger.warning(f"{service} Warning: No usable ID found for {title}; skipping")
            continue
        dedupe_key = native_id if native_id is not None else key
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        ids.append(key)
    return ids


def candidate_keys(ids_block, media_type, convert, native=None):
    """Every identifier this item could plausibly be matched on, not just one 'best' key.
    The old design picked a single best key per side (tmdb first, then a native id, then imdb, then
    tvdb) and compared those. That breaks whenever the two sides expose different id types for
    the same title - e.g. a desired show whose tvdb->tmdb Convert lookup misses this run (rate
    limited or not yet cached) falls back to a bare tvdb key, while the matching current item
    already carries a native tmdb id and never even looks at its own tvdb value under the old
    priority order. Two keys for the same title that never intersect reads as "not present",
    so the real item gets deleted and a duplicate gets added in its place. Returning the full
    set of candidates and matching on intersection means any single shared id is enough to
    recognize the same item on both sides, regardless of which id each side happened to key on.
    Returns an empty set only when the ids block carries nothing usable at all.
    native: optional (label, value) pair for the provider's own id that doesn't fit tmdb/tvdb/imdb
    (FlickList: ("fldb", ids_block.get("fldb"))); skipped when value is None."""
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
    if native is not None:
        native_label, native_value = native
        if native_value is not None:
            keys.add((media_type, native_label, native_value))
    return keys


def plan_list_sync(desired, current_items, convert, *, ids_of, type_of, native_id_of):
    """The list-sync diff, lifted out of FlickList.sync_list verbatim.

    desired: iterable of (ids_block, media_type) pairs already known to the caller (what the
    collection wants on the list). current_items: raw items from the provider's own list-items
    read; ids_of(item)/type_of(item) extract the ids block and media type from each. native_id_of
    is called with an ids_block (either a desired one directly, or one extracted via ids_of) and
    must return a (label, value) pair for candidate_keys' native id, or a pair with a None value
    when there isn't one (FlickList: lambda ids_block: ("fldb", ids_block.get("fldb"))).

    Matching is by candidate-key-set intersection, not a single best key per item (see
    candidate_keys). A current item is only ever removed when NONE of its candidate keys appear
    anywhere in the desired universe; the moment it shares even one id with some desired item, it's
    treated as still wanted, even if that wasn't the id either side would have picked as "primary"
    under the old single-key design. This keeps the conservative-on-delete guarantee (a stale entry
    is cheap, a wrongly deleted one is not) while covering the cases that fell through it: an
    unresolved tvdb->tmdb conversion on the desired side, and a current item keyed on a native id
    plus imdb with no tmdb/tvdb at all.

    Returns (add_payloads, remove_payloads, unmatched_count) where add/remove are lists of
    (ids_block, media_type) pairs and unmatched_count is how many current items had no usable id
    at all (left in place either way)."""
    desired_entries = []
    desired_keys = set()
    for ids_block, media_type in desired:
        keys = candidate_keys(ids_block, media_type, convert, native=native_id_of(ids_block))
        if not keys:
            continue
        desired_entries.append((keys, ids_block, media_type))
        desired_keys |= keys

    current_entries = []
    current_keys = set()
    unmatched = 0
    for item in current_items:
        item_ids = ids_of(item)
        media_type = type_of(item)
        keys = candidate_keys(item_ids, media_type, convert, native=native_id_of(item_ids))
        if not keys:
            unmatched += 1
            continue
        current_entries.append((keys, item_ids, media_type))
        current_keys |= keys

    add_payloads = [(ids_block, media_type) for keys, ids_block, media_type in desired_entries if keys.isdisjoint(current_keys)]
    # Never remove an item this run couldn't positively rule out (no shared id with the desired universe at all) - a stale entry is cheap, a wrongly deleted one is not.
    remove_payloads = [(item_ids, media_type) for keys, item_ids, media_type in current_entries if keys.isdisjoint(desired_keys)]
    return add_payloads, remove_payloads, unmatched


def validate_flag(err_type, method_name, method_data):
    """True/blank enables the builder; explicit false just leaves it out, same as omitting the
    attribute - erroring on `method_name: false` punished a value config.yml owners can reach
    for naturally (e.g. templating a shared block where one library sets a flag off)."""
    if method_data is None:
        return True
    return util.parse(err_type, method_name, method_data, datatype="bool", default=True)


def validate_rating_range(err_type, method_name, method_data):
    """Blank -> no filter; a bare number -> minimum only; a dict -> explicit minimum/maximum."""

    def to_float(value, label):
        try:
            return float(value)
        except (TypeError, ValueError):
            raise Failed(f"{err_type} Error: {method_name} {label} must be a number")

    if method_data is None or isinstance(method_data, bool):
        return {"minimum": None, "maximum": None}
    if isinstance(method_data, dict):
        dict_methods = {dm.lower(): dm for dm in method_data}
        minimum = to_float(method_data[dict_methods["minimum"]], "minimum") if "minimum" in dict_methods else None
        maximum = to_float(method_data[dict_methods["maximum"]], "maximum") if "maximum" in dict_methods else None
        return {"minimum": minimum, "maximum": maximum}
    return {"minimum": to_float(method_data, "minimum"), "maximum": None}


def validate_positive_int(err_type, method_name, method_data):
    """Blank/true -> None (no limit); an integer -> that many, must be positive. Not yet wired up
    to any connector in Layer 0 (FlickList's own flicklist_up_next stays local per the plan's
    "Keeps" list) - added now for the next tracker that needs this exact shape."""
    if method_data is None or isinstance(method_data, bool):
        return None
    try:
        limit = int(method_data)
    except (TypeError, ValueError):
        raise Failed(f"{err_type} Error: {method_name} must be blank, true, or an integer limit")
    if limit < 1:
        raise Failed(f"{err_type} Error: {method_name} limit must be a positive integer")
    return limit
