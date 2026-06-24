import sqlite3
from unittest.mock import MagicMock

import pytest

from modules import cache as cache_module
from modules.cache import Cache


@pytest.fixture
def cache(tmp_path, monkeypatch):
    # modules.util.logger is None outside a real Kometa run; Cache.__init__ logs on startup.
    monkeypatch.setattr(cache_module, "logger", MagicMock())
    # Cache derives its db path from the config path: "<name>.cache"
    return Cache(str(tmp_path / "test.yml"), 60)


def _row_count(cache, rating_key, data_type):
    with sqlite3.connect(cache.cache_path) as connection:
        return connection.execute(
            "SELECT COUNT(*) FROM overlay_value_cache WHERE rating_key = ? AND type = ?",
            (str(rating_key), data_type),
        ).fetchone()[0]


def test_overlay_value_cache_no_duplicate_rows(cache):
    # The old overlay_special_text2 table had no UNIQUE(rating_key, type), so repeated
    # writes accumulated duplicate rows. overlay_value_cache must keep exactly one.
    for _ in range(3):
        cache.update_overlay_value_cache(False, 5173, "plex_imdb_rating", "7.3")
    value, _ = cache.query_overlay_value_cache(5173, "plex_imdb_rating")
    assert value == "7.3"
    assert _row_count(cache, 5173, "plex_imdb_rating") == 1


def test_overlay_value_cache_updates_in_place(cache):
    cache.update_overlay_value_cache(False, 5173, "plex_imdb_rating", "7.3")
    cache.update_overlay_value_cache(False, 5173, "plex_imdb_rating", "7.5")
    value, _ = cache.query_overlay_value_cache(5173, "plex_imdb_rating")
    assert value == "7.5"
    assert _row_count(cache, 5173, "plex_imdb_rating") == 1


def test_overlay_value_cache_distinct_types_coexist(cache):
    cache.update_overlay_value_cache(False, 5173, "plex_imdb_rating", "7.3")
    cache.update_overlay_value_cache(False, 5173, "mdb_tomatoes_rating", "8.1")
    assert cache.query_overlay_value_cache(5173, "plex_imdb_rating")[0] == "7.3"
    assert cache.query_overlay_value_cache(5173, "mdb_tomatoes_rating")[0] == "8.1"


def test_overlay_value_cache_miss_returns_none(cache):
    assert cache.query_overlay_value_cache(123, "missing") == (None, None)


def test_overlay_value_cache_fresh_write_not_expired(cache):
    # A fresh write stores a past date within the expiration window, so it must not read as expired.
    cache.update_overlay_value_cache(False, 5173, "plex_imdb_rating", "7.3")
    _, expired = cache.query_overlay_value_cache(5173, "plex_imdb_rating")
    assert expired is False


def test_overlay_value_cache_aged_entry_expires(cache):
    from datetime import datetime, timedelta

    cache.update_overlay_value_cache(False, 5173, "plex_imdb_rating", "7.3")
    # Age the row past the expiration window.
    stale = (datetime.now() - timedelta(days=65)).strftime("%Y-%m-%d")
    with sqlite3.connect(cache.cache_path) as connection:
        connection.execute(
            "UPDATE overlay_value_cache SET expiration_date = ? WHERE rating_key = ? AND type = ?",
            (stale, "5173", "plex_imdb_rating"),
        )
    _, expired = cache.query_overlay_value_cache(5173, "plex_imdb_rating")
    assert expired is True
