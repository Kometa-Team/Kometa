"""Tests for modules/mdblist.py — MDBList API integration."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401
from modules.util import Failed
from tests.conftest import FakeLogger, FakeRequests

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
