"""Tests for the Lidarr connector, run against a fake HTTP session that records every request."""

from types import SimpleNamespace

import pytest
import requests

import modules.lidarr as lidarr_module
import modules.timings as timings_module
from modules.lidarr import Lidarr
from modules.timings import TimingRegistry
from modules.util import Failed
from tests.conftest import FakeLogger

URL = "http://lidarr:8686"
API = f"{URL}/api/v1"
TOKEN = "lidarr-api-key"
LIBRARY = "Music"

ARTIST_A = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
ARTIST_B = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
ARTIST_C = "cccccccc-cccc-4ccc-8ccc-cccccccccccc"

KOMETA, FAVORITES = 10, 11


class FakeResponse:
    def __init__(self, payload=None, status_code=200):
        self.payload = payload
        self.status_code = status_code
        self.content = b"" if payload is None else b"json"

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Client Error")

    def json(self):
        return self.payload


class FakeSession:
    """Stand-in for requests.Session: serves canned payloads by (method, path) and records each request."""

    def __init__(self, routes):
        self.routes = routes
        self.calls = []

    def request(self, method, url, **kwargs):
        path = url.removeprefix(API)
        self.calls.append(SimpleNamespace(method=method, url=url, path=path, **kwargs))
        if (method, path) not in self.routes:
            raise AssertionError(f"unexpected request: {method} {path}")
        reply = self.routes[(method, path)]
        return reply if isinstance(reply, FakeResponse) else FakeResponse(reply)

    def sent(self, method, path):
        return [call for call in self.calls if call.method == method and call.path == path]


class FakeAddsCache:
    def __init__(self, cached=()):
        self.cached = set(cached)
        self.updates = []

    def query_lidarr_adds(self, mbid, library):
        return mbid if mbid in self.cached else None

    def update_lidarr_adds(self, mbid, library):
        self.updates.append((mbid, library))


def make_routes():
    return {
        ("GET", "/system/status"): {"version": "2.9.6"},
        ("GET", "/qualityprofile"): [{"id": 1, "name": "Any"}, {"id": 2, "name": "Lossless"}],
        ("GET", "/metadataprofile"): [{"id": 7, "name": "Standard"}],
        ("GET", "/rootfolder"): [{"path": "/music"}],
        ("GET", "/tag"): [{"id": KOMETA, "label": "kometa"}, {"id": FAVORITES, "label": "Favorites"}],
        ("GET", "/artist"): [],
    }


def make_params(**overrides):
    params = {
        "url": f"{URL}/",
        "token": TOKEN,
        "add_missing": False,
        "add_existing": False,
        "upgrade_existing": False,
        "monitor_existing": False,
        "root_folder_path": "/music",
        "monitor": "all",
        "monitor_new_albums": "all",
        "quality_profile": "lossless",
        "tag": [],
        "search": False,
        "lidarr_path": "",
        "plex_path": "",
        "ignore_cache": False,
    }
    params.update(overrides)
    return params


def connect(routes=None, cache=None, **params):
    session = FakeSession(make_routes() if routes is None else routes)
    lidarr = Lidarr(SimpleNamespace(session=session), cache, SimpleNamespace(original_mapping_name=LIBRARY), make_params(**params))
    return lidarr, session


def make_lidarr(routes=None, cache=None, **params):
    """A connected Lidarr whose session has forgotten the setup requests."""
    lidarr, session = connect(routes, cache, **params)
    session.calls.clear()
    return lidarr, session


def artist(mbid, artist_id, name, **fields):
    return {"id": artist_id, "foreignArtistId": mbid, "artistName": name, **fields}


@pytest.fixture(autouse=True)
def logger(monkeypatch):
    fake = FakeLogger()
    monkeypatch.setattr(lidarr_module, "logger", fake)
    return fake


@pytest.fixture(autouse=True)
def registry(monkeypatch):
    fresh = TimingRegistry()
    monkeypatch.setattr(timings_module, "registry", fresh)
    return fresh


class TestConnect:
    def test_checks_the_server_and_resolves_profiles_with_the_api_key(self):
        lidarr, session = connect()
        assert [(call.method, call.path) for call in session.calls] == [
            ("GET", "/system/status"),
            ("GET", "/qualityprofile"),
            ("GET", "/metadataprofile"),
            ("GET", "/rootfolder"),
        ]
        assert all(call.url.startswith(f"{API}/") for call in session.calls)
        assert all(call.headers == {"X-Api-Key": TOKEN} and call.timeout == 30 for call in session.calls)
        assert lidarr.quality_profile_id == 2
        assert lidarr.metadata_profile_id == 7

    def test_quality_profile_can_be_given_by_id(self):
        lidarr, _ = connect(quality_profile=1)
        assert lidarr.quality_profile_id == 1

    def test_url_and_token_are_redacted_and_the_host_is_tagged_for_timings(self, logger, registry):
        connect()
        assert URL in logger.secrets
        assert TOKEN in logger.secrets
        assert registry.arr_hosts == {"lidarr:8686": "lidarr"}

    @pytest.mark.parametrize(
        ("lidarr_path", "plex_path", "expected"),
        [("/data/music", "/media/music", ("/data/music", "/media/music")), ("/data/music", "", ("", "")), ("", "/media/music", ("", ""))],
    )
    def test_path_mapping_needs_both_sides(self, lidarr_path, plex_path, expected):
        lidarr, _ = connect(lidarr_path=lidarr_path, plex_path=plex_path)
        assert (lidarr.lidarr_path, lidarr.plex_path) == expected

    def test_unknown_root_folder_fails(self):
        with pytest.raises(Failed, match="Invalid Root Folder: /missing"):
            connect(root_folder_path="/missing")

    def test_unknown_quality_profile_fails_and_lists_the_options(self):
        with pytest.raises(Failed, match=r"Invalid Quality Profile: FLAC\. Options: \['Any', 'Lossless'\]"):
            connect(quality_profile="FLAC")

    def test_http_errors_become_lidarr_errors(self):
        routes = make_routes()
        routes[("GET", "/system/status")] = FakeResponse(status_code=401)
        with pytest.raises(Failed, match="Lidarr Error: 401"):
            connect(routes)

    @pytest.mark.parametrize(
        ("route", "payload", "message"),
        [
            (("GET", "/system/status"), [], "Expected an object from /system/status"),
            (("GET", "/qualityprofile"), {"id": 1}, "Expected a list of objects from /qualityprofile"),
            (("GET", "/rootfolder"), ["/music"], "Expected a list of objects from /rootfolder"),
        ],
    )
    def test_unexpected_payload_shapes_fail(self, route, payload, message):
        routes = make_routes()
        routes[route] = payload
        with pytest.raises(Failed, match=message):
            connect(routes)

    def test_other_setup_errors_are_wrapped_instead_of_crashing(self):
        routes = make_routes()
        routes[("GET", "/metadataprofile")] = []
        with pytest.raises(Failed, match="^Lidarr Error: "):
            connect(routes)


class TestValidMbid:
    @pytest.mark.parametrize(
        ("mbid", "valid"),
        [
            (ARTIST_A, True),
            (ARTIST_A.upper(), True),
            (None, False),
            ("", False),
            (ARTIST_A[:-1], False),
            (f"{ARTIST_A}0", False),
            (f" {ARTIST_A}", False),
            (ARTIST_A.replace("-", ""), False),
        ],
    )
    def test_accepts_only_a_full_musicbrainz_uuid(self, mbid, valid):
        assert Lidarr.valid_mbid(mbid) is valid


class TestGetMbidIds:
    ARTISTS = [
        artist(ARTIST_A, 1, "Both Tags", tags=[KOMETA, FAVORITES]),
        artist(ARTIST_B, 2, "One Tag", tags=[KOMETA]),
        artist(ARTIST_C, 3, "Untagged", tags=[]),
        artist("not-an-mbid", 4, "Bad ID", tags=[]),
    ]

    def test_all_returns_every_artist_with_a_valid_mbid(self):
        lidarr, _ = make_lidarr(make_routes() | {("GET", "/artist"): self.ARTISTS})
        assert lidarr.get_mbid_ids("lidarr_all", True) == [(ARTIST_A, "mbid"), (ARTIST_B, "mbid"), (ARTIST_C, "mbid")]

    def test_taglist_requires_every_tag(self):
        lidarr, _ = make_lidarr(make_routes() | {("GET", "/artist"): self.ARTISTS})
        assert lidarr.get_mbid_ids("lidarr_taglist", ["kometa", "favorites"]) == [(ARTIST_A, "mbid")]
        assert lidarr.get_mbid_ids("lidarr_taglist", ["kometa"]) == [(ARTIST_A, "mbid"), (ARTIST_B, "mbid")]

    def test_blank_taglist_selects_only_untagged_artists(self):
        lidarr, _ = make_lidarr(make_routes() | {("GET", "/artist"): self.ARTISTS})
        assert lidarr.get_mbid_ids("lidarr_taglist", []) == [(ARTIST_C, "mbid")]

    @pytest.mark.parametrize("tags", [["favourites"], ["kometa", "favourites"]])
    def test_taglist_with_a_tag_missing_from_lidarr_selects_nothing(self, logger, tags):
        lidarr, _ = make_lidarr(make_routes() | {("GET", "/artist"): self.ARTISTS})
        assert lidarr.get_mbid_ids("lidarr_taglist", tags) == []
        assert logger.warning_messages == ["Lidarr Warning: Tags not found in Lidarr: favourites"]

    def test_artist_names_are_kept_for_reporting(self):
        lidarr, session = make_lidarr(make_routes() | {("GET", "/artist"): self.ARTISTS})
        lidarr.get_mbid_ids("lidarr_all", True)
        assert lidarr.get_artist_name(ARTIST_B) == "One Tag"
        assert len(session.sent("GET", "/artist")) == 1


class TestGetArtistName:
    def test_fetches_the_artist_list_once(self):
        lidarr, session = make_lidarr(make_routes() | {("GET", "/artist"): [artist(ARTIST_A, 1, "Artist A")]})
        assert lidarr.get_artist_name(ARTIST_A) == "Artist A"
        assert lidarr.get_artist_name(ARTIST_B) == "Unknown Artist"
        assert len(session.sent("GET", "/artist")) == 1


class TestEditTags:
    @pytest.mark.parametrize(
        ("apply_tags", "existing", "expected"),
        [
            ("", [KOMETA], [KOMETA, FAVORITES]),
            ("", [FAVORITES, KOMETA], [FAVORITES, KOMETA]),
            ("sync", [KOMETA], [FAVORITES]),
            ("remove", [KOMETA, FAVORITES], [KOMETA]),
        ],
    )
    def test_apply_modes(self, apply_tags, existing, expected):
        routes = make_routes() | {("GET", "/artist"): [artist(ARTIST_A, 1, "Artist A", tags=existing)], ("PUT", "/artist/1"): {}}
        lidarr, session = make_lidarr(routes)
        lidarr.edit_tags([ARTIST_A], ["FAVORITES"], apply_tags)
        [put] = session.sent("PUT", "/artist/1")
        assert put.json["tags"] == expected

    def test_missing_tags_are_created_in_lower_case(self):
        routes = make_routes() | {
            ("GET", "/artist"): [artist(ARTIST_A, 1, "Artist A", tags=[])],
            ("POST", "/tag"): {"id": 12, "label": "new wave"},
            ("PUT", "/artist/1"): {},
        }
        lidarr, session = make_lidarr(routes)
        lidarr.edit_tags([ARTIST_A], ["New Wave"], "")
        assert [post.json for post in session.sent("POST", "/tag")] == [{"label": "new wave"}]
        assert session.sent("PUT", "/artist/1")[0].json["tags"] == [12]

    def test_tag_creation_must_return_a_tag(self):
        lidarr, _ = make_lidarr(make_routes() | {("POST", "/tag"): ["unexpected"]})
        with pytest.raises(Failed, match="Expected a tag object when creating a tag"):
            lidarr.edit_tags([ARTIST_A], ["new wave"], "")

    def test_artists_not_in_lidarr_are_reported_and_skipped(self, logger):
        lidarr, session = make_lidarr()
        lidarr.edit_tags([ARTIST_A], ["kometa"], "")
        assert logger.warning_messages == [f"MusicBrainz Artist ID Not in Lidarr | {ARTIST_A}"]
        assert not [call for call in session.calls if call.method == "PUT"]


class TestRemoveAllWithTags:
    def test_removes_only_artists_with_every_tag_and_keeps_their_files(self, logger):
        routes = make_routes() | {
            ("GET", "/artist"): [
                artist(ARTIST_A, 1, "Both Tags", tags=[KOMETA, FAVORITES]),
                artist(ARTIST_B, 2, "One Tag", tags=[KOMETA]),
                artist(ARTIST_C, 3, "Untagged", tags=[]),
            ],
            ("DELETE", "/artist/1"): None,
        }
        lidarr, session = make_lidarr(routes)
        lidarr.remove_all_with_tags(["kometa", "favorites"])
        deletes = [call for call in session.calls if call.method == "DELETE"]
        assert [(call.path, call.json) for call in deletes] == [("/artist/1", {"deleteFiles": False, "addImportListExclusion": False})]
        assert logger.info_messages == ["Removed from Lidarr | Both Tags"]

    def test_tags_missing_from_lidarr_remove_nothing_and_are_not_created(self):
        routes = make_routes() | {("GET", "/artist"): [artist(ARTIST_A, 1, "Artist A", tags=[KOMETA])]}
        lidarr, session = make_lidarr(routes)
        lidarr.remove_all_with_tags(["missing"])
        assert [call.method for call in session.calls if call.method != "GET"] == []

    def test_one_tag_missing_from_lidarr_removes_nothing(self, logger):
        routes = make_routes() | {("GET", "/artist"): [artist(ARTIST_A, 1, "Artist A", tags=[KOMETA])], ("DELETE", "/artist/1"): None}
        lidarr, session = make_lidarr(routes)
        lidarr.remove_all_with_tags(["kometa", "temp"])
        assert [call.path for call in session.calls if call.method == "DELETE"] == []
        assert logger.warning_messages == ["Lidarr Warning: Tags not found in Lidarr: temp"]


class TestAddArtists:
    LOOKUP = {("GET", "/artist/lookup"): [{"artistName": "Artist A", "foreignArtistId": ARTIST_A}], ("POST", "/artist"): {"id": 1}}

    def test_adds_a_new_artist_with_the_configured_defaults(self, logger):
        cache = FakeAddsCache()
        lidarr, session = make_lidarr(make_routes() | self.LOOKUP, cache=cache)
        assert lidarr.add_artists([ARTIST_A]) == [ARTIST_A]
        assert session.sent("GET", "/artist/lookup")[0].params == {"term": f"lidarr:{ARTIST_A}"}
        [post] = session.sent("POST", "/artist")
        assert post.json == {
            "artistName": "Artist A",
            "foreignArtistId": ARTIST_A,
            "qualityProfileId": 2,
            "metadataProfileId": 7,
            "rootFolderPath": "/music",
            "monitored": True,
            "monitorNewItems": "all",
            "tags": [],
            "addOptions": {"monitor": "all", "searchForMissingAlbums": False},
        }
        assert cache.updates == [(ARTIST_A, LIBRARY)]
        assert logger.info_messages == ["Added to Lidarr | Artist A"]

    def test_options_override_the_defaults(self):
        lidarr, session = make_lidarr(make_routes() | self.LOOKUP)
        lidarr.add_artists([ARTIST_A], folder="/other", quality="Any", monitor="none", monitor_new_albums="new", search=True, tag=["kometa"])
        payload = session.sent("POST", "/artist")[0].json
        assert payload["rootFolderPath"] == "/other"
        assert payload["qualityProfileId"] == 1
        assert payload["monitored"] is False
        assert payload["monitorNewItems"] == "new"
        assert payload["tags"] == [KOMETA]
        assert payload["addOptions"] == {"monitor": "none", "searchForMissingAlbums": True}

    def test_a_metadata_profile_from_the_lookup_is_kept(self):
        lookup = {("GET", "/artist/lookup"): [{"artistName": "Artist A", "metadataProfileId": 3}], ("POST", "/artist"): {"id": 1}}
        lidarr, session = make_lidarr(make_routes() | lookup)
        lidarr.add_artists([ARTIST_A])
        assert session.sent("POST", "/artist")[0].json["metadataProfileId"] == 3

    def test_invalid_mbids_are_reported_and_never_looked_up(self, logger):
        lidarr, session = make_lidarr()
        assert lidarr.add_artists(["not-an-mbid"]) == []
        assert logger.warning_messages == ["Lidarr Warning: Invalid MusicBrainz Artist ID: not-an-mbid"]
        assert not session.sent("GET", "/artist/lookup")

    def test_mbids_the_lookup_cannot_find_are_reported(self, logger):
        lidarr, session = make_lidarr(make_routes() | {("GET", "/artist/lookup"): []})
        assert lidarr.add_artists([ARTIST_A]) == []
        assert logger.warning_messages == [f"Lidarr Warning: MusicBrainz Artist ID not found: {ARTIST_A}"]
        assert not session.sent("POST", "/artist")

    def test_cached_adds_are_skipped_using_the_plex_name(self, logger):
        lidarr, session = make_lidarr(make_routes() | self.LOOKUP, cache=FakeAddsCache(cached=[ARTIST_A]))
        assert lidarr.add_artists([(ARTIST_A, "Plex Name")]) == []
        assert logger.info_messages == [f"Skipped In Cache | Plex Name (MBID: {ARTIST_A})"]
        assert not session.sent("GET", "/artist/lookup")

    def test_ignore_cache_adds_cached_artists_again(self):
        lidarr, _ = make_lidarr(make_routes() | self.LOOKUP, cache=FakeAddsCache(cached=[ARTIST_A]), ignore_cache=True)
        assert lidarr.add_artists([ARTIST_A]) == [ARTIST_A]

    def test_existing_artists_are_left_alone_by_default(self, logger):
        cache = FakeAddsCache()
        existing = artist(ARTIST_A, 5, "Artist A", qualityProfileId=1, monitored=False, monitorNewItems="none")
        lidarr, session = make_lidarr(make_routes() | {("GET", "/artist"): [existing]}, cache=cache)
        assert lidarr.add_artists([ARTIST_A]) == []
        assert [(call.method, call.path) for call in session.calls] == [("GET", "/tag"), ("GET", "/artist")]
        assert logger.info_messages == ["Already in Lidarr | Artist A"]
        assert cache.updates == [(ARTIST_A, LIBRARY)]

    def test_upgrade_existing_changes_only_the_quality_profile(self):
        existing = artist(ARTIST_A, 5, "Artist A", qualityProfileId=1, monitored=False, monitorNewItems="none")
        lidarr, session = make_lidarr(make_routes() | {("GET", "/artist"): [existing], ("PUT", "/artist/5"): {}}, upgrade_existing=True)
        lidarr.add_artists([ARTIST_A])
        [put] = session.sent("PUT", "/artist/5")
        assert put.json == {**existing, "qualityProfileId": 2}
        assert not session.sent("GET", "/album")

    def test_monitor_existing_updates_the_artist_and_its_albums(self, logger):
        existing = artist(ARTIST_A, 5, "Artist A", qualityProfileId=2, monitored=False, monitorNewItems="none")
        routes = make_routes() | {
            ("GET", "/artist"): [existing],
            ("PUT", "/artist/5"): {},
            ("GET", "/album"): [{"id": 50}, {"id": 51}],
            ("PUT", "/album/monitor"): None,
        }
        lidarr, session = make_lidarr(routes, monitor_existing=True)
        lidarr.add_artists([ARTIST_A])
        assert session.sent("PUT", "/artist/5")[0].json == {**existing, "monitored": True, "monitorNewItems": "all"}
        assert session.sent("GET", "/album")[0].params == {"artistId": 5}
        assert [put.json for put in session.sent("PUT", "/album/monitor")] == [{"albumIds": [50, 51], "monitored": True}]
        assert logger.info_messages == ["Updated in Lidarr | Artist A"]


class TestAlbumMonitoring:
    """`monitor` applied to an existing artist's albums (monitor_existing)."""

    OWNED = {"id": 1, "releaseDate": "1997-05-21T00:00:00Z", "statistics": {"trackFileCount": 12}}
    MISSING = {"id": 2, "releaseDate": "2000-10-02T00:00:00Z", "statistics": {"trackFileCount": 0}}
    UPCOMING = {"id": 3, "releaseDate": "2999-01-01T00:00:00Z", "statistics": {"trackFileCount": 0}}
    UNDATED = {"id": 4}
    ALBUMS = [OWNED, MISSING, UPCOMING, UNDATED]
    UNMONITOR_ALL = {"albumIds": [1, 2, 3, 4], "monitored": False}

    def monitor_puts(self, monitor, albums):
        existing = artist(ARTIST_A, 5, "Artist A", qualityProfileId=2, monitored=monitor != "none", monitorNewItems="all")
        routes = make_routes() | {("GET", "/artist"): [existing], ("GET", "/album"): albums, ("PUT", "/album/monitor"): None}
        lidarr, session = make_lidarr(routes, monitor_existing=True, monitor=monitor)
        lidarr.add_artists([ARTIST_A])
        return [put.json for put in session.sent("PUT", "/album/monitor")]

    @pytest.mark.parametrize(
        ("monitor", "expected"),
        [
            ("all", [{"albumIds": [1, 2, 3, 4], "monitored": True}]),
            ("none", [{"albumIds": [1, 2, 3, 4], "monitored": False}]),
            ("future", [UNMONITOR_ALL, {"albumIds": [3, 4], "monitored": True}]),
            ("missing", [UNMONITOR_ALL, {"albumIds": [2, 3, 4], "monitored": True}]),
            ("existing", [UNMONITOR_ALL, {"albumIds": [1], "monitored": True}]),
            ("first", [UNMONITOR_ALL, {"albumIds": [1], "monitored": True}]),
            ("latest", [UNMONITOR_ALL, {"albumIds": [3], "monitored": True}]),
        ],
    )
    def test_monitor_options(self, monitor, expected):
        assert self.monitor_puts(monitor, self.ALBUMS) == expected

    def test_first_and_latest_with_no_dated_albums_only_unmonitor(self):
        assert self.monitor_puts("first", [self.UNDATED]) == [{"albumIds": [4], "monitored": False}]

    def test_an_artist_without_albums_sends_nothing(self):
        assert self.monitor_puts("latest", []) == []
