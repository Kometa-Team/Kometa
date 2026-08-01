import csv
import json
import re
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from io import StringIO
from urllib.parse import urlparse

from modules import util
from modules.util import Failed

logger = util.logger

builders = ["floppy_list", "floppy_list_details"]
list_pattern = re.compile(r"^/list/(?P<list_id>\d+)(?:/|$)")


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

    def _response(self, url):
        headers = {"X-API-Key": self.token} if self.token else None
        try:
            response = self.requests.get(url, headers=headers)
        except Exception as e:
            raise Failed(f"Floppy Error: Failed to load {url}: {e}") from e
        if response.status_code == 401:
            raise Failed("Floppy Error: Invalid or missing API token")
        if response.status_code == 403:
            raise Failed("Floppy Error: This list is private or the API token does not have access")
        if response.status_code == 404:
            raise Failed(f"Floppy Error: List not found at {url}")
        if response.status_code >= 400:
            raise Failed(f"Floppy Error: {response.status_code} on {url}")
        return response

    def _request(self, url):
        response = self._response(url)
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

    def get_rating(self, media_type, tmdb_id=None, tvdb_id=None, imdb_id=None, season=None, episode=None):
        self._load_ratings()
        candidates = [("tmdb", tmdb_id), ("tvdb", tvdb_id), ("imdb", imdb_id)]
        for source, media_id in candidates:
            if media_id is None:
                continue
            key = (media_type, source, str(media_id), season, episode)
            if key in self._ratings:
                # Plex's API is 0-10, but its UI renders each whole API point as
                # half a star. Round metadata writes to 0.5-star UI steps.
                return float(Decimal(str(self._ratings[key])).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        raise Failed

    def get_overlay_rating(self, media_type, tmdb_id=None, tvdb_id=None, imdb_id=None, season=None, episode=None):
        """Return Floppy's original decimal rating for direct overlay display."""
        self._load_ratings()
        for source, media_id in (("tmdb", tmdb_id), ("tvdb", tvdb_id), ("imdb", imdb_id)):
            if media_id is not None:
                key = (media_type, source, str(media_id), season, episode)
                if key in self._ratings:
                    return self._ratings[key]
        raise Failed

    def get_ids(self, list_data, is_movie=None):
        list_url = list_data["url"] if isinstance(list_data, dict) else list_data
        list_id = self._list_id(list_url)
        logger.info(f"Processing Floppy List: {list_url}")
        ids = self._api_ids(list_id, is_movie) if self.token else self._public_ids(list_id, is_movie)
        if not ids:
            raise Failed(f"Floppy Error: No IDs found in {list_url}")
        return ids
