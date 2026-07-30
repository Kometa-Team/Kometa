"""Lightweight always-on timing instrumentation, gated by KOMETA_TIMINGS/--timings.

Design:
- A single process-wide TimingRegistry accumulates (library, collection, phase, source) -> seconds/calls/bytes.
- Kometa is single-threaded (no `threading` usage anywhere in the codebase), so no locking is needed.
- When KOMETA_TIMINGS is unset/false every entry point below is a guarded early return - near-zero overhead.
- `track()` is a context manager for scoping an arbitrary block of code.
- `timed()` is a decorator for scoping an entire method with minimal diff noise at call sites.
- `wrap_cache_methods()` instruments every query_/update_ method on modules.cache.Cache from one call site.
- `instrument_session()` instruments a requests.Session so every HTTP call it makes is timed and tagged
  by source, regardless of which library (plexapi/tmdbapis/arrapi/in-repo modules) issued the request.
"""

import csv
import json
import os
import threading
import time
from collections import defaultdict
from contextlib import contextmanager
from functools import wraps
from urllib.parse import urlparse

from modules import util

logger = util.logger


# Set by kometa.py from run_args["timings"] before any import-time reader of this flag runs; defaults False so a bare `import modules.timings` stays inert.
ENABLED = False

# Hostname substring -> source tag, first match wins; unknown hosts fall back to "other:<hostname>" so new traffic is still visible.
HOST_SOURCE_MAP = [
    ("themoviedb.org", "tmdb"),
    ("trakt.tv", "trakt"),
    ("imdb.com", "imdb"),
    ("mdblist.com", "mdblist"),
    ("omdbapi.com", "omdb"),
    ("thetvdb.com", "tvdb"),
    ("anidb.net", "anidb"),
    ("anilist.co", "anilist"),
    ("myanimelist.net", "mal"),
    ("letterboxd.com", "letterboxd"),
    ("simkl.com", "simkl"),
    ("notifiarr.com", "notifiarr"),
    ("github.com", "github"),
    ("githubusercontent.com", "github"),
    ("icheckmovies.com", "icheckmovies"),
    ("boxofficemojo.com", "mojo"),
]


def hostname_to_source(url):
    """Map a request URL to a short source tag. Plex/Radarr/Sonarr hosts are user-configured and
    can't be recognised from the hostname alone, so those are looked up in the registry, populated
    once each service connects via registry.set_plex_hostname()/register_arr_host()."""
    try:
        host = (urlparse(url).hostname or "").lower()
    except ValueError:
        host = ""
    if not host:
        return "other:unknown"
    if registry.plex_hostname and host == registry.plex_hostname:
        return "plex"
    if host in registry.arr_hosts:
        return registry.arr_hosts[host]
    for needle, source in HOST_SOURCE_MAP:
        if needle in host:
            return source
    return f"other:{host}"


def git_sha():
    # Docker mounts never include .git, so KOMETA_GIT_SHA lets the host pass its own `git rev-parse HEAD` in - checked first as the only reliable source in a container.
    env_sha = os.environ.get("KOMETA_GIT_SHA")
    if env_sha:
        return env_sha
    try:
        from git import InvalidGitRepositoryError, Repo  # noqa

        try:
            return Repo(path=".").head.commit.hexsha
        except (InvalidGitRepositoryError, ValueError, TypeError):
            return None
    except ImportError:
        return None


def _looks_like_miss(result):
    """Best-effort hit/miss detection for cache query_* methods, whose return shapes vary
    (single value, tuple of values, list, dict). None/all-None-tuple is treated as a miss;
    anything else (including an empty list/dict, which means "row existed") is a hit."""
    if result is None:
        return True
    if isinstance(result, tuple):
        return all(v is None for v in result)
    return False


class TimingRegistry:
    """Accumulates elapsed seconds/call counts/bytes into buckets keyed by
    (library, collection, phase, source). record() is lock-guarded for feat/threading's workers>1 runs; the rest is still single-threaded-only."""

    def __init__(self):
        self.enabled = ENABLED
        self._lock = threading.Lock()
        self.buckets = defaultdict(lambda: {"seconds": 0.0, "calls": 0, "bytes": 0})
        self.cache_hits = defaultdict(int)
        self.cache_misses = defaultdict(int)
        self.cache_seconds = defaultdict(float)
        self.start_time = time.perf_counter()
        self.meta = {}
        self._banner_logged = False
        # Single-threaded call-scoped tag (e.g. "image" for get_image/download_image) that instrument_session's request hook appends to the source.
        self.context_tag = None
        # Single-threaded call-scoped tag so network buckets can be split by library, not just source - set via library_context(), read in instrument_session().
        self.library_ctx = None
        # Single-threaded call-scoped tag so every bucket can be split overlay-loop vs collection-loop work - set via overlay_context(), read in record()/timed()/instrument_session().
        self.overlay_ctx = None
        # Populated once each service connects - see set_plex_hostname()/register_arr_host().
        self.plex_hostname = None
        self.arr_hosts = {}

    def reset(self):
        # Re-stamps start_time and clears the four accumulator dicts so a persistent scheduler process's next run starts from zero instead of adding to every run since the container started.
        with self._lock:
            self.start_time = time.perf_counter()
            self.buckets = defaultdict(lambda: {"seconds": 0.0, "calls": 0, "bytes": 0})
            self.cache_hits = defaultdict(int)
            self.cache_misses = defaultdict(int)
            self.cache_seconds = defaultdict(float)
            self.meta = {}
            self._banner_logged = False

    def set_plex_hostname(self, hostname):
        if hostname:
            self.plex_hostname = hostname.lower()

    def register_arr_host(self, hostname, source):
        if hostname:
            self.arr_hosts[hostname.lower()] = source

    def record(self, phase, seconds, library=None, collection=None, source=None, num_bytes=0, overlay=None):
        if not self.enabled:
            return
        if overlay is None:
            overlay = self.overlay_ctx
        with self._lock:
            bucket = self.buckets[(library, collection, phase, source, overlay)]
            bucket["seconds"] += seconds
            bucket["calls"] += 1
            bucket["bytes"] += num_bytes

    def record_cache(self, name, seconds, hit):
        if not self.enabled:
            return
        with self._lock:
            self.cache_seconds[name] += seconds
            if hit:
                self.cache_hits[name] += 1
            else:
                self.cache_misses[name] += 1
        self.record("cache", seconds, source=name)

    def banner(self):
        if not self.enabled or self._banner_logged:
            return
        self._banner_logged = True
        logger.info(f"KOMETA_TIMINGS enabled (git SHA: {git_sha() or 'unknown'})")

    def set_meta(self, **kwargs):
        self.meta.update(kwargs)

    def total_wall_time(self):
        return time.perf_counter() - self.start_time

    def top_buckets(self, n=10):
        rows = []
        for (library, collection, phase, source, overlay), data in self.buckets.items():
            rows.append((library, collection, phase, source, overlay, data["seconds"], data["calls"], data["bytes"]))
        rows.sort(key=lambda r: r[5], reverse=True)
        return rows[:n]

    def network_summary(self):
        """(source -> {seconds, calls, bytes}) rolled up across all libraries/collections/phases."""
        summary = defaultdict(lambda: {"seconds": 0.0, "calls": 0, "bytes": 0})
        for (_, _, phase, source, _), data in self.buckets.items():
            if phase != "network":
                continue
            summary[source]["seconds"] += data["seconds"]
            summary[source]["calls"] += data["calls"]
            summary[source]["bytes"] += data["bytes"]
        return summary

    def cache_hit_rates(self):
        rates = {}
        for name in set(self.cache_hits) | set(self.cache_misses):
            hits = self.cache_hits[name]
            misses = self.cache_misses[name]
            total = hits + misses
            rates[name] = {"hits": hits, "misses": misses, "hit_rate": (hits / total) if total else None, "seconds": self.cache_seconds[name]}
        return rates

    def export(self, logs_dir):
        """Write logs/timings-<timestamp>.json, .csv, and a plain-text -summary.log. Returns
        (json_path, csv_path, summary_path), or (None, None, None) if disabled. Deliberately never
        touches meta.log/logger - these are the only files instrumentation is allowed to write to,
        so a normal run's meta.log is byte-for-byte identical whether KOMETA_TIMINGS is set or not."""
        if not self.enabled:
            return None, None, None
        os.makedirs(logs_dir, exist_ok=True)
        stamp = time.strftime("%Y%m%d-%H%M%S")
        json_path = os.path.join(logs_dir, f"timings-{stamp}.json")
        csv_path = os.path.join(logs_dir, f"timings-{stamp}.csv")
        summary_path = os.path.join(logs_dir, f"timings-{stamp}-summary.log")

        buckets_out = []
        for (library, collection, phase, source, overlay), data in self.buckets.items():
            calls = data["calls"]
            buckets_out.append(
                {
                    "library": library,
                    "collection": collection,
                    "phase": phase,
                    "source": source,
                    "overlay": overlay,
                    "seconds": round(data["seconds"], 6),
                    "calls": calls,
                    "bytes": data["bytes"],
                    "mean_seconds": round(data["seconds"] / calls, 6) if calls else 0.0,
                }
            )

        payload = {
            "meta": self.meta,
            "total_wall_seconds": round(self.total_wall_time(), 3),
            "cache": self.cache_hit_rates(),
            "buckets": buckets_out,
        }
        with open(json_path, "w", encoding="utf-8") as fp:
            json.dump(payload, fp, indent=2)

        with open(csv_path, "w", newline="", encoding="utf-8") as fp:
            writer = csv.writer(fp)
            writer.writerow(["library", "collection", "phase", "source", "overlay", "seconds", "calls", "bytes", "mean_seconds"])
            for row in buckets_out:
                writer.writerow([row["library"], row["collection"], row["phase"], row["source"], row["overlay"], row["seconds"], row["calls"], row["bytes"], row["mean_seconds"]])

        with open(summary_path, "w", encoding="utf-8") as fp:
            fp.write(f"Kometa timings summary - {stamp}\n")
            for key, value in self.meta.items():
                fp.write(f"{key}: {value}\n")
            fp.write(f"total_wall_seconds: {round(self.total_wall_time(), 3)}\n")
            fp.write(f"timings_json: {json_path}\n")
            fp.write(f"timings_csv: {csv_path}\n")
            fp.write("\n")
            for line in self.summary_lines():
                fp.write(f"{line}\n")

        return json_path, csv_path, summary_path

    def summary_lines(self, top_n=10):
        """Compact human-readable summary written to the standalone timings-*-summary.log file
        (never to meta.log/logger - see export())."""
        lines = ["Timings Summary (top buckets by total time):"]
        for library, collection, phase, source, overlay, seconds, calls, num_bytes in self.top_buckets(top_n):
            tag = "overlay" if overlay else ("collection" if overlay is False else None)
            label = " / ".join(str(v) for v in (library, collection, phase, source, tag) if v)
            lines.append(f"  {label:<60} | {seconds:>8.2f}s | {calls:>6} calls")
        net = self.network_summary()
        if net:
            lines.append("Network by source:")
            for source, data in sorted(net.items(), key=lambda kv: kv[1]["seconds"], reverse=True):
                lines.append(f"  {source:<20} | {data['seconds']:>8.2f}s | {data['calls']:>6} calls | {data['bytes']:>10} bytes")
        cache = self.cache_hit_rates()
        if cache:
            lines.append("Cache hit rates:")
            for name, data in sorted(cache.items(), key=lambda kv: kv[1]["seconds"], reverse=True):
                rate = f"{data['hit_rate'] * 100:.1f}%" if data["hit_rate"] is not None else "n/a"
                lines.append(f"  {name:<25} | hits={data['hits']:>5} misses={data['misses']:>5} | hit rate={rate}")
        return lines


registry = TimingRegistry()


@contextmanager
def tag_context(tag):
    """Tags every network call made while inside this block with an extra ":tag" suffix on its
    source, e.g. get_image/download_image use tag_context("image") so overlay/asset image
    downloads are separable from a source's regular API traffic in the network summary."""
    if not registry.enabled:
        yield
        return
    previous = registry.context_tag
    registry.context_tag = tag
    try:
        yield
    finally:
        registry.context_tag = previous


@contextmanager
def library_context(name):
    """Tags every network call made while inside this block with a library name, so 'network'
    buckets support per-library breakdowns (e.g. is Plex slower to answer TV Shows than Movies
    right now?) instead of only ever showing library=None."""
    if not registry.enabled:
        yield
        return
    previous = registry.library_ctx
    registry.library_ctx = name
    try:
        yield
    finally:
        registry.library_ctx = previous


@contextmanager
def overlay_context(is_overlay):
    """Tags every bucket recorded while inside this block as overlay-loop (True) or
    collection-loop (False) work, so gather_ids/filter_and_save_items/network/etc buckets -
    shared by both call paths - can be split cleanly instead of double-counted against
    compile_overlays. Wraps compile_overlays' per-overlay-file loop in overlays.py."""
    if not registry.enabled:
        yield
        return
    previous = registry.overlay_ctx
    registry.overlay_ctx = is_overlay
    try:
        yield
    finally:
        registry.overlay_ctx = previous


@contextmanager
def track(phase, library=None, collection=None, source=None, overlay=None):
    if not registry.enabled:
        yield
        return
    start = time.perf_counter()
    try:
        yield
    finally:
        registry.record(phase, time.perf_counter() - start, library=library, collection=collection, source=source, overlay=overlay)


def timed(phase, source_arg=None):
    """Decorator form of `track` for instance methods. `source_arg` (int positional index or str
    kwarg name) optionally tags the bucket's source from one of the wrapped call's arguments -
    e.g. gather_ids(self, method, value) uses source_arg=0 to tag by data-source method name."""

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not registry.enabled:
                return func(self, *args, **kwargs)
            source = None
            if isinstance(source_arg, int) and len(args) > source_arg:
                source = args[source_arg]
            elif isinstance(source_arg, str):
                source = kwargs.get(source_arg)
            library = getattr(getattr(self, "library", None), "name", None)
            collection = getattr(self, "name", None)
            with track(phase, library=library, collection=collection, source=source):
                return func(self, *args, **kwargs)

        return wrapper

    return decorator


def wrap_cache_methods(cls, prefixes=("query_", "update_")):
    """Class decorator: wraps every query_*/update_* method on `cls` with call-count/time/hit-miss
    tracking in one place, instead of hand-instrumenting ~50 near-identical cache methods."""
    if not ENABLED:
        return cls
    for name, attr in list(vars(cls).items()):
        if not callable(attr) or not any(name.startswith(p) for p in prefixes):
            continue
        is_query = name.startswith("query_")

        @wraps(attr)
        def wrapped(self, *args, __orig=attr, __name=name, __is_query=is_query, **kwargs):
            if not registry.enabled:
                return __orig(self, *args, **kwargs)
            start = time.perf_counter()
            result = __orig(self, *args, **kwargs)
            elapsed = time.perf_counter() - start
            if __is_query:
                registry.record_cache(__name, elapsed, hit=not _looks_like_miss(result))
            else:
                registry.record("cache", elapsed, source=__name)
            return result

        setattr(cls, name, wrapped)
    return cls


def instrument_session(session):
    """Wrap session.request so every HTTP call this session makes (including calls issued
    internally by plexapi/tmdbapis/arrapi, which all share this session) is timed and tagged
    by source. Call once per session, from Requests.create_session(). No-op when disabled."""
    if not ENABLED:
        return session
    original_request = session.request

    @wraps(original_request)
    def wrapped_request(method, url, *args, **kwargs):
        start = time.perf_counter()
        response = original_request(method, url, *args, **kwargs)
        elapsed = time.perf_counter() - start
        source = hostname_to_source(url)
        if registry.context_tag:
            source = f"{source}:{registry.context_tag}"
        num_bytes = 0
        try:
            num_bytes = int(response.headers.get("Content-Length", 0) or 0)
        except (ValueError, AttributeError):
            pass
        registry.record("network", elapsed, library=registry.library_ctx, source=source, num_bytes=num_bytes, overlay=registry.overlay_ctx)
        return response

    session.request = wrapped_request
    return session
