"""Tests for modules/cache.py — the SQLite caching layer.

The Cache class uses real SQLite databases (no mocking the DB layer).
Every test creates an isolated cache file via tmp_path so there's zero
cross-test contamination.
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

from modules.cache import Cache
from tests.conftest import FakeLogger

# ═══════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════


def make_cache(tmp_path: pytest.TempPathFactory, expiration: int = 30) -> Cache:
    """Build a Cache backed by an isolated SQLite file in tmp_path."""
    import modules.util as util
    from modules import cache as cache_module

    cache_module.logger = FakeLogger()
    util.logger = FakeLogger()
    return Cache(config_path=str(tmp_path / "config.yml"), expiration=expiration)


def table_exists(cache: Cache, table_name: str) -> bool:
    with sqlite3.connect(cache.cache_path) as conn:
        with closing(conn.cursor()) as cur:
            cur.execute(
                "SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,),
            )
            return cur.fetchone()[0] > 0


# ═══════════════════════════════════════════════════════════════════════
# Init
# ═══════════════════════════════════════════════════════════════════════


class TestInit:
    def test_creates_cache_file(self, tmp_path):
        cache = make_cache(tmp_path)
        assert os.path.exists(cache.cache_path)

    def test_creates_expected_tables(self, tmp_path):
        cache = make_cache(tmp_path)
        for table in [
            "guids_map",
            "imdb_to_tmdb_map",
            "letterboxd_map",
            "mojo_map",
            "omdb_data3",
            "mdb_data5",
            "anidb_data4",
            "anime_map",
            "mal_data4",
            "tmdb_movie_data2",
            "tmdb_show_data4",
            "image_maps",
            "radarr_adds",
            "sonarr_adds",
            "list_cache",
            "list_ids",
            "imdb_keywords",
            "imdb_parental",
            "ergast_race",
            "overlay_special_text2",
            "testing",
            "letterboxd_incremental_state",
        ]:
            assert table_exists(cache, table), f"Table {table} not created"

    def test_drops_old_table_names(self, tmp_path):
        cache = make_cache(tmp_path)
        for old_table in ["imdb_map", "mdb_data", "omdb_data", "tvdb_data", "anidb_data", "mal_data", "tmdb_movie_data", "tmdb_show_data"]:
            assert not table_exists(cache, old_table), f"Old table {old_table} not dropped"

    def test_cache_path_derived_from_config(self, tmp_path):
        cache = make_cache(tmp_path)
        assert cache.cache_path == os.path.join(str(tmp_path), "config.cache")

    def test_expiration_stored(self, tmp_path):
        cache = make_cache(tmp_path, expiration=90)
        assert cache.expiration == 90


# ═══════════════════════════════════════════════════════════════════════
# _query_map / _update_map (core internals)
# ═══════════════════════════════════════════════════════════════════════


class TestQueryMap:
    def test_update_then_query_round_trip(self, tmp_path):
        cache = make_cache(tmp_path)
        cache._update_map("letterboxd_map", "letterboxd_id", "lb-1", "tmdb_id", "12345", expired=False)
        result, expired = cache._query_map("letterboxd_map", "lb-1", "letterboxd_id", "tmdb_id")
        assert result == 12345
        assert expired is False

    def test_query_missing_key_returns_none(self, tmp_path):
        cache = make_cache(tmp_path)
        result, expired = cache._query_map("letterboxd_map", "does-not-exist", "letterboxd_id", "tmdb_id")
        assert result is None
        assert expired is None

    def test_expired_entry(self, tmp_path):
        cache = make_cache(tmp_path, expiration=30)
        long_ago = (datetime.now() - timedelta(days=999)).strftime("%Y-%m-%d")
        with sqlite3.connect(cache.cache_path) as conn:
            conn.execute("INSERT OR IGNORE INTO letterboxd_map(letterboxd_id) VALUES(?)", ("stale-id",))
            conn.execute(
                "UPDATE letterboxd_map SET tmdb_id = ?, expiration_date = ? WHERE letterboxd_id = ?",
                ("99999", long_ago, "stale-id"),
            )
        result, expired = cache._query_map("letterboxd_map", "stale-id", "letterboxd_id", "tmdb_id")
        assert result == 99999
        assert expired is True

    def test_numeric_id_conversion(self, tmp_path):
        cache = make_cache(tmp_path)
        cache._update_map("letterboxd_map", "letterboxd_id", "lb-2", "tmdb_id", "42", expired=False)
        result, _ = cache._query_map("letterboxd_map", "lb-2", "letterboxd_id", "tmdb_id")
        assert result == 42
        assert isinstance(result, int)

    def test_string_id_preserved_when_contains_underscore(self, tmp_path):
        cache = make_cache(tmp_path)
        cache._update_map("letterboxd_map", "letterboxd_id", "lb-3", "tmdb_id", "tvdb_season:123_1", expired=False)
        result, _ = cache._query_map("letterboxd_map", "lb-3", "letterboxd_id", "tmdb_id")
        assert isinstance(result, str)
        assert "_" in result

    def test_query_with_media_type(self, tmp_path):
        cache = make_cache(tmp_path)
        cache._update_map("imdb_to_tmdb_map", "imdb_id", "imdb-1", "tmdb_id", "777", expired=False, media_type="movie")
        result, expired = cache._query_map("imdb_to_tmdb_map", "imdb-1", "imdb_id", "tmdb_id", media_type="movie")
        assert result == 777
        assert expired is False


# ═══════════════════════════════════════════════════════════════════════
# Public map methods
# ═══════════════════════════════════════════════════════════════════════


class TestLetterboxdMap:
    def test_round_trip(self, tmp_path):
        cache = make_cache(tmp_path)
        cache.update_letterboxd_map(False, "lb-film", 9001)
        result, expired = cache.query_letterboxd_map("lb-film")
        assert result == 9001
        assert expired is False

    def test_missing(self, tmp_path):
        cache = make_cache(tmp_path)
        result, expired = cache.query_letterboxd_map("does-not-exist")
        assert result is None
        assert expired is None


class TestImdbToTmdbMap:
    def test_round_trip(self, tmp_path):
        cache = make_cache(tmp_path)
        cache.update_imdb_to_tmdb_map("movie", False, "tt123", "456")
        result, expired = cache.query_imdb_to_tmdb_map("tt123", imdb=True)
        assert result == 456
        assert expired is False

    def test_missing(self, tmp_path):
        cache = make_cache(tmp_path)
        result, expired = cache.query_imdb_to_tmdb_map("tt999", imdb=True)
        assert result is None
        assert expired is None

    def test_reverse_lookup_tmdb_to_imdb(self, tmp_path):
        cache = make_cache(tmp_path)
        cache.update_imdb_to_tmdb_map("movie", False, "tt456", "789")
        result, expired = cache.query_imdb_to_tmdb_map("789", imdb=False)
        assert result == "tt456"
        assert expired is False


class TestGuidMap:
    def test_round_trip(self, tmp_path):
        cache = make_cache(tmp_path)
        cache.update_guid_map("plex://movie/abc123", "550", "tt999", False, "movie")
        t_id, imdb_id, media_type, expired = cache.query_guid_map("plex://movie/abc123")
        assert t_id == [550]
        assert imdb_id == ["tt999"]
        assert media_type == "movie"
        assert expired is False

    def test_missing(self, tmp_path):
        cache = make_cache(tmp_path)
        t_id, imdb_id, media_type, expired = cache.query_guid_map("plex://movie/does-not-exist")
        assert t_id is None
        assert imdb_id is None
        assert media_type is None
        assert expired is None

    def test_multiple_t_ids(self, tmp_path):
        cache = make_cache(tmp_path)
        cache.update_guid_map("plex://show/xyz", "101, 102", "tt001", False, "show")
        t_id, _, _, _ = cache.query_guid_map("plex://show/xyz")
        assert t_id == [101, 102]

    def test_update_overwrites(self, tmp_path):
        cache = make_cache(tmp_path)
        cache.update_guid_map("plex://movie/abc123", "550", "tt999", False, "movie")
        cache.update_guid_map("plex://movie/abc123", "551", "tt888", False, "movie")
        t_id, imdb_id, _, _ = cache.query_guid_map("plex://movie/abc123")
        assert t_id == [551]
        assert imdb_id == ["tt888"]


class TestMojoMap:
    def test_round_trip(self, tmp_path):
        cache = make_cache(tmp_path)
        cache.update_mojo_map(False, "https://mojo.com/film/123", "tt99999")
        result, expired = cache.query_mojo_map("https://mojo.com/film/123")
        assert result == "tt99999"
        assert expired is False


# ═══════════════════════════════════════════════════════════════════════
# Data caching (uses SimpleNamespace for structured objects)
# ═══════════════════════════════════════════════════════════════════════


def _make_mdb_obj(**overrides):
    defaults = {
        "title": "Test Movie",
        "year": 2023,
        "released": datetime(2023, 6, 1),
        "released_digital": None,
        "type": "movie",
        "imdbid": "tt123",
        "traktid": "1",
        "tmdbid": "550",
        "score": 8,
        "average": 7.5,
        "imdb_rating": 8.0,
        "metacritic_rating": 75,
        "metacriticuser_rating": None,
        "trakt_rating": None,
        "tomatoes_rating": None,
        "tomatoesaudience_rating": None,
        "tmdb_rating": None,
        "letterboxd_rating": None,
        "myanimelist_rating": None,
        "content_rating": "PG-13",
        "commonsense": None,
        "age_rating": None,
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


class TestMdbCache:
    def test_round_trip(self, tmp_path):
        cache = make_cache(tmp_path)
        mdb_obj = _make_mdb_obj()
        cache.update_mdb(False, "mdb-key-1", mdb_obj, expiration=30)
        result, expired = cache.query_mdb("mdb-key-1", expiration=30)
        assert result["title"] == "Test Movie"
        assert result["year"] == 2023
        assert expired is False

    def test_missing(self, tmp_path):
        cache = make_cache(tmp_path)
        result, expired = cache.query_mdb("no-such-key", expiration=30)
        assert result == {}
        assert expired is None


def _make_anidb_obj(**overrides):
    defaults = {
        "main_title": "Fullmetal Alchemist",
        "titles": ["FMA", "Hagane no"],
        "studio": "Bones",
        "rating": 8.5,
        "average": 8.0,
        "score": 9,
        "released": datetime(2003, 10, 4),
        "tags": ["action", "fantasy"],
        "mal_id": "123",
        "imdb_id": "tt1355642",
        "tmdb_id": "46298",
        "tmdb_type": "tv",
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


class TestAnidbCache:
    def test_round_trip(self, tmp_path):
        cache = make_cache(tmp_path)
        anidb_obj = _make_anidb_obj()
        cache.update_anidb(False, 12345, anidb_obj, expiration=30)
        result, expired = cache.query_anidb(12345, expiration=30)
        assert result["main_title"] == "Fullmetal Alchemist"
        assert expired is False

    def test_missing(self, tmp_path):
        cache = make_cache(tmp_path)
        result, expired = cache.query_anidb(99999, expiration=30)
        assert result == {}
        assert expired is None


def _make_mal_obj(**overrides):
    defaults = {
        "title": "Attack on Titan",
        "title_english": None,
        "title_japanese": None,
        "status": "finished_airing",
        "airing": False,
        "aired": datetime(2013, 4, 7),
        "rating": "R",
        "score": 8.5,
        "rank": 1,
        "popularity": 1,
        "genres": ["Action"],
        "explicit_genres": [],
        "themes": [],
        "demographics": [],
        "studio": "WIT Studio",
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


class TestMalCache:
    def test_round_trip(self, tmp_path):
        cache = make_cache(tmp_path)
        mal_obj = _make_mal_obj()
        cache.update_mal(False, 54321, mal_obj, expiration=30)
        result, expired = cache.query_mal(54321, expiration=30)
        assert result["title"] == "Attack on Titan"
        assert expired is False


class TestImdbKeywords:
    def test_round_trip(self, tmp_path):
        cache = make_cache(tmp_path)
        keywords = {"violence": (100, 200), "gore": (50, 150)}
        cache.update_imdb_keywords(False, "tt999", keywords, expiration=30)
        result, expired = cache.query_imdb_keywords("tt999", expiration=30)
        assert result == {"violence": (100, 200), "gore": (50, 150)}
        assert expired is False

    def test_missing(self, tmp_path):
        cache = make_cache(tmp_path)
        result, expired = cache.query_imdb_keywords("tt000", expiration=30)
        assert result == {}
        assert expired is None


class TestImdbParental:
    def test_round_trip(self, tmp_path):
        cache = make_cache(tmp_path)
        parental = {"Nudity": "None", "Violence": "Moderate", "Profanity": "Mild", "Alcohol": "None", "Frightening": "Mild"}
        cache.update_imdb_parental(False, "tt888", parental, expiration=30)
        result, expired = cache.query_imdb_parental("tt888", expiration=30)
        assert result["Violence"] == "Moderate"
        assert result["Profanity"] == "Mild"
        assert expired is False


# ═══════════════════════════════════════════════════════════════════════
# List cache / list IDs
# ═══════════════════════════════════════════════════════════════════════


class TestListCache:
    def test_round_trip(self, tmp_path):
        cache = make_cache(tmp_path)
        key = cache.update_list_cache("trakt_list", "https://trakt.tv/list/1", False, expiration=30)
        assert key is not None
        result_key, expired = cache.query_list_cache("trakt_list", "https://trakt.tv/list/1", expiration=30)
        assert result_key == key
        assert expired is False

    def test_missing(self, tmp_path):
        cache = make_cache(tmp_path)
        result_key, expired = cache.query_list_cache("nonexistent", "data", 30)
        assert result_key is None
        assert expired is None


class TestListIds:
    def test_round_trip(self, tmp_path):
        cache = make_cache(tmp_path)
        key = cache.update_list_cache("test", "data", False, 30)
        cache.update_list_ids(key, [("101", "tmdb"), ("102", "tmdb")])
        result = cache.query_list_ids(key)
        assert result == [("101", "tmdb"), ("102", "tmdb")]

    def test_missing(self, tmp_path):
        cache = make_cache(tmp_path)
        assert cache.query_list_ids(999) == []

    def test_delete(self, tmp_path):
        cache = make_cache(tmp_path)
        key = cache.update_list_cache("test", "data2", False, 30)
        cache.update_list_ids(key, [(201, "tvdb")])
        cache.delete_list_ids(key)
        assert cache.query_list_ids(key) == []


# ═══════════════════════════════════════════════════════════════════════
# Image map methods
# ═══════════════════════════════════════════════════════════════════════


class TestImageMap:
    def test_get_table_name(self, tmp_path):
        cache = make_cache(tmp_path)
        table_name = cache.get_image_table_name("Movies")
        assert table_name is not None
        assert table_name.startswith("image_map_")
        assert table_exists(cache, table_name)

    def test_round_trip(self, tmp_path):
        cache = make_cache(tmp_path)
        table = cache.get_image_table_name("Movies")
        cache.update_image_map("rk-101", table, "/path/to/poster.jpg", "abc123")
        location, compare, overlay = cache.query_image_map("rk-101", table)
        assert location == "/path/to/poster.jpg"
        assert compare == "abc123"
        assert overlay == ""

    def test_missing(self, tmp_path):
        cache = make_cache(tmp_path)
        table = cache.get_image_table_name("Movies")
        location, compare, overlay = cache.query_image_map("rk-999", table)
        assert location is None
        assert compare is None
        assert overlay is None

    def test_multiple_libraries_different_tables(self, tmp_path):
        cache = make_cache(tmp_path)
        movies_table = cache.get_image_table_name("Movies")
        shows_table = cache.get_image_table_name("TV Shows")
        assert movies_table != shows_table

    def test_update_overwrite(self, tmp_path):
        cache = make_cache(tmp_path)
        table = cache.get_image_table_name("Movies")
        cache.update_image_map("rk-201", table, "/old/path.jpg", "old-hash")
        cache.update_image_map("rk-201", table, "/new/path.jpg", "new-hash")
        location, compare, _ = cache.query_image_map("rk-201", table)
        assert location == "/new/path.jpg"
        assert compare == "new-hash"


# ═══════════════════════════════════════════════════════════════════════
# Arr add-tracking methods
# ═══════════════════════════════════════════════════════════════════════


class TestArrAdds:
    def test_radarr_add_then_query(self, tmp_path):
        cache = make_cache(tmp_path)
        cache.update_radarr_adds(550, "Movies")
        assert cache.query_radarr_adds(550, "Movies") == 550

    def test_radarr_missing(self, tmp_path):
        cache = make_cache(tmp_path)
        assert cache.query_radarr_adds(999, "Movies") is None

    def test_sonarr_add_then_query(self, tmp_path):
        cache = make_cache(tmp_path)
        cache.update_sonarr_adds(368207, "TV")
        assert cache.query_sonarr_adds(368207, "TV") == 368207

    def test_radarr_library_scoped(self, tmp_path):
        cache = make_cache(tmp_path)
        cache.update_radarr_adds(550, "Movies")
        assert cache.query_radarr_adds(550, "Movies") == 550
        assert cache.query_radarr_adds(550, "Different Library") is None


# ═══════════════════════════════════════════════════════════════════════
# Letterboxd incremental state
# ═══════════════════════════════════════════════════════════════════════


class TestLetterboxdIncrementalState:
    def test_set_and_query(self, tmp_path):
        cache = make_cache(tmp_path)
        cache.update_letterboxd_incremental_state("user1", "reviews", "2026-06-01", [101, 102])
        timestamp, ids = cache.query_letterboxd_incremental_state("user1", "reviews")
        assert timestamp == "2026-06-01"
        assert ids == [101, 102]

    def test_missing_returns_defaults(self, tmp_path):
        cache = make_cache(tmp_path)
        timestamp, ids = cache.query_letterboxd_incremental_state("nobody", "reviews")
        assert timestamp is None
        assert ids == []

    def test_update_overwrites(self, tmp_path):
        cache = make_cache(tmp_path)
        cache.update_letterboxd_incremental_state("user2", "films", "2026-01-01", [1])
        cache.update_letterboxd_incremental_state("user2", "films", "2026-06-15", [2, 3])
        timestamp, ids = cache.query_letterboxd_incremental_state("user2", "films")
        assert timestamp == "2026-06-15"
        assert ids == [2, 3]


# ═══════════════════════════════════════════════════════════════════════
# Overlay special text
# ═══════════════════════════════════════════════════════════════════════


class TestOverlaySpecialText:
    def test_round_trip(self, tmp_path):
        cache = make_cache(tmp_path)
        cache.update_overlay_special_text("rk-101", "rating", "PG-13")
        result = cache.query_overlay_special_text("rk-101")
        assert result == {"rating": "PG-13"}

    def test_multiple_types(self, tmp_path):
        cache = make_cache(tmp_path)
        cache.update_overlay_special_text("rk-101", "rating", "R")
        cache.update_overlay_special_text("rk-101", "audio", "5.1")
        result = cache.query_overlay_special_text("rk-101")
        assert result == {"rating": "R", "audio": "5.1"}

    def test_missing(self, tmp_path):
        cache = make_cache(tmp_path)
        result = cache.query_overlay_special_text("rk-999")
        assert result == {}

    def test_update_overwrite(self, tmp_path):
        cache = make_cache(tmp_path)
        cache.update_overlay_special_text("rk-101", "rating", "R")
        cache.update_overlay_special_text("rk-101", "rating", "NC-17")
        result = cache.query_overlay_special_text("rk-101")
        assert result == {"rating": "NC-17"}


# ═══════════════════════════════════════════════════════════════════════
# Ergast (F1 race data)
# ═══════════════════════════════════════════════════════════════════════


def _make_race(season: int, round_num: int, name: str, date: datetime | None = None):
    return SimpleNamespace(season=season, round=round_num, name=name, date=date or datetime(season, 3, 1))


class TestErgast:
    def test_round_trip(self, tmp_path):
        cache = make_cache(tmp_path)
        races = [_make_race(2025, 1, "Bahrain"), _make_race(2025, 2, "Jeddah")]
        cache.update_ergast(False, 2025, races, expiration=30)
        result, expired = cache.query_ergast(2025, expiration=30)
        assert len(result) == 2
        assert result[0]["raceName"] == "Bahrain"
        assert expired is False

    def test_missing(self, tmp_path):
        cache = make_cache(tmp_path)
        result, expired = cache.query_ergast(1999, expiration=30)
        assert result == []
        assert expired is None


# ═══════════════════════════════════════════════════════════════════════
# Testing data (used by the --test CLI)
# ═══════════════════════════════════════════════════════════════════════


class TestTesting:
    def test_round_trip(self, tmp_path):
        cache = make_cache(tmp_path)
        cache.update_testing("test-1", "value_a", "value_b", "True")
        val1, val2, success = cache.query_testing("test-1")
        assert val1 == "value_a"
        assert val2 == "value_b"
        assert success is True

    def test_missing(self, tmp_path):
        cache = make_cache(tmp_path)
        val1, val2, success = cache.query_testing("no-such-test")
        assert val1 is None
        assert val2 is None
        assert success is None


# ═══════════════════════════════════════════════════════════════════════
# Edge cases
# ═══════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    def test_empty_cache_operations_dont_crash(self, tmp_path):
        cache = make_cache(tmp_path)
        assert cache.query_letterboxd_map("x") == (None, None)
        assert cache.query_omdb("tt000", 30) == ({}, None)
        assert cache.query_list_ids(999) == []
        assert cache.query_radarr_adds(999, "Movies") is None

    def test_update_same_key_twice(self, tmp_path):
        cache = make_cache(tmp_path)
        cache.update_letterboxd_map(False, "dup", 1)
        cache.update_letterboxd_map(False, "dup", 1)
        result, _ = cache.query_letterboxd_map("dup")
        assert result == 1

    def test_long_plex_guid(self, tmp_path):
        cache = make_cache(tmp_path)
        long_guid = "plex://movie/5d7768244de0ee001fcc7ff05d7768244de0ee001fcc7ff0"
        cache.update_guid_map(long_guid, "550", "tt999", False, "movie")
        t_id, imdb_id, _, _ = cache.query_guid_map(long_guid)
        assert t_id == [550]
        assert imdb_id == ["tt999"]

    def test_special_chars_in_ids(self, tmp_path):
        cache = make_cache(tmp_path)
        for special_id in ["tvdb:123_45", "anilist-6789", "mal:9999"]:
            cache.update_letterboxd_map(False, special_id, 42)
            result, _ = cache.query_letterboxd_map(special_id)
            assert result == 42, f"Failed for ID: {special_id}"

    def test_omdb_cache(self, tmp_path):
        """OMDb methods use column-based storage, not JSON."""
        omdb_obj = SimpleNamespace(
            imdb_id="tt123",
            title="Test",
            year=2023,
            released=datetime(2023, 6, 15),
            content_rating="R",
            genres_str="Drama",
            imdb_rating=7.5,
            imdb_votes="10000",
            metacritic_rating=80,
            type="movie",
            series_id=None,
            season_num=None,
            episode_num=None,
        )
        cache = make_cache(tmp_path)
        cache.update_omdb(False, omdb_obj, expiration=30)
        result, expired = cache.query_omdb("tt123", expiration=30)
        assert result["Title"] == "Test"
        assert result["Year"] == 2023
        assert expired is False

    def test_anime_map_round_trip(self, tmp_path):
        cache = make_cache(tmp_path)
        cache.update_anime_map(False, {"anidb": 123, "anilist": 1, "myanimelist": 2, "kitsu": 3})
        result, expired = cache.query_anime_map(123, "anidb")
        assert result is not None
        assert result["anilist"] == 1
        assert result["myanimelist"] == 2
        assert expired is False

    def test_anime_map_missing(self, tmp_path):
        cache = make_cache(tmp_path)
        result, expired = cache.query_anime_map(999, "anidb")
        assert result is None
        assert expired is None
