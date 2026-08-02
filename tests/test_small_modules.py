"""Tests for small notification and data-source modules.

All use ``__new__`` to bypass constructors that make API calls.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401 — pre-import to break circular deps
from modules.util import Failed
from tests.conftest import FakeLogger, FakeRequests, FakeResponse

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

    def test_init_does_not_publish_access_test(self, monkeypatch):
        from modules.ntfy import Ntfy

        monkeypatch.setattr("modules.ntfy.logger", FakeLogger())
        requests = MagicMock()

        Ntfy(requests, {"url": "http://ntfy:8080", "token": "fake", "topic": "test"})

        requests.post.assert_not_called()


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


class TestTracearr:
    SERVER_ID = "550e8400-e29b-41d4-a716-446655440000"

    @pytest.fixture
    def adapter(self, monkeypatch):
        from modules.tracearr import Tracearr

        monkeypatch.setattr("modules.tracearr.logger", FakeLogger())
        t = Tracearr.__new__(Tracearr)
        t.requests = MagicMock()
        t.url = "http://tracearr:3000"
        t.api = f"{t.url}/api/v1/public"
        t.history_api = f"{t.url}/api/v2/public"
        t.history_version = 2
        t.apikey = "trr_pub_test"
        t.server_id = self.SERVER_ID
        t.library = MagicMock()
        t.library.is_movie = True
        t.library.is_show = False
        t.library.exact_search = MagicMock(return_value=[MagicMock(ratingKey=202)])
        return t

    def test_get_rating_keys_returns_popular_items(self, adapter, monkeypatch):
        monkeypatch.setattr("modules.tracearr.logger", FakeLogger())
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        adapter._request = MagicMock(
            return_value={
                "data": [
                    {
                        "serverId": self.SERVER_ID,
                        "mediaType": "movie",
                        "mediaTitle": "Tracearr Movie",
                        "year": 2024,
                        "watched": True,
                        "stoppedAt": now,
                        "user": {"id": "user-1"},
                    },
                    {
                        "serverId": self.SERVER_ID,
                        "mediaType": "movie",
                        "mediaTitle": "Tracearr Movie",
                        "year": 2024,
                        "watched": True,
                        "stoppedAt": now,
                        "user": {"id": "user-2"},
                    },
                    {
                        "serverId": self.SERVER_ID,
                        "mediaType": "movie",
                        "mediaTitle": "Other Movie",
                        "year": 2023,
                        "watched": True,
                        "stoppedAt": now,
                        "user": {"id": "user-3"},
                    },
                ],
                "meta": {"total": 3, "page": 1, "pageSize": 100},
            }
        )
        adapter.library.exact_search = MagicMock(side_effect=lambda title, libtype=None, year=None: [MagicMock(ratingKey=202)] if title == "Tracearr Movie" else [])
        result = adapter.get_rating_keys(
            {"list_type": "popular", "list_size": 10, "list_days": 30, "list_minimum": 0},
        )
        assert result == [(202, "ratingKey")]
        adapter.library.exact_search.assert_any_call("Tracearr Movie", libtype="movie", year=2024)
        params = adapter._request.call_args.kwargs["params"]
        assert params["server_id"] == self.SERVER_ID
        assert params["media_type"] == "movie"
        assert params["pageSize"] == 100

    def test_show_history_requests_episodes_and_groups_by_show(self, adapter, monkeypatch):
        monkeypatch.setattr("modules.tracearr.logger", FakeLogger())
        adapter.library.is_movie = False
        adapter.library.is_show = True
        adapter._request = MagicMock(
            return_value={
                "data": [
                    {
                        "serverId": self.SERVER_ID,
                        "mediaType": "episode",
                        "mediaTitle": "Pilot",
                        "showTitle": "Example Show",
                        "year": 2020,
                        "watched": True,
                        "stoppedAt": "2026-07-29T12:00:00Z",
                        "user": {"id": "user-1"},
                    },
                    {
                        "serverId": self.SERVER_ID,
                        "mediaType": "episode",
                        "mediaTitle": "Finale",
                        "showTitle": "Example Show",
                        "year": 2026,
                        "watched": True,
                        "stoppedAt": "2026-07-30T12:00:00Z",
                        "user": {"id": "user-1"},
                    },
                ],
                "meta": {"total": 2, "page": 1, "pageSize": 100},
            }
        )

        result = adapter.get_rating_keys({"list_type": "watched", "list_size": 10, "list_days": 30, "list_minimum": 0})

        assert result == [(202, "ratingKey")]
        adapter.library.exact_search.assert_called_once_with("Example Show", libtype="show", year=None)
        assert adapter._request.call_args.kwargs["params"]["media_type"] == "episode"

    def test_v2_history_uses_library_and_rating_key_for_exact_plex_item(self, adapter):
        adapter.library.Plex.key = 7
        plex_item = MagicMock(ratingKey=202)
        adapter.library.fetch_item.return_value = plex_item
        adapter._request = MagicMock(
            return_value={
                "data": [
                    {
                        "server_id": self.SERVER_ID,
                        "media_type": "movie",
                        "media_title": "Tracearr Movie",
                        "year": 2024,
                        "library_id": "7",
                        "rating_key": "202",
                        "watched": True,
                        "stopped_at": "2026-07-30T12:00:00Z",
                        "user": {"id": "user-1"},
                    }
                ],
                "meta": {"nextCursor": None, "pageSize": 100},
            }
        )

        result = adapter.get_rating_keys({"list_type": "history", "list_size": 10, "list_days": 30, "list_minimum": 0})

        assert result == [(202, "ratingKey")]
        adapter.library.fetch_item.assert_called_once_with("202")
        adapter.library.exact_search.assert_not_called()
        assert adapter._request.call_args.kwargs["api"] == adapter.history_api

    def test_v2_history_excludes_items_watched_in_another_plex_library(self, adapter):
        adapter.library.Plex.key = 7
        adapter._request = MagicMock(
            return_value={
                "data": [
                    {
                        "server_id": self.SERVER_ID,
                        "media_type": "movie",
                        "media_title": "Tracearr Movie",
                        "year": 2024,
                        "library_id": "8",
                        "rating_key": "202",
                        "watched": True,
                        "stopped_at": "2026-07-30T12:00:00Z",
                        "user": {"id": "user-1"},
                    }
                ],
                "meta": {"nextCursor": None, "pageSize": 100},
            }
        )

        result = adapter.get_rating_keys({"list_type": "history", "list_size": 10, "list_days": 30, "list_minimum": 0})

        assert result == []
        adapter.library.fetch_item.assert_not_called()
        adapter.library.exact_search.assert_not_called()

    def test_v2_show_history_fetches_grandparent_rating_key(self, adapter):
        adapter.library.is_movie = False
        adapter.library.is_show = True
        adapter.library.Plex.key = 9
        plex_show = MagicMock(ratingKey=303)
        adapter.library.fetch_item.return_value = plex_show
        adapter._request = MagicMock(
            return_value={
                "data": [
                    {
                        "server_id": self.SERVER_ID,
                        "media_type": "episode",
                        "media_title": "Pilot",
                        "show_title": "Example Show",
                        "season_number": 1,
                        "episode_number": 1,
                        "library_id": "9",
                        "rating_key": "304",
                        "grandparent_rating_key": "303",
                        "watched": True,
                        "stopped_at": "2026-07-30T12:00:00Z",
                        "user": {"id": "user-1"},
                    }
                ],
                "meta": {"nextCursor": None, "pageSize": 100},
            }
        )

        result = adapter.get_rating_keys({"list_type": "history", "list_size": 10, "list_days": 30, "list_minimum": 0})

        assert result == [(303, "ratingKey")]
        adapter.library.fetch_item.assert_called_once_with("303")

    def test_popular_and_trending_include_incomplete_sessions(self, adapter):
        items = [
            {
                "serverId": self.SERVER_ID,
                "mediaType": "movie",
                "mediaTitle": "Started Movie",
                "year": 2024,
                "watched": False,
                "startedAt": "2026-07-30T12:00:00Z",
                "user": {"id": "user-1"},
            }
        ]

        assert [item["title"] for item in adapter._aggregate_history(items, "popular", 0)] == ["Started Movie"]
        assert [item["title"] for item in adapter._aggregate_history(items, "trending", 0)] == ["Started Movie"]
        assert adapter._aggregate_history(items, "watched", 0) == []
        assert adapter._aggregate_history(items, "completed", 0) == []

    def test_trending_ranks_activity_volume_while_history_ranks_recency(self, adapter):
        items = [
            {
                "serverId": self.SERVER_ID,
                "mediaType": "movie",
                "mediaTitle": "Recently Played Once",
                "year": 2026,
                "watched": False,
                "stoppedAt": "2026-07-30T12:00:00Z",
                "user": {"id": "user-1"},
            },
            *[
                {
                    "serverId": self.SERVER_ID,
                    "mediaType": "movie",
                    "mediaTitle": "Active Earlier",
                    "year": 2025,
                    "watched": False,
                    "stoppedAt": f"2026-07-{20 + index:02d}T12:00:00Z",
                    "user": {"id": f"user-{index}"},
                }
                for index in range(1, 4)
            ],
        ]

        assert [item["title"] for item in adapter._aggregate_history(items, "history", 0)] == ["Recently Played Once", "Active Earlier"]
        assert [item["title"] for item in adapter._aggregate_history(items, "trending", 0)] == ["Active Earlier", "Recently Played Once"]

    def test_rewatched_requires_repeat_plays_by_the_same_user(self, adapter):
        def movie(title, user, day):
            return {
                "serverId": self.SERVER_ID,
                "mediaType": "movie",
                "mediaTitle": title,
                "year": 2025,
                "watched": True,
                "stoppedAt": f"2026-07-{day:02d}T12:00:00Z",
                "user": {"id": user},
            }

        items = [
            movie("Three Plays by One User", "user-1", 20),
            movie("Three Plays by One User", "user-1", 21),
            movie("Three Plays by One User", "user-1", 22),
            movie("Two Plays by One User", "user-2", 23),
            movie("Two Plays by One User", "user-2", 24),
            movie("One Play Each", "user-3", 25),
            movie("One Play Each", "user-4", 26),
        ]

        ranked = adapter._aggregate_history(items, "rewatched", 0)

        assert [item["title"] for item in ranked] == ["Three Plays by One User", "Two Plays by One User"]
        assert [item["repeat_plays"] for item in ranked] == [2, 1]
        assert [item["title"] for item in adapter._aggregate_history(items, "rewatched", 2)] == ["Three Plays by One User"]

    def test_completed_sorts_by_most_recent_completion(self, adapter):
        items = [
            {
                "serverId": self.SERVER_ID,
                "mediaType": "movie",
                "mediaTitle": "Frequently Watched",
                "year": 2024,
                "watched": True,
                "stoppedAt": "2026-07-20T12:00:00Z",
                "user": {"id": "user-1"},
            },
            {
                "serverId": self.SERVER_ID,
                "mediaType": "movie",
                "mediaTitle": "Frequently Watched",
                "year": 2024,
                "watched": True,
                "stoppedAt": "2026-07-21T12:00:00Z",
                "user": {"id": "user-1"},
            },
            {
                "serverId": self.SERVER_ID,
                "mediaType": "movie",
                "mediaTitle": "Recently Completed",
                "year": 2025,
                "watched": True,
                "stoppedAt": "2026-07-30T12:00:00Z",
                "user": {"id": "user-2"},
            },
        ]

        ranked = adapter._aggregate_history(items, "completed", 0)

        assert [item["title"] for item in ranked] == ["Recently Completed", "Frequently Watched"]

    def test_binged_counts_distinct_completed_episodes_per_user(self, adapter):
        def episode(show, season, number, user, watched=True):
            return {
                "serverId": self.SERVER_ID,
                "mediaType": "episode",
                "mediaTitle": f"Episode {number}",
                "showTitle": show,
                "seasonNumber": season,
                "episodeNumber": number,
                "watched": watched,
                "stoppedAt": f"2026-07-{20 + number:02d}T12:00:00Z",
                "user": {"id": user},
            }

        items = [
            episode("Three Episode Binge", 1, 1, "user-1"),
            episode("Three Episode Binge", 1, 2, "user-1"),
            episode("Three Episode Binge", 1, 3, "user-1"),
            episode("Two Episode Binge", 1, 1, "user-2"),
            episode("Two Episode Binge", 1, 2, "user-2"),
            episode("Split Between Users", 1, 1, "user-3"),
            episode("Split Between Users", 1, 2, "user-4"),
            episode("Repeated Episode", 1, 1, "user-5"),
            episode("Repeated Episode", 1, 1, "user-5"),
            episode("Incomplete Episode", 1, 1, "user-6", watched=False),
            episode("Incomplete Episode", 1, 2, "user-6", watched=False),
        ]

        ranked = adapter._aggregate_history(items, "binged", 0)

        assert [item["title"] for item in ranked] == ["Three Episode Binge", "Two Episode Binge"]
        assert [item["binged_episodes"] for item in ranked] == [3, 2]
        assert [item["title"] for item in adapter._aggregate_history(items, "binged", 3)] == ["Three Episode Binge"]

    def test_transcoded_ranks_only_sessions_requiring_transcoding(self, adapter):
        def movie(title, user, **quality):
            return {
                "serverId": self.SERVER_ID,
                "mediaType": "movie",
                "mediaTitle": title,
                "year": 2024,
                "watched": True,
                "stoppedAt": "2026-07-30T12:00:00Z",
                "user": {"id": user},
                **quality,
            }

        items = [
            movie("Frequently Transcoded", "user-1", isTranscode=True),
            movie("Frequently Transcoded", "user-2", videoDecision="transcode"),
            movie("Audio Transcoded", "user-3", audioDecision="transcode"),
            movie("Direct Played", "user-4", isTranscode=False, videoDecision="directplay", audioDecision="copy"),
        ]

        ranked = adapter._aggregate_history(items, "transcoded", 0)

        assert [item["title"] for item in ranked] == ["Frequently Transcoded", "Audio Transcoded"]
        assert [item["transcoded_sessions"] for item in ranked] == [2, 1]
        assert [item["title"] for item in adapter._aggregate_history(items, "transcoded", 2)] == ["Frequently Transcoded"]

    def test_playlist_uses_external_id(self, adapter):
        item = MagicMock(ratingKey=202, guid="plex://movie/example")
        adapter.library.exact_search.return_value = [item]
        adapter.library.get_ids.return_value = (1234, None, "tt1234567")
        adapter._request = MagicMock(
            return_value={
                "data": [
                    {
                        "serverId": self.SERVER_ID,
                        "mediaType": "movie",
                        "mediaTitle": "Tracearr Movie",
                        "year": 2024,
                        "watched": True,
                        "stoppedAt": "2026-07-30T12:00:00Z",
                        "user": {"id": "user-1"},
                    }
                ],
                "meta": {"total": 1, "page": 1, "pageSize": 100},
            }
        )

        result = adapter.get_rating_keys(
            {"list_type": "history", "list_size": 10, "list_days": 30, "list_minimum": 0},
            is_playlist=True,
            libraries=[adapter.library],
        )

        assert result == [(1234, "tmdb")]
        assert "media_type" not in adapter._request.call_args.kwargs["params"]

    def test_v2_playlist_deduplicates_same_movie_watched_from_two_libraries(self, adapter):
        adapter.library.Plex.key = 7
        adapter.library.fetch_item.return_value = MagicMock(ratingKey=202)
        adapter.library.get_ids.return_value = (1234, None, None)
        second_library = MagicMock()
        second_library.is_movie = True
        second_library.is_show = False
        second_library.Plex.key = 8
        second_library.fetch_item.return_value = MagicMock(ratingKey=203)
        second_library.get_ids.return_value = (1234, None, None)
        adapter._request = MagicMock(
            return_value={
                "data": [
                    {
                        "server_id": self.SERVER_ID,
                        "media_type": "movie",
                        "media_title": "Duplicate Movie",
                        "year": 2024,
                        "library_id": library_id,
                        "rating_key": rating_key,
                        "watched": True,
                        "stopped_at": "2026-07-30T12:00:00Z",
                        "user": {"id": "user-1"},
                    }
                    for library_id, rating_key in (("7", "202"), ("8", "203"))
                ],
                "meta": {"nextCursor": None, "pageSize": 100},
            }
        )

        result = adapter.get_rating_keys(
            {"list_type": "history", "list_size": 10, "list_days": 30, "list_minimum": 0},
            is_playlist=True,
            libraries=[adapter.library, second_library],
        )

        assert result == [(1234, "tmdb")]
        adapter.library.fetch_item.assert_called_once_with("202")
        second_library.fetch_item.assert_called_once_with("203")

    def test_binged_playlist_requests_only_episodes(self, adapter):
        adapter.library.is_movie = False
        adapter.library.is_show = True
        item = MagicMock(ratingKey=202, guid="plex://show/example")
        adapter.library.exact_search.return_value = [item]
        adapter.library.get_ids.return_value = (None, 5678, "tt1234567")
        adapter._request = MagicMock(
            return_value={
                "data": [
                    {
                        "serverId": self.SERVER_ID,
                        "mediaType": "episode",
                        "mediaTitle": f"Episode {number}",
                        "showTitle": "Binged Show",
                        "seasonNumber": 1,
                        "episodeNumber": number,
                        "watched": True,
                        "stoppedAt": f"2026-07-{20 + number:02d}T12:00:00Z",
                        "user": {"id": "user-1"},
                    }
                    for number in (1, 2)
                ],
                "meta": {"total": 2, "page": 1, "pageSize": 100},
            }
        )

        result = adapter.get_rating_keys(
            {"list_type": "binged", "list_size": 10, "list_days": 30, "list_minimum": 0},
            is_playlist=True,
            libraries=[adapter.library],
        )

        assert result == [(5678, "tvdb")]
        assert adapter._request.call_args.kwargs["params"]["media_type"] == "episode"

    def test_resolves_server_uuid_by_plex_name(self, adapter):
        adapter.library.PlexServer.friendlyName = "Main Plex"
        health = {
            "servers": [
                {"id": self.SERVER_ID, "name": "Main Plex", "type": "plex"},
                {"id": "550e8400-e29b-41d4-a716-446655440001", "name": "Jellyfin", "type": "jellyfin"},
            ]
        }

        assert adapter._resolve_server_id(health, None) == self.SERVER_ID

    def test_configured_server_uuid_takes_precedence(self, adapter):
        adapter.library.PlexServer.friendlyName = "Main Plex"
        configured_id = "550e8400-e29b-41d4-a716-446655440002"
        health = {
            "servers": [
                {"id": self.SERVER_ID, "name": "Main Plex", "type": "plex"},
                {"id": configured_id, "name": "Other Plex", "type": "plex"},
            ]
        }

        assert adapter._resolve_server_id(health, configured_id) == configured_id

    def test_ambiguous_server_requires_server_id(self, adapter):
        adapter.library.PlexServer.friendlyName = "Different Name"
        health = {
            "servers": [
                {"id": self.SERVER_ID, "name": "Plex One", "type": "plex"},
                {"id": "550e8400-e29b-41d4-a716-446655440002", "name": "Plex Two", "type": "plex"},
            ]
        }

        with pytest.raises(Failed, match="set tracearr server_id explicitly"):
            adapter._resolve_server_id(health, None)

    def test_request_reports_authentication_error(self, adapter):
        adapter.requests.get.return_value = FakeResponse(payload={"message": "Invalid API key"}, status_code=401)

        with pytest.raises(Failed, match="API key was rejected.*Invalid API key"):
            adapter._request("history", api=adapter.history_api, allow_404=True)

    def test_request_can_treat_v2_404_as_unsupported(self, adapter):
        adapter.requests.get.return_value = FakeResponse(payload={"message": "Route not found"}, status_code=404)

        assert adapter._request("history", api=adapter.history_api, allow_404=True) is None

    def test_history_falls_back_to_v1_only_when_v2_is_unavailable(self, adapter):
        adapter._request = MagicMock(
            side_effect=[
                None,
                {
                    "data": [
                        {
                            "serverId": self.SERVER_ID,
                            "mediaType": "movie",
                            "mediaTitle": "Legacy Movie",
                            "year": 2024,
                            "watched": True,
                            "stoppedAt": "2026-07-30T12:00:00Z",
                            "user": {"id": "user-1"},
                        }
                    ],
                    "meta": {"total": 1, "page": 1, "pageSize": 100},
                },
            ]
        )

        result = adapter.get_rating_keys({"list_type": "history", "list_size": 10, "list_days": 30, "list_minimum": 0})

        assert result == [(202, "ratingKey")]
        assert adapter.history_version == 1
        first_call, second_call = adapter._request.call_args_list
        assert first_call.kwargs["api"] == adapter.history_api
        assert first_call.kwargs["allow_404"] is True
        assert second_call.kwargs["params"]["serverId"] == self.SERVER_ID
        assert second_call.kwargs["params"]["mediaType"] == "movie"
        assert second_call.kwargs["params"]["startDate"] == first_call.kwargs["params"]["since"][:10]

    def test_request_rejects_non_json_response(self, adapter):
        adapter.requests.get.return_value = FakeResponse(status_code=502, content=b"Bad Gateway", json_error=ValueError("not json"))

        with pytest.raises(Failed, match="Non-JSON response.*HTTP 502"):
            adapter._request("history")

    def test_history_requires_pagination_envelope(self, adapter):
        adapter._request = MagicMock(return_value={"data": []})

        with pytest.raises(Failed, match="pagination metadata"):
            adapter._fetch_history({"page": 1, "pageSize": 100})

    def test_history_paginates_using_v2_cursor_metadata(self, adapter):
        adapter._request = MagicMock(
            side_effect=[
                {"data": [{"id": "first"}], "meta": {"nextCursor": "next-page", "pageSize": 1}},
                {"data": [{"id": "second"}], "meta": {"nextCursor": None, "pageSize": 1}},
            ]
        )

        assert adapter._fetch_history({"pageSize": 1}) == [{"id": "first"}, {"id": "second"}]
        assert adapter._request.call_args_list[1].kwargs["params"]["cursor"] == "next-page"

    def test_v1_history_fallback_preserves_page_pagination(self, adapter):
        adapter._request = MagicMock(
            side_effect=[
                {"data": [{"id": "first"}], "meta": {"total": 2, "page": 1, "pageSize": 1}},
                {"data": [{"id": "second"}], "meta": {"total": 2, "page": 2, "pageSize": 1}},
            ]
        )
        params = {
            "pageSize": 1,
            "since": "2026-07-01T12:00:00+00:00",
            "until": "2026-07-31T12:00:00+00:00",
            "server_id": self.SERVER_ID,
            "media_type": "movie",
        }

        assert adapter._fetch_history_v1(params) == [{"id": "first"}, {"id": "second"}]
        assert adapter._request.call_args_list[1].kwargs["params"]["page"] == 2

    def test_constructor_requires_public_api_key(self, monkeypatch):
        from modules.tracearr import Tracearr

        monkeypatch.setattr("modules.tracearr.logger", FakeLogger())
        with pytest.raises(Failed, match="API key is required"):
            Tracearr(MagicMock(), MagicMock(), {"url": "http://tracearr:3000", "apikey": None, "server_id": None})
