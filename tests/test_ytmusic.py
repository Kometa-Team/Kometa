import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from jsonschema import Draft7Validator

from modules import builder as builder_module
from modules import meta as meta_module
from modules import ytmusic as ytmusic_module
from modules.builder import CollectionBuilder
from modules.util import BuilderValidationError, Failed
from modules.ytmusic import YouTubeMusic, playlist_id


def plex_track(artist, album, title, rating_key, duration):
    return SimpleNamespace(grandparentTitle=artist, parentTitle=album, title=title, ratingKey=rating_key, duration=duration, guids=[])


def playlist_track(artist, album, title, duration):
    return {"title": title, "artists": [{"name": artist}], "album": {"name": album} if album else None, "duration_seconds": duration}


def test_playlist_url_and_id_validation():
    assert playlist_id("PLC7LNuBoMA-o") == "PLC7LNuBoMA-o"
    assert playlist_id("https://music.youtube.com/playlist?list=PLC7LNuBoMA-o&si=example") == "PLC7LNuBoMA-o"
    for value in ("https://example.com/playlist?list=PLC7LNuBoMA-o", "https://music.youtube.com/watch?v=abc", "https://music.youtube.com/playlist", "bad id"):
        with pytest.raises(Failed):
            playlist_id(value)


def test_playlist_matches_tracks_in_order_and_reports_missing():
    library = SimpleNamespace(is_music=True, get_all=Mock(return_value=[plex_track("First Artist", "Album A", "First Song", 1, 180500), plex_track("Second Artist", "Album B", "Second Song", 2, 210000)]))
    connector = YouTubeMusic()
    connector.client = Mock()
    connector.client.get_playlist.return_value = {
        "tracks": [
            playlist_track("Second Artist", "Different Album", "Second Song", 210),
            playlist_track("First Artist", "Album A", "First Song", 180),
            playlist_track("Second Artist", "Album B", "Second Song", 210),
            playlist_track("Missing Artist", None, "Missing Song", 200),
        ]
    }

    result = connector.get_rating_keys("PLC7LNuBoMA-o", library)

    assert result[:2] == [(2, "ratingKey"), (1, "ratingKey")]
    assert result[2][1] == "music_missing"
    assert json.loads(result[2][0])["name"] == "Missing Song"
    connector.client.get_playlist.assert_called_once_with("PLC7LNuBoMA-o", limit=None)


def test_duration_precedes_album_and_secondary_artist_can_match():
    library = SimpleNamespace(is_music=True, get_all=Mock(return_value=[plex_track("Primary", "Album A", "Song", 1, 250000), plex_track("Guest", "Album B", "Song", 2, 180000)]))
    connector = YouTubeMusic()
    connector.client = Mock()
    connector.client.get_playlist.return_value = {"tracks": [{"title": "Song", "artists": [{"name": "Primary"}, {"name": "Guest"}], "album": {"name": "Album A"}, "duration_seconds": 180}]}

    assert connector.get_rating_keys("PLC7LNuBoMA-o", library) == [(2, "ratingKey")]


def test_album_then_unique_artist_title_fallback_and_ambiguous_missing():
    library = SimpleNamespace(is_music=True, get_all=Mock(return_value=[plex_track("Artist", "First Album", "Repeated", 1, 180000), plex_track("Artist", "Second Album", "Repeated", 2, 240000), plex_track("Artist", "Only Album", "Unique", 3, 200000)]))
    connector = YouTubeMusic()
    connector.client = Mock()
    connector.client.get_playlist.return_value = {"tracks": [playlist_track("Artist", "Second Album", "Repeated", None), playlist_track("Artist", None, "Unique", None), playlist_track("Artist", None, "Repeated", None)]}

    results = connector.get_rating_keys("PLC7LNuBoMA-o", library)

    assert results[:2] == [(2, "ratingKey"), (3, "ratingKey")]
    assert json.loads(results[2][0])["reason"] == "ambiguous"


def test_invalid_playlist_response_is_reported():
    connector = YouTubeMusic()
    connector.client = Mock()
    connector.client.get_playlist.return_value = {"title": "No tracks"}
    with pytest.raises(Failed, match="did not return tracks"):
        connector.get_rating_keys("PLC7LNuBoMA-o", SimpleNamespace(is_music=True))


def test_builder_validates_track_level_and_supports_custom_order():
    builder = CollectionBuilder.__new__(CollectionBuilder)
    builder.Type = "Collection"
    builder.builder_level = "track"
    builder.builders = []
    builder.config = SimpleNamespace(YouTubeMusic=Mock(playlist_metadata=Mock(return_value=(None, None))))
    builder.summaries = {}
    builder.posters = {}
    builder._ytmusic("ytmusic_list", ["PLC7LNuBoMA-o", "https://music.youtube.com/playlist?list=PLSecond"])
    assert builder.builders == [("ytmusic_list", "PLC7LNuBoMA-o"), ("ytmusic_list", "PLSecond")]
    assert "ytmusic_list" in builder_module.custom_sort_builders
    assert "ytmusic_list" in builder_module.parts_collection_valid
    assert "ytmusic_top_artists" in builder_module.custom_sort_builders
    assert "ytmusic_top_artists" in builder_module.parts_collection_valid
    assert "ytmusic_charts" not in builder_module.all_builders
    assert builder_module._default_music_level({"ytmusic_list": "ytmusic_list"}) == "track"
    builder.builder_level = "artist"
    with pytest.raises(BuilderValidationError, match="track-level"):
        builder._ytmusic("ytmusic_list", "PLC7LNuBoMA-o")


def test_top_artists_builder_country_and_level():
    builder = CollectionBuilder.__new__(CollectionBuilder)
    builder.Type = "Collection"
    builder.builder_level = "artist"
    builder.builders = []
    builder._ytmusic("ytmusic_top_artists", [True, {"country": "us"}, "global"])
    assert builder.builders == [("ytmusic_top_artists", "ZZ"), ("ytmusic_top_artists", "US"), ("ytmusic_top_artists", "ZZ")]
    assert builder_module._default_music_level({"ytmusic_top_artists": True}) == "artist"
    with pytest.raises(BuilderValidationError):
        builder._ytmusic("ytmusic_top_artists", {"country": "USA"})
    builder.builder_level = "track"
    with pytest.raises(BuilderValidationError, match="artist-level"):
        builder._ytmusic("ytmusic_top_artists", True)


def test_top_artists_matches_unique_names_and_reports_missing():
    library = SimpleNamespace(is_music=True, get_all=Mock(return_value=[SimpleNamespace(title="Artist One", ratingKey=1, guids=[])]))
    connector = YouTubeMusic()
    connector.client = Mock()
    connector.client.get_charts.return_value = {"artists": [{"title": "Artist One", "browseId": "UC1"}, {"title": "Artist Two", "browseId": "UC2"}]}
    result = connector.get_top_artists("US", library)
    assert result[0] == (1, "ratingKey")
    assert result[1][1] == "music_missing"
    assert json.loads(result[1][0])["artist"] == "Artist Two"
    connector.client.get_charts.assert_called_once_with(country="US")


def test_top_artists_falls_back_when_country_chart_contains_albums():
    library = SimpleNamespace(is_music=True, get_all=Mock(return_value=[]))
    connector = YouTubeMusic()
    connector.client = Mock()
    connector.client.get_charts.side_effect = [
        {"artists": [{"title": "Wrong Album", "browseId": "MPREb_album"}]},
        {"artists": [{"title": "Drake", "browseId": "UCU6cE7pdJPc6DU2jSrKEsdQ"}]},
    ]

    result = connector.get_top_artists("US", library)

    assert json.loads(result[0][0])["artist"] == "Drake"
    assert [call.kwargs for call in connector.client.get_charts.call_args_list] == [{"country": "US"}, {"country": "ZZ"}]


def test_top_artists_rejects_non_artist_browse_ids():
    library = SimpleNamespace(is_music=True, get_all=Mock(return_value=[]))
    connector = YouTubeMusic()
    connector.client = Mock()
    connector.client.get_charts.return_value = {"artists": [{"title": "Album", "browseId": "MPREb_album"}]}

    with pytest.raises(Failed, match="artist charts are unavailable"):
        connector.get_top_artists("ZZ", library)


def test_dynamic_chart_sections_and_unavailable_section():
    connector = YouTubeMusic()
    connector.client = Mock()
    connector.client.get_charts.return_value = {"videos": [{"title": "Top Songs", "playlistId": "PLTop"}]}
    assert connector.chart_playlists("ZZ", "videos")[0]["playlistId"] == "PLTop"
    with pytest.raises(Failed, match="Available sections: videos"):
        connector.chart_playlists("ZZ", "genres")
    assert set(ytmusic_module.chart_sections) == {"videos", "genres", "languages"}
    assert "ytmusic_genre_charts" in meta_module.auto["Artist"]


def test_list_builder_supports_limit_for_dynamic_charts():
    builder = CollectionBuilder.__new__(CollectionBuilder)
    builder.Type = "Collection"
    builder.builder_level = "track"
    builder.builders = []
    builder.summaries = {}
    builder.posters = {}
    builder.config = SimpleNamespace(YouTubeMusic=Mock(playlist_metadata=Mock(return_value=(None, None))))
    builder._ytmusic("ytmusic_list", {"playlist": "PLTop", "limit": 25})
    assert builder.builders == [("ytmusic_list", {"playlist": "PLTop", "limit": 25})]
    connector = YouTubeMusic()
    connector.client = Mock()
    connector.client.get_playlist.return_value = {"tracks": []}
    assert connector.get_rating_keys(builder.builders[0][1], SimpleNamespace(is_music=True, get_all=Mock(return_value=[]))) == []
    connector.client.get_playlist.assert_called_once_with("PLTop", limit=25)


def test_playlist_metadata_uses_description_and_largest_cover():
    connector = YouTubeMusic()
    connector.client = Mock()
    connector.client.get_playlist.return_value = {"description": "  Official Pop chart  ", "thumbnails": [{"url": "https://example.com/small.jpg", "width": 100, "height": 100}, {"url": "https://example.com/large.jpg", "width": 500, "height": 500}]}
    assert connector.playlist_metadata("PLPop") == ("Official Pop chart", "https://example.com/large.jpg")
    connector.client.get_playlist.assert_called_once_with("PLPop", limit=0)


def test_list_builder_applies_available_metadata():
    builder = CollectionBuilder.__new__(CollectionBuilder)
    builder.Type = "Collection"
    builder.builder_level = "track"
    builder.builders = []
    builder.summaries = {}
    builder.posters = {}
    builder.config = SimpleNamespace(YouTubeMusic=Mock(playlist_metadata=Mock(return_value=("Chart description", "https://example.com/cover.jpg"))))
    builder._ytmusic("ytmusic_list", "PLPop")
    assert builder.summaries["ytmusic_list"] == "Chart description"
    assert builder.posters["ytmusic_list"] == "https://example.com/cover.jpg"


def test_connector_uses_public_ytmusicapi_client(monkeypatch):
    client = Mock()
    constructor = Mock(return_value=client)
    monkeypatch.setattr(ytmusic_module, "YTMusic", constructor)
    connector = YouTubeMusic()
    assert connector.client is client
    constructor.assert_called_once_with()


def test_artist_image_requires_exact_match_and_uses_monthly_listeners_for_duplicates():
    connector = YouTubeMusic()
    connector.client = Mock()
    connector.client.search.return_value = [
        {"artist": "Same Artist", "browseId": "UC1"},
        {"artist": "Same Artist", "browseId": "UC2"},
        {"artist": "Same Artist (Live)", "browseId": "UC3"},
    ]
    connector.client.get_artist.side_effect = [
        {"name": "Same Artist", "monthlyListeners": "900K", "thumbnails": [{"url": "https://example.com/less-popular.jpg", "width": 500, "height": 500}]},
        {"name": "Same Artist", "monthlyListeners": "10M", "thumbnails": [{"url": "https://example.com/more-popular.jpg", "width": 1000, "height": 1000}]},
    ]

    assert connector.artist_image_url("Same Artist") == "https://example.com/more-popular.jpg"
    assert connector.client.search.call_args.args == ("Same Artist",)
    assert connector.client.search.call_args.kwargs == {"filter": "artists", "limit": 20, "ignore_spelling": True}
    assert connector.client.get_artist.call_count == 2


def test_artist_image_uses_public_thumbnail_for_single_exact_match():
    connector = YouTubeMusic()
    connector.client = Mock()
    connector.client.search.return_value = [
        {
            "artist": "Exact Artist",
            "browseId": "UC1",
            "thumbnails": [
                {"url": "https://example.com/profile.jpg", "width": 500, "height": 500},
                {"url": "https://example.com/banner.jpg", "width": 1600, "height": 900},
            ],
        }
    ]

    assert connector.artist_image_url("Exact Artist") == "https://example.com/profile.jpg"
    assert connector.artist_image_url("Exact Artist", background=True) == "https://example.com/banner.jpg"
    connector.client.get_artist.assert_not_called()


def test_artist_image_matches_unicode_dash_variants():
    connector = YouTubeMusic()
    connector.client = Mock()
    connector.client.search.return_value = [
        {
            "artist": "Sophie Ellis-Bextor",
            "browseId": "UC1",
            "thumbnails": [{"url": "https://example.com/profile.jpg", "width": 500, "height": 500}],
        }
    ]

    assert connector.artist_image_url("Sophie Ellis‐Bextor") == "https://example.com/profile.jpg"


def test_artist_image_requests_high_resolution_youtube_thumbnails():
    connector = YouTubeMusic()
    connector.client = Mock()
    connector.client.search.return_value = [
        {
            "artist": "Exact Artist",
            "browseId": "UC1",
            "thumbnails": [
                {"url": "https://lh3.googleusercontent.com/profile=w60-h60-l90-rj", "width": 500, "height": 500},
                {"url": "https://yt3.ggpht.com/banner=s88-c-k-c0x00ffffff-no-rj", "width": 1600, "height": 900},
            ],
        }
    ]

    assert connector.artist_image_url("Exact Artist") == "https://lh3.googleusercontent.com/profile=w1200-h1200-l90-rj"
    assert connector.artist_image_url("Exact Artist", background=True) == "https://yt3.ggpht.com/banner=s1920-c-k-c0x00ffffff-no-rj"


def test_artist_image_handles_unsupported_artist_page_layout(monkeypatch):
    logger = Mock()
    monkeypatch.setattr(ytmusic_module, "logger", logger)
    connector = YouTubeMusic()
    connector.client = Mock()
    connector.client.search.return_value = [{"artist": "Blondie", "browseId": "UC1"}]
    connector.client.get_artist.side_effect = KeyError("Unable to find 'twoColumnBrowseResultsRenderer' in response payload")

    assert connector.artist_image_url("Blondie") is None
    warning = logger.warning.call_args.args[0]
    assert "artist details unavailable for Blondie" in warning
    assert "unsupported artist page layout" in warning
    assert "response payload" not in warning


def test_artist_image_skips_non_exact_or_unranked_duplicate_matches(monkeypatch):
    monkeypatch.setattr(ytmusic_module, "logger", Mock())
    connector = YouTubeMusic()
    connector.client = Mock()
    connector.client.search.return_value = [{"artist": "Artist Name (Live)", "browseId": "UC1"}]
    assert connector.artist_image_url("Artist Name") is None
    connector.client.get_artist.assert_not_called()

    connector.artist_image_cache.clear()
    connector.client.search.return_value = [{"artist": "Artist Name", "browseId": "UC1"}, {"artist": "Artist Name", "browseId": "UC2"}]
    connector.client.get_artist.side_effect = [
        {"name": "Artist Name", "thumbnails": [{"url": "https://example.com/one.jpg", "width": 500, "height": 500}]},
        {"name": "Artist Name", "thumbnails": [{"url": "https://example.com/two.jpg", "width": 500, "height": 500}]},
    ]
    assert connector.artist_image_url("Artist Name") is None


def test_ytmusic_schema_accepts_connector_and_list():
    root = Path(__file__).resolve().parents[1] / "json-schema"
    config_schema = json.loads((root / "config-schema.json").read_text(encoding="utf-8"))
    collection_schema = json.loads((root / "collection-schema.json").read_text(encoding="utf-8"))
    Draft7Validator.check_schema(config_schema)
    Draft7Validator.check_schema(collection_schema)
    Draft7Validator(config_schema).validate({"plex": {"url": "https://plex.example", "token": "token"}, "tmdb": {"apikey": "key"}, "ytmusic": {}})
    Draft7Validator(config_schema).validate({"plex": {"url": "https://plex.example", "token": "token"}, "tmdb": {"apikey": "key"}, "libraries": {"Music": {"operations": {"mass_poster_update": {"source": "ytmusic"}}}}})
    assert not Draft7Validator(config_schema).is_valid({"plex": {"url": "https://plex.example", "token": "token"}, "tmdb": {"apikey": "key"}, "ytmusic": {"auth": "browser.json"}})
    Draft7Validator(config_schema).validate({"plex": {"url": "https://plex.example", "token": "token"}, "tmdb": {"apikey": "key"}, "ytmusic": {}, "libraries": {"Music": {"operations": {"mass_poster_update": {"source": "ytmusic"}}}}})
    Draft7Validator(config_schema).validate({"plex": {"url": "https://plex.example", "token": "token"}, "tmdb": {"apikey": "key"}, "ytmusic": {}, "libraries": {"Music": {"operations": {"mass_background_update": {"source": "ytmusic"}}}}})
    Draft7Validator(config_schema).validate({"plex": {"url": "https://plex.example", "token": "token"}, "tmdb": {"apikey": "key"}, "ytmusic": {}, "libraries": {"Music": {"operations": {"mass_image_update": {"background": "ytmusic"}}}}})
    Draft7Validator(collection_schema).validate({"collections": {"Playlist": {"ytmusic_list": "PLC7LNuBoMA-o", "collection_order": "custom"}}})
    Draft7Validator(collection_schema).validate({"collections": {"Chart": {"ytmusic_top_artists": {"country": "US"}, "collection_order": "custom"}}})
    assert not Draft7Validator(collection_schema).is_valid({"collections": {"Chart": {"ytmusic_charts": {"country": "US"}}}})
    Draft7Validator(collection_schema).validate({"dynamic_collections": {"Genre Charts": {"type": "ytmusic_genre_charts", "data": {"country": "US", "limit": 50}}}})
