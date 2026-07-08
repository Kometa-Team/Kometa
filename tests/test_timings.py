"""Tests for modules/timings.py — the KOMETA_TIMINGS instrumentation layer.

This is the first test coverage request.py/cache.py get (see kometa-test-gaps.md), via the
session-hook and cache-wrapping tests below. Kept self-contained: no real network, no real
sqlite file, no real Kometa config.
"""

from __future__ import annotations

import json
import os
import time
from unittest.mock import MagicMock

import pytest

import modules.timings as timings_module
from modules.timings import TimingRegistry, hostname_to_source, tag_context, timed, track, wrap_cache_methods

# ═══════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def enabled_registry(monkeypatch):
    """A fresh, enabled TimingRegistry swapped in as the module-level singleton."""
    registry = TimingRegistry()
    registry.enabled = True
    monkeypatch.setattr(timings_module, "registry", registry)
    return registry


@pytest.fixture
def disabled_registry(monkeypatch):
    """A fresh, disabled TimingRegistry swapped in as the module-level singleton."""
    registry = TimingRegistry()
    registry.enabled = False
    monkeypatch.setattr(timings_module, "registry", registry)
    return registry


# ═══════════════════════════════════════════════════════════════════════
# Registry accumulation
# ═══════════════════════════════════════════════════════════════════════


def test_record_accumulates_seconds_and_calls(enabled_registry):
    enabled_registry.record("gather_ids", 1.5, library="Movies", collection="Marvel", source="tmdb")
    enabled_registry.record("gather_ids", 0.5, library="Movies", collection="Marvel", source="tmdb")
    bucket = enabled_registry.buckets[("Movies", "Marvel", "gather_ids", "tmdb")]
    assert bucket["seconds"] == pytest.approx(2.0)
    assert bucket["calls"] == 2


def test_record_keeps_separate_buckets_per_key(enabled_registry):
    enabled_registry.record("network", 1.0, source="tmdb")
    enabled_registry.record("network", 1.0, source="trakt")
    assert len(enabled_registry.buckets) == 2


def test_record_is_noop_when_disabled(disabled_registry):
    disabled_registry.record("gather_ids", 1.5, library="Movies")
    assert len(disabled_registry.buckets) == 0


def test_track_context_manager_records_elapsed_time(enabled_registry):
    with track("build_filter", library="TV Shows"):
        time.sleep(0.01)
    bucket = enabled_registry.buckets[("TV Shows", None, "build_filter", None)]
    assert bucket["calls"] == 1
    assert bucket["seconds"] > 0


def test_track_is_noop_when_disabled(disabled_registry):
    with track("build_filter", library="TV Shows"):
        pass
    assert len(disabled_registry.buckets) == 0


def test_timed_decorator_tags_library_and_collection_from_self(enabled_registry):
    class FakeBuilder:
        def __init__(self):
            self.library = MagicMock(name="MovieLib")
            self.library.name = "Movies"
            self.name = "Marvel Collection"

        @timed("gather_ids", source_arg=0)
        def gather_ids(self, method, value):
            return f"{method}:{value}"

    result = FakeBuilder().gather_ids("tmdb_list", "12345")
    assert result == "tmdb_list:12345"
    bucket = enabled_registry.buckets[("Movies", "Marvel Collection", "gather_ids", "tmdb_list")]
    assert bucket["calls"] == 1


def test_timed_decorator_is_noop_when_disabled(disabled_registry):
    class FakeBuilder:
        @timed("gather_ids", source_arg=0)
        def gather_ids(self, method, value):
            return "unwrapped"

    assert FakeBuilder().gather_ids("tmdb_list", "x") == "unwrapped"
    assert len(disabled_registry.buckets) == 0


# ═══════════════════════════════════════════════════════════════════════
# Cache hit/miss wrapping
# ═══════════════════════════════════════════════════════════════════════


def test_wrap_cache_methods_records_hit_and_miss(enabled_registry, monkeypatch):
    monkeypatch.setattr(timings_module, "ENABLED", True)

    class FakeCache:
        def query_thing(self, key):
            return None if key == "missing" else (key, "value")

        def update_thing(self, key, value):
            return None

    WrappedCache = wrap_cache_methods(FakeCache)
    cache = WrappedCache()

    assert cache.query_thing("present") == ("present", "value")
    assert cache.query_thing("missing") is None
    cache.update_thing("present", "value")

    rates = enabled_registry.cache_hit_rates()
    assert rates["query_thing"]["hits"] == 1
    assert rates["query_thing"]["misses"] == 1
    update_bucket = enabled_registry.buckets[(None, None, "cache", "update_thing")]
    assert update_bucket["calls"] == 1


def test_wrap_cache_methods_is_noop_when_globally_disabled(monkeypatch):
    monkeypatch.setattr(timings_module, "ENABLED", False)

    class FakeCache:
        def query_thing(self, key):
            return key

    original_method = FakeCache.query_thing
    WrappedCache = wrap_cache_methods(FakeCache)
    assert WrappedCache.query_thing is original_method


# ═══════════════════════════════════════════════════════════════════════
# Network session hook (first coverage for the request.py session pattern)
# ═══════════════════════════════════════════════════════════════════════


def test_instrument_session_wraps_request_and_tags_by_hostname(enabled_registry, monkeypatch):
    monkeypatch.setattr(timings_module, "ENABLED", True)

    fake_response = MagicMock()
    fake_response.headers = {"Content-Length": "42"}

    class FakeSession:
        def __init__(self):
            self.calls = []

        def request(self, method, url, *args, **kwargs):
            self.calls.append((method, url))
            return fake_response

    session = FakeSession()
    wrapped = timings_module.instrument_session(session)

    result = wrapped.request("GET", "https://api.themoviedb.org/3/movie/1")
    assert result is fake_response
    assert session.calls == [("GET", "https://api.themoviedb.org/3/movie/1")]

    bucket = enabled_registry.buckets[(None, None, "network", "tmdb")]
    assert bucket["calls"] == 1
    assert bucket["bytes"] == 42


def test_instrument_session_is_noop_when_globally_disabled(monkeypatch):
    monkeypatch.setattr(timings_module, "ENABLED", False)

    class FakeSession:
        def request(self, method, url, *args, **kwargs):
            return "unwrapped-response"

    session = FakeSession()
    wrapped = timings_module.instrument_session(session)
    # When disabled, instrument_session must not set an instance-level override at all -
    # "request" should still resolve through the class, not a per-instance wrapper.
    assert "request" not in wrapped.__dict__
    assert wrapped.request("GET", "https://example.com") == "unwrapped-response"


def test_tag_context_adds_suffix_to_network_source(enabled_registry, monkeypatch):
    monkeypatch.setattr(timings_module, "ENABLED", True)
    fake_response = MagicMock()
    fake_response.headers = {}

    class FakeSession:
        def request(self, method, url, *args, **kwargs):
            return fake_response

    wrapped = timings_module.instrument_session(FakeSession())
    with tag_context("image"):
        wrapped.request("GET", "https://api.themoviedb.org/3/image/1.jpg")

    assert (None, None, "network", "tmdb:image") in enabled_registry.buckets


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://api.themoviedb.org/3/movie/1", "tmdb"),
        ("https://api.trakt.tv/users/me", "trakt"),
        ("https://api.mdblist.com/lists", "mdblist"),
        ("https://unknown-host.example.com/x", "other:unknown-host.example.com"),
        ("", "other:unknown"),
    ],
)
def test_hostname_to_source_mapping(url, expected):
    assert hostname_to_source(url) == expected


def test_hostname_to_source_recognises_registered_plex_and_arr_hosts(enabled_registry):
    enabled_registry.set_plex_hostname("plex.example.com")
    enabled_registry.register_arr_host("radarr.example.com", "radarr")
    assert hostname_to_source("http://plex.example.com:32400/library") == "plex"
    assert hostname_to_source("http://radarr.example.com:7878/api") == "radarr"


# ═══════════════════════════════════════════════════════════════════════
# Export round-trip
# ═══════════════════════════════════════════════════════════════════════


def test_export_writes_json_and_csv_that_round_trip(enabled_registry, tmp_path):
    enabled_registry.record("gather_ids", 1.25, library="Movies", collection="Marvel", source="tmdb")
    enabled_registry.record("network", 0.75, source="trakt", num_bytes=100)
    enabled_registry.set_meta(kometa_version="2.4.4-build35", git_sha="abc123")

    json_path, csv_path = enabled_registry.export(str(tmp_path))

    assert os.path.exists(json_path)
    assert os.path.exists(csv_path)

    with open(json_path, encoding="utf-8") as fp:
        payload = json.load(fp)

    assert payload["meta"]["kometa_version"] == "2.4.4-build35"
    assert payload["meta"]["git_sha"] == "abc123"
    bucket_sources = {(b["phase"], b["source"]) for b in payload["buckets"]}
    assert ("gather_ids", "tmdb") in bucket_sources
    assert ("network", "trakt") in bucket_sources

    with open(csv_path, encoding="utf-8") as fp:
        csv_lines = fp.read().splitlines()
    assert csv_lines[0] == "library,collection,phase,source,seconds,calls,bytes,mean_seconds"
    assert len(csv_lines) == 1 + len(payload["buckets"])


def test_export_is_noop_when_disabled(disabled_registry, tmp_path):
    json_path, csv_path = disabled_registry.export(str(tmp_path))
    assert json_path is None
    assert csv_path is None
    assert os.listdir(tmp_path) == []


# ═══════════════════════════════════════════════════════════════════════
# Overhead sanity: disabled path costs (near) nothing
# ═══════════════════════════════════════════════════════════════════════


def test_disabled_track_overhead_is_negligible(disabled_registry):
    """Guards the <3% overhead requirement from Phase 2d: 100k no-op track() calls
    should take a small fraction of a second, not seconds."""
    start = time.perf_counter()
    for _ in range(100_000):
        with track("noop_phase"):
            pass
    elapsed = time.perf_counter() - start
    assert elapsed < 1.0
