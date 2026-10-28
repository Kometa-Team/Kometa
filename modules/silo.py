"""Silo media server client and library.

Silo is a media server peer of Plex. Kometa talks to its native ``/api/v2`` API.
Collection membership is addressed with the catalog content id. Poster, backdrop,
logo, and overlay images are applied from a URL. A local file is published to
transfer.kometa.wiki first. Labels, item deletion, and playlists are refused
through the capability matrix.
"""

import json
import os
import re
import time
import uuid
from collections.abc import Iterable
from threading import Lock
from types import SimpleNamespace
from urllib.parse import quote, urljoin, urlsplit

import requests

from modules import util
from modules.library import Library
from modules.local_search import compile_selector
from modules.media_server import Capability, CapabilityMatrix, MediaServer, log_server_connection, register_media_server
from modules.util import BuilderValidationError, CollectionNotFound, Failed

logger = util.logger

LIBRARY_TYPES = {"movies": "Movie", "series": "Show"}
TAG_FIELDS = {"genre": "genres", "studio": "studios", "network": "networks", "country": "countries"}
PERSON_FIELDS = {"actor", "director", "writer", "producer"}
TRANSFER_BASE = "https://transfer.kometa.wiki"
TRANSFER_MAX_DAYS = "7"
TRANSFER_DOWNLOAD_DELAY = 0.75
REQUEST_INTERVAL = 0.5
_REQUEST_PACERS = {}
_REQUEST_PACERS_LOCK = Lock()
IMAGE_EXTENSIONS = {".jpg", ".png", ".webp"}
ARTWORK_KINDS = {"poster": "poster", "background": "backdrop", "backdrop": "backdrop", "logo": "logo"}
IMAGE_SOURCES = {"tmdb": "TMDb", "tvdb": "TVDb", "trakt": "Trakt", "ytmusic": "YouTube Music"}


def _resolution_value(value):
    value = str(value).strip().lower()
    value = {"4k": "2160p", "uhd": "2160p", "8k": "4320p", "2k": "1440p"}.get(value, value)
    return f"{value}p" if value.isascii() and value.isdecimal() else value


def _transfer_filename(location, kind):
    extension = os.path.splitext(str(location))[1].lower()
    if extension == ".jpeg":
        extension = ".jpg"
    if extension not in IMAGE_EXTENSIONS:
        extension = ".jpg"
    return f"kometa-{kind}-{uuid.uuid4().hex[:12]}{extension}"


def publish_image(location, filename=None, timeout=60):
    """Publish a local image and return the public URL Silo can download."""
    path = os.fspath(location)
    if not os.path.isfile(path):
        raise Failed(f"Silo Error: Image file not found: {path}")
    name = filename or _transfer_filename(path, "image")
    name = re.sub(r"[^A-Za-z0-9._-]", "-", name).strip("-.") or "image.jpg"
    try:
        with open(path, "rb") as handle:
            response = requests.put(f"{TRANSFER_BASE}/{quote(name)}", data=handle, headers={"Max-Days": TRANSFER_MAX_DAYS}, timeout=timeout)
    except requests.RequestException as error:
        raise Failed(f"Silo Error: Could not publish {os.path.basename(path)} to transfer.kometa.wiki: {error}") from error
    body = (response.text or "").strip()
    if response.status_code >= 400 or not body.startswith(f"{TRANSFER_BASE}/"):
        detail = body.replace("\n", " ")[:200]
        raise Failed(f"Silo Error: transfer.kometa.wiki returned {response.status_code}{f': {detail}' if detail else ''}")
    return body


def api_base(url):
    base = str(url).strip().rstrip("/")
    if base.endswith("/api/v2"):
        return base
    return f"{base}/api/v2"


def kometa_library_type(silo_type):
    mapped = LIBRARY_TYPES.get(str(silo_type or ""))
    if mapped is None:
        raise Failed(f"Silo Error: Library type '{silo_type}' is not movies or series")
    return mapped


def select_silo_library(libraries, name):
    match = next((library for library in libraries if library.get("name") == name), None)
    if match is None:
        options = [library.get("name") for library in libraries]
        raise Failed(f"Silo Error: Library '{name}' not found. Options: {options}")
    kometa_library_type(match.get("type"))
    return match


class SiloMediaServer(MediaServer):
    type_name = "silo"
    type_label = "Silo"

    def __init__(self, url, token, timeout=60, verify_ssl=None, db_cache=None, name=None, profile_id=None):
        super().__init__(url=url, token=token, timeout=timeout, verify_ssl=verify_ssl, db_cache=db_cache, name=name)
        self.profile_id = profile_id

    @property
    def capabilities(self) -> CapabilityMatrix:
        return SILO_CAPABILITIES

    @classmethod
    def from_config(cls, silo_config, name=None, profile_id=None):
        timeout = silo_config["timeout"] if "timeout" in silo_config and silo_config["timeout"] is not None else 60
        return cls(
            url=silo_config["url"],
            token=silo_config["token"],
            timeout=timeout,
            verify_ssl=silo_config.get("verify_ssl"),
            name=name,
            profile_id=profile_id if profile_id is not None else silo_config.get("profile_id"),
        )


class _RequestPacer:
    def __init__(self):
        self.lock = Lock()
        self.last_request_at = None

    def wait(self):
        with self.lock:
            now = time.monotonic()
            if self.last_request_at is not None:
                delay = REQUEST_INTERVAL - (now - self.last_request_at)
                if delay > 0:
                    time.sleep(delay)
            self.last_request_at = time.monotonic()
            return self.last_request_at


class SiloClient:
    """HTTP client for one Silo server. The token is a bearer session token or API key."""

    def __init__(self, server, session=None):
        self.server = server
        self.base = api_base(server.url)
        self.session = session or requests.Session()
        self.session.headers["Authorization"] = f"Bearer {server.token}"
        self.session.headers["Accept"] = "application/json"
        if server.profile_id:
            self.session.headers["X-Profile-Id"] = str(server.profile_id)
        if server.verify_ssl is False:
            self.session.verify = False
        self._listing_profiles = False
        parsed = urlsplit(self.base)
        server_key = parsed._replace(scheme=parsed.scheme.lower(), netloc=parsed.netloc.lower()).geturl()
        with _REQUEST_PACERS_LOCK:
            self._request_pacer = _REQUEST_PACERS.setdefault(server_key, _RequestPacer())

    def request(self, method, path, params=None, json_body=None, headers=None, files=None):
        for attempt in range(6):
            self._request_pacer.wait()
            try:
                response = self.session.request(method, f"{self.base}/{path.lstrip('/')}", params=params, json=json_body, files=files, headers=headers, timeout=self.server.timeout)
            except requests.RequestException as error:
                raise Failed(f"Silo Error: {method} {path} failed: {error}") from error
            if response.status_code != 429 or attempt == 5:
                break
            delay = util.wait_for_retry_after_header.parse(response.headers.get("Retry-After"))
            if delay is None:
                delay = min(2**attempt, 10)
            logger.warning(f"Silo rate limit: {method} {path}; retrying in {delay:g} seconds ({attempt + 1}/5)")
            time.sleep(delay)
        if response.status_code >= 400:
            detail = _response_detail(response)
            if _profile_not_found(response):
                detail = self._missing_profile_detail()
            elif len(detail) > 300:
                detail = detail[:300]
            error_type = CollectionNotFound if response.status_code == 404 and method.upper() == "GET" and re.fullmatch(r"/admin/collections/[^/]+", path) else Failed
            raise error_type(f"Silo Error: {method} {path} returned {response.status_code}{f': {detail}' if detail else ''}")
        if response.status_code == 204 or not response.content:
            return None, response.headers
        try:
            return response.json(), response.headers
        except ValueError as error:
            raise Failed(f"Silo Error: {method} {path} did not return JSON") from error

    def _pages(self, method, path, params=None, json_body=None):
        query = dict(params or {})
        body = dict(json_body or {})
        while True:
            if method == "GET":
                data, _headers = self.request("GET", path, params=query)
            else:
                data, _headers = self.request(method, path, params=query, json_body=body)
            if isinstance(data, list):
                yield data, len(data)
                return
            page_items = (data or {}).get("items") or []
            total = (data or {}).get("total") if isinstance(data, dict) else None
            yield page_items, total if isinstance(total, int) else None
            page = (data or {}).get("page") or {}
            cursor = page.get("next_cursor")
            if not page.get("has_more") or not cursor:
                return
            if method == "GET":
                query["cursor"] = cursor
            else:
                body["cursor"] = cursor

    def _items(self, method, path, params=None, json_body=None):
        items = []
        for page_items, _total in self._pages(method, path, params=params, json_body=json_body):
            items.extend(page_items)
        return items

    def list_libraries(self):
        return self._items("GET", "/libraries")

    def server_info(self):
        data, _ = self.request("GET", "/system/info")
        return {"name": self.server.display_name, "version": (data or {}).get("server_version")}

    def _missing_profile_detail(self):
        configured = self.server.profile_id
        detail = "Profile not found"
        if configured:
            detail += f" for profile_id '{configured}'"
        if self._listing_profiles:
            return detail
        choices = self._profile_choices()
        if choices:
            return f"{detail}. Available users and profiles: {choices}"
        return f"{detail}. Available users and profiles could not be listed"

    def _profile_choices(self):
        """List users and profiles without the profile header that Silo just rejected."""
        self._listing_profiles = True
        saved = self.session.headers.pop("X-Profile-Id", None)
        try:
            try:
                users = self._items("GET", "/admin/users")
            except Failed:
                users = None
            if users:
                return _format_user_profiles(self, users)
            return _format_account_profiles(self)
        finally:
            self._listing_profiles = False
            if saved is not None:
                self.session.headers["X-Profile-Id"] = saved

    def list_collections(self, library_id):
        return self._items("GET", "/admin/collections", params={"library_id": library_id})

    def get_collection(self, collection_id):
        data, headers = self.request("GET", f"/admin/collections/{_path_id(collection_id)}")
        return data, headers.get("ETag") or headers.get("Etag")

    def create_collection(self, payload):
        data, headers = self.request("POST", "/admin/collections", json_body=payload)
        return data, headers.get("ETag") or headers.get("Etag")

    def update_collection(self, collection_id, payload, etag):
        data, headers = self.request("PATCH", f"/admin/collections/{_path_id(collection_id)}", json_body=payload, headers={"If-Match": etag or "*"})
        return data, headers.get("ETag") or headers.get("Etag")

    def delete_collection(self, collection_id, etag):
        self.request("DELETE", f"/admin/collections/{_path_id(collection_id)}", headers={"If-Match": etag or "*"})

    def collection_items(self, collection_id):
        return self._items("GET", f"/admin/collections/{_path_id(collection_id)}/items")

    def add_collection_item(self, collection_id, content_id, position=0):
        path = f"/admin/collections/{_path_id(collection_id)}/items/{_path_id(content_id)}"
        data, _headers = self.request("PUT", path, json_body={"position": position})
        return data

    def remove_collection_item(self, collection_id, content_id):
        path = f"/admin/collections/{_path_id(collection_id)}/items/{_path_id(content_id)}"
        self.request("DELETE", path)

    def browse(self, library_id, media_type=None, query=None, limit=200):
        items = []
        for page_items, _total in self.catalog_pages(library_id, media_type=media_type, query=query, limit=limit):
            items.extend(page_items)
        return items

    def catalog_pages(self, library_id, media_type=None, query=None, limit=200):
        params = {"source": "query", "library_id": library_id, "limit": min(limit or 200, 200)}
        if media_type:
            params["type"] = media_type
        if query:
            params["q"] = query
        return self._pages("GET", "/catalog", params=params)

    def query(self, library_id, query_definition, limit=100):
        body = {"library_id": library_id, "limit": min(limit or 100, 100), "groups": _query_groups(query_definition)}
        if isinstance(query_definition, dict):
            body["match"] = query_definition.get("match", "all")
            if query_definition.get("media_scope"):
                body["type"] = query_definition["media_scope"]
            if query_definition.get("sort"):
                body["sort"] = query_definition["sort"]["field"]
                body["order"] = query_definition["sort"]["order"]
            if query_definition.get("limit"):
                body["query_limit"] = query_definition["limit"]
        return self._items("POST", "/catalog/query", json_body=body)

    def preview(self, query_definition, limit=20):
        data, _headers = self.request("POST", "/admin/collections/preview", json_body={"query_definition": _query_document(query_definition), "limit": limit})
        if isinstance(data, dict):
            return data.get("items") or []
        return data or []

    def get_item(self, content_id, library_id=None):
        params = {"library_id": library_id} if library_id else None
        data, _headers = self.request("GET", f"/catalog/items/{_path_id(content_id)}", params=params)
        return data or {}

    def update_metadata(self, content_id, fields):
        data, _headers = self.request("PATCH", f"/admin/items/{_path_id(content_id)}/metadata", json_body=fields)
        return data

    def refresh_metadata(self, content_id):
        self.request("POST", f"/admin/items/{_path_id(content_id)}/refresh-metadata", json_body={"mode": "quick"})

    def apply_item_image(self, content_id, kind, source_url):
        self.request("POST", f"/admin/items/{_path_id(content_id)}/images/apply", json_body={"type": kind, "original_url": source_url})

    def set_collection_artwork(self, collection_id, kind, source_url):
        self.request("PUT", f"/admin/collections/{_path_id(collection_id)}/{kind}", files={"source_url": (None, source_url)})


class SiloCollection:
    def __init__(self, data, etag=None):
        self.data = {}
        self.etag = None
        self.apply(data, etag=etag)

    def apply(self, data, etag=None):
        if data:
            self.data.update(data)
        self.id = self.data.get("id")
        self.ratingKey = self.id
        self.title = self.data.get("title") or self.data.get("name") or ""
        if etag:
            self.etag = etag
        self.smart = self.data.get("collection_type") == "smart"
        self.summary = self.data.get("description") or ""
        self.childCount = self.data.get("item_count") or 0


class SiloItem:
    def __init__(self, data, library):
        self.library = library
        self.data = {}
        self.apply(data or {})

    def apply(self, data):
        if data:
            self.data.update(data)
        self.content_id = self.data.get("content_id") or self.data.get("media_item_id")
        self.media_item_id = self.data.get("media_item_id") or self.content_id
        self.ratingKey = self.content_id
        self.key = self.content_id
        self.title = self.data.get("title") or ""
        self.year = self.data.get("year")
        self.type = {"series": "show"}.get(self.data.get("type"), self.data.get("type"))
        self.guid = f"silo://{self.content_id}"
        self.summary = self.data.get("overview") or self.data.get("description") or ""
        poster_url = self.data.get("poster_url")
        self.poster_url = urljoin(f"{self.library.client.server.url.rstrip('/')}/", poster_url) if poster_url else None
        self.posterUrl = self.poster_url
        self.thumb = self.poster_url
        self.tmdb_id = _numeric_id(self.data.get("tmdb_id"))
        self.tvdb_id = _numeric_id(self.data.get("tvdb_id"))
        self.imdb_id = self.data.get("imdb_id") or None
        self.genres = list(self.data.get("genres") or [])
        self.studios = list(self.data.get("studios") or [])
        self.networks = list(self.data.get("networks") or [])
        self.countries = list(self.data.get("countries") or [])
        self.actors = self._people(self.data.get("cast") or [])
        crew = self.data.get("crew") or []
        for role, jobs in {
            "directors": {"director"},
            "writers": {"writer", "screenplay", "story", "screenwriter"},
            "producers": {"producer", "executive producer", "co-producer", "associate producer"},
        }.items():
            setattr(self, role, self._people([credit for credit in crew if isinstance(credit, dict) and str(credit.get("job") or "").strip().casefold() in jobs]))

    @staticmethod
    def _people(credits):
        people = []
        seen = set()
        for credit in credits:
            if not isinstance(credit, dict):
                continue
            name = credit.get("name")
            if not isinstance(name, str) or not name.strip():
                continue
            name = name.strip()
            identity = name.casefold()
            if identity in seen:
                continue
            seen.add(identity)
            people.append(SimpleNamespace(id=credit.get("person_id") or f"name:{identity}", tag=name))
        return people

    def seasons(self):
        return self.library.list_seasons(self)

    def episodes(self):
        return self.library.list_episodes(self)


class Silo(Library):
    uses_overlay_labels = False

    def __init__(self, config, params, client=None):
        super().__init__(config, params)
        server = self.server
        if not isinstance(server, SiloMediaServer):
            raise Failed("Silo Error: Library is not connected to a Silo server")
        self.url = server.url
        self.token = server.token
        self.timeout = server.timeout
        logger.secret(self.url)
        logger.secret(self.token)
        self.client = client or SiloClient(server)
        self.session = self.client.session
        record = select_silo_library(self.client.list_libraries(), params["name"])
        self.silo_library = record
        self.library_id = record.get("id")
        self.type = kometa_library_type(record.get("type"))
        self.is_movie = self.type == "Movie"
        self.is_show = self.type == "Show"
        self.is_music = False
        self.is_other = False
        language = record.get("metadata_language") or "en"
        self.Plex = _SiloSection(self.type.lower(), language, self.library_id, record.get("name"))
        self.agent = "silo"
        self.scanner = "silo"
        self._all_items = []
        log_server_connection(logger, server, self.client.server_info)
        logger.info(f"Connected to library {params['name']}")
        logger.info(f"Type: {self.type}")

    def _silo(self):
        server = self.server
        if not isinstance(server, SiloMediaServer):
            raise Failed("Silo Error: Library is not connected to a Silo server")
        return server

    def notify(self, text, collection=None, critical=True):
        self.config.notify(text, server=self._silo().display_name, library=self.name, collection=collection, critical=critical)

    def notify_delete(self, message, playlist=False):
        self.config.notify_delete(message, server=self._silo().display_name, library=None if playlist else self.name)

    def _artwork_kind(self, image_type, poster=True):
        if image_type in ARTWORK_KINDS:
            return ARTWORK_KINDS[image_type]
        if poster and image_type in (None, "poster"):
            return "poster"
        status = self.require(Capability.UPLOAD_BANNER)
        raise Failed(f"{self._silo().display_name} cannot upload image bytes ({status.detail or image_type or 'banner'})")

    def _public_image_url(self, image, url=False, kind="poster"):
        location = image.location if hasattr(image, "location") and hasattr(image, "is_url") else image
        remote = image.is_url if hasattr(image, "is_url") and hasattr(image, "location") else url
        if not remote and isinstance(location, str) and location.startswith(("http://", "https://")):
            remote = True
        if remote:
            if not isinstance(location, str) or not location.startswith(("http://", "https://")):
                raise Failed("Silo Error: Image URL is missing")
            return location
        source_url = publish_image(location, filename=_transfer_filename(location, kind), timeout=self.timeout)
        logger.debug(f"Waiting {TRANSFER_DOWNLOAD_DELAY} seconds before Silo fetches the published image")
        time.sleep(TRANSFER_DOWNLOAD_DELAY)
        return source_url

    def upload_images(self, item, poster=None, background=None, logo=None, square_art=None, overlay=False):
        if isinstance(item, SiloCollection):
            for kind, image in (("logo", logo), ("square_art", square_art)):
                if image is not None:
                    logger.warning(f"Silo Warning: Collection {kind} artwork is not supported; skipping {kind} for {item.title}")
            logo = None
            square_art = None
        return super().upload_images(item, poster=poster, background=background, logo=logo, square_art=square_art, overlay=overlay)

    def _apply_artwork(self, item, kind, source_url):
        if isinstance(item, SiloCollection):
            if kind not in ("poster", "backdrop"):
                raise Failed(f"Silo Error: {self._silo().display_name} collections have no {kind} URL")
            self.client.set_collection_artwork(item.id, kind, source_url)
            return
        content_id = getattr(item, "content_id", None)
        if not content_id:
            raise Failed("Silo Error: Item has no content id for artwork")
        self.client.apply_item_image(content_id, kind, source_url)

    def _upload_image(self, item, image):
        self.require(Capability.UPLOAD_OVERLAY)
        kind = "poster" if image.is_poster else "backdrop" if image.is_background else "logo" if image.is_logo else None
        if kind is None:
            raise Failed(f"{self._silo().display_name} cannot upload this overlay image")
        self._apply_artwork(item, kind, self._public_image_url(image, kind=kind))
        return True

    def upload_poster(self, item, image, url=False):
        self.require(Capability.UPLOAD_POSTER)
        self._apply_artwork(item, "poster", self._public_image_url(image, url=url, kind="poster"))
        return True

    def image_update(self, item, image, tmdb=None, title=None, poster=True, image_type=None):
        image_type = image_type or ("poster" if poster else "background")
        display_type = {"poster": "Poster", "background": "Background", "backdrop": "Background", "logo": "Logo"}.get(image_type, image_type.replace("_", " ").title())
        text = f"{f'{title} ' if title else ''}{display_type}"
        if image is None and isinstance(tmdb, tuple) and tmdb[0] in ("lock", "unlock"):
            action = "Lock" if tmdb[0] == "lock" else "Unlock"
            logger.warning(f"{text} | {action} Not Supported")
            return action, "Silo", "Failed"
        kind = self._artwork_kind(image_type, poster=poster)
        capability = {"poster": Capability.UPLOAD_POSTER, "backdrop": Capability.UPLOAD_BACKDROP, "logo": Capability.UPLOAD_LOGO}[kind]
        self.require(capability)
        source = "URL"
        candidate = tmdb
        if image is not None:
            source = "URL" if (getattr(image, "is_url", False) or (isinstance(image, str) and image.startswith(("http://", "https://")))) else "Assets"
            candidate = image
        elif isinstance(tmdb, tuple):
            source = IMAGE_SOURCES.get(tmdb[0], str(tmdb[0] or "URL"))
            candidate = tmdb[1]
        if candidate is None or (isinstance(candidate, str) and not candidate):
            logger.warning(f"{text} | No Image URL")
            return "Reset", source, "Missing"
        source_url = self._public_image_url(candidate, kind=kind)
        self._apply_artwork(item, kind, source_url)
        logger.info(f"{text} | Set from {source_url}")
        return "Reset", source, "Updated"

    def upload_background(self, item, image, url=False):
        self.require(Capability.UPLOAD_BACKDROP)
        self._apply_artwork(item, "backdrop", self._public_image_url(image, url=url, kind="backdrop"))
        return True

    def upload_logo(self, item, image, url=False):
        self.require(Capability.UPLOAD_LOGO)
        self._apply_artwork(item, "logo", self._public_image_url(image, url=url, kind="logo"))
        return True

    def reload(self, item, force=False):
        if isinstance(item, SiloCollection):
            data, etag = self.client.get_collection(item.id)
            item.apply(data, etag=etag)
            return item
        cached = getattr(self, "_search_details", {}).get(item.content_id)
        if cached is not None and not force:
            item.apply(cached.data)
            return item
        self.require(Capability.RELOAD_ITEM_FORCE if force else Capability.RELOAD_ITEM)
        item.apply(self.client.get_item(item.content_id, library_id=self.library_id))
        if hasattr(self, "_search_details"):
            self._search_details[item.content_id] = item
        if force:
            getattr(self, "_native_rating_details", {}).pop(item.content_id, None)
        return item

    def item_reload(self, item, exclude_elements=None):
        return self.reload(item)

    def fetch_overlay_value(self, item, variable_name):
        if not variable_name.startswith("silo_"):
            return super().fetch_overlay_value(item, variable_name)
        sources = {
            "silo_imdb_rating": ("rating_imdb", "imdb", 10, 1),
            "silo_tmdb_rating": ("rating_tmdb", "tmdb", 10, 1),
            "silo_tomatoes_rating": ("rating_rt_critic", "rt_critic", 100, 0.1),
            "silo_tomatoesaudience_rating": ("rating_rt_audience", "rt_audience", 100, 0.1),
            "silo_user_rating": ("user_rating", None, 5, 2),
        }
        if variable_name not in sources:
            raise Failed(f"Silo Error: Unknown native rating source: {variable_name}")
        if not hasattr(self, "_native_rating_details"):
            self._native_rating_details = {}
        if item.content_id not in self._native_rating_details:
            self._native_rating_details[item.content_id] = self.client.get_item(item.content_id, library_id=self.library_id)
        detail = self._native_rating_details[item.content_id]
        field, source, maximum, factor = sources[variable_name]
        value = detail.get(field)
        if value is None and source:
            for rating in detail.get("ratings") or detail.get("rating_sources") or []:
                if rating.get("source") == source:
                    value = rating.get("score")
                    maximum, factor = 100, 0.1
                    break
        if util.is_missing_rating(value):
            return None
        minimum = 1 if field == "user_rating" else 0
        if not util.is_valid_rating(value, minimum=minimum, maximum=maximum):
            logger.warning(f"Silo Warning: Invalid {variable_name} value {value}; expected {minimum} to {maximum}")
            return None
        return float(value) * factor

    def update_collection_details(self, collection, summary, details):
        """Apply native collection metadata without Plex's automatic label edits."""
        self.item_reload(collection)
        for field in ("sort_title", "label", "label.remove", "label.sync", "visible_library", "visible_home", "visible_shared"):
            if field in details:
                logger.warning(f"Silo Warning: Collection {field} is not supported by this adapter; skipping {field}")
        for field in ("content_rating", "collection_mode", "collection_filtering"):
            if field in details:
                raise Failed(f"Silo Error: Collection metadata attribute {field} is not supported")
        payload = {}
        if summary and str(summary) != collection.summary:
            payload["description"] = str(summary)
        if "collection_order" in details:
            order = details["collection_order"]
            sort_config = self._collection_sort_config(order)
            if sort_config != (collection.data.get("sort_config") or {}):
                payload["sort_config"] = sort_config
        if not payload:
            return []
        data, etag = self.client.update_collection(collection.id, payload, collection.etag)
        collection.apply({**payload, **(data or {})}, etag=etag)
        logger.info("Collection metadata updated")
        return ["Metadata"]

    @staticmethod
    def _collection_sort_config(order):
        if order in ("custom", "custom.asc", "custom.desc"):
            return {}
        if order == "release":
            return {"field": "release_date", "order": "asc"}
        if order == "alpha":
            return {"field": "title", "order": "asc"}
        field, _, direction = str(order).rpartition(".")
        fields = {"title": "title", "release": "release_date", "added": "added_at", "year": "year", "duration": "runtime", "content_rating": "content_rating"}
        if field not in fields or direction not in ("asc", "desc"):
            raise Failed(f"Silo Error: Unsupported collection order: {order}")
        return {"field": fields[field], "order": direction}

    def sort_collection_items(self, collection, items, order):
        if isinstance(order, list):
            if len(order) != 1:
                raise Failed("Silo Error: Collection sorting accepts one sort field")
            config = self._collection_sort_config(order[0])
            self.item_reload(collection)
            if config != collection.data.get("sort_config"):
                data, etag = self.client.update_collection(collection.id, {"sort_config": config}, collection.etag)
                collection.apply({"sort_config": config, **(data or {})}, etag=etag)
            return
        if order not in ("custom", "custom.asc", "custom.desc"):
            raise Failed(f"Silo Error: Unsupported custom collection order: {order}")
        if collection.smart:
            raise Failed("Silo Error: Explicit item ordering requires a manual collection")
        members = self.client.collection_items(collection.id)
        if any(not (row.get("media_item_id") or row.get("content_id")) or not isinstance(row.get("position"), int) for row in members):
            raise Failed("Silo Error: Invalid collection membership response; sorting aborted before changes")
        members.sort(key=lambda row: row["position"])
        positions = {str(row.get("media_item_id") or row.get("content_id")): row.get("position", index) for index, row in enumerate(members)}
        desired = list(dict.fromkeys(str(item.content_id) for item in (list(reversed(items)) if order == "custom.desc" else items)))
        # Preserve append-mode members absent from the current builder result.
        desired.extend(key for key in positions if key not in desired)
        if any(key not in positions for key in desired):
            raise Failed("Silo Error: Collection membership changed before sorting; rerun to refresh it")
        for position, key in enumerate(desired):
            original_position = positions[key]
            if original_position == position:
                continue
            self.client.remove_collection_item(collection.id, key)
            try:
                self.client.add_collection_item(collection.id, key, position=position)
            except Failed as error:
                try:
                    self.client.add_collection_item(collection.id, key, position=original_position)
                except Failed as restore_error:
                    raise Failed(f"Silo Error: Sorting failed and membership could not be restored for {key}: {restore_error}") from error
                raise

    def edit_tags(self, attr, obj, add_tags=None, remove_tags=None, sync_tags=None, do_print=True, locked=True, is_locked=None):
        if attr in ("label", "labels"):
            self.require(Capability.GET_ITEM_LABELS)
        field = TAG_FIELDS.get(attr)
        if field is None:
            raise Failed(f"Silo Error: {self._silo().display_name} cannot edit {attr.replace('_', ' ')}")
        self.require(Capability.SYNC_TAGS)
        current = list(getattr(obj, field, None) or [])
        if sync_tags is not None:
            updated = list(sync_tags)
        else:
            updated = [tag for tag in current if tag not in (remove_tags or [])]
            updated.extend(tag for tag in (add_tags or []) if tag not in updated)
        self.client.update_metadata(obj.content_id, {field: updated})
        obj.apply({field: updated})
        if do_print:
            logger.info(f"{obj.title} | {attr} | {', '.join(updated)}")
        return ", ".join(updated)

    def get_tags(self, tag):
        if tag == "country":
            if not hasattr(self, "_country_values"):
                data, _ = self.client.request("GET", "/catalog/filters", params={"source": "query", "library_id": self.library_id, "type": _media_type(self, None), "skip_technical": "true"})
                self._country_values = (data or {}).get("countries") or []
            names = {self._country_names().get(value.upper(), value) for value in self._country_values if isinstance(value, str) and value.strip()}
            return [SimpleNamespace(key=name, title=name) for name in sorted(names)]
        if tag in ("decade", "year"):
            years = {int(item.year) for item in self.get_all(ignore_schedule_scope=True) if not isinstance(item.year, bool) and str(item.year).isascii() and str(item.year).isdecimal() and 1 <= int(item.year) <= 9999}
            if tag == "decade":
                return [SimpleNamespace(key=str(year), title=f"{year}s") for year in sorted({year // 10 * 10 for year in years})]
            return [SimpleNamespace(key=str(year), title=str(year)) for year in sorted(years)]
        if tag in ("contentRating", "content_rating"):
            names = {item.data.get("content_rating") for item in self.get_all(ignore_schedule_scope=True)}
            return [SimpleNamespace(key=name, title=name) for name in sorted(name for name in names if isinstance(name, str) and name.strip())]
        if tag in ("resolution", "episode.resolution"):
            names = set()
            for item in self._local_search_items(builder_level="episode" if tag.startswith("episode.") else None, ignore_schedule_scope=True):
                values = [version.get("resolution") for version in item.data.get("versions") or []]
                if not any(values):
                    values = [(item.data.get("overlay_summary") or {}).get("resolution")]
                for value in values:
                    if value is not None and str(value).strip():
                        resolution = _resolution_value(value)
                        names.add({"2160p": "4k", "4320p": "8k", "1440p": "2k"}.get(resolution, resolution[:-1] if re.fullmatch(r"\d+p", resolution) else resolution))
            return [SimpleNamespace(key=name, title=name) for name in sorted(names)]
        if tag in ("audioLanguage", "audio_language", "episode.audioLanguage", "episode.audio_language", "subtitleLanguage", "subtitle_language", "episode.subtitleLanguage", "episode.subtitle_language"):
            level = "episode" if tag.startswith("episode.") else None
            tracks = ("subtitle_tracks", "external_subtitles") if "subtitle" in tag else ("audio_tracks",)
            names = set()
            for item in self._local_search_items(builder_level=level, ignore_schedule_scope=True):
                for version in item.data.get("versions") or []:
                    for field in tracks:
                        for track in version.get(field) or []:
                            language = track.get("language")
                            if isinstance(language, str) and language.strip():
                                names.add(language.strip().lower())
            return [SimpleNamespace(key=name, title=name) for name in sorted(names)]
        field = TAG_FIELDS.get(tag)
        if field is None:
            raise Failed(f"Silo Error: Dynamic collection tag '{tag}' is not supported; supported tags: {', '.join(TAG_FIELDS)}, audio_language, subtitle_language, content_rating, resolution, decade, year")
        names = {name for item in self.get_all(ignore_schedule_scope=True) for name in getattr(item, field, []) if isinstance(name, str) and name.strip()}
        return [SimpleNamespace(key=name, title=name) for name in sorted(names, key=lambda name: (name.casefold(), name))]

    def _country_names(self):
        names = getattr(getattr(self.config, "TMDb", None), "iso_3166_1", {})
        names = {str(code).upper(): name for code, name in names.items()} if isinstance(names, dict) else {}
        for code, name in {"SU": "Soviet Union", "CS": "Czechoslovakia", "XC": "Czechoslovakia", "YU": "Yugoslavia", "XK": "Kosovo"}.items():
            names.setdefault(code, name)
        return names

    def item_labels(self, item):
        self.require(Capability.GET_ITEM_LABELS)
        return []

    def find_poster_url(self, item):
        return getattr(item, "poster_url", None)

    def asset_directories(self, item):
        if isinstance(item, SiloCollection) and self.collection_asset_directory:
            return self.collection_asset_directory
        return self.asset_directory

    def asset_search_paths(self, item, item_dir=None, folder_name=None, asset_directory=None, folders_only=False):
        from modules.plex import Plex

        name = item if isinstance(item, str) else item.title
        return Plex.asset_search_paths(self, name, item_dir=item_dir, folder_name=folder_name, asset_directory=asset_directory, folders_only=folders_only)

    def find_item_assets(self, item, item_asset_directory=None, asset_directory=None, folder_name=None):
        # The filesystem resolver also accepts a title; it makes no Plex requests.
        from modules.plex import Plex

        directories = self.asset_directories(item) if asset_directory is None else asset_directory
        name = item if isinstance(item, str) else item.title
        return Plex.find_item_assets(self, name, item_asset_directory=item_asset_directory, asset_directory=directories, folder_name=folder_name)

    def item_posters(self, item, providers=None):
        if providers == []:
            return None
        poster = self.find_poster_url(item)
        if not poster:
            raise Failed("Silo Error: No poster found to restore")
        return poster

    def bulk_reload(self, items, force=False):
        for item in items:
            self.reload(item, force=force)

    def get_item_display_title(self, item, sort=False):
        return (item.data.get("sort_title") or item.title) if sort else util.item_title(item)

    def get_all(self, builder_level=None, load=False, ignore_schedule_scope=False):
        self.require(Capability.GET_ALL_ITEMS)
        if not builder_level and self._all_items and not load:
            return list(self._all_items)
        media_type = _media_type(self, builder_level)
        label = _load_label(self, builder_level)
        logger.info(f"Loading All {label} from Library: {self.name}")
        items = []
        total = None
        for page_items, page_total in self.client.catalog_pages(self.library_id, media_type=media_type):
            if isinstance(page_total, int):
                total = page_total
            for card in page_items:
                items.append(self._item_with_ids(card))
                overall = total if isinstance(total, int) and total >= len(items) else len(items)
                logger.ghost(f"Loaded: {len(items)}/{overall}")
            if page_items:
                overall = total if isinstance(total, int) and total >= len(items) else len(items)
                logger.exorcise()
                logger.info(f"Loaded: {len(items)}/{overall}")
        logger.info(f"Loaded {len(items)} {label}")
        if not builder_level:
            self._all_items = list(items)
        return items

    def get_items_added_since(self, builder_level, cutoff):
        self.require(Capability.SEARCH_ADDED)
        groups = [{"match": "all", "rules": [{"field": "added_at", "op": "gte", "value": cutoff.isoformat()}]}]
        cards = self.client.query(self.library_id, {"groups": groups})
        return [SiloItem(card, self) for card in cards]

    def cached_item_subitems(self, item, method_name):
        cache_key = (item.ratingKey, method_name)
        if cache_key not in self.filter_attr_cache:
            method = getattr(item, method_name, None)
            subitems = method() if callable(method) else []
            self.filter_attr_cache[cache_key] = list(subitems) if isinstance(subitems, Iterable) and not isinstance(subitems, (str, bytes)) else []
        return self.filter_attr_cache[cache_key]

    def get_ids(self, item):
        self.require(Capability.GET_PROVIDER_IDS)
        if not item.tmdb_id and not item.tvdb_id and not item.imdb_id:
            item.apply(self.client.get_item(item.content_id, library_id=self.library_id))
        if self.is_movie:
            return item.tmdb_id, None, item.imdb_id
        return None, item.tvdb_id, item.imdb_id

    def list_seasons(self, item):
        data, _headers = self.client.request("GET", f"/catalog/series/{_path_id(item.content_id)}/seasons")
        rows = data.get("items") if isinstance(data, dict) else data
        return [SiloItem(row, self) for row in rows or []]

    def list_episodes(self, item):
        season = item.data.get("season_number")
        if season is None:
            return []
        series_id = item.data.get("series_id") or item.content_id
        data, _headers = self.client.request("GET", f"/catalog/series/{_path_id(series_id)}/seasons/{season}/episodes")
        rows = data.get("items") if isinstance(data, dict) else data
        return [SiloItem(row, self) for row in rows or []]

    def map_guids(self, items):
        for item in items:
            key = item.ratingKey
            if self.is_movie and item.tmdb_id:
                self.movie_rating_key_map[key] = item.tmdb_id
                _remember(item.tmdb_id, key, self.movie_map)
            if self.is_show and item.tvdb_id:
                self.show_rating_key_map[key] = item.tvdb_id
                _remember(item.tvdb_id, key, self.show_map)
            if item.imdb_id:
                self.imdb_rating_key_map[key] = item.imdb_id
                _remember(item.imdb_id, key, self.imdb_map)
        self.plex_map_levels.update({self.type, self.type.lower()})
        logger.info("")
        logger.info(f"Processed {len(items)} {self.type}s")

    def search(self, title=None, sort=None, maxresults=None, libtype=None, **kwargs):
        if any(kwargs.get(name) for name in ("label", "labels")):
            self.require(Capability.GET_ITEM_LABELS)
        self.require(Capability.SEARCH_TITLE if title else Capability.SEARCH_FULL_TEXT)
        cards = self.client.browse(self.library_id, media_type=libtype or _media_type(self, None), query=title, limit=maxresults or 50)
        return [SiloItem(card, self) for card in cards]

    def fetch_item(self, item):
        cached = getattr(self, "_search_details", {}).get(getattr(item, "content_id", item))
        if cached is not None:
            return cached
        if isinstance(item, SiloItem):
            return self.reload(item)
        return self.reload(SiloItem({"content_id": item}, self))

    def get_all_collections(self, label=None):
        if label:
            return []
        return self._collections()

    def get_collection(self, data, force_search=False, debug=True):
        self.require(Capability.GET_COLLECTION_BY_NAME)
        if isinstance(data, SiloCollection):
            return data
        title = data if isinstance(data, str) else str(getattr(data, "title", data))
        matches = [collection for collection in self._collections() if str(collection.title).casefold() == title.casefold()]
        if not matches:
            if debug:
                logger.debug(f"Looking for: {data}")
            raise Failed(f"Silo Error: Collection {data} not found")
        if len(matches) > 1:
            logger.warning(f"Silo Warning: Multiple collections found with title '{title}', using the first exact match")
        return matches[0]

    def get_collection_items(self, collection, smart_label_collection):
        if smart_label_collection:
            self.require(Capability.GET_ITEM_LABELS)
        target = self._collection(collection)
        self.require(Capability.GET_COLLECTION_ITEMS)
        if target.smart and target.data.get("query_definition"):
            return [SiloItem(card, self) for card in self.client.preview(target.data.get("query_definition"))]
        return [SiloItem(member, self) for member in self.client.collection_items(target.id)]

    def get_collection_name_and_items(self, collection, smart_label_collection):
        if isinstance(collection, SiloCollection):
            return collection.title, self.get_collection_items(collection, smart_label_collection)
        # The builder passes a name when its initial lookup found no collection.
        # Plex creates manual collections implicitly when the first items are added.
        return str(collection), []

    def create_blank_collection(self, title):
        self.require(Capability.CREATE_COLLECTION)
        try:
            return self.get_collection(title, debug=False)
        except Failed:
            pass
        data, etag = self.client.create_collection({"title": title, "library_id": self.library_id, "collection_type": "manual"})
        return SiloCollection(data, etag=etag)

    def alter_collection(self, items, collection, smart_label_collection=False, add=True):
        if smart_label_collection:
            self.require(Capability.ADD_TAG if add else Capability.REMOVE_TAG)
        self.require(Capability.ADD_COLLECTION_ITEMS if add else Capability.REMOVE_COLLECTION_ITEMS)
        target = self.create_blank_collection(collection) if add and isinstance(collection, str) else self._collection(collection)
        items = list(items)
        for index, item in enumerate(items):
            content_id = item.content_id if isinstance(item, SiloItem) else getattr(item, "ratingKey", item)
            if add:
                logger.ghost(f"Adding ({index + 1}/{len(items)}) {getattr(item, 'title', content_id)} to collection: {target.title}")
                self.client.add_collection_item(target.id, content_id, position=index)
            else:
                logger.ghost(f"Removing ({index + 1}/{len(items)}) {getattr(item, 'title', content_id)} from collection: {target.title}")
                self.client.remove_collection_item(target.id, content_id)
        logger.exorcise()

    def delete_collection(self, obj, notify=True, delete_message=None):
        self.require(Capability.DELETE_COLLECTION)
        target = self._collection(obj)
        etag = target.etag
        if not etag:
            _data, etag = self.client.get_collection(target.id)
        self.client.delete_collection(target.id, etag or "*")
        self.stats["deleted"] += 1
        if notify:
            self.notify_delete(delete_message or f"Collection {target.title} deleted")
        return target

    def create_smart_collection(self, title, smart_type, uri_args, ignore_blank_results):
        self.require(Capability.NATIVE_SMART_COLLECTIONS)
        query = _query_document(uri_args)
        if not ignore_blank_results and not self.client.preview(query):
            raise Failed(f"Silo Error: No items for smart collection: {title}")
        try:
            return self.get_collection(title, debug=False)
        except Failed:
            pass
        data, etag = self.client.create_collection({"title": title, "library_id": self.library_id, "collection_type": "smart", "query_definition": query})
        return SiloCollection(data, etag=etag)

    def build_native_filter(self, definition, default_sort=None):
        """Translate native metadata and relative date filters without Plex URIs."""
        if not isinstance(definition, dict):
            raise Failed("Silo Error: smart_filter must be a mapping")
        if "groups" in definition:
            return None, "Silo native query", definition
        allowed = {"all", "any", "sort_by", "limit", "type", "validate"}
        if set(definition) - allowed or ("all" in definition and "any" in definition):
            raise Failed("Silo Error: smart_filter requires one all/any group; unsupported filter options")
        match = "any" if "any" in definition else "all"
        filters = definition.get(match)
        if not isinstance(filters, dict) or not filters:
            raise Failed("Silo Error: smart_filter requires a nonempty all/any group")
        groups = []
        fields = {"release": "release_date", "added": "added_at"}
        for name, value in filters.items():
            field, _, modifier = name.partition(".")
            if field in ("decade", "year"):
                operators = {"": "is", "is": "is", "not": "is_not", "isnot": "is_not"}
                if field == "year":
                    operators.update({op: op for op in ("gt", "gte", "lt", "lte")})
                if modifier not in operators:
                    raise BuilderValidationError(f"Silo Error: smart_filter {name} is unsupported")
                years = []
                for entry in value if isinstance(value, list) else [value]:
                    text = str(entry).strip()
                    if field == "decade":
                        text = text.removesuffix("s")
                    if isinstance(entry, bool) or not text.isascii() or not text.isdecimal() or not 1 <= int(text) <= 9999:
                        raise BuilderValidationError(f"Silo Error: smart_filter {name} requires valid years")
                    years.append(int(text) // 10 * 10 if field == "decade" else int(text))
                if not years:
                    raise BuilderValidationError(f"Silo Error: smart_filter {name} requires valid years")
                op = operators[modifier]
                groups.append({"match": "all" if op == "is_not" else "any", "rules": [{"field": field, "op": op, "value": year} for year in years]})
                continue
            if field in TAG_FIELDS or field in PERSON_FIELDS or field in ("audio_language", "subtitle_language", "content_rating", "resolution"):
                if modifier not in ("", "is", "not", "isnot"):
                    raise Failed(f"Silo Error: smart_filter {name} is unsupported")
                values = value if isinstance(value, list) else [value]
                if field in ("content_rating", "resolution"):
                    values = [str(v) if isinstance(v, int) and not isinstance(v, bool) else v for v in values]
                if not values or any(not isinstance(v, str) or not v.strip() for v in values):
                    raise Failed(f"Silo Error: smart_filter {name} requires nonempty tag names")
                if field in ("audio_language", "subtitle_language"):
                    values = [v.strip().lower() for v in values]
                elif field == "resolution":
                    values = [_resolution_value(v) for v in values]
                elif field == "country":
                    names = self._country_names()
                    aliases = {"united states": "US", "south korea": "KR", "north korea": "KP", "russia": "RU", "taiwan": "TW"}
                    expanded = []
                    for value in values:
                        expanded.append(value)
                        expanded.extend(code for code, country in names.items() if country.casefold() == value.casefold())
                        code = aliases.get(value.casefold())
                        if code:
                            expanded.append(code)
                        elif value.upper() in names:
                            expanded.append(names[value.upper()])
                    values = list(dict.fromkeys(expanded))
                negative = modifier in ("not", "isnot")
                groups.append({"match": "all" if negative else "any", "rules": [{"field": field, "op": "is_not" if negative else "is", "value": v} for v in values]})
                continue
            if name not in fields or isinstance(value, bool) or not str(value).isdigit() or int(value) <= 0:
                raise Failed(f"Silo Error: smart_filter {name} is unsupported; supported relative date filters are release and added with positive day counts")
            groups.append({"match": match, "rules": [{"field": fields[name], "op": "in_last", "value": f"{int(value)}d"}]})
        scope = definition.get("type") or _media_type(self, None)
        scope = {"movies": "movie", "shows": "series", "show": "series"}.get(scope, scope)
        if scope not in ("movie", "series"):
            raise Failed(f"Silo Error: smart_filter type {scope} is unsupported")
        sort = str(definition.get("sort_by") or "release.desc")
        field, _, order = sort.rpartition(".")
        sorts = {"release": "release_date", "added": "added_at", "title": "title", "year": "year", "critic_rating": "rating_rt_critic"}
        if field not in sorts or order not in ("asc", "desc"):
            raise Failed(f"Silo Error: smart_filter sort_by {sort} is unsupported")
        query = {"media_scope": scope, "library_ids": [str(self.library_id)], "match": match, "groups": groups, "sort": {"field": sorts[field], "order": order}}
        if definition.get("limit") is not None:
            limit = definition["limit"]
            if isinstance(limit, bool) or not str(limit).isdigit() or int(limit) <= 0:
                raise Failed("Silo Error: smart_filter limit must be a positive integer")
            query["limit"] = int(limit)
        return None, "Silo native query", _query_document(query)

    def smart_filter(self, collection):
        return self._collection(collection).data.get("query_definition")

    def update_smart_collection(self, collection, uri_args):
        self.require(Capability.UPDATE_SMART_FILTER)
        target = self._collection(collection)
        query = _query_document(uri_args)
        etag = target.etag
        if not etag:
            _data, etag = self.client.get_collection(target.id)
        data, new_etag = self.client.update_collection(target.id, {"query_definition": query}, etag or "*")
        target.data["query_definition"] = query
        if isinstance(data, dict):
            target.data.update(data)
        target.etag = new_etag or etag
        return target

    def create_playlist(self, name, items=None):
        self.require(Capability.CREATE_PLAYLIST)

    def get_playlist(self, title):
        self.require(Capability.GET_PLAYLIST)

    def smart_label_check(self, label):
        self.require(Capability.GET_ITEM_LABELS)
        return False

    def fetchItems(self, uri_args):
        if isinstance(uri_args, dict) and "silo_local_search" in uri_args:
            predicate = compile_selector(uri_args["silo_local_search"])
            return [item for item in self._local_search_items() if predicate(item)]
        status = self.require(Capability.PARSE_SMART_FILTER)
        if not isinstance(uri_args, (dict, list)):
            raise Failed(f"Silo Error: Plex smart filter URIs are not Silo query documents ({status.detail})")
        return [SiloItem(card, self) for card in self.client.query(self.library_id, uri_args)]

    def build_local_search(self, definition):
        compile_selector(definition)
        return None, "Silo local metadata search", {"silo_local_search": definition}

    def _local_search_items(self, builder_level=None, ignore_schedule_scope=False):
        if not hasattr(self, "_search_details"):
            self._search_details = {}
        for item in self.get_all(builder_level=builder_level, ignore_schedule_scope=ignore_schedule_scope):
            if item.content_id not in self._search_details:
                if "versions" not in item.data:
                    item.apply(self.client.get_item(item.content_id, library_id=self.library_id))
                self._search_details[item.content_id] = item
            yield self._search_details[item.content_id]

    def get_rating_keys(self, method, data, is_playlist=False):
        if method == "plex_search":
            items = self.fetchItems(data[2])
        elif method == "plex_all":
            if data not in ("movie", "show", "item"):
                raise BuilderValidationError(f"Silo Error: Local overlay selection for {data} is not supported")
            items = list(self._local_search_items())
        else:
            raise BuilderValidationError(f"Silo Error: Builder {method} is not supported")
        return [(item.ratingKey, "ratingKey") for item in items]

    def check_filters(self, item, filters_in, current_time):
        return all(compile_selector({key: value})(item) for key, value in filters_in)

    def query(self, method):
        return method()

    def query_data(self, method, data):
        return method(data)

    def get_playlist_from_users(self, playlist_title):
        self.require(Capability.GET_PLAYLIST)

    def create_smart_playlist(self, title, uri_args):
        self.require(Capability.CREATE_PLAYLIST)

    def update_smart_playlist(self, playlist, uri_args):
        self.require(Capability.CREATE_PLAYLIST)

    def split(self, text):
        from modules.plex import Plex

        return Plex.split(self, text)  # type: ignore[arg-type]  # split only reads library fields such as is_movie

    def _collections(self):
        self.require(Capability.GET_ALL_COLLECTIONS)
        collections = []
        for record in self.client.list_collections(self.library_id):
            if record.get("library_id") in (None, self.library_id) or self.library_id in (record.get("library_ids") or []):
                collections.append(SiloCollection(record))
        return collections

    def _collection(self, collection):
        if isinstance(collection, SiloCollection):
            return collection
        return self.get_collection(collection)

    def _item_with_ids(self, card):
        fields = ("tmdb_id", "tvdb_id", "imdb_id")
        cache = getattr(self.config, "Cache", None)
        content_id = card.get("content_id")
        cache_data = json.dumps([self.client.base, self.server.profile_id, self.library_id, content_id])
        expired = None
        if cache and content_id:
            list_key, expired = cache.query_list_cache("silo_item_ids", cache_data, cache.expiration)
            if list_key and expired is False and not any(card.get(field) for field in fields):
                ids = {field: value for value, field in cache.query_list_ids(list_key) if field in fields}
                if ids:
                    return SiloItem({**card, **ids}, self)
        if not any(card.get(field) for field in fields) and content_id:
            try:
                card = {**card, **(self.client.get_item(content_id, library_id=self.library_id) or {})}
            except Failed as error:
                logger.error(error)
        if cache and content_id and any(card.get(field) for field in fields):
            list_key = cache.update_list_cache("silo_item_ids", cache_data, True, cache.expiration)
            cache.delete_list_ids(list_key)
            cache.update_list_ids(list_key, [(str(card[field]), field) for field in fields if card.get(field)])
        return SiloItem(card, self)


class _SiloSection:
    """Attributes collection setup reads from ``library.Plex``."""

    def __init__(self, library_type, language, key, title):
        self.type = library_type
        self.TYPE = library_type
        self.language = language
        self.key = key
        self.title = title

    def __getattr__(self, name):
        raise Failed(f"Silo Error: Plex library attribute '{name}' is not available on a Silo library")


def _response_payload(response):
    try:
        return response.json()
    except ValueError:
        return None


def _response_detail(response):
    payload = _response_payload(response)
    if isinstance(payload, dict):
        detail = payload.get("detail") or payload.get("title")
        if detail:
            errors = []
            for error in payload.get("errors") or []:
                if isinstance(error, dict) and error.get("detail"):
                    errors.append(f"{error.get('location') or 'request'}: {error['detail']}")
            return str(detail).strip() + (f" ({'; '.join(errors)})" if errors else "")
    return (getattr(response, "text", None) or "").strip().replace("\n", " ")


def _profile_not_found(response):
    payload = _response_payload(response)
    if isinstance(payload, dict) and str(payload.get("detail") or "").casefold() == "profile not found":
        return True
    return "profile not found" in (getattr(response, "text", None) or "").casefold()


def _profile_label(profile, primary_ids=()):
    ident = profile.get("id")
    if ident is None:
        return ""
    label = f"profile {ident}"
    name = profile.get("name") or ""
    if name:
        label += f' "{name}"'
    if profile.get("is_primary") or str(ident) in primary_ids:
        label += " primary"
    return label


def _format_profiles(profiles, primary_ids=()):
    return ", ".join(label for label in (_profile_label(profile, primary_ids) for profile in profiles) if label)


def _primary_profile_ids(client):
    try:
        profiles = client._items("GET", "/profiles")
    except Failed:
        return set()
    return {str(profile.get("id")) for profile in profiles if profile.get("is_primary") and profile.get("id") is not None}


def _format_user_profiles(client, users):
    primary_ids = _primary_profile_ids(client)
    parts = []
    for user in users:
        user_id = user.get("id")
        if user_id is None:
            continue
        username = user.get("username") or ""
        try:
            profiles = client._items("GET", f"/admin/users/{_path_id(user_id)}/profiles")
        except Failed:
            profiles = []
        who = f"user {user_id}"
        if username:
            who += f" ({username})"
        parts.append(f"{who}: {_format_profiles(profiles, primary_ids) or 'no profiles'}")
    return "; ".join(parts)


def _format_account_profiles(client):
    account = {}
    try:
        data, _headers = client.request("GET", "/account/me")
        if isinstance(data, dict):
            account = data
    except Failed:
        account = {}
    try:
        profiles = client._items("GET", "/profiles")
    except Failed:
        profiles = []
    listed = _format_profiles(profiles)
    user_id = account.get("id")
    if user_id is None:
        return listed
    who = f"user {user_id}"
    username = account.get("username") or ""
    if username:
        who += f" ({username})"
    return f"{who}: {listed or 'no profiles'}"


def _path_id(value):
    return quote(str(value), safe="")


def _numeric_id(value):
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return value


def _remember(external_id, rating_key, dict_map):
    current = dict_map.get(external_id)
    if current is None:
        dict_map[external_id] = [rating_key]
    elif rating_key not in current:
        current.append(rating_key)


def _load_label(library, builder_level):
    level = str(builder_level or library.type or "item").lower()
    names = {"movie": "Movie", "show": "Show", "series": "Show", "episode": "Episode", "season": "Season"}
    return f"{names.get(level, level.capitalize())}s"


def _media_type(library, builder_level):
    if builder_level in ("movie", "show", "series", "episode", "season"):
        return {"show": "series"}.get(builder_level, builder_level)
    if library.is_movie:
        return "movie"
    if library.is_show:
        return "series"
    return None


def _query_groups(query_definition):
    if isinstance(query_definition, dict) and "groups" in query_definition:
        return query_definition["groups"]
    if isinstance(query_definition, list):
        return query_definition
    return []


def _query_document(uri_args):
    if isinstance(uri_args, dict):
        query = dict(uri_args)
        if isinstance(query.get("library_ids"), list):
            # Stored query documents retain numeric library IDs, unlike the
            # surrounding v2 API's opaque string IDs.
            query["library_ids"] = [int(value) if isinstance(value, str) and value.isascii() and value.isdecimal() else value for value in query["library_ids"]]
        return query
    status_detail = "Silo smart collections use a query document"
    raise Failed(f"Silo Error: {status_detail}")


# The matrix is defined below the class so the module can register the server at import.
def _silo_capabilities():
    declared = {capability: CapabilityStatusFull() for capability in Capability}
    details = {
        Capability.GET_COLLECTION_BY_NAME: ("partial", "By title filter"),
        Capability.SYNC_COLLECTION: ("partial", "Per item"),
        Capability.DELETE_COLLECTION: ("partial", "If-Match"),
        Capability.SMART_COLLECTION_WORKAROUND: ("none", "Not applicable. Silo creates native smart collections."),
        Capability.TEST_FILTER: ("full", "preview"),
        Capability.DELETE_ITEM: ("none", "No API"),
        Capability.SEARCH_ACTOR: ("full", "Rule actor"),
        Capability.SEARCH_GENRE: ("full", "Rule genre"),
        Capability.SEARCH_YEAR: ("full", "Rule year"),
        Capability.SEARCH_RATING: ("full", "Rules and profile stars"),
        Capability.SEARCH_ADDED: ("full", "Rule added_at"),
        Capability.VALIDATE_FILTER_SYNTAX: ("partial", "By execution"),
        Capability.SEARCH_CHOICES: ("full", "Facets"),
        Capability.PARSE_SMART_FILTER: ("partial", "Own query document"),
        Capability.BUILD_FILTER: ("full", "{field,op,value}"),
        Capability.VALIDATE_FILTER_LOGIC: ("full", "Preview and query"),
        Capability.ADD_TAG: ("none", "No tag field"),
        Capability.REMOVE_TAG: ("none", "No tag field"),
        Capability.SYNC_TAGS: ("partial", "Genre, studio, network, and country"),
        Capability.GET_ITEM_LABELS: ("none", "No labels"),
        Capability.LOCK_TAG: ("full", "locked_fields"),
        Capability.SET_USER_RATING: ("partial", "Profile stars, 1-5"),
        Capability.UPLOAD_POSTER: ("partial", "URL; local files go to transfer.kometa.wiki"),
        Capability.UPLOAD_BACKDROP: ("partial", "URL; local files go to transfer.kometa.wiki"),
        Capability.UPLOAD_LOGO: ("partial", "URL; local files go to transfer.kometa.wiki"),
        Capability.UPLOAD_BANNER: ("partial", "Apply an existing image"),
        Capability.UPLOAD_OVERLAY: ("partial", "Poster URL via transfer.kometa.wiki"),
        Capability.FIND_POSTER_ASSET: ("partial", "Container path"),
        Capability.FIND_BACKDROP_ASSET: ("partial", "Container path"),
        Capability.FIND_LOGO_ASSET: ("partial", "Container path"),
        Capability.VALIDATE_ASSET: ("full", "Local check"),
        Capability.UPLOAD_THEME_SONG: ("none", "No upload"),
        Capability.UPLOAD_THEME_VIDEO: ("none", "No upload"),
        Capability.BATCH_TAGS: ("none", "No tag field"),
        Capability.BATCH_RATINGS: ("partial", "Per item"),
        Capability.BATCH_METADATA: ("partial", "Query then PATCH"),
        Capability.BUILDER_REPLACE_ITEMS: ("partial", "Diff, no bulk replace"),
        Capability.CREATE_PLAYLIST: ("none", "No API"),
        Capability.GET_PLAYLIST: ("none", "No API"),
        Capability.ADD_PLAYLIST_ITEMS: ("none", "No API"),
        Capability.REMOVE_PLAYLIST_ITEMS: ("none", "No API"),
        Capability.DELETE_PLAYLIST: ("none", "No API"),
        Capability.PARSE_RELATIVE_DATE: ("full", "in_last"),
        Capability.GET_RATING_KEY: ("full", "content_id"),
        Capability.GET_ACTOR_ID: ("full", "People API"),
        Capability.GET_PROVIDER_IDS: ("full", "imdb, tmdb, and tvdb"),
        Capability.SEND_NOTIFICATION: ("full", "Kometa"),
        Capability.NOTIFY_DELETION: ("full", "Kometa"),
    }
    from modules.media_server import CapabilityStatus, Support

    support_by_name = {"full": Support.FULL, "partial": Support.PARTIAL, "none": Support.NONE}
    for capability, (level, detail) in details.items():
        declared[capability] = CapabilityStatus(support_by_name[level], detail)
    return CapabilityMatrix(declared)


def CapabilityStatusFull():
    from modules.media_server import CapabilityStatus, Support

    return CapabilityStatus(Support.FULL)


SILO_CAPABILITIES = _silo_capabilities()
register_media_server(SiloMediaServer)
