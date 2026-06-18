from types import SimpleNamespace

import pytest

from modules import tvdb
from modules.util import Failed


def _make_tvdb(response_status):
    """Build a TVDb instance whose underlying requests.get returns the chosen status."""
    fake_response = SimpleNamespace(
        status_code=response_status,
        reason="Mocked",
        content=b"<html></html>",
    )
    fake_requests = SimpleNamespace(get=lambda url, language=None: fake_response)
    return tvdb.TVDb(requests=fake_requests, cache=None, tvdb_language="eng", expiration=60)


def test_notfound_is_failed_subclass():
    # Callers that want to keep catching every TVDb failure as Failed should still work.
    assert issubclass(tvdb.NotFound, Failed)


def test_get_request_raises_notfound_on_4xx():
    t = _make_tvdb(404)
    with pytest.raises(tvdb.NotFound):
        t.get_request("https://www.thetvdb.com/dereferrer/series/463160")


def test_get_request_raises_failed_on_5xx(monkeypatch):
    # Suppress tenacity's wait so the 6-retry loop finishes instantly.
    monkeypatch.setattr("time.sleep", lambda _: None)
    t = _make_tvdb(503)
    with pytest.raises(Failed) as excinfo:
        t.get_request("https://www.thetvdb.com/dereferrer/series/81189")
    # Must not be the NotFound subclass — 5xx is treated as transient.
    assert not isinstance(excinfo.value, tvdb.NotFound)


def test_tvdbobj_init_propagates_notfound_for_stale_id():
    t = _make_tvdb(404)
    with pytest.raises(tvdb.NotFound) as excinfo:
        tvdb.TVDbObj(t, 463160, is_movie=False, ignore_cache=True)
    assert "463160" in str(excinfo.value)
    assert "No Series found" in str(excinfo.value)
