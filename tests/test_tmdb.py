from types import SimpleNamespace

import pytest
from tmdbapis import NotFound as TMDbApiNotFound

from modules import tmdb
from modules.util import Failed


class FakeLogger:
    """No-op logger so validate_tmdb_ids' debug/error calls don't blow up."""

    def __getattr__(self, name):
        return lambda *args, **kwargs: None


def _bare_tmdb(monkeypatch):
    # Bypass __init__ (which needs a real API key / TMDbAPIs session) and just
    # exercise the validation helpers in isolation.
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
