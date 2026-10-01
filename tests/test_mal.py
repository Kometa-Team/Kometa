"""Tests for modules/mal.py — MyAnimeList client."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401
from modules.util import ServiceError
from tests.conftest import FakeLogger


class TestMyAnimeList:
    @pytest.fixture
    def adapter(self, monkeypatch):
        monkeypatch.setattr("modules.mal.logger", FakeLogger())
        from modules.mal import MyAnimeList

        m = MyAnimeList.__new__(MyAnimeList)
        m.requests = MagicMock()
        m.cache = MagicMock()
        m.client_id = "fake"
        m.client_secret = "fake"
        m._genres = {}
        m._studios = {}
        m._delay = None
        return m

    def test_genres_populates_on_first_access(self, adapter):
        adapter._jikan_request = MagicMock(return_value={"data": [{"mal_id": 1, "name": "Action"}]})
        genres = adapter.genres
        assert "Action" in genres
        assert genres["Action"] == 1

    def test_jikan_request_raises_service_error_on_jikan_error_payload(self, adapter):
        # Jikan returns a 200-decodable error body (e.g. when MAL itself is unreachable) rather than
        # an HTTP error status, so get_json() happily hands back this dict instead of raising.
        adapter.requests.get_json = MagicMock(return_value={"status": 504, "type": "BadResponseException", "message": "Jikan failed to connect to MyAnimeList. MyAnimeList may be down/unavailable or refuses to connect", "error": None})
        with pytest.raises(ServiceError, match="Jikan API returned an error"):
            adapter._jikan_request("anime", params={"genres": 1})

    def test_jikan_request_passes_through_valid_payload(self, adapter):
        payload = {"data": [{"mal_id": 1}], "pagination": {"last_visible_page": 1, "items": {"total": 1}}}
        adapter.requests.get_json = MagicMock(return_value=payload)
        assert adapter._jikan_request("anime", params={"genres": 1}) == payload

    def test_pagination_raises_service_error_on_zero_total(self, adapter):
        adapter._jikan_request = MagicMock(return_value={"data": [], "pagination": {"last_visible_page": 1, "items": {"total": 0}}})
        with pytest.raises(ServiceError, match="No MyAnimeList IDs for Search"):
            adapter._pagination("anime", params={"genres": 1}, limit=100)
