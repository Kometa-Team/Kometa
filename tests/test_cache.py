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


def _table_exists(cache, name):
    with sqlite3.connect(cache.cache_path) as connection:
        return (
            connection.execute(
                "SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?", (name,)
            ).fetchone()[0]
            > 0
        )


def _columns(cache, table):
    with sqlite3.connect(cache.cache_path) as connection:
        return [row[1] for row in connection.execute(f"PRAGMA table_info({table})").fetchall()]


def test_get_image_table_name_creates_overlay_state_and_image_tables(cache):
    table_name = cache.get_image_table_name("TestLib")
    assert _table_exists(cache, f"{table_name}_overlay_state")
    assert _table_exists(cache, f"{table_name}_overlay_images")
    # _overlays is slim (no overlay column); _square_arts stays a poster cache (keeps overlay column).
    assert "overlay" not in _columns(cache, f"{table_name}_overlays")
    assert "overlay" in _columns(cache, f"{table_name}_square_arts")


def test_get_image_table_name_slims_legacy_overlays_table(cache):
    table_name = cache.get_image_table_name("TestLib")
    # Simulate a pre-redesign _overlays table that still has the overlay column.
    with sqlite3.connect(cache.cache_path) as connection:
        connection.execute(f"DROP TABLE {table_name}_overlays")
        connection.execute(
            f"CREATE TABLE {table_name}_overlays (key INTEGER PRIMARY KEY, rating_key TEXT UNIQUE, overlay TEXT, compare TEXT, location TEXT)"
        )
        connection.commit()
    # Re-resolving the table should drop+recreate it slim.
    cache.get_image_table_name("TestLib")
    assert "overlay" not in _columns(cache, f"{table_name}_overlays")


def test_overlay_poster_query_update(cache):
    table_name = cache.get_image_table_name("TestLib")
    poster_table = f"{table_name}_overlays"
    assert cache.query_overlay_poster(5173, poster_table) == (None, None)
    cache.update_overlay_poster(5173, poster_table, "http://thumb/1", "compareA")
    assert cache.query_overlay_poster(5173, poster_table) == ("http://thumb/1", "compareA")
    cache.update_overlay_poster(5173, poster_table, "http://thumb/2", "compareB")
    assert cache.query_overlay_poster(5173, poster_table) == ("http://thumb/2", "compareB")


def test_query_overlay_value_cache_all(cache):
    cache.update_overlay_value_cache(False, 5173, "plex_imdb_rating", "7.3")
    cache.update_overlay_value_cache(False, 5173, "mdb_tomatoes_rating", "8.1")
    cache.update_overlay_value_cache(False, 9999, "plex_imdb_rating", "5.0")
    assert cache.query_overlay_value_cache_all(5173) == {"plex_imdb_rating": "7.3", "mdb_tomatoes_rating": "8.1"}
    assert cache.query_overlay_value_cache_all(123) == {}


def test_overlay_state_insert_update_and_unique(cache):
    table_name = cache.get_image_table_name("TestLib")
    state_table = f"{table_name}_overlay_state"
    # Repeated writes for the same (rating_key, overlay_key) must update in place, not duplicate.
    for value in ["7.3", "7.5"]:
        cache.update_overlay_state(5173, "Overlay File (0) Rating1Fresh", state_table, "hashA", value)
    states = cache.query_overlay_state(5173, state_table)
    assert states["Overlay File (0) Rating1Fresh"] == ("hashA", "7.5")
    with sqlite3.connect(cache.cache_path) as connection:
        count = connection.execute(
            f"SELECT COUNT(*) FROM {state_table} WHERE rating_key='5173'"
        ).fetchone()[0]
    assert count == 1


def test_overlay_state_multiple_keys_and_null_value(cache):
    table_name = cache.get_image_table_name("TestLib")
    state_table = f"{table_name}_overlay_state"
    cache.update_overlay_state(5173, "Overlay File (0) Rating1Fresh", state_table, "hashA", "7.3")
    cache.update_overlay_state(5173, "Overlay File (0) 4K", state_table, "hashB")  # image-only, NULL value
    states = cache.query_overlay_state(5173, state_table)
    assert states["Overlay File (0) Rating1Fresh"] == ("hashA", "7.3")
    assert states["Overlay File (0) 4K"] == ("hashB", None)


def test_overlay_state_delete(cache):
    table_name = cache.get_image_table_name("TestLib")
    state_table = f"{table_name}_overlay_state"
    cache.update_overlay_state(5173, "Overlay File (0) 4K", state_table, "hashB")
    cache.delete_overlay_state(5173, state_table)
    assert cache.query_overlay_state(5173, state_table) == {}


def test_overlay_image_insert_update_query(cache):
    table_name = cache.get_image_table_name("TestLib")
    image_table = f"{table_name}_overlay_images"
    assert cache.query_overlay_image("Overlay File (0) 4K", image_table) is None
    cache.update_overlay_image("Overlay File (0) 4K", image_table, "12345")
    assert cache.query_overlay_image("Overlay File (0) 4K", image_table) == "12345"
    cache.update_overlay_image("Overlay File (0) 4K", image_table, "67890")
    assert cache.query_overlay_image("Overlay File (0) 4K", image_table) == "67890"
    with sqlite3.connect(cache.cache_path) as connection:
        count = connection.execute(f"SELECT COUNT(*) FROM {image_table}").fetchone()[0]
    assert count == 1


def test_migrate_overlay_value_cache_upgrades_and_resets(cache):
    table_name = cache.get_image_table_name("TestLib")
    # Simulate a legacy cache: recreate overlay_special_text2 (with a duplicate row, the legacy bug)
    # and a stale overlay application row that the migration must clear.
    with sqlite3.connect(cache.cache_path) as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS overlay_special_text2 (key INTEGER PRIMARY KEY, rating_key TEXT, type TEXT, text TEXT)"
        )
        connection.executemany(
            "INSERT INTO overlay_special_text2(rating_key, type, text) VALUES(?, ?, ?)",
            [
                ("5173", "plex_imdb_rating", "7.3"),
                ("5173", "plex_imdb_rating", "7.3"),
                ("5173", "mdb_tomatoes_rating", "8.1"),
            ],
        )
        connection.execute(
            f"INSERT INTO {table_name}_overlays(rating_key, compare, location) VALUES('5173', 'c', 'loc')"
        )
        connection.commit()

    cache.migrate_overlay_value_cache()

    assert cache.query_overlay_value_cache(5173, "plex_imdb_rating")[0] == "7.3"
    assert cache.query_overlay_value_cache(5173, "mdb_tomatoes_rating")[0] == "8.1"
    with sqlite3.connect(cache.cache_path) as connection:
        # legacy table dropped
        assert (
            connection.execute(
                "SELECT count(name) FROM sqlite_master WHERE type='table' AND name='overlay_special_text2'"
            ).fetchone()[0]
            == 0
        )
        # duplicate collapsed to a single row
        assert (
            connection.execute(
                "SELECT COUNT(*) FROM overlay_value_cache WHERE rating_key='5173' AND type='plex_imdb_rating'"
            ).fetchone()[0]
            == 1
        )
        # overlay application state reset
        assert connection.execute(f"SELECT COUNT(*) FROM {table_name}_overlays").fetchone()[0] == 0


def test_migrate_overlay_value_cache_noop_without_legacy_table(cache):
    # No legacy table present (fresh install): migration must be a silent no-op and not raise.
    cache.migrate_overlay_value_cache()
    with sqlite3.connect(cache.cache_path) as connection:
        assert (
            connection.execute(
                "SELECT count(name) FROM sqlite_master WHERE type='table' AND name='overlay_special_text2'"
            ).fetchone()[0]
            == 0
        )
