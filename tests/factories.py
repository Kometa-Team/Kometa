"""Factories and small fakes for isolated builder, Plex and Requests method tests.

These bypass initialization intentionally. Constructor and lifecycle tests should
instantiate the real class instead.
"""

from types import SimpleNamespace
from typing import cast
from unittest.mock import MagicMock

from modules.builder import CollectionBuilder
from modules.plex import Plex
from modules.request import Requests
from tests.conftest import FakeLogger


def make_builder(**attrs) -> CollectionBuilder:
    """Create a minimal CollectionBuilder with ``__new__``."""
    builder = CollectionBuilder.__new__(CollectionBuilder)
    defaults = {
        "Type": "Collection",
        "builder_level": "movie",
        "playlist": False,
        "music_playlist": False,
        "music_playlist_smart": False,
        "smart_filter_result_type": None,
        "libraries": [],
        "ignore_imdb_ids": [],
        "ignore_ids": [],
        "missing_movies": [],
        "missing_parts": [],
        "missing_shows": [],
        "do_missing": True,
        "filters": [],
        "details": {"show_filtered": False, "show_unfiltered": False, "only_filter_missing": False},
        "filtered_keys": {},
        "found_items": [],
        "found_item_keys": set(),
        "do_report": False,
        "obj": None,
        "name": "Test Collection",
        "builders": [],
        "items": [],
        "mdb_list_arr_ids": None,
        "item_details": {},
        "asset_directory": None,
        "collection_asset_directory": None,
        "collection_assets_configured": False,
        "overlay": False,
        "radarr_details": {"add_existing": False, "upgrade_existing": False, "monitor_existing": False},
        "sonarr_details": {"add_existing": False, "upgrade_existing": False, "monitor_existing": False},
        "run_again_movies": [],
        "run_again_shows": [],
        "notification_additions": [],
        "notification_removals": [],
        "added_to_radarr": [],
        "added_to_sonarr": [],
        "collection_poster": None,
        "collection_background": None,
        "deleted": False,
        "created": True,
        "smart_label_collection": False,
        "check_filters": lambda item, display: True,
        "value_filters": [],
    }
    defaults.update(attrs)
    for key, value in defaults.items():
        setattr(builder, key, value)
    return builder


def make_plex(**attrs) -> Plex:
    """Create a minimal Plex instance with ``Plex.__new__``.

    Defaults provide enough for basic method calls.  Override any
    attribute via keyword arguments.

    Sets ``Plex.logger`` and ``plex_module.logger`` to FakeLogger.
    """
    import modules.plex as plex_module

    plex = Plex.__new__(Plex)

    # Required by Library base class
    plex.name = attrs.pop("name", "Test Library")
    plex.is_movie = attrs.pop("is_movie", True)
    plex.is_show = attrs.pop("is_show", False)
    plex.type = attrs.pop("type", "Movie")
    plex.cached_items = attrs.pop("cached_items", {})
    plex.filter_attr_cache = attrs.pop("filter_attr_cache", {})
    plex.collection_names = attrs.pop("collection_names", [])
    plex.collection_files = attrs.pop("collection_files", [])
    plex.stats = attrs.pop("stats", {"deleted": 0})
    plex.config = attrs.pop("config", SimpleNamespace(notify=MagicMock(), notify_delete=MagicMock()))

    # Required by Plex class
    plex.collection_asset_directory = attrs.pop("collection_asset_directory", [])
    plex.plex = attrs.pop("plex", None)
    plex.url = attrs.pop("url", "http://localhost:32400")
    plex.token = attrs.pop("token", "fake-token")
    plex.PlexServer = attrs.pop("PlexServer", MagicMock())
    plex.Plex = attrs.pop("Plex", MagicMock())
    plex.session = attrs.pop("session", MagicMock())
    plex.timeout = attrs.pop("timeout", 30)
    plex._language_choice_cache = attrs.pop("_language_choice_cache", {})

    # Apply any remaining overrides
    for key, value in attrs.items():
        setattr(plex, key, value)

    plex_module.logger = FakeLogger()
    return plex


def make_plex_item(
    rating_key: int = 1,
    title: str = "Test Item",
    year: int = 2023,
    **extras,
) -> MagicMock:
    """Return a MagicMock that looks like a Plex video object."""
    item = MagicMock()
    item.ratingKey = rating_key
    item.title = title
    item.year = year
    item.type = extras.pop("type", "movie")
    for key, value in extras.items():
        setattr(item, key, value)
    return item


class FakeImageResponse:
    """Minimal image HTTP response for get_image() tests."""

    def __init__(self, status_code=200, content_type="image/png", content=b"fake-png-bytes"):
        self.status_code = status_code
        self.headers = {"Content-Type": content_type}
        self.content = content


def make_requests() -> Requests:
    """Bare Requests instance without hitting the network or cloudscraper."""
    return Requests.__new__(Requests)


def make_image_requests():
    """Bare Requests instance with just the attributes get_image() touches, plus its get()/head() cast to MagicMock for mock-attribute access."""
    req = make_requests()
    req._image_url_cache = {}
    req.image_content_types = ["image/png", "image/jpeg", "image/webp"]
    req.get = MagicMock()
    req.head = MagicMock()
    return req, cast(MagicMock, req.get), cast(MagicMock, req.head)
