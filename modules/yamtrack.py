import re
from urllib.parse import urljoin, urlparse

from lxml import html

from modules import util
from modules.util import Failed

logger = util.logger

builders = ["yamtrack_list", "yamtrack_list_details", "yamtrack_tracked"]
details_pattern = re.compile(r"^/details/tmdb/(?P<media_type>movie|tv)/(?P<tmdb_id>\d+)(?:/|$)")
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
}


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
        if not list_url.startswith(self.url):
            raise Failed(f"YamTrack Error: {list_url} must start with {self.url}")
        response = self._request_html(list_url)
        if urlparse(getattr(response, "url", list_url)).path.rstrip("/") == "/accounts/login":
            self._login(urlparse(list_url).path or "/")
            response = self._request_html(list_url)
        try:
            return html.fromstring(response.content)
        except Exception as e:
            raise Failed(f"YamTrack Error: Failed to parse {list_url}: {e}") from e

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
            if is_movie is True and media_type != "movies":
                tracked[media_type] = {status: False for status in tracked_statuses}
                continue
            if is_movie is False and media_type != "tv_shows":
                tracked[media_type] = {status: False for status in tracked_statuses}
                continue
            if media_type not in methods:
                tracked[media_type] = {status: False for status in tracked_statuses}
                continue
            media_methods = {m.lower(): m for m in yamtrack_tracked[methods[media_type]]} if media_type in methods and isinstance(yamtrack_tracked[methods[media_type]], dict) else {}
            tracked[media_type] = {}
            for status in tracked_statuses:
                tracked[media_type][status] = util.parse(err_type, status, yamtrack_tracked[methods[media_type]], methods=media_methods, parent=f"yamtrack_tracked {media_type}", datatype="bool", default=True)

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
            parsed = urlparse(href if href.startswith("http") else urljoin(self.url, href))
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
        ids = []
        seen = set()
        for media_type, (url_type, id_type) in tracked_types.items():
            if is_movie is True and media_type != "movies":
                continue
            if is_movie is False and media_type != "tv_shows":
                continue
            enabled_statuses = {status for status, enabled in tracked[media_type].items() if enabled}
            if not enabled_statuses:
                continue
            tracked_url = f"{self.url}/{self.username}/{url_type}"
            if logger:
                logger.info(f"Processing YamTrack Tracked: {tracked_url}")
            page = self._html(tracked_url)
            for tmdb_id, found_id_type, status in self._tracked_items(page):
                if found_id_type != id_type or status not in enabled_statuses:
                    continue
                key = (tmdb_id, found_id_type)
                if key not in seen:
                    ids.append(key)
                    seen.add(key)
        if not ids:
            raise Failed("YamTrack Error: No TMDb IDs found in tracked items")
        return ids

    def _tracked_items(self, page):
        for link in page.xpath("//a[@href]"):
            href = link.get("href")
            parsed = urlparse(href if href.startswith("http") else urljoin(self.url, href))
            match = details_pattern.match(parsed.path)
            if not match:
                continue
            card = link.xpath("ancestor::div[@x-data][1]")
            status = self._card_status(card[0] if card else link)
            if status:
                id_type = "tmdb" if match.group("media_type") == "movie" else "tmdb_show"
                yield int(match.group("tmdb_id")), id_type, status

    @staticmethod
    def _card_status(card):
        for class_name in card.xpath(".//div[contains(@class, 'w-4') and contains(@class, 'h-4')]/@class"):
            for status, (color, _) in tracked_statuses.items():
                if color in class_name:
                    return status
        return None
