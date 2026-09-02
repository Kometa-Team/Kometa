from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from tenacity import RetryError, wait_none
from tmdbapis import NotFound as TMDbApiNotFound

from modules import tmdb
from modules.util import Failed, ServiceError


def _bare_tmdb(monkeypatch):
    from tests.conftest import FakeLogger

    monkeypatch.setattr(tmdb, "logger", FakeLogger())
    return tmdb.TMDb.__new__(tmdb.TMDb)


def _episode(episode_id, season_number, episode_number, vote_average):
    return SimpleNamespace(
        id=episode_id,
        season_number=season_number,
        episode_number=episode_number,
        title=f"Episode {episode_number}",
        air_date=None,
        overview="",
        still_url="",
        vote_count=1,
        vote_average=vote_average,
        imdb_id=None,
        tvdb_id=None,
    )


def test_notfound_is_failed_subclass():
    # Callers that keep catching every TMDb failure as Failed must still work.
    assert issubclass(tmdb.NotFound, Failed)


def test_unavailable_is_service_error_subclass():
    assert issubclass(tmdb.Unavailable, ServiceError)


@pytest.mark.parametrize(
    "message",
    [
        "(502 [Bad Gateway]) {'status_code': 43, 'status_message': \"Couldn't connect to the backend server.\"}",
        "(408 [Request Timeout]) {'status_code': 24}",
        "(429 [Too Many Requests]) {'status_code': 25}",
        "(503 [Service Unavailable]) {'status_code': 9}",
        "{'status_code': 46, 'status_message': 'The API is undergoing maintenance.'}",
    ],
)
def test_tmdb_service_failures_are_transient(message):
    assert tmdb._is_transient_tmdb_exception(tmdb.TMDbException(message))


def test_tmdb_404_is_not_transient():
    assert not tmdb._is_transient_tmdb_exception(tmdb.TMDbException("(404 [Not Found]) {'status_code': 34}"))


def test_structured_status_takes_precedence_over_message_status():
    response_error = Exception("(502 [Bad Gateway]) {'status_code': 43}")
    response_error.response = SimpleNamespace(status_code=404)
    exception_error = Exception("(502 [Bad Gateway]) {'status_code': 43}")
    exception_error.status_code = 404
    transient_error = Exception("(404 [Not Found]) {'status_code': 34}")
    transient_error.response = SimpleNamespace(status_code=502)

    assert not tmdb._is_transient_tmdb_exception(response_error)
    assert not tmdb._is_transient_tmdb_exception(exception_error)
    assert tmdb._is_transient_tmdb_exception(transient_error)


@pytest.mark.parametrize(
    "error",
    [
        tmdb.TMDbException("(502 [Bad Gateway]) {'status_code': 43}"),
        tmdb.TMDbException("(429 [Too Many Requests]) {'status_code': 25}"),
        tmdb.ReadTimeout("TMDb request timed out"),
    ],
)
def test_discover_retries_transient_service_errors_without_traceback(monkeypatch, error):
    t = _bare_tmdb(monkeypatch)
    logger = tmdb.logger
    results = SimpleNamespace(total_results=2, get_results=MagicMock(side_effect=[error, [SimpleNamespace(id=10), SimpleNamespace(id=20)]]))
    discover = MagicMock(return_value=results)
    t.TMDb = SimpleNamespace(discover_tv_shows=discover)
    monkeypatch.setattr(tmdb.TMDb._get_discover_results.retry, "wait", wait_none())

    ids, amount = t._get_discover_ids({"watch_region": "US"}, False, "tmdb_show", 0)

    assert ids == [(10, "tmdb_show"), (20, "tmdb_show")]
    assert amount == 2
    discover.assert_called_once_with(watch_region="US")
    assert results.get_results.call_count == 2
    assert len(logger.warning_messages) == 1
    assert "transient service error" in logger.warning_messages[0]


@pytest.mark.parametrize(
    "error",
    [
        tmdb.TMDbException("(401 [Unauthorized]) {'status_code': 7}"),
        tmdb.TMDbException("(404 [Not Found]) {'status_code': 34}"),
        Failed("terminal Kometa failure"),
        TypeError("programming error"),
    ],
)
def test_discover_does_not_retry_terminal_errors(monkeypatch, error):
    t = _bare_tmdb(monkeypatch)
    results = SimpleNamespace(total_results=2, get_results=MagicMock(side_effect=error))
    discover = MagicMock(return_value=results)
    t.TMDb = SimpleNamespace(discover_tv_shows=discover)
    monkeypatch.setattr(tmdb.TMDb._get_discover_results.retry, "wait", wait_none())

    with pytest.raises(type(error)) as excinfo:
        t._get_discover_ids({}, False, "tmdb_show", 0)

    assert str(excinfo.value) == str(error)
    discover.assert_called_once_with()
    results.get_results.assert_called_once_with(2)


def test_discover_exhaustion_becomes_service_unavailable(monkeypatch):
    t = _bare_tmdb(monkeypatch)
    results = SimpleNamespace(total_results=2, get_results=MagicMock(side_effect=tmdb.TMDbException("(502 [Bad Gateway]) {'status_code': 43}")))
    discover = MagicMock(return_value=results)
    t.TMDb = SimpleNamespace(discover_tv_shows=discover)
    monkeypatch.setattr(tmdb.TMDb._get_discover_results.retry, "wait", wait_none())

    with pytest.raises(tmdb.Unavailable, match="Service unavailable after 6 attempts"):
        t._get_discover_ids({}, False, "tmdb_show", 0)

    discover.assert_called_once_with()
    assert results.get_results.call_count == 6


def test_show_hydration_retries_lazy_transient_502(monkeypatch):
    t = _bare_tmdb(monkeypatch)
    logger = MagicMock()
    monkeypatch.setattr(tmdb, "logger", logger)
    t.cache = None
    t.language = "en"
    t.expiration = 30

    class FlakyShow:
        title = "Test Show"
        tagline = ""
        overview = ""
        imdb_id = "tt123"
        poster_url = None
        backdrop_url = None
        logos = []
        vote_average = 8.0
        original_language = SimpleNamespace(iso_639_1="en", english_name="English")
        genres = []
        keywords = []
        original_name = "Test Show"
        first_air_date = None
        last_air_date = None
        status = "Returning Series"
        type = "Scripted"
        networks = []
        tvdb_id = 123
        origin_countries = []
        seasons = []

        def __init__(self):
            self.vote_count_calls = 0

        @property
        def vote_count(self):
            self.vote_count_calls += 1
            if self.vote_count_calls == 1:
                raise tmdb.TMDbException("(502 [Bad Gateway]) {'status_code': 43}")
            return 10

    data = FlakyShow()
    t.TMDb = SimpleNamespace(tv_show=MagicMock(return_value=data))
    monkeypatch.setattr(tmdb.TMDbShow._load_data.retry, "wait", wait_none())

    show = tmdb.TMDbShow(t, 500)

    assert show.vote_count == 10
    assert data.vote_count_calls == 2
    logger.warning.assert_called_once()
    logger.stacktrace.assert_not_called()


@pytest.mark.parametrize(
    ("value_type", "aggregate_key"),
    [
        ("agg_tv_cast", "roles"),
        ("agg_tv_crew", "jobs"),
    ],
)
def test_aggregate_credits_skip_malformed_entries(monkeypatch, value_type, aggregate_key):
    logger = MagicMock()
    monkeypatch.setattr(tmdb, "logger", logger)
    captured = {}

    def parent_parse(self, **kwargs):
        captured.update(kwargs)
        return "parsed"

    monkeypatch.setattr(tmdb.TMDbAPIs, "_parse", parent_parse)
    api = tmdb.KometaTMDbAPIs.__new__(tmdb.KometaTMDbAPIs)
    valid_entry = {"character" if aggregate_key == "roles" else "job": "Presenter"}
    original = {"id": 10, "name": "Example Person", aggregate_key: [valid_entry, ["malformed"], None]}

    assert api._parse(data=original, value_type=value_type) == "parsed"
    assert captured["data"][aggregate_key] == [valid_entry]
    assert original[aggregate_key] == [valid_entry, ["malformed"], None]
    logger.warning.assert_called_once()


def test_show_hydration_wraps_unexpected_parser_errors(monkeypatch):
    logger = MagicMock()
    monkeypatch.setattr(tmdb, "logger", logger)
    show = tmdb.TMDbShow.__new__(tmdb.TMDbShow)
    show.tmdb_id = 500

    class MalformedShow:
        @property
        def title(self):
            raise AttributeError("'list' object has no attribute 'items'")

    with pytest.raises(Failed, match=r"Failed to parse Show with TMDb ID 500.*list.*items"):
        show._load_data(MalformedShow())

    logger.stacktrace.assert_called_once_with()


def test_episode_hydration_wraps_unexpected_parser_errors(monkeypatch):
    logger = MagicMock()
    monkeypatch.setattr(tmdb, "logger", logger)
    episode = tmdb.TMDbEpisode.__new__(tmdb.TMDbEpisode)
    episode.tmdb_id = 500
    episode.season_number = 2
    episode.episode_number = 3

    class MalformedEpisode:
        @property
        def id(self):
            raise AttributeError("'list' object has no attribute 'items'")

    with pytest.raises(Failed, match=r"Failed to parse Episode with TMDb ID 500 Season 2 Episode 3.*list.*items"):
        episode._load_data(MalformedEpisode())

    logger.stacktrace.assert_called_once_with()


def test_get_collection_raises_notfound_for_deleted_collection(monkeypatch):
    t = _bare_tmdb(monkeypatch)

    def deleted(tmdb_id, partial=None):
        raise TMDbApiNotFound("(404) Requested Item Not Found")

    t.TMDb = SimpleNamespace(collection=deleted)
    with pytest.raises(tmdb.NotFound) as excinfo:
        t.get_collection(1664873)
    assert "1664873" in str(excinfo.value)
    assert "No Collection found" in str(excinfo.value)


def test_validate_tmdb_ids_all_deleted_raises_notfound(monkeypatch):
    t = _bare_tmdb(monkeypatch)

    def all_gone(tmdb_id, tmdb_method):
        raise tmdb.NotFound(f"TMDb Error: No Collection found for TMDb ID {tmdb_id}")

    t.validate_tmdb = all_gone
    # Every ID is gone from TMDb -> NotFound (not a plain Failed) so the caller
    # can downgrade it instead of treating it as a hard collection failure.
    with pytest.raises(tmdb.NotFound):
        t.validate_tmdb_ids("1664873, 1664903", "tmdb_collection")


def test_validate_tmdb_ids_partial_failure_raises_failed(monkeypatch):
    t = _bare_tmdb(monkeypatch)

    def mixed(tmdb_id, tmdb_method):
        if tmdb_id == 1664873:
            raise tmdb.NotFound("gone from TMDb")
        raise Failed("transient TMDb error")

    t.validate_tmdb = mixed
    # A non-NotFound failure in the mix means we must NOT downgrade: a plain
    # Failed is raised so the collection still surfaces as an error.
    with pytest.raises(Failed) as excinfo:
        t.validate_tmdb_ids("1664873, 99999", "tmdb_collection")
    assert not isinstance(excinfo.value, tmdb.NotFound)


def test_validate_tmdb_ids_returns_valid_ids(monkeypatch):
    t = _bare_tmdb(monkeypatch)
    t.validate_tmdb = lambda tmdb_id, tmdb_method: tmdb_id
    assert t.validate_tmdb_ids("391, 938, 429", "tmdb_movie") == [391, 938, 429]


def test_get_episode_by_id_builds_and_reuses_show_map(monkeypatch):
    t = _bare_tmdb(monkeypatch)
    t.language = "en"
    t.cache = None
    t._episode_id_maps = {}
    t._complete_episode_id_maps = set()
    t.get_show = MagicMock(return_value=SimpleNamespace(seasons=[SimpleNamespace(season_number=1), SimpleNamespace(season_number=2)]))
    episodes = {
        1: [_episode(101, 1, 1, 7.1), _episode(102, 1, 2, 7.2)],
        2: [_episode(201, 2, 1, 8.1)],
    }
    t.get_season = MagicMock(side_effect=lambda _, season_number: SimpleNamespace(episodes=episodes[season_number]))

    assert t.get_episode_by_id(500, 201).vote_average == 8.1
    assert t.get_episode_by_id(500, 101).vote_average == 7.1
    assert t.get_show.call_count == 1
    assert t.get_season.call_count == 2


def test_get_episode_by_id_bulk_writes_season_map_to_cache(monkeypatch):
    t = _bare_tmdb(monkeypatch)
    t.language = "en"
    t.expiration = 30
    t._episode_id_maps = {}
    t._complete_episode_id_maps = set()
    t.cache = MagicMock()
    t.cache.query_tmdb_episode_by_id.return_value = ({}, None)
    t.get_show = MagicMock(return_value=SimpleNamespace(seasons=[SimpleNamespace(season_number=1)]))
    t.get_season = MagicMock(return_value=SimpleNamespace(episodes=[_episode(101, 1, 1, 7.1), _episode(102, 1, 2, 7.2)]))

    assert t.get_episode_by_id(500, 102).vote_average == 7.2
    assert t.cache.update_tmdb_episode.call_count == 2


def test_get_episode_by_id_uses_warm_persistent_cache(monkeypatch):
    t = _bare_tmdb(monkeypatch)
    t.language = "en"
    t.expiration = 30
    t._episode_id_maps = {}
    t._complete_episode_id_maps = set()
    t.cache = MagicMock()
    t.cache.query_tmdb_episode_by_id.return_value = (
        {
            "tmdb_id": 500,
            "season_number": 1,
            "episode_number": 28,
            "episode_id": 201,
            "title": "Cached Episode",
            "air_date": None,
            "overview": "",
            "still_url": "",
            "vote_count": 10,
            "vote_average": 8.1,
            "imdb_id": "",
            "tvdb_id": None,
        },
        False,
    )
    t.get_show = MagicMock()
    t.get_season = MagicMock()

    assert t.get_episode_by_id(500, 201).vote_average == 8.1
    t.get_show.assert_not_called()
    t.get_season.assert_not_called()


def test_get_episode_by_id_rejects_warm_cache_entry_from_another_show(monkeypatch):
    t = _bare_tmdb(monkeypatch)
    t.language = "en"
    t.expiration = 30
    t._episode_id_maps = {}
    t._complete_episode_id_maps = set()
    t.cache = MagicMock()
    t.cache.query_tmdb_episode_by_id.return_value = (
        {
            "tmdb_id": 999,
            "season_number": 1,
            "episode_number": 1,
            "episode_id": 201,
            "title": "Wrong Show",
            "air_date": None,
            "overview": "",
            "still_url": "",
            "vote_count": 10,
            "vote_average": 9.9,
            "imdb_id": "",
            "tvdb_id": None,
        },
        False,
    )
    t.get_show = MagicMock(return_value=SimpleNamespace(seasons=[SimpleNamespace(season_number=1)]))
    t.get_season = MagicMock(return_value=SimpleNamespace(episodes=[_episode(101, 1, 1, 7.1)]))

    with pytest.raises(Failed, match="TMDb Episode ID 201"):
        t.get_episode_by_id(500, 201)
    t.get_show.assert_called_once_with(500)


def test_get_episode_by_id_reports_unmatched_guid(monkeypatch):
    t = _bare_tmdb(monkeypatch)
    t.language = "en"
    t.cache = None
    t._episode_id_maps = {}
    t._complete_episode_id_maps = set()
    t.get_show = MagicMock(return_value=SimpleNamespace(seasons=[SimpleNamespace(season_number=1)]))
    t.get_season = MagicMock(return_value=SimpleNamespace(episodes=[_episode(101, 1, 1, 7.1)]))

    with pytest.raises(Failed, match="TMDb Episode ID 999"):
        t.get_episode_by_id(500, 999)


def test_get_episode_by_id_normalizes_show_retry_error(monkeypatch):
    t = _bare_tmdb(monkeypatch)
    t.language = "en"
    t.cache = None
    t._episode_id_maps = {}
    t._complete_episode_id_maps = set()
    t.get_show = MagicMock(side_effect=RetryError(MagicMock()))

    with pytest.raises(Failed, match="Failed to build Episode ID map for TMDb ID 500"):
        t.get_episode_by_id(500, 101)


def test_get_episode_by_id_normalizes_season_tmdb_exception(monkeypatch):
    t = _bare_tmdb(monkeypatch)
    t.language = "en"
    t.cache = None
    t._episode_id_maps = {}
    t._complete_episode_id_maps = set()
    t.get_show = MagicMock(return_value=SimpleNamespace(seasons=[SimpleNamespace(season_number=1)]))
    t.get_season = MagicMock(side_effect=tmdb.TMDbException("network failure"))

    with pytest.raises(Failed, match="TMDb ID 500 Season 1"):
        t.get_episode_by_id(500, 101)


# ═══════════════════════════════════════════════════════════════════════
# Data classes
# ═══════════════════════════════════════════════════════════════════════


class TestTMDbCountry:
    def test_from_string(self):
        c = tmdb.TMDbCountry("US:United States")
        assert c.iso_3166_1 == "US"
        assert c.name == "United States"

    def test_from_object(self):
        obj = SimpleNamespace(iso_3166_1="GB", name="United Kingdom")
        c = tmdb.TMDbCountry(obj)
        assert c.iso_3166_1 == "GB"
        assert c.name == "United Kingdom"

    def test_repr(self):
        assert repr(tmdb.TMDbCountry("FR:France")) == "FR:France"


class TestTMDbSeason:
    def test_from_string(self):
        s = tmdb.TMDbSeason("1%:%Season 1%:%7.5")
        assert s.season_number == 1
        assert s.name == "Season 1"
        assert s.average == 7.5

    def test_from_object(self):
        obj = SimpleNamespace(season_number=2, name="Season 2", vote_average=8.0)
        s = tmdb.TMDbSeason(obj)
        assert s.season_number == 2
        assert s.name == "Season 2"
        assert s.average == 8.0

    def test_repr(self):
        assert repr(tmdb.TMDbSeason("1%:%S1%:%9.0")) == "1%:%S1%:%9.0"


class TestTMDBObj:
    def test_load_from_dict(self):
        obj = tmdb.TMDBObj.__new__(tmdb.TMDBObj)
        obj._load(
            {
                "title": "Test",
                "tagline": "Tag",
                "overview": "Desc",
                "imdb_id": "tt123",
                "release_date": "2023-06-15",
                "vote_average": 7.5,
                "vote_count": 100,
                "poster_url": "/p.jpg",
                "backdrop_url": "/b.jpg",
                "language_iso": "en",
                "language_name": "English",
                "genres": "Action|Drama",
                "keywords": "violence|crime",
            }
        )
        assert obj.title == "Test"
        assert obj.genres == ["Action", "Drama"]
        assert obj.keywords == ["violence", "crime"]

    def test_validate_tmdb_returns_id(self, monkeypatch):
        t = _bare_tmdb(monkeypatch)
        t.get_movie = MagicMock(return_value=SimpleNamespace(id=550))
        assert t.validate_tmdb(550, "tmdb_movie") == 550

    def test_validate_tmdb_ids_raises_notfound_when_all_missing(self, monkeypatch):
        t = _bare_tmdb(monkeypatch)
        t.validate_tmdb = MagicMock(side_effect=tmdb.NotFound("gone"))
        with pytest.raises(tmdb.NotFound):
            t.validate_tmdb_ids("99999", "tmdb_movie")
