"""Tests for modules/trakt.py — Trakt.tv list/genre fetcher."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401
import modules.trakt as trakt_module
from modules.trakt import Trakt, base_url
from modules.util import Failed


class TestTrakt:
    @pytest.fixture
    def adapter(self):
        from modules.trakt import Trakt

        t = Trakt.__new__(Trakt)
        t._request = MagicMock()
        t._slugs = None
        t._movie_genres = None
        t._show_genres = None
        t._movie_languages = None
        t._show_languages = None
        t._movie_countries = None
        t._show_countries = None
        t._movie_certifications = None
        t._show_certifications = None
        return t

    def test_movie_genres(self, adapter):
        adapter._request.return_value = [{"slug": "action"}, {"slug": "comedy"}]
        assert adapter.movie_genres == ["action", "comedy"]

    def test_movie_genres_caches(self, adapter):
        adapter._request.return_value = [{"slug": "action"}]
        _ = adapter.movie_genres
        adapter._request.reset_mock()
        assert adapter.movie_genres == ["action"]
        adapter._request.assert_not_called()

    def test_show_genres(self, adapter):
        adapter._request.return_value = [{"slug": "drama"}]
        assert adapter.show_genres == ["drama"]

    def test_slugs_is_property(self, adapter):
        """slugs is a @property — accessed without ()."""
        adapter._request.return_value = [{"ids": {"slug": "my-list"}}]
        assert adapter.slugs == ["my-list"]


class TestTraktAuthorization:
    @pytest.fixture
    def adapter(self):
        from modules.trakt import Trakt

        trakt = Trakt.__new__(Trakt)
        trakt.requests = MagicMock()
        trakt.client_id = "client-id"
        trakt.client_secret = "client-secret"
        trakt.authorization = {"refresh_token": "refresh-token"}
        trakt.webhooks = MagicMock()
        return trakt

    @pytest.fixture(autouse=True)
    def mock_trakt_logger(self, monkeypatch):
        logger = MagicMock()
        monkeypatch.setattr("modules.trakt.logger", logger)
        return logger

    def test_failed_refresh_logs_http_response(self, adapter, mock_trakt_logger):
        adapter.requests.post.return_value = MagicMock(status_code=403, reason="Forbidden")

        assert adapter._refresh() is False
        mock_trakt_logger.debug.assert_called_once_with("Trakt Error: Access Token Refresh Failed: (403) Forbidden")


class TestTraktRequest:
    @pytest.fixture(autouse=True)
    def mock_trakt_logger(self, monkeypatch):
        monkeypatch.setattr(trakt_module, "logger", MagicMock())

    @staticmethod
    def adapter(response):
        trakt = Trakt.__new__(Trakt)
        trakt.requests = MagicMock()
        trakt.requests.post.return_value = response
        trakt.authorization = {"access_token": "token"}
        trakt.client_id = "client-id"
        return trakt

    def test_request_accepts_created_response(self):
        payload = {"added": {"movies": 1}, "not_found": {"movies": []}}
        response = SimpleNamespace(status_code=201, reason="Created", headers={}, content=b"{}", json=MagicMock(return_value=payload))
        trakt = self.adapter(response)

        result = trakt._request("/users/me/lists/example/items", json_data={"movies": [{"ids": {"tmdb": 1}}]})

        assert result == payload
        response.json.assert_called_once_with()
        trakt.requests.post.assert_called_once_with(
            f"{base_url}/users/me/lists/example/items",
            json={"movies": [{"ids": {"tmdb": 1}}]},
            headers={"Content-Type": "application/json", "Authorization": "Bearer token", "trakt-api-version": "2", "trakt-api-key": "client-id"},
        )

    def test_request_accepts_no_content_response(self):
        response = SimpleNamespace(status_code=204, reason="No Content", headers={}, content=b"", json=MagicMock())
        trakt = self.adapter(response)

        assert trakt._request("/users/me/lists/example/items", json_data={}) == []
        response.json.assert_not_called()

    def test_request_rejects_non_success_response(self):
        response = SimpleNamespace(status_code=300, reason="Multiple Choices", headers={}, content=b"", json=MagicMock())
        trakt = self.adapter(response)

        with pytest.raises(Failed, match=r"\(300\) Multiple Choices"):
            trakt._request("/users/me/lists/example/items", json_data={})
