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


class TestRefresh:
    @pytest.fixture
    def adapter(self, monkeypatch):
        monkeypatch.setattr("modules.mal.logger", FakeLogger())
        from modules.mal import MyAnimeList

        m = MyAnimeList.__new__(MyAnimeList)
        m.requests = MagicMock()
        m.requests.post_json.return_value = {"error": "invalid_grant"}
        m.authorization = {"access_token": "old", "refresh_token": "rt-1"}
        m.client_secret = "app-secret"
        return m

    @pytest.mark.parametrize("client_secret", [None, "", "leftover-secret"])
    def test_official_client_omits_client_secret(self, adapter, client_secret):
        from modules.mal import OFFICIAL_CLIENT_ID, urls

        adapter.client_id = OFFICIAL_CLIENT_ID
        adapter.client_secret = client_secret
        assert adapter._refresh() is False
        adapter.requests.post_json.assert_called_once_with(
            urls["oauth_token"],
            data={"client_id": OFFICIAL_CLIENT_ID, "refresh_token": "rt-1", "grant_type": "refresh_token"},
        )
        assert "client_secret" not in adapter.requests.post_json.call_args.kwargs["data"]

    def test_other_client_posts_client_secret(self, adapter):
        from modules.mal import urls

        adapter.client_id = "user-app-id"
        adapter.requests.post_json.return_value = {"error": "invalid_grant"}
        assert adapter._refresh() is False
        adapter.requests.post_json.assert_called_once_with(
            urls["oauth_token"],
            data={"client_id": "user-app-id", "client_secret": "app-secret", "refresh_token": "rt-1", "grant_type": "refresh_token"},
        )
