"""Tests for the Sonarr connector, run against a fake arrapi client that records every call."""

import inspect
from types import SimpleNamespace

import pytest
from arrapi import SonarrAPI
from arrapi.exceptions import ArrException, NotFound, Unauthorized

import modules.sonarr as sonarr_module
import modules.timings as timings_module
from modules.sonarr import Sonarr
from modules.timings import TimingRegistry
from modules.util import Failed
from tests.conftest import FakeLogger

URL = "http://sonarr:8989"
TOKEN = "sonarr-api-key"
LIBRARY = "TV Shows"

KOMETA, ANIME = 10, 11


def tag(tag_id, label):
    return SimpleNamespace(id=tag_id, label=label)


def series(tvdb_id, title, path=None, tags=(), quality=1):
    return SimpleNamespace(tvdbId=tvdb_id, title=title, path=path, tags=list(tags), qualityProfileId=quality, folder=title)


class FakeSonarrAPI:
    """Stand-in for arrapi.SonarrAPI.

    Each call is bound to the real SonarrAPI method's signature, so a call arrapi would reject fails here too,
    and is recorded with its arguments by name (defaults filled in).
    """

    def __init__(self):
        self.series = []
        self.lookup = {}
        self.tags = [tag(KOMETA, "kometa"), tag(ANIME, "Anime")]
        self.profiles = [SimpleNamespace(id=1, name="Any"), SimpleNamespace(id=4, name="HD-1080p")]
        self._raw = SimpleNamespace(v3=True)
        self.setup_error = None
        self.add_error = None
        self.add_outcome = None
        self.calls = []

    def _record(self, name, *args, **kwargs):
        bound = inspect.signature(getattr(SonarrAPI, name)).bind(self, *args, **kwargs)
        bound.apply_defaults()
        arguments = {key: value for key, value in bound.arguments.items() if key != "self"}
        self.calls.append((name, arguments))
        return arguments

    def sent(self, name):
        return [arguments for call, arguments in self.calls if call == name]

    def connect(self, *args, **kwargs):
        self._record("__init__", *args, **kwargs)
        return self

    def respect_list_exclusions_when_adding(self, *args, **kwargs):
        self._record("respect_list_exclusions_when_adding", *args, **kwargs)

    def _validate_add_options(self, *args, **kwargs):
        self._record("_validate_add_options", *args, **kwargs)
        if self.setup_error:
            raise self.setup_error

    def quality_profile(self, *args, **kwargs):
        self._record("quality_profile", *args, **kwargs)
        return list(self.profiles)

    def all_series(self, *args, **kwargs):
        self._record("all_series", *args, **kwargs)
        return list(self.series)

    def all_tags(self, *args, **kwargs):
        self._record("all_tags", *args, **kwargs)
        return list(self.tags)

    def get_series(self, *args, **kwargs):
        tvdb_id = self._record("get_series", *args, **kwargs)["tvdb_id"]
        if tvdb_id not in self.lookup:
            raise NotFound(f"Item Not Found: {tvdb_id}")
        return self.lookup[tvdb_id]

    def add_multiple_series(self, *args, **kwargs):
        shows = self._record("add_multiple_series", *args, **kwargs)["ids"]
        if self.add_error:
            raise self.add_error
        if self.add_outcome:
            return self.add_outcome(shows)
        return [show[0] if isinstance(show, tuple) else show for show in shows], [], [], []

    def edit_multiple_series(self, *args, **kwargs):
        ids = self._record("edit_multiple_series", *args, **kwargs)["ids"]
        known = {show.tvdbId: show for show in self.series}
        return [known[i] for i in ids if i in known], [i for i in ids if i not in known]

    def delete_multiple_series(self, *args, **kwargs):
        self._record("delete_multiple_series", *args, **kwargs)
        return []


class FakeAddsCache:
    def __init__(self, cached=()):
        self.cached = set(cached)
        self.updates = []

    def query_sonarr_adds(self, tvdb_id, library):
        return tvdb_id if tvdb_id in self.cached else None

    def update_sonarr_adds(self, tvdb_id, library):
        self.updates.append((tvdb_id, library))


def make_params(**overrides):
    params = {
        "url": URL,
        "token": TOKEN,
        "add_missing": False,
        "add_existing": False,
        "upgrade_existing": False,
        "monitor_existing": False,
        "root_folder_path": "/tv",
        "monitor": "all",
        "quality_profile": "HD-1080p",
        "language_profile": "English",
        "series_type": "standard",
        "season_folder": True,
        "tag": [],
        "search": False,
        "cutoff_search": False,
        "sonarr_path": "",
        "plex_path": "",
        "ignore_cache": False,
    }
    params.update(overrides)
    return params


def connect(monkeypatch, api=None, cache=None, **params):
    api = api or FakeSonarrAPI()
    session = object()
    monkeypatch.setattr(sonarr_module, "SonarrAPI", api.connect)
    sonarr = Sonarr(SimpleNamespace(session=session), cache, SimpleNamespace(original_mapping_name=LIBRARY), make_params(**params))
    return sonarr, api, session


@pytest.fixture
def make_sonarr(monkeypatch):
    """A connected Sonarr whose fake client has forgotten the setup calls."""

    def make(api=None, cache=None, **params):
        sonarr, api, _ = connect(monkeypatch, api, cache, **params)
        api.calls.clear()
        return sonarr, api

    return make


@pytest.fixture(autouse=True)
def logger(monkeypatch):
    fake = FakeLogger()
    monkeypatch.setattr(sonarr_module, "logger", fake)
    return fake


@pytest.fixture(autouse=True)
def registry(monkeypatch):
    fresh = TimingRegistry()
    monkeypatch.setattr(timings_module, "registry", fresh)
    return fresh


def test_the_fake_rejects_calls_the_real_client_would_reject():
    with pytest.raises(TypeError):
        FakeSonarrAPI().edit_multiple_series([101], quality=4)


class TestConnect:
    def test_connects_with_the_shared_session_and_validates_the_add_options(self, monkeypatch):
        sonarr, api, session = connect(monkeypatch)
        assert [call for call, _ in api.calls] == ["__init__", "respect_list_exclusions_when_adding", "_validate_add_options", "quality_profile"]
        assert api.sent("__init__") == [{"url": URL, "apikey": TOKEN, "session": session}]
        validated = api.sent("_validate_add_options")[0]
        assert (validated["root_folder"], validated["quality_profile"], validated["language_profile"]) == ("/tv", "HD-1080p", "English")
        assert sonarr.profiles == api.profiles

    def test_url_and_token_are_redacted_and_the_host_is_tagged_for_timings(self, monkeypatch, logger, registry):
        connect(monkeypatch)
        assert URL in logger.secrets
        assert TOKEN in logger.secrets
        assert registry.arr_hosts == {"sonarr:8989": "sonarr"}

    @pytest.mark.parametrize(
        ("sonarr_path", "plex_path", "expected"),
        [("/data/tv", "/media/tv", ("/data/tv", "/media/tv")), ("/data/tv", "", ("", "")), ("", "/media/tv", ("", ""))],
    )
    def test_path_mapping_needs_both_sides(self, monkeypatch, sonarr_path, plex_path, expected):
        sonarr, _, _ = connect(monkeypatch, sonarr_path=sonarr_path, plex_path=plex_path)
        assert (sonarr.sonarr_path, sonarr.plex_path) == expected

    def test_client_errors_become_failed(self, monkeypatch):
        api = FakeSonarrAPI()
        api.setup_error = Unauthorized("Invalid API Key")
        with pytest.raises(Failed, match="Invalid API Key"):
            connect(monkeypatch, api)


class TestGetTvdbIds:
    @pytest.fixture
    def tagged(self, make_sonarr):
        sonarr, api = make_sonarr()
        api.series = [
            series(101, "Severance", tags=[tag(KOMETA, "kometa")]),
            series(202, "Frieren", tags=[tag(ANIME, "Anime")]),
            series(303, "Andor"),
        ]
        return sonarr, api

    def test_all_returns_every_series_without_reading_tags(self, tagged):
        sonarr, api = tagged
        assert sonarr.get_tvdb_ids("sonarr_all", True) == [(101, "tvdb"), (202, "tvdb"), (303, "tvdb")]
        assert api.sent("all_tags") == []

    # The builder lower-cases the tag list, while Sonarr keeps the label's case ("Anime").
    @pytest.mark.parametrize(("data", "expected"), [(["kometa"], [101]), (["anime"], [202]), (["kometa", "anime"], [101, 202])])
    def test_taglist_selects_series_with_any_of_the_tags(self, tagged, data, expected):
        sonarr, _ = tagged
        assert sonarr.get_tvdb_ids("sonarr_taglist", data) == [(tvdb_id, "tvdb") for tvdb_id in expected]

    def test_blank_taglist_selects_only_untagged_series(self, tagged):
        sonarr, _ = tagged
        assert sonarr.get_tvdb_ids("sonarr_taglist", []) == [(303, "tvdb")]

    def test_taglist_with_a_tag_missing_from_sonarr_selects_nothing(self, tagged):
        sonarr, _ = tagged
        assert sonarr.get_tvdb_ids("sonarr_taglist", ["missing"]) == []

    def test_empty_when_sonarr_has_no_series(self, make_sonarr):
        sonarr, _ = make_sonarr()
        assert sonarr.get_tvdb_ids("sonarr_all", True) == []


class TestEditTags:
    @pytest.mark.parametrize(("apply_tags", "mode"), [("", "add"), ("sync", "replace"), ("remove", "remove")])
    def test_sends_the_translated_apply_mode_in_batches_of_100(self, make_sonarr, logger, apply_tags, mode):
        sonarr, api = make_sonarr()
        sonarr.edit_tags([101], ["kometa"], apply_tags)
        edit = api.sent("edit_multiple_series")[0]
        assert (edit["ids"], edit["tags"], edit["apply_tags"], edit["per_request"]) == ([101], ["kometa"], mode, 100)
        assert f"{mode.capitalize()} Sonarr Tags: ['kometa']" in logger.info_messages

    def test_reports_edited_series_and_ids_not_in_sonarr(self, make_sonarr, logger):
        sonarr, api = make_sonarr()
        api.series = [series(101, "Severance", tags=["kometa"])]
        sonarr.edit_tags([101, 999], ["kometa"], "")
        assert f"Sonarr Tags | {'Severance':<25} | ['kometa']" in logger.info_messages
        assert "1 Series edited in Sonarr" in logger.info_messages
        assert "TVDb ID Not in Sonarr | 999" in logger.info_messages


class TestRemoveAllWithTags:
    def test_removes_only_series_with_every_tag_and_keeps_their_files(self, make_sonarr):
        sonarr, api = make_sonarr()
        both = series(101, "Severance", tags=[tag(KOMETA, "kometa"), tag(ANIME, "Anime")])
        api.series = [both, series(202, "Frieren", tags=[tag(KOMETA, "kometa")]), series(303, "Andor")]
        sonarr.remove_all_with_tags(["Kometa", "anime"])
        assert api.sent("delete_multiple_series") == [{"ids": [both], "addImportExclusion": False, "deleteFiles": False, "per_request": None}]

    def test_nothing_is_deleted_when_no_series_has_every_tag(self, make_sonarr):
        sonarr, api = make_sonarr()
        api.series = [series(101, "Severance", tags=[tag(KOMETA, "kometa")])]
        sonarr.remove_all_with_tags(["kometa", "missing"])
        assert api.sent("delete_multiple_series") == []


class TestAddTvdb:
    @pytest.fixture
    def severance(self):
        return series(101, "Severance")

    @pytest.fixture
    def adding(self, make_sonarr, severance):
        def make(cache=None, **params):
            sonarr, api = make_sonarr(cache=cache, **params)
            api.lookup = {101: severance}
            return sonarr, api

        return make

    def test_adds_a_new_series_with_the_configured_defaults(self, adding, severance, logger):
        cache = FakeAddsCache()
        sonarr, api = adding(cache=cache)
        assert sonarr.add_tvdb([101]) == [severance]
        assert api.sent("get_series") == [{"series_id": None, "tvdb_id": 101}]
        assert api.sent("add_multiple_series") == [
            {
                "ids": [severance],
                "root_folder": "/tv",
                "quality_profile": "HD-1080p",
                "language_profile": "English",
                "monitor": "all",
                "season_folder": True,
                "search": False,
                "unmet_search": False,
                "series_type": "standard",
                "tags": [],
                "per_request": 100,
            }
        ]
        assert cache.updates == [(101, LIBRARY)]
        assert "Added to Sonarr | 101     | Severance" in logger.info_messages
        assert "1 Series added to Sonarr" in logger.info_messages

    def test_options_override_the_defaults(self, adding, severance):
        sonarr, api = adding(cutoff_search=True)
        sonarr.add_tvdb([101], folder="/anime", monitor="first", quality=1, language="Japanese", series="anime", season=False, tag=["kometa"], search=True, cutoff_search=False)
        add = api.sent("add_multiple_series")[0]
        assert {key: add[key] for key in add if key not in ("ids", "per_request")} == {
            "root_folder": "/anime",
            "quality_profile": 1,
            "language_profile": "Japanese",
            "monitor": "firstSeason",
            "season_folder": False,
            "search": True,
            "unmet_search": False,
            "series_type": "anime",
            "tags": ["kometa"],
        }

    @pytest.mark.parametrize(("monitor", "expected"), [("latest", "latestSeason"), ("pilot", "pilot"), ("none", "none")])
    def test_monitor_names_are_translated_for_sonarr(self, adding, monitor, expected):
        sonarr, api = adding(monitor=monitor)
        sonarr.add_tvdb([101])
        assert api.sent("add_multiple_series")[0]["monitor"] == expected

    def test_sonarr_v4_gets_the_placeholder_language_profile(self, adding):
        sonarr, api = adding()
        api._raw.v3 = False
        sonarr.add_tvdb([101])
        assert api.sent("add_multiple_series")[0]["language_profile"] == 1

    def test_works_without_a_cache(self, adding, severance):
        sonarr, _ = adding(cache=None)
        assert sonarr.add_tvdb([101]) == [severance]

    def test_cached_adds_are_skipped_without_a_lookup(self, adding, logger):
        sonarr, api = adding(cache=FakeAddsCache(cached=[101]))
        assert sonarr.add_tvdb([101]) == []
        assert api.sent("get_series") == []
        assert api.sent("add_multiple_series") == []
        assert "Skipped In Cache: [101]" in logger.info_messages
        assert "1 Series already exist in Sonarr" in logger.info_messages

    @pytest.mark.parametrize(("param", "option"), [(True, None), (False, True)])
    def test_ignore_cache_adds_cached_series_again(self, adding, severance, param, option):
        sonarr, _ = adding(cache=FakeAddsCache(cached=[101]), ignore_cache=param)
        options = {} if option is None else {"ignore_cache": option}
        assert sonarr.add_tvdb([101], **options) == [severance]

    def test_ids_sonarr_cannot_find_are_reported_as_invalid(self, adding, logger):
        sonarr, api = adding()
        assert sonarr.add_tvdb([999]) == []
        assert api.sent("add_multiple_series") == []
        assert "Invalid TVDb IDs: [999]" in logger.info_messages
        assert "1 Series with Invalid IDs" in logger.info_messages

    def test_rejected_and_excluded_adds_are_reported(self, adding, severance, logger):
        frieren = series(202, "Frieren")
        sonarr, api = adding()
        api.lookup[202] = frieren
        api.add_outcome = lambda shows: ([], [], [101], [202])
        assert sonarr.add_tvdb([101, 202]) == []
        assert "Invalid TVDb IDs: [101]" in logger.info_messages
        assert "Excluded TVDb IDs: [202]" in logger.info_messages
        assert "1 Series ignored by Sonarr's Exclusion List" in logger.info_messages

    def test_client_errors_while_adding_become_failed(self, adding):
        sonarr, api = adding()
        api.add_error = ArrException("Sonarr is down")
        with pytest.raises(Failed, match="Sonarr Error: Sonarr is down"):
            sonarr.add_tvdb([101])

    def test_ids_are_added_in_batches_of_100(self, make_sonarr):
        sonarr, api = make_sonarr()
        api.lookup = {tvdb_id: series(tvdb_id, f"Show {tvdb_id}") for tvdb_id in range(1, 206)}
        assert len(sonarr.add_tvdb(list(range(1, 206)))) == 205
        assert [len(add["ids"]) for add in api.sent("add_multiple_series")] == [100, 100, 5]

    def test_a_last_id_that_fails_lookup_still_sends_the_batch(self, adding, severance):
        sonarr, api = adding()
        assert sonarr.add_tvdb([101, 999]) == [severance]
        assert [add["ids"] for add in api.sent("add_multiple_series")] == [[severance]]


class TestAddTvdbExisting:
    @pytest.fixture
    def existing(self, make_sonarr):
        def make(quality=1, cache=None, **params):
            sonarr, api = make_sonarr(cache=cache, **params)
            api.series = [series(101, "Severance", path="/tv/Severance", quality=quality)]
            return sonarr, api

        return make

    def test_existing_series_are_left_alone_by_default(self, existing, logger):
        cache = FakeAddsCache()
        sonarr, api = existing(cache=cache)
        assert sonarr.add_tvdb([101]) == []
        assert api.sent("get_series") == []
        assert api.sent("add_multiple_series") == []
        assert api.sent("edit_multiple_series") == []
        assert cache.updates == [(101, LIBRARY)]
        assert "Already in Sonarr | 101     | Severance" in logger.info_messages
        assert "1 Series already exist in Sonarr" in logger.info_messages

    @pytest.mark.parametrize("quality_profile", ["HD-1080p", 4])
    def test_upgrade_existing_moves_series_to_the_quality_profile(self, existing, logger, quality_profile):
        sonarr, api = existing(quality_profile=quality_profile, upgrade_existing=True)
        sonarr.add_tvdb([101])
        edits = api.sent("edit_multiple_series")
        assert [(edit["ids"], edit["quality_profile"], edit["monitor"]) for edit in edits] == [([101], 4, None)]
        assert "Quality Upgraded To HD-1080p | 101     | Severance" in logger.info_messages

    def test_upgrade_existing_skips_series_already_on_the_profile(self, existing, logger):
        sonarr, api = existing(quality=4, upgrade_existing=True)
        sonarr.add_tvdb([101])
        assert api.sent("edit_multiple_series") == []
        assert "Already in Sonarr | 101     | Severance" in logger.info_messages

    def test_upgrade_existing_with_an_unknown_profile_changes_nothing(self, existing):
        sonarr, api = existing(quality_profile="Ultra-HD", upgrade_existing=True)
        sonarr.add_tvdb([101])
        assert api.sent("edit_multiple_series") == []

    def test_monitor_existing_remonitors_with_the_translated_option(self, existing, logger):
        sonarr, api = existing(monitor_existing=True)
        sonarr.add_tvdb([101], monitor="latest")
        edits = api.sent("edit_multiple_series")
        assert [(edit["ids"], edit["monitor"], edit["quality_profile"]) for edit in edits] == [([101], "latestSeason", None)]
        assert "Monitored: latestSeason in Sonarr | 101     | Severance" in logger.info_messages

    def test_options_can_turn_upgrade_and_monitor_on_per_collection(self, existing):
        sonarr, api = existing()
        sonarr.add_tvdb([101], upgrade_existing=True, monitor_existing=True)
        assert [(edit["quality_profile"], edit["monitor"]) for edit in api.sent("edit_multiple_series")] == [(4, None), (None, "all")]

    def test_series_sonarr_reports_as_existing_while_adding_are_handled_the_same(self, make_sonarr, logger):
        severance = series(101, "Severance")
        sonarr, api = make_sonarr(monitor_existing=True)
        api.lookup = {101: severance}
        api.add_outcome = lambda shows: ([], [severance], [], [])
        assert sonarr.add_tvdb([101]) == []
        assert api.sent("edit_multiple_series")[0]["ids"] == [101]


class TestAddTvdbWithPaths:
    """Adding existing Plex shows passes (tvdb_id, path) pairs, with the path already mapped to Sonarr's side."""

    def test_the_plex_path_is_sent_with_the_series(self, make_sonarr):
        severance = series(101, "Severance")
        sonarr, api = make_sonarr()
        api.lookup = {101: severance}
        assert sonarr.add_tvdb([(101, "/tv/Severance (2022)")]) == [severance]
        assert api.sent("add_multiple_series")[0]["ids"] == [(severance, "/tv/Severance (2022)")]

    # Sonarr's paths are compared case-insensitively and without a trailing slash.
    def test_a_path_sonarr_has_under_another_id_is_reported_as_mismatched(self, make_sonarr, logger):
        sonarr, api = make_sonarr()
        api.series = [series(202, "Severance (old)", path="/TV/Severance/")]
        assert sonarr.add_tvdb([(101, "/tv/Severance")]) == []
        assert api.sent("get_series") == []
        assert "Plex TVDb ID: 101     | Sonarr TVDb ID: 202     | Path: /tv/Severance" in logger.info_messages
        assert "1 Series with mismatched TVDb IDs" in logger.info_messages

    def test_a_path_outside_the_root_folder_is_reported(self, make_sonarr, logger):
        sonarr, api = make_sonarr()
        assert sonarr.add_tvdb([(101, "/media/Severance")]) == []
        assert api.sent("get_series") == []
        assert "Invalid Root Folder for TVDb ID | 101     | /media/Severance" in logger.info_messages
        assert "1 Series with Invalid Paths" in logger.info_messages

    def test_a_new_series_whose_folder_is_taken_is_reported_and_not_added(self, make_sonarr, logger):
        sonarr, api = make_sonarr()
        api.series = [series(202, "Other", path="/tv/Severance"), series(303, "Not on disk yet")]
        api.lookup = {101: series(101, "Severance")}
        assert sonarr.add_tvdb([101]) == []
        assert api.sent("add_multiple_series") == []
        assert "TVDb ID: 101     | Sonarr TVDb ID: 202     | Path: /tv/Severance" in logger.info_messages
        assert "1 Series with paths already in use by other TVDb IDs" in logger.info_messages
