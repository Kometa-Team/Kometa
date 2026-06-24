from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from tmdbapis import NotFound as TMDbApiNotFound

from modules import tmdb
from modules.util import Failed


def _bare_tmdb(monkeypatch):
    from tests.conftest import FakeLogger

    monkeypatch.setattr(tmdb, "logger", FakeLogger())
    return tmdb.TMDb.__new__(tmdb.TMDb)


def test_notfound_is_failed_subclass():
    # Callers that keep catching every TMDb failure as Failed must still work.
    assert issubclass(tmdb.NotFound, Failed)


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
