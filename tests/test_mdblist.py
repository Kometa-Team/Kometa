"""Tests for modules/mdblist.py — MDBList API integration."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401
from modules.util import Failed, LimitReached
from tests.conftest import FakeLogger

# ═══════════════════════════════════════════════════════════════════════
# MDbObj — data parsing
# ═══════════════════════════════════════════════════════════════════════


class TestMDbObj:
    _BASE = {"title": "Test", "imdbid": "tt1", "released": None, "released_digital": None}

    def test_parses_basic_movie_data(self):
        from modules.mdblist import MDbObj

        data = {**self._BASE, "year": 2023, "score": 8}
        m = MDbObj(data)
        assert m.title == "Test"
        assert m.year == 2023
        assert m.imdbid == "tt1"
        assert m.score == 8

    def test_handles_release_year_alias(self):
        from modules.mdblist import MDbObj

        m = MDbObj({**self._BASE, "release_year": "2023"})
        assert m.year == 2023

    def test_handles_ratings_list(self):
        from modules.mdblist import MDbObj

        m = MDbObj(
            {
                **self._BASE,
                "ratings": [
                    {"source": "imdb", "value": "7.5"},
                    {"source": "metacritic", "value": "80"},
                    {"source": "tmdb", "value": "8"},
                ],
            }
        )
        assert m.imdb_rating == 7.5
        assert m.metacritic_rating == 80
        assert m.tmdb_rating == 8

    def test_handles_none_release_date(self):
        from modules.mdblist import MDbObj

        m = MDbObj({**self._BASE})
        assert m.released is None

    def test_handles_omitted_release_fields_in_batch_response(self):
        from modules.mdblist import MDbObj

        m = MDbObj({"id": 101, "imdb_id": "tt101", "title": "Batch Item"})

        assert m.released is None
        assert m.released_digital is None
        assert m.tmdbid == 101
        assert m.imdbid == "tt101"

    def test_handles_invalid_release_date(self):
        from modules.mdblist import MDbObj

        m = MDbObj({**self._BASE, "released": "not-a-date"})
        assert m.released is None

    def test_handles_valid_release_date(self):
        from datetime import datetime

        from modules.mdblist import MDbObj

        m = MDbObj({**self._BASE, "released": "2023-06-15", "released_digital": None})
        assert m.released == datetime(2023, 6, 15)


# ═══════════════════════════════════════════════════════════════════════
# MDBList
# ═══════════════════════════════════════════════════════════════════════


class TestMDBList:
    @pytest.fixture
    def adapter(self):
        from modules.mdblist import MDBList

        m = MDBList.__new__(MDBList)
        m.requests = MagicMock()
        m.cache = MagicMock()
        m.apikey = None
        m.expiration = 60
        m.limit = False
        m.supporter = False
        m.patron = False
        m.api_requests = 0
        m.api_request_count = 0
        m.rating_id_limit = 10
        m._run_cache = {}
        return m

    def test_has_key_false_initially(self, adapter):
        assert adapter.has_key is False

    def test_validate_list_rejects_invalid_url(self, adapter):
        with pytest.raises(Failed, match="must start with"):
            adapter.validate_mdblist_lists("Collection", "not-a-url")

    def test_validate_list_accepts_valid_url(self, adapter):
        result = adapter.validate_mdblist_lists(
            "Collection",
            "https://mdblist.com/lists/username/list-name/",
        )
        assert len(result) == 1
        assert result[0]["url"] == "https://mdblist.com/lists/username/list-name"

    def test_validate_list_with_limit(self, adapter):
        result = adapter.validate_mdblist_lists(
            "Collection",
            {"url": "https://mdblist.com/lists/u/l/", "limit": 50},
        )
        assert result[0]["limit"] == 50

    def test_validate_list_with_sort(self, adapter):
        result = adapter.validate_mdblist_lists(
            "Collection",
            {"url": "https://mdblist.com/lists/u/l/", "sort_by": "score"},
        )
        assert result[0]["sort_by"] == "score"

    def test_add_key_raises_on_bad_api(self, adapter, monkeypatch):
        monkeypatch.setattr("modules.mdblist.logger", FakeLogger())
        adapter._request = MagicMock(side_effect=Failed("Invalid API key"))
        with pytest.raises(Failed, match="Invalid"):
            adapter.add_key("bad-key", 30)

    def test_get_items_returns_fresh_cache_entries_without_request(self, adapter):
        adapter.cache.query_mdb.return_value = ({"title": "Cached", "released": None, "released_digital": None}, False)
        adapter._request = MagicMock()

        result = adapter.get_items("tmdb", "movie", [101])

        assert result[101].title == "Cached"
        adapter._request.assert_not_called()
        adapter.cache.update_mdb.assert_not_called()

    def test_get_items_fetches_only_missing_and_expired_entries(self, adapter):
        adapter.cache.query_mdb.side_effect = [
            ({"title": "Cached", "released": None, "released_digital": None}, False),
            ({"title": "Expired", "released": None, "released_digital": None}, True),
            ({}, None),
        ]
        adapter._request = MagicMock(
            return_value=(
                [
                    {"id": 202, "title": "Refreshed", "released": None, "released_digital": None},
                    {"id": 303, "title": "Fetched", "released": None, "released_digital": None},
                ],
                {},
            )
        )

        result = adapter.get_items("tmdb", "movie", [101, 202, 303])

        assert {media_id: item.title for media_id, item in result.items()} == {101: "Cached", 202: "Refreshed", 303: "Fetched"}
        adapter._request.assert_called_once_with("https://api.mdblist.com/tmdb/movie/", json_data={"ids": [202, 303]})
        assert [call.args[:2] for call in adapter.cache.update_mdb.call_args_list] == [(True, "tm202"), (None, "tm303")]

    def test_get_items_chunks_requests_at_one_hundred_ids(self, adapter):
        adapter.cache = None
        adapter._request = MagicMock(side_effect=[([], {}), ([], {}), ([], {})])

        adapter.get_items("tvdb", "show", range(205))

        assert [len(call.kwargs["json_data"]["ids"]) for call in adapter._request.call_args_list] == [100, 100, 5]

    def test_get_items_deduplicates_ids(self, adapter):
        adapter.cache = None
        adapter._request = MagicMock(return_value=([{"imdbid": "tt1", "title": "One", "released": None, "released_digital": None}], {}))

        result = adapter.get_items("imdb", "movie", ["tt1", "tt1"])

        assert list(result) == ["tt1"]
        adapter._request.assert_called_once_with("https://api.mdblist.com/imdb/movie/", json_data={"ids": ["tt1"]})

    @pytest.mark.parametrize(
        ("provider", "media_id", "response"),
        [
            ("imdb", "tt1", {"imdb_id": "tt1"}),
            ("tmdb", 101, {"ids": {"tmdb": 101}}),
            ("tvdb", 202, {"tvdb_id": 202}),
        ],
    )
    def test_get_items_matches_provider_id_response_variants(self, adapter, provider, media_id, response):
        adapter.cache = None
        response.update({"title": "Matched", "released": None, "released_digital": None})
        adapter._request = MagicMock(return_value=([response], {}))

        result = adapter.get_items(provider, "show" if provider == "tvdb" else "movie", [media_id])

        assert result[media_id].title == "Matched"

    def test_get_items_returns_only_items_present_in_partial_response(self, adapter, monkeypatch):
        logger = FakeLogger()
        monkeypatch.setattr("modules.mdblist.logger", logger)
        adapter.cache = None
        adapter._request = MagicMock(return_value=([{"id": 101, "title": "Found", "released": None, "released_digital": None}], {}))

        result = adapter.get_items("tmdb", "movie", [101, 202])

        assert list(result) == [101]
        assert any("1 of 2 requested tmdb IDs" in message for message in logger.warning_messages)

    def test_get_items_propagates_limit_reached_without_requesting_later_batches(self, adapter):
        adapter.cache = None
        adapter._request = MagicMock(side_effect=[([], {}), LimitReached("limit reached")])

        with pytest.raises(LimitReached, match="limit reached"):
            adapter.get_items("tmdb", "movie", range(250))

        assert adapter._request.call_count == 2

    def test_get_items_rejects_non_list_batch_response(self, adapter):
        adapter.cache = None
        adapter._request = MagicMock(return_value=({"items": []}, {}))

        with pytest.raises(Failed, match="Batch response must be a list"):
            adapter.get_items("tmdb", "movie", [101])

    def test_bulk_results_feed_single_lookups_without_persistent_cache(self, adapter):
        adapter.cache = None
        adapter._request = MagicMock(
            return_value=(
                [
                    {"id": 101, "title": "One", "released": None, "released_digital": None},
                    {"id": 202, "title": "Two", "released": None, "released_digital": None},
                ],
                {},
            )
        )

        adapter.get_items("tmdb", "movie", [101, 202])
        first = adapter.get_movie(101)
        second = adapter.get_movie(202)

        assert first.title == "One"
        assert second.title == "Two"
        adapter._request.assert_called_once_with("https://api.mdblist.com/tmdb/movie/", json_data={"ids": [101, 202]})

    def test_bulk_lookup_reuses_run_cache_without_persistent_cache(self, adapter):
        adapter.cache = None
        adapter._request = MagicMock(return_value=([{"id": 101, "title": "One", "released": None, "released_digital": None}], {}))

        adapter.get_items("tmdb", "movie", [101])
        result = adapter.get_items("tmdb", "movie", [101])

        assert result[101].title == "One"
        assert adapter._request.call_count == 1

    def test_item_alias_is_reused_from_persistent_cache_on_next_run(self, adapter, tmp_path, monkeypatch):
        from modules.cache import Cache
        from modules.mdblist import MDbObj

        monkeypatch.setattr("modules.cache.logger", FakeLogger())
        cache = Cache(config_path=str(tmp_path / "config.yml"), expiration=60)
        fallback = MDbObj({"id": "tt2", "title": "Fallback", "released": None, "released_digital": None})
        adapter.cache = cache

        adapter.cache_item_alias("tmdb", "movie", 202, fallback)

        next_run = type(adapter).__new__(type(adapter))
        next_run.cache = cache
        next_run.expiration = 60
        next_run._run_cache = {}
        next_run._request = MagicMock()
        result = next_run.get_movie(202)

        assert result.title == "Fallback"
        next_run._request.assert_not_called()

    def test_ignore_cache_bypasses_and_does_not_replace_run_cache(self, adapter, monkeypatch):
        monkeypatch.setattr("modules.mdblist.logger", FakeLogger())
        adapter.cache = None
        adapter._run_cache["tm101"] = MagicMock(title="Cached")
        adapter._request = MagicMock(return_value=({"id": 101, "title": "Fresh", "released": None, "released_digital": None}, {}))

        result = adapter.get_item("tmdb", "movie", 101, ignore_cache=True)

        assert result.title == "Fresh"
        assert adapter._run_cache["tm101"].title == "Cached"

    @pytest.mark.parametrize("batch_size", [0, 101])
    def test_get_items_rejects_invalid_batch_size(self, adapter, batch_size):
        with pytest.raises(Failed, match=f"batch_size.*{batch_size}"):
            adapter.get_items("tmdb", "movie", [1], batch_size=batch_size)

    def test_sync_list_rejects_ambiguous_names(self, adapter):
        adapter._request = MagicMock(return_value=([{"id": 1, "name": "Favourites"}, {"id": 2, "name": "Favourites"}], {}))
        with pytest.raises(Failed, match="Multiple lists"):
            adapter.sync_list("Favourites", [])

    def test_sync_list_uses_list_id_when_syncing(self, adapter, monkeypatch):
        monkeypatch.setattr("modules.mdblist.logger", FakeLogger())
        adapter._request = MagicMock(return_value=([{"id": 1, "name": "Favourites"}], {}))
        adapter.get_tmdb_ids = MagicMock(return_value=[])

        adapter.sync_list("Favourites", [])

        adapter.get_tmdb_ids.assert_called_once_with("mdblist_list", {"id": 1}, is_movie=None)

    def test_sync_list_removes_existing_items_before_adding_in_source_order(self, adapter, monkeypatch):
        monkeypatch.setattr("modules.mdblist.logger", FakeLogger())
        adapter._request = MagicMock(return_value=([{"id": 1, "name": "Favourites"}], {}))
        adapter.get_tmdb_ids = MagicMock(return_value=[(1, "tmdb")])

        adapter.sync_list("Favourites", [(1, "tmdb"), (2, "tmdb")])

        remove_call = next(call for call in adapter._request.call_args_list if call.args[0].endswith("/items/remove"))
        add_call = next(call for call in adapter._request.call_args_list if call.args[0].endswith("/items/add"))
        assert remove_call.kwargs["json_data"] == {"movies": [{"tmdb": 1}]}
        assert add_call.kwargs["json_data"] == {"movies": [{"tmdb": 1}, {"tmdb": 2}]}
        assert adapter._request.call_args_list.index(remove_call) < adapter._request.call_args_list.index(add_call)

    def test_sync_list_limits_removals_to_requested_media_types(self, adapter, monkeypatch):
        monkeypatch.setattr("modules.mdblist.logger", FakeLogger())
        adapter._request = MagicMock(return_value=([{"id": 1, "name": "Favourites", "username": "user", "slug": "favourites"}], {}))
        adapter.get_tmdb_ids = MagicMock(return_value=[(1, "tmdb"), (2, "tmdb_show")])

        adapter.sync_list("Favourites", [], removal_types={"tmdb"})

        remove_call = next(call for call in adapter._request.call_args_list if call.args[0].endswith("/items/remove"))
        assert remove_call.kwargs["json_data"] == {"movies": [{"tmdb": 1}]}
