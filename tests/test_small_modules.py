"""Tests for small notification and data-source modules.

All use ``__new__`` to bypass constructors that make API calls.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401 — pre-import to break circular deps
from modules.util import Failed
from tests.conftest import FakeLogger, FakeRequests

# ═══════════════════════════════════════════════════════════════════════
# StevenLu (32 lines — trending movie lists)
# ═══════════════════════════════════════════════════════════════════════


class TestStevenLu:
    @pytest.fixture
    def adapter(self):
        from modules.stevenlu import StevenLu

        s = StevenLu.__new__(StevenLu)
        s.requests = FakeRequests(
            get_payloads={
                "https://s3.amazonaws.com/popular-movies/movies.json": [
                    {"title": "Test Movie", "imdb_id": "tt1234567"},
                ],
            }
        )
        return s

    def test_popular_returns_imdb_ids(self, adapter, monkeypatch):
        monkeypatch.setattr("modules.stevenlu.logger", FakeLogger())
        ids = adapter.get_imdb_ids("stevenlu_popular", None)
        assert len(ids) == 1


class TestGotify:
    @pytest.fixture
    def adapter(self):
        from modules.gotify import Gotify

        g = Gotify.__new__(Gotify)
        g.requests = MagicMock()
        g.url = "http://gotify:8080"
        g.token = "fake"
        g.header = {"X-Gotify-Key": "fake"}
        return g

    def test_notification_calls_request(self, adapter, monkeypatch):
        monkeypatch.setattr("modules.gotify.logger", FakeLogger())
        monkeypatch.setattr("modules.webhooks.get_message", lambda j: ("msg", "title", None))
        adapter._request = MagicMock(return_value=None)
        adapter.notification({"event": "test"})
        adapter._request.assert_called_once()


class TestNtfy:
    @pytest.fixture
    def adapter(self):
        from modules.ntfy import Ntfy

        n = Ntfy.__new__(Ntfy)
        n.requests = MagicMock()
        n.url = "http://ntfy:8080"
        n.token = "fake"
        n.topic = "test"
        return n

    def test_notification_sends_request(self, adapter, monkeypatch):
        monkeypatch.setattr("modules.ntfy.logger", FakeLogger())
        monkeypatch.setattr("modules.webhooks.get_message", lambda j: ("msg", "title", None))
        adapter._request = MagicMock(return_value=None)
        adapter.notification({"event": "test"})
        adapter._request.assert_called_once()


class TestNotifiarr:
    @pytest.fixture
    def adapter(self):
        from modules.notifiarr import Notifiarr

        n = Notifiarr.__new__(Notifiarr)
        n.requests = MagicMock()
        n.apikey = "fake"
        n.header = {"x-api-key": "fake"}
        return n

    def test_notification_calls_request(self, adapter):
        adapter._request = MagicMock(return_value=None)
        adapter.notification({"event": "test"})
        adapter._request.assert_called_once()


class TestICheckMovies:
    @pytest.fixture
    def adapter(self):
        from modules.icheckmovies import ICheckMovies

        i = ICheckMovies.__new__(ICheckMovies)
        i.requests = FakeRequests(
            html_pages={
                "https://www.icheckmovies.com/lists/": "<html><body></body></html>",
            }
        )
        return i

    def test_validate_rejects_non_list_url(self, adapter):
        with pytest.raises(Failed, match="must begin with"):
            adapter.validate_icheckmovies_lists("invalid-url")


class TestTautulli:
    @pytest.fixture
    def adapter(self):
        from modules.tautulli import Tautulli

        t = Tautulli.__new__(Tautulli)
        t.requests = MagicMock()
        t.api = "http://tautulli:8181/api/v2?apikey=fake"
        t.library = MagicMock()
        t.library.is_movie = True
        t.has_section = False
        return t

    def test_get_rating_keys_returns_list(self, adapter, monkeypatch):
        monkeypatch.setattr("modules.tautulli.logger", FakeLogger())
        adapter._request = MagicMock(
            return_value={
                "response": {
                    "data": [
                        {
                            "stat_id": "popular_movies",
                            "rows": [
                                {"rating_key": "101", "section_id": 1, "title": "Test", "year": 2023, "users_watched": 100, "total_plays": 200},
                            ],
                        }
                    ]
                }
            }
        )
        from plexapi.video import Movie as PlexMovie

        adapter.library.fetch_item = MagicMock(return_value=MagicMock(spec=PlexMovie))
        adapter.library.exact_search = MagicMock()
        result = adapter.get_rating_keys(
            {"list_type": "popular", "list_size": 10, "list_days": 30, "list_buffer": 0, "list_minimum": 0},
            all_items=True,
        )
        assert result == [("101", "ratingKey")]
