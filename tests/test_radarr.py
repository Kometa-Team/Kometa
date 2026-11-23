"""Tests for the Radarr connector, run against a fake arrapi client that records every call."""

import inspect
from types import SimpleNamespace

import pytest
from arrapi import RadarrAPI
from arrapi.exceptions import ArrException, NotFound, Unauthorized

import modules.radarr as radarr_module
import modules.timings as timings_module
from modules.radarr import Radarr
from modules.timings import TimingRegistry
from modules.util import Failed
from tests.conftest import FakeLogger

URL = "http://radarr:7878"
TOKEN = "radarr-api-key"
LIBRARY = "Movies"

KOMETA, UHD = 10, 11


def tag(tag_id, label):
    return SimpleNamespace(id=tag_id, label=label)


def movie(tmdb_id, title, path=None, tags=(), quality=1, monitored=True):
    return SimpleNamespace(tmdbId=tmdb_id, title=title, path=path, tags=list(tags), qualityProfileId=quality, monitored=monitored, folder=title)


class FakeRadarrAPI:
    """Stand-in for arrapi.RadarrAPI.

    Each call is bound to the real RadarrAPI method's signature, so a call arrapi would reject fails here too,
    and is recorded with its arguments by name (defaults filled in).
    """

    def __init__(self):
        self.movies = []
        self.lookup = {}
        self.tags = [tag(KOMETA, "kometa"), tag(UHD, "UHD")]
        self.profiles = [SimpleNamespace(id=1, name="Any"), SimpleNamespace(id=4, name="HD-1080p")]
        self.setup_error = None
        self.add_error = None
        self.add_outcome = None
        self.calls = []

    def _record(self, name, *args, **kwargs):
        bound = inspect.signature(getattr(RadarrAPI, name)).bind(self, *args, **kwargs)
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

    def all_movies(self, *args, **kwargs):
        self._record("all_movies", *args, **kwargs)
        return list(self.movies)

    def all_tags(self, *args, **kwargs):
        self._record("all_tags", *args, **kwargs)
        return list(self.tags)

    def get_movie(self, *args, **kwargs):
        tmdb_id = self._record("get_movie", *args, **kwargs)["tmdb_id"]
        if tmdb_id not in self.lookup:
            raise NotFound(f"Item Not Found: {tmdb_id}")
        return self.lookup[tmdb_id]

    def add_multiple_movies(self, *args, **kwargs):
        movies = self._record("add_multiple_movies", *args, **kwargs)["ids"]
        if self.add_error:
            raise self.add_error
        if self.add_outcome:
            return self.add_outcome(movies)
        return [item[0] if isinstance(item, tuple) else item for item in movies], [], [], []

    def edit_multiple_movies(self, *args, **kwargs):
        ids = self._record("edit_multiple_movies", *args, **kwargs)["ids"]
        known = {item.tmdbId: item for item in self.movies}
        return [known[i] for i in ids if i in known], [i for i in ids if i not in known]

    def delete_multiple_movies(self, *args, **kwargs):
        self._record("delete_multiple_movies", *args, **kwargs)
        return []


class FakeAddsCache:
    def __init__(self, cached=()):
        self.cached = set(cached)
        self.updates = []

    def query_radarr_adds(self, tmdb_id, library):
        return tmdb_id if tmdb_id in self.cached else None

    def update_radarr_adds(self, tmdb_id, library):
        self.updates.append((tmdb_id, library))


def make_params(**overrides):
    params = {
        "url": URL,
        "token": TOKEN,
        "add_missing": False,
        "add_existing": False,
        "upgrade_existing": False,
        "monitor_existing": False,
        "root_folder_path": "/movies",
        "monitor": True,
        "availability": "announced",
        "quality_profile": "HD-1080p",
        "tag": [],
        "search": False,
        "radarr_path": "",
        "plex_path": "",
        "ignore_cache": False,
    }
    params.update(overrides)
    return params


def connect(monkeypatch, api=None, cache=None, **params):
    api = api or FakeRadarrAPI()
    session = object()
    monkeypatch.setattr(radarr_module, "RadarrAPI", api.connect)
    radarr = Radarr(SimpleNamespace(session=session), cache, SimpleNamespace(original_mapping_name=LIBRARY), make_params(**params))
    return radarr, api, session


@pytest.fixture
def make_radarr(monkeypatch):
    """A connected Radarr whose fake client has forgotten the setup calls."""

    def make(api=None, cache=None, **params):
        radarr, api, _ = connect(monkeypatch, api, cache, **params)
        api.calls.clear()
        return radarr, api

    return make


@pytest.fixture(autouse=True)
def logger(monkeypatch):
    fake = FakeLogger()
    monkeypatch.setattr(radarr_module, "logger", fake)
    return fake


@pytest.fixture(autouse=True)
def registry(monkeypatch):
    fresh = TimingRegistry()
    monkeypatch.setattr(timings_module, "registry", fresh)
    return fresh


def test_the_fake_rejects_calls_the_real_client_would_reject():
    with pytest.raises(TypeError):
        FakeRadarrAPI().edit_multiple_movies([550], quality=4)


class TestConnect:
    def test_connects_with_the_shared_session_and_validates_the_add_options(self, monkeypatch):
        radarr, api, session = connect(monkeypatch)
        assert [call for call, _ in api.calls] == ["__init__", "respect_list_exclusions_when_adding", "_validate_add_options", "quality_profile"]
        assert api.sent("__init__") == [{"url": URL, "apikey": TOKEN, "session": session}]
        validated = api.sent("_validate_add_options")[0]
        assert (validated["root_folder"], validated["quality_profile"]) == ("/movies", "HD-1080p")
        assert radarr.profiles == api.profiles

    def test_url_and_token_are_redacted_and_the_host_is_tagged_for_timings(self, monkeypatch, logger, registry):
        connect(monkeypatch)
        assert URL in logger.secrets
        assert TOKEN in logger.secrets
        assert registry.arr_hosts == {"radarr:7878": "radarr"}

    @pytest.mark.parametrize(
        ("radarr_path", "plex_path", "expected"),
        [("/data/movies", "/media/movies", ("/data/movies", "/media/movies")), ("/data/movies", "", ("", "")), ("", "/media/movies", ("", ""))],
    )
    def test_path_mapping_needs_both_sides(self, monkeypatch, radarr_path, plex_path, expected):
        radarr, _, _ = connect(monkeypatch, radarr_path=radarr_path, plex_path=plex_path)
        assert (radarr.radarr_path, radarr.plex_path) == expected

    def test_client_errors_become_failed(self, monkeypatch):
        api = FakeRadarrAPI()
        api.setup_error = Unauthorized("Invalid API Key")
        with pytest.raises(Failed, match="Invalid API Key"):
            connect(monkeypatch, api)


class TestGetTmdbIds:
    @pytest.fixture
    def tagged(self, make_radarr):
        radarr, api = make_radarr()
        api.movies = [
            movie(550, "Fight Club", tags=[tag(KOMETA, "kometa")]),
            movie(603, "The Matrix", tags=[tag(UHD, "UHD")]),
            movie(680, "Pulp Fiction"),
        ]
        return radarr, api

    def test_all_returns_every_movie_without_reading_tags(self, tagged):
        radarr, api = tagged
        assert radarr.get_tmdb_ids("radarr_all", True) == [(550, "tmdb"), (603, "tmdb"), (680, "tmdb")]
        assert api.sent("all_tags") == []

    # The builder lower-cases the tag list, while Radarr keeps the label's case ("UHD").
    @pytest.mark.parametrize(("data", "expected"), [(["kometa"], [550]), (["uhd"], [603]), (["kometa", "uhd"], [550, 603])])
    def test_taglist_selects_movies_with_any_of_the_tags(self, tagged, data, expected):
        radarr, _ = tagged
        assert radarr.get_tmdb_ids("radarr_taglist", data) == [(tmdb_id, "tmdb") for tmdb_id in expected]

    def test_blank_taglist_selects_only_untagged_movies(self, tagged):
        radarr, _ = tagged
        assert radarr.get_tmdb_ids("radarr_taglist", []) == [(680, "tmdb")]

    def test_taglist_with_a_tag_missing_from_radarr_selects_nothing(self, tagged):
        radarr, _ = tagged
        assert radarr.get_tmdb_ids("radarr_taglist", ["missing"]) == []

    def test_empty_when_radarr_has_no_movies(self, make_radarr):
        radarr, _ = make_radarr()
        assert radarr.get_tmdb_ids("radarr_all", True) == []


class TestEditTags:
    @pytest.mark.parametrize(("apply_tags", "mode"), [("", "add"), ("sync", "replace"), ("remove", "remove")])
    def test_sends_the_translated_apply_mode_in_batches_of_100(self, make_radarr, logger, apply_tags, mode):
        radarr, api = make_radarr()
        radarr.edit_tags([550], ["kometa"], apply_tags)
        edit = api.sent("edit_multiple_movies")[0]
        assert (edit["ids"], edit["tags"], edit["apply_tags"], edit["per_request"]) == ([550], ["kometa"], mode, 100)
        assert f"{mode.capitalize()} Radarr Tags: ['kometa']" in logger.info_messages

    def test_reports_edited_movies_and_ids_not_in_radarr(self, make_radarr, logger):
        radarr, api = make_radarr()
        api.movies = [movie(550, "Fight Club", tags=["kometa"]), movie(603, "The Matrix", tags=["kometa"])]
        radarr.edit_tags([550, 603, 999], ["kometa"], "")
        assert f"Radarr Tags | {'Fight Club':<25} | ['kometa']" in logger.info_messages
        assert "2 Movies edited in Radarr" in logger.info_messages
        assert "TMDb ID Not in Radarr | 999" in logger.info_messages


class TestRemoveAllWithTags:
    def test_removes_only_movies_with_every_tag_and_keeps_their_files(self, make_radarr):
        radarr, api = make_radarr()
        both = movie(550, "Fight Club", tags=[tag(KOMETA, "kometa"), tag(UHD, "UHD")])
        api.movies = [both, movie(603, "The Matrix", tags=[tag(KOMETA, "kometa")]), movie(680, "Pulp Fiction")]
        radarr.remove_all_with_tags(["Kometa", "uhd"])
        assert api.sent("delete_multiple_movies") == [{"ids": [both], "addImportExclusion": False, "deleteFiles": False, "per_request": None}]

    def test_nothing_is_deleted_when_no_movie_has_every_tag(self, make_radarr):
        radarr, api = make_radarr()
        api.movies = [movie(550, "Fight Club", tags=[tag(KOMETA, "kometa")])]
        radarr.remove_all_with_tags(["kometa", "missing"])
        assert api.sent("delete_multiple_movies") == []


class TestAddTmdb:
    @pytest.fixture
    def fight_club(self):
        return movie(550, "Fight Club")

    @pytest.fixture
    def adding(self, make_radarr, fight_club):
        def make(cache=None, **params):
            radarr, api = make_radarr(cache=cache, **params)
            api.lookup = {550: fight_club}
            return radarr, api

        return make

    def test_adds_a_new_movie_with_the_configured_defaults(self, adding, fight_club, logger):
        cache = FakeAddsCache()
        radarr, api = adding(cache=cache)
        assert radarr.add_tmdb([550]) == [fight_club]
        assert api.sent("get_movie") == [{"movie_id": None, "tmdb_id": 550, "imdb_id": None}]
        assert api.sent("add_multiple_movies") == [
            {
                "ids": [fight_club],
                "root_folder": "/movies",
                "quality_profile": "HD-1080p",
                "monitor": True,
                "search": False,
                "minimum_availability": "announced",
                "tags": [],
                "per_request": 100,
            }
        ]
        assert cache.updates == [(550, LIBRARY)]
        assert "Added to Radarr | 550     | Fight Club" in logger.info_messages
        assert "1 Movie added to Radarr" in logger.info_messages

    def test_options_override_the_defaults(self, adding):
        radarr, api = adding()
        radarr.add_tmdb([550], folder="/movies-4k", monitor=False, availability="released", quality=1, tag=["kometa"], search=True)
        add = api.sent("add_multiple_movies")[0]
        assert {key: add[key] for key in add if key not in ("ids", "per_request")} == {
            "root_folder": "/movies-4k",
            "quality_profile": 1,
            "monitor": False,
            "search": True,
            "minimum_availability": "released",
            "tags": ["kometa"],
        }

    @pytest.mark.parametrize(("availability", "expected"), [("cinemas", "inCinemas"), ("db", "preDB")])
    def test_availability_names_are_translated_for_radarr(self, adding, availability, expected):
        radarr, api = adding(availability=availability)
        radarr.add_tmdb([550])
        assert api.sent("add_multiple_movies")[0]["minimum_availability"] == expected

    def test_works_without_a_cache(self, adding, fight_club):
        radarr, _ = adding(cache=None)
        assert radarr.add_tmdb([550]) == [fight_club]

    def test_cached_adds_are_skipped_without_a_lookup(self, adding, logger):
        radarr, api = adding(cache=FakeAddsCache(cached=[550]))
        assert radarr.add_tmdb([550]) == []
        assert api.sent("get_movie") == []
        assert api.sent("add_multiple_movies") == []
        assert "Skipped In Cache: [550]" in logger.info_messages
        assert "1 Movie already exist in Radarr" in logger.info_messages

    @pytest.mark.parametrize(("param", "option"), [(True, None), (False, True)])
    def test_ignore_cache_adds_cached_movies_again(self, adding, fight_club, param, option):
        radarr, _ = adding(cache=FakeAddsCache(cached=[550]), ignore_cache=param)
        options = {} if option is None else {"ignore_cache": option}
        assert radarr.add_tmdb([550], **options) == [fight_club]

    def test_ids_radarr_cannot_find_are_reported_as_invalid(self, adding, logger):
        radarr, api = adding()
        assert radarr.add_tmdb([999]) == []
        assert api.sent("add_multiple_movies") == []
        assert "Invalid TMDb IDs: [999]" in logger.info_messages
        assert "1 Movie with Invalid IDs" in logger.info_messages

    def test_rejected_and_excluded_adds_are_reported(self, adding, logger):
        radarr, api = adding()
        api.lookup[603] = movie(603, "The Matrix")
        api.add_outcome = lambda movies: ([], [], [550], [603])
        assert radarr.add_tmdb([550, 603]) == []
        assert "Invalid TMDb IDs: [550]" in logger.info_messages
        assert "Excluded TMDb IDs: [603]" in logger.info_messages
        assert "1 Movie ignored by Radarr's Exclusion List" in logger.info_messages

    def test_client_errors_while_adding_become_failed(self, adding):
        radarr, api = adding()
        api.add_error = ArrException("Radarr is down")
        with pytest.raises(Failed, match="Radarr Error: Radarr is down"):
            radarr.add_tmdb([550])

    def test_ids_are_added_in_batches_of_100(self, make_radarr):
        radarr, api = make_radarr()
        api.lookup = {tmdb_id: movie(tmdb_id, f"Movie {tmdb_id}") for tmdb_id in range(1, 206)}
        assert len(radarr.add_tmdb(list(range(1, 206)))) == 205
        assert [len(add["ids"]) for add in api.sent("add_multiple_movies")] == [100, 100, 5]

    def test_a_last_id_that_fails_lookup_still_sends_the_batch(self, adding, fight_club):
        radarr, api = adding()
        assert radarr.add_tmdb([550, 999]) == [fight_club]
        assert [add["ids"] for add in api.sent("add_multiple_movies")] == [[fight_club]]


class TestAddTmdbExisting:
    @pytest.fixture
    def existing(self, make_radarr):
        def make(quality=1, monitored=True, cache=None, **params):
            radarr, api = make_radarr(cache=cache, **params)
            api.movies = [movie(550, "Fight Club", path="/movies/Fight Club", quality=quality, monitored=monitored)]
            return radarr, api

        return make

    def test_existing_movies_are_left_alone_by_default(self, existing, logger):
        cache = FakeAddsCache()
        radarr, api = existing(monitored=False, cache=cache)
        assert radarr.add_tmdb([550]) == []
        assert api.sent("get_movie") == []
        assert api.sent("add_multiple_movies") == []
        assert api.sent("edit_multiple_movies") == []
        assert cache.updates == [(550, LIBRARY)]
        assert "Already in Radarr | 550     | Fight Club" in logger.info_messages
        assert "1 Movie already exist in Radarr" in logger.info_messages

    @pytest.mark.parametrize("quality_profile", ["HD-1080p", 4])
    def test_upgrade_existing_moves_movies_to_the_quality_profile(self, existing, logger, quality_profile):
        radarr, api = existing(quality_profile=quality_profile, upgrade_existing=True)
        radarr.add_tmdb([550])
        edits = api.sent("edit_multiple_movies")
        assert [(edit["ids"], edit["quality_profile"], edit["monitored"]) for edit in edits] == [([550], 4, None)]
        assert "Quality Upgraded To HD-1080p | 550     | Fight Club" in logger.info_messages

    def test_upgrade_existing_skips_movies_already_on_the_profile(self, existing, logger):
        radarr, api = existing(quality=4, upgrade_existing=True)
        radarr.add_tmdb([550])
        assert api.sent("edit_multiple_movies") == []
        assert "Already in Radarr | 550     | Fight Club" in logger.info_messages

    def test_upgrade_existing_with_an_unknown_profile_changes_nothing(self, existing):
        radarr, api = existing(quality_profile="Ultra-HD", upgrade_existing=True)
        radarr.add_tmdb([550])
        assert api.sent("edit_multiple_movies") == []

    @pytest.mark.parametrize(("monitored", "monitor"), [(False, True), (True, False)])
    def test_monitor_existing_sets_monitored_to_the_monitor_option(self, existing, logger, monitored, monitor):
        radarr, api = existing(monitored=monitored, monitor_existing=True)
        radarr.add_tmdb([550], monitor=monitor)
        edits = api.sent("edit_multiple_movies")
        assert [(edit["ids"], edit["monitored"], edit["quality_profile"]) for edit in edits] == [([550], monitor, None)]
        assert f"Monitored: {monitor} in Radarr | 550     | Fight Club" in logger.info_messages

    def test_monitor_existing_skips_movies_already_monitored_that_way(self, existing, logger):
        radarr, api = existing(monitored=True, monitor_existing=True)
        radarr.add_tmdb([550])
        assert api.sent("edit_multiple_movies") == []
        assert "Already in Radarr | 550     | Fight Club" in logger.info_messages

    def test_options_can_turn_upgrade_and_monitor_on_per_collection(self, existing):
        radarr, api = existing(monitored=False)
        radarr.add_tmdb([550], upgrade_existing=True, monitor_existing=True)
        assert [(edit["quality_profile"], edit["monitored"]) for edit in api.sent("edit_multiple_movies")] == [(4, None), (None, True)]

    @pytest.mark.parametrize(("quality", "monitored", "expected"), [(1, True, [(4, None)]), (4, False, [(None, True)])])
    def test_with_both_on_only_the_setting_that_differs_is_changed(self, existing, quality, monitored, expected):
        radarr, api = existing(quality=quality, monitored=monitored, upgrade_existing=True, monitor_existing=True)
        radarr.add_tmdb([550])
        assert [(edit["quality_profile"], edit["monitored"]) for edit in api.sent("edit_multiple_movies")] == expected

    def test_movies_radarr_reports_as_existing_while_adding_are_handled_the_same(self, make_radarr):
        fight_club = movie(550, "Fight Club", monitored=False)
        radarr, api = make_radarr(monitor_existing=True)
        api.lookup = {550: fight_club}
        api.add_outcome = lambda movies: ([], [fight_club], [], [])
        assert radarr.add_tmdb([550]) == []
        assert api.sent("edit_multiple_movies")[0]["ids"] == [550]


class TestAddTmdbWithPaths:
    """Adding existing Plex movies passes (tmdb_id, path) pairs, with the path already mapped to Radarr's side."""

    def test_the_plex_path_is_sent_with_the_movie(self, make_radarr):
        fight_club = movie(550, "Fight Club")
        radarr, api = make_radarr()
        api.lookup = {550: fight_club}
        assert radarr.add_tmdb([(550, "/movies/Fight Club (1999)")]) == [fight_club]
        assert api.sent("add_multiple_movies")[0]["ids"] == [(fight_club, "/movies/Fight Club (1999)")]

    # Radarr's paths are compared case-insensitively and without a trailing slash.
    def test_a_path_radarr_has_under_another_id_is_reported_as_mismatched(self, make_radarr, logger):
        radarr, api = make_radarr()
        api.movies = [movie(603, "Fight Club (old)", path="/Movies/Fight Club/")]
        assert radarr.add_tmdb([(550, "/movies/Fight Club")]) == []
        assert api.sent("get_movie") == []
        assert "Plex TMDb ID: 550     | Radarr TMDb ID: 603     | Path: /movies/Fight Club" in logger.info_messages
        assert "1 Movie with mismatched TMDb IDs" in logger.info_messages

    def test_a_path_outside_the_root_folder_is_reported(self, make_radarr, logger):
        radarr, api = make_radarr()
        assert radarr.add_tmdb([(550, "/media/Fight Club")]) == []
        assert api.sent("get_movie") == []
        assert "Invalid Root Folder for TMDb ID | 550     | /media/Fight Club" in logger.info_messages
        assert "1 Movie with Invalid Paths" in logger.info_messages

    def test_a_new_movie_whose_folder_is_taken_is_reported_and_not_added(self, make_radarr, logger):
        radarr, api = make_radarr()
        api.movies = [movie(603, "Other", path="/Movies/Fight Club"), movie(680, "Not on disk yet")]
        api.lookup = {550: movie(550, "Fight Club")}
        assert radarr.add_tmdb([550]) == []
        assert api.sent("add_multiple_movies") == []
        assert "TMDb ID: 550     | Radarr TMDb ID: 603     | Path: /movies/Fight Club" in logger.info_messages
        assert "1 Movie with paths already in use by other TMDb IDs" in logger.info_messages
