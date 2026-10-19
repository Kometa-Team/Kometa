import re
import time
from urllib.parse import urlparse

import requests
from tenacity import RetryError

from modules import util
from modules.util import Failed

base_url = "https://listrr.pro"
api_url = "https://listrr.pro/api"
builders = ["listrr_list", "listrr_list_details"]

# Live challenge names this scheme. The published description says X-API-KEY.
authorization_scheme = "APIKEY"
max_retry_after_seconds = 120.0
max_429_attempts = 3
default_retry_wait = 60.0

sort_by_options = {
    "name.asc": ("Name", "Ascending"),
    "name.desc": ("Name", "Descending"),
    "release.asc": ("ReleaseDate", "Ascending"),
    "release.desc": ("ReleaseDate", "Descending"),
}
_list_attributes = {"url", "list_id", "sort_by", "limit"}
_hex_id = re.compile(r"^[0-9a-fA-F]{24}$")
_list_path = re.compile(r"^/Lists/Show(?:Movie|Show)List/([0-9a-fA-F]{24})/?$")
_imdb_id = re.compile(r"^tt\d+$")
_imdb_digits = re.compile(r"^\d+$")


class Listrr:
    def __init__(self, requests, apikey):
        self.requests = requests
        self.apikey = apikey
        util.logger.secret(self.apikey)

    def test_connection(self):
        self._request(f"{api_url}/List/My/1")

    def validate_lists(self, err_type, method_data):
        valid_lists = []
        for value in util.get_list(method_data, split=False, return_none=False):
            if isinstance(value, dict):
                unknown = set(value) - _list_attributes
                if unknown:
                    attributes = ", ".join(sorted(unknown))
                    raise Failed(f"{err_type} Error: listrr_list has invalid attribute(s): {attributes}")
                list_id = self._id_from_entry(err_type, value)
                sort_by = value["sort_by"] if "sort_by" in value else "name.asc"
                if sort_by not in sort_by_options:
                    options = ", ".join(sort_by_options)
                    raise Failed(f"{err_type} Error: sort_by must be one of {options}")
                limit = self._limit(err_type, value["limit"]) if "limit" in value else 0
            else:
                list_id = self._parse_list_id(value)
                sort_by = "name.asc"
                limit = 0
            valid_lists.append({"list_id": list_id, "sort_by": sort_by, "limit": limit})
        if not valid_lists:
            raise Failed(f"{err_type} Error: No valid Listrr lists")
        return valid_lists

    def list_description(self, list_id):
        data = self._request(f"{api_url}/List/{list_id}")
        return data.get("description") or ""

    def get_listrr_ids(self, method, data, is_movie):
        entries = data if isinstance(data, list) else [data]
        results = []
        emitted = set()
        for entry in entries:
            entry_results = [item for item in self._ids_for_entry(method, entry, is_movie) if item not in emitted]
            results.extend(entry_results)
            emitted.update(entry_results)
        return results

    def _ids_for_entry(self, method, data, is_movie):
        list_id = data["list_id"]
        sort_name, direction = sort_by_options[data.get("sort_by", "name.asc")]
        limit = data.get("limit", 0)
        util.logger.info(f"Processing {method}: {list_id}")
        meta = self._request(f"{api_url}/List/{list_id}")
        list_is_movie = self._list_is_movie(meta.get("type"))
        if is_movie is True and list_is_movie is False:
            raise Failed(f"Listrr Error: List {list_id} is a Show list and cannot be used on a movie library")
        if is_movie is False and list_is_movie is True:
            raise Failed(f"Listrr Error: List {list_id} is a Movie list and cannot be used on a show library")
        if list_is_movie is None:
            if is_movie is None:
                raise Failed(f"Listrr Error: List {list_id} did not report a media type")
            list_is_movie = is_movie
        self._log_state(list_id, meta)
        segment = "Movies" if list_is_movie else "Shows"
        results = []
        seen = set()
        page = 1
        while True:
            body = self._request(f"{api_url}/List/{segment}/{list_id}/{sort_name}/{direction}/{page}")
            items = body.get("items") or []
            if not isinstance(items, list):
                raise Failed("Listrr Error: items response was not a list")
            pages = body.get("pages") if "pages" in body else None
            if pages is not None:
                pages = util.check_num(pages)
            if not items:
                break
            for item in items:
                if not isinstance(item, dict):
                    continue
                emitted = self._emit(item, list_is_movie, seen)
                if emitted is None:
                    continue
                results.append(emitted)
                if limit and len(results) >= limit:
                    self._log_progress(len(results), body.get("count"))
                    return results
            self._log_progress(len(results), body.get("count"))
            if pages is None or page >= pages:
                break
            page += 1
        return results

    def _headers(self):
        return {"Authorization": f"{authorization_scheme} {self.apikey}"}

    def _send(self, url):
        getter = getattr(self.requests, "get_once", None)
        if getter is None:
            getter = self.requests.get
        try:
            return getter(url, headers=self._headers())
        except RetryError as exc:
            raise Failed(f"Listrr Error: Request failed for {url}: {exc}") from exc
        except requests.exceptions.RequestException as exc:
            raise Failed(f"Listrr Error: Request failed for {url}: {exc}") from exc

    def _request(self, url):
        attempts = 0
        while True:
            response = self._send(url)
            if response.status_code != 429:
                break
            attempts += 1
            if attempts >= max_429_attempts:
                raise Failed(f"Listrr Error: Rate limited on {url} after {max_429_attempts} attempts this run; giving up for now")
            wait_seconds = self._retry_wait(response)
            if wait_seconds > max_retry_after_seconds:
                raise Failed(f"Listrr Error: Rate limited on {url}; server asked us to wait {wait_seconds:.0f} seconds " f"(over the {max_retry_after_seconds:.0f}s cap) - giving up for now rather than blocking the run")
            util.logger.warning(f"Listrr Warning: Rate limited on {url}; waiting {wait_seconds} seconds")
            time.sleep(wait_seconds)
        self._raise_for_status(response)
        try:
            data = response.json()
        except ValueError:
            raise Failed(f"Listrr Error: ({response.status_code}) non-JSON response: {self._short_body(response)}")
        if not isinstance(data, dict):
            raise Failed(f"Listrr Error: ({response.status_code}) expected a JSON object")
        return data

    @staticmethod
    def _retry_wait(response):
        headers = response.headers or {}
        retry_after = headers.get("Retry-After", headers.get("retry-after"))
        if retry_after is None:
            return default_retry_wait
        try:
            return float(retry_after)
        except (TypeError, ValueError):
            return default_retry_wait

    def _raise_for_status(self, response):
        status = response.status_code
        headers = response.headers or {}
        location = headers.get("Location", headers.get("location", "")) or ""
        if status == 401 or (status == 302 and "Identity/Account/Login" in location):
            raise Failed("Listrr Error: API key was rejected")
        if status == 302:
            raise Failed(f"Listrr Error: (302) unexpected redirect to {location}")
        if status == 404:
            raise Failed("Listrr Error: List could not be found, or is not visible to this key")
        if status == 400:
            raise Failed("Listrr Error: List type does not match this route")
        if status >= 400:
            raise Failed(f"Listrr Error: ({status}) {self._short_body(response)}")

    @staticmethod
    def _short_body(response):
        text = getattr(response, "text", None)
        if text is None:
            content = getattr(response, "content", b"") or b""
            text = content.decode("utf-8", errors="ignore") if isinstance(content, (bytes, bytearray)) else str(content)
        collapsed = " ".join(str(text).split())
        if collapsed:
            return collapsed[:200]
        return getattr(response, "reason", "") or ""

    def _id_from_entry(self, err_type, entry):
        url = entry.get("url")
        list_id = entry.get("list_id")
        parsed_url = self._parse_list_id(url) if url not in (None, "") else None
        parsed_id = self._parse_list_id(list_id) if list_id not in (None, "") else None
        if parsed_url and parsed_id and parsed_url != parsed_id:
            raise Failed(f"{err_type} Error: url and list_id point at different Listrr lists")
        if parsed_url:
            return parsed_url
        if parsed_id:
            return parsed_id
        raise Failed(f"{err_type} Error: listrr_list requires a url or list_id")

    @staticmethod
    def _limit(err_type, value):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise Failed(f"{err_type} Error: limit must be an integer 0 or greater")
        return value

    @staticmethod
    def _parse_list_id(value):
        if isinstance(value, bool) or value is None:
            raise Failed(f"Listrr Error: {value} is not a Listrr list id or URL")
        text = str(value).strip()
        if "://" in text:
            parsed = urlparse(text)
            host = (parsed.hostname or "").lower()
            if parsed.scheme not in ("http", "https") or host != "listrr.pro":
                raise Failed(f"Listrr Error: {value} is not a listrr.pro list URL")
            match = _list_path.match(parsed.path)
            if not match:
                raise Failed(f"Listrr Error: {value} is not a Listrr list id or URL")
            return match.group(1).lower()
        if _hex_id.fullmatch(text):
            return text.lower()
        raise Failed(f"Listrr Error: {text} is not a Listrr list id or URL")

    @staticmethod
    def _list_is_movie(list_type):
        if list_type == "Movie":
            return True
        if list_type == "Show":
            return False
        return None

    @staticmethod
    def _log_state(list_id, meta):
        state = meta.get("state")
        if state in ("Error", "SchduledForDeletion"):
            util.logger.warning(f"Listrr Warning: List {list_id} state is {state} (lastProcessed {meta.get('lastProcessed')}); using the current items")
        elif state in ("Updating", "Scheduled"):
            util.logger.info(f"Listrr Info: List {list_id} is {state}; items are the last processed snapshot")

    @staticmethod
    def _log_progress(found, count):
        if isinstance(count, int) and not isinstance(count, bool):
            util.logger.info(f"Reading current Listrr items: {found}/{count}")
        else:
            util.logger.info(f"Reading current Listrr items: {found}")

    def _emit(self, item, list_is_movie, seen):
        native = item.get("id")
        key = self._movie_id(item) if list_is_movie else self._show_id(item)
        if key is None:
            name = item.get("name") or native or "Unknown"
            util.logger.warning(f"Listrr Warning: No usable ID found for {name}; skipping")
            return None
        dedupe = str(native).strip() if native is not None and str(native).strip() else key
        if dedupe in seen:
            return None
        seen.add(dedupe)
        return key

    def _movie_id(self, item):
        tmdb_id = util.check_num(item.get("tmDbId"))
        if tmdb_id:
            return (tmdb_id, "tmdb")
        imdb_id = self._imdb_id(item)
        if imdb_id:
            return (imdb_id, "imdb")
        return None

    def _show_id(self, item):
        tvdb_id = util.check_num(item.get("tvDbId"))
        if tvdb_id:
            return (tvdb_id, "tvdb")
        tmdb_id = util.check_num(item.get("tmDbId"))
        if tmdb_id:
            return (tmdb_id, "tmdb_show")
        imdb_id = self._imdb_id(item)
        if imdb_id:
            return (imdb_id, "imdb")
        return None

    @staticmethod
    def _imdb_id(item):
        raw = item.get("imDbId")
        if raw is None:
            return None
        text = str(raw).strip()
        if not text:
            return None
        if _imdb_id.fullmatch(text):
            return text
        if _imdb_digits.fullmatch(text):
            return f"tt{text}"
        name = item.get("name") or item.get("id") or "Unknown"
        util.logger.warning(f"Listrr Warning: Invalid IMDb ID '{text}' for {name}; skipping")
        return None
