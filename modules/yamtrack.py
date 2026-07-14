import re
from urllib.parse import urljoin, urlparse

from lxml import html

from modules import util
from modules.util import Failed

logger = util.logger

builders = ["yamtrack_list", "yamtrack_list_details", "yamtrack_tracked"]
details_pattern = re.compile(r"^/details/tmdb/(?P<media_type>movie|tv)/(?P<tmdb_id>\d+)(?:/|$)")
mal_details_pattern = re.compile(r"^/details/mal/anime/(?P<mal_id>\d+)(?:/|$)")
tracked_statuses = {
    "dropped": ("text-red", "Dropped"),
    "planning": ("text-sky", "Planning"),
    "in_progress": ("text-indigo", "In Progress"),
    "paused": ("text-orange", "Paused"),
    "completed": ("text-emerald", "Completed"),
}
tracked_types = {
    "movies": ("movie", "tmdb"),
    "tv_shows": ("tv", "tmdb_show"),
    "anime": ("anime", "mal"),
}
cross_library_tracked_types = ["anime"]


class YamTrack:
    def __init__(self, requests, params):
        self.requests = requests
        self.url = params["url"].rstrip("/")
        self.username = params["username"]
        self.password = params["password"]
        if logger:
            logger.secret(self.password)

    def _headers(self, referer=None):
        return {"Referer": referer or self.url}

    def _request_html(self, url):
        if logger:
            logger.trace(f"URL: {url}")
        try:
            response = self.requests.get(url, headers=self._headers(), header=True)
        except Exception as e:
            raise Failed(f"YamTrack Error: Failed to load {url}: {e}") from e
        if response.status_code >= 400:
            raise Failed(f"YamTrack Error: {response.status_code} on {url}")
        return response

    def _login(self, next_path="/"):
        login_url = urljoin(f"{self.url}/", f"accounts/login/?next={next_path}")
        page = self._request_html(login_url)
        try:
            login_page = html.fromstring(page.content)
            token = login_page.xpath("string(//input[@name='csrfmiddlewaretoken']/@value)")
            next_value = login_page.xpath("string(//input[@name='next']/@value)") or next_path
        except Exception:
            token = ""
            next_value = next_path

        data = {"login": self.username, "username": self.username, "password": self.password, "next": next_value}
        if token:
            data["csrfmiddlewaretoken"] = token
        headers = self._headers(referer=login_url)
        if token:
            headers["X-CSRFToken"] = token
        response = self.requests.post(urljoin(f"{self.url}/", "accounts/login/"), data=data, headers=headers, header=True)
        if response.status_code >= 400:
            raise Failed(f"YamTrack Error: Login failed with status {response.status_code}")
        if urlparse(getattr(response, "url", login_url)).path.rstrip("/") == "/accounts/login":
            raise Failed("YamTrack Error: Login failed")

    def _html(self, list_url):
        if not self._is_yamtrack_url(list_url):
            raise Failed(f"YamTrack Error: {list_url} must start with {self.url}")
        response = self._request_html(list_url)
        if urlparse(getattr(response, "url", list_url)).path.rstrip("/") == "/accounts/login":
            self._login(urlparse(list_url).path or "/")
            response = self._request_html(list_url)
        try:
            return html.fromstring(response.content)
        except Exception as e:
            raise Failed(f"YamTrack Error: Failed to parse {list_url}: {e}") from e

    def _is_yamtrack_url(self, url):
        parsed = urlparse(url)
        expected = urlparse(self.url)
        return parsed.scheme == expected.scheme and parsed.netloc == expected.netloc

    def test_connection(self):
        self._html(f"{self.url}/")

    def validate_lists(self, err_type, yamtrack_lists):
        valid_lists = []
        for value in util.get_list(yamtrack_lists, split=False, return_none=False):
            if isinstance(value, dict):
                raise Failed(f"{err_type} Error: YamTrack List cannot be a dictionary")
            list_url = str(value).strip()
            self._html(list_url)
            valid_lists.append(list_url)
        if not valid_lists:
            raise Failed(f"{err_type} Error: No valid YamTrack Lists")
        return valid_lists

    def validate_tracked(self, err_type, yamtrack_tracked, is_movie=None):
        if not isinstance(yamtrack_tracked, dict):
            raise Failed(f"{err_type} Error: yamtrack_tracked must be a dictionary")

        methods = {m.lower(): m for m in yamtrack_tracked}
        tracked = {}
        for media_type in tracked_types:
            if not self._tracked_type_applies(media_type, is_movie):
                tracked[media_type] = self._default_statuses(False)
                continue
            if media_type not in methods:
                tracked[media_type] = self._default_statuses(False)
                continue
            media_data = yamtrack_tracked[methods[media_type]]
            if not isinstance(media_data, dict):
                raise Failed(f"{err_type} Error: yamtrack_tracked {media_type} must be a dictionary")
            media_methods = {m.lower(): m for m in media_data}
            tracked[media_type] = {}
            for status in tracked_statuses:
                tracked[media_type][status] = util.parse(err_type, status, media_data, methods=media_methods, parent=f"yamtrack_tracked {media_type}", datatype="bool", default=True)

        if not any(enabled for statuses in tracked.values() for enabled in statuses.values()):
            raise Failed(f"{err_type} Error: yamtrack_tracked must have at least one status set to true")
        return tracked

    def list_description(self, list_url):
        page = self._html(list_url)
        description = page.xpath("string(//textarea[@name='description'])").strip()
        if not description:
            description = page.xpath("string(//*[@id='id_description'])").strip()
        return description

    def get_tmdb_ids(self, method, list_url, is_movie=None):
        pretty = method.replace("_", " ").title()
        if logger:
            logger.info(f"Processing {pretty}: {list_url}")
        page = self._html(list_url)
        ids = []
        seen = set()
        for href in page.xpath("//a/@href"):
            parsed = self._parse_href(href)
            match = details_pattern.match(parsed.path)
            if not match:
                continue
            tmdb_id = int(match.group("tmdb_id"))
            id_type = "tmdb" if match.group("media_type") == "movie" else "tmdb_show"
            if is_movie is True and id_type != "tmdb":
                continue
            if is_movie is False and id_type != "tmdb_show":
                continue
            key = (tmdb_id, id_type)
            if key not in seen:
                ids.append(key)
                seen.add(key)
        if not ids:
            raise Failed(f"YamTrack Error: No TMDb IDs found in {list_url}")
        return ids

    def get_tracked_tmdb_ids(self, tracked, is_movie=None):
        ids, _ = self.get_tracked_ids(tracked, is_movie=is_movie)
        if not ids:
            raise Failed("YamTrack Error: No TMDb IDs found in tracked items")
        return ids

    def get_tracked_ids(self, tracked, is_movie=None):
        ids = []
        mal_ids = []
        seen = set()
        seen_mal = set()
        for media_type, (url_type, id_type) in tracked_types.items():
            if not self._tracked_type_applies(media_type, is_movie):
                continue
            enabled_statuses = {status for status, enabled in tracked[media_type].items() if enabled}
            if not enabled_statuses:
                continue
            tracked_url = f"{self.url}/{self.username}/{url_type}"
            if logger:
                logger.info(f"Processing YamTrack Tracked: {tracked_url}")
            page = self._html(tracked_url)
            if id_type == "mal":
                for mal_id, status in self._tracked_anime_items(page):
                    if status not in enabled_statuses or mal_id in seen_mal:
                        continue
                    mal_ids.append(mal_id)
                    seen_mal.add(mal_id)
            else:
                for tmdb_id, found_id_type, status in self._tracked_items(page):
                    if found_id_type != id_type or status not in enabled_statuses:
                        continue
                    key = (tmdb_id, found_id_type)
                    if key not in seen:
                        ids.append(key)
                        seen.add(key)
        if not ids and not mal_ids:
            raise Failed("YamTrack Error: No IDs found in tracked items")
        return ids, mal_ids

    @staticmethod
    def _default_statuses(enabled):
        return {status: enabled for status in tracked_statuses}

    @staticmethod
    def _tracked_type_applies(media_type, is_movie):
        if media_type in cross_library_tracked_types or is_movie is None:
            return True
        return (is_movie is True and media_type == "movies") or (is_movie is False and media_type == "tv_shows")

    def _tracked_items(self, page):
        for link in page.xpath("//a[@href]"):
            href = link.get("href")
            parsed = self._parse_href(href)
            match = details_pattern.match(parsed.path)
            if not match:
                continue
            card = link.xpath("ancestor::div[@x-data][1]")
            status = self._card_status(card[0] if card else link)
            if status:
                id_type = "tmdb" if match.group("media_type") == "movie" else "tmdb_show"
                yield int(match.group("tmdb_id")), id_type, status

    def _tracked_anime_items(self, page):
        for link in page.xpath("//a[@href]"):
            href = link.get("href")
            parsed = self._parse_href(href)
            match = mal_details_pattern.match(parsed.path)
            if not match:
                continue
            row = link.xpath("ancestor::tr[1]")
            status = self._row_status(row[0] if row else link)
            if status:
                yield int(match.group("mal_id")), status

    @staticmethod
    def _card_status(card):
        for class_name in card.xpath(".//div[contains(@class, 'w-4') and contains(@class, 'h-4')]/@class"):
            for status, (color, _) in tracked_statuses.items():
                if color in class_name:
                    return status
        return None

    def _parse_href(self, href):
        return urlparse(href if href.startswith("http") else urljoin(self.url, href))

    @staticmethod
    def _row_status(row):
        row_text = [text.strip() for text in row.xpath(".//td/text()[normalize-space()]")]
        for status, (_, pretty) in tracked_statuses.items():
            if pretty in row_text:
                return status
        return None
