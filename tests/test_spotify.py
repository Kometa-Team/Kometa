from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import modules.spotify as spotify_module
from modules.builder import CollectionBuilder
from modules.spotify import Spotify
from modules.util import Failed
from tests.conftest import FakeLogger


@pytest.fixture(autouse=True)
def patch_logger(monkeypatch):
    monkeypatch.setattr(spotify_module, "logger", FakeLogger())


class TestSpotifyOAuth:
    def test_rejects_non_loopback_http_redirect_uri(self):
        with pytest.raises(Failed, match="redirect_uri"):
            Spotify(
                MagicMock(),
                False,
                {
                    "client_id": "client-id",
                    "client_secret": "client-secret",
                    "redirect_uri": "http://localhost:8888/callback",
                    "config_path": "config.yml",
                    "authorization": {},
                },
            )

    def test_refreshes_access_token_and_persists_authorization(self, monkeypatch):
        monkeypatch.setattr(spotify_module.time, "time", lambda: 1_000_000)
        requests = MagicMock()
        requests.post_json.return_value = {
            "access_token": "new-access-token",
            "expires_in": 3600,
            "scope": spotify_module.scopes,
            "token_type": "Bearer",
        }
        yaml = MagicMock()
        yaml.data = {"spotify": {"client_id": "client-id"}}
        requests.file_yaml.return_value = yaml

        spotify = Spotify(
            requests,
            False,
            {
                "client_id": "client-id",
                "client_secret": "client-secret",
                "redirect_uri": "http://127.0.0.1:8888/callback",
                "config_path": "config.yml",
                "authorization": {"refresh_token": "original-refresh-token", "scope": spotify_module.scopes},
            },
        )

        assert spotify.access_token == "new-access-token"
        requests.post_json.assert_called_once_with(
            spotify_module.token_url,
            data={"grant_type": "refresh_token", "refresh_token": "original-refresh-token"},
            headers={"Authorization": "Basic Y2xpZW50LWlkOmNsaWVudC1zZWNyZXQ="},
        )
        assert yaml.data["spotify"]["authorization"] == {
            "refresh_token": "original-refresh-token",
            "access_token": "new-access-token",
            "expires_in": 3600,
            "scope": spotify_module.scopes,
            "token_type": "Bearer",
            "expires_at": 1_003_600,
        }
        yaml.save.assert_called_once_with()

    def test_authorization_rejects_redirect_with_an_unexpected_state(self, monkeypatch):
        requests = MagicMock()
        monkeypatch.setattr(spotify_module.secrets, "token_urlsafe", lambda length: "expected-state")
        monkeypatch.setattr(spotify_module.webbrowser, "open", lambda *args, **kwargs: None)
        monkeypatch.setattr(spotify_module.util, "logger_input", lambda prompt: "http://localhost:8888/callback?code=code&state=wrong-state")

        with pytest.raises(Failed, match="state"):
            Spotify(
                requests,
                False,
                {
                    "client_id": "client-id",
                    "client_secret": "client-secret",
                "redirect_uri": "http://127.0.0.1:8888/callback",
                    "config_path": "config.yml",
                    "authorization": {},
                },
            )
        requests.post_json.assert_not_called()


class TestSpotifyPlaylist:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("37i9dQZF1FwLliIcKXtMsW", "37i9dQZF1FwLliIcKXtMsW"),
            ("https://open.spotify.com/playlist/37i9dQZF1FwLliIcKXtMsW", "37i9dQZF1FwLliIcKXtMsW"),
        ],
    )
    def test_accepts_bare_id_and_playlist_url(self, value, expected):
        assert spotify_module.parse_playlist_id(value) == expected

    def test_rejects_an_invalid_playlist_url(self):
        with pytest.raises(Failed, match="Invalid playlist URL"):
            spotify_module.parse_playlist_id("https://open.spotify.com/album/37i9dQZF1FwLliIcKXtMsW")

    def test_collects_all_paginated_playlist_tracks(self):
        requests = MagicMock()
        first_url = f"{spotify_module.api_url}/playlists/37i9dQZF1DXcBWIGoYBM5M/items"
        next_url = "https://api.spotify.com/v1/playlists/37i9dQZF1DXcBWIGoYBM5M/items?offset=1"
        requests.get_json.side_effect = [
            {"items": [{"item": {"id": "first"}}], "next": next_url},
            {"items": [{"item": {"id": "second"}}, {"item": None}], "next": None},
        ]
        spotify = Spotify.__new__(Spotify)
        spotify.requests = requests
        spotify.access_token = "access-token"

        assert spotify.get_playlist_tracks("37i9dQZF1DXcBWIGoYBM5M") == [{"id": "first"}, {"id": "second"}]
        assert requests.get_json.call_args_list[0].args == (first_url,)
        assert all(call.kwargs["headers"] == {"Authorization": "Bearer access-token"} for call in requests.get_json.call_args_list)

    def test_resolves_playlist_name_case_insensitively(self):
        requests = MagicMock()
        requests.get_json.return_value = {"items": [{"id": "37i9dQZF1DX4JAvHpjipBk", "name": "Release Radar"}], "next": None}
        spotify = Spotify.__new__(Spotify)
        spotify.requests = requests
        spotify.access_token = "access-token"

        assert spotify.resolve_playlist_id("release radar") == "37i9dQZF1DX4JAvHpjipBk"
        requests.get_json.assert_called_once_with(
            f"{spotify_module.api_url}/me/playlists",
            headers={"Authorization": "Bearer access-token"},
        )

    def test_rejects_duplicate_playlist_names(self):
        requests = MagicMock()
        requests.get_json.return_value = {
            "items": [
                {"id": "37i9dQZF1DX4JAvHpjipBk", "name": "Release Radar"},
                {"id": "37i9dQZF1DX7F6T2n2fegs", "name": "release radar"},
            ],
            "next": None,
        }
        spotify = Spotify.__new__(Spotify)
        spotify.requests = requests
        spotify.access_token = "access-token"

        with pytest.raises(Failed, match="More than one playlist"):
            spotify.resolve_playlist_id("Release Radar")

    def test_includes_spotify_error_message_in_failures(self):
        requests = MagicMock()
        requests.get_json.return_value = {"error": {"status": 403, "message": "Forbidden"}}
        spotify = Spotify.__new__(Spotify)
        spotify.requests = requests
        spotify.access_token = "access-token"

        with pytest.raises(Failed, match="403: Forbidden"):
            spotify.get_liked_tracks()

    def test_collects_liked_tracks(self):
        requests = MagicMock()
        requests.get_json.return_value = {"items": [{"track": {"id": "liked"}}], "next": None}
        spotify = Spotify.__new__(Spotify)
        spotify.requests = requests
        spotify.access_token = "access-token"

        assert spotify.get_liked_tracks() == [{"id": "liked"}]
        requests.get_json.assert_called_once_with(
            f"{spotify_module.api_url}/me/tracks",
            headers={"Authorization": "Bearer access-token"},
        )

    def test_collects_top_tracks(self):
        requests = MagicMock()
        requests.get_json.return_value = {"items": [{"id": "top-track"}], "next": None}
        spotify = Spotify.__new__(Spotify)
        spotify.requests = requests
        spotify.access_token = "access-token"

        assert spotify.get_top_tracks("short") == [{"id": "top-track"}]
        requests.get_json.assert_called_once_with(
            f"{spotify_module.api_url}/me/top/tracks?time_range=short_term&limit=50",
            headers={"Authorization": "Bearer access-token"},
        )

    def test_collects_recent_tracks(self):
        requests = MagicMock()
        requests.get_json.return_value = {"items": [{"track": {"id": "recent-track"}}], "next": None}
        spotify = Spotify.__new__(Spotify)
        spotify.requests = requests
        spotify.access_token = "access-token"

        assert spotify.get_recent_tracks() == [{"id": "recent-track"}]
        requests.get_json.assert_called_once_with(
            f"{spotify_module.api_url}/me/player/recently-played?limit=50",
            headers={"Authorization": "Bearer access-token"},
        )

    def test_collects_saved_albums(self):
        requests = MagicMock()
        requests.get_json.return_value = {"items": [{"album": {"id": "saved-album", "name": "Saved Album"}}], "next": None}
        spotify = Spotify.__new__(Spotify)
        spotify.requests = requests
        spotify.access_token = "access-token"

        assert spotify.get_saved_albums() == [{"id": "saved-album", "name": "Saved Album"}]
        requests.get_json.assert_called_once_with(
            f"{spotify_module.api_url}/me/albums",
            headers={"Authorization": "Bearer access-token"},
        )

    def test_gets_playlist_description_and_artwork(self):
        requests = MagicMock()
        requests.get_json.side_effect = [
            {"description": "A playlist", "images": [{"url": "https://image.example/old-cover.jpg"}]},
            [{"url": "https://image.example/custom-cover.jpg"}],
        ]
        spotify = Spotify.__new__(Spotify)
        spotify.requests = requests
        spotify.access_token = "access-token"

        details = spotify.get_playlist_details("37i9dQZF1FwLliIcKXtMsW")
        assert details["description"] == "A playlist"
        assert details["images"] == [{"url": "https://image.example/custom-cover.jpg"}]
        assert requests.get_json.call_args_list == [
            ((f"{spotify_module.api_url}/playlists/37i9dQZF1FwLliIcKXtMsW",), {"headers": {"Authorization": "Bearer access-token"}}),
            ((f"{spotify_module.api_url}/playlists/37i9dQZF1FwLliIcKXtMsW/images",), {"headers": {"Authorization": "Bearer access-token"}}),
        ]

    def test_resolves_spotify_track_to_a_local_plex_track(self):
        spotify_client = MagicMock()
        spotify_client.get_playlist_tracks.return_value = [
            {
                "name": "Fame Is a Gun",
                "artists": [{"name": "Addison Rae"}],
                "album": {"name": "Addison"},
                "disc_number": 1,
                "track_number": 9,
                "duration_ms": 183264,
            }
        ]
        library = SimpleNamespace(find_music_track_rating_keys=MagicMock(return_value=[11458]))
        builder = CollectionBuilder.__new__(CollectionBuilder)
        builder.library = library
        builder.config = SimpleNamespace(Spotify=spotify_client)

        assert builder._spotify_rating_keys("spotify_list", "37i9dQZF1FwLliIcKXtMsW") == [(11458, "ratingKey")]
        spotify_client.get_playlist_tracks.assert_called_once_with("37i9dQZF1FwLliIcKXtMsW")
        library.find_music_track_rating_keys.assert_called_once_with("Fame Is a Gun", ["Addison Rae"], "Addison", 1, 9, 183264)

    def test_resolves_liked_tracks(self):
        spotify_client = MagicMock()
        spotify_client.get_liked_tracks.return_value = []
        builder = CollectionBuilder.__new__(CollectionBuilder)
        builder.library = SimpleNamespace(find_music_track_rating_keys=MagicMock())
        builder.config = SimpleNamespace(Spotify=spotify_client)

        assert builder._spotify_rating_keys("spotify_liked", "me") == []
        spotify_client.get_liked_tracks.assert_called_once_with()

    @pytest.mark.parametrize(
        ("method", "value"),
        [("spotify_top", "short"), ("spotify_top", "medium"), ("spotify_top", "long"), ("spotify_recent", "me"), ("spotify_saved", "me")],
    )
    def test_accepts_new_spotify_builder_values(self, method, value):
        builder = CollectionBuilder.__new__(CollectionBuilder)
        builder.builders = []

        builder._spotify(method, value)

        assert builder.builders == [(method, value)]

    @pytest.mark.parametrize(
        ("method", "value", "spotify_method"),
        [
            ("spotify_top", "short", "get_top_tracks"),
            ("spotify_recent", "me", "get_recent_tracks"),
            ("spotify_saved", "me", "get_saved_albums"),
        ],
    )
    def test_resolves_new_spotify_track_builders(self, method, value, spotify_method):
        spotify_client = MagicMock()
        getattr(spotify_client, spotify_method).return_value = []
        builder = CollectionBuilder.__new__(CollectionBuilder)
        builder.library = SimpleNamespace(find_music_track_rating_keys=MagicMock())
        builder.config = SimpleNamespace(Spotify=spotify_client)

        assert builder._spotify_rating_keys(method, value) == []
        getattr(spotify_client, spotify_method).assert_called_once_with(*((value,) if method == "spotify_top" else ()))

    def test_resolves_saved_spotify_album_to_a_local_plex_album(self):
        spotify_client = MagicMock()
        spotify_client.get_saved_albums.return_value = [{"name": "After Hours", "artists": [{"name": "The Weeknd"}]}]
        library = SimpleNamespace(find_music_album_rating_keys=MagicMock(return_value=[1986]))
        builder = CollectionBuilder.__new__(CollectionBuilder)
        builder.library = library
        builder.config = SimpleNamespace(Spotify=spotify_client)
        builder.missing_albums = []

        assert builder._spotify_rating_keys("spotify_saved", "me") == [(1986, "ratingKey")]
        library.find_music_album_rating_keys.assert_called_once_with("After Hours", ["The Weeknd"])
        assert builder.missing_albums == []

    def test_collects_unmatched_track_with_artist_and_title(self):
        spotify_client = MagicMock()
        spotify_client.get_playlist_tracks.return_value = [{"name": "Rolling in the Deep", "artists": [{"name": "Adele"}]}]
        library = SimpleNamespace(find_music_track_rating_keys=MagicMock(return_value=[]))
        builder = CollectionBuilder.__new__(CollectionBuilder)
        builder.library = library
        builder.config = SimpleNamespace(Spotify=spotify_client)
        builder.missing_tracks = []

        assert builder._spotify_rating_keys("spotify_list", "playlist-id") == []
        assert builder.missing_tracks == ["Adele - Rolling in the Deep"]

    def test_list_details_registers_the_list_and_collection_metadata(self):
        spotify_client = MagicMock()
        spotify_client.resolve_playlist_id.return_value = "37i9dQZF1FwLliIcKXtMsW"
        spotify_client.get_playlist_details.return_value = {"description": "A playlist", "images": [{"url": "https://image.example/cover.jpg"}]}
        builder = CollectionBuilder.__new__(CollectionBuilder)
        builder.builders = []
        builder.summaries = {}
        builder.posters = {}
        builder.config = SimpleNamespace(Spotify=spotify_client)

        builder._spotify("spotify_list_details", "37i9dQZF1FwLliIcKXtMsW")

        assert builder.builders == [("spotify_list", "37i9dQZF1FwLliIcKXtMsW")]
        assert builder.summaries["spotify_list_details"] == "A playlist\n\nSource: Spotify (https://open.spotify.com/playlist/37i9dQZF1FwLliIcKXtMsW)"
        assert builder.posters["spotify_list_details"] == "https://image.example/cover.jpg"
