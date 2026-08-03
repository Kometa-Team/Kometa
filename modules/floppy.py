import csv
import json
import re
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from io import StringIO
from urllib.parse import urlparse

from modules import util
from modules.util import Failed

logger = util.logger

builders = ["floppy_list", "floppy_list_details", "floppy_tracked"]
list_pattern = re.compile(r"^/list/(?P<list_id>\d+)(?:/|$)")
tracked_statuses = {"no_status": None, "planning": 0, "in_progress": 1, "paused": 2, "completed": 3, "dropped": 4}
tracked_types = ["movie", "show", "season", "anime"]
tracked_media_types = {"movie": "movie", "show": "tv", "season": "season", "anime": "anime"}


class FloppyApiUnavailable(Failed):
    """Raised when an optional Floppy API route is unavailable."""


class Floppy:
    def __init__(self, requests, params):
        self.requests = requests
        self.url = params["url"].rstrip("/")
        self.token = params.get("token")
        if logger and self.token:
            logger.secret(self.token)
        self._ratings = None

    def _list_id(self, list_url):
        parsed = urlparse(str(list_url).strip())
        expected = urlparse(self.url)
        if parsed.scheme not in ("http", "https") or parsed.netloc != expected.netloc:
            raise Failed(f"Floppy Error: {list_url} must be a list URL on {self.url}")
        match = list_pattern.match(parsed.path)
        if not match:
            raise Failed(f"Floppy Error: {list_url} must use the format {self.url}/list/ID")
        return int(match.group("list_id"))

    def _response(self, url, params=None):
        headers = {"X-API-Key": self.token} if self.token else None
        try:
            response = self.requests.get(url, headers=headers, params=params)
        except Exception as e:
            raise Failed(f"Floppy Error: Failed to load {url}: {e}") from e
        if response.status_code == 401:
            raise Failed("Floppy Error: Invalid or missing API token")
        if response.status_code == 403:
            raise Failed(f"Floppy Error: Access denied for {url}")
        if response.status_code == 404:
            if "/api/" in url:
                raise FloppyApiUnavailable(f"Floppy Error: API endpoint not found at {url}")
            raise Failed(f"Floppy Error: List not found at {url}")
        if response.status_code >= 400:
            raise Failed(f"Floppy Error: {response.status_code} on {url}")
        return response

    def _request(self, url, params=None):
        response = self._response(url, params=params)
        try:
            return response.json()
        except ValueError as e:
            raise Failed(f"Floppy Error: Invalid JSON returned by {url}") from e

    def test_connection(self):
        if self.token:
            self._request(f"{self.url}/api/v1/lists?limit=1")

    def validate_lists(self, err_type, floppy_lists):
        valid_lists = []
        for value in util.get_list(floppy_lists, split=False, return_none=False):
            if isinstance(value, dict):
                methods = {str(k).lower(): k for k in value}
                if "url" not in methods or value[methods["url"]] is None:
                    raise Failed(f"{err_type} Error: Floppy List url is required")
                list_url = str(value[methods["url"]]).strip()
                sync_tags = util.parse(err_type, "sync_tags", value, methods=methods, datatype="bool", default=False)
            else:
                list_url = str(value).strip()
                sync_tags = False
            self._list_id(list_url)
            valid_lists.append({"url": list_url, "sync_tags": sync_tags})
        if not valid_lists:
            raise Failed(f"{err_type} Error: No valid Floppy Lists")
        return valid_lists

    def validate_tracked(self, err_type, floppy_tracked, is_movie=None):
        if isinstance(floppy_tracked, dict):
            methods = {str(k).lower(): k for k in floppy_tracked}
            unknown = [str(k) for k in floppy_tracked if str(k).lower() not in ("status", "type")]
            if unknown:
                raise Failed(f"{err_type} Error: floppy_tracked attribute {unknown[0]} is invalid")
            if "status" not in methods:
                raise Failed(f"{err_type} Error: floppy_tracked status is required")
            status_data = floppy_tracked[methods["status"]]
            type_data = floppy_tracked[methods["type"]] if "type" in methods else None
        else:
            status_data = floppy_tracked
            type_data = None

        statuses = self._validate_tracked_values(err_type, "status", status_data, list(tracked_statuses) + ["all"])
        if "all" in statuses:
            statuses = ["all"]

        default_types = ["movie"] if is_movie is True else ["show", "season"] if is_movie is False else ["movie", "show", "season"]
        media_types = default_types if type_data is None else self._validate_tracked_values(err_type, "type", type_data, tracked_types)
        applicable_types = [media_type for media_type in media_types if media_type == "anime" or is_movie is None or (is_movie and media_type == "movie") or (not is_movie and media_type in ("show", "season"))]
        if not applicable_types:
            library_name = "movie" if is_movie else "show"
            raise Failed(f"{err_type} Error: floppy_tracked type does not apply to a {library_name} library")
        return {"status": statuses, "type": applicable_types}

    @staticmethod
    def _validate_tracked_values(err_type, attribute, data, valid_values):
        values = [str(value).strip().lower().replace(" ", "_") for value in util.get_list(data, return_none=False)]
        if not values:
            raise Failed(f"{err_type} Error: floppy_tracked {attribute} is required")
        for value in values:
            if value not in valid_values:
                raise Failed(f"{err_type} Error: floppy_tracked {attribute} {value} is invalid; options: {', '.join(valid_values)}")
        return list(dict.fromkeys(values))

    @staticmethod
    def _api_id(item, is_movie):
        data = item.get("item") or item
        media_type = data.get("media_type")
        source = data.get("source")
        media_id = data.get("media_id")
        if media_id is None or media_type not in ("movie", "tv"):
            return None
        if is_movie is True and media_type != "movie":
            return None
        if is_movie is False and media_type != "tv":
            return None
        if source == "imdb":
            return str(media_id), "imdb"
        try:
            media_id = int(media_id)
        except (TypeError, ValueError):
            return None
        if source == "tmdb":
            return media_id, "tmdb" if media_type == "movie" else "tmdb_show"
        if source == "tvdb" and media_type == "tv":
            return media_id, "tvdb"
        return None

    def _api_ids(self, list_id, is_movie):
        ids = []
        seen = set()
        next_url = f"{self.url}/api/v1/lists/{list_id}/items?limit=1000"
        while next_url:
            payload = self._request(next_url)
            for item in payload.get("results", []):
                item_id = self._api_id(item, is_movie)
                if item_id and item_id not in seen:
                    ids.append(item_id)
                    seen.add(item_id)
            next_url = payload.get("pagination", {}).get("next")
        return ids

    def _public_ids(self, list_id, is_movie):
        ids = []
        arr_types = ["radarr", "sonarr"] if is_movie is None else ["radarr" if is_movie else "sonarr"]
        for arr_type in arr_types:
            payload = self._request(f"{self.url}/list/{list_id}/json?arr={arr_type}")
            id_type = "tmdb" if arr_type == "radarr" else "tmdb_show"
            for item in payload:
                try:
                    ids.append((int(item["id"]), id_type))
                except (KeyError, TypeError, ValueError):
                    continue
        return ids

    def get_list_details(self, list_data):
        list_url = list_data["url"]
        list_id = self._list_id(list_url)
        if self.token:
            url = f"{self.url}/api/v1/export/csv?include_collection=0"
        else:
            url = f"{self.url}/list/{list_id}/export"
        response = self._response(url)
        content = response.content.decode("utf-8-sig") if isinstance(response.content, bytes) else str(response.content)
        for row in csv.DictReader(StringIO(content)):
            if row.get("row_type") != "list" or str(row.get("list_uid")) != str(list_id):
                continue
            try:
                tags = json.loads(row.get("list_tags") or "[]")
            except (TypeError, ValueError):
                tags = []
            tags = [str(tag).strip() for tag in tags if str(tag).strip()]
            return row.get("list_description", "").strip(), tags
        raise Failed(f"Floppy Error: List {list_id} was not found in the CSV export")

    def _load_ratings(self):
        if not self.token:
            raise Failed("Floppy Error: An API token is required for rating updates")
        if self._ratings is not None:
            return
        url = f"{self.url}/api/v1/export/csv?include_lists=0&include_collection=0"
        response = self._response(url)
        content = response.content.decode("utf-8-sig") if isinstance(response.content, bytes) else str(response.content)
        self._ratings = {}
        for row in csv.DictReader(StringIO(content)):
            score = row.get("score")
            if row.get("row_type") != "media" or row.get("media_type") not in ("movie", "tv", "episode") or score in (None, ""):
                continue
            try:
                rating = float(Decimal(str(score)))
            except (InvalidOperation, TypeError, ValueError):
                continue
            key = (
                row.get("media_type"),
                row.get("source"),
                str(row.get("media_id")),
                int(row["season_number"]) if row.get("season_number") else None,
                int(row["episode_number"]) if row.get("episode_number") else None,
            )
            self._ratings[key] = rating

    def get_tracked_ids(self, tracked, is_movie=None):
        if not self.token:
            raise Failed("Floppy Error: An API token is required for floppy_tracked")
        selected_types = {tracked_media_types[media_type] for media_type in tracked["type"]}
        selected_statuses = set(tracked["status"])
        include_all = "all" in selected_statuses
        include_no_status = "no_status" in selected_statuses

        candidates = []
        try:
            for media_type in selected_types:
                statuses = (None,) if include_all or include_no_status else (tracked_statuses[status] for status in selected_statuses)
                for status in statuses:
                    candidates.extend(self._media_items(media_type, status))
        except FloppyApiUnavailable:
            candidates = self._legacy_tracked_items(selected_types, selected_statuses, include_all)

        if not include_all:
            candidates = [row for row in candidates if self._tracked_status(row) in {tracked_statuses[status] for status in selected_statuses}]

        ids = []
        mal_ids = []
        seen = set()
        seen_mal = set()
        for row in candidates:
            data = row.get("item") or row
            if row.get("tracked") is False:
                continue
            media_type = data.get("media_type")
            if media_type == "anime":
                if data.get("source") == "mal":
                    try:
                        mal_id = int(data["media_id"])
                    except (KeyError, TypeError, ValueError):
                        continue
                    if mal_id not in seen_mal:
                        mal_ids.append(mal_id)
                        seen_mal.add(mal_id)
                continue
            item_id = self._tracked_api_id(row, is_movie)
            if item_id and item_id not in seen:
                ids.append(item_id)
                seen.add(item_id)
        if not ids and not mal_ids:
            raise Failed("Floppy Error: No IDs found in tracked items")
        return ids, mal_ids

    def _legacy_tracked_items(self, selected_types, selected_statuses, include_all):
        response = self._response(f"{self.url}/api/v1/export/csv?include_lists=0")
        content = response.content.decode("utf-8-sig") if isinstance(response.content, bytes) else str(response.content)
        rows = list(csv.DictReader(StringIO(content)))
        candidates, tracked_keys = [], set()
        for row in rows:
            if row.get("row_type") != "media" or row.get("media_type") not in selected_types:
                continue
            key = self._tracked_key(row)
            if key:
                tracked_keys.add(key)
                status = str(row.get("status") or "").strip().lower().replace(" ", "_") or "no_status"
                if include_all or status in selected_statuses:
                    candidates.append(row)
        if include_all or "no_status" in selected_statuses:
            candidates.extend(row for row in rows if row.get("row_type") == "collection" and row.get("media_type") in selected_types and self._tracked_key(row) not in tracked_keys)
        return candidates

    def _media_items(self, media_type, status=None):
        items, limit, offset = [], 100, 0
        while True:
            params = {"media_type": media_type, "limit": limit, "offset": offset}
            if status is not None:
                params["status"] = status
            payload = self._request(f"{self.url}/api/v1/media/", params=params)
            batch = payload if isinstance(payload, list) else payload.get("results", payload.get("items", payload.get("data", [])))
            if not isinstance(batch, list):
                raise Failed("Floppy Error: Invalid media response from /api/v1/media")
            items.extend(item for item in batch if isinstance(item, dict))
            if len(batch) < limit:
                return items
            offset += limit

    @staticmethod
    def _tracked_key(row):
        media_type = row.get("media_type")
        source = row.get("source")
        media_id = row.get("media_id")
        if not media_type or not source or media_id in (None, ""):
            return None
        season = row.get("season_number") if media_type == "season" else None
        return media_type, source, str(media_id), str(season or "")

    @staticmethod
    def _tracked_status(row):
        status = row.get("status")
        if status is None:
            return None
        if isinstance(status, int):
            return status
        return tracked_statuses.get(str(status).strip().lower().replace(" ", "_"))

    @classmethod
    def _tracked_api_id(cls, row, is_movie):
        data = row.get("item") or row
        media_type = data.get("media_type")
        api_type = "movie" if media_type == "movie" else "tv" if media_type in ("tv", "season") else None
        if api_type is None:
            return None
        return cls._api_id({"media_type": api_type, "source": data.get("source"), "media_id": data.get("media_id")}, is_movie)

    def get_rating(self, media_type, tmdb_id=None, tvdb_id=None, imdb_id=None, season=None, episode=None):
        self._load_ratings()
        ratings = self._ratings
        if ratings is None:
            raise Failed("Floppy Error: Ratings could not be loaded")
        candidates = [("tmdb", tmdb_id), ("tvdb", tvdb_id), ("imdb", imdb_id)]
        for source, media_id in candidates:
            if media_id is None:
                continue
            key = (media_type, source, str(media_id), season, episode)
            if key in ratings:
                # Plex's API is 0-10, but its UI renders each whole API point as
                # half a star. Round metadata writes to 0.5-star UI steps.
                return float(Decimal(str(ratings[key])).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        raise Failed

    def get_tags(self, media_type, tmdb_id=None, tvdb_id=None, imdb_id=None):
        """Return the user's Floppy tags for a movie or TV item."""
        if not self.token:
            raise Failed("Floppy Error: An API token is required for floppy_tag")
        for source, media_id in (("tmdb", tmdb_id), ("tvdb", tvdb_id), ("imdb", imdb_id)):
            if media_id is None:
                continue
            try:
                payload = self._request(f"{self.url}/api/v1/media/{media_type}/{source}/{media_id}/tags/")
            except FloppyApiUnavailable:
                raise Failed("Floppy Error: Your Floppy server does not support item tags")
            except Failed as e:
                if "not found" in str(e).lower():
                    continue
                raise
            tags = payload.get("results", payload) if isinstance(payload, dict) else payload
            if not isinstance(tags, list):
                raise Failed("Floppy Error: Invalid tag response")
            return [str(tag.get("name", "")).strip() for tag in tags if isinstance(tag, dict) and str(tag.get("name", "")).strip()]
        return []

    def get_overlay_rating(self, media_type, tmdb_id=None, tvdb_id=None, imdb_id=None, season=None, episode=None):
        """Return Floppy's original decimal rating for direct overlay display."""
        self._load_ratings()
        ratings = self._ratings
        if ratings is None:
            raise Failed("Floppy Error: Ratings could not be loaded")
        for source, media_id in (("tmdb", tmdb_id), ("tvdb", tvdb_id), ("imdb", imdb_id)):
            if media_id is not None:
                key = (media_type, source, str(media_id), season, episode)
                if key in ratings:
                    return ratings[key]
        raise Failed

    def get_ids(self, list_data, is_movie=None):
        list_url = list_data["url"] if isinstance(list_data, dict) else list_data
        list_id = self._list_id(list_url)
        logger.info(f"Processing Floppy List: {list_url}")
        ids = self._api_ids(list_id, is_movie) if self.token else self._public_ids(list_id, is_movie)
        if not ids:
            raise Failed(f"Floppy Error: No IDs found in {list_url}")
        return ids
