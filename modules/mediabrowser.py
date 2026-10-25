"""Jellyfin and Emby media servers.

Both speak the MediaBrowser API. A library selects one with ``server`` on a
``media_servers`` entry of ``type: jellyfin`` or ``type: emby``. Collections are
boxsets. Posters, backdrops, logos, banners, and overlays upload as image bytes,
or the server downloads a URL. Plex smart-filter addresses are not accepted.
"""

import os
from collections.abc import Iterable
from datetime import datetime, timezone
from urllib.parse import quote

import requests

from modules import util
from modules.library import Library
from modules.media_server import Capability, CapabilityMatrix, MediaServer, register_media_server
from modules.util import Failed

logger = util.logger

LIBRARY_TYPES = {"movies": "Movie", "movie": "Movie", "tvshows": "Show", "tv": "Show"}
ITEM_TYPES = {"Movie": "movie", "Series": "show", "Season": "season", "Episode": "episode", "BoxSet": "collection", "Playlist": "playlist"}
ITEM_FIELDS = "ProviderIds,Genres,Studios,Overview,Tags,DateCreated,ProductionYear,PremiereDate,CommunityRating,CriticRating,OfficialRating,ChildCount,RecursiveItemCount,SortName,ImageTags,LockedFields"
PAGE_SIZE = 200
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

    def request(self, method, path, params=None, json_body=None, data=None, headers=None):
        try:
            response = self.session.request(method, f"{self.base}/{path.lstrip('/')}", params=params, json=json_body, data=data, headers=headers, timeout=self.server.timeout)
        except requests.RequestException as error:
            raise Failed(f"{self.server.type_label} Error: {method} {path} failed: {error}") from error
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
        params = {"name": name}
        if parent_id:
            params["parentId"] = parent_id
        if item_ids:
            params["ids"] = ",".join(str(item_id) for item_id in item_ids)
        return self.request("POST", "/Collections", params=params) or {}

    def add_collection_items(self, collection_id, item_ids):
        self.request("POST", f"/Collections/{_path_id(collection_id)}/Items", params={"ids": ",".join(str(item_id) for item_id in item_ids)})

    def remove_collection_items(self, collection_id, item_ids):
        self.request("DELETE", f"/Collections/{_path_id(collection_id)}/Items", params={"ids": ",".join(str(item_id) for item_id in item_ids)})

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
        self.request("POST", f"/Items/{_path_id(item_id)}/Images/{image_type}", data=content, headers={"Content-Type": content_type})

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
        self.titleSort = self.data.get("SortName") or self.title
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
        self.tags = list(self.data.get("Tags") or [])
        self.childCount = self.data.get("ChildCount") or self.data.get("RecursiveItemCount") or 0
        self.smart = False
        self.collectionMode = -1
        self.collectionSort = -1
        self.locations = []

    def seasons(self):
        return self.library.list_children(self, "Season")

    def episodes(self):
        return self.library.list_children(self, "Episode")

    def editSummary(self, summary):
        self.library.client.update_item(self.ratingKey, {"Overview": summary})
        self.summary = summary

    def editSortTitle(self, sort_title):
        self.library.client.update_item(self.ratingKey, {"SortName": sort_title})
        self.titleSort = sort_title

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
        logger.info(f"Connected to {server.type_label} server {server.display_name}")
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
        self.require(Capability.RELOAD_ITEM_FORCE if force else Capability.RELOAD_ITEM)
        if force:
            self.client.refresh_item(item.ratingKey)
        item.apply(self.client.get_item(item.ratingKey))
        return item

    def item_reload(self, item, exclude_elements=None):
        return self.reload(item)

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
        if locked and field in LOCK_FIELDS:
            locked_fields = list(obj.data.get("LockedFields") or [])
            if LOCK_FIELDS[field] not in locked_fields:
                locked_fields.append(LOCK_FIELDS[field])
            payload["LockedFields"] = locked_fields
        self.client.update_item(obj.ratingKey, payload)
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
        poster = self.find_poster_url(item)
        return [poster] if poster else []

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

    def get_collection(self, data, force_search=False, debug=True):
        self.require(Capability.GET_COLLECTION_BY_NAME)
        if isinstance(data, MediaBrowserCollection):
            return data
        title = str(getattr(data, "title", data))
        matches = [collection for collection in self._collections() if str(collection.title).casefold() == title.casefold()]
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
        created = self.client.create_collection(title, parent_id=self.library_id)
        return self._wrap_collection(self.client.get_item(created.get("Id")) or {"Id": created.get("Id"), "Name": title, "Type": "BoxSet"})

    def alter_collection(self, items, collection, smart_label_collection=False, add=True):
        if smart_label_collection:
            self.require(Capability.ADD_TAG if add else Capability.REMOVE_TAG)
            for item in items:
                self.edit_tags("label", item, add_tags=[str(collection)] if add else None, remove_tags=None if add else [str(collection)], do_print=False, locked=False)
            return
        self.require(Capability.ADD_COLLECTION_ITEMS if add else Capability.REMOVE_COLLECTION_ITEMS)
        target = self._collection(collection)
        ids = [_item_id(item) for item in items]
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
        self.require(Capability.PARSE_SMART_FILTER)

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
        logger.warning(f"{self._server().type_label} collections do not use Plex collection order ({data})")

    def collection_visibility(self, collection):
        return {"library": True, "home": True, "shared": True}

    def collection_visibility_update(self, collection, visibility=None, library=None, home=None, shared=None):
        logger.warning(f"{self._server().type_label} collections do not use Plex visibility")

    def edit_query(self, item, edits, advanced=False):
        logger.warning(f"{self._server().type_label} does not apply Plex edit keys")

    def split(self, text):
        from modules.plex import Plex

        return Plex.split(self, text)  # type: ignore[arg-type]  # split only reads library fields such as is_movie

    def _collections(self):
        self.require(Capability.GET_ALL_COLLECTIONS)
        return [self._wrap_collection(row) for row in self.client.items({"includeItemTypes": "BoxSet", "recursive": "true"})]

    def _playlists(self):
        self.require(Capability.GET_PLAYLIST)
        return [self._wrap_playlist(row) for row in self.client.items({"includeItemTypes": "Playlist", "recursive": "true"})]

    def _collection(self, collection):
        if isinstance(collection, MediaBrowserCollection):
            return collection
        return self.get_collection(getattr(collection, "title", collection))

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
