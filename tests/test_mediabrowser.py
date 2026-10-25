"""Jellyfin and Emby media server client, capability matrix, and library operations."""

from datetime import datetime, timezone

import pytest

import modules.builder  # noqa: F401 — pre-import to break circular deps
import modules.mediabrowser as browser_module
from modules.media_server import Capability, Support, build_media_server, media_server_class
from modules.mediabrowser import EMBY_CAPABILITIES, JELLYFIN_CAPABILITIES, Emby, EmbyMediaServer, Jellyfin, JellyfinMediaServer, MediaBrowserClient, MediaBrowserCollection, MediaBrowserItem
from modules.util import Failed
from tests.conftest import FakeLogger, FakeResponse

browser_module.logger = FakeLogger()


class FakeSession:
    def __init__(self, responses):
        self.headers = {}
        self.verify = True
        self.calls = []
        self.responses = list(responses)

    def request(self, method, url, params=None, json=None, data=None, headers=None, timeout=None):
        self.calls.append({"method": method, "url": url, "params": params, "json": json, "data": data, "headers": headers, "timeout": timeout})
        return self.responses.pop(0)


def _server(kind="jellyfin", **overrides):
    values = {"url": "http://media:8096", "token": "token", "name": "Cinema", "user_id": "user-1"}
    values.update(overrides)
    return JellyfinMediaServer(**values) if kind == "jellyfin" else EmbyMediaServer(**values)


def _library(client, kind="jellyfin", **overrides):
    library_class = Jellyfin if kind == "jellyfin" else Emby
    library = library_class.__new__(library_class)
    library.server = overrides.get("server") or _server(kind)
    library.client = client
    library.url = library.server.url
    library.library_id = "lib-1"
    library.is_movie = True
    library.is_show = False
    library.type = "Movie"
    library.name = "Films"
    library.timeout = library.server.timeout
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
    return library


def test_jellyfin_and_emby_are_registered_with_scored_capabilities():
    assert media_server_class("jellyfin") is JellyfinMediaServer
    assert media_server_class("emby") is EmbyMediaServer
    for matrix in (JELLYFIN_CAPABILITIES, EMBY_CAPABILITIES):
        assert {capability for capability, _status in matrix.items()} == set(Capability)
        assert matrix.support(Capability.UPLOAD_POSTER) is Support.FULL
        assert matrix.support(Capability.UPLOAD_OVERLAY) is Support.FULL
        assert matrix.support(Capability.CREATE_PLAYLIST) is Support.FULL
        assert matrix.support(Capability.GET_ITEM_LABELS) is Support.FULL
        assert matrix.support(Capability.NATIVE_SMART_COLLECTIONS) is Support.NONE
        assert matrix.support(Capability.PARSE_SMART_FILTER) is Support.NONE
        assert matrix.support(Capability.UPLOAD_THEME_SONG) is Support.NONE
    server = build_media_server("Cinema", {"type": "jellyfin", "url": "http://media:8096/", "token": "token", "user": "user-9"})
    assert isinstance(server, JellyfinMediaServer)
    assert server.url == "http://media:8096"
    assert server.user_id == "user-9"
    emby = build_media_server("Theater", {"type": "emby", "url": "http://emby:8096", "token": "token"})
    assert isinstance(emby, EmbyMediaServer)
    assert emby.user_id is None
    with pytest.raises(Failed, match="not supported"):
        build_media_server("Other", {"type": "kodi", "url": "http://media", "token": "token"})


def test_client_pages_items_and_picks_an_administrator():
    session = FakeSession(
        [
            FakeResponse([{"Id": "guest", "Policy": {"IsAdministrator": False}}, {"Id": "admin", "Policy": {"IsAdministrator": True}}]),
            FakeResponse({"Items": [{"Id": "movie-1"}], "TotalRecordCount": 2}),
            FakeResponse({"Items": [{"Id": "movie-2"}], "TotalRecordCount": 2}),
        ]
    )
    client = MediaBrowserClient(_server(user_id=None), session=session)
    rows = client.items({"includeItemTypes": "Movie"}, limit=None)
    assert client.user_id == "admin"
    assert [row["Id"] for row in rows] == ["movie-1", "movie-2"]
    assert session.calls[1]["params"]["startIndex"] == 0
    assert session.calls[2]["params"]["startIndex"] == 1
    assert session.calls[2]["params"]["userId"] == "admin"
    assert session.headers["X-Emby-Token"] == "token"


def test_library_builds_a_collection_and_uploads_images(tmp_path):
    poster = tmp_path / "poster.jpg"
    poster.write_bytes(b"jpeg")
    session = FakeSession(
        [
            FakeResponse({"Items": [], "TotalRecordCount": 0}),
            FakeResponse({"Id": "col-1"}),
            FakeResponse({"Id": "col-1", "Name": "Heat", "Type": "BoxSet"}),
            FakeResponse(None, status_code=204, content=b""),
            FakeResponse(None, status_code=204, content=b""),
            FakeResponse(None, status_code=204, content=b""),
        ]
    )
    library = _library(MediaBrowserClient(_server(), session=session))
    item = MediaBrowserItem({"Id": "movie-1", "Name": "Heat", "Type": "Movie", "ProviderIds": {"Tmdb": "550", "Imdb": "tt0113277"}}, library)

    created = library.create_blank_collection("Heat")
    assert isinstance(created, MediaBrowserCollection)
    assert created.ratingKey == "col-1"
    assert session.calls[1]["url"].endswith("/Collections")
    assert session.calls[1]["params"]["name"] == "Heat"
    assert session.calls[1]["params"]["parentId"] == "lib-1"

    library.alter_collection([item], created)
    assert session.calls[3]["method"] == "POST"
    assert session.calls[3]["url"].endswith("/Collections/col-1/Items")
    assert session.calls[3]["params"]["ids"] == "movie-1"

    library.upload_poster(item, str(poster))
    assert session.calls[4]["method"] == "POST"
    assert session.calls[4]["url"].endswith("/Items/movie-1/Images/Primary")
    assert session.calls[4]["data"] == b"jpeg"
    assert session.calls[4]["headers"]["Content-Type"] == "image/jpeg"

    remote = "https://image.tmdb.org/poster.jpg"
    library.upload_poster(item, remote, url=True)
    assert session.calls[5]["url"].endswith("/Items/movie-1/RemoteImages/Download")
    assert session.calls[5]["params"] == {"type": "Primary", "imageUrl": remote}

    with pytest.raises(Failed, match="No dynamic collection filter"):
        library.create_smart_collection("Heat", "movie", "?type=1", False)


def test_provider_ids_playlist_entries_and_added_since(monkeypatch):
    monkeypatch.setattr(browser_module, "PAGE_SIZE", 1)
    session = FakeSession(
        [
            FakeResponse({"Items": [{"Id": "movie-1", "Name": "Heat", "Type": "Movie", "ProviderIds": {"Tmdb": "550", "Imdb": "tt0113277"}, "DateCreated": "2026-10-02T00:00:00Z"}], "TotalRecordCount": 1}),
            FakeResponse({"Id": "list-1"}),
            FakeResponse({"Id": "list-1", "Name": "Queue", "Type": "Playlist"}),
            FakeResponse({"Items": [{"Id": "movie-1", "PlaylistItemId": "entry-1", "Name": "Heat", "Type": "Movie"}]}),
            FakeResponse(None, status_code=204, content=b""),
            FakeResponse({"Items": [{"Id": "movie-1", "DateCreated": "2026-10-02T00:00:00Z"}], "TotalRecordCount": 2}),
            FakeResponse({"Items": [{"Id": "movie-old", "DateCreated": "2026-09-01T00:00:00Z"}], "TotalRecordCount": 2}),
        ]
    )
    library = _library(MediaBrowserClient(_server(), session=session))
    items = library.get_all()
    assert items[0].tmdb_id == 550
    assert items[0].imdb_id == "tt0113277"
    assert library.get_ids(items[0]) == (550, None, "tt0113277")
    library.map_guids(items)
    assert library.movie_map[550] == ["movie-1"]

    playlist = library.create_playlist("Queue", [items[0]])
    playlist.removeItems(items)
    assert session.calls[4]["method"] == "DELETE"
    assert session.calls[4]["params"]["entryIds"] == "entry-1"

    added = library.get_items_added_since(None, datetime(2026, 10, 1, tzinfo=timezone.utc))
    assert [item.ratingKey for item in added] == ["movie-1"]
    assert session.calls[5]["params"]["startIndex"] == 0
    assert session.calls[6]["params"]["startIndex"] == 1


def test_emby_library_edits_tags_and_refuses_a_music_library():
    session = FakeSession(
        [
            FakeResponse({"Id": "movie-1", "Name": "Heat", "Type": "Movie", "Tags": ["Old"], "LockedFields": []}),
            FakeResponse({"Id": "movie-1"}),
        ]
    )
    library = _library(MediaBrowserClient(_server("emby"), session=session), kind="emby")
    item = MediaBrowserItem({"Id": "movie-1", "Name": "Heat", "Type": "Movie", "Tags": ["Old"], "LockedFields": []}, library)
    assert library.edit_tags("label", item, add_tags=["Kometa"], do_print=False) == "Old, Kometa"
    assert session.calls[1]["json"]["Tags"] == ["Old", "Kometa"]
    assert "Tags" in session.calls[1]["json"]["LockedFields"]
    assert item.tags == ["Old", "Kometa"]
    with pytest.raises(Failed, match="Emby Error: Library type 'music'"):
        browser_module.kometa_library_type("music", "Emby")
