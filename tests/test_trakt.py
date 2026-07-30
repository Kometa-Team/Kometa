"""Tests for modules/trakt.py — Trakt.tv list/genre fetcher."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401
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
        trakt.pin = None
        trakt.authorization = {"refresh_token": "refresh-token"}
        return trakt

    @pytest.fixture(autouse=True)
    def mock_trakt_logger(self, monkeypatch):
        logger = MagicMock()
        monkeypatch.setattr("modules.trakt.logger", logger)
        return logger

    def test_headless_pin_prompt_raises_actionable_trakt_error(self, adapter, monkeypatch):
        monkeypatch.setattr("modules.trakt.webbrowser.open", MagicMock())
        monkeypatch.setattr("modules.trakt.util.logger_input", MagicMock(side_effect=Failed("Input Failed")))

        with pytest.raises(Failed) as exc_info:
            adapter._authorization()

        assert str(exc_info.value) == "Trakt Error: Authorization required; interactive input is unavailable. Reauthenticate at https://utilities.kometa.wiki/ and update your config."

    def test_other_input_failures_are_unchanged(self, adapter, monkeypatch):
        monkeypatch.setattr("modules.trakt.webbrowser.open", MagicMock())
        monkeypatch.setattr("modules.trakt.util.logger_input", MagicMock(side_effect=Failed("Different input failure")))

        with pytest.raises(Failed, match="Different input failure"):
            adapter._authorization()

    def test_failed_refresh_logs_http_response(self, adapter, mock_trakt_logger):
        adapter.requests.post.return_value = MagicMock(status_code=403, reason="Forbidden")

        assert adapter._refresh() is False
        mock_trakt_logger.debug.assert_called_once_with("Trakt Error: Access Token Refresh Failed: (403) Forbidden")
