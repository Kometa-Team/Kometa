from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from tenacity import wait_none

from modules import tvdb
from modules.util import Failed


def _make_tvdb(response_status, content=b"<html></html>"):
    """Build a TVDb instance whose underlying requests.get returns the chosen status."""
    fake_response = SimpleNamespace(
        status_code=response_status,
        reason="Mocked",
        content=content,
    )
    fake_requests = SimpleNamespace(get=MagicMock(return_value=fake_response))
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
    assert t.requests.get.call_count == 6


def test_tvdbobj_init_propagates_notfound_for_stale_id():
    t = _make_tvdb(404)
    with pytest.raises(tvdb.NotFound) as excinfo:
        tvdb.TVDbObj(t, 463160, is_movie=False, ignore_cache=True)
    assert "463160" in str(excinfo.value)
    assert "No Series found" in str(excinfo.value)


def test_empty_response_exhaustion_includes_url_and_status(monkeypatch):
    url = "https://www.thetvdb.com/dereferrer/series/81189"
    t = _make_tvdb(202, content=b"")
    monkeypatch.setattr(tvdb.TVDb.get_request.retry, "wait", wait_none())

    with pytest.raises(tvdb.Unavailable) as excinfo:
        t.get_request(url)

    assert url in str(excinfo.value)
    assert "HTTP 202" in str(excinfo.value)
    assert "after 3 attempt(s)" in str(excinfo.value)
    assert t.requests.get.call_count == 3
    assert t._empty_response_failures == 1
    assert t._empty_response_circuit_open is False


def test_two_distinct_exhausted_empty_responses_open_circuit(monkeypatch):
    t = _make_tvdb(200, content=b"")
    monkeypatch.setattr(tvdb.TVDb.get_request.retry, "wait", wait_none())

    with pytest.raises(tvdb.Unavailable, match="empty document"):
        t.get_request("https://www.thetvdb.com/dereferrer/series/1")

    with pytest.raises(tvdb.Unavailable, match="circuit opened after 2 distinct URLs"):
        t.get_request("https://www.thetvdb.com/dereferrer/series/2")

    assert t.requests.get.call_count == 6
    assert t._empty_response_circuit_open is True

    with pytest.raises(tvdb.CircuitOpen, match="remainder of this run"):
        t.get_request("https://www.thetvdb.com/dereferrer/series/3")

    assert t.requests.get.call_count == 6


def test_exhausted_empty_url_fails_fast_when_repeated(monkeypatch):
    url = "https://www.thetvdb.com/dereferrer/series/1"
    t = _make_tvdb(200, content=b"")
    monkeypatch.setattr(tvdb.TVDb.get_request.retry, "wait", wait_none())

    with pytest.raises(tvdb.Unavailable, match="empty document"):
        t.get_request(url)
    with pytest.raises(tvdb.Unavailable, match="already exhausted"):
        t.get_request(url)

    assert t.requests.get.call_count == 3
    assert t._empty_response_failures == 1
    assert t._empty_response_circuit_open is False


def test_usable_response_resets_empty_response_streak(monkeypatch):
    t = _make_tvdb(202, content=b"")
    usable_response = SimpleNamespace(status_code=200, reason="OK", content=b"<html></html>")
    t.requests.get.side_effect = [t.requests.get.return_value] * 3 + [usable_response]
    monkeypatch.setattr(tvdb.TVDb.get_request.retry, "wait", wait_none())

    with pytest.raises(tvdb.Unavailable):
        t.get_request("https://www.thetvdb.com/dereferrer/series/1")

    t.get_request("https://www.thetvdb.com/dereferrer/series/2")

    assert t._empty_response_failures == 0
    assert t._empty_response_circuit_open is False


def test_circuit_open_propagates_from_url_lookup(monkeypatch):
    monkeypatch.setattr(tvdb, "logger", MagicMock())
    t = _make_tvdb(200)
    t._empty_response_failures = tvdb.empty_response_circuit_threshold
    t._empty_response_circuit_open = True

    with pytest.raises(tvdb.CircuitOpen):
        t.get_id_from_url("https://www.thetvdb.com/series/example")

    t.requests.get.assert_not_called()
