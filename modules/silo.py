"""Silo media server client and library.

Silo is a media server peer of Plex. Kometa talks to its native ``/api/v2`` API.
Collection membership is addressed with the catalog content id. Poster, backdrop,
logo, and overlay images are applied from a URL. A local file is published to
transfer.kometa.wiki first. Labels, item deletion, and playlists are refused
through the capability matrix.
"""

import os
import re
import uuid
from collections.abc import Iterable
from urllib.parse import quote

import requests

from modules import util
from modules.library import Library
from modules.media_server import Capability, CapabilityMatrix, MediaServer, register_media_server
from modules.util import Failed

logger = util.logger

LIBRARY_TYPES = {"movies": "Movie", "series": "Show"}
TAG_FIELDS = {"genre": "genres", "studio": "studios", "network": "networks", "country": "countries"}
TRANSFER_BASE = "https://transfer.kometa.wiki"
TRANSFER_MAX_DAYS = "7"
IMAGE_EXTENSIONS = {".jpg", ".png", ".webp"}
ARTWORK_KINDS = {"poster": "poster", "background": "backdrop", "backdrop": "backdrop", "logo": "logo"}
IMAGE_SOURCES = {"tmdb": "TMDb", "tvdb": "TVDb", "trakt": "Trakt", "ytmusic": "YouTube Music"}


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

    def request(self, method, path, params=None, json_body=None, headers=None, files=None):
        try:
            response = self.session.request(method, f"{self.base}/{path.lstrip('/')}", params=params, json=json_body, files=files, headers=headers, timeout=self.server.timeout)
        except requests.RequestException as error:
            raise Failed(f"Silo Error: {method} {path} failed: {error}") from error
        if response.status_code >= 400:
            detail = (response.text or "").strip().replace("\n", " ")[:300]
            raise Failed(f"Silo Error: {method} {path} returned {response.status_code}{f': {detail}' if detail else ''}")
        if response.status_code == 204 or not response.content:
            return None, response.headers
        try:
            return response.json(), response.headers
        except ValueError as error:
            raise Failed(f"Silo Error: {method} {path} did not return JSON") from error

    def _items(self, method, path, params=None, json_body=None):
        items = []
        query = dict(params or {})
        body = dict(json_body or {})
        while True:
            if method == "GET":
                data, _headers = self.request("GET", path, params=query)
            else:
                data, _headers = self.request(method, path, params=query, json_body=body)
            if isinstance(data, list):
                return data
            page_items = (data or {}).get("items") or []
            items.extend(page_items)
            page = (data or {}).get("page") or {}
            cursor = page.get("next_cursor")
            if not page.get("has_more") or not cursor:
                return items
            if method == "GET":
                query["cursor"] = cursor
            else:
                body["cursor"] = cursor

    def list_libraries(self):
        return self._items("GET", "/libraries")

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
        params = {"source": "query", "library_id": library_id, "limit": min(limit or 200, 200)}
        if media_type:
            params["type"] = media_type
        if query:
            params["q"] = query
        return self._items("GET", "/catalog", params=params)

    def query(self, library_id, query_definition, limit=100):
        body = {"library_id": library_id, "limit": min(limit or 100, 100), "groups": _query_groups(query_definition)}
        return self._items("POST", "/catalog/query", json_body=body)

    def preview(self, query_definition, limit=20):
        data, _headers = self.request("POST", "/admin/collections/preview", json_body={"query_definition": query_definition, "limit": limit})
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
        self.request("POST", f"/admin/items/{_path_id(content_id)}/refresh-metadata")

    def apply_item_image(self, content_id, kind, source_url):
        self.request("POST", f"/admin/items/{_path_id(content_id)}/images/apply", json_body={"type": kind, "original_url": source_url})

    def set_collection_artwork(self, collection_id, kind, source_url):
        self.request("PUT", f"/admin/collections/{_path_id(collection_id)}/{kind}", files={"source_url": (None, source_url)})


class SiloCollection:
    def __init__(self, data, etag=None):
        self.data = dict(data or {})
        self.id = self.data.get("id")
        self.ratingKey = self.id
        self.title = self.data.get("title") or self.data.get("name") or ""
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
        self.type = self.data.get("type")
        self.guid = f"silo://{self.content_id}"
        self.summary = self.data.get("overview") or self.data.get("description") or ""
        self.poster_url = self.data.get("poster_url")
        self.tmdb_id = _numeric_id(self.data.get("tmdb_id"))
        self.tvdb_id = _numeric_id(self.data.get("tvdb_id"))
        self.imdb_id = self.data.get("imdb_id") or None
        self.genres = list(self.data.get("genres") or [])
        self.studios = list(self.data.get("studios") or [])
        self.networks = list(self.data.get("networks") or [])
        self.countries = list(self.data.get("countries") or [])

    def seasons(self):
        return self.library.list_seasons(self)

    def episodes(self):
        return self.library.list_episodes(self)


class Silo(Library):
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
        logger.info(f"Connected to Silo server {server.display_name}")
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
        return publish_image(location, filename=_transfer_filename(location, kind), timeout=self.timeout)

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
        self.require(Capability.RELOAD_ITEM_FORCE if force else Capability.RELOAD_ITEM)
        if force:
            self.client.refresh_metadata(item.content_id)
        item.apply(self.client.get_item(item.content_id, library_id=self.library_id))
        return item

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

    def item_labels(self, item):
        self.require(Capability.GET_ITEM_LABELS)
        return []

    def find_poster_url(self, item):
        return getattr(item, "poster_url", None)

    def item_posters(self, item, providers=None):
        poster = self.find_poster_url(item)
        return [poster] if poster else []

    def get_all(self, builder_level=None, load=False, ignore_schedule_scope=False):
        self.require(Capability.GET_ALL_ITEMS)
        if not builder_level and self._all_items and not load:
            return list(self._all_items)
        media_type = _media_type(self, builder_level)
        cards = self.client.browse(self.library_id, media_type=media_type)
        items = [self._item_with_ids(card) for card in cards]
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
        if isinstance(item, SiloItem):
            return self.reload(item)
        return self.reload(SiloItem({"content_id": item}, self))

    def get_collection(self, data, force_search=False, debug=True):
        self.require(Capability.GET_COLLECTION_BY_NAME)
        if isinstance(data, SiloCollection):
            return data
        title = str(getattr(data, "title", data))
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
        target = collection if isinstance(collection, SiloCollection) else self._collection(collection)
        name = target.title if isinstance(target, SiloCollection) else str(collection)
        return name, self.get_collection_items(target, smart_label_collection)

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
        target = self._collection(collection)
        for index, item in enumerate(items):
            content_id = item.content_id if isinstance(item, SiloItem) else getattr(item, "ratingKey", item)
            if add:
                logger.ghost(f"Adding {getattr(item, 'title', content_id)} to collection: {target.title}")
                self.client.add_collection_item(target.id, content_id, position=index)
            else:
                logger.ghost(f"Removing {getattr(item, 'title', content_id)} from collection: {target.title}")
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

    def update_smart_collection(self, collection, uri_args):
        self.require(Capability.UPDATE_SMART_FILTER)
        target = self._collection(collection)
        query = _query_document(uri_args)
        etag = target.etag
        if not etag:
            _data, etag = self.client.get_collection(target.id)
        data, new_etag = self.client.update_collection(target.id, {"query_definition": query}, etag or "*")
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
        status = self.require(Capability.PARSE_SMART_FILTER)
        if not isinstance(uri_args, (dict, list)):
            raise Failed(f"Silo Error: Plex smart filter URIs are not Silo query documents ({status.detail})")
        return [SiloItem(card, self) for card in self.client.query(self.library_id, uri_args)]

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
        return self.get_collection(getattr(collection, "title", collection))

    def _item_with_ids(self, card):
        if not any(card.get(field) for field in ("tmdb_id", "tvdb_id", "imdb_id")) and card.get("content_id"):
            try:
                card = {**card, **(self.client.get_item(card["content_id"], library_id=self.library_id) or {})}
            except Failed as error:
                logger.error(error)
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
        return uri_args
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
