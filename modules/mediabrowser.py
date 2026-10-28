"""Jellyfin and Emby media servers.

Both speak the MediaBrowser API. A library selects one with ``server`` on a
``media_servers`` entry of ``type: jellyfin`` or ``type: emby``. Collections are
boxsets. Posters, backdrops, logos, banners, and overlays upload as image bytes,
or the server downloads a URL. Plex smart-filter addresses are not accepted.
"""

import base64
import os
import time
import unicodedata
from collections.abc import Iterable
from datetime import datetime, timezone
from types import SimpleNamespace
from urllib.parse import quote

import requests

from modules import util
from modules.local_search import compile_selector
from modules.library import Library
from modules.media_server import Capability, CapabilityMatrix, MediaServer, log_server_connection, register_media_server
from modules.util import Failed

logger = util.logger

LIBRARY_TYPES = {"movies": "Movie", "movie": "Movie", "tvshows": "Show", "tv": "Show"}
ITEM_TYPES = {"Movie": "movie", "Series": "show", "Season": "season", "Episode": "episode", "BoxSet": "collection", "Playlist": "playlist"}
ITEM_FIELDS = "ProviderIds,Genres,Studios,ProductionLocations,People,Overview,Tags,DateCreated,ProductionYear,PremiereDate,CommunityRating,CriticRating,OfficialRating,ChildCount,RecursiveItemCount,SortName,ImageTags,LockedFields,Path"
PAGE_SIZE = 200
COLLECTION_BATCH_SIZE = 100
LOCAL_COLLECTION_SORTS = {"title": "SortName", "release": "PremiereDate", "added": "DateCreated", "year": "ProductionYear", "audience_rating": "CommunityRating", "critic_rating": "CriticRating"}
IMAGE_TYPES = {"poster": "Primary", "background": "Backdrop", "backdrop": "Backdrop", "logo": "Logo", "banner": "Banner", "square_art": "Thumb"}
CONTENT_TYPES = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp", ".gif": "image/gif"}
TAG_FIELDS = {"genre": "Genres", "studio": "Studios", "label": "Tags", "labels": "Tags"}
LOCK_FIELDS = {"Genres": "Genres", "Studios": "Studios", "Tags": "Tags", "Name": "Name", "Overview": "Overview", "OfficialRating": "OfficialRating"}


def _browser_capabilities():
    declared = {capability: _status("full") for capability in Capability}
    details = {
        Capability.GET_COLLECTION_BY_NAME: ("partial", "First title match"),
        Capability.SYNC_COLLECTION: ("partial", "Per item"),
        Capability.NATIVE_SMART_COLLECTIONS: ("none", "No dynamic collection filter"),
        Capability.SMART_COLLECTION_WORKAROUND: ("partial", "Manual boxset rebuilt by builders"),
        Capability.UPDATE_SMART_FILTER: ("none", "No dynamic filter"),
        Capability.TEST_FILTER: ("partial", "Item query"),
        Capability.GET_ALL_ITEMS_NATIVE: ("partial", "MediaBrowser DTO"),
        Capability.SEARCH_RATING: ("partial", "Minimum community or critic rating"),
        Capability.SEARCH_ADDED: ("partial", "DateCreated, newest first"),
        Capability.VALIDATE_FILTER_SYNTAX: ("partial", "By execution"),
        Capability.SEARCH_CHOICES: ("partial", "Genres, studios, and tags"),
        Capability.PARSE_SMART_FILTER: ("none", "Plex smart filter URIs are not accepted"),
        Capability.BUILD_FILTER: ("none", "No Plex filter language"),
        Capability.VALIDATE_FILTER_LOGIC: ("partial", "By execution"),
        Capability.SYNC_TAGS: ("partial", "Tags, genres, and studios"),
        Capability.LOCK_TAG: ("partial", "LockedFields"),
        Capability.SET_USER_RATING: ("full", "UserData rating, 0-10"),
        Capability.SET_CRITIC_RATING: ("partial", "CriticRating field"),
        Capability.UPLOAD_POSTER: ("full", "Primary image bytes or remote URL"),
        Capability.UPLOAD_BACKDROP: ("full", "Backdrop image bytes or remote URL"),
        Capability.UPLOAD_LOGO: ("full", "Logo image bytes or remote URL"),
        Capability.UPLOAD_BANNER: ("full", "Banner and thumb"),
        Capability.UPLOAD_OVERLAY: ("full", "Primary image bytes"),
        Capability.FIND_POSTER_ASSET: ("partial", "Local asset directory"),
        Capability.FIND_BACKDROP_ASSET: ("partial", "Local asset directory"),
        Capability.FIND_LOGO_ASSET: ("partial", "Local asset directory"),
        Capability.VALIDATE_ASSET: ("full", "Local check"),
        Capability.UPLOAD_THEME_SONG: ("none", "No upload endpoint"),
        Capability.UPLOAD_THEME_VIDEO: ("none", "No upload endpoint"),
        Capability.BATCH_TAGS: ("partial", "Per item"),
        Capability.BATCH_RATINGS: ("partial", "Per item"),
        Capability.BATCH_METADATA: ("partial", "Per item"),
        Capability.BUILDER_REPLACE_ITEMS: ("partial", "Diff, no bulk replace"),
        Capability.GET_ACTOR_ID: ("partial", "Person search"),
    }
    for capability, (level, detail) in details.items():
        declared[capability] = _status(level, detail)
    return CapabilityMatrix(declared)


def _status(level, detail=""):
    from modules.media_server import CapabilityStatus, Support

    return CapabilityStatus({"full": Support.FULL, "partial": Support.PARTIAL, "none": Support.NONE}[level], detail)


JELLYFIN_CAPABILITIES = _browser_capabilities()
EMBY_CAPABILITIES = _browser_capabilities()


class JellyfinMediaServer(MediaServer):
    type_name = "jellyfin"
    type_label = "Jellyfin"

    def __init__(self, url, token, timeout=60, verify_ssl=None, db_cache=None, name=None, user_id=None):
        super().__init__(url=url, token=token, timeout=timeout, verify_ssl=verify_ssl, db_cache=db_cache, name=name)
        self.user_id = str(user_id).strip() if user_id else None

    @property
    def capabilities(self) -> CapabilityMatrix:
        return JELLYFIN_CAPABILITIES

    @classmethod
    def from_config(cls, server_config, name=None, user_id=None):
        timeout = server_config["timeout"] if server_config.get("timeout") is not None else 60
        return cls(
            url=server_config["url"],
            token=server_config["token"],
            timeout=timeout,
            verify_ssl=server_config.get("verify_ssl"),
            name=name,
            user_id=user_id if user_id is not None else server_config.get("user"),
        )


class EmbyMediaServer(JellyfinMediaServer):
    type_name = "emby"
    type_label = "Emby"

    @property
    def capabilities(self) -> CapabilityMatrix:
        return EMBY_CAPABILITIES


class MediaBrowserClient:
    """HTTP client for one Jellyfin or Emby server. The token is an API key."""

    def __init__(self, server, session=None):
        self.server = server
        self.base = str(server.url).rstrip("/")
        self.user_id = server.user_id
        self.session = session or requests.Session()
        self.session.headers["X-Emby-Token"] = server.token
        self.session.headers["Accept"] = "application/json"
        if server.verify_ssl is False:
            self.session.verify = False

    def request(self, method, path, params=None, json_body=None, data=None, headers=None, retry_safe=False, recover=None):
        method = method.upper()
        parts = path.strip("/").split("/")
        item_write = len(parts) == 2 and parts[0] == "Items" and method in ("POST", "DELETE")
        membership_write = len(parts) == 3 and parts[0] == "Collections" and parts[2] == "Items" and method in ("POST", "DELETE")
        retry_safe = retry_safe or method in ("GET", "HEAD") or item_write or membership_write or recover is not None
        connection_failed = False
        for attempt in range(3):
            try:
                response = self.session.request(method, f"{self.base}/{path.lstrip('/')}", params=params, json=json_body, data=data, headers=headers, timeout=self.server.timeout)
                break
            except requests.RequestException as error:
                transient = isinstance(error, (requests.ConnectionError, requests.Timeout)) and not isinstance(error, requests.exceptions.SSLError)
                if not retry_safe or not transient or attempt == 2:
                    raise Failed(f"{self.server.type_label} Error: {method} {path} failed: {error}") from error
                delay = 2**attempt
                logger.warning(f"{self.server.type_label} Warning: {method} {path} connection failed; retrying in {delay} seconds ({attempt + 1}/2)")
                time.sleep(delay)
                connection_failed = True
                if recover is not None:
                    recovered = recover()
                    if recovered is not None:
                        return recovered
        if connection_failed and method == "DELETE" and item_write and response.status_code == 404:
            return None
        if response.status_code >= 400:
            detail = (getattr(response, "text", "") or "").strip().replace("\n", " ")[:300]
            raise Failed(f"{self.server.type_label} Error: {method} {path} returned {response.status_code}{f': {detail}' if detail else ''}")
        if response.status_code == 204 or not response.content:
            return None
        if response.content[:1] in (b"{", b"["):
            try:
                return response.json()
            except ValueError as error:
                raise Failed(f"{self.server.type_label} Error: {method} {path} did not return JSON") from error
        return None

    def ensure_user(self):
        if self.user_id:
            return self.user_id
        users = self.request("GET", "/Users") or []
        admins = [user for user in users if (user.get("Policy") or {}).get("IsAdministrator")]
        chosen = (admins or users or [None])[0]
        if not chosen or not chosen.get("Id"):
            raise Failed(f"{self.server.type_label} Error: No user found. Set user under media_servers")
        self.user_id = chosen["Id"]
        self.server.user_id = self.user_id
        return self.user_id

    def virtual_folders(self):
        return self.request("GET", "/Library/VirtualFolders") or []

    def server_info(self):
        data = self.request("GET", "/System/Info") or {}
        os_name = data.get("OperatingSystemDisplayName") or data.get("OperatingSystem")
        if os_name in ("Unix", "Linux", "Windows"):
            os_name = data.get("OperatingSystem") or os_name
        return {"name": data.get("ServerName"), "version": data.get("Version"), "os": os_name, "os_version": data.get("OperatingSystemVersion")}

    def items(self, params, limit=None, one_page=False):
        self.ensure_user()
        query = {"userId": self.user_id, "fields": ITEM_FIELDS, "recursive": "true"}
        query.update({key: value for key, value in (params or {}).items() if value is not None})
        page_size = int(limit or query.get("limit") or 200)
        start = int(query.get("startIndex") or 0)
        query.pop("limit", None)
        query.pop("startIndex", None)
        rows = []
        while True:
            query["startIndex"] = start
            query["limit"] = page_size
            data = self.request("GET", "/Items", params=dict(query)) or {}
            batch = data.get("Items") or []
            if one_page:
                return batch
            rows.extend(batch)
            total = data.get("TotalRecordCount", start + len(batch))
            start += len(batch)
            if not batch or start >= total or (limit and len(rows) >= limit):
                return rows[:limit] if limit else rows

    def get_item(self, item_id):
        if self.server.type_name == "emby":
            user_id = self.ensure_user()
            return self.request("GET", f"/Users/{_path_id(user_id)}/Items/{_path_id(item_id)}") or {}
        params = {"userId": self.user_id} if self.user_id else None
        return self.request("GET", f"/Items/{_path_id(item_id)}", params=params) or {}

    def update_item(self, item_id, fields):
        current = self.get_item(item_id)
        current.update(fields)
        current["Id"] = str(item_id)
        self.request("POST", f"/Items/{_path_id(item_id)}", json_body=current)
        return current

    def update_user_data(self, item_id, fields):
        self.ensure_user()
        self.request("POST", f"/UserItems/{_path_id(item_id)}/UserData", params={"userId": self.user_id}, json_body=fields)

    def refresh_item(self, item_id):
        self.request("POST", f"/Items/{_path_id(item_id)}/Refresh", params={"metadataRefreshMode": "FullRefresh", "imageRefreshMode": "FullRefresh"})

    def delete_item(self, item_id):
        self.request("DELETE", f"/Items/{_path_id(item_id)}")

    def create_collection(self, name, item_ids=None, parent_id=None):
        ids = list(item_ids or [])
        params = {"name": name}
        if self.server.type_name == "jellyfin":
            params["isLocked"] = "true"
        if parent_id:
            params["parentId"] = parent_id
        if ids:
            params["ids"] = ",".join(str(item_id) for item_id in ids[:COLLECTION_BATCH_SIZE])

        def recover():
            matches = [row for row in self.items({"includeItemTypes": "BoxSet", "searchTerm": name}) if str(row.get("Name", "")).casefold() == name.casefold() and row.get("Id")]
            if len(matches) > 1:
                raise Failed(f"{self.server.type_label} Error: Collection creation response was lost and multiple collections match '{name}'; cannot safely recover")
            if matches:
                logger.warning(f"{self.server.type_label} Warning: Recovered collection '{name}' after a lost creation response")
                return {"Id": matches[0]["Id"]}
            return None

        created = self.request("POST", "/Collections", params=params, recover=recover) or {}
        if len(ids) > COLLECTION_BATCH_SIZE:
            if not created.get("Id"):
                raise Failed(f"{self.server.type_label} Error: Collection creation returned no ID for remaining members")
            self.add_collection_items(created["Id"], ids[COLLECTION_BATCH_SIZE:])
        return created

    def add_collection_items(self, collection_id, item_ids):
        self._change_collection_items("POST", collection_id, item_ids)

    def remove_collection_items(self, collection_id, item_ids):
        self._change_collection_items("DELETE", collection_id, item_ids)

    def _change_collection_items(self, method, collection_id, item_ids):
        ids = list(item_ids)
        for start in range(0, len(ids), COLLECTION_BATCH_SIZE):
            self.request(method, f"/Collections/{_path_id(collection_id)}/Items", params={"ids": ",".join(str(item_id) for item_id in ids[start : start + COLLECTION_BATCH_SIZE])})

    def create_playlist(self, name, item_ids=None):
        self.ensure_user()
        params = {"name": name, "userId": self.user_id}
        if item_ids:
            params["ids"] = ",".join(str(item_id) for item_id in item_ids)
        return self.request("POST", "/Playlists", params=params) or {}

    def add_playlist_items(self, playlist_id, item_ids):
        self.ensure_user()
        self.request("POST", f"/Playlists/{_path_id(playlist_id)}/Items", params={"ids": ",".join(str(item_id) for item_id in item_ids), "userId": self.user_id})

    def playlist_entries(self, playlist_id):
        self.ensure_user()
        data = self.request("GET", f"/Playlists/{_path_id(playlist_id)}/Items", params={"userId": self.user_id, "fields": ITEM_FIELDS}) or {}
        return data.get("Items") or []

    def remove_playlist_entries(self, playlist_id, entry_ids):
        self.request("DELETE", f"/Playlists/{_path_id(playlist_id)}/Items", params={"entryIds": ",".join(str(entry_id) for entry_id in entry_ids)})

    def upload_image(self, item_id, image_type, content, content_type):
        # Both servers decode the request body from base64 before reading the image.
        self.request("POST", f"/Items/{_path_id(item_id)}/Images/{image_type}", data=base64.b64encode(content), headers={"Content-Type": content_type})

    def download_remote_image(self, item_id, image_type, image_url):
        self.request("POST", f"/Items/{_path_id(item_id)}/RemoteImages/Download", params={"type": image_type, "imageUrl": image_url})


class _Tag:
    def __init__(self, tag):
        self.tag = tag


class MediaBrowserItem:
    def __init__(self, data, library):
        self.library = library
        self.data = {}
        self.apply(data or {})

    def apply(self, data):
        if data:
            self.data.update(data)
        self.ratingKey = self.data.get("Id")
        self.key = self.ratingKey
        self.title = self.data.get("Name") or ""
        self.year = self.data.get("ProductionYear")
        raw_type = str(self.data.get("Type") or "")
        self.type = ITEM_TYPES.get(raw_type, raw_type.lower())
        self.guid = f"{self.library.server.type_name}://{self.ratingKey}"
        self.summary = self.data.get("Overview") or ""
        self.titleSort = self.data.get("ForcedSortName") or self.data.get("SortName") or self.title
        self.contentRating = self.data.get("OfficialRating")
        self.userRating = (self.data.get("UserData") or {}).get("Rating")
        self.audienceRating = self.data.get("CommunityRating")
        self.rating = self.data.get("CriticRating")
        providers = self.data.get("ProviderIds") or {}
        self.tmdb_id = _numeric_id(_provider(providers, "Tmdb", "TMDb", "tmdb"))
        self.tvdb_id = _numeric_id(_provider(providers, "Tvdb", "TVDb", "tvdb"))
        self.imdb_id = _provider(providers, "Imdb", "IMDb", "imdb")
        self.genres = list(self.data.get("Genres") or [])
        self.studios = [studio.get("Name") for studio in (self.data.get("Studios") or []) if isinstance(studio, dict) and studio.get("Name")]
        self.tags = list(self.data.get("Tags") or [tag.get("Name") if isinstance(tag, dict) else tag for tag in self.data.get("TagItems") or []])
        for role, types in {"actors": {"actor", "gueststar"}, "directors": {"director"}, "writers": {"writer"}, "producers": {"producer", "executiveproducer"}}.items():
            people = []
            seen = set()
            for person in self.data.get("People") or []:
                if not isinstance(person, dict) or str(person.get("Type") or "").replace(" ", "").casefold() not in types:
                    continue
                name = str(person.get("Name") or "").strip()
                if name and name.casefold() not in seen:
                    seen.add(name.casefold())
                    people.append(SimpleNamespace(id=person.get("Id") or f"name:{name.casefold()}", tag=name))
            setattr(self, role, people)
        self.childCount = self.data.get("ChildCount") or self.data.get("RecursiveItemCount") or 0
        self.smart = False
        self.collectionMode = -1
        self.collectionSort = {"PremiereDate": 0, "SortName": 1}.get(self.data.get("DisplayOrder"), -1)
        self.locations = []
        self.posterUrl = self.library.find_poster_url(self)
        self.thumb = self.posterUrl

    def seasons(self):
        return self.library.list_children(self, "Season")

    def episodes(self):
        return self.library.list_children(self, "Episode")

    def editSummary(self, summary):
        self.library.client.update_item(self.ratingKey, {"Overview": summary})
        self.summary = summary

    def editSortTitle(self, sort_title):
        fields = {"ForcedSortName": sort_title}
        if self.library.server.type_name == "emby":
            # Emby's editor writes both; retaining an empty/stale forced value
            # can otherwise override the new SortName during the update.
            fields["SortName"] = sort_title
            fields["LockedFields"] = list(dict.fromkeys([*(self.data.get("LockedFields") or []), "SortName"]))
        self.data.update(self.library.client.update_item(self.ratingKey, fields))
        self.titleSort = sort_title
        if self.library.server.type_name == "emby":
            stored = self.library.client.get_item(self.ratingKey)
            actual = stored.get("ForcedSortName") or stored.get("SortName")
            self.apply(stored)

            def sort_key(value):
                return "".join(character for character in unicodedata.normalize("NFD", value) if not unicodedata.combining(character)).casefold()

            if not isinstance(actual, str) or sort_key(actual) != sort_key(sort_title):
                raise Failed(f"Emby Error: Sort title for '{self.title}' was not retained: requested '{sort_title}', server returned '{actual}'")

    def editContentRating(self, rating):
        self.library.client.update_item(self.ratingKey, {"OfficialRating": rating})
        self.contentRating = rating

    def editTitle(self, title):
        self.library.client.update_item(self.ratingKey, {"Name": title})
        self.title = title


class MediaBrowserCollection(MediaBrowserItem):
    pass


class MediaBrowserPlaylist(MediaBrowserItem):
    def addItems(self, items):
        self.library.require(Capability.ADD_PLAYLIST_ITEMS)
        self.library.client.add_playlist_items(self.ratingKey, [_item_id(item) for item in items])

    def removeItems(self, items):
        self.library.require(Capability.REMOVE_PLAYLIST_ITEMS)
        wanted = {_item_id(item) for item in items}
        entry_ids = []
        for entry in self.library.client.playlist_entries(self.ratingKey):
            if entry.get("Id") in wanted or entry.get("PlaylistItemId") in wanted:
                entry_ids.append(entry.get("PlaylistItemId") or entry.get("Id"))
        if entry_ids:
            self.library.client.remove_playlist_entries(self.ratingKey, entry_ids)


class MediaBrowser(Library):
    server_class = JellyfinMediaServer
    overlay_backup_fallback = True

    def __init__(self, config, params, client=None):
        super().__init__(config, params)
        server = self.server
        if not isinstance(server, self.server_class):
            raise Failed(f"{self.server_class.type_label} Error: Library is not connected to a {self.server_class.type_label} server")
        self.url = server.url
        self.token = server.token
        self.timeout = server.timeout
        logger.secret(self.url)
        logger.secret(self.token)
        self.client = client or MediaBrowserClient(server)
        self.session = self.client.session
        self.client.ensure_user()
        record = select_library(self.client.virtual_folders(), params["name"], server.type_label)
        self.library_record = record
        self.library_id = record.get("ItemId")
        self.type = kometa_library_type(record.get("CollectionType"), server.type_label)
        self.is_movie = self.type == "Movie"
        self.is_show = self.type == "Show"
        self.is_music = False
        self.is_other = False
        self.Plex = _BrowserSection(self.type.lower(), "en", self.library_id, record.get("Name"), server.type_label)
        self.agent = server.type_name
        self.scanner = server.type_name
        self._all_items = []
        self.users = []
        log_server_connection(logger, server, self.client.server_info)
        logger.info(f"Connected to library {params['name']}")
        logger.info(f"Type: {self.type}")

    def _server(self) -> JellyfinMediaServer:
        server = self.server
        if not isinstance(server, JellyfinMediaServer):
            raise Failed(f"{self.server_class.type_label} Error: Library is not connected to a {self.server_class.type_label} server")
        return server

    def notify(self, text, collection=None, critical=True):
        self.config.notify(text, server=self._server().display_name, library=self.name, collection=collection, critical=critical)

    def notify_delete(self, message, playlist=False):
        self.config.notify_delete(message, server=self._server().display_name, library=self.name)

    def _image_type(self, image_type, poster=True):
        if image_type in IMAGE_TYPES:
            return IMAGE_TYPES[image_type]
        if poster and image_type in (None, "poster"):
            return "Primary"
        raise Failed(f"{self._server().type_label} Error: Image type {image_type or 'banner'} is not supported")

    def _apply_image(self, item, image_type, image, url=False):
        item_id = _item_id(item)
        location = image.location if hasattr(image, "location") and hasattr(image, "is_url") else image
        remote = image.is_url if hasattr(image, "is_url") and hasattr(image, "location") else url
        if not remote and isinstance(location, str) and location.startswith(("http://", "https://")):
            remote = True
        if remote:
            if not isinstance(location, str) or not location.startswith(("http://", "https://")):
                raise Failed(f"{self._server().type_label} Error: Image URL is missing")
            self.client.download_remote_image(item_id, image_type, location)
            return
        path = os.fspath(location)
        if not os.path.isfile(path):
            raise Failed(f"{self._server().type_label} Error: Image file not found: {path}")
        content_type = CONTENT_TYPES.get(os.path.splitext(path)[1].lower(), "image/jpeg")
        with open(path, "rb") as handle:
            self.client.upload_image(item_id, image_type, handle.read(), content_type)

    def poster_cache_is_valid(self, item):
        return bool((item.data.get("ImageTags") or {}).get("Primary"))

    def _upload_image(self, item, image):
        self.require(Capability.UPLOAD_OVERLAY)
        if image.is_poster:
            image_type = "Primary"
        elif image.is_background:
            image_type = "Backdrop"
        elif image.is_logo:
            image_type = "Logo"
        else:
            raise Failed(f"{self._server().type_label} Error: This overlay image is not supported")
        self._apply_image(item, image_type, image)
        return True

    def upload_poster(self, item, image, url=False):
        self.require(Capability.UPLOAD_POSTER)
        self._apply_image(item, "Primary", image, url=url)
        return True

    def upload_background(self, item, image, url=False):
        self.require(Capability.UPLOAD_BACKDROP)
        self._apply_image(item, "Backdrop", image, url=url)
        return True

    def upload_logo(self, item, image, url=False):
        self.require(Capability.UPLOAD_LOGO)
        self._apply_image(item, "Logo", image, url=url)
        return True

    def image_update(self, item, image, tmdb=None, title=None, poster=True, image_type=None):
        image_type = image_type or ("poster" if poster else "background")
        display_type = {"poster": "Poster", "background": "Background", "backdrop": "Background", "logo": "Logo", "banner": "Banner", "square_art": "Square Art"}.get(image_type, str(image_type).replace("_", " ").title())
        text = f"{f'{title} ' if title else ''}{display_type}"
        if image is None and isinstance(tmdb, tuple) and tmdb[0] in ("lock", "unlock"):
            action = "Lock" if tmdb[0] == "lock" else "Unlock"
            logger.warning(f"{text} | {action} Not Supported")
            return action, self._server().type_label, "Failed"
        kind = self._image_type(image_type, poster=poster)
        capability = {"Primary": Capability.UPLOAD_POSTER, "Backdrop": Capability.UPLOAD_BACKDROP, "Logo": Capability.UPLOAD_LOGO, "Banner": Capability.UPLOAD_BANNER, "Thumb": Capability.UPLOAD_BANNER}[kind]
        self.require(capability)
        source = "URL"
        candidate = tmdb
        if image is not None:
            source = "URL" if (getattr(image, "is_url", False) or (isinstance(image, str) and str(image).startswith(("http://", "https://")))) else "Assets"
            candidate = image
        elif isinstance(tmdb, tuple):
            source = {"tmdb": "TMDb", "tvdb": "TVDb", "trakt": "Trakt"}.get(tmdb[0], str(tmdb[0] or "URL"))
            candidate = tmdb[1]
        if candidate is None or (isinstance(candidate, str) and not candidate):
            logger.warning(f"{text} | No Image URL")
            return "Reset", source, "Missing"
        self._apply_image(item, kind, candidate)
        logger.info(f"{text} | Set from {source}")
        return "Reset", source, "Updated"

    def reload(self, item, force=False):
        cached = getattr(self, "_search_details", {}).get(item.ratingKey)
        if cached is not None and not force:
            item.apply(cached.data)
            return item
        self.require(Capability.RELOAD_ITEM_FORCE if force else Capability.RELOAD_ITEM)
        item.apply(self.client.get_item(item.ratingKey))
        if hasattr(self, "_search_details"):
            self._search_details[item.ratingKey] = item
        return item

    def item_reload(self, item, exclude_elements=None):
        return self.reload(item)

    def bulk_reload(self, items, force=False):
        for item in items:
            self.reload(item, force=force)

    def get_legacy_overlay_labels(self):
        # Plex's historical '<name> Overlay' labels are not MediaBrowser tags.
        return []

    def batch_add_label(self, items, label):
        for item in items:
            if label not in item.tags:
                self.edit_tags("label", item, add_tags=[label], do_print=False)

    def get_item_display_title(self, item, sort=False):
        title = item.titleSort if sort else item.title
        if item.type == "season":
            series = item.data.get("SeriesName") or ""
            number = item.data.get("IndexNumber")
            return f"{series} Season {number}".strip() if number is not None else f"{series} {title}".strip()
        if item.type == "episode":
            series = item.data.get("SeriesName") or ""
            season = item.data.get("ParentIndexNumber") or 0
            episode = item.data.get("IndexNumber") or 0
            return f"{series} S{season:02}E{episode:02}".strip()
        return title

    def edit_tags(self, attr, obj, add_tags=None, remove_tags=None, sync_tags=None, do_print=True, locked=True, is_locked=None):
        field = TAG_FIELDS.get(attr)
        if field is None:
            raise Failed(f"{self._server().type_label} Error: Cannot edit {attr.replace('_', ' ')}")
        self.require(Capability.SYNC_TAGS if sync_tags is not None else Capability.ADD_TAG if add_tags else Capability.REMOVE_TAG)
        current = list(getattr(obj, "tags" if field == "Tags" else "genres" if field == "Genres" else "studios", None) or [])
        if sync_tags is not None:
            updated = list(sync_tags)
        else:
            updated = [tag for tag in current if tag not in (remove_tags or [])]
            updated.extend(tag for tag in (add_tags or []) if tag not in updated)
        payload = {"Studios": [{"Name": name} for name in updated]} if field == "Studios" else {field: updated}
        if field == "Tags" and self.server.type_name == "emby":
            payload["TagItems"] = updated
        if locked and field in LOCK_FIELDS:
            locked_fields = list(obj.data.get("LockedFields") or [])
            if LOCK_FIELDS[field] not in locked_fields:
                locked_fields.append(LOCK_FIELDS[field])
            payload["LockedFields"] = locked_fields
        self.client.update_item(obj.ratingKey, payload)
        obj.data.update(payload)
        if field == "Tags":
            obj.tags = updated
        elif field == "Genres":
            obj.genres = updated
        else:
            obj.studios = updated
        display = ", ".join(updated)
        if do_print and display:
            logger.info(display)
        return display

    def item_labels(self, item):
        self.require(Capability.GET_ITEM_LABELS)
        return [_Tag(tag) for tag in (getattr(item, "tags", None) or [])]

    def find_poster_url(self, item):
        tags = item.data.get("ImageTags") or {}
        if not tags.get("Primary"):
            return None
        return f"{self.url}/Items/{item.ratingKey}/Images/Primary?tag={quote(str(tags['Primary']))}"

    def item_posters(self, item, providers=None):
        if providers == []:
            return None
        poster = self.find_poster_url(item)
        if not poster:
            raise Failed(f"{self.server.type_label} Error: No poster found to restore")
        return poster

    def get_all(self, builder_level=None, load=False, ignore_schedule_scope=False):
        self.require(Capability.GET_ALL_ITEMS)
        if not builder_level and self._all_items and not load:
            return list(self._all_items)
        include = _include_type(self, builder_level)
        rows = self.client.items({"parentId": self.library_id, "includeItemTypes": include, "recursive": "true"})
        items = [self._wrap(row) for row in rows]
        if not builder_level:
            self._all_items = list(items)
        return items

    def get_items_added_since(self, builder_level, cutoff):
        self.require(Capability.SEARCH_ADDED)
        include = _include_type(self, builder_level)
        rows = []
        start = 0
        page_size = PAGE_SIZE
        while True:
            batch = self.client.items(
                {"parentId": self.library_id, "includeItemTypes": include, "sortBy": "DateCreated", "sortOrder": "Descending", "startIndex": start, "limit": page_size},
                limit=page_size,
                one_page=True,
            )
            if not batch:
                break
            stop = False
            for row in batch:
                added = _parse_date(row.get("DateCreated"))
                added_cutoff = _as_utc(cutoff)
                if added is not None and added_cutoff is not None and added < added_cutoff:
                    stop = True
                    break
                rows.append(row)
            if stop or len(batch) < page_size:
                break
            start += len(batch)
        logger.info(f"Loaded {len(rows)} {self.type}s Added Since {cutoff.date() if hasattr(cutoff, 'date') else cutoff}")
        return [self._wrap(row) for row in rows]

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
            item.apply(self.client.get_item(item.ratingKey))
        if self.is_movie:
            return item.tmdb_id, None, item.imdb_id
        return None, item.tvdb_id, item.imdb_id

    def list_children(self, item, include_type):
        rows = self.client.items({"parentId": item.ratingKey, "includeItemTypes": include_type, "recursive": "false"})
        return [self._wrap(row) for row in rows]

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
        self.require(Capability.SEARCH_TITLE if title else Capability.SEARCH_FULL_TEXT)
        params = {"parentId": self.library_id, "recursive": "true", "includeItemTypes": _include_type(self, libtype)}
        if title:
            params["searchTerm"] = title
        if kwargs.get("label") or kwargs.get("labels"):
            self.require(Capability.GET_ITEM_LABELS)
            params["tags"] = kwargs.get("label") or kwargs.get("labels")
        if kwargs.get("genre"):
            params["genres"] = kwargs["genre"]
        if kwargs.get("year"):
            params["years"] = kwargs["year"]
        if kwargs.get("actor"):
            params["person"] = kwargs["actor"]
        rows = self.client.items(params, limit=maxresults)
        return [self._wrap(row) for row in rows]

    def fetch_item(self, item):
        if isinstance(item, MediaBrowserItem):
            return self.reload(item)
        return self.reload(self._wrap({"Id": item}))

    def asset_directories(self, item):
        if isinstance(item, (MediaBrowserCollection, MediaBrowserPlaylist)) and self.collection_asset_directory:
            return self.collection_asset_directory
        return self.asset_directory

    def asset_search_paths(self, item, item_dir=None, folder_name=None, asset_directory=None, folders_only=False):
        from modules.plex import Plex

        name = item if isinstance(item, str) else item.title
        return Plex.asset_search_paths(self, name, item_dir=item_dir, folder_name=folder_name, asset_directory=asset_directory, folders_only=folders_only)

    def find_item_assets(self, item, item_asset_directory=None, asset_directory=None, folder_name=None):
        # Reuse the filesystem resolver by title; this makes no Plex requests.
        from modules.plex import Plex

        directories = self.asset_directories(item) if asset_directory is None else asset_directory
        name = item if isinstance(item, str) else item.title
        return Plex.find_item_assets(self, name, item_asset_directory=item_asset_directory, asset_directory=directories, folder_name=folder_name)

    def get_collection(self, data, force_search=False, debug=True):
        self.require(Capability.GET_COLLECTION_BY_NAME)
        if isinstance(data, MediaBrowserCollection):
            return data
        title = data if isinstance(data, str) else str(getattr(data, "title", data))
        collections = self._collections()
        matches = [collection for collection in collections if str(collection.title).casefold() == title.casefold()]
        if not matches and self.server.type_name == "jellyfin":
            # Providers can rename unlocked boxsets while their original folder
            # names survive. Recover only an unambiguous exact folder match.
            folder = f"{title} [boxset]".casefold()
            renamed = [collection for collection in collections if str(collection.data.get("Path") or "").replace("\\", "/").rstrip("/").rsplit("/", 1)[-1].casefold() == folder]
            if len(renamed) > 1:
                raise Failed(f"Jellyfin Error: Multiple renamed collections match the original folder for '{title}'; cannot safely recover")
            if renamed:
                collection = renamed[0]
                logger.warning(f"Jellyfin Warning: Restoring collection '{collection.title}' to '{title}' using its original folder name and locking metadata")
                collection.apply(self.client.update_item(collection.ratingKey, {"Name": title, "LockData": True, "ProviderIds": {}}))
                matches = [collection]
        if not matches:
            if debug:
                logger.debug(f"Looking for: {data}")
            raise Failed(f"{self._server().type_label} Error: Collection {data} not found")
        if len(matches) > 1:
            logger.warning(f"{self._server().type_label} Warning: Multiple collections found with title '{title}', using the first exact match")
        return matches[0]

    def get_collection_items(self, collection, smart_label_collection):
        if smart_label_collection:
            self.require(Capability.GET_ITEM_LABELS)
            return self.search(label=collection.title if isinstance(collection, MediaBrowserCollection) else str(collection))
        if isinstance(collection, MediaBrowserPlaylist):
            return [self._wrap(row) for row in self.client.playlist_entries(collection.ratingKey)]
        if isinstance(collection, MediaBrowserCollection):
            self.require(Capability.GET_COLLECTION_ITEMS)
            return [self._wrap(row) for row in self.client.items({"parentId": collection.ratingKey, "recursive": "false"})]
        return []

    def get_collection_name_and_items(self, collection, smart_label_collection):
        if isinstance(collection, (MediaBrowserCollection, MediaBrowserPlaylist)):
            return collection.title, self.get_collection_items(collection, smart_label_collection)
        return str(collection), []

    def create_blank_collection(self, title):
        self.require(Capability.CREATE_COLLECTION)
        try:
            return self.get_collection(title, debug=False)
        except Failed:
            pass
        if self.server.type_name == "emby":
            raise Failed(
                "Emby Error: A new collection requires initial members. For separator collections, set placeholder_imdb_id, placeholder_tmdb_movie, or placeholder_tvdb_show under template_variables to an item present in this library (for example, placeholder_imdb_id: tt0068646). Otherwise, use a builder-based collection."
            )
        created = self.client.create_collection(title, parent_id=self.library_id)
        return self._wrap_collection(self.client.get_item(created.get("Id")) or {"Id": created.get("Id"), "Name": title, "Type": "BoxSet"})

    def alter_collection(self, items, collection, smart_label_collection=False, add=True):
        if smart_label_collection:
            self.require(Capability.ADD_TAG if add else Capability.REMOVE_TAG)
            for item in items:
                self.edit_tags("label", item, add_tags=[str(collection)] if add else None, remove_tags=None if add else [str(collection)], do_print=False, locked=False)
            return
        self.require(Capability.ADD_COLLECTION_ITEMS if add else Capability.REMOVE_COLLECTION_ITEMS)
        ids = [_item_id(item) for item in items]
        if not ids:
            return
        if add and isinstance(collection, str) and self.server.type_name == "emby":
            try:
                target = self.get_collection(collection, debug=False)
            except Failed:
                self.require(Capability.CREATE_COLLECTION)
                # Emby creates the boxset with its initial members, without a
                # movie-library parent. These IDs must not be added twice.
                self.client.create_collection(collection, item_ids=ids)
                return
        else:
            target = self.create_blank_collection(collection) if add and isinstance(collection, str) else self._collection(collection)
        for item in items:
            logger.ghost(f"{'Adding' if add else 'Removing'} {getattr(item, 'title', _item_id(item))} collection: {target.title}")
        if add:
            self.client.add_collection_items(target.ratingKey, ids)
        else:
            self.client.remove_collection_items(target.ratingKey, ids)
        logger.exorcise()

    def delete(self, obj, notify=True, delete_message=None):
        if isinstance(obj, MediaBrowserPlaylist):
            self.require(Capability.DELETE_PLAYLIST)
            label = "Playlist"
        elif isinstance(obj, MediaBrowserCollection):
            self.require(Capability.DELETE_COLLECTION)
            label = "Collection"
        else:
            self.require(Capability.DELETE_ITEM)
            label = "Item"
        self.client.delete_item(obj.ratingKey)
        if isinstance(obj, MediaBrowserCollection):
            self.stats["deleted"] += 1
        if notify:
            self.notify_delete(delete_message or f"{label} {obj.title} deleted")
        return obj

    def delete_collection(self, obj, notify=True, delete_message=None):
        return self.delete(obj, notify=notify, delete_message=delete_message)

    def create_smart_collection(self, title, smart_type, uri_args, ignore_blank_results):
        self.require(Capability.NATIVE_SMART_COLLECTIONS)

    def update_smart_collection(self, collection, uri_args):
        self.require(Capability.UPDATE_SMART_FILTER)

    def create_playlist(self, name, items=None):
        self.require(Capability.CREATE_PLAYLIST)
        created = self.client.create_playlist(name, [_item_id(item) for item in (items or [])])
        playlist_id = created.get("Id")
        return self._wrap_playlist(self.client.get_item(playlist_id) or {"Id": playlist_id, "Name": name, "Type": "Playlist"})

    def get_playlist(self, title):
        self.require(Capability.GET_PLAYLIST)
        matches = [playlist for playlist in self._playlists() if str(playlist.title).casefold() == str(title).casefold()]
        if not matches:
            raise Failed(f"{self._server().type_label} Error: Playlist {title} not found")
        return matches[0]

    def get_playlist_from_users(self, playlist_title):
        return self.get_playlist(playlist_title)

    def create_smart_playlist(self, title, uri_args):
        self.require(Capability.NATIVE_SMART_COLLECTIONS)

    def update_smart_playlist(self, playlist, uri_args):
        self.require(Capability.UPDATE_SMART_FILTER)

    def smart_label_check(self, label):
        self.require(Capability.GET_ITEM_LABELS)
        return bool(self.search(label=label, maxresults=1))

    def fetchItems(self, uri_args):
        if isinstance(uri_args, dict) and "local_collection_search" in uri_args:
            definition = uri_args["local_collection_search"]
            predicate = self.validate_collection_search(definition)
            items = [item for item in self._local_search_items(require_media=self._search_requires_media(definition)) if predicate(self._search_metadata(item))]
            field, _, order = definition.get("sort_by", "title.asc").rpartition(".")
            key = LOCAL_COLLECTION_SORTS[field]
            known = [item for item in items if item.data.get(key) is not None or field == "title"]
            missing = [item for item in items if item.data.get(key) is None and field != "title"]
            known.sort(key=lambda item: item.data[key] if item.data.get(key) is not None else item.title.casefold(), reverse=order == "desc")
            return (known + missing)[: definition.get("limit")]
        if isinstance(uri_args, dict) and "local_metadata_search" in uri_args:
            predicate = compile_selector(uri_args["local_metadata_search"], self.server.type_label)
            return [item for item in self._local_search_items(require_media=self._search_requires_media(uri_args["local_metadata_search"])) if predicate(self._search_metadata(item))]
        self.require(Capability.PARSE_SMART_FILTER)

    def build_local_search(self, definition):
        if isinstance(definition, dict) and "local_collection_search" in definition:
            self.validate_collection_search(definition["local_collection_search"])
            return None, f"{self.server.type_label} locally rebuilt collection", definition
        compile_selector(definition, self.server.type_label)
        return None, f"{self.server.type_label} local metadata search", {"local_metadata_search": definition}

    def validate_collection_search(self, definition):
        if not isinstance(definition, dict) or set(definition) - {"all", "any", "sort_by", "limit", "type", "validate"}:
            raise Failed(f"{self.server.type_label} Error: Unsupported smart_filter options")
        scope = definition.get("type")
        if scope and scope not in (("movie", "movies") if self.is_movie else ("show", "shows", "series")):
            raise Failed(f"{self.server.type_label} Error: smart_filter type {scope} is not supported for this library")
        if definition.get("sort_by", "title.asc") not in [f"{field}.{order}" for field in LOCAL_COLLECTION_SORTS for order in ("asc", "desc")]:
            raise Failed(f"{self.server.type_label} Error: Unsupported smart_filter sort_by")
        if "limit" in definition and (isinstance(definition["limit"], bool) or not isinstance(definition["limit"], int) or definition["limit"] <= 0):
            raise Failed(f"{self.server.type_label} Error: smart_filter limit must be a positive integer")
        return compile_selector({key: value for key, value in definition.items() if key in ("all", "any")}, self.server.type_label)

    @staticmethod
    def _search_requires_media(definition):
        if isinstance(definition, list):
            return any(MediaBrowser._search_requires_media(group) for group in definition)
        if isinstance(definition, dict):
            return any(
                key.partition(".")[0] in {"resolution", "edition", "filepath", "hdr", "has_dolby_vision", "audio_language", "subtitle_language"} or (key in ("all", "any") and MediaBrowser._search_requires_media(value)) for key, value in definition.items()
            )
        return False

    def _local_search_items(self, builder_level=None, require_media=True):
        if not hasattr(self, "_search_details"):
            self._search_details = {}
        if not hasattr(self, "_media_details_loaded"):
            self._media_details_loaded = set()
        logger.info(f"Loading {self.server.type_label} catalog for local search")
        items = self.get_all(builder_level=builder_level) if builder_level else self.get_all()
        total = len(items)
        logger.info(f"Scanning {total} {self.server.type_label} items for local search{' (loading media details as needed)' if require_media else ' (catalog metadata)'}")
        try:
            for index, item in enumerate(items, 1):
                cache_key = (builder_level, item.ratingKey) if builder_level else item.ratingKey
                item = self._search_details.get(cache_key, item)
                logger.ghost(f"Scanning: {index}/{total} {item.title}")
                if require_media and cache_key not in self._media_details_loaded and "MediaSources" not in item.data and "MediaStreams" not in item.data:
                    item.apply(self.client.get_item(item.ratingKey))
                    self._media_details_loaded.add(cache_key)
                self._search_details[cache_key] = item
                if index % PAGE_SIZE == 0:
                    logger.info(f"Scanned: {index}/{total}")
                yield item
        finally:
            logger.exorcise()
        logger.info(f"Scanned: {total}/{total}")

    @staticmethod
    def _search_metadata(item):
        versions = []
        for source in item.data.get("MediaSources") or [item.data]:
            streams = source.get("MediaStreams") or item.data.get("MediaStreams") or []
            video = next((stream for stream in streams if stream.get("Type") == "Video"), {})
            width = video.get("Width") or 0
            height = video.get("Height") or 0
            resolution = (
                "4320p"
                if width >= 7600 or height >= 4200
                else (
                    "2160p"
                    if width >= 3800 or height >= 2100
                    else "1440p" if width >= 2500 or height >= 1400 else "1080p" if width >= 1900 or height >= 1000 else "720p" if width >= 1200 or height >= 700 else "576p" if width > 720 or height > 480 else "480p" if width or height else None
                )
            )
            video_range = video.get("VideoRangeType") or video.get("VideoRange")
            version = {"file_path": source.get("Path") or item.data.get("Path"), "resolution": resolution, "edition_raw": item.data.get("EditionName")}
            for stream_type, field in (("Audio", "audio_tracks"), ("Subtitle", "subtitle_tracks")):
                version[field] = [{"language": stream["Language"].strip().lower()} for stream in streams if stream.get("Type") == stream_type and isinstance(stream.get("Language"), str) and stream["Language"].strip()]
            aspect = video.get("AspectRatio") or source.get("AspectRatio")
            try:
                parts = str(aspect).replace("/", ":").split(":")
                ratio = float(parts[0]) / float(parts[1]) if len(parts) == 2 else float(aspect)
            except (TypeError, ValueError, ZeroDivisionError):
                ratio = width / height if width and height else None
            if ratio is not None and ratio > 0:
                version["aspect"] = round(ratio, 2)
            if video_range is not None and str(video_range).upper() not in ("UNKNOWN", ""):
                version["hdr"] = str(video_range).upper() != "SDR"
                version["dolby_vision"] = str(video_range).lower().startswith(("dovi", "dolby"))
            if video.get("DvProfile") is not None:
                version["dolby_vision"] = bool(video["DvProfile"])
            versions.append(version)
        return SimpleNamespace(
            data={
                "title": item.title,
                "year": item.year,
                "content_rating": item.contentRating,
                "genres": item.genres,
                "studios": item.studios,
                "countries": item.data.get("ProductionLocations") or [],
                "versions": versions,
                "release": item.data.get("PremiereDate"),
                "added": item.data.get("DateCreated"),
                **{role: [person.tag for person in getattr(item, f"{role}s", [])] for role in ("actor", "director", "writer", "producer")},
            }
        )

    def get_rating_keys(self, method, data, is_playlist=False):
        if method == "plex_search":
            items = self.fetchItems(data[2])
        elif method == "plex_all" and data in ("movie", "show", "item"):
            items = list(self._local_search_items())
        else:
            raise Failed(f"{self.server.type_label} Error: Unsupported local builder: {method}")
        return [(item.ratingKey, "ratingKey") for item in items]

    def get_tags(self, tag):
        """Discover dynamic collection keys from this library's native metadata."""
        if tag in ("year", "decade"):
            years = {int(item.year) for item in self.get_all() if not isinstance(item.year, bool) and str(item.year).isascii() and str(item.year).isdecimal() and 1 <= int(item.year) <= 9999}
            if tag == "decade":
                return [SimpleNamespace(key=str(year), title=f"{year}s") for year in sorted({year // 10 * 10 for year in years})]
            return [SimpleNamespace(key=str(year), title=str(year)) for year in sorted(years)]
        if tag in ("resolution", "episode.resolution"):
            names = set()
            for item in self._local_search_items(builder_level="episode" if tag.startswith("episode.") else None):
                for version in self._search_metadata(item).data["versions"]:
                    resolution = version.get("resolution")
                    if resolution:
                        names.add({"2160p": "4k", "4320p": "8k", "1440p": "2k"}.get(resolution, resolution.removesuffix("p")))
            return [SimpleNamespace(key=name, title=name) for name in sorted(names)]
        language_fields = {"audioLanguage": "audio_language", "audio_language": "audio_language", "subtitleLanguage": "subtitle_language", "subtitle_language": "subtitle_language"}
        language_tag = tag.removeprefix("episode.")
        if language_tag in language_fields:
            from modules.local_search import values

            field = language_fields[language_tag]
            names = {name for item in self._local_search_items(builder_level="episode" if tag.startswith("episode.") else None) for name in values(self._search_metadata(item), field)}
            return [SimpleNamespace(key=name, title=name) for name in sorted(names)]
        fields = {"contentRating": "contentRating", "content_rating": "contentRating", "genre": "genres", "studio": "studios", "country": "countries"}
        field = fields.get(tag)
        if field is None:
            raise Failed(f"{self.server.type_label} Error: Dynamic collection tag '{tag}' is not supported; supported tags: genre, studio, country, content_rating, audio_language, subtitle_language, resolution, year, decade")
        names = set()
        for item in self.get_all():
            values = (item.data.get("ProductionLocations") or []) if field == "countries" else getattr(item, field, [])
            for name in [values] if isinstance(values, str) else values or []:
                if isinstance(name, str) and name.strip():
                    names.add(name.strip())
        return [SimpleNamespace(key=name, title=name) for name in sorted(names, key=lambda name: (name.casefold(), name))]

    def check_filters(self, item, filters_in, current_time):
        normalized = self._search_metadata(item)
        for key, value in filters_in:
            field, _, modifier = key.partition(".")
            if field == "aspect":
                aspects = [version["aspect"] for version in normalized.data["versions"] if "aspect" in version]
                modifier = {"is": "", "isnot": ".not"}.get(modifier, f".{modifier}" if modifier else "")
                if modifier not in ("", ".not", ".gt", ".gte", ".lt", ".lte"):
                    raise Failed(f"{self.server.type_label} Error: Unsupported aspect filter modifier: {key}")
                if util.is_number_filter(max(aspects) if aspects else None, modifier, value):
                    return False
            elif not compile_selector({key: value}, self.server.type_label)(normalized):
                return False
        return True

    def set_user_rating(self, item, rating):
        self.require(Capability.SET_USER_RATING)
        self.client.update_user_data(_item_id(item), {"Rating": rating})

    def set_critic_rating(self, item, rating):
        self.require(Capability.SET_CRITIC_RATING)
        self.client.update_item(_item_id(item), {"CriticRating": rating})

    def query(self, method):
        return method()

    def query_data(self, method, data):
        return method(data)

    def collection_mode_query(self, collection, data):
        logger.warning(f"{self._server().type_label} collections do not use Plex collection mode ({data})")

    def collection_order_query(self, collection, data):
        if data in ("custom", "custom.asc", "custom.desc"):
            return False
        fields = {"release": "PremiereDate", "alpha": "SortName", "release.asc": "PremiereDate", "title.asc": "SortName"}
        if self.server.type_name == "jellyfin":
            fields.update({"added.asc": "DateCreated", "year.asc": "ProductionYear", "duration.asc": "Runtime", "content_rating.asc": "OfficialRating"})
        display_order = fields.get(data)
        if display_order is None:
            logger.warning(f"{self._server().type_label} Warning: Collection order {data} is not supported; keeping the server's display order")
            return False
        if collection.data.get("DisplayOrder") == display_order:
            return False
        payload = self.client.update_item(collection.ratingKey, {"DisplayOrder": display_order})
        collection.apply(payload)
        return True

    def sort_collection_items(self, collection, items, order):
        if isinstance(order, list) and len(order) == 1:
            if self.collection_order_query(collection, order[0]):
                logger.info(f"Collection display order updated: {order[0]}")
            return
        logger.warning(f"Collection Warning: Custom item ordering is not supported by {self.server.display_name}; keeping the server's display order")

    def collection_visibility(self, collection):
        return {"library": True, "home": True, "shared": True}

    def collection_visibility_update(self, collection, visibility=None, library=None, home=None, shared=None):
        logger.warning(f"{self._server().type_label} collections do not use Plex visibility")

    def edit_query(self, item, edits, advanced=False):
        logger.warning(f"{self._server().type_label} does not apply Plex edit keys")

    def split(self, text):
        from modules.plex import Plex

        return Plex.split(self, text)  # type: ignore[arg-type]  # split only reads library fields such as is_movie

    def get_all_collections(self, label=None):
        collections = self._collections()
        if label is None:
            return collections
        return [collection for collection in collections if str(label) in list(getattr(collection, "tags", None) or [])]

    def _collections(self):
        self.require(Capability.GET_ALL_COLLECTIONS)
        return [self._wrap_collection(row) for row in self.client.items({"includeItemTypes": "BoxSet", "recursive": "true"})]

    def _playlists(self):
        self.require(Capability.GET_PLAYLIST)
        return [self._wrap_playlist(row) for row in self.client.items({"includeItemTypes": "Playlist", "recursive": "true"})]

    def _collection(self, collection):
        if isinstance(collection, MediaBrowserCollection):
            return collection
        return self.get_collection(collection)

    def _wrap(self, row):
        if row.get("Type") == "BoxSet":
            return self._wrap_collection(row)
        if row.get("Type") == "Playlist":
            return self._wrap_playlist(row)
        return MediaBrowserItem(row, self)

    def _wrap_collection(self, row):
        row = dict(row)
        row["Type"] = "BoxSet"
        return MediaBrowserCollection(row, self)

    def _wrap_playlist(self, row):
        row = dict(row)
        row["Type"] = "Playlist"
        return MediaBrowserPlaylist(row, self)


class Jellyfin(MediaBrowser):
    server_class = JellyfinMediaServer


class Emby(MediaBrowser):
    server_class = EmbyMediaServer


class _BrowserSection:
    """Attributes collection setup reads from ``library.Plex``."""

    def __init__(self, library_type, language, key, title, product):
        self.type = library_type
        self.TYPE = library_type
        self.language = language
        self.key = key
        self.title = title
        self.product = product

    def __getattr__(self, name):
        raise Failed(f"{self.product} Error: Plex library attribute '{name}' is not available on a {self.product} library")


def select_library(folders, name, product):
    match = next((folder for folder in folders if folder.get("Name") == name), None)
    if match is None:
        options = [folder.get("Name") for folder in folders]
        raise Failed(f"{product} Error: Library '{name}' not found. Options: {options}")
    kometa_library_type(match.get("CollectionType"), product)
    return match


def kometa_library_type(collection_type, product):
    mapped = LIBRARY_TYPES.get(str(collection_type or "").lower())
    if mapped is None:
        raise Failed(f"{product} Error: Library type '{collection_type}' is not movies or tvshows")
    return mapped


def _path_id(value):
    return quote(str(value), safe="")


def _item_id(item):
    return getattr(item, "ratingKey", item)


def _provider(providers, *keys):
    if not isinstance(providers, dict):
        return None
    folded = {str(key).lower(): value for key, value in providers.items()}
    for key in keys:
        if folded.get(key.lower()):
            return folded[key.lower()]
    return None


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


def _include_type(library, builder_level):
    if builder_level in ("movie", "Movie"):
        return "Movie"
    if builder_level in ("show", "series", "Show"):
        return "Series"
    if builder_level in ("season", "Season"):
        return "Season"
    if builder_level in ("episode", "Episode"):
        return "Episode"
    return "Movie" if library.is_movie else "Series"


def _parse_date(value):
    if not value:
        return None
    text = str(value).replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _as_utc(value):
    if not isinstance(value, datetime):
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


register_media_server(JellyfinMediaServer)
register_media_server(EmbyMediaServer)
