"""Silo media server client, capability matrix, and library operations."""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401 — pre-import to break circular deps
import modules.silo as silo_module
from modules.media_server import Capability, Support, build_media_server, media_server_class
from modules.silo import SILO_CAPABILITIES, Silo, SiloClient, SiloCollection, SiloItem, SiloMediaServer, _SiloSection, api_base
from modules.util import BuilderValidationError, CollectionNotFound, Failed
from tests.conftest import FakeLogger, FakeResponse

silo_module.logger = FakeLogger()


def test_silo_server_info_reads_reported_revision_without_inventing_os():
    client = SiloClient(_server())
    client.request = MagicMock(return_value=({"server_version": "6de6d5e5"}, {}))
    assert client.server_info() == {"name": client.server.display_name, "version": "6de6d5e5"}
    client.request.assert_called_once_with("GET", "/system/info")


def test_silo_library_connection_logs_remote_revision(monkeypatch):
    server = _server()
    monkeypatch.setattr(silo_module.Library, "__init__", lambda self, config, params: setattr(self, "server", server))
    logger = FakeLogger()
    monkeypatch.setattr(silo_module, "logger", logger)
    client = MagicMock()
    client.list_libraries.return_value = [{"id": "lib-1", "name": "Movies", "type": "movies"}]
    client.server_info.return_value = {"name": "Silo", "version": "revision"}
    Silo(None, {"name": "Movies"}, client=client)
    assert "Connected to server Silo version revision" in logger.info_messages
    assert "Operating system: not reported" in logger.info_messages


@pytest.fixture(autouse=True)
def skip_real_network_delays(monkeypatch):
    monkeypatch.setattr(silo_module, "_REQUEST_PACERS", {})
    clock = [0.0]
    monkeypatch.setattr(silo_module.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(silo_module.time, "sleep", lambda delay: clock.__setitem__(0, clock[0] + delay))
    return clock


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
    overrides.setdefault("pace_requests", True)
    values = {"url": "http://silo:8090", "token": "token", "name": "Shelf", "profile_id": "profile"}
    values.update(overrides)
    return SiloMediaServer(**values)


@pytest.mark.parametrize("configured,expected", [({}, False), ({"pace_requests": False}, False), ({"pace_requests": True}, True)])
def test_pacing_flag_is_opt_in_at_server_level(configured, expected):
    server = build_media_server("Shelf", {"type": "silo", "url": "http://silo:8090", "token": "token", **configured})
    assert server.pace_requests is expected
    session = FakeSession([FakeResponse({}), FakeResponse({})])
    client = SiloClient(server, session=session)
    assert (client._request_pacer is not None) is expected
    client.get_item("movie-1")
    client.get_item("movie-2")


@pytest.mark.parametrize("value", ["true", "false", 1, None])
def test_pacing_flag_requires_boolean(value):
    with pytest.raises(Failed, match="pace_requests must be a boolean"):
        build_media_server("Shelf", {"type": "silo", "url": "http://silo", "token": "token", "pace_requests": value})


def test_unpaced_requests_still_retry_429(monkeypatch):
    waits = []
    monkeypatch.setattr(silo_module.time, "sleep", waits.append)
    session = FakeSession([FakeResponse({}), FakeResponse({}, status_code=429, headers={"Retry-After": "2"}), FakeResponse({})])
    client = SiloClient(_server(pace_requests=False), session=session)
    client.get_item("movie-1")
    client.get_item("movie-2")
    assert waits == [2]
    assert len(session.calls) == 3


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


def test_silo_aspect_overlay_filters_use_track_metadata(monkeypatch):
    from modules import builder as builder_module
    from tests.factories import make_builder

    monkeypatch.setattr(builder_module, "logger", FakeLogger())
    library = _library(SiloClient(_server(), session=FakeSession([])))
    movie = SiloItem({"content_id": "movie-1", "title": "Academy", "type": "movie", "versions": [{"video_tracks": [{"aspect_ratio": "4:3"}]}]}, library)
    library._search_details = {movie.content_id: movie}
    builder = make_builder(library=library, overlay=True, Type="Overlay", filters=[], default_percent=50)
    builder._filters("filters", {"aspect.gt": 1.32, "aspect.lt": 1.34, "video_codec.not": "h264"})
    # Unknown codec fails even a negative filter; aspect itself matches.
    assert library.check_filters(movie, builder.filters[0][:2], None)
    assert not library.check_filters(movie, builder.filters[0], None)
    assert library.client.session.calls == []


def test_silo_technical_smart_filter_rebuilds_locally_and_preserves_sorted_order(monkeypatch):
    from modules.builder import CollectionBuilder

    monkeypatch.setattr("modules.builder.logger", FakeLogger())

    library = _library(SiloClient(_server(), session=FakeSession([])))
    data = {"smart_filter": {"all": {"aspect.gt": 1.3, "audio_codec.regex": "truehd"}, "sort_by": "rating_imdb.desc", "limit": 1}}
    methods = {"smart_filter": "smart_filter"}
    CollectionBuilder._adapt_local_smart_filter(library, data, methods)
    assert "smart_filter" not in data
    assert data["collection_order"] == "custom"
    library.get_all = lambda **kwargs: [
        SiloItem({"content_id": f"movie-{i}", "type": "movie", "title": str(i), "rating_imdb": rating, "versions": [{"codec_audio": "truehd", "video_tracks": [{"aspect_ratio": "4:3"}]}]}, library) for i, rating in enumerate((7, 9))
    ]
    search = library.build_local_search(data["plex_search"])
    assert library.get_rating_keys("plex_search", search) == [("movie-1", "ratingKey")]


@pytest.mark.parametrize(
    "field,value,native,expected",
    [("duration.gte", 90, "runtime", 90), ("critic_rating.gte", 7, "rating_rt_critic", 70), ("audience_rating.lt", 8, "rating_rt_audience", 80), ("rating_imdb.gt", 7.5, "rating_imdb", 7.5), ("bitrate.gt", 1000, "bitrate", 1000)],
)
def test_silo_native_numeric_fields_keep_correct_units(field, value, native, expected):
    from modules.builder import CollectionBuilder

    library = _library(SiloClient(_server(), session=FakeSession([])))
    definition = {"all": {field: value}}
    data = {"smart_filter": definition}
    CollectionBuilder._adapt_local_smart_filter(library, data, {"smart_filter": "smart_filter"})
    assert data == {"smart_filter": definition}
    query = library.build_native_filter(definition)[2]
    assert query["groups"][0]["rules"][0] == {"field": native, "op": field.split(".")[1], "value": expected}


def test_silo_local_search_upgrades_catalog_cache_when_details_are_needed(monkeypatch):
    logger = MagicMock()
    monkeypatch.setattr(silo_module, "logger", logger)
    client = SiloClient(_server(), session=FakeSession([FakeResponse({"content_id": "movie-1", "versions": [{"video_tracks": [{"aspect_ratio": "4:3"}]}]})]))
    library = _library(client)
    library.get_all = lambda **kwargs: [SiloItem({"content_id": "movie-1", "title": "Movie", "type": "movie"}, library)]
    assert len(list(library._local_search_items(require_details=False))) == 1
    assert client.session.calls == []
    search = library.build_local_search({"aspect.gt": 1.3})
    assert library.get_rating_keys("plex_search", search) == [("movie-1", "ratingKey")]
    assert library.get_rating_keys("plex_search", search) == [("movie-1", "ratingKey")]
    assert len(client.session.calls) == 1
    logger.ghost.assert_called_with("Scanning: 1/1 Movie")
    logger.info.assert_any_call("Scanned: 1/1")


def test_silo_nested_smart_filter_uses_local_fallback(monkeypatch):
    from modules.builder import CollectionBuilder

    monkeypatch.setattr("modules.builder.logger", FakeLogger())

    library = _library(SiloClient(_server(), session=FakeSession([])))
    data = {"smart_filter": {"all": [{"genre": "Drama"}, {"any": {"aspect.gt": 2, "hdr10plus": True}}]}}
    CollectionBuilder._adapt_local_smart_filter(library, data, {"smart_filter": "smart_filter"})
    assert "plex_search" in data
    assert data["collection_order"] == "custom"


def test_silo_unavailable_filter_field_fails_before_plex_validation(monkeypatch):
    from tests.factories import make_builder

    monkeypatch.setattr("modules.builder.logger", FakeLogger())
    library = _library(SiloClient(_server(), session=FakeSession([])))
    builder = make_builder(library=library, filters=[])
    with pytest.raises(BuilderValidationError, match="Silo does not provide filter field label"):
        builder._filters("filters", {"label": "Overlay"})
    assert library.client.session.calls == []


def test_silo_csv_content_ratings_flow_through_overlay_local_search():
    library = _library(SiloClient(_server(), session=FakeSession([])))
    library.get_all = lambda **kwargs: [SiloItem({"content_id": str(i), "title": str(i), "type": "movie", "content_rating": rating}, library) for i, rating in enumerate(("R", "PG-13", "PG"))]
    search = library.build_local_search({"validate": False, "any": {"content_rating": "R, PG-13"}})
    assert library.get_rating_keys("plex_search", search) == [("0", "ratingKey"), ("1", "ratingKey")]
    assert library.client.session.calls == []


def test_silo_native_csv_tag_values_are_separate_alternatives():
    library = _library(SiloClient(_server(), session=FakeSession([])))
    query = library.build_native_filter({"any": {"content_rating": " R, PG-13, "}})[2]
    assert query["groups"][0] == {"match": "any", "rules": [{"field": "content_rating", "op": "is", "value": "R"}, {"field": "content_rating", "op": "is", "value": "PG-13"}]}
    query = library.build_native_filter({"any": {"studio": ["Example, Inc."]}})[2]
    assert query["groups"][0]["rules"][0]["value"] == "Example, Inc."


def test_silo_episode_percentage_filter_uses_child_metadata():
    library = _library(SiloClient(_server(), session=FakeSession([])))
    library.is_show = True
    library.is_movie = False
    show = SiloItem({"content_id": "show-1", "type": "series"}, library)
    season = SiloItem({"content_id": "season-1", "type": "season", "season_number": 1}, library)
    episodes = [SiloItem({"content_id": f"ep-{i}", "type": "episode", "versions": [{"video_tracks": [{"width": width, "height": 1080}]}]}, library) for i, width in enumerate((1920, 1440))]
    library.list_seasons = lambda item: [season]
    library.list_episodes = lambda item: episodes
    library.reload = lambda item: item
    assert library.check_filters(show, [("episodes", {"width.gte": 1900, "percentage": 50})], None)
    assert not library.check_filters(show, [("episodes", {"width.gte": 1900, "percentage": 100})], None)


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
        Capability.LOCK_TAG,
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


def test_all_silo_requests_share_pacing(monkeypatch):
    clock = [10.0]
    waits = []

    def sleep(delay):
        waits.append(delay)
        clock[0] += delay

    monkeypatch.setattr(silo_module.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(silo_module.time, "sleep", sleep)
    session = FakeSession([FakeResponse({}) for _ in range(6)])
    client = SiloClient(_server(), session=session)
    client.add_collection_item("collection", "movie-1")
    assert waits == []
    clock[0] += 0.2
    client.get_item("movie-1")
    client.request("POST", "/catalog/query", json_body={})
    assert waits == pytest.approx([0.3, 0.5])
    client.remove_collection_item("collection", "movie-1")
    assert waits == pytest.approx([0.3, 0.5, 0.5])
    client.add_collection_item("collection", "movie-1", position=1)
    assert waits == pytest.approx([0.3, 0.5, 0.5, 0.5])
    clock[0] += 1
    client.delete_collection("collection", '"etag"')
    assert waits == pytest.approx([0.3, 0.5, 0.5, 0.5])


def test_pacing_is_shared_across_library_clients_and_profiles(skip_real_network_delays):
    first = SiloClient(_server(url="http://SILO:8090/", profile_id="first"), session=FakeSession([FakeResponse({})]))
    second = SiloClient(_server(url="http://silo:8090/api/v2", profile_id="second", token="another"), session=FakeSession([FakeResponse({})]))
    other = SiloClient(_server(url="http://another:8090"), session=FakeSession([FakeResponse({})]))
    assert first._request_pacer is second._request_pacer
    assert first._request_pacer is not other._request_pacer
    first.get_item("movie-1")
    assert skip_real_network_delays[0] == 0
    second.get_collection("collection")
    assert skip_real_network_delays[0] == 0.5
    other.get_item("movie-2")
    assert skip_real_network_delays[0] == 0.5


def test_request_pacer_serializes_concurrent_callers():
    from concurrent.futures import ThreadPoolExecutor

    pacer = silo_module._RequestPacer()
    with ThreadPoolExecutor(max_workers=4) as executor:
        timestamps = list(executor.map(lambda _: pacer.wait(), range(8)))
    assert sorted(timestamps) == [i * 0.5 for i in range(8)]


def test_admin_reads_and_writes_share_pacing(monkeypatch):
    clock = [0.0]
    waits = []

    def sleep(delay):
        waits.append(delay)
        clock[0] += delay

    monkeypatch.setattr(silo_module.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(silo_module.time, "sleep", sleep)
    session = FakeSession([FakeResponse({}) for _ in range(3)])
    client = SiloClient(_server(), session=session)
    client.get_collection("one")
    client.get_collection("two")
    client.add_collection_item("two", "movie-1")
    assert waits == [0.5, 0.5]


@pytest.mark.parametrize("status,exception", [(404, CollectionNotFound), (403, Failed), (500, Failed)])
def test_collection_detail_error_is_typed(status, exception):
    session = FakeSession([FakeResponse({"detail": "Unavailable"}, status_code=status)])
    with pytest.raises(exception) as error:
        SiloClient(_server(), session=session).get_collection("missing")
    assert type(error.value) is exception


@pytest.mark.parametrize("retry_after,waits_expected", [("0", [0, 0.5]), ("2", [2])])
def test_write_retries_respect_both_pacing_and_retry_after(monkeypatch, retry_after, waits_expected):
    clock = [0.0]
    waits = []

    def sleep(delay):
        waits.append(delay)
        clock[0] += delay

    monkeypatch.setattr(silo_module.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(silo_module.time, "sleep", sleep)
    session = FakeSession([FakeResponse(status_code=429, headers={"Retry-After": retry_after}), FakeResponse({})])
    client = SiloClient(_server(), session=session)
    client.add_collection_item("collection", "movie-1")
    assert waits == pytest.approx(waits_expected)
    assert len(session.calls) == 2


@pytest.mark.parametrize("retry_after,expected_delay", [("7", 7), ("0", 0), (None, 1), ("invalid", 1), ("Thu, 01 Jan 1970 00:00:00 GMT", 0)])
def test_client_retries_rate_limit(monkeypatch, retry_after, expected_delay, skip_real_network_delays):
    delays = []
    monkeypatch.setattr(silo_module.time, "sleep", lambda delay: (delays.append(delay), skip_real_network_delays.__setitem__(0, skip_real_network_delays[0] + delay)))
    session = FakeSession([FakeResponse(status_code=429, headers={"Retry-After": retry_after}), FakeResponse({"content_id": "movie-imdb-tt1853728"})])
    client = SiloClient(_server(), session=session)
    assert client.get_item("movie-imdb-tt1853728")["content_id"] == "movie-imdb-tt1853728"
    assert delays == [expected_delay] + ([0.5] if expected_delay == 0 else [])
    assert session.calls[0] == session.calls[1]


def test_client_rate_limit_retries_are_bounded(monkeypatch, skip_real_network_delays):
    delays = []
    monkeypatch.setattr(silo_module.time, "sleep", lambda delay: (delays.append(delay), skip_real_network_delays.__setitem__(0, skip_real_network_delays[0] + delay)))
    session = FakeSession([FakeResponse({"detail": "Too many requests"}, status_code=429) for _ in range(6)])
    with pytest.raises(Failed, match="returned 429.*Too many requests"):
        SiloClient(_server(), session=session).get_item("movie-imdb-tt1853728")
    assert len(session.calls) == 6
    assert delays == [1, 2, 4, 8, 10]


def test_client_does_not_retry_other_errors(monkeypatch):
    delays = []
    monkeypatch.setattr(silo_module.time, "sleep", delays.append)
    session = FakeSession([FakeResponse(status_code=403)])
    with pytest.raises(Failed, match="returned 403"):
        SiloClient(_server(), session=session).get_item("movie-imdb-tt1853728")
    assert len(session.calls) == 1
    assert delays == []


def test_silo_ids_persist_between_runs_and_refresh_after_expiration(tmp_path, monkeypatch):
    from modules import cache as cache_module
    from modules.cache import Cache

    monkeypatch.setattr(cache_module, "logger", FakeLogger())
    config_path = str(tmp_path / "config.yml")
    card = {"content_id": "movie-imdb-tt1853728", "title": "Django Unchained", "type": "movie"}
    detail = {"tmdb_id": 68718, "tvdb_id": 123, "imdb_id": "tt1853728"}
    session = FakeSession([FakeResponse(detail)])
    library = _library(SiloClient(_server(), session=session))
    library.config.Cache = Cache(config_path, 30)
    item = library._item_with_ids(card)
    assert (item.tmdb_id, item.tvdb_id, item.imdb_id) == (68718, 123, "tt1853728")
    library.config.Cache.connection.close()

    # A new connection and library simulate a separate Kometa invocation.
    next_session = FakeSession([])
    library = _library(SiloClient(_server(), session=next_session))
    cache = library.config.Cache = Cache(config_path, 30)
    item = library._item_with_ids(card)
    assert (item.tmdb_id, item.tvdb_id, item.imdb_id) == (68718, 123, "tt1853728")
    assert next_session.calls == []

    with cache.connection:
        cache.connection.execute("UPDATE list_cache SET expiration_date = '2000-01-01' WHERE list_type = 'silo_item_ids'")
    next_session.responses.append(FakeResponse({**detail, "tmdb_id": 999}))
    assert library._item_with_ids(card).tmdb_id == 999
    assert len(next_session.calls) == 1
    assert library._item_with_ids(card).tmdb_id == 999
    assert len(next_session.calls) == 1
    cache.connection.close()


def test_silo_failed_id_lookup_is_not_cached(tmp_path, monkeypatch):
    from modules import cache as cache_module
    from modules.cache import Cache

    monkeypatch.setattr(cache_module, "logger", FakeLogger())
    card = {"content_id": "movie-imdb-tt1853728"}
    session = FakeSession([FakeResponse(status_code=503), FakeResponse({"imdb_id": "tt1853728"})])
    library = _library(SiloClient(_server(), session=session))
    cache = library.config.Cache = Cache(str(tmp_path / "config.yml"), 30)
    assert library._item_with_ids(card).imdb_id is None
    assert library._item_with_ids(card).imdb_id == "tt1853728"
    assert len(session.calls) == 2
    cache.connection.close()


@pytest.mark.parametrize("media_type,level,accepted", [("movie", "movie", True), ("show", "show", True), ("series", "show", True), ("show", "movie", False)])
@pytest.mark.parametrize("source", ["imdb", "tmdb"])
def test_builder_accepts_silo_items_from_external_ids(monkeypatch, media_type, level, accepted, source):
    from modules import builder as builder_module
    from tests.factories import make_builder

    monkeypatch.setattr(builder_module, "logger", FakeLogger())
    library = _library(None)
    item = SiloItem({"content_id": "movie-imdb-tt1853728", "title": "Example", "type": media_type}, library)
    library.imdb_map = {"tt1853728": [item.ratingKey]}
    library.movie_map = {68718: [item.ratingKey]}
    library.fetch_item = lambda key: item
    builder = make_builder(library=library, libraries=[library], builder_level=level, parts_collection=False, check_value_filter=lambda item: True)
    identifier = ("tt1853728", "imdb") if source == "imdb" else (68718, "tmdb")
    builder.filter_and_save_items([identifier, identifier])
    assert builder.found_items == ([item] if accepted else [])


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


def test_get_all_collections_lists_the_library_and_reloads_a_collection():
    session = FakeSession(
        [
            FakeResponse(
                {
                    "items": [
                        {"id": "col-1", "title": "Heat", "library_id": "lib-1", "collection_type": "manual", "item_count": 2},
                        {"id": "col-2", "title": "Elsewhere", "library_id": "other"},
                    ],
                    "page": {"has_more": False},
                }
            ),
            FakeResponse({"id": "col-1", "title": "Heat", "collection_type": "smart", "item_count": 4}, headers={"ETag": '"v2"'}),
        ]
    )
    library = _library(SiloClient(_server(), session=session))

    collections = library.get_all_collections()

    assert [collection.title for collection in collections] == ["Heat"]
    assert library.get_all_collections(label="Kometa") == []
    reloaded = library.reload(collections[0], force=True)
    assert reloaded is collections[0]
    assert reloaded.smart is True
    assert reloaded.childCount == 4
    assert reloaded.etag == '"v2"'
    assert session.calls[1]["url"].endswith("/admin/collections/col-1")
    assert all("refresh-metadata" not in call["url"] for call in session.calls)


@pytest.mark.parametrize("reference", ["Star Trek Stuff", SimpleNamespace(title="Star Trek Stuff")])
@pytest.mark.parametrize("operation", ["lookup", "create", "add", "remove"])
def test_existing_collection_resolves_by_title(reference, operation):
    record = {"id": "col-trek", "title": "Star Trek Stuff", "library_id": "lib-1", "collection_type": "manual"}
    session = FakeSession([FakeResponse({"items": [record], "page": {"has_more": False}}), FakeResponse(None, status_code=204)])
    library = _library(SiloClient(_server(), session=session))
    if operation == "lookup":
        assert library.get_collection(reference).id == "col-trek"
    elif operation == "create":
        assert library.create_blank_collection("Star Trek Stuff").id == "col-trek"
        assert len(session.calls) == 1
    else:
        item = SiloItem({"content_id": "movie-imdb-tt0084726", "title": "The Wrath of Khan", "type": "movie"}, library)
        library.alter_collection([item], reference, add=operation == "add")
        assert session.calls[1]["method"] == ("PUT" if operation == "add" else "DELETE")
        assert session.calls[1]["url"].endswith("/admin/collections/col-trek/items/movie-imdb-tt0084726")


def test_builder_creates_silo_collection_on_first_add(monkeypatch):
    from modules import builder as builder_module
    from tests.factories import make_builder

    monkeypatch.setattr(builder_module, "logger", FakeLogger())
    record = {"id": "col-trek", "title": "Star Trek Stuff", "library_id": "lib-1", "collection_type": "manual"}
    session = FakeSession(
        [
            FakeResponse({"items": [], "page": {"has_more": False}}),
            FakeResponse(record),
            FakeResponse(None, status_code=204),
        ]
    )
    library = _library(SiloClient(_server(), session=session))
    item = SiloItem({"content_id": "movie-imdb-tt0084726", "title": "The Wrath of Khan", "type": "movie"}, library)
    builder = make_builder(
        library=library,
        name="Star Trek Stuff",
        found_items=[item],
        limit=0,
        beginning_count=0,
        remove_item_map={},
        details={"changes_webhooks": False},
    )
    assert builder.add_to_collection() == (1, 0)
    assert [call["method"] for call in session.calls] == ["GET", "POST", "PUT"]
    assert session.calls[1]["json"] == {"title": "Star Trek Stuff", "library_id": "lib-1", "collection_type": "manual"}
    assert session.calls[2]["url"].endswith("/col-trek/items/movie-imdb-tt0084726")


def test_empty_silo_builder_does_not_create_collection(monkeypatch):
    from modules import builder as builder_module
    from tests.factories import make_builder

    monkeypatch.setattr(builder_module, "logger", FakeLogger())
    session = FakeSession([])
    library = _library(SiloClient(_server(), session=session))
    builder = make_builder(library=library, limit=0)
    assert builder.add_to_collection() == (0, 0)
    assert session.calls == []


@pytest.mark.parametrize("summary,expected", [("New summary", ["Metadata"]), ("Original summary", []), (None, [])])
def test_builder_updates_silo_collection_metadata(monkeypatch, summary, expected):
    from modules import builder as builder_module
    from tests.factories import make_builder

    monkeypatch.setattr(builder_module, "logger", FakeLogger())
    record = {"id": "col-trek", "title": "Star Trek Stuff", "description": "Original summary", "collection_type": "manual", "sort_config": {"field": "release_date", "order": "asc"}}
    session = FakeSession([FakeResponse(record, headers={"ETag": '"v1"'}), FakeResponse({"description": "New summary"}, headers={"ETag": '"v2"'})])
    library = _library(SiloClient(_server(), session=session))
    library.collection_images = {}
    collection = SiloCollection(record)
    builder = make_builder(
        library=library,
        obj=collection,
        name="Star Trek Stuff",
        summaries={"summary": summary},
        details={"sort_title": "!001 Star Trek", "collection_order": "release"},
        mapping_name="Star Trek Stuff",
        collection_logo=None,
        collection_square_art=None,
        url_theme=None,
        file_theme=None,
    )
    builder._load_collection_assets = lambda: (None, None)
    builder._pick_collection_artwork = lambda *args: None
    assert builder.update_details() == expected
    assert session.calls[0]["method"] == "GET"
    assert len(session.calls) == (2 if expected else 1)
    if expected:
        assert session.calls[1]["method"] == "PATCH"
        assert session.calls[1]["json"] == {"description": "New summary"}
        assert session.calls[1]["headers"] == {"If-Match": '"v1"'}
        assert collection.summary == "New summary"
        assert collection.etag == '"v2"'


@pytest.mark.parametrize("folders", [True, False])
@pytest.mark.parametrize("present", [True, False])
def test_silo_metadata_resolves_local_collection_artwork(tmp_path, monkeypatch, folders, present):
    from modules import builder as builder_module
    from modules import library as library_module
    from modules import plex as plex_module
    from tests.factories import make_builder

    for module in (builder_module, library_module, plex_module):
        monkeypatch.setattr(module, "logger", FakeLogger())
    record = {"id": "col-trek", "title": "Star Trek Stuff", "sort_config": {"field": "release_date", "order": "asc"}}
    session = FakeSession([FakeResponse(record), FakeResponse(None, status_code=204), FakeResponse(None, status_code=204)])
    library = _library(SiloClient(_server(), session=session))
    library.config.Cache = None
    library.collection_images = {}
    library.asset_folders = folders
    library.asset_depth = 1
    library.create_asset_folders = False
    library.show_missing_assets = True
    library.dimensional_asset_rename = False
    library.prioritize_assets = True
    library.download_url_assets = False
    library.asset_directory = [str(tmp_path)]
    library.collection_asset_directory = [str(tmp_path)]
    directory = tmp_path / "nested" / "Trek" if folders else tmp_path
    directory.mkdir(parents=True, exist_ok=True)
    poster = directory / ("poster.jpg" if folders else "Trek.jpg")
    background = directory / ("background.jpg" if folders else "Trek_background.jpg")
    if present:
        poster.write_bytes(b"poster")
        background.write_bytes(b"background")
    published = []

    def publish(location, **kwargs):
        published.append(location)
        return "https://example.com/" + location.rsplit("/", 1)[-1]

    monkeypatch.setattr(silo_module, "publish_image", publish)
    builder = make_builder(
        library=library,
        obj=SiloCollection(record),
        name="Star Trek Stuff",
        summaries={},
        details={"name_mapping": "Trek", "sort_title": "!001 Star Trek", "collection_order": "release", "label": ["Award"], "label.remove": ["Old"], "label.sync": ["Award"], "visible_home": True, "visible_shared": True, "visible_library": False},
        mapping_name="Star Trek Stuff",
        collection_asset_directory=[str(tmp_path)],
        collection_assets_configured=True,
        collection_logo=None,
        collection_square_art=None,
        url_theme=None,
        file_theme=None,
        posters={},
        backgrounds={},
        logos={},
        square_arts={},
    )
    assert builder.update_details() == (["Image"] if present else [])
    assert published == ([str(poster), str(background)] if present else [])
    assert len(session.calls) == (3 if present else 1)
    if present:
        assert session.calls[1]["url"].endswith("/col-trek/poster")
        assert session.calls[2]["url"].endswith("/col-trek/backdrop")


@pytest.mark.parametrize("field", ["content_rating", "collection_mode", "collection_filtering"])
def test_silo_collection_metadata_reports_unsupported_options(field):
    record = {"id": "col-trek", "title": "Star Trek Stuff"}
    session = FakeSession([FakeResponse(record)])
    library = _library(SiloClient(_server(), session=session))
    with pytest.raises(Failed, match=f"Collection metadata attribute {field} is not supported"):
        library.update_collection_details(SiloCollection(record), None, {field: "value"})
    assert len(session.calls) == 1


@pytest.mark.parametrize("field", ["label", "label.remove", "label.sync", "visible_library", "visible_home", "visible_shared"])
def test_silo_collection_labels_warn_without_blocking_summary(field, monkeypatch):
    logger = FakeLogger()
    monkeypatch.setattr(silo_module, "logger", logger)
    record = {"id": "award", "title": "Cannes 2024"}
    session = FakeSession([FakeResponse(record, headers={"ETag": '"v1"'}), FakeResponse({"description": "Award winners"})])
    library = _library(SiloClient(_server(), session=session))
    assert library.update_collection_details(SiloCollection(record), "Award winners", {field: ["Cannes"]}) == ["Metadata"]
    assert session.calls[1]["json"] == {"description": "Award winners"}
    assert any(f"skipping {field}" in message for message in logger.warning_messages)


@pytest.mark.parametrize("tag,field", [("genre", "genres"), ("studio", "studios"), ("network", "networks")])
def test_dynamic_tags_use_cached_native_metadata(tag, field):
    library = _library(SiloClient(_server(), session=FakeSession([])))
    library._all_items = [SiloItem({"content_id": "1", field: ["Drama", "Action", ""]}, library), SiloItem({"content_id": "2", field: ["Drama"]}, library)]
    assert [(choice.key, choice.title) for choice in library.get_tags(tag)] == [("Action", "Action"), ("Drama", "Drama")]
    assert library.client.session.calls == []
    with pytest.raises(Failed, match="not supported"):
        library.get_tags("label")


@pytest.mark.parametrize("tag", ["genre", "studio", "network", "country"])
@pytest.mark.parametrize("modifier,op", [("", "is"), (".is", "is"), (".not", "is_not")])
def test_dynamic_tag_filters_translate_to_native_queries(tag, modifier, op):
    library = _library(SiloClient(_server(), session=FakeSession([])))
    _, _, query = library.build_native_filter({"sort_by": "release.desc", "any": {f"{tag}{modifier}": ["Drama", "Action"]}})
    assert query["groups"] == [{"match": "all" if op == "is_not" else "any", "rules": [{"field": tag, "op": op, "value": value} for value in ["Drama", "Action"]]}]
    assert query["library_ids"] == ["lib-1"]
    assert query["sort"] == {"field": "release_date", "order": "desc"}


@pytest.mark.parametrize("value", [[], "", None, [1]])
def test_dynamic_tag_filters_reject_missing_values(value):
    library = _library(SiloClient(_server(), session=FakeSession([])))
    with pytest.raises(Failed, match="nonempty tag names"):
        library.build_native_filter({"any": {"genre": value}})


@pytest.mark.parametrize("lowercase_codes", [True, False])
def test_silo_country_discovery_uses_scoped_facets_and_reuses_response(lowercase_codes):
    session = FakeSession([FakeResponse({"countries": ["US", "GB", "SU", "US", "France"]})])
    library = _library(SiloClient(_server(), session=session))
    names = {"US": "United States of America", "GB": "United Kingdom", "FR": "France"}
    library.config.TMDb = SimpleNamespace(iso_3166_1={code.lower() if lowercase_codes else code: name for code, name in names.items()})
    assert [choice.title for choice in library.get_tags("country")] == ["France", "Soviet Union", "United Kingdom", "United States of America"]
    assert len(library.get_tags("country")) == 4
    assert len(session.calls) == 1
    assert session.calls[0]["url"].endswith("/catalog/filters")
    assert session.calls[0]["params"] == {"source": "query", "library_id": "lib-1", "type": "movie", "skip_technical": "true"}


@pytest.mark.parametrize("modifier,op", [("", "is"), (".not", "is_not")])
def test_silo_country_filters_match_native_codes_and_legacy_names(modifier, op):
    library = _library(SiloClient(_server(), session=FakeSession([])))
    library.config.TMDb = SimpleNamespace(iso_3166_1={"us": "United States of America", "fr": "France"})
    _, _, query = library.build_native_filter({"any": {f"country{modifier}": ["United States", "France", "Czechoslovakia"]}})
    rules = query["groups"][0]["rules"]
    assert [rule["value"] for rule in rules] == ["United States", "US", "France", "FR", "Czechoslovakia", "CS", "XC"]
    assert all(rule["op"] == op for rule in rules)
    assert query["groups"][0]["match"] == ("all" if modifier else "any")


def test_silo_cast_and_crew_expose_dynamic_people():
    library = _library(SiloClient(_server(), session=FakeSession([])))
    item = SiloItem(
        {
            "content_id": "1",
            "cast": [
                {"person_id": "42", "name": " Actor One "},
                {"name": "Actor One"},
                {"name": "Actor Two"},
                {"name": ""},
                None,
            ],
            "crew": [
                {"person_id": "43", "name": "Director", "job": "Director"},
                {"name": "Writer", "job": "Screenplay"},
                {"name": "Writer", "job": "Story"},
                {"name": "Producer", "job": "Executive Producer"},
                {"name": "Camera", "job": "Cinematography"},
            ],
        },
        library,
    )
    assert [(person.id, person.tag) for person in item.actors] == [("42", "Actor One"), ("name:actor two", "Actor Two")]
    assert [person.tag for person in item.directors] == ["Director"]
    assert [person.tag for person in item.writers] == ["Writer"]
    assert [person.tag for person in item.producers] == ["Producer"]
    item.apply({"title": "Updated"})
    assert len(item.actors) == 2
    item.apply({"cast": [], "crew": []})
    assert item.actors == item.directors == item.writers == item.producers == []


@pytest.mark.parametrize("role", ["actor", "director", "writer", "producer"])
def test_silo_person_smart_filter_resolves_tmdb_names(role):
    from tests.factories import make_builder

    library = _library(SiloClient(_server(), session=FakeSession([])))
    builder = make_builder(library=library, details={"tmdb_person": ["Actor One"]})
    definition = {"sort_by": "release.desc", "any": {role: "tmdb"}}
    _, _, query = builder.build_filter("smart_filter", definition)
    assert query["groups"] == [{"match": "any", "rules": [{"field": role, "op": "is", "value": "Actor One"}]}]
    assert definition["any"][role] == "tmdb"


@pytest.mark.parametrize("method,data", [("plex_collectionless", {}), ("plex_all", "episode")])
def test_unsupported_builders_raise_validation_errors_without_api_requests(method, data):
    session = FakeSession([])
    library = _library(SiloClient(_server(), session=session))
    with pytest.raises(BuilderValidationError, match="not supported"):
        library.get_rating_keys(method, data)
    assert session.calls == []


def test_silo_smart_queries_serialize_numeric_library_ids():
    from modules.silo import _query_document

    query = {"library_ids": ["1", 2], "groups": [{"match": "any", "rules": [{"field": "actor", "op": "is", "value": "Mark Ruffalo"}]}]}
    assert _query_document(query)["library_ids"] == [1, 2]
    assert query["library_ids"] == ["1", 2]
    session = FakeSession([FakeResponse({"items": []}), FakeResponse({"id": "actor"}), FakeResponse({})])
    library = _library(SiloClient(_server(), session=session))
    library.library_id = "1"
    library.get_collection = MagicMock(side_effect=Failed("not found"))
    library.client.preview(query)
    collection = library.create_smart_collection("Mark Ruffalo", None, query, True)
    collection.etag = '"v1"'
    library.update_smart_collection(collection, query)
    assert all(call["json"]["query_definition"]["library_ids"] == [1, 2] for call in session.calls)


def test_silo_validation_error_includes_field_details():
    session = FakeSession([FakeResponse({"detail": "The request did not pass validation; see errors.", "errors": [{"location": "body", "detail": "Invalid query_definition"}]}, status_code=422)])
    with pytest.raises(Failed, match="body: Invalid query_definition"):
        SiloClient(_server(), session=session).create_collection({"title": "Mark Ruffalo"})


@pytest.mark.parametrize("tag", ["audioLanguage", "audio_language", "episode.audioLanguage"])
def test_silo_dynamic_audio_languages_use_all_tracks_and_reuse_details(tag):
    session = FakeSession([FakeResponse({"versions": [{"audio_tracks": [{"language": "EN"}, {"language": "fr"}, {"language": None}]}, {"audio_tracks": [{"language": "en"}, {"language": " ja "}, {"language": ""}]}]})])
    library = _library(SiloClient(_server(), session=session))
    item = SiloItem({"content_id": "movie-1", "title": "Movie"}, library)
    library.get_all = MagicMock(return_value=[item])
    assert [(choice.key, choice.title) for choice in library.get_tags(tag)] == [("en", "en"), ("fr", "fr"), ("ja", "ja")]
    assert len(library.get_tags(tag)) == 3
    assert len(session.calls) == 1
    library.get_all.assert_called_with(builder_level="episode" if tag.startswith("episode.") else None, ignore_schedule_scope=True)


@pytest.mark.parametrize("modifier,match,op", [("", "any", "is"), (".is", "any", "is"), (".not", "all", "is_not")])
@pytest.mark.parametrize("field", ["audio_language", "subtitle_language"])
def test_silo_language_queries_use_native_rules(modifier, match, op, field):
    library = _library(SiloClient(_server(), session=FakeSession([])))
    library.library_id = "1"
    _, _, query = library.build_native_filter({"any": {f"{field}{modifier}": [" EN ", "fr"]}, "sort_by": "release.desc"})
    assert query["groups"] == [{"match": match, "rules": [{"field": field, "op": op, "value": language} for language in ["en", "fr"]]}]
    assert query["library_ids"] == [1]


@pytest.mark.parametrize("tag", ["subtitleLanguage", "subtitle_language", "episode.subtitleLanguage", "episode.subtitle_language"])
def test_silo_dynamic_subtitle_languages_include_external_tracks(tag):
    session = FakeSession(
        [
            FakeResponse(
                {
                    "versions": [
                        {"subtitle_tracks": [{"language": "EN", "external": False}, {"language": "fr", "external": True}, {"language": None}], "audio_tracks": [{"language": "de"}]},
                        {"external_subtitles": [{"language": " ja "}, {"language": "en"}, {"language": ""}]},
                    ]
                }
            )
        ]
    )
    library = _library(SiloClient(_server(), session=session))
    item = SiloItem({"content_id": "movie-1"}, library)
    library.get_all = MagicMock(return_value=[item])
    assert [choice.key for choice in library.get_tags(tag)] == ["en", "fr", "ja"]
    assert len(library.get_tags(tag)) == 3
    assert len(session.calls) == 1
    library.get_all.assert_called_with(builder_level="episode" if tag.startswith("episode.") else None, ignore_schedule_scope=True)


@pytest.mark.parametrize("tag", ["contentRating", "content_rating"])
def test_silo_dynamic_content_ratings(tag):
    library = _library(SiloClient(_server(), session=FakeSession([])))
    library._all_items = [SiloItem({"content_id": str(i), "content_rating": value}, library) for i, value in enumerate(["PG", "R13", "PG", None, "", "nz/M"])]
    assert [choice.key for choice in library.get_tags(tag)] == ["PG", "R13", "nz/M"]
    assert library.client.session.calls == []


@pytest.mark.parametrize("tag", ["resolution", "episode.resolution"])
def test_silo_dynamic_resolutions_use_default_keys(tag):
    library = _library(SiloClient(_server(), session=FakeSession([])))
    item = SiloItem({"content_id": "movie-1", "versions": [{"resolution": value} for value in ["480p", "1080p", "2160p", "4k", "4320p", "1440p", None]]}, library)
    fallback = SiloItem({"content_id": "movie-2", "versions": [], "overlay_summary": {"resolution": "720p"}}, library)
    library.get_all = MagicMock(return_value=[item, fallback])
    assert [choice.key for choice in library.get_tags(tag)] == ["1080", "2k", "480", "4k", "720", "8k"]
    assert library.client.session.calls == []


@pytest.mark.parametrize("field,value,expected", [("resolution", 1080, "1080p"), ("resolution", "4k", "2160p"), ("resolution", "8k", "4320p"), ("resolution", "sd", "sd"), ("content_rating", "nz/R13", "nz/R13"), ("content_rating", 13, "13")])
def test_silo_resolution_and_rating_filters_use_native_values(field, value, expected):
    library = _library(SiloClient(_server(), session=FakeSession([])))
    _, _, query = library.build_native_filter({"any": {field: value}})
    assert query["groups"] == [{"match": "any", "rules": [{"field": field, "op": "is", "value": expected}]}]


def test_silo_dynamic_decades_and_years_ignore_missing_years():
    library = _library(SiloClient(_server(), session=FakeSession([])))
    library._all_items = [SiloItem({"content_id": str(i), "year": year}, library) for i, year in enumerate([1990, 1999, "2001", 2024, None, 0, True, "unknown"])]
    assert [(choice.key, choice.title) for choice in library.get_tags("decade")] == [("1990", "1990s"), ("2000", "2000s"), ("2020", "2020s")]
    assert [choice.key for choice in library.get_tags("year")] == ["1990", "1999", "2001", "2024"]
    assert library.client.session.calls == []


@pytest.mark.parametrize("field,values,expected", [("decade", ["1990s", 2000], [1990, 2000]), ("year", ["1990", "1994", 1999], [1990, 1994, 1999])])
def test_silo_decade_defaults_translate_years_and_rating_sort(field, values, expected):
    library = _library(SiloClient(_server(), session=FakeSession([])))
    _, _, query = library.build_native_filter({"any": {field: values}, "sort_by": "critic_rating.desc", "limit": 100})
    assert query["groups"] == [{"match": "any", "rules": [{"field": field, "op": "is", "value": year} for year in expected]}]
    assert query["sort"] == {"field": "rating_rt_critic", "order": "desc"}
    assert query["limit"] == 100


@pytest.mark.parametrize("value", [None, True, [], "unknown", 0, 10000])
def test_silo_decade_filter_rejects_invalid_years(value):
    library = _library(SiloClient(_server(), session=FakeSession([])))
    with pytest.raises(BuilderValidationError, match="valid years"):
        library.build_native_filter({"any": {"decade": value}})


def test_silo_basic_release_smart_filter_uses_native_query(monkeypatch):
    from modules import builder as builder_module
    from tests.factories import make_builder

    monkeypatch.setattr(builder_module, "logger", FakeLogger())
    session = FakeSession(
        [
            FakeResponse({"items": [{"content_id": "movie-tmdb-1"}], "page": {"has_more": False}}),
            FakeResponse({"items": [{"content_id": "movie-tmdb-1"}]}),
            FakeResponse({"items": [], "page": {"has_more": False}}),
            FakeResponse({"id": "new", "title": "Newly Released", "collection_type": "smart"}),
        ]
    )
    library = _library(SiloClient(_server(), session=session))
    builder = make_builder(library=library)
    kind, _, query = builder.build_filter("smart_filter", {"sort_by": "release.desc", "limit": 5, "any": {"release": 90}}, default_sort="random")
    assert query["groups"] == [{"match": "any", "rules": [{"field": "release_date", "op": "in_last", "value": "90d"}]}]
    assert query["media_scope"] == "movie"
    assert query["library_ids"] == ["lib-1"]
    assert len(library.fetchItems(query)) == 1
    body = session.calls[0]["json"]
    assert (body["type"], body["sort"], body["order"]) == ("movie", "release_date", "desc")
    assert body["query_limit"] == 5
    created = library.create_smart_collection("Newly Released", kind, query, False)
    assert created.smart
    assert session.calls[-1]["json"]["query_definition"] == query


def test_builder_updates_existing_native_silo_smart_filter(monkeypatch):
    from modules import builder as builder_module
    from tests.factories import make_builder

    monkeypatch.setattr(builder_module, "logger", FakeLogger())
    session = FakeSession([FakeResponse(None, status_code=204, headers={"ETag": '"v2"'})])
    library = _library(SiloClient(_server(), session=session))
    collection = SiloCollection({"id": "new", "collection_type": "smart", "query_definition": {"groups": []}}, etag='"v1"')
    builder = make_builder(library=library, obj=collection)
    _, _, query = library.build_native_filter({"all": {"added": 30}, "sort_by": "added.desc"})
    builder.update_smart_filter(query)
    assert session.calls[0]["json"] == {"query_definition": query}
    assert collection.etag == '"v2"'
    builder.update_smart_filter(query)
    assert len(session.calls) == 1


@pytest.mark.parametrize("definition", [{"any": {"label": "Kometa"}}, {"any": {"release": 0}}, {"any": {"release": 90}, "sort_by": "random"}, {"all": {}, "any": {"release": 90}}])
def test_silo_native_filter_refuses_unsupported_semantics(definition):
    library = _library(SiloClient(_server(), session=FakeSession([])))
    with pytest.raises(Failed, match="Silo Error"):
        library.build_native_filter(definition)


def test_overlay_plex_search_reports_unsupported_translation(monkeypatch):
    from modules import builder as builder_module
    from tests.factories import make_builder

    monkeypatch.setattr(builder_module, "logger", FakeLogger())
    session = FakeSession([])
    library = _library(SiloClient(_server(), session=session))
    builder = make_builder(library=library, Type="Overlay", overlay=True)
    with pytest.raises(Failed, match="Unsupported local search field"):
        builder._plex("plex_search", {"all": {"unsupported_field.regex": "Director.*Cut"}})
    assert session.calls == []


def test_local_overlay_filter_validation_does_not_use_plex_choices():
    from tests.factories import make_builder

    library = _library(SiloClient(_server(), session=FakeSession([])))
    builder = make_builder(library=library, Type="Overlay")
    assert builder.validate_attribute("edition", "", "edition", "Director", True) == "Director"
    assert builder.validate_attribute("resolution", ".regex", "resolution.regex", "(?i)2160|4k", True) == ["(?i)2160|4k"]


def test_overlay_resolution_search_executes_locally_and_reuses_details(monkeypatch):
    from modules import builder as builder_module
    from tests.factories import make_builder

    monkeypatch.setattr(builder_module, "logger", FakeLogger())
    detail = {"content_id": "movie-tmdb-152", "type": "movie", "title": "Example", "overlay_summary": {"hdr": "Dolby Vision"}, "versions": [{"resolution": "2160p", "hdr": True, "file_path": "/Movies/Example.DV.HDR10+.mkv"}]}
    session = FakeSession([FakeResponse(detail)])
    library = _library(SiloClient(_server(), session=session))
    library.get_all = lambda **kwargs: [SiloItem({"content_id": "movie-tmdb-152", "type": "movie", "title": "Example"}, library)]
    builder = make_builder(library=library, Type="Overlay", overlay=True, current_time=None, check_value_filter=lambda item: True, filters=[[("filepath.regex", [r"(?i)\bdv.HDR10(\+|P(lus)?\b)"]), ("has_dolby_vision", True)]])
    del builder.check_filters
    search = builder.build_filter("plex_search", {"all": {"any": {"resolution.regex": "(?i)2160|4k"}, "hdr": True}})
    ids = library.get_rating_keys("plex_search", search)
    assert ids == [("movie-tmdb-152", "ratingKey")]
    builder.filter_and_save_items(ids)
    assert [item.ratingKey for item in builder.found_items] == ["movie-tmdb-152"]
    assert library.get_rating_keys("plex_search", search) == ids
    assert library.get_rating_keys("plex_all", "movie") == ids
    assert len(session.calls) == 1


@pytest.mark.parametrize("order,expected", [("release", {"field": "release_date", "order": "asc"}), ("alpha", {"field": "title", "order": "asc"}), ("custom", {})])
def test_silo_collection_order_updates_native_sort_config(order, expected):
    record = {"id": "col-1", "title": "Example", "sort_config": {"field": "year", "order": "desc"}}
    session = FakeSession([FakeResponse(record, headers={"ETag": '"v1"'}), FakeResponse(None, status_code=204, headers={"ETag": '"v2"'})])
    library = _library(SiloClient(_server(), session=session))
    collection = SiloCollection(record)
    assert library.update_collection_details(collection, "Summary", {"collection_order": order}) == ["Metadata"]
    assert session.calls[1]["json"] == {"description": "Summary", "sort_config": expected}
    assert session.calls[1]["headers"] == {"If-Match": '"v1"'}
    assert collection.data["sort_config"] == expected
    assert collection.etag == '"v2"'


@pytest.mark.parametrize("descending", [False, True])
def test_silo_custom_order_repositions_members_and_keeps_append_extras(monkeypatch, descending):
    from modules import builder as builder_module
    from tests.factories import make_builder

    monkeypatch.setattr(builder_module, "logger", FakeLogger())
    session = FakeSession([])
    library = _library(SiloClient(_server(), session=session))
    collection = SiloCollection({"id": "col-1", "collection_type": "manual"})
    members = {"a": 1, "b": 0, "extra": 9}
    calls = []
    library.client.collection_items = lambda key: [{"media_item_id": key, "position": value} for key, value in sorted(members.items(), key=lambda pair: pair[1])]

    def remove(collection_id, key):
        calls.append(("remove", key))
        del members[key]

    def add(collection_id, key, position=0):
        assert key not in members
        calls.append(("add", key, position))
        members[key] = position

    library.client.remove_collection_item = remove
    library.client.add_collection_item = add
    items = [SiloItem({"content_id": key, "type": "movie"}, library) for key in ("a", "b")]
    builder = make_builder(library=library, obj=collection, found_items=items, custom_sort="custom.desc" if descending else "custom")
    builder.sort_collection()
    assert members == ({"b": 0, "a": 1, "extra": 2} if descending else {"a": 0, "b": 1, "extra": 2})
    calls.clear()
    builder.sort_collection()
    assert calls == []


def test_silo_reorder_restores_member_after_failed_add():
    library = _library(SiloClient(_server(), session=FakeSession([])))
    library.client.collection_items = lambda key: [{"media_item_id": "a", "position": 4}]
    calls = []
    library.client.remove_collection_item = lambda *args: calls.append(("remove", args))

    def add(collection_id, key, position=0):
        calls.append(("add", key, position))
        if position == 0:
            raise Failed("upload failed")

    library.client.add_collection_item = add
    with pytest.raises(Failed, match="upload failed"):
        library.sort_collection_items(SiloCollection({"id": "col-1"}), [SiloItem({"content_id": "a"}, library)], "custom")
    assert calls[-1] == ("add", "a", 4)


def test_silo_native_sort_field_uses_conditional_patch():
    session = FakeSession([FakeResponse({"id": "col-1"}, headers={"ETag": '"v1"'}), FakeResponse(None, status_code=204)])
    library = _library(SiloClient(_server(), session=session))
    library.sort_collection_items(SiloCollection({"id": "col-1"}), [], ["added.desc"])
    assert session.calls[-1]["json"] == {"sort_config": {"field": "added_at", "order": "desc"}}
    assert session.calls[-1]["headers"] == {"If-Match": '"v1"'}


@pytest.mark.parametrize("members", [[{"media_item_id": "a"}], [{"position": 0}], [{"media_item_id": "different", "position": 0}]])
def test_silo_reorder_validates_members_before_mutation(members):
    session = FakeSession([])
    library = _library(SiloClient(_server(), session=session))
    library.client.collection_items = lambda key: members
    with pytest.raises(Failed, match="Silo Error"):
        library.sort_collection_items(SiloCollection({"id": "col-1"}), [SiloItem({"content_id": "a"}, library)], "custom")
    assert session.calls == []


@pytest.mark.parametrize("variable", ["imdb_rating", "tmdb_rating"])
def test_silo_provider_overlay_ratings_use_shared_resolver_and_cache(variable):
    cache = MagicMock()
    cache.query_overlay_value_cache.return_value = (None, True)
    library = _library(SiloClient(_server(), session=FakeSession([])))
    library.config.Cache = cache
    library.config.IMDb = SimpleNamespace(get_rating=MagicMock(return_value=8.2))
    library.config.TMDb = SimpleNamespace(get_item=MagicMock(return_value=SimpleNamespace(vote_average=8.2)))
    item = SiloItem({"content_id": "movie-imdb-tt0120689", "title": "Example", "type": "movie", "tmdb_id": 152, "imdb_id": "tt0120689"}, library)
    assert library.fetch_overlay_value(item, variable) == 8.2
    cache.update_overlay_value_cache.assert_called_once_with(False, item.ratingKey, variable, 8.2)
    cache.query_overlay_value_cache.return_value = (8.2, False)
    assert library.fetch_overlay_value(item, variable) == 8.2
    provider = library.config.IMDb.get_rating if variable == "imdb_rating" else library.config.TMDb.get_item
    assert provider.call_count == 1


def test_silo_plex_rating_reports_required_provider_metadata():
    library = _library(SiloClient(_server(), session=FakeSession([])))
    item = SiloItem({"content_id": "movie-tmdb-152", "type": "movie"}, library)
    with pytest.raises(Failed, match="requires Plex provider rating metadata"):
        library.fetch_overlay_value(item, "plex_imdb_rating")


@pytest.mark.parametrize(
    "variable,field,raw,expected",
    [
        ("silo_imdb_rating", "rating_imdb", 8.4, 8.4),
        ("silo_tmdb_rating", "rating_tmdb", 7.6, 7.6),
        ("silo_tomatoes_rating", "rating_rt_critic", 92, 9.2),
        ("silo_tomatoesaudience_rating", "rating_rt_audience", 85, 8.5),
        ("silo_user_rating", "user_rating", 4, 8.0),
    ],
)
def test_silo_native_overlay_ratings(variable, field, raw, expected):
    session = FakeSession([FakeResponse({field: raw})])
    library = _library(SiloClient(_server(), session=session))
    item = SiloItem({"content_id": "movie-tmdb-152", "type": "movie"}, library)
    assert library.fetch_overlay_value(item, variable) == pytest.approx(expected)
    assert library.fetch_overlay_value(item, variable) == pytest.approx(expected)
    assert len(session.calls) == 1


@pytest.mark.parametrize(
    "payload,variable,expected",
    [
        ({"ratings": [{"source": "imdb", "score": 84}]}, "silo_imdb_rating", 8.4),
        ({"rating_sources": [{"source": "rt_critic", "score": 92}]}, "silo_tomatoes_rating", 9.2),
        ({}, "silo_imdb_rating", None),
        ({"rating_imdb": float("nan")}, "silo_imdb_rating", None),
        ({"rating_rt_critic": 101}, "silo_tomatoes_rating", None),
        ({"user_rating": 0}, "silo_user_rating", None),
        ({"rating_imdb": True}, "silo_imdb_rating", None),
    ],
)
def test_silo_native_rating_fallback_and_validation(payload, variable, expected):
    library = _library(SiloClient(_server(), session=FakeSession([FakeResponse(payload)])))
    item = SiloItem({"content_id": "movie-tmdb-152", "type": "movie"}, library)
    result = library.fetch_overlay_value(item, variable)
    assert result is None if expected is None else result == pytest.approx(expected)


def test_native_ratings_are_shared_between_sources_but_not_profile_instances():
    item_data = {"content_id": "movie-tmdb-152", "type": "movie"}
    for stars in (1, 5):
        session = FakeSession([FakeResponse({"user_rating": stars, "rating_imdb": 8.4})])
        library = _library(SiloClient(_server(profile_id=str(stars)), session=session))
        item = SiloItem(item_data, library)
        assert library.fetch_overlay_value(item, "silo_user_rating") == stars * 2
        assert library.fetch_overlay_value(item, "silo_imdb_rating") == 8.4
        assert len(session.calls) == 1


def test_forced_reload_reads_fresh_metadata_without_refresh_job():
    session = FakeSession([FakeResponse({"content_id": "movie-tmdb-152", "title": "Fresh"})])
    library = _library(SiloClient(_server(), session=session))
    item = SiloItem({"content_id": "movie-tmdb-152", "title": "Old"}, library)
    library._search_details = {item.content_id: item}
    library._native_rating_details = {item.content_id: {"rating_imdb": 1}}
    library.bulk_reload([item], force=True)
    assert item.title == "Fresh"
    assert [call["method"] for call in session.calls] == ["GET"]
    assert item.content_id not in library._native_rating_details
    assert library.reload(item).title == "Fresh"
    assert len(session.calls) == 1


def test_explicit_silo_metadata_refresh_sends_json():
    session = FakeSession([FakeResponse({"id": "job-1"}, status_code=202)])
    SiloClient(_server(), session=session).refresh_metadata("movie-tmdb-152")
    assert session.calls[0]["method"] == "POST"
    assert session.calls[0]["json"] == {"mode": "quick"}


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


def test_get_all_reports_loaded_progress_for_each_catalog_page():
    ghosts = []
    silo_module.logger.ghost = lambda text="": ghosts.append(str(text))
    session = FakeSession(
        [
            FakeResponse({"items": [{"content_id": "movie:one", "title": "One", "tmdb_id": 1}], "total": 2, "page": {"has_more": True, "next_cursor": "page-2"}}),
            FakeResponse({"items": [{"content_id": "movie:two", "title": "Two", "tmdb_id": 2}], "total": 2, "page": {"has_more": False}}),
        ]
    )
    library = _library(SiloClient(_server(), session=session))

    items = library.get_all()

    assert [item.ratingKey for item in items] == ["movie:one", "movie:two"]
    assert ghosts == ["Loaded: 1/2", "Loaded: 2/2"]
    assert "Loading All Movies from Library: Films" in silo_module.logger.info_messages
    assert silo_module.logger.info_messages.count("Loaded: 1/2") == 1
    assert silo_module.logger.info_messages.count("Loaded: 2/2") == 1
    assert "Loaded 2 Movies" in silo_module.logger.info_messages
    assert session.calls[1]["params"]["cursor"] == "page-2"


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


def test_collection_skips_unsupported_artwork_before_publishing(tmp_path, monkeypatch):
    from modules import library as library_module
    from modules.poster import ImageData

    logger = FakeLogger()
    monkeypatch.setattr(silo_module, "logger", logger)
    monkeypatch.setattr(library_module, "logger", logger)

    def unexpected_publish(*args, **kwargs):
        pytest.fail("Unsupported collection artwork must not be published")

    monkeypatch.setattr(silo_module, "publish_image", unexpected_publish)
    local = tmp_path / "logo.png"
    local.write_bytes(b"logo")
    session = FakeSession([FakeResponse(None, status_code=204), FakeResponse(None, status_code=204)])
    library = _library(SiloClient(_server(), session=session))
    library.config.Cache = None
    collection = SiloCollection({"id": "col-trek", "title": "Star Trek Stuff"})
    result = library.upload_images(
        collection,
        poster=ImageData("url_poster", "https://example.com/poster.jpg"),
        background=ImageData("url_background", "https://example.com/background.jpg", image_type="background"),
        logo=ImageData("asset_directory", str(local), image_type="logo", is_url=False),
        square_art=ImageData("asset_directory", str(local), image_type="square_art", is_url=False),
    )
    assert result == (True, True, False, False)
    assert len(session.calls) == 2
    assert session.calls[0]["url"].endswith("/col-trek/poster")
    assert session.calls[1]["url"].endswith("/col-trek/backdrop")
    assert len(logger.warning_messages) == 2
    assert logger.error_messages == []


def test_item_logo_upload_remains_supported(monkeypatch):
    from modules import library as library_module
    from modules.poster import ImageData

    monkeypatch.setattr(library_module, "logger", FakeLogger())
    session = FakeSession([FakeResponse(None, status_code=204)])
    library = _library(SiloClient(_server(), session=session))
    library.config.Cache = None
    item = SiloItem({"content_id": "movie-tmdb-152", "type": "movie"}, library)
    assert library.upload_images(item, logo=ImageData("url_logo", "https://example.com/logo.png", image_type="logo")) == (False, False, True, False)
    assert len(session.calls) == 1


def test_silo_overlay_lifecycle_uses_backups_without_labels(tmp_path, monkeypatch):
    from PIL import Image

    from modules import overlays as overlays_module
    from modules.overlays import Overlays

    logger = FakeLogger()
    monkeypatch.setattr(overlays_module, "logger", logger)
    monkeypatch.setattr(silo_module, "publish_image", lambda *args, **kwargs: "https://example.com/restored.jpg")
    session = FakeSession([FakeResponse(None, status_code=204)])
    library = _library(SiloClient(_server(), session=session))
    library.overlay_backup = str(tmp_path / "backup")
    library.overlay_folder = str(tmp_path)
    library.remove_overlays = True
    library.is_music = False
    library.asset_directory = []
    library.collection_asset_directory = []
    library.asset_folders = False
    library.asset_depth = 0
    library.create_asset_folders = False
    item = SiloItem({"content_id": "movie-tmdb-152", "type": "movie", "title": "Star Trek"}, library)
    library.get_all = lambda **kwargs: [item]
    backup = tmp_path / "backup" / "movie-tmdb-152.jpg"
    backup.parent.mkdir()
    Image.new("RGB", (10, 15)).save(backup)
    engine = Overlays.__new__(Overlays)
    engine.library = library
    engine.cache = None
    engine.run_overlays()
    assert len(session.calls) == 1
    assert session.calls[0]["json"]["original_url"] == "https://example.com/restored.jpg"
    assert not backup.exists()
    assert logger.error_messages == []


@pytest.mark.parametrize("server_url", ["http://silo:8090", "http://silo:8090/", "http://silo:8090/api/v2"])
@pytest.mark.parametrize(
    "poster_url,expected",
    [
        ("/api/v2/artwork/local/movies/movie-tmdb-27040/poster.webp?exp=123&sig=a%2Fb", "http://silo:8090/api/v2/artwork/local/movies/movie-tmdb-27040/poster.webp?exp=123&sig=a%2Fb"),
        ("https://images.example.com/poster.jpg?sig=a%2Fb", "https://images.example.com/poster.jpg?sig=a%2Fb"),
        (None, None),
    ],
)
def test_silo_poster_urls_resolve_server_relative_artwork(server_url, poster_url, expected):
    library = _library(SiloClient(_server(url=server_url), session=FakeSession([])))
    item = SiloItem({"content_id": "movie-tmdb-27040", "poster_url": poster_url}, library)
    assert item.poster_url == item.posterUrl == item.thumb == expected
    assert library.find_poster_url(item) == expected


def test_silo_poster_selection_preserves_existing_backup():
    library = _library(SiloClient(_server(), session=FakeSession([])))
    item = SiloItem({"content_id": "movie-tmdb-152", "title": "Example", "poster_url": "https://example.com/poster.jpg"}, library)
    assert item.posterUrl == item.thumb == "https://example.com/poster.jpg"
    assert library.item_posters(item) == item.posterUrl
    assert library.item_posters(item, providers=[]) is None


@pytest.mark.parametrize("missing_rating", [False, True])
def test_silo_overlay_application_reuses_original_without_labels(tmp_path, monkeypatch, missing_rating):
    from PIL import Image

    from modules import overlays as overlays_module
    from modules.overlays import Overlays

    logger = FakeLogger()
    monkeypatch.setattr(overlays_module, "logger", logger)
    session = FakeSession([FakeResponse({"poster_url": "https://example.com/poster.jpg"}), FakeResponse({"poster_url": "https://example.com/poster.jpg"}), FakeResponse(None, status_code=204)] * 2)
    library = _library(SiloClient(_server(), session=session))
    library.session = session
    library.overlay_backup = str(tmp_path / "backup")
    library.overlay_folder = str(tmp_path)
    library.remove_overlays = library.reapply_overlays = library.assets_for_all = False
    library.reset_overlays = None
    library.is_music = False
    library.asset_directory = []
    library.collection_asset_directory = []
    library.asset_folders = False
    library.asset_depth = 0
    library.create_asset_folders = False
    library.plex_bulk_edit_batch_size = 0
    library.overlay_artwork_filetype = "png"
    library.overlay_artwork_quality = None
    downloads = []

    def download(title, url, path, **kwargs):
        downloads.append(url)
        path += ".png"
        Image.new("RGB", (10, 15), "red").save(path)
        return SimpleNamespace(location=path)

    library.config.Requests = SimpleNamespace(download_image=download)

    def publish(path, **kwargs):
        with Image.open(path) as image:
            assert image.getexif()[0x04BC] == "overlay"
        return "https://example.com/rendered.png"

    monkeypatch.setattr(silo_module, "publish_image", publish)
    item = SiloItem({"content_id": "movie-tmdb-152", "title": "Star Trek", "type": "movie"}, library)
    library.get_all = lambda **kwargs: [item]
    definition = SimpleNamespace(name="blur(2)", mapping_name="Blur", variables=[], updated=False, image=None, get_overlay_compare=lambda: "hash")
    properties = {"Blur": definition}
    if missing_rating:
        properties["MissingRating"] = SimpleNamespace(
            name="text(<<silo_tomatoesaudience_rating>>)",
            mapping_name="MissingRating",
            variables=["silo_tomatoesaudience_rating"],
            updated=False,
            image=None,
            queue_name=None,
            level="movie",
            get_overlay_compare=lambda: "rating-hash",
        )
        library.fetch_overlay_value = lambda *args: None
    engine = Overlays.__new__(Overlays)
    engine.library = library
    engine.cache = None
    engine.compile_overlays = lambda: ({item.ratingKey: (item, list(properties))}, properties)
    engine.run_overlays()
    engine.run_overlays()
    assert downloads == ["https://example.com/poster.jpg"]
    uploads = [call for call in session.calls if call["method"] == "POST"]
    assert len(uploads) == 2
    assert logger.error_messages == []
    assert [message for message in logger.info_messages if "Overlays Applied:" in message] == ["  Overlays Applied: Blur"] * 2


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
    events = []

    def publish(location, filename=None, timeout=60):
        events.append("publish")
        return published

    monkeypatch.setattr(silo_module, "publish_image", publish)
    monkeypatch.setattr(silo_module.time, "sleep", lambda delay: events.append(("wait", delay)))
    session = FakeSession([FakeResponse({"content_id": "movie:heat-1995"})])
    library = _library(SiloClient(_server(), session=session))
    item = SiloItem({"content_id": "movie:heat-1995", "title": "Heat"}, library)

    assert library.upload_poster(item, str(poster)) is True
    assert events == ["publish", ("wait", 0.75)]
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
    clock = iter(range(10))
    monkeypatch.setattr(silo_module.time, "monotonic", lambda: next(clock))
    monkeypatch.setattr(silo_module.time, "sleep", lambda delay: pytest.fail("Remote URLs must not wait for publishing"))
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


@pytest.mark.parametrize("windows", [True, False])
@pytest.mark.parametrize("overlay", [True, False])
def test_silo_item_assets_use_media_folder_and_preserve_overlay(tmp_path, monkeypatch, windows, overlay):
    from modules import library as library_module
    from modules import plex as plex_module

    for module in (silo_module, library_module, plex_module):
        monkeypatch.setattr(module, "logger", FakeLogger())
    session = FakeSession([FakeResponse(None, status_code=204) for _ in range(1 if overlay else 2)])
    library = _library(SiloClient(_server(), session=session))
    library.config.Cache = None
    library.asset_directory = [str(tmp_path / "assets")]
    library.collection_asset_directory = []
    library.asset_folders = True
    library.asset_depth = 0
    library.create_asset_folders = False
    library.dimensional_asset_rename = False
    library.show_missing_assets = True
    library.show_asset_not_needed = False
    library.overlay_backup = str(tmp_path / "backups")
    directory = tmp_path / "assets" / "127 Hours (2010)"
    directory.mkdir(parents=True)
    (directory / "poster.jpg").write_bytes(b"poster")
    (directory / "background.jpg").write_bytes(b"background")
    if overlay:
        backup = tmp_path / "backups"
        backup.mkdir()
        (backup / "movie-1.jpg").write_bytes(b"original")
    path = r"C:\Movies\127 Hours (2010)\movie.mkv" if windows else "/Movies/127 Hours (2010)/movie.mkv"
    item = SiloItem({"content_id": "movie-1", "type": "movie", "title": "127 Hours", "versions": [{"file_path": path}]}, library)
    monkeypatch.setattr(silo_module, "publish_image", lambda *args, **kwargs: "https://images.example/asset.jpg")
    monkeypatch.setattr(silo_module.time, "sleep", lambda *args: None)
    library.find_and_upload_assets(item, [])
    assert [call["json"]["type"] for call in session.calls] == (["backdrop"] if overlay else ["poster", "backdrop"])
    assert all(call["url"].endswith("/movie-1/images/apply") for call in session.calls)


def test_operations_reload_upgrades_catalog_and_reuses_full_details():
    record = {"content_id": "movie-1", "title": "Example", "type": "movie", "versions": [{"file_path": "/Movies/Example/movie.mkv"}]}
    session = FakeSession([FakeResponse(record)])
    library = _library(SiloClient(_server(), session=session))
    item = SiloItem({"content_id": "movie-1", "title": "Example", "type": "movie"}, library)
    library._search_details = {item.content_id: item}
    library.bulk_reload([item])
    library.reload(item)
    assert item.locations == ["/Movies/Example/movie.mkv"]
    assert len(session.calls) == 1


def test_silo_native_rating_writes_are_batched_and_profile_scoped():
    session = FakeSession([FakeResponse({"content_id": "movie-1", "title": "Example"}), FakeResponse(None, status_code=204), FakeResponse(None, status_code=204)])
    library = _library(SiloClient(_server(), session=session))
    item = SiloItem({"content_id": "movie-1", "title": "Example", "type": "movie"}, library)
    library._native_rating_details = {"movie-1": {"rating_imdb": 1}}
    library.update_native_ratings(item, {"rating_imdb": 8.2, "rating_rt_critic": 75, "user_rating": 4})
    assert session.calls[0]["method"] == "PATCH"
    assert session.calls[0]["json"] == {"rating_imdb": 8.2, "rating_rt_critic": 75}
    assert session.calls[1]["method"] == "PUT"
    assert session.calls[1]["json"] == {"rating": 4}
    assert session.calls[1]["url"].endswith("/ratings/movie-1")
    assert session.calls[1]["profile"] == "profile"
    assert "movie-1" not in library._native_rating_details
    library.update_native_ratings(item, {"user_rating": None})
    assert session.calls[2]["method"] == "DELETE"
    assert item.data["user_rating"] is None


def test_native_mass_image_failure_is_reported_without_aborting(monkeypatch):
    from modules import library as library_module

    logger = FakeLogger()
    monkeypatch.setattr(library_module, "logger", logger)
    library = _library(SiloClient(_server(), session=FakeSession([])))
    library.client.apply_item_image = MagicMock(side_effect=Failed("server rejected image"))
    item = SiloItem({"content_id": "movie-1", "title": "Example", "type": "movie"}, library)
    assert library.poster_update(item, None, tmdb=("tmdb", "https://images.example/poster.jpg")) == ("Reset", "tmdb", "Failed")
    assert any("Example" in message and "server rejected image" in message for message in logger.error_messages)


def test_silo_show_episodes_are_gathered_from_its_seasons():
    library = SimpleNamespace(list_seasons=MagicMock(), list_episodes=MagicMock(return_value=["episode"]))
    show = SiloItem({"content_id": "series-1", "type": "series", "title": "Example"}, library)
    season = SiloItem({"content_id": "season-1", "type": "season", "season_number": 1}, library)
    library.list_seasons.return_value = [season]
    assert show.episodes() == ["episode"]
    library.list_episodes.assert_called_once_with(season)
