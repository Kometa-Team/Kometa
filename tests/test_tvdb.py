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


def _make_tvdb_empty_body():
    """TVDb whose requests.get returns a 200 with an empty body (parses to lxml 'Document is empty')."""
    fake_response = SimpleNamespace(status_code=200, reason="OK", content=b"")
    fake_requests = SimpleNamespace(get=lambda url, language=None: fake_response)
    return tvdb.TVDb(requests=fake_requests, cache=None, tvdb_language="eng", expiration=60)


def test_empty_body_raises_unavailable(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda _: None)
    t = _make_tvdb_empty_body()
    with pytest.raises(tvdb.Unavailable):
        t.get_request("https://www.thetvdb.com/dereferrer/series/81189")


def test_empty_body_retries_are_trimmed(monkeypatch):
    """The empty-document retry loop should stop at 3 attempts, not the old 6."""
    monkeypatch.setattr("time.sleep", lambda _: None)
    calls = {"n": 0}

    def counting_get(url, language=None):
        calls["n"] += 1
        return SimpleNamespace(status_code=200, reason="OK", content=b"")

    t = tvdb.TVDb(requests=SimpleNamespace(get=counting_get), cache=None, tvdb_language="eng", expiration=60)
    with pytest.raises(tvdb.Unavailable):
        t.get_request("https://www.thetvdb.com/dereferrer/series/81189")
    assert calls["n"] == 3


def test_circuit_breaker_trips_and_fails_fast(monkeypatch):
    """After TVDB_DEGRADED_THRESHOLD exhausted loops, further lookups fail fast without any network call."""
    monkeypatch.setattr("time.sleep", lambda _: None)
    calls = {"n": 0}

    def counting_get(url, language=None):
        calls["n"] += 1
        return SimpleNamespace(status_code=200, reason="OK", content=b"")

    t = tvdb.TVDb(requests=SimpleNamespace(get=counting_get), cache=None, tvdb_language="eng", expiration=60)

    # Drive exactly THRESHOLD exhausted retry loops to trip the breaker.
    for _ in range(tvdb.TVDB_DEGRADED_THRESHOLD):
        with pytest.raises(tvdb.Unavailable):
            t.get_request("https://www.thetvdb.com/dereferrer/series/81189")
    assert t._degraded is True

    calls_before = calls["n"]
    # Next call should short-circuit: Unavailable raised before requests.get is ever invoked.
    with pytest.raises(tvdb.Unavailable):
        t.get_request("https://www.thetvdb.com/dereferrer/series/99999")
    assert calls["n"] == calls_before  # no additional network calls
