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

    def request(self, method, url, params=None, json=None, headers=None, timeout=None, files=None):
        self.calls.append({"method": method, "url": url, "params": params, "json": json, "headers": headers, "timeout": timeout, "files": files, "profile": self.headers.get("X-Profile-Id")})
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
    library.timeout = library.server.timeout
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


def test_silo_skips_plex_maintenance_operations():
    from collections import defaultdict

    from modules.library import Library

    methods = [
        "notify",
        "notify_delete",
        "_upload_image",
        "upload_poster",
        "image_update",
        "reload",
        "edit_tags",
        "item_labels",
        "find_poster_url",
        "item_posters",
        "get_all",
        "get_items_added_since",
        "cached_item_subitems",
        "get_ids",
    ]
    shelf = type("Shelf", (Library,), {name: (lambda *args, **kwargs: None) for name in methods})
    params = defaultdict(lambda: None)
    params.update(
        {
            "name": "Movies",
            "mapping_name": "Movies",
            "collection_files": [],
            "metadata_files": [],
            "overlay_files": [],
            "skip_library": False,
            "asset_depth": 0,
            "asset_directory": [],
            "default_dir": "config",
            "run_order": ["operations", "metadata", "collections", "overlays"],
        }
    )
    library = shelf(SimpleNamespace(Cache=None, default_dir="config"), params)

    assert library.clean_bundles is False
    assert library.empty_trash is False
    assert library.optimize is False


def test_silo_is_a_registered_server_with_scored_capabilities():
    assert media_server_class("silo") is SiloMediaServer
    assert {capability for capability, _status in SILO_CAPABILITIES.items()} == set(Capability)
    none = {
        Capability.SMART_COLLECTION_WORKAROUND,
        Capability.DELETE_ITEM,
        Capability.ADD_TAG,
        Capability.REMOVE_TAG,
        Capability.GET_ITEM_LABELS,
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
        Capability.UPLOAD_POSTER,
        Capability.UPLOAD_BACKDROP,
        Capability.UPLOAD_LOGO,
        Capability.UPLOAD_OVERLAY,
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
        build_media_server("Shelf", {"type": "kodi", "url": "http://silo", "token": "token"})


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


def test_missing_profile_lists_users_and_profiles():
    problem = {"title": "Not found", "status": 404, "detail": "Profile not found"}
    session = FakeSession(
        [
            FakeResponse(problem, status_code=404),
            FakeResponse({"items": [{"id": "12", "username": "alice"}, {"id": "13", "username": "bob"}], "page": {"has_more": False}}),
            FakeResponse({"items": [{"id": "34", "name": "Alice", "is_primary": True}], "page": {"has_more": False}}),
            FakeResponse({"items": [{"id": "34", "name": "Alice"}, {"id": "35", "name": "Kids"}], "page": {"has_more": False}}),
            FakeResponse({"items": [{"id": "40", "name": "Bob"}], "page": {"has_more": False}}),
        ]
    )
    client = SiloClient(_server(profile_id="999"), session=session)

    with pytest.raises(Failed) as caught:
        client.list_libraries()

    message = str(caught.value)
    assert "GET /libraries returned 404" in message
    assert "Profile not found for profile_id '999'" in message
    assert 'user 12 (alice): profile 34 "Alice" primary, profile 35 "Kids"' in message
    assert 'user 13 (bob): profile 40 "Bob"' in message
    assert session.calls[0]["profile"] == "999"
    assert session.calls[1]["url"].endswith("/admin/users")
    assert session.calls[1]["profile"] is None
    assert session.calls[2]["url"].endswith("/profiles")
    assert session.calls[3]["url"].endswith("/admin/users/12/profiles")
    assert session.calls[4]["url"].endswith("/admin/users/13/profiles")
    assert session.headers["X-Profile-Id"] == "999"


def test_missing_profile_falls_back_to_the_signed_in_account():
    session = FakeSession(
        [
            FakeResponse({"detail": "Profile not found"}, status_code=404),
            FakeResponse({"detail": "Forbidden"}, status_code=403),
            FakeResponse({"id": "12", "username": "alice"}),
            FakeResponse({"items": [{"id": "34", "name": "Alice", "is_primary": True}], "page": {"has_more": False}}),
        ]
    )
    client = SiloClient(_server(profile_id="999"), session=session)

    with pytest.raises(Failed) as caught:
        client.list_libraries()

    assert 'user 12 (alice): profile 34 "Alice" primary' in str(caught.value)
    assert session.calls[2]["url"].endswith("/account/me")
    assert session.calls[3]["url"].endswith("/profiles")
    assert session.calls[2]["profile"] is None


def test_other_not_found_errors_do_not_list_profiles():
    session = FakeSession([FakeResponse({"detail": "Collection not found"}, status_code=404)])
    client = SiloClient(_server(), session=session)

    with pytest.raises(Failed, match="Collection not found"):
        client.get_collection("missing")

    assert len(session.calls) == 1


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


def test_publish_image_puts_the_file_on_transfer(monkeypatch, tmp_path):
    image = tmp_path / "Heat Poster.png"
    image.write_bytes(b"png-bytes")
    captured = {}

    class Response:
        status_code = 200
        text = "https://transfer.kometa.wiki/token/kometa-poster.png\n"

    def fake_put(url, data=None, headers=None, timeout=None):
        captured["url"] = url
        captured["body"] = data.read()
        captured["headers"] = headers
        captured["timeout"] = timeout
        return Response()

    monkeypatch.setattr(silo_module.requests, "put", fake_put)
    assert silo_module.publish_image(image, filename="kometa-poster.png", timeout=12) == "https://transfer.kometa.wiki/token/kometa-poster.png"
    assert captured["url"] == "https://transfer.kometa.wiki/kometa-poster.png"
    assert captured["body"] == b"png-bytes"
    assert captured["headers"] == {"Max-Days": "7"}
    assert "Authorization" not in captured["headers"]
    assert captured["timeout"] == 12

    missing = Response()
    missing.status_code = 500
    missing.text = "nope"
    monkeypatch.setattr(silo_module.requests, "put", lambda *args, **kwargs: missing)
    with pytest.raises(Failed, match="transfer.kometa.wiki returned 500"):
        silo_module.publish_image(image)


def test_local_poster_is_published_then_applied(monkeypatch, tmp_path):
    poster = tmp_path / "overlay.jpg"
    poster.write_bytes(b"jpeg")
    published = "https://transfer.kometa.wiki/abc/overlay.jpg"
    monkeypatch.setattr(silo_module, "publish_image", lambda location, filename=None, timeout=60: published)
    session = FakeSession([FakeResponse({"content_id": "movie:heat-1995"})])
    library = _library(SiloClient(_server(), session=session))
    item = SiloItem({"content_id": "movie:heat-1995", "title": "Heat"}, library)

    assert library.upload_poster(item, str(poster)) is True
    assert session.calls[0]["method"] == "POST"
    assert session.calls[0]["url"].endswith("/admin/items/movie%3Aheat-1995/images/apply")
    assert session.calls[0]["json"] == {"type": "poster", "original_url": published}
    assert session.calls[0]["files"] is None

    overlay = SimpleNamespace(is_poster=True, is_background=False, is_logo=False, is_url=False, location=str(poster))
    session.responses.append(FakeResponse({"content_id": "movie:heat-1995"}))
    assert library._upload_image(item, overlay) is True
    assert session.calls[1]["json"]["original_url"] == published


def test_remote_poster_is_given_to_silo_without_publishing(monkeypatch):
    def fail_publish(*_args, **_kwargs):
        raise AssertionError("local publish")

    monkeypatch.setattr(silo_module, "publish_image", fail_publish)
    session = FakeSession([FakeResponse({"ok": True}), FakeResponse({"ok": True})])
    library = _library(SiloClient(_server(), session=session))
    item = SiloItem({"content_id": "movie:heat-1995", "title": "Heat"}, library)
    remote = "https://image.tmdb.org/t/p/original/poster.jpg"

    library.upload_poster(item, remote, url=True)
    assert session.calls[0]["json"]["original_url"] == remote

    assert library.image_update(item, None, tmdb=("tmdb", remote)) == ("Reset", "TMDb", "Updated")
    assert session.calls[1]["json"] == {"type": "poster", "original_url": remote}
    assert library.image_update(item, None, tmdb=("lock", None)) == ("Lock", "Silo", "Failed")


def test_collection_artwork_uses_the_source_url_field(monkeypatch, tmp_path):
    poster = tmp_path / "collection.png"
    poster.write_bytes(b"png")
    published = "https://transfer.kometa.wiki/abc/collection.png"
    monkeypatch.setattr(silo_module, "publish_image", lambda location, filename=None, timeout=60: published)
    session = FakeSession([FakeResponse({"id": "col 1"}), FakeResponse({"id": "col 1"})])
    library = _library(SiloClient(_server(), session=session))
    collection = SiloCollection({"id": "col 1", "title": "Heat"})

    library.upload_poster(collection, str(poster))
    assert session.calls[0]["method"] == "PUT"
    assert session.calls[0]["url"].endswith("/admin/collections/col%201/poster")
    assert session.calls[0]["files"] == {"source_url": (None, published)}
    assert session.calls[0]["json"] is None

    library.upload_background(collection, "https://image.tmdb.org/backdrop.jpg", url=True)
    assert session.calls[1]["url"].endswith("/admin/collections/col%201/backdrop")
    assert session.calls[1]["files"]["source_url"] == (None, "https://image.tmdb.org/backdrop.jpg")
