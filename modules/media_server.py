"""Media server connection and the capability matrix each server can be queried for.

The matrix follows the feature rows in Kometa-Team/Kometa#3351. Servers are not
equivalent, so callers ask the matrix before using a feature instead of assuming
every backend matches Plex.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from modules.util import Failed


class Support(Enum):
    FULL = "full"
    PARTIAL = "partial"
    NONE = "none"


class Capability(Enum):
    """One row from the media-server feature matrix."""

    CREATE_COLLECTION = "create_collection"
    GET_ALL_COLLECTIONS = "get_all_collections"
    GET_COLLECTION_BY_NAME = "get_collection_by_name"
    GET_COLLECTION_ITEMS = "get_collection_items"
    ADD_COLLECTION_ITEMS = "add_collection_items"
    REMOVE_COLLECTION_ITEMS = "remove_collection_items"
    SYNC_COLLECTION = "sync_collection"
    DELETE_COLLECTION = "delete_collection"
    NATIVE_SMART_COLLECTIONS = "native_smart_collections"
    SMART_COLLECTION_WORKAROUND = "smart_collection_workaround"
    UPDATE_SMART_FILTER = "update_smart_filter"
    TEST_FILTER = "test_filter"
    GET_ALL_ITEMS = "get_all_items"
    GET_ALL_ITEMS_NATIVE = "get_all_items_native"
    FETCH_ITEM = "fetch_item"
    DELETE_ITEM = "delete_item"
    RELOAD_ITEM = "reload_item"
    RELOAD_ITEM_FORCE = "reload_item_force"
    SEARCH_FULL_TEXT = "search_full_text"
    SEARCH_TITLE = "search_title"
    SEARCH_ACTOR = "search_actor"
    SEARCH_GENRE = "search_genre"
    SEARCH_YEAR = "search_year"
    SEARCH_RATING = "search_rating"
    SEARCH_ADDED = "search_added"
    VALIDATE_FILTER_SYNTAX = "validate_filter_syntax"
    SEARCH_CHOICES = "search_choices"
    PARSE_SMART_FILTER = "parse_smart_filter"
    BUILD_FILTER = "build_filter"
    VALIDATE_FILTER_LOGIC = "validate_filter_logic"
    ADD_TAG = "add_tag"
    REMOVE_TAG = "remove_tag"
    SYNC_TAGS = "sync_tags"
    GET_ITEM_LABELS = "get_item_labels"
    LOCK_TAG = "lock_tag"
    SET_USER_RATING = "set_user_rating"
    SET_CRITIC_RATING = "set_critic_rating"
    EDIT_TITLE = "edit_title"
    EDIT_SORT_TITLE = "edit_sort_title"
    EDIT_SUMMARY = "edit_summary"
    EDIT_YEAR = "edit_year"
    UPLOAD_POSTER = "upload_poster"
    UPLOAD_BACKDROP = "upload_backdrop"
    UPLOAD_LOGO = "upload_logo"
    UPLOAD_BANNER = "upload_banner"
    UPLOAD_OVERLAY = "upload_overlay"
    FIND_POSTER_ASSET = "find_poster_asset"
    FIND_BACKDROP_ASSET = "find_backdrop_asset"
    FIND_LOGO_ASSET = "find_logo_asset"
    VALIDATE_ASSET = "validate_asset"
    UPLOAD_THEME_SONG = "upload_theme_song"
    UPLOAD_THEME_VIDEO = "upload_theme_video"
    BATCH_TAGS = "batch_tags"
    BATCH_RATINGS = "batch_ratings"
    BATCH_METADATA = "batch_metadata"
    BUILDER_ADD_ITEMS = "builder_add_items"
    BUILDER_REMOVE_ITEMS = "builder_remove_items"
    BUILDER_REPLACE_ITEMS = "builder_replace_items"
    CREATE_PLAYLIST = "create_playlist"
    GET_PLAYLIST = "get_playlist"
    ADD_PLAYLIST_ITEMS = "add_playlist_items"
    REMOVE_PLAYLIST_ITEMS = "remove_playlist_items"
    DELETE_PLAYLIST = "delete_playlist"
    PARSE_FILTER_EXPRESSION = "parse_filter_expression"
    PARSE_RELATIVE_DATE = "parse_relative_date"
    PARSE_QUERY_STRING = "parse_query_string"
    SEND_NOTIFICATION = "send_notification"
    NOTIFY_DELETION = "notify_deletion"
    GET_RATING_KEY = "get_rating_key"
    GET_ACTOR_ID = "get_actor_id"
    GET_PROVIDER_IDS = "get_provider_ids"

    @property
    def label(self) -> str:
        return CAPABILITY_INFO[self].label

    @property
    def section(self) -> str:
        return CAPABILITY_INFO[self].section


@dataclass(frozen=True)
class CapabilityInfo:
    label: str
    section: str


CAPABILITY_INFO = {
    Capability.CREATE_COLLECTION: CapabilityInfo("Create basic collection", "A1. Create Collection"),
    Capability.GET_ALL_COLLECTIONS: CapabilityInfo("Get all collections", "A2. Get Collections"),
    Capability.GET_COLLECTION_BY_NAME: CapabilityInfo("Get collection by name", "A2. Get Collections"),
    Capability.GET_COLLECTION_ITEMS: CapabilityInfo("Get collection items", "A2. Get Collections"),
    Capability.ADD_COLLECTION_ITEMS: CapabilityInfo("Add items to collection", "A3. Alter Collection"),
    Capability.REMOVE_COLLECTION_ITEMS: CapabilityInfo("Remove items from collection", "A3. Alter Collection"),
    Capability.SYNC_COLLECTION: CapabilityInfo("Sync collection (replace all)", "A3. Alter Collection"),
    Capability.DELETE_COLLECTION: CapabilityInfo("Delete collection", "A3. Alter Collection"),
    Capability.NATIVE_SMART_COLLECTIONS: CapabilityInfo("Native smart collections", "A4. Smart Collections (Filter-Based, Dynamic)"),
    Capability.SMART_COLLECTION_WORKAROUND: CapabilityInfo("Smart collection workaround", "A4. Smart Collections (Filter-Based, Dynamic)"),
    Capability.UPDATE_SMART_FILTER: CapabilityInfo("Update smart filter", "A4. Smart Collections (Filter-Based, Dynamic)"),
    Capability.TEST_FILTER: CapabilityInfo("Test filter before applying", "A4. Smart Collections (Filter-Based, Dynamic)"),
    Capability.GET_ALL_ITEMS: CapabilityInfo("Get all items", "B1. Get Items"),
    Capability.GET_ALL_ITEMS_NATIVE: CapabilityInfo("Get all items (native format)", "B1. Get Items"),
    Capability.FETCH_ITEM: CapabilityInfo("Fetch single item by ID", "B1. Get Items"),
    Capability.DELETE_ITEM: CapabilityInfo("Delete item from library", "B2. Delete Items"),
    Capability.RELOAD_ITEM: CapabilityInfo("Reload item metadata from server", "B3. Reload Items"),
    Capability.RELOAD_ITEM_FORCE: CapabilityInfo("Reload with force/refresh", "B3. Reload Items"),
    Capability.SEARCH_FULL_TEXT: CapabilityInfo("Full-text search", "C1. Search Methods"),
    Capability.SEARCH_TITLE: CapabilityInfo("Search by title", "C1. Search Methods"),
    Capability.SEARCH_ACTOR: CapabilityInfo("Search by actor", "C1. Search Methods"),
    Capability.SEARCH_GENRE: CapabilityInfo("Search by genre", "C1. Search Methods"),
    Capability.SEARCH_YEAR: CapabilityInfo("Search by year", "C1. Search Methods"),
    Capability.SEARCH_RATING: CapabilityInfo("Search by rating (user/critic)", "C1. Search Methods"),
    Capability.SEARCH_ADDED: CapabilityInfo("Search by added date", "C1. Search Methods"),
    Capability.VALIDATE_FILTER_SYNTAX: CapabilityInfo("Validate filter syntax", "C2. Search Validation & Choices"),
    Capability.SEARCH_CHOICES: CapabilityInfo("Get available search choices", "C2. Search Validation & Choices"),
    Capability.PARSE_SMART_FILTER: CapabilityInfo("Parse smart filter URI", "C3. Smart Filters"),
    Capability.BUILD_FILTER: CapabilityInfo("Build filter expressions", "C3. Smart Filters"),
    Capability.VALIDATE_FILTER_LOGIC: CapabilityInfo("Validate filter logic", "C3. Smart Filters"),
    Capability.ADD_TAG: CapabilityInfo("Add tag to item", "D1. Tags/Labels"),
    Capability.REMOVE_TAG: CapabilityInfo("Remove tag from item", "D1. Tags/Labels"),
    Capability.SYNC_TAGS: CapabilityInfo("Replace all tags (sync)", "D1. Tags/Labels"),
    Capability.GET_ITEM_LABELS: CapabilityInfo("Get item labels", "D1. Tags/Labels"),
    Capability.LOCK_TAG: CapabilityInfo("Lock/protect tag data", "D1. Tags/Labels"),
    Capability.SET_USER_RATING: CapabilityInfo("Set user rating", "D2. Ratings"),
    Capability.SET_CRITIC_RATING: CapabilityInfo("Set critic rating", "D2. Ratings"),
    Capability.EDIT_TITLE: CapabilityInfo("Edit title", "D3. Text Metadata"),
    Capability.EDIT_SORT_TITLE: CapabilityInfo("Edit sort title", "D3. Text Metadata"),
    Capability.EDIT_SUMMARY: CapabilityInfo("Edit description/overview", "D3. Text Metadata"),
    Capability.EDIT_YEAR: CapabilityInfo("Edit year", "D3. Text Metadata"),
    Capability.UPLOAD_POSTER: CapabilityInfo("Upload poster", "E1. Poster/Backdrop Upload"),
    Capability.UPLOAD_BACKDROP: CapabilityInfo("Upload backdrop", "E1. Poster/Backdrop Upload"),
    Capability.UPLOAD_LOGO: CapabilityInfo("Upload logo", "E1. Poster/Backdrop Upload"),
    Capability.UPLOAD_BANNER: CapabilityInfo("Upload banner", "E1. Poster/Backdrop Upload"),
    Capability.UPLOAD_OVERLAY: CapabilityInfo("Upload overlay/composite", "E1. Poster/Backdrop Upload"),
    Capability.FIND_POSTER_ASSET: CapabilityInfo("Find poster in asset folder", "E2. Asset Discovery"),
    Capability.FIND_BACKDROP_ASSET: CapabilityInfo("Find backdrop in asset folder", "E2. Asset Discovery"),
    Capability.FIND_LOGO_ASSET: CapabilityInfo("Find logo in asset folder", "E2. Asset Discovery"),
    Capability.VALIDATE_ASSET: CapabilityInfo("Validate asset exists", "E2. Asset Discovery"),
    Capability.UPLOAD_THEME_SONG: CapabilityInfo("Upload theme song", "E3. Theme Media"),
    Capability.UPLOAD_THEME_VIDEO: CapabilityInfo("Upload theme video", "E3. Theme Media"),
    Capability.BATCH_TAGS: CapabilityInfo("Apply tags to multiple items", "F1. Batch Operations"),
    Capability.BATCH_RATINGS: CapabilityInfo("Apply ratings to multiple items", "F1. Batch Operations"),
    Capability.BATCH_METADATA: CapabilityInfo("Apply metadata to filtered set", "F1. Batch Operations"),
    Capability.BUILDER_ADD_ITEMS: CapabilityInfo("Add items (from builders)", "F2. Collection-Based Operations"),
    Capability.BUILDER_REMOVE_ITEMS: CapabilityInfo("Remove items from collection", "F2. Collection-Based Operations"),
    Capability.BUILDER_REPLACE_ITEMS: CapabilityInfo("Replace collection contents", "F2. Collection-Based Operations"),
    Capability.CREATE_PLAYLIST: CapabilityInfo("Create playlist", "G1. Create/Manage Playlists"),
    Capability.GET_PLAYLIST: CapabilityInfo("Get playlist by ID", "G1. Create/Manage Playlists"),
    Capability.ADD_PLAYLIST_ITEMS: CapabilityInfo("Add items to playlist", "G1. Create/Manage Playlists"),
    Capability.REMOVE_PLAYLIST_ITEMS: CapabilityInfo("Remove items from playlist", "G1. Create/Manage Playlists"),
    Capability.DELETE_PLAYLIST: CapabilityInfo("Delete playlist", "G1. Create/Manage Playlists"),
    Capability.PARSE_FILTER_EXPRESSION: CapabilityInfo("Parse filter expression (split)", "H1. Text Parsing"),
    Capability.PARSE_RELATIVE_DATE: CapabilityInfo("Parse relative date", "H1. Text Parsing"),
    Capability.PARSE_QUERY_STRING: CapabilityInfo("Parse query string", "H1. Text Parsing"),
    Capability.SEND_NOTIFICATION: CapabilityInfo("Send notification", "H2. Notifications"),
    Capability.NOTIFY_DELETION: CapabilityInfo("Notify item deletion", "H2. Notifications"),
    Capability.GET_RATING_KEY: CapabilityInfo("Get rating key", "H3. ID Resolution"),
    Capability.GET_ACTOR_ID: CapabilityInfo("Get actor ID", "H3. ID Resolution"),
    Capability.GET_PROVIDER_IDS: CapabilityInfo("Get provider IDs (TMDb, IMDb, etc)", "H3. ID Resolution"),
}


@dataclass(frozen=True)
class CapabilityStatus:
    support: Support
    detail: str = ""

    @property
    def supported(self) -> bool:
        return self.support is not Support.NONE


class CapabilityMatrix:
    """Complete support declaration for one media server type."""

    def __init__(self, declared):
        missing = [capability.value for capability in Capability if capability not in declared]
        unknown = [key for key in declared if not isinstance(key, Capability)]
        if missing or unknown:
            parts = []
            if missing:
                parts.append(f"missing {', '.join(missing)}")
            if unknown:
                parts.append("unknown " + ", ".join(repr(key) for key in unknown))
            raise ValueError(f"Capability matrix is incomplete: {'; '.join(parts)}")
        self._declared = {capability: declared[capability] for capability in Capability}

    def get(self, capability: Capability) -> CapabilityStatus:
        if not isinstance(capability, Capability):
            raise TypeError(f"Expected a Capability, got {capability!r}")
        return self._declared[capability]

    def support(self, capability: Capability) -> Support:
        return self.get(capability).support

    def supports(self, capability: Capability) -> bool:
        return self.get(capability).supported

    def __iter__(self):
        return iter(self._declared)

    def items(self):
        return self._declared.items()


def _plex_capabilities() -> CapabilityMatrix:
    declared = {capability: CapabilityStatus(Support.FULL) for capability in Capability}
    declared[Capability.SMART_COLLECTION_WORKAROUND] = CapabilityStatus(Support.NONE, "Not applicable. Plex creates native smart collections.")
    declared[Capability.TEST_FILTER] = CapabilityStatus(Support.FULL, "preview")
    return CapabilityMatrix(declared)


PLEX_CAPABILITIES = _plex_capabilities()


class MediaServer(ABC):
    """Connection settings and the capability matrix for one server."""

    type_name = ""
    type_label = ""

    def __init__(self, url, token, timeout=60, verify_ssl=None, db_cache=None, name=None):
        self.url = url
        self.token = token
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.db_cache = db_cache
        self.name = name

    @property
    def display_name(self) -> str:
        return self.name or self.type_label or self.type_name

    @property
    @abstractmethod
    def capabilities(self) -> CapabilityMatrix:
        """Return the matrix for this server. Implementations should return a shared instance."""

    def support(self, capability: Capability) -> Support:
        return self.capabilities.support(capability)

    def supports(self, capability: Capability) -> bool:
        return self.capabilities.supports(capability)

    def require(self, capability: Capability) -> CapabilityStatus:
        """Return the status when the server can perform the capability.

        Partial support is allowed. The caller reads ``detail`` for the limit.
        Unsupported capabilities raise ``Failed`` before a backend call is made.
        """
        status = self.capabilities.get(capability)
        if status.support is Support.NONE:
            detail = f" ({status.detail})" if status.detail else ""
            raise Failed(f"{self.display_name} does not support {capability.label}{detail}")
        return status


class PlexMediaServer(MediaServer):
    type_name = "plex"
    type_label = "Plex"

    @property
    def capabilities(self) -> CapabilityMatrix:
        return PLEX_CAPABILITIES

    @classmethod
    def from_config(cls, plex_config, name=None):
        """Build a server from the resolved ``plex:`` block. This does not open a connection."""
        timeout = plex_config["timeout"] if "timeout" in plex_config and plex_config["timeout"] is not None else 60
        return cls(
            url=plex_config["url"],
            token=plex_config["token"],
            timeout=timeout,
            verify_ssl=plex_config.get("verify_ssl"),
            db_cache=plex_config.get("db_cache"),
            name=name,
        )


_SERVER_CLASSES = {PlexMediaServer.type_name: PlexMediaServer}


def register_media_server(server_class):
    """Register a media server class so config type names can construct it."""
    _SERVER_CLASSES[server_class.type_name] = server_class
    return server_class


def media_server_class(type_name):
    """Return the media server class for a config type name."""
    try:
        return _SERVER_CLASSES[str(type_name).lower()]
    except KeyError:
        supported = ", ".join(sorted(_SERVER_CLASSES))
        raise Failed(f"Media server type '{type_name}' is not supported. Options: {supported}") from None


def build_media_server(name, data):
    """Build a named server from one ``media_servers`` entry. This does not open a connection."""
    if not isinstance(data, dict):
        raise Failed(f"Config Error: media_servers.{name} must be a dictionary")
    server_type = str(data.get("type") or "").strip().lower()
    if not server_type:
        raise Failed(f"Config Error: media_servers.{name} requires type")
    url = data.get("url")
    token = data.get("token")
    if not url or not str(url).strip():
        raise Failed(f"Config Error: media_servers.{name} requires url")
    if not token or not str(token).strip():
        raise Failed(f"Config Error: media_servers.{name} requires token")
    timeout = 60 if data.get("timeout") is None else data.get("timeout")
    if isinstance(timeout, bool) or not isinstance(timeout, int):
        raise Failed(f"Config Error: media_servers.{name} timeout must be an integer")
    payload = {
        "url": str(url).strip().rstrip("/"),
        "token": token,
        "timeout": timeout,
        "verify_ssl": data.get("verify_ssl"),
        "db_cache": data.get("db_cache"),
    }
    if server_type == "silo":
        from modules.silo import SiloMediaServer

        return SiloMediaServer.from_config(payload, name=str(name), profile_id=data.get("profile_id"))
    if server_type in ("jellyfin", "emby"):
        from modules.mediabrowser import EmbyMediaServer, JellyfinMediaServer

        server_class = JellyfinMediaServer if server_type == "jellyfin" else EmbyMediaServer
        return server_class.from_config(payload, name=str(name), user_id=data.get("user"))
    if server_type == "plex":
        return PlexMediaServer.from_config(payload, name=str(name))
    media_server_class(server_type)
    raise Failed(f"Media server type '{server_type}' cannot be built from media_servers")
