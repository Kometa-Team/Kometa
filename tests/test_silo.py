"""Silo media server client, capability matrix, and library operations."""

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

import modules.builder  # noqa: F401 — pre-import to break circular deps
import modules.silo as silo_module
from modules.media_server import Capability, Support, build_media_server, media_server_class
from modules.silo import SILO_CAPABILITIES, Silo, SiloClient, SiloCollection, SiloItem, SiloMediaServer, _SiloSection, api_base
from modules.util import Failed
from tests.conftest import FakeLogger, FakeResponse

silo_module.logger = FakeLogger()


class FakeSession:
    def __init__(self, responses):
        self.headers = {}
        self.verify = True
        self.calls = []
        self.responses = list(responses)

    def request(self, method, url, params=None, json=None, headers=None, timeout=None):
        self.calls.append({"method": method, "url": url, "params": params, "json": json, "headers": headers, "timeout": timeout})
        return self.responses.pop(0)


def _server(**overrides):
    values = {"url": "http://silo:8090", "token": "token", "name": "Shelf", "profile_id": "profile"}
    values.update(overrides)
    return SiloMediaServer(**values)


def _library(client, **overrides):
    library = Silo.__new__(Silo)
    library.server = overrides.get("server") or _server()
    library.client = client
    library.library_id = "lib-1"
    library.is_movie = True
    library.is_show = False
    library.type = "Movie"
    library.name = "Films"
    library.stats = {"deleted": 0}
    library.config = type("Config", (), {"notify": lambda *args, **kwargs: None, "notify_delete": lambda *args, **kwargs: None})()
    library.filter_attr_cache = {}
    library.movie_rating_key_map = {}
    library.show_rating_key_map = {}
    library.imdb_rating_key_map = {}
    library.movie_map = {}
    library.show_map = {}
    library.imdb_map = {}
    library.plex_map_levels = set()
    library._all_items = []
    library.Plex = _SiloSection("movie", "en", library.library_id, "Films")
    for name, value in overrides.items():
        setattr(library, name, value)
    return library


def test_silo_is_a_registered_server_with_scored_capabilities():
    assert media_server_class("silo") is SiloMediaServer
    assert {capability for capability, _status in SILO_CAPABILITIES.items()} == set(Capability)
    none = {
        Capability.SMART_COLLECTION_WORKAROUND,
        Capability.DELETE_ITEM,
        Capability.ADD_TAG,
        Capability.REMOVE_TAG,
        Capability.GET_ITEM_LABELS,
        Capability.UPLOAD_POSTER,
        Capability.UPLOAD_BACKDROP,
        Capability.UPLOAD_LOGO,
        Capability.UPLOAD_OVERLAY,
        Capability.UPLOAD_THEME_SONG,
        Capability.UPLOAD_THEME_VIDEO,
        Capability.BATCH_TAGS,
        Capability.CREATE_PLAYLIST,
        Capability.GET_PLAYLIST,
        Capability.ADD_PLAYLIST_ITEMS,
        Capability.REMOVE_PLAYLIST_ITEMS,
        Capability.DELETE_PLAYLIST,
    }
    partial = {
        Capability.GET_COLLECTION_BY_NAME,
        Capability.SYNC_COLLECTION,
        Capability.DELETE_COLLECTION,
        Capability.VALIDATE_FILTER_SYNTAX,
        Capability.PARSE_SMART_FILTER,
        Capability.SYNC_TAGS,
        Capability.SET_USER_RATING,
        Capability.UPLOAD_BANNER,
        Capability.FIND_POSTER_ASSET,
        Capability.FIND_BACKDROP_ASSET,
        Capability.FIND_LOGO_ASSET,
        Capability.BATCH_RATINGS,
        Capability.BATCH_METADATA,
        Capability.BUILDER_REPLACE_ITEMS,
    }
    assert {capability for capability in Capability if SILO_CAPABILITIES.support(capability) is Support.NONE} == none
    assert {capability for capability in Capability if SILO_CAPABILITIES.support(capability) is Support.PARTIAL} == partial
    server = _server()
    with pytest.raises(Failed, match="No API"):
        server.require(Capability.DELETE_ITEM)
    assert server.require(Capability.SYNC_TAGS).detail == "Genre, studio, network, and country"
    assert server.require(Capability.TEST_FILTER).detail == "preview"


def test_build_media_server_reads_a_silo_block_without_connecting():
    server = build_media_server(
        "Shelf",
        {"type": "silo", "url": "http://silo:8090/", "token": "token", "timeout": 15, "verify_ssl": False, "profile_id": "home"},
    )
    assert isinstance(server, SiloMediaServer)
    assert server.url == "http://silo:8090"
    assert server.timeout == 15
    assert server.profile_id == "home"
    assert api_base(server.url) == "http://silo:8090/api/v2"
    assert api_base("http://silo:8090/api/v2") == "http://silo:8090/api/v2"
    with pytest.raises(Failed, match="timeout must be an integer"):
        build_media_server("Shelf", {"type": "silo", "url": "http://silo", "token": "token", "timeout": True})
    with pytest.raises(Failed, match="not supported"):
        build_media_server("Shelf", {"type": "emby", "url": "http://silo", "token": "token"})


def test_client_pages_catalog_results_and_quotes_collection_ids():
    session = FakeSession(
        [
            FakeResponse({"items": [{"content_id": "movie:one"}], "page": {"has_more": True, "next_cursor": "cursor-2"}}),
            FakeResponse({"items": [{"content_id": "movie:two"}], "page": {"has_more": False}}),
            FakeResponse({"id": "col 1", "title": "Heat"}, headers={"ETag": '"v1"'}),
            FakeResponse(None, status_code=204, content=b""),
        ]
    )
    client = SiloClient(_server(), session=session)

    items = client.browse("lib-1", media_type="movie")
    assert [item["content_id"] for item in items] == ["movie:one", "movie:two"]
    assert session.calls[1]["params"]["cursor"] == "cursor-2"
    assert session.calls[0]["url"] == "http://silo:8090/api/v2/catalog"
    assert session.headers["Authorization"] == "Bearer token"
    assert session.headers["X-Profile-Id"] == "profile"

    created, etag = client.create_collection({"title": "Heat"})
    assert created["id"] == "col 1"
    assert etag == '"v1"'
    client.add_collection_item("col 1", "movie:heat-1995", position=3)
    assert session.calls[3]["method"] == "PUT"
    assert session.calls[3]["url"].endswith("/admin/collections/col%201/items/movie%3Aheat-1995")
    assert session.calls[3]["json"] == {"position": 3}


def test_library_builds_collections_and_refuses_missing_capabilities():
    session = FakeSession(
        [
            FakeResponse({"items": [], "page": {"has_more": False}}),
            FakeResponse({"items": [], "page": {"has_more": False}}),
            FakeResponse({"id": "col-1", "title": "Heat", "collection_type": "manual"}, headers={"ETag": '"a"'}),
            FakeResponse({"ok": True}),
            FakeResponse(None, status_code=204, content=b""),
        ]
    )
    deleted = []
    library = _library(SiloClient(_server(), session=session))
    library.config = SimpleNamespace(notify_delete=lambda message, **kwargs: deleted.append(message))

    with pytest.raises(Failed, match="Collection Heat not found"):
        library.get_collection("Heat")
    created = library.create_blank_collection("Heat")
    assert isinstance(created, SiloCollection)
    assert created.id == "col-1"
    assert session.calls[2]["json"]["collection_type"] == "manual"
    assert session.calls[2]["json"]["library_id"] == "lib-1"

    item = SiloItem({"content_id": "movie:heat-1995", "title": "Heat", "tmdb_id": "550"}, library)
    assert item.tmdb_id == 550
    assert item.ratingKey == "movie:heat-1995"
    library.alter_collection([item], created)
    assert session.calls[3]["url"].endswith("/items/movie%3Aheat-1995")

    library.delete_collection(created)
    assert session.calls[4]["method"] == "DELETE"
    assert session.calls[4]["headers"]["If-Match"] == '"a"'
    assert library.stats["deleted"] == 1
    assert deleted == ["Collection Heat deleted"]

    with pytest.raises(Failed, match="does not support"):
        library.upload_poster(item, "poster.jpg")
    with pytest.raises(Failed, match="cannot upload image bytes"):
        library.image_update(item, "banner.jpg", poster=False, image_type="banner")
    with pytest.raises(Failed, match="query documents"):
        library.fetchItems("/library/sections/1/all?type=1")
    with pytest.raises(Failed, match="does not support"):
        library.create_playlist("Queue")
    with pytest.raises(Failed, match="not available"):
        library.Plex.listFilters("movie")


def test_get_all_loads_provider_ids_and_keeps_string_rating_keys():
    session = FakeSession(
        [
            FakeResponse({"items": [{"content_id": "movie:heat-1995", "title": "Heat"}], "page": {"has_more": False}}),
            FakeResponse({"content_id": "movie:heat-1995", "title": "Heat", "tmdb_id": 550, "imdb_id": "tt0113277"}),
        ]
    )
    library = _library(SiloClient(_server(), session=session))
    items = library.get_all()
    assert items[0].tmdb_id == 550
    assert items[0].imdb_id == "tt0113277"
    assert session.calls[1]["url"].endswith("/catalog/items/movie%3Aheat-1995")
    library.map_guids(items)
    assert library.movie_map[550] == ["movie:heat-1995"]
    assert library.get_ids(items[0]) == (550, None, "tt0113277")

    added = _library(
        SiloClient(
            _server(),
            session=FakeSession([FakeResponse({"items": [{"content_id": "movie:new", "title": "New"}], "page": {}})]),
        )
    )
    cutoff = datetime(2026, 10, 1, tzinfo=timezone.utc)
    found = added.get_items_added_since(None, cutoff)
    assert found[0].ratingKey == "movie:new"
    assert added.client.session.calls[0]["json"]["groups"][0]["rules"][0]["value"] == cutoff.isoformat()
