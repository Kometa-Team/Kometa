"""
Tests for Plex.fetch_overlay_value() — cache-first logic, float normalization,
source dispatch for plex_* ratings, and None/error handling.

fetch_overlay_value lives in modules/plex.py. It:
  1. Returns a cached float immediately if overlay_value_cache is warm.
  2. Falls through to a source fetch on cache miss or expiry.
  3. Casts the result to float (sources like IMDb can return strings).
  4. Writes the result to cache; does NOT write on None or non-numeric.
  5. Returns None when no rating is available.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

from modules.plex import Plex


def _make_plex(cache=None, get_ids=None, get_ratings=None):
    """Minimal Plex stub — bypasses __init__, wires only what fetch_overlay_value needs."""
    plx = Plex.__new__(Plex)
    plx.config = SimpleNamespace(Cache=cache)
    plx.is_movie = True
    plx.is_show = False
    plx._trakt_user_ratings = None
    plx.get_ids = get_ids or MagicMock(return_value=(None, None, None))
    plx.get_ratings = get_ratings or MagicMock(return_value={})
    return plx


def _item(rating_key=5173):
    return SimpleNamespace(ratingKey=rating_key, title="Test Movie", guid="plex://movie/abc")


# ── Cache-first logic ──────────────────────────────────────────────────────────


def test_returns_cached_float_when_fresh():
    # Warm cache hit — source must never be called.
    cache = MagicMock()
    cache.query_overlay_value_cache.return_value = ("7.3", False)
    fetch_spy = MagicMock(return_value={})
    plx = _make_plex(cache=cache, get_ratings=fetch_spy)

    result = plx.fetch_overlay_value(_item(), "plex_imdb_rating")

    assert result == 7.3
    assert isinstance(result, float)
    cache.query_overlay_value_cache.assert_called_once_with(5173, "plex_imdb_rating")
    cache.update_overlay_value_cache.assert_not_called()
    fetch_spy.assert_not_called()


def test_expired_cache_re_fetches():
    # Expired entry — falls through to source, returns fresh value, writes to cache.
    cache = MagicMock()
    cache.query_overlay_value_cache.return_value = ("6.0", True)  # expired
    plx = _make_plex(cache=cache, get_ratings=MagicMock(return_value={"plex_imdb": 7.5}))

    result = plx.fetch_overlay_value(_item(), "plex_imdb_rating")

    assert result == 7.5
    cache.update_overlay_value_cache.assert_called_once()


def test_cache_miss_fetches_and_writes():
    # No cached entry — fetches, writes result, returns float.
    cache = MagicMock()
    cache.query_overlay_value_cache.return_value = (None, None)
    plx = _make_plex(cache=cache, get_ratings=MagicMock(return_value={"plex_audience": 8.2}))

    result = plx.fetch_overlay_value(_item(), "plex_audience_rating")

    assert result == 8.2
    cache.update_overlay_value_cache.assert_called_once_with(False, 5173, "plex_audience_rating", 8.2)


def test_no_cache_always_fetches():
    # config.Cache is None — no cache read/write, source always consulted.
    plx = _make_plex(cache=None, get_ratings=MagicMock(return_value={"plex_imdb": 6.0}))

    result = plx.fetch_overlay_value(_item(), "plex_imdb_rating")

    assert result == 6.0


# ── Float normalization ────────────────────────────────────────────────────────


def test_string_from_source_normalized_to_float():
    # Some sources (e.g. IMDb) return a string; must be cast to float before returning/writing.
    plx = _make_plex(cache=None, get_ratings=MagicMock(return_value={"plex_imdb": "7.3"}))

    result = plx.fetch_overlay_value(_item(), "plex_imdb_rating")

    assert result == 7.3
    assert isinstance(result, float)


def test_non_numeric_string_returns_none():
    # float("N/A") raises ValueError → returns None, no cache write.
    cache = MagicMock()
    cache.query_overlay_value_cache.return_value = (None, None)
    plx = _make_plex(cache=cache, get_ratings=MagicMock(return_value={"plex_imdb": "N/A"}))

    result = plx.fetch_overlay_value(_item(), "plex_imdb_rating")

    assert result is None
    cache.update_overlay_value_cache.assert_not_called()


# ── None handling ──────────────────────────────────────────────────────────────


def test_none_from_source_returns_none_and_no_cache_write():
    # Source returns nothing for this item — must NOT poison the cache with a None entry.
    cache = MagicMock()
    cache.query_overlay_value_cache.return_value = (None, None)
    plx = _make_plex(cache=cache, get_ratings=MagicMock(return_value={}))  # KeyError → None

    result = plx.fetch_overlay_value(_item(), "plex_imdb_rating")

    assert result is None
    cache.update_overlay_value_cache.assert_not_called()


# ── plex_* variable dispatch ───────────────────────────────────────────────────


def test_plex_rating_key_stripped_correctly():
    # "plex_imdb_rating" → strip "_rating" → look up "plex_imdb" in get_ratings result.
    plx = _make_plex(cache=None, get_ratings=MagicMock(return_value={"plex_imdb": 9.1, "plex_audience": 8.0}))

    assert plx.fetch_overlay_value(_item(), "plex_imdb_rating") == 9.1
    assert plx.fetch_overlay_value(_item(), "plex_audience_rating") == 8.0


def test_plex_rating_key_not_found_returns_none():
    # Item has no entry for this plex rating type → KeyError → returns None.
    plx = _make_plex(cache=None, get_ratings=MagicMock(return_value={}))

    result = plx.fetch_overlay_value(_item(), "plex_imdb_rating")

    assert result is None
