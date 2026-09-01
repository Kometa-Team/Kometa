"""Tests for modules/omdb.py — OMDb API integration."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401
from tests.conftest import FakeLogger, FakeResponse


class TestOMDb:
    @pytest.fixture
    def adapter(self):
        from modules.omdb import OMDb

        o = OMDb.__new__(OMDb)
        o.requests = MagicMock()
        o.cache = MagicMock()
        o.cache.query_omdb.return_value = ({}, None)
        o.apikey = "k"
        o.expiration = 30
        o.limit = False
        return o

    def test_get_omdb_parses_response(self, adapter, monkeypatch):
        monkeypatch.setattr("modules.omdb.logger", FakeLogger())
        adapter.requests.get.return_value = FakeResponse({"Title": "T", "Year": "2023", "imdbID": "tt1", "Response": "True"}, 200)
        r = adapter.get_omdb("tt1", ignore_cache=True)
        assert r.title == "T"

    @pytest.mark.parametrize(
        "response",
        [
            {"imdbRating": "10.1"},
            {"imdbRating": "nan"},
            {"Metascore": "-1"},
            {"Ratings": [{"Source": "Rotten Tomatoes", "Value": "101%"}]},
            {"imdbRating": "not-a-rating"},
        ],
    )
    def test_invalid_provider_rating_is_returned_but_not_cached(self, adapter, monkeypatch, response):
        logger = FakeLogger()
        monkeypatch.setattr("modules.omdb.logger", logger)
        adapter.requests.get.return_value = FakeResponse({"Title": "T", "imdbID": "tt1", "Response": "True", **response}, 200)

        result = adapter.get_omdb("tt1")

        assert not result.ratings_valid
        adapter.cache.update_omdb.assert_not_called()
        assert any("response will not be cached" in message for message in logger.warning_messages)

    def test_missing_provider_rating_can_be_cached(self, adapter, monkeypatch):
        monkeypatch.setattr("modules.omdb.logger", FakeLogger())
        adapter.requests.get.return_value = FakeResponse({"Title": "T", "imdbID": "tt1", "imdbRating": "N/A", "Response": "True"}, 200)

        result = adapter.get_omdb("tt1")

        assert result.ratings_valid
        adapter.cache.update_omdb.assert_called_once()
