import hashlib
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx
from serializd import SerializdClient
from serializd.exceptions import SerializdError

from modules.util import Failed

mobile_url = "https://serializd.onrender.com/mobile/page"
builders = [
    "serializd_list",
    "serializd_watchlist",
    "serializd_trending",
    "serializd_popular",
    "serializd_featured",
]
chart_endpoints = {
    "serializd_trending": "trending_shows",
    "serializd_popular": "popular_shows",
    "serializd_featured": "featured",
}
list_url_pattern = re.compile(r"^/list/(?:[^/]+-)?(?P<list_id>\d+)/?$")
watchlist_url_pattern = re.compile(r"^/user/(?P<username>[^/]+)/watchlist/?$")
username_pattern = re.compile(r"^[A-Za-z0-9_.-]+$")


class Serializd:
    def __init__(self, email, password, timeout=60):
        self.client = SerializdClient()
        self.client.session.timeout = timeout
        self.cache_key = hashlib.sha256(str(email).strip().lower().encode("utf-8")).hexdigest()
        for attempt in range(1, 4):
            try:
                self.client.login(email=email, password=password)
                break
            except httpx.TransportError as err:
                if attempt == 3:
                    raise Failed(f"Serializd Error: Failed to authenticate after {attempt} attempts: {err}") from err
            except Exception as err:
                raise Failed(f"Serializd Error: Failed to authenticate: {err}") from err

    @staticmethod
    def _tmdb_id(tmdb_id):
        try:
            tmdb_id = int(tmdb_id)
        except (TypeError, ValueError) as err:
            raise Failed("Serializd Error: TMDb ID is required") from err
        if tmdb_id < 1:
            raise Failed("Serializd Error: TMDb ID is required")
        return tmdb_id

    def get_show_genres(self, tmdb_id):
        tmdb_id = self._tmdb_id(tmdb_id)
        try:
            show = self.client.get_show(tmdb_id)
        except (httpx.HTTPError, SerializdError, ValueError, TypeError) as err:
            raise Failed(f"Serializd Error: Failed to fetch TMDb Show ID {tmdb_id}: {err}") from err
        return [genre.name for genre in show.genres]

    def get_show_nanogenres(self, tmdb_id):
        tmdb_id = self._tmdb_id(tmdb_id)
        data = self._get_json(f"/show/{tmdb_id}/nanogenres", f"nanogenres for TMDb Show ID {tmdb_id}")
        return [self._without_leading_emoji(str(nanogenre["name"])) for nanogenre in data.get("nanogenres", []) if nanogenre.get("name")]

    @staticmethod
    def _without_leading_emoji(name):
        for index, character in enumerate(name):
            if character.isalnum():
                return name[index:]
        return name

    def get_show_all_genres(self, tmdb_id):
        return list(dict.fromkeys(self.get_show_genres(tmdb_id) + self.get_show_nanogenres(tmdb_id)))

    def _get_rating(self, url, description):
        rating = self._get_json(url, description).get("averageRating")
        if not rating:
            raise Failed(f"Serializd Error: No rating found for {description}")
        return float(rating)

    def get_show_rating(self, tmdb_id):
        tmdb_id = self._tmdb_id(tmdb_id)
        return self._get_rating(f"{mobile_url}/show_v2_part_1/{tmdb_id}", f"TMDb Show ID {tmdb_id}")

    def get_episode_rating(self, tmdb_id, season_number, episode_number):
        tmdb_id = self._tmdb_id(tmdb_id)
        url = f"{mobile_url}/show/{tmdb_id}/season/{int(season_number)}/episode_part_1/{int(episode_number)}"
        return self._get_rating(url, f"TMDb Show ID {tmdb_id} S{int(season_number):02}E{int(episode_number):02}")

    def get_episode_user_rating(self, tmdb_id, season_number, episode_number):
        tmdb_id = self._tmdb_id(tmdb_id)
        description = f"TMDb Show ID {tmdb_id} S{int(season_number):02}E{int(episode_number):02}"
        url = f"{mobile_url}/show/{tmdb_id}/season/{int(season_number)}/episode_part_2/{int(episode_number)}"
        reviews = self._get_json(url, description).get("episodeReviewsForLoggedInUser") or []
        for review in reviews:
            if isinstance(review, dict) and review.get("rating") is not None:
                return float(review["rating"])
        raise Failed(f"Serializd Error: No user rating found for {description}")

    def _get_json(self, url, description, params=None):
        try:
            response = self.client.session.get(url, **({"params": params} if params is not None else {}))
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                raise ValueError("response was not a JSON object")
            return data
        except (httpx.HTTPError, SerializdError, ValueError, TypeError) as err:
            raise Failed(f"Serializd Error: Failed to fetch {description}: {err}") from err

    @staticmethod
    def _list_id(value):
        parsed = urlparse(str(value).strip())
        if parsed.scheme not in ["http", "https"] or parsed.netloc.lower() not in ["serializd.com", "www.serializd.com"]:
            raise Failed(f"Serializd Error: Invalid list URL: {value}")
        match = list_url_pattern.fullmatch(parsed.path)
        if not match:
            raise Failed(f"Serializd Error: Invalid list URL: {value}")
        return int(match.group("list_id"))

    @staticmethod
    def _watchlist_user(value):
        value = str(value).strip()
        if value.lower() == "me":
            return "me"
        parsed = urlparse(value)
        if parsed.scheme or parsed.netloc:
            if parsed.scheme not in ["http", "https"] or parsed.netloc.lower() not in ["serializd.com", "www.serializd.com"]:
                raise Failed(f"Serializd Error: Invalid watchlist URL: {value}")
            match = watchlist_url_pattern.fullmatch(parsed.path)
            if not match:
                raise Failed(f"Serializd Error: Invalid watchlist URL: {value}")
            value = match.group("username")
        if not username_pattern.fullmatch(value):
            raise Failed(f"Serializd Error: Invalid username: {value}")
        return value

    def validate_builder(self, method, values):
        if method in chart_endpoints:
            if isinstance(values, bool) or (isinstance(values, float) and not values.is_integer()):
                raise Failed(f"Serializd Error: {method} must be an integer greater than 0")
            try:
                limit = int(values)
            except (TypeError, ValueError) as err:
                raise Failed(f"Serializd Error: {method} must be an integer greater than 0") from err
            if limit < 1:
                raise Failed(f"Serializd Error: {method} must be an integer greater than 0")
            return [limit]
        validated = []
        for value in values if isinstance(values, list) else [values]:
            if isinstance(value, dict) or value is None:
                raise Failed(f"Serializd Error: {method} must be a URL or username")
            validated.append(self._list_id(value) if method == "serializd_list" else self._watchlist_user(value))
        if not validated:
            raise Failed(f"Serializd Error: {method} is blank")
        return validated

    def _authenticated_username(self):
        data = self._get_json("/user_information", "authenticated user information")
        username = data.get("username")
        if not username and isinstance(data.get("user"), dict):
            username = data["user"].get("username")
        if not username and isinstance(data.get("details"), dict):
            username = data["details"].get("username")
        if not username:
            raise Failed("Serializd Error: Authenticated username was not returned by the API")
        return str(username)

    def get_builder_ids(self, method, value):
        if method == "serializd_list":
            return self._list_ids(value)
        if method in chart_endpoints:
            return self._chart_ids(method, value)
        username = self._authenticated_username() if value == "me" else value
        return self._watchlist_ids(username)

    def _chart_ids(self, method, limit):
        ids = []
        seen = set()
        page = 1
        while len(ids) < limit:
            data = self._get_json(
                f"{mobile_url}/{chart_endpoints[method]}",
                f"{method.replace('_', ' ')} page {page}",
                params={"page": page},
            )
            results = data.get("results") or []
            shows = [result.get("showDetails") for result in results] if method == "serializd_featured" else results
            self._extend_show_ids(ids, seen, shows, "id", limit=limit)
            if page >= int(data.get("totalPages") or 1) or not results:
                break
            page += 1
        return ids

    def _list_ids(self, list_id):
        ids = []
        seen = set()
        seen_pages = set()
        cursor_time = datetime.now(timezone.utc).isoformat()
        page = 1
        while True:
            data = self._get_json(
                f"{mobile_url}/list/list_items/{int(list_id)}",
                f"list {list_id} page {page}",
                params={"page": page, "cursor_time": cursor_time},
            )
            items = data.get("listItems") or []
            page_signature = tuple((item.get("showId"), item.get("seasonId"), (item.get("episode") or {}).get("episodeNumber") if isinstance(item.get("episode"), dict) else None) for item in items)
            if not items or page_signature in seen_pages:
                break
            seen_pages.add(page_signature)
            self._extend_show_ids(ids, seen, items, "showId")
            page += 1
        return ids

    def _watchlist_ids(self, username):
        ids = []
        seen = set()
        page = 1
        while True:
            data = self._get_json(
                f"/user/{username}/watchlistpage_v2/{page}",
                f"{username} watchlist page {page}",
                params={"sort_by": "date_added_desc", "filters": "{}"},
            )
            self._extend_show_ids(ids, seen, data.get("items") or [], "showId")
            if page >= int(data.get("totalPages") or 1):
                break
            page += 1
        return ids

    @staticmethod
    def _extend_show_ids(ids, seen, items, id_key, limit=None):
        for item in items:
            if not isinstance(item, dict) or item.get(id_key) is None:
                continue
            show_id = int(item[id_key])
            if show_id not in seen:
                ids.append((show_id, "tmdb_show"))
                seen.add(show_id)
                if limit and len(ids) >= limit:
                    break

    def log_watched_episodes(self, tmdb_id, season_number, episode_numbers):
        tmdb_id = self._tmdb_id(tmdb_id)
        episode_numbers = sorted({int(number) for number in episode_numbers})
        if not episode_numbers:
            return False
        description = f"TMDb Show ID {tmdb_id} Season {int(season_number)} Episodes {episode_numbers}"
        try:
            season = self.client.get_season(tmdb_id, int(season_number))
            if not self.client.log_episodes(tmdb_id, season.seasonId, episode_numbers):
                raise Failed(f"Serializd Error: Failed to mark watched episodes for {description}")
        except Failed:
            raise
        except (httpx.HTTPError, SerializdError, ValueError, TypeError) as err:
            raise Failed(f"Serializd Error: Failed to mark watched episodes for {description}: {err}") from err
        return True
