"""Jellyfin and Emby media server client, capability matrix, and library operations."""

import base64
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
import requests

import modules.builder  # noqa: F401 — pre-import to break circular deps
import modules.mediabrowser as browser_module
from modules.media_server import Capability, Support, build_media_server, media_server_class
from modules.mediabrowser import EMBY_CAPABILITIES, JELLYFIN_CAPABILITIES, Emby, EmbyMediaServer, Jellyfin, JellyfinMediaServer, MediaBrowserClient, MediaBrowserCollection, MediaBrowserItem
from modules.util import Failed
from tests.conftest import FakeLogger, FakeResponse

browser_module.logger = FakeLogger()


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
@pytest.mark.parametrize("os_name,display,expected", [("Linux", "Unix", "Linux"), ("Linux", "Debian GNU/Linux 12", "Debian GNU/Linux 12"), ("", "", "")])
def test_server_info_reads_remote_version_and_os(kind, os_name, display, expected):
    session = FakeSession([FakeResponse({"ServerName": "Remote", "Version": "1.2.3", "OperatingSystem": os_name, "OperatingSystemDisplayName": display})])
    info = MediaBrowserClient(_server(kind), session=session).server_info()
    assert info == {"name": "Remote", "version": "1.2.3", "os": expected, "os_version": None}
    assert session.calls[0]["url"].endswith("/System/Info")


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
def test_library_connection_logs_remote_server_information(monkeypatch, kind):
    server = _server(kind)
    monkeypatch.setattr(browser_module.Library, "__init__", lambda self, config, params: setattr(self, "server", server))
    logger = FakeLogger()
    monkeypatch.setattr(browser_module, "logger", logger)
    client = MagicMock()
    client.virtual_folders.return_value = [{"Name": "Movies", "ItemId": "lib-1", "CollectionType": "movies"}]
    client.server_info.return_value = {"name": "Remote", "version": "1.2.3", "os": "Linux"}
    (Jellyfin if kind == "jellyfin" else Emby)(None, {"name": "Movies"}, client=client)
    assert "Connected to server Remote version 1.2.3" in logger.info_messages
    assert "Running on Linux" in logger.info_messages


def test_people_search_uses_catalog_then_lazily_upgrades_for_track_search():
    detail = {"Id": "1", "Name": "Movie", "Type": "Movie", "MediaStreams": [{"Type": "Audio", "Language": "eng"}]}
    session = FakeSession([FakeResponse(detail)])
    library = _library(MediaBrowserClient(_server("emby"), session=session), kind="emby")
    library.get_all = lambda: [MediaBrowserItem({"Id": "1", "Name": "Movie", "Type": "Movie", "People": [{"Name": "Robert De Niro", "Type": "Actor"}]}, library)]
    people = library.build_local_search({"local_collection_search": {"sort_by": "release.desc", "any": {"actor": "Robert De Niro"}}})
    assert library.get_rating_keys("plex_search", people) == [("1", "ratingKey")]
    assert session.calls == []
    tracks = library.build_local_search({"local_collection_search": {"sort_by": "title.asc", "all": [{"any": {"audio_language": "en"}}]}})
    assert library.get_rating_keys("plex_search", tracks) == [("1", "ratingKey")]
    assert library.get_rating_keys("plex_search", tracks) == [("1", "ratingKey")]
    assert len(session.calls) == 1


def test_local_search_reports_scan_progress_and_checkpoints(monkeypatch):
    logger = MagicMock()
    monkeypatch.setattr(browser_module, "logger", logger)
    monkeypatch.setattr(browser_module, "PAGE_SIZE", 2)
    library = _library(MediaBrowserClient(_server(), session=FakeSession([])))
    library.get_all = lambda: [MediaBrowserItem({"Id": str(i), "Name": f"Movie {i}", "Type": "Movie"}, library) for i in range(3)]
    assert len(list(library._local_search_items(require_media=False))) == 3
    assert [call.args[0] for call in logger.ghost.call_args_list] == ["Scanning: 1/3 Movie 0", "Scanning: 2/3 Movie 1", "Scanning: 3/3 Movie 2"]
    logger.info.assert_any_call("Scanned: 2/3")
    logger.info.assert_any_call("Scanned: 3/3")
    logger.exorcise.assert_called_once()


def test_local_search_clears_progress_on_detail_failure(monkeypatch):
    logger = MagicMock()
    monkeypatch.setattr(browser_module, "logger", logger)
    client = MediaBrowserClient(_server(), session=FakeSession([]))
    client.get_item = MagicMock(side_effect=Failed("Details failed"))
    library = _library(client)
    library.get_all = lambda: [MediaBrowserItem({"Id": "1", "Name": "Movie", "Type": "Movie"}, library)]
    with pytest.raises(Failed, match="Details failed"):
        list(library._local_search_items())
    logger.ghost.assert_called_once_with("Scanning: 1/1 Movie")
    logger.exorcise.assert_called_once()


def test_new_jellyfin_collection_is_locked_before_provider_refresh():
    session = FakeSession([FakeResponse({"Id": "collection"})])
    MediaBrowserClient(_server(), session=session).create_collection("Best of 2016")
    assert session.calls[0]["params"] == {"name": "Best of 2016", "isLocked": "true"}


@pytest.mark.parametrize("path", ["/collections/Best of 2016 [boxset]", r"C:\collections\Best of 2016 [boxset]"])
def test_recovers_provider_renamed_collection_using_original_folder(path):
    record = {"Id": "collection", "Name": "Best of the Best Collection", "Path": path, "ProviderIds": {"Tmdb": "wrong"}, "Overview": "Keep"}
    session = FakeSession([FakeResponse(record), FakeResponse(None, status_code=204)])
    library = _library(MediaBrowserClient(_server(), session=session))
    collection = library._wrap_collection(record)
    library._collections = lambda: [collection]
    result = library.get_collection("Best of 2016")
    assert result.ratingKey == "collection"
    assert result.title == "Best of 2016"
    assert session.calls[-1]["json"] == {**record, "Name": "Best of 2016", "LockData": True, "ProviderIds": {}}
    assert library.get_collection("Best of 2016") is result
    assert len(session.calls) == 2


def test_renamed_collection_recovery_rejects_ambiguous_or_missing_folder_matches():
    library = _library(MediaBrowserClient(_server(), session=FakeSession([])))
    library._collections = lambda: [library._wrap_collection({"Id": str(i), "Name": "Wrong", "Path": f"/collections/{i}/Best of 2016 [boxset]"}) for i in range(2)]
    with pytest.raises(Failed, match="Multiple renamed collections"):
        library.get_collection("Best of 2016")
    with pytest.raises(Failed, match="not found"):
        library.get_collection("Best of 2017")


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
def test_dynamic_years_and_decades_match_native_production_years(kind):
    library = _library(MediaBrowserClient(_server(kind), session=FakeSession([])), kind=kind)
    years = [1989, 1990, 1999, 2000, None, 0, True, "unknown", 10000]
    library.get_all = lambda: [MediaBrowserItem({"Id": str(i), "Name": f"Movie {i}", "Type": "Movie", "ProductionYear": year, "MediaSources": [], "CriticRating": i}, library) for i, year in enumerate(years)]
    assert [(tag.key, tag.title) for tag in library.get_tags("decade")] == [("1980", "1980s"), ("1990", "1990s"), ("2000", "2000s")]
    assert [tag.key for tag in library.get_tags("year")] == ["1989", "1990", "1999", "2000"]
    search = library.build_local_search({"local_collection_search": {"sort_by": "critic_rating.desc", "limit": 100, "any": {"decade": "1990"}}})
    assert library.get_rating_keys("plex_search", search) == [("2", "ratingKey"), ("1", "ratingKey")]
    search = library.build_local_search({"local_collection_search": {"sort_by": "title.asc", "any": {"year": "2000"}}})
    assert library.get_rating_keys("plex_search", search) == [("3", "ratingKey")]


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
@pytest.mark.parametrize("prefix", ["", "episode."])
def test_resolution_dynamic_keys_match_default_selectors(kind, prefix):
    library = _library(MediaBrowserClient(_server(kind), session=FakeSession([])), kind=kind)
    resolutions = [("480", 720, 480), ("576", 720, 576), ("720", 1280, 720), ("1080", 1920, 800), ("2k", 2560, 1440), ("4k", 3840, 1600), ("8k", 7680, 4320)]
    items = [MediaBrowserItem({"Id": key, "Name": key, "Type": "Movie", "MediaSources": [{"MediaStreams": [{"Type": "Video", "Width": width, "Height": height}]}]}, library) for key, width, height in resolutions]
    items.append(MediaBrowserItem({"Id": "unknown", "Name": "Unknown", "Type": "Movie", "MediaSources": []}, library))
    library.get_all = MagicMock(return_value=items)
    assert {tag.key for tag in library.get_tags(prefix + "resolution")} == {key for key, _, _ in resolutions}
    if prefix:
        library.get_all.assert_called_with(builder_level="episode")
    for aliases, expected in [([480, 576, "sd"], {"480", "576"}), (["1080", "2k"], {"1080", "2k"}), (["4k", "8k"], {"4k", "8k"}), (["1080p"], {"1080"})]:
        search = library.build_local_search({"local_collection_search": {"sort_by": "title.asc", "any": {"resolution": aliases}}})
        assert {key for key, _ in library.get_rating_keys("plex_search", search)} == expected


def test_resolution_discovery_includes_alternate_versions():
    library = _library(MediaBrowserClient(_server(), session=FakeSession([])))
    library.get_all = lambda: [
        MediaBrowserItem({"Id": "1", "Name": "Movie", "Type": "Movie", "MediaSources": [{"MediaStreams": [{"Type": "Video", "Width": 1920, "Height": 1080}]}, {"MediaStreams": [{"Type": "Video", "Width": 3840, "Height": 2160}]}]}, library)
    ]
    assert [tag.key for tag in library.get_tags("resolution")] == ["1080", "4k"]


@pytest.mark.parametrize("raw,expected", [("eng", "en"), ("fra", "fr"), ("fre", "fr"), ("deu", "de"), ("ger", "de"), ("ces", "cs"), ("cze", "cs"), ("zho", "zh"), ("chi", "zh"), (" EN ", "en"), ("fil", "fil"), ("und", "und")])
def test_language_defaults_use_canonical_codes_for_discovery_and_matching(raw, expected):
    from pathlib import Path

    from ruamel.yaml import YAML

    library = _library(MediaBrowserClient(_server(), session=FakeSession([])))
    library.get_all = lambda: [MediaBrowserItem({"Id": "1", "Name": "Movie", "Type": "Movie", "MediaStreams": [{"Type": "Audio", "Language": raw}]}, library)]
    assert [tag.key for tag in library.get_tags("audioLanguage")] == [expected]
    for code in (raw, expected):
        search = library.build_local_search({"local_collection_search": {"sort_by": "title.asc", "any": {"audio_language": code}}})
        assert library.get_rating_keys("plex_search", search) == [("1", "ratingKey")]
    with Path("defaults/both/audio_language.yml").open() as handle:
        definition = next(iter(YAML(typ="safe").load(handle)["dynamic_collections"].values()))
    if expected != "und":
        assert expected in definition["include"]


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
@pytest.mark.parametrize("prefix", ["", "episode."])
def test_dynamic_track_languages_match_all_versions_and_external_subtitles(kind, prefix):
    library = _library(MediaBrowserClient(_server(kind), session=FakeSession([])), kind=kind)
    item = MediaBrowserItem(
        {
            "Id": "1",
            "Name": "Movie",
            "Type": "Movie",
            "MediaSources": [
                {"MediaStreams": [{"Type": "Audio", "Language": " ENG "}, {"Type": "Audio", "Language": "eng"}, {"Type": "Subtitle", "Language": "fra"}, {"Type": "Audio"}]},
                {"MediaStreams": [{"Type": "Audio", "Language": "deu"}, {"Type": "Subtitle", "Language": "jpn", "IsExternal": True}, {"Type": "Subtitle", "Language": " "}]},
            ],
        },
        library,
    )
    unknown = MediaBrowserItem({"Id": "2", "Name": "Unknown", "Type": "Movie", "MediaSources": []}, library)
    library.get_all = MagicMock(return_value=[item, unknown])
    for alias in ("audioLanguage", "audio_language"):
        assert [tag.key for tag in library.get_tags(prefix + alias)] == ["de", "en"]
    for alias in ("subtitleLanguage", "subtitle_language"):
        assert [(tag.key, tag.title) for tag in library.get_tags(prefix + alias)] == [("fr", "fr"), ("ja", "ja")]
    if prefix:
        library.get_all.assert_called_with(builder_level="episode")
    for selector in ({"audio_language": "eng"}, {"subtitle_language": "jpn"}, {"audio_language.not": "fra"}):
        search = library.build_local_search({"local_collection_search": {"sort_by": "title.asc", "all": selector}})
        assert library.get_rating_keys("plex_search", search) == [("1", "ratingKey")]
    assert library.get_rating_keys("plex_search", library.build_local_search({"all": {"audio_language": "zzz"}})) == []


def test_dynamic_languages_load_and_reuse_item_details():
    detail = {"Id": "1", "Name": "Movie", "Type": "Movie", "MediaStreams": [{"Type": "Audio", "Language": "eng"}, {"Type": "Subtitle", "Language": "fra", "IsExternal": True}]}
    session = FakeSession([FakeResponse(detail)])
    library = _library(MediaBrowserClient(_server(), session=session))
    library.get_all = lambda: [MediaBrowserItem({"Id": "1", "Name": "Movie", "Type": "Movie"}, library)]
    assert [tag.key for tag in library.get_tags("audioLanguage")] == ["en"]
    assert [tag.key for tag in library.get_tags("subtitleLanguage")] == ["fr"]
    assert len(session.calls) == 1


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
@pytest.mark.parametrize("tag", ["contentRating", "content_rating"])
def test_dynamic_content_ratings_discovery_and_collection_selection(kind, tag):
    library = _library(MediaBrowserClient(_server(kind), session=FakeSession([])), kind=kind)
    records = [{"Id": str(i), "Name": f"Movie {i}", "Type": "Movie", "OfficialRating": rating, "MediaSources": []} for i, rating in enumerate(["R", "PG", "PG-13", "R", None, ""])]
    library.get_all = lambda: [MediaBrowserItem(record, library) for record in records]
    assert [(tag.key, tag.title) for tag in library.get_tags(tag)] == [("PG", "PG"), ("PG-13", "PG-13"), ("R", "R")]
    definition = {"sort_by": "title.asc", "any": {"content_rating": ["PG"]}}
    search = library.build_local_search({"local_collection_search": definition})
    assert library.get_rating_keys("plex_search", search) == [("1", "ratingKey")]
    other = library.build_local_search({"local_collection_search": {"sort_by": "title.asc", "all": {"content_rating.not": ["R", "PG"]}}})
    assert library.get_rating_keys("plex_search", other) == [("2", "ratingKey")]


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
def test_dynamic_tags_use_native_library_values(kind):
    library = _library(MediaBrowserClient(_server(kind), session=FakeSession([])), kind=kind)
    library.get_all = lambda: [MediaBrowserItem({"Id": "1", "Name": "Movie", "Type": "Movie", "Genres": ["Drama", "Drama"], "Studios": [{"Name": "Studio"}], "ProductionLocations": ["Canada"]}, library)]
    for field, expected in [("genre", "Drama"), ("studio", "Studio"), ("country", "Canada")]:
        assert [(tag.key, tag.title) for tag in library.get_tags(field)] == [(expected, expected)]
    with pytest.raises(Failed, match="Dynamic collection tag 'unsupported' is not supported"):
        library.get_tags("unsupported")


class FakeSession:
    def __init__(self, responses):
        self.headers = {}
        self.verify = True
        self.calls = []
        self.responses = list(responses)

    def request(self, method, url, params=None, json=None, data=None, headers=None, timeout=None):
        self.calls.append({"method": method, "url": url, "params": params, "json": json, "data": data, "headers": headers, "timeout": timeout})
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
@pytest.mark.parametrize("method", ["smart_filter", "smart_url", "smart_label"])
def test_builder_rejects_smart_options_before_server_requests(kind, method):
    from modules.builder import CollectionBuilder
    from modules.util import BuilderValidationError

    session = FakeSession([])
    library = _library(MediaBrowserClient(_server(kind), session=session), kind=kind)
    with pytest.raises(BuilderValidationError, match=f"{method} is not supported.*builder-based collection"):
        CollectionBuilder(None, None, "Newly Released", {method: {"any": {"unsupported_field": 90}}}, library=library)
    assert session.calls == []


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
@pytest.mark.parametrize("method", ["smart_filter", "smart_url", "smart_label"])
def test_builder_validates_smart_options_added_by_templates(monkeypatch, kind, method):
    from modules import builder as builder_module
    from modules.builder import CollectionBuilder
    from modules.util import BuilderValidationError

    monkeypatch.setattr(builder_module, "logger", FakeLogger())
    session = FakeSession([])
    library = _library(MediaBrowserClient(_server(kind), session=session), kind=kind)
    metadata = SimpleNamespace(apply_template=lambda *args: {method: {"any": {"unsupported_field": 90}}})
    with pytest.raises(BuilderValidationError, match=f"{method} is not supported.*builder-based collection"):
        CollectionBuilder(None, metadata, "Newly Released", {"template": {"name": "smart_filter"}}, library=library)
    assert session.calls == []


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
@pytest.mark.parametrize("error", [requests.ConnectionError("Connection reset by peer"), requests.Timeout("timed out")])
def test_read_retries_transient_connection_errors(monkeypatch, kind, error):
    delays = []
    monkeypatch.setattr(browser_module.time, "sleep", delays.append)
    session = FakeSession([error, FakeResponse({"Items": [], "TotalRecordCount": 0})])
    client = MediaBrowserClient(_server(kind), session=session)
    assert client.items({"includeItemTypes": "BoxSet"}) == []
    assert delays == [1]
    assert session.calls[0] == session.calls[1]


def test_read_connection_retries_are_bounded(monkeypatch):
    delays = []
    monkeypatch.setattr(browser_module.time, "sleep", delays.append)
    session = FakeSession([requests.ConnectionError("reset") for _ in range(3)])
    client = MediaBrowserClient(_server("emby"), session=session)
    with pytest.raises(Failed, match="GET /Items failed: reset"):
        client.items({})
    assert len(session.calls) == 3
    assert delays == [1, 2]


@pytest.mark.parametrize("method", ["add_collection_items", "remove_collection_items"])
@pytest.mark.parametrize("error", [requests.ConnectionError("reset"), requests.Timeout("timeout")])
@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
def test_native_membership_retries_only_failed_batch(monkeypatch, kind, method, error):
    delays = []
    monkeypatch.setattr(browser_module.time, "sleep", delays.append)
    session = FakeSession([FakeResponse(None, status_code=204), error, FakeResponse(None, status_code=204)])
    client = MediaBrowserClient(_server(kind), session=session)
    getattr(client, method)("collection", [str(i) for i in range(101)])
    assert len(session.calls) == 3
    assert session.calls[1] == session.calls[2]
    assert session.calls[1]["params"] == {"ids": "100"}
    assert delays == [1]


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
def test_native_membership_retry_limit_preserves_failure(monkeypatch, kind):
    delays = []
    monkeypatch.setattr(browser_module.time, "sleep", delays.append)
    session = FakeSession([requests.ConnectionError("reset") for _ in range(3)])
    with pytest.raises(Failed, match="POST /Collections/collection/Items failed: reset"):
        MediaBrowserClient(_server(kind), session=session).add_collection_items("collection", ["1"])
    assert len(session.calls) == 3
    assert delays == [1, 2]


@pytest.mark.parametrize("error", [requests.exceptions.SSLError("certificate"), requests.RequestException("invalid request"), FakeResponse({}, status_code=400)])
@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
def test_native_membership_does_not_retry_nontransient_errors(monkeypatch, kind, error):
    delays = []
    monkeypatch.setattr(browser_module.time, "sleep", delays.append)
    session = FakeSession([error])
    with pytest.raises(Failed):
        MediaBrowserClient(_server(kind), session=session).add_collection_items("collection", ["1"])
    assert len(session.calls) == 1
    assert delays == []


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
def test_native_collection_creation_recovers_lost_response(monkeypatch, kind):
    delays = []
    monkeypatch.setattr(browser_module.time, "sleep", delays.append)
    session = FakeSession([requests.ConnectionError("reset"), FakeResponse({"Items": [{"Id": "saved", "Name": "Example"}], "TotalRecordCount": 1})])
    assert MediaBrowserClient(_server(kind), session=session).create_collection("Example") == {"Id": "saved"}
    assert [call["method"] for call in session.calls] == ["POST", "GET"]
    assert delays == [1]


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
def test_creation_retries_after_confirming_no_matching_collection(monkeypatch, kind):
    monkeypatch.setattr(browser_module.time, "sleep", lambda _: None)
    session = FakeSession([requests.ConnectionError("reset"), FakeResponse({"Items": [], "TotalRecordCount": 0}), FakeResponse({"Id": "new"})])
    assert MediaBrowserClient(_server(kind), session=session).create_collection("Example") == {"Id": "new"}
    assert session.calls[0] == session.calls[2]


def test_creation_recovery_refuses_ambiguous_matches(monkeypatch):
    monkeypatch.setattr(browser_module.time, "sleep", lambda _: None)
    session = FakeSession([requests.ConnectionError("reset"), FakeResponse({"Items": [{"Id": str(i), "Name": "Example"} for i in range(2)], "TotalRecordCount": 2})])
    with pytest.raises(Failed, match="multiple collections match"):
        MediaBrowserClient(_server("emby"), session=session).create_collection("Example")
    assert len(session.calls) == 2


@pytest.mark.parametrize("status", [204, 404])
def test_item_deletion_retries_and_accepts_already_deleted_item(monkeypatch, status):
    delays = []
    monkeypatch.setattr(browser_module.time, "sleep", delays.append)
    session = FakeSession([requests.ConnectionError("reset"), FakeResponse(None, status_code=status)])
    MediaBrowserClient(_server("emby"), session=session).delete_item("123")
    assert session.calls[0] == session.calls[1]
    assert delays == [1]


def test_item_deletion_does_not_hide_initial_not_found():
    session = FakeSession([FakeResponse({}, status_code=404)])
    with pytest.raises(Failed, match="returned 404"):
        MediaBrowserClient(_server("emby"), session=session).delete_item("123")


def test_creation_lookup_failure_does_not_replay_creation(monkeypatch):
    monkeypatch.setattr(browser_module.time, "sleep", lambda _: None)
    session = FakeSession([requests.ConnectionError("reset")])
    client = MediaBrowserClient(_server("emby"), session=session)
    client.items = MagicMock(side_effect=Failed("lookup unavailable"))
    with pytest.raises(Failed, match="lookup unavailable"):
        client.create_collection("Example")
    assert len(session.calls) == 1


def test_shared_request_policy_retries_item_metadata_without_opt_in(monkeypatch):
    monkeypatch.setattr(browser_module.time, "sleep", lambda _: None)
    session = FakeSession([requests.ConnectionError("reset"), FakeResponse(None, status_code=204)])
    client = MediaBrowserClient(_server("emby"), session=session)
    client.request("POST", "/Items/123", json_body={"Name": "Example"})
    assert session.calls[0] == session.calls[1]


def test_creation_retries_remain_bounded(monkeypatch):
    delays = []
    monkeypatch.setattr(browser_module.time, "sleep", delays.append)
    session = FakeSession([requests.ConnectionError("reset"), FakeResponse({"Items": [], "TotalRecordCount": 0}), requests.ConnectionError("reset"), FakeResponse({"Items": [], "TotalRecordCount": 0}), requests.ConnectionError("reset")])
    with pytest.raises(Failed, match="POST /Collections failed"):
        MediaBrowserClient(_server("emby"), session=session).create_collection("Example")
    assert [call["method"] for call in session.calls] == ["POST", "GET", "POST", "GET", "POST"]
    assert delays == [1, 2]


def test_emby_creation_continues_after_membership_retry(monkeypatch):
    delays = []
    monkeypatch.setattr(browser_module.time, "sleep", delays.append)
    session = FakeSession([FakeResponse({"Id": "collection"}), requests.ConnectionError("reset"), FakeResponse(None, status_code=204), FakeResponse(None, status_code=204)])
    client = MediaBrowserClient(_server("emby"), session=session)
    assert client.create_collection("480 Movies", item_ids=[str(i) for i in range(201)]) == {"Id": "collection"}
    assert session.calls[0]["url"].endswith("/Collections")
    assert session.calls[1] == session.calls[2]
    assert session.calls[3]["params"] == {"ids": "200"}
    assert delays == [1]


@pytest.mark.parametrize("method,error", [("POST", requests.ConnectionError("reset")), ("DELETE", requests.Timeout("timeout")), ("GET", requests.exceptions.SSLError("certificate")), ("GET", requests.RequestException("invalid request"))])
def test_unsafe_or_nontransient_requests_are_not_retried(monkeypatch, method, error):
    delays = []
    monkeypatch.setattr(browser_module.time, "sleep", delays.append)
    session = FakeSession([error])
    with pytest.raises(Failed):
        MediaBrowserClient(_server("emby"), session=session).request(method, "/Items")
    assert len(session.calls) == 1
    assert delays == []


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


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
@pytest.mark.parametrize("exists", [True, False])
def test_builder_adds_to_collection_by_title(monkeypatch, kind, exists):
    from modules import builder as builder_module
    from tests.factories import make_builder

    monkeypatch.setattr(builder_module, "logger", FakeLogger())
    record = {"Id": "col-trek", "Name": "Star Trek Stuff", "Type": "BoxSet"}
    responses = [FakeResponse({"Items": [record] if exists else [], "TotalRecordCount": int(exists)})]
    seeded_creation = kind == "emby" and not exists
    if seeded_creation:
        responses.append(FakeResponse({"Id": "col-trek"}))
    elif not exists:
        responses.extend([FakeResponse({"Id": "col-trek"}), FakeResponse(record)])
    if not seeded_creation:
        responses.append(FakeResponse(None, status_code=204))
    session = FakeSession(responses)
    library = _library(MediaBrowserClient(_server(kind), session=session), kind=kind)
    item = MediaBrowserItem({"Id": "movie-1", "Name": "The Wrath of Khan", "Type": "Movie"}, library)
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
    assert session.calls[-1]["method"] == "POST"
    assert session.calls[-1]["url"].endswith("/Collections" if seeded_creation else "/Collections/col-trek/Items")
    assert session.calls[-1]["params"]["ids"] == "movie-1"
    creations = [call for call in session.calls if call["url"].endswith("/Collections")]
    assert len(creations) == (0 if exists else 1)
    if creations:
        assert creations[0]["params"]["name"] == "Star Trek Stuff"
    if seeded_creation:
        assert creations[0]["params"] == {"name": "Star Trek Stuff", "ids": "movie-1"}
        assert len(session.calls) == 2
    assert session.responses == []


def test_emby_collection_creation_includes_all_initial_members():
    session = FakeSession([FakeResponse({"Items": [], "TotalRecordCount": 0}), FakeResponse({"Id": "new"})])
    library = _library(MediaBrowserClient(_server("emby"), session=session), kind="emby")
    library.alter_collection(["558", "410", "348"], "Star Trek Stuff")
    assert session.calls[1]["params"] == {"name": "Star Trek Stuff", "ids": "558,410,348"}
    assert len(session.calls) == 2


def test_emby_blank_collection_reports_required_members():
    session = FakeSession([FakeResponse({"Items": [], "TotalRecordCount": 0})])
    library = _library(MediaBrowserClient(_server("emby"), session=session), kind="emby")
    with pytest.raises(Failed, match="requires initial members") as error:
        library.create_blank_collection("Empty")
    for text in ("separator collections", "placeholder_imdb_id", "placeholder_tmdb_movie", "placeholder_tvdb_show", "template_variables", "item present in this library"):
        assert text in str(error.value)
    assert len(session.calls) == 1


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
def test_collection_lookup_and_removal_accept_title_strings(kind):
    record = {"Id": "col-trek", "Name": "Star Trek Stuff", "Type": "BoxSet"}
    listing = {"Items": [record], "TotalRecordCount": 1}
    session = FakeSession([FakeResponse(listing), FakeResponse(listing), FakeResponse(None, status_code=204)])
    library = _library(MediaBrowserClient(_server(kind), session=session), kind=kind)
    assert library.get_collection("Star Trek Stuff").ratingKey == "col-trek"
    library.alter_collection(["movie-1"], "Star Trek Stuff", add=False)
    assert session.calls[-1]["method"] == "DELETE"
    assert session.calls[-1]["url"].endswith("/Collections/col-trek/Items")


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
@pytest.mark.parametrize("folders", [True, False])
@pytest.mark.parametrize("present", [True, False])
def test_collection_metadata_discovers_and_uploads_assets(tmp_path, monkeypatch, kind, folders, present):
    from modules import builder as builder_module
    from modules import library as library_module
    from modules import plex as plex_module
    from tests.factories import make_builder

    for module in (builder_module, library_module, plex_module):
        monkeypatch.setattr(module, "logger", FakeLogger())
    record = {"Id": "col-trek", "Name": "Star Trek Stuff", "Type": "BoxSet", "Tags": ["Kometa"]}
    session = FakeSession([FakeResponse(record), FakeResponse(record), FakeResponse(None, status_code=204), FakeResponse(None, status_code=204), FakeResponse(None, status_code=204)])
    library = _library(MediaBrowserClient(_server(kind), session=session), kind=kind)
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
    if present:
        (directory / ("poster.jpg" if folders else "Trek.jpg")).write_bytes(b"poster")
        (directory / ("background.jpg" if folders else "Trek_background.jpg")).write_bytes(b"background")
    builder = make_builder(
        library=library,
        obj=library._wrap_collection(record),
        name="Star Trek Stuff",
        summaries={},
        details={"name_mapping": "Trek"},
        mapping_name="Star Trek Stuff",
        hub_priority=None,
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
    updated = builder.update_details()
    assert ("Image" in updated) is present
    uploads = [call for call in session.calls if "/Images/" in call["url"]]
    assert len(uploads) == (2 if present else 0)
    if present:
        assert uploads[0]["url"].endswith("/Items/col-trek/Images/Primary")
        assert base64.b64decode(uploads[0]["data"], validate=True) == b"poster"
        assert uploads[1]["url"].endswith("/Items/col-trek/Images/Backdrop")
        assert base64.b64decode(uploads[1]["data"], validate=True) == b"background"


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
@pytest.mark.parametrize("image_type,content_type", [("Primary", "image/png"), ("Backdrop", "image/jpeg"), ("Logo", "image/webp")])
def test_image_upload_sends_base64_body(kind, image_type, content_type):
    content = bytes(range(256))
    session = FakeSession([FakeResponse(None, status_code=204)])
    client = MediaBrowserClient(_server(kind), session=session)
    client.upload_image("item-1", image_type, content, content_type)
    call = session.calls[0]
    assert call["method"] == "POST"
    assert call["url"].endswith(f"/Items/item-1/Images/{image_type}")
    assert call["headers"] == {"Content-Type": content_type}
    assert base64.b64decode(call["data"], validate=True) == content
    assert call["json"] is None


def test_emby_tmdb_builder_fetches_user_scoped_item_details(monkeypatch):
    from modules import builder as builder_module
    from tests.factories import make_builder

    monkeypatch.setattr(builder_module, "logger", FakeLogger())
    record = {"Id": "558", "Name": "Star Trek", "Type": "Movie", "ProviderIds": {"Tmdb": "152"}}
    session = FakeSession([FakeResponse(record)])
    library = _library(MediaBrowserClient(_server("emby"), session=session), kind="emby")
    library.movie_map = {152: ["558"]}
    builder = make_builder(library=library, libraries=[library], parts_collection=False, check_value_filter=lambda item: True)
    builder.filter_and_save_items([(152, "tmdb")])
    assert [item.ratingKey for item in builder.found_items] == ["558"]
    assert session.calls[0]["url"].endswith("/Users/user-1/Items/558")


def test_emby_item_read_discovers_user_when_unconfigured():
    session = FakeSession([FakeResponse([{"Id": "admin", "Policy": {"IsAdministrator": True}}]), FakeResponse({"Id": "558"})])
    client = MediaBrowserClient(_server("emby", user_id=None), session=session)
    assert client.get_item("558") == {"Id": "558"}
    assert session.calls[0]["url"].endswith("/Users")
    assert session.calls[1]["url"].endswith("/Users/admin/Items/558")


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
def test_metadata_update_uses_server_item_read_route(kind):
    session = FakeSession([FakeResponse({"Id": "558", "Name": "Star Trek", "Overview": "Old"}), FakeResponse(None, status_code=204)])
    client = MediaBrowserClient(_server(kind), session=session)
    client.update_item("558", {"Overview": "New"})
    read_path = "/Users/user-1/Items/558" if kind == "emby" else "/Items/558"
    assert session.calls[0]["url"].endswith(read_path)
    assert session.calls[1]["url"].endswith("/Items/558")
    assert session.calls[1]["method"] == "POST"
    assert session.calls[1]["json"] == {"Id": "558", "Name": "Star Trek", "Overview": "New"}


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
@pytest.mark.parametrize("custom_sort", ["custom", "custom.desc", ["title.asc", "year.asc"]])
def test_builder_skips_unsupported_collection_ordering(monkeypatch, kind, custom_sort):
    from modules import builder as builder_module
    from tests.factories import make_builder

    logger = FakeLogger()
    monkeypatch.setattr(builder_module, "logger", logger)
    monkeypatch.setattr(browser_module, "logger", logger)
    session = FakeSession([])
    library = _library(MediaBrowserClient(_server(kind), session=session), kind=kind)
    builder = make_builder(library=library, name="IMDb Lowest Rated", custom_sort=custom_sort)
    builder.sort_collection()
    assert session.calls == []
    assert len(logger.warning_messages) == 1
    assert "Custom item ordering is not supported" in logger.warning_messages[0]
    assert logger.error_messages == []


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
def test_overlay_plex_search_reports_unsupported_translation(monkeypatch, kind):
    from modules import builder as builder_module
    from tests.factories import make_builder

    monkeypatch.setattr(builder_module, "logger", FakeLogger())
    session = FakeSession([])
    library = _library(MediaBrowserClient(_server(kind), session=session), kind=kind)
    builder = make_builder(library=library, Type="Overlay", overlay=True)
    with pytest.raises(Failed, match="Unsupported local search field"):
        builder._plex("plex_search", {"all": {"unsupported_field.regex": "Director.*Cut"}})
    assert session.calls == []


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
def test_local_overlay_resolution_selection_and_filters(monkeypatch, kind):
    from modules import builder as builder_module
    from tests.factories import make_builder

    monkeypatch.setattr(builder_module, "logger", FakeLogger())
    detail = {"Id": "558", "Name": "Example", "Type": "Movie", "MediaSources": [{"Path": "/Movies/Example.DV.HDR10+.mkv", "MediaStreams": [{"Type": "Video", "Width": 3840, "Height": 1600, "VideoRangeType": "DOVIWithHDR10", "DvProfile": 8}]}]}
    session = FakeSession([FakeResponse(detail)])
    library = _library(MediaBrowserClient(_server(kind), session=session), kind=kind)
    library.get_all = lambda: [MediaBrowserItem({"Id": "558", "Name": "Example", "Type": "Movie"}, library)]
    builder = make_builder(library=library, Type="Overlay", overlay=True, current_time=None, check_value_filter=lambda item: True, filters=[[("filepath.regex", [r"(?i)\bdv.HDR10\+"]), ("has_dolby_vision", True)]])
    del builder.check_filters
    builder._plex("plex_search", {"all": {"any": {"resolution.regex": "(?i)2160|4k"}, "hdr": True}})
    method, search = builder.builders[0]
    ids = library.get_rating_keys(method, search)
    assert ids == [("558", "ratingKey")]
    builder.filter_and_save_items(ids)
    assert [item.ratingKey for item in builder.found_items] == ["558"]
    assert library.get_rating_keys(method, search) == ids
    assert len(session.calls) == 1


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
def test_local_overlay_search_does_not_guess_missing_metadata(kind):
    library = _library(MediaBrowserClient(_server(kind), session=FakeSession([])), kind=kind)
    item = MediaBrowserItem({"Id": "1", "Name": "Unknown", "Type": "Movie", "MediaSources": []}, library)
    assert library.check_filters(item, [("has_dolby_vision", False)], None) is False
    assert library.check_filters(item, [("filepath.not", "Director")], None) is False


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
@pytest.mark.parametrize("order,display_order", [("release", "PremiereDate"), ("alpha", "SortName"), ("title.asc", "SortName")])
def test_native_collection_display_order(kind, order, display_order):
    record = {"Id": "col-1", "Name": "Example", "Type": "BoxSet", "Overview": "Keep this"}
    session = FakeSession([FakeResponse(record), FakeResponse(None, status_code=204)])
    library = _library(MediaBrowserClient(_server(kind), session=session), kind=kind)
    collection = library._wrap_collection(record)
    assert library.collection_order_query(collection, order) is True
    assert session.calls[-1]["json"] == {**record, "DisplayOrder": display_order}
    assert collection.data["DisplayOrder"] == display_order
    assert library.collection_order_query(collection, order) is False
    assert len(session.calls) == 2
    assert collection.collectionSort == (0 if display_order == "PremiereDate" else 1)


@pytest.mark.parametrize("field,expected", [("added.asc", "DateCreated"), ("year.asc", "ProductionYear"), ("duration.asc", "Runtime"), ("content_rating.asc", "OfficialRating")])
def test_jellyfin_native_sort_runs_through_builder(monkeypatch, field, expected):
    from modules import builder as builder_module
    from tests.factories import make_builder

    monkeypatch.setattr(builder_module, "logger", FakeLogger())
    session = FakeSession([FakeResponse({"Id": "col-1", "Name": "Example"}), FakeResponse(None, status_code=204)])
    library = _library(MediaBrowserClient(_server(), session=session))
    collection = library._wrap_collection({"Id": "col-1", "Name": "Example"})
    make_builder(library=library, obj=collection, custom_sort=[field]).sort_collection()
    assert session.calls[-1]["json"]["DisplayOrder"] == expected


@pytest.mark.parametrize("kind,order", [("emby", "added.asc"), ("jellyfin", "title.desc"), ("emby", "release.desc")])
def test_unsupported_display_order_does_not_mutate_members(kind, order):
    session = FakeSession([])
    library = _library(MediaBrowserClient(_server(kind), session=session), kind=kind)
    assert library.collection_order_query(library._wrap_collection({"Id": "col-1"}), order) is False
    assert session.calls == []


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
@pytest.mark.parametrize(
    "data,display,sort_title",
    [
        ({"Type": "Movie", "Name": "The Example", "SortName": "Example, The"}, "The Example", "Example, The"),
        ({"Type": "Series", "Name": "Example"}, "Example", "Example"),
        ({"Type": "Season", "Name": "Specials", "SeriesName": "Example", "IndexNumber": 0}, "Example Season 0", "Example Season 0"),
        ({"Type": "Episode", "Name": "Pilot", "SeriesName": "Example", "ParentIndexNumber": 1, "IndexNumber": 2}, "Example S01E02", "Example S01E02"),
        ({"Type": "Episode", "Name": "Unknown"}, "S00E00", "S00E00"),
    ],
)
def test_item_display_titles_do_not_query_server(kind, data, display, sort_title):
    session = FakeSession([])
    library = _library(MediaBrowserClient(_server(kind), session=session), kind=kind)
    item = MediaBrowserItem({"Id": "item-1", **data}, library)
    assert library.get_item_display_title(item) == display
    assert library.get_item_display_title(item, sort=True) == sort_title
    assert session.calls == []


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
def test_overlay_application_uses_native_tags_and_reuses_backup(tmp_path, monkeypatch, kind):
    from PIL import Image

    from modules import overlays as overlays_module
    from modules.overlays import Overlays

    logger = FakeLogger()
    monkeypatch.setattr(overlays_module, "logger", logger)
    record = {"Id": "558", "Name": "Example", "Type": "Movie", "ImageTags": {"Primary": "original"}, "Tags": []}
    session = FakeSession([FakeResponse(None, status_code=204), FakeResponse(record), FakeResponse(None, status_code=204), FakeResponse(None, status_code=204)])
    library = _library(MediaBrowserClient(_server(kind), session=session), kind=kind)
    library.session = session
    library.overlay_backup = str(tmp_path / "backup")
    library.overlay_folder = str(tmp_path)
    library.remove_overlays = library.reapply_overlays = library.assets_for_all = False
    library.reset_overlays = None
    library.is_music = False
    library.asset_directory = library.collection_asset_directory = []
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
    item = MediaBrowserItem(record, library)
    library._search_details = {item.ratingKey: item}
    library.get_all = lambda **kwargs: [item]
    library.search = lambda **kwargs: [item] if kwargs.get("label") in item.tags else []
    definition = SimpleNamespace(name="blur(2)", mapping_name="Blur", variables=[], updated=False, image=None, get_overlay_compare=lambda: "hash")
    engine = Overlays.__new__(Overlays)
    engine.library = library
    engine.cache = None
    engine.compile_overlays = lambda: ({item.ratingKey: (item, ["Blur"])}, {"Blur": definition})
    engine.run_overlays()
    engine.run_overlays()
    assert len(downloads) == 1
    assert item.tags == item.data["Tags"] == ["Overlay"]
    assert len(session.calls) == 4
    assert session.calls[2]["json"]["Tags"] == ["Overlay"]
    uploads = [call for call in session.calls if "/Images/Primary" in call["url"]]
    assert len(uploads) == 2
    for call in uploads:
        assert base64.b64decode(call["data"], validate=True).startswith(b"\x89PNG")
    assert logger.error_messages == []


@pytest.mark.parametrize("width,height,badge", [(428, 240, "480"), (720, 404, "480"), (640, 360, "480"), (720, 480, "480"), (720, 576, "576"), (1024, 432, "576"), (1280, 536, "720"), (1920, 800, "1080"), (3840, 1600, "2160")])
def test_resolution_overlay_categories_include_cropped_video(width, height, badge):
    library = _library(MediaBrowserClient(_server(), session=FakeSession([])))
    item = MediaBrowserItem({"Id": "1", "Name": "Cropped", "Type": "Movie", "MediaStreams": [{"Type": "Video", "Width": width, "Height": height}]}, library)
    assert library.check_filters(item, [("resolution.regex", [badge])], None)


def test_emby_removes_untagged_overlay_using_existing_backup(tmp_path, monkeypatch):
    from PIL import Image

    from modules import overlays as overlays_module
    from modules.overlays import Overlays

    logger = FakeLogger()
    monkeypatch.setattr(overlays_module, "logger", logger)
    record = {"Id": "558", "Name": "Example", "Type": "Movie", "Tags": [], "TagItems": []}
    session = FakeSession([FakeResponse({"Items": [], "TotalRecordCount": 0}), FakeResponse(None, status_code=204), FakeResponse(record), FakeResponse(None, status_code=204)])
    library = _library(MediaBrowserClient(_server("emby"), session=session), kind="emby")
    library.overlay_backup = str(tmp_path / "backup")
    library.overlay_folder = str(tmp_path)
    library.remove_overlays = True
    library.is_music = False
    library.asset_directory = library.collection_asset_directory = []
    library.asset_folders = False
    library.asset_depth = 0
    library.create_asset_folders = False
    item = MediaBrowserItem(record, library)
    library.get_all = lambda **kwargs: [item]
    backup = tmp_path / "backup" / "558.jpg"
    backup.parent.mkdir()
    Image.new("RGB", (10, 15), "red").save(backup)
    original = backup.read_bytes()
    engine = Overlays.__new__(Overlays)
    engine.library = library
    engine.cache = None
    engine.run_overlays()
    assert base64.b64decode(session.calls[1]["data"], validate=True) == original
    assert session.calls[-1]["json"]["TagItems"] == []
    assert not backup.exists()
    assert logger.error_messages == []


def test_emby_reads_and_preserves_native_tag_items():
    record = {"Id": "558", "Name": "Example", "Type": "Movie", "TagItems": [{"Name": "Keep", "Id": 1}, {"Name": "Overlay", "Id": 2}]}
    session = FakeSession([FakeResponse(record), FakeResponse(None, status_code=204)])
    library = _library(MediaBrowserClient(_server("emby"), session=session), kind="emby")
    item = MediaBrowserItem(record, library)
    assert item.tags == ["Keep", "Overlay"]
    library.edit_tags("label", item, remove_tags=["Overlay"], do_print=False)
    assert session.calls[-1]["json"]["TagItems"] == ["Keep"]
    assert session.calls[-1]["json"]["Tags"] == ["Keep"]


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
def test_forced_reload_does_not_queue_server_metadata_refresh(kind):
    session = FakeSession([FakeResponse({"Id": "558", "Name": "Fresh", "Type": "Movie"})])
    library = _library(MediaBrowserClient(_server(kind), session=session), kind=kind)
    item = MediaBrowserItem({"Id": "558", "Name": "Old", "Type": "Movie"}, library)
    library._search_details = {item.ratingKey: item}
    library.bulk_reload([item], force=True)
    assert item.title == "Fresh"
    assert [call["method"] for call in session.calls] == ["GET"]
    assert library.reload(item).title == "Fresh"
    assert len(session.calls) == 1


@pytest.mark.parametrize("kind,field", [("jellyfin", "ForcedSortName"), ("emby", "SortName")])
def test_separator_sort_title_uses_server_write_field(kind, field):
    record = {"Id": "separator", "Name": "Award Collections", "Type": "BoxSet", "SortName": "award collections", "Overview": "Keep"}
    session = FakeSession([FakeResponse(record), FakeResponse(None, status_code=204)])
    if kind == "emby":
        session.responses.append(FakeResponse({**record, "ForcedSortName": "!100_!Award Collections", "SortName": "!100_!Award Collections", "LockedFields": ["SortName"]}))
    library = _library(MediaBrowserClient(_server(kind), session=session), kind=kind)
    item = MediaBrowserCollection(record, library)
    item.editSortTitle("!100_!Award Collections")
    assert session.calls[1]["json"][field] == "!100_!Award Collections"
    assert session.calls[1]["json"]["Overview"] == "Keep"
    item.apply({"Overview": "Updated"})
    assert item.titleSort == "!100_!Award Collections"


@pytest.mark.parametrize("role,prefix", [("Actor", "140"), ("Director", "150"), ("Producer", "160"), ("Writer", "170")])
@pytest.mark.parametrize("forced", [None, "", "Old sort title"])
def test_emby_people_sort_titles_replace_stale_forced_names(role, prefix, forced):
    record = {"Id": "people", "Name": f"Example ({role})", "Type": "BoxSet", "SortName": f"Example ({role})", "ForcedSortName": forced, "Overview": "Keep", "LockedFields": ["Overview"]}
    session = FakeSession([FakeResponse(record), FakeResponse(None, status_code=204)])
    library = _library(MediaBrowserClient(_server("emby"), session=session), kind="emby")
    item = MediaBrowserCollection(record, library)
    expected = f"!{prefix}_Example ({role})"
    session.responses.append(FakeResponse({**record, "ForcedSortName": expected, "SortName": expected, "LockedFields": ["Overview", "SortName"]}))
    item.editSortTitle(expected)
    payload = session.calls[1]["json"]
    assert payload["ForcedSortName"] == payload["SortName"] == expected
    assert payload["Name"] == record["Name"]
    assert payload["Overview"] == "Keep"
    assert payload["LockedFields"] == ["Overview", "SortName"]
    assert [call["method"] for call in session.calls] == ["GET", "POST", "GET"]
    item.apply({"Overview": "Later update"})
    assert item.titleSort == expected


def test_emby_sort_title_update_reports_server_reset_instead_of_success():
    record = {"Id": "people", "Name": "Christian Bale", "SortName": "Christian Bale", "ForcedSortName": "Christian Bale", "Type": "BoxSet", "LockedFields": ["Tags"]}
    session = FakeSession([FakeResponse(dict(record)), FakeResponse(None, status_code=204), FakeResponse(dict(record))])
    library = _library(MediaBrowserClient(_server("emby"), session=session), kind="emby")
    item = MediaBrowserCollection(record, library)
    with pytest.raises(Failed, match="Sort title.*was not retained"):
        item.editSortTitle("!140_Christian Bale")
    assert session.calls[1]["json"]["LockedFields"] == ["Tags", "SortName"]
    assert item.titleSort == "Christian Bale"


def test_emby_sort_lock_is_not_duplicated():
    record = {"Id": "people", "Name": "Person", "SortName": "Person", "Type": "BoxSet", "LockedFields": ["SortName", "Tags"]}
    expected = "!140_Person"
    saved = {**record, "SortName": expected, "ForcedSortName": expected}
    session = FakeSession([FakeResponse(record), FakeResponse(None, status_code=204), FakeResponse(saved)])
    library = _library(MediaBrowserClient(_server("emby"), session=session), kind="emby")
    MediaBrowserCollection(record, library).editSortTitle(expected)
    assert session.calls[1]["json"]["LockedFields"] == ["SortName", "Tags"]


@pytest.mark.parametrize("saved_title", ["!140_Toshiro Mifune", "!140_toshiro mifune", "!140_Toshiro\u0304 Mifune"])
def test_emby_sort_title_verification_accepts_accent_and_case_normalization(saved_title):
    record = {"Id": "people", "Name": "Toshirō Mifune", "SortName": "Toshiro Mifune", "Type": "BoxSet"}
    saved = {**record, "SortName": saved_title, "ForcedSortName": saved_title, "LockedFields": ["SortName"]}
    session = FakeSession([FakeResponse(dict(record)), FakeResponse(None, status_code=204), FakeResponse(saved)])
    library = _library(MediaBrowserClient(_server("emby"), session=session), kind="emby")
    item = MediaBrowserCollection(record, library)
    item.editSortTitle("!140_Toshirō Mifune")
    assert item.titleSort == saved_title


@pytest.mark.parametrize("saved_title", ["Toshiro Mifune", "!150_Toshiro Mifune", "!140_Other Person", None])
def test_emby_sort_title_verification_still_rejects_lost_prefix_or_wrong_name(saved_title):
    record = {"Id": "people", "Name": "Toshirō Mifune", "SortName": "Toshiro Mifune", "Type": "BoxSet"}
    saved = {**record, "SortName": saved_title, "ForcedSortName": saved_title}
    session = FakeSession([FakeResponse(dict(record)), FakeResponse(None, status_code=204), FakeResponse(saved)])
    library = _library(MediaBrowserClient(_server("emby"), session=session), kind="emby")
    with pytest.raises(Failed, match="was not retained"):
        MediaBrowserCollection(record, library).editSortTitle("!140_Toshirō Mifune")


@pytest.mark.parametrize("has_primary", [True, False])
def test_separator_missing_primary_overrides_matching_poster_cache(has_primary, monkeypatch):
    from modules import library as library_module
    from modules.poster import ImageData

    monkeypatch.setattr(library_module, "logger", FakeLogger())
    session = FakeSession([] if has_primary else [FakeResponse(None, status_code=204)])
    library = _library(MediaBrowserClient(_server(), session=session))
    library.config.Cache = MagicMock()
    library.image_table_name = "images_1"
    library.show_asset_not_needed = True
    image = ImageData("url_poster", "https://example.com/separator.jpg")
    library.config.Cache.query_image_map.return_value = ("", image.compare, "")
    item = MediaBrowserCollection({"Id": "separator", "Name": "Award Collections", "Type": "BoxSet", "ImageTags": {"Primary": "tag"} if has_primary else {}}, library)
    assert library.upload_images(item, poster=image)[0] is (not has_primary)
    assert len(session.calls) == (0 if has_primary else 1)
    if not has_primary:
        assert session.calls[0]["params"]["imageUrl"] == image.location


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
@pytest.mark.parametrize(
    "video,filter_key,expected",
    [
        ({"AspectRatio": "4:3"}, "aspect", True),
        ({"AspectRatio": "1.33:1"}, "aspect", True),
        ({"Width": 640, "Height": 480}, "aspect", True),
        ({"AspectRatio": "16:9"}, "aspect", False),
        ({"AspectRatio": "16:9"}, "aspect.gte", True),
        ({}, "aspect.not", False),
    ],
)
def test_aspect_collection_filters_use_native_video_metadata(kind, video, filter_key, expected):
    library = _library(MediaBrowserClient(_server(kind), session=FakeSession([])), kind=kind)
    item = MediaBrowserItem({"Id": "movie", "Type": "Movie", "MediaSources": [{"MediaStreams": [{"Type": "Video", **video}]}]}, library)
    assert library.check_filters(item, [(filter_key, 1.33)], None) is expected


@pytest.mark.parametrize("method", ["POST", "DELETE"])
def test_large_collection_membership_requests_are_batched(method):
    ids = [f"{index:032x}" for index in range(250)]
    session = FakeSession([FakeResponse(None, status_code=204) for _ in range(3)])
    client = MediaBrowserClient(_server(), session=session)
    change = client.add_collection_items if method == "POST" else client.remove_collection_items
    change("collection", iter(ids))
    batches = [call["params"]["ids"].split(",") for call in session.calls]
    assert [len(batch) for batch in batches] == [100, 100, 50]
    assert [item_id for batch in batches for item_id in batch] == ids
    assert all(call["method"] == method for call in session.calls)


def test_large_emby_collection_creation_batches_initial_members():
    ids = [f"{index:032x}" for index in range(250)]
    session = FakeSession([FakeResponse({"Id": "collection"}), FakeResponse(None, status_code=204), FakeResponse(None, status_code=204)])
    client = MediaBrowserClient(_server("emby"), session=session)
    assert client.create_collection("Aspect", item_ids=ids)["Id"] == "collection"
    batches = [call["params"]["ids"].split(",") for call in session.calls]
    assert [len(batch) for batch in batches] == [100, 100, 50]
    assert [item_id for batch in batches for item_id in batch] == ids


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
@pytest.mark.parametrize("field,date_field", [("release", "PremiereDate"), ("added", "DateCreated")])
def test_basic_released_smart_filter_becomes_local_collection(kind, field, date_field, monkeypatch):
    from datetime import timedelta

    from modules import builder as builder_module
    from modules.builder import CollectionBuilder

    monkeypatch.setattr(builder_module, "logger", FakeLogger())
    library = _library(MediaBrowserClient(_server(kind), session=FakeSession([])), kind=kind)
    now = datetime.now(timezone.utc)
    records = [
        {"Id": "older", date_field: (now - timedelta(days=40)).isoformat()},
        {"Id": "recent", date_field: (now - timedelta(days=2)).isoformat()},
        {"Id": "old", date_field: (now - timedelta(days=100)).isoformat()},
        {"Id": "future", date_field: (now + timedelta(days=3)).isoformat()},
        {"Id": "unknown"},
    ]
    items = [MediaBrowserItem({"Name": row["Id"], "Type": "Movie", "MediaSources": [], **row}, library) for row in records]
    library.get_all = lambda: items
    data = {"smart_filter": {"any": {field: 90}, "sort_by": f"{field}.desc", "limit": 1}, "sync_mode": "sync"}
    methods = {key: key for key in data}
    CollectionBuilder._adapt_local_smart_filter(library, data, methods)
    CollectionBuilder._validate_smart_server(library, methods)
    assert "smart_filter" not in data
    assert data["collection_order"] == f"{field}.desc"
    search = library.build_local_search(data["plex_search"])
    assert library.get_rating_keys("plex_search", search) == [("recent", "ratingKey")]


def test_new_episodes_is_skipped_on_movie_libraries_before_capability_validation():
    from modules.builder import CollectionBuilder
    from modules.util import NotScheduled

    library = _library(MediaBrowserClient(_server(), session=FakeSession([])))
    data = {"smart_filter": {"type": "episodes", "any": {"episode_air_date": 7}}, "run_definition": ["show"]}
    with pytest.raises(NotScheduled, match="run_definition"):
        CollectionBuilder._adapt_local_smart_filter(library, data, {key: key for key in data})


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
@pytest.mark.parametrize("role", ["actor", "director", "writer", "producer"])
def test_people_collections_resolve_tmdb_names_and_match_native_roles(kind, role, monkeypatch):
    from modules import builder as builder_module
    from modules.builder import CollectionBuilder
    from tests.factories import make_builder

    monkeypatch.setattr(builder_module, "logger", FakeLogger())
    library = _library(MediaBrowserClient(_server(kind), session=FakeSession([])), kind=kind)
    rows = [
        {"Id": "lower", "CommunityRating": 6.0, "People": [{"Id": "person", "Name": "Person One", "Type": role.capitalize()}]},
        {"Id": "higher", "CommunityRating": 9.0, "People": [{"Id": "person", "Name": "Person One", "Type": role.capitalize()}]},
        {"Id": "wrong-role", "CommunityRating": 10.0, "People": [{"Name": "Person One", "Type": "Actor" if role != "actor" else "Writer"}]},
        {"Id": "unknown", "CommunityRating": 10.0},
    ]
    items = [MediaBrowserItem({"Name": row["Id"], "Type": "Movie", "MediaSources": [], **row}, library) for row in rows]
    library.get_all = lambda: items
    assert [person.tag for person in getattr(items[0], f"{role}s")] == ["Person One"]
    data = {"smart_filter": {"any": {role: "tmdb"}, "sort_by": "audience_rating.desc", "limit": 1}}
    CollectionBuilder._adapt_local_smart_filter(library, data, {key: key for key in data})
    builder = make_builder(library=library, details={"tmdb_person": ["Person One"]})
    search = builder.build_filter("plex_search", data["plex_search"])
    assert library.get_rating_keys("plex_search", search) == [("higher", "ratingKey")]
    assert data["plex_search"]["local_collection_search"]["any"][role] == "tmdb"


def test_native_people_are_deduplicated_and_survive_partial_metadata_updates():
    library = _library(MediaBrowserClient(_server(), session=FakeSession([])))
    item = MediaBrowserItem(
        {
            "Id": "movie",
            "Type": "Movie",
            "People": [
                {"Id": "42", "Name": "Writer", "Type": "Writer"},
                {"Name": "Writer", "Type": "Writer"},
                {"Name": "", "Type": "Writer"},
                {"Name": "Producer", "Type": "Executive Producer"},
            ],
        },
        library,
    )
    assert [(person.id, person.tag) for person in item.writers] == [("42", "Writer")]
    assert [person.tag for person in item.producers] == ["Producer"]
    item.apply({"Overview": "Updated"})
    assert item.writers[0].tag == "Writer"


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
    assert base64.b64decode(session.calls[4]["data"], validate=True) == b"jpeg"
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


def test_get_all_collections_returns_boxsets_and_can_filter_a_tag():
    session = FakeSession(
        [
            FakeResponse({"Items": [{"Id": "box-1", "Name": "Heat", "Type": "BoxSet", "Tags": ["Kometa"]}, {"Id": "box-2", "Name": "Other", "Type": "BoxSet", "Tags": []}], "TotalRecordCount": 2}),
            FakeResponse({"Items": [{"Id": "box-1", "Name": "Heat", "Type": "BoxSet", "Tags": ["Kometa"]}, {"Id": "box-2", "Name": "Other", "Type": "BoxSet", "Tags": []}], "TotalRecordCount": 2}),
        ]
    )
    library = _library(MediaBrowserClient(_server(), session=session))

    collections = library.get_all_collections()

    assert [collection.title for collection in collections] == ["Heat", "Other"]
    assert [collection.title for collection in library.get_all_collections(label="Kometa")] == ["Heat"]
    assert session.calls[0]["params"]["includeItemTypes"] == "BoxSet"


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
@pytest.mark.parametrize("sources,expected", [([], False), ([{}], False), ([{}, {}], True), (None, None)])
def test_duplicate_search_uses_known_media_sources(kind, sources, expected):
    library = _library(MediaBrowserClient(_server(kind), session=FakeSession([])), kind=kind)
    record = MediaBrowserItem({"Id": "1", "Name": "Movie", "Type": "Movie", "MediaSources": sources}, library)
    from modules.local_search import compile_selector

    metadata = library._search_metadata(record)
    for value in (True, False):
        assert compile_selector({"duplicate": value})(metadata) == (expected is value)


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
def test_duplicate_search_loads_sources_even_when_streams_are_present(kind):
    detail = {"Id": "1", "Name": "Movie", "Type": "Movie", "MediaSources": [{"Id": "a"}, {"Id": "b"}]}
    session = FakeSession([FakeResponse(detail)])
    library = _library(MediaBrowserClient(_server(kind), session=session), kind=kind)
    library.get_all = lambda: [MediaBrowserItem({"Id": "1", "Name": "Movie", "Type": "Movie", "MediaStreams": []}, library)]
    search = library.build_local_search({"any": {"duplicate": True}})
    assert library.get_rating_keys("plex_search", search) == [("1", "ratingKey")]
    assert library.get_rating_keys("plex_search", search) == [("1", "ratingKey")]
    assert len(session.calls) == 1
