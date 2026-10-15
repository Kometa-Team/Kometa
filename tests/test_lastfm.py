import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, call

import pylast
import pytest
from jsonschema import Draft7Validator, ValidationError

from modules import builder as builder_module
from modules import lastfm, util
from modules.builder import CollectionBuilder
from modules.lastfm import LastFM
from modules.library import Library
from modules.util import BuilderValidationError, Failed


@pytest.fixture(autouse=True)
def mock_logger(monkeypatch):
    monkeypatch.setattr(lastfm, "logger", Mock())


def plex_artist(name, rating_key, *mbids):
    return SimpleNamespace(title=name, ratingKey=rating_key, guids=[SimpleNamespace(id=f"mbid://{mbid}") for mbid in mbids])


def chart_artist(name, mbid):
    return SimpleNamespace(item=SimpleNamespace(get_name=lambda: name, get_mbid=lambda: mbid))


def plex_album(artist, title, rating_key, *mbids):
    return SimpleNamespace(parentTitle=artist, title=title, ratingKey=rating_key, guids=[SimpleNamespace(id=f"mbid://{mbid}") for mbid in mbids])


def chart_album(artist, title, mbid):
    return SimpleNamespace(item=SimpleNamespace(get_name=lambda: title, get_artist=lambda: SimpleNamespace(get_name=lambda: artist), get_mbid=lambda: mbid))


def plex_track(artist, album, title, rating_key, *mbids, duration=0):
    return SimpleNamespace(grandparentTitle=artist, parentTitle=album, title=title, ratingKey=rating_key, duration=duration, guids=[SimpleNamespace(id=f"mbid://{mbid}") for mbid in mbids])


def chart_track(artist, album, title, mbid, duration=0):
    track = Mock()
    track.get_name.return_value = title
    track.get_artist.return_value.get_name.return_value = artist
    track.get_mbid.return_value = mbid
    track.get_album.return_value = SimpleNamespace(get_name=lambda: album) if album else None
    track.get_duration.return_value = duration
    return SimpleNamespace(item=track)


def test_top_artists_match_mbid_then_unique_name_without_lidarr():
    mbid = "9c9f1380-2516-4fc9-a3e6-f9f61941d090"
    plex_artists = [plex_artist("Different name", 10, mbid), plex_artist("Name only", 20), plex_artist("Fallback name", 50), plex_artist("Duplicate", 30), plex_artist("Duplicate", 40)]
    library = SimpleNamespace(name="Music", is_music=True, get_all=Mock(return_value=plex_artists))
    network = Mock()
    network.get_user.return_value.get_top_artists.return_value = [
        chart_artist("Last.fm name", mbid.upper()),
        chart_artist("Name only", None),
        chart_artist("Duplicate", "a740310b-3e15-4ffb-a77b-9f40bcf3e821"),
        chart_artist("Fallback name", "d6ef62f2-8b1c-45f2-8bac-123456789abc"),
    ]
    connector = LastFM("test-key")
    connector.network = network

    results = connector.get_rating_keys("lastfm_user_top_artists", {"username": "listener", "period": "1month", "limit": 50}, library)
    assert results[:2] == [(10, "ratingKey"), (20, "ratingKey")]
    assert json.loads(results[2][0]) == {"name": "Duplicate", "mbid": "a740310b-3e15-4ffb-a77b-9f40bcf3e821", "reason": "ambiguous"}
    assert results[3] == (50, "ratingKey")
    lastfm.logger.info.assert_not_called()
    network.get_user.return_value.get_top_artists.assert_called_once_with(period="1month", limit=50)


def test_top_artists_support_custom_order():
    assert "lastfm_user_top_artists" in builder_module.custom_sort_builders
    plex_artists = [plex_artist("Second", 20), plex_artist("First", 10)]
    library = SimpleNamespace(is_music=True, get_all=Mock(return_value=plex_artists))
    connector = LastFM("test-key")
    connector.network = Mock()
    connector.network.get_user.return_value.get_top_artists.return_value = [chart_artist("First", None), chart_artist("Second", None)]

    assert connector.get_rating_keys("lastfm_user_top_artists", {"username": "listener", "period": "overall", "limit": 2}, library) == [(10, "ratingKey"), (20, "ratingKey")]


def test_top_albums_match_release_id_then_unique_artist_and_title_in_chart_order():
    release_mbid = "f20971f2-c8ad-4d26-91ab-730f6dedafb2"
    plex_albums = [
        plex_album("Dream Theater", "Images and Words", 20, "ee30c026-b4f4-3e2a-94cf-7e586f1ccae0"),
        plex_album("Beyoncé", "Lemonade", 10, "ec3d3ed8-5f39-4ff7-8927-c8477ff16370"),
        plex_album("Other Artist", "Images and Words", 30),
        plex_album("Dream Theater", "Ambiguous", 40),
        plex_album("Dream Theater", "Ambiguous", 50),
    ]
    library = SimpleNamespace(is_music=True, get_all=Mock(return_value=plex_albums))
    connector = LastFM("test-key")
    connector.network = Mock()
    connector.network.get_user.return_value.get_top_albums.return_value = [
        chart_album("Beyoncé", "Lemonade", "ec3d3ed8-5f39-4ff7-8927-c8477ff16370"),
        chart_album("Dream Theater", "Images and Words", release_mbid),
        chart_album("Dream Theater", "Ambiguous", None),
    ]

    results = connector.get_rating_keys("lastfm_user_top_albums", {"username": "listener", "period": "overall", "limit": 3}, library)
    assert results[:2] == [(10, "ratingKey"), (20, "ratingKey")]
    assert json.loads(results[2][0]) == {"artist": "Dream Theater", "name": "Ambiguous", "mbid": "", "reason": "ambiguous"}
    assert results[2][1] == "lastfm_album_missing"
    connector.network.get_user.return_value.get_top_albums.assert_called_once_with(period="overall", limit=3)


def test_top_tracks_use_id_then_unique_artist_album_and_title():
    mbid = "be191a11-c480-4240-8baa-6c4be0f8d400"
    plex_tracks = [plex_track("Alannah Myles", "Alannah Myles", "Black Velvet", 10, mbid), plex_track("Alannah Myles", "Greatest Hits", "Black Velvet", 20), plex_track("Other", "Other Album", "Missing", 30)]
    library = SimpleNamespace(is_music=True, get_all=Mock(return_value=plex_tracks))
    connector = LastFM("test-key")
    connector.network = Mock()
    id_match = chart_track("Different Name", None, "Other Title", mbid)
    title_match = chart_track("Alannah Myles", "Greatest Hits", "Black Velvet", None)
    no_album = chart_track("Alannah Myles", None, "Black Velvet", None)
    connector.network.get_user.return_value.get_top_tracks.return_value = [id_match, title_match, no_album]

    results = connector.get_rating_keys("lastfm_user_top_tracks", {"username": "listener", "period": "1month", "limit": 3}, library)

    assert results[:2] == [(10, "ratingKey"), (20, "ratingKey")]
    id_match.item.get_album.assert_not_called()
    assert results[2][1] == "music_missing"
    assert json.loads(results[2][0]) == {"level": "track", "artist": "Alannah Myles", "album": None, "name": "Black Velvet", "mbid": "", "reason": "not found"}
    connector.network.get_user.return_value.get_top_tracks.assert_called_once_with(period="1month", limit=3)


def test_top_tracks_can_match_unique_artist_title_and_close_duration():
    plex_tracks = [plex_track("Alannah Myles", "Alannah Myles", "Black Velvet", 10, duration=287477), plex_track("Alannah Myles", "Greatest Hits", "Black Velvet", 20, duration=305000)]
    library = SimpleNamespace(is_music=True, get_all=Mock(return_value=plex_tracks))
    connector = LastFM("test-key")
    connector.network = Mock()
    connector.network.get_user.return_value.get_top_tracks.return_value = [chart_track("Alannah Myles", None, "Black Velvet", None, duration=288000)]

    assert connector.get_rating_keys("lastfm_user_top_tracks", {"username": "listener", "period": "overall", "limit": 1}, library) == [(10, "ratingKey")]


def test_top_tracks_prefer_duration_match_over_lastfm_album():
    plex_tracks = [plex_track("Alannah Myles", "Alannah Myles", "Black Velvet", 10, duration=287477), plex_track("Alannah Myles", "Greatest Hits", "Black Velvet", 20, duration=305000)]
    library = SimpleNamespace(is_music=True, get_all=Mock(return_value=plex_tracks))
    connector = LastFM("test-key")
    connector.network = Mock()
    chart = chart_track("Alannah Myles", "Greatest Hits", "Black Velvet", None, duration=288000)
    connector.network.get_user.return_value.get_top_tracks.return_value = [chart]

    assert connector.get_rating_keys("lastfm_user_top_tracks", {"username": "listener", "period": "overall", "limit": 1}, library) == [(10, "ratingKey")]
    chart.item.get_album.assert_not_called()


def test_loved_tracks_keep_newest_order_and_deduplicate():
    mbid = "be191a11-c480-4240-8baa-6c4be0f8d400"
    library = SimpleNamespace(is_music=True, get_all=Mock(return_value=[plex_track("Alannah Myles", "Alannah Myles", "Black Velvet", 10, mbid), plex_track("Other", "Album", "Song", 20)]))
    connector = LastFM("test-key")
    connector.network = Mock()
    loved = [
        SimpleNamespace(track=chart_track("Alannah Myles", None, "Black Velvet", mbid).item),
        SimpleNamespace(track=chart_track("Other", "Album", "Song", None).item),
        SimpleNamespace(track=chart_track("Alannah Myles", None, "Black Velvet", mbid).item),
    ]
    connector.network.get_user.return_value.get_loved_tracks.return_value = loved

    assert connector.get_rating_keys("lastfm_user_loved_tracks", {"username": "listener", "limit": 3}, library) == [(10, "ratingKey"), (20, "ratingKey")]
    connector.network.get_user.return_value.get_loved_tracks.assert_called_once_with(limit=3)


def test_recent_tracks_use_scrobble_album_after_duration_and_report_missing():
    library = SimpleNamespace(is_music=True, get_all=Mock(return_value=[plex_track("Alannah Myles", "Greatest Hits", "Black Velvet", 10), plex_track("Alannah Myles", "Alannah Myles", "Black Velvet", 20)]))
    connector = LastFM("test-key")
    connector.network = Mock()
    recent = [SimpleNamespace(track=chart_track("Alannah Myles", None, "Black Velvet", None).item, album="Greatest Hits"), SimpleNamespace(track=chart_track("Other", None, "Missing", None).item, album=None)]
    connector.network.get_user.return_value.get_recent_tracks.return_value = recent

    result = connector.get_rating_keys("lastfm_user_recent_tracks", {"username": "listener", "limit": 2, "from": 100, "to": 200}, library)

    assert result[0] == (10, "ratingKey")
    assert result[1][1] == "music_missing"
    assert json.loads(result[1][0])["name"] == "Missing"
    connector.network.get_user.return_value.get_recent_tracks.assert_called_once_with(limit=2, time_from=100, time_to=200, cacheable=False)


@pytest.mark.parametrize("method,level", [("lastfm_user_tags", "artist"), ("lastfm_user_tags", "album"), ("lastfm_user_tags", "track"), ("lastfm_tag_charts", "artist"), ("lastfm_tag_charts", "album"), ("lastfm_tag_charts", "track")])
def test_tag_builders_match_all_music_levels(method, level):
    item = {"artist": plex_artist("ABBA", 10), "album": plex_album("ABBA", "Gold", 10), "track": plex_track("ABBA", "Gold", "Dancing Queen", 10)}[level]
    source = {"artist": chart_artist("ABBA", None).item, "album": chart_album("ABBA", "Gold", None).item, "track": chart_track("ABBA", "Gold", "Dancing Queen", None).item}[level]
    library = SimpleNamespace(is_music=True, get_all=Mock(return_value=[item]))
    connector = LastFM("test-key")
    connector.network = Mock()
    getter_name = {"artist": "artists", "album": "albums", "track": "tracks"}[level]
    if method == "lastfm_user_tags":
        getter = getattr(connector.network.get_user.return_value, f"get_tagged_{getter_name}")
        getter.return_value = [source]
        value = {"username": "listener", "tag": "pop", "level": level, "limit": 5}
    else:
        getter = getattr(connector.network.get_tag.return_value, f"get_top_{getter_name}")
        getter.return_value = [SimpleNamespace(item=source)]
        value = {"tag": "pop", "level": level, "limit": 5}

    assert connector.get_rating_keys(method, value, library) == [(10, "ratingKey")]
    if method == "lastfm_user_tags":
        getter.assert_called_once_with("pop", limit=5)
    else:
        getter.assert_called_once_with(limit=5)


def test_global_api_charts_match_artists_and_tracks_in_order():
    connector = LastFM("test-key")
    connector.network = Mock()
    artists = [plex_artist("First", 10), plex_artist("Second", 20)]
    artist_library = SimpleNamespace(is_music=True, get_all=Mock(return_value=artists))
    connector.network.get_top_artists.return_value = [chart_artist("Second", None), chart_artist("First", None)]
    assert connector.get_rating_keys("lastfm_chart_top_artists", {"limit": 2}, artist_library) == [(20, "ratingKey"), (10, "ratingKey")]
    connector.network.get_top_artists.assert_called_once_with(limit=2)

    tracks = [plex_track("ABBA", "Gold", "Dancing Queen", 30, duration=231444)]
    track_library = SimpleNamespace(is_music=True, get_all=Mock(return_value=tracks))
    connector.network.get_top_tracks.return_value = [chart_track("ABBA", None, "Dancing Queen", None, duration=231000)]
    assert connector.get_rating_keys("lastfm_chart_top_tracks", {"limit": 1}, track_library) == [(30, "ratingKey")]
    connector.network.get_top_tracks.assert_called_once_with(limit=1)


def test_missing_track_without_album_logs_artist_and_track(monkeypatch):
    logger = Mock()
    monkeypatch.setattr(builder_module, "logger", logger)
    builder = CollectionBuilder.__new__(CollectionBuilder)
    builder.library = SimpleNamespace(name="Music", is_music=True)
    builder.name = "Top Tracks"
    builder.Type = "Collection"
    builder.details = {"show_missing": True}
    builder.do_report = False
    builder.missing_tracks = [{"artist": "Alannah Myles", "album": None, "name": "Black Velvet", "mbid": "", "reason": "not found"}]

    builder._report_missing_music()

    assert "1/1 Top Tracks Collection | ? | Alannah Myles - Black Velvet" in [args.args[0] for args in logger.info.call_args_list]


def test_missing_track_with_album_logs_artist_and_track_but_reports_album(monkeypatch):
    logger = Mock()
    monkeypatch.setattr(builder_module, "logger", logger)
    builder = CollectionBuilder.__new__(CollectionBuilder)
    builder.library = SimpleNamespace(name="Music", is_music=True, add_missing=Mock())
    builder.name = "Top Tracks"
    builder.Type = "Collection"
    builder.details = {"show_missing": True}
    builder.do_report = True
    builder.missing_tracks = [{"artist": "Alannah Myles", "album": "Greatest Hits", "name": "Black Velvet", "mbid": "track-id", "reason": "not found"}]

    builder._report_missing_music()

    assert "1/1 Top Tracks Collection | ? | Alannah Myles - Black Velvet" in [args.args[0] for args in logger.info.call_args_list]
    builder.library.add_missing.assert_called_once_with("Top Tracks", [("Alannah Myles - Greatest Hits - Black Velvet", "track-id")], False, is_music="track")


def test_music_collection_item_titles_show_artist_and_item(monkeypatch):
    class Album:
        pass

    class Track:
        pass

    monkeypatch.setattr(util, "Album", Album)
    monkeypatch.setattr(util, "Track", Track)
    album = Album()
    album.parentTitle, album.title = "Alannah Myles", "Greatest Hits"
    track = Track()
    track.grandparentTitle, track.parentTitle, track.title = "Alannah Myles", "Greatest Hits", "Black Velvet"

    assert util.item_title(album) == "Alannah Myles - Greatest Hits"
    assert util.item_title(track) == "Alannah Myles - Black Velvet"


def test_top_artists_service_failure_is_reported():
    connector = LastFM("test-key")
    connector.network = Mock()
    connector.network.get_user.side_effect = pylast.NetworkError(connector.network, OSError("unavailable"))
    library = SimpleNamespace(name="Music", is_music=True, get_all=Mock(return_value=[]))
    with pytest.raises(Failed, match="Last.fm Error"):
        connector.get_rating_keys("lastfm_user_top_artists", {"username": "listener", "period": "overall", "limit": 10}, library)


def test_builder_parses_username_and_options():
    builder = CollectionBuilder.__new__(CollectionBuilder)
    builder.Type = "Collection"
    builder.builder_level = "artist"
    builder.builders = []
    builder._lastfm("lastfm_user_top_artists", [{"username": "listener", "period": "7DAY", "limit": 25}, "friend"])
    assert builder.builders == [
        ("lastfm_user_top_artists", {"username": "listener", "period": "7day", "limit": 25}),
        ("lastfm_user_top_artists", {"username": "friend", "period": "overall", "limit": 50}),
    ]
    with pytest.raises((BuilderValidationError, Failed)):
        builder._lastfm("lastfm_user_top_artists", {"period": "overall"})
    builder.builder_level = "album"
    with pytest.raises(BuilderValidationError, match="artist-level"):
        builder._lastfm("lastfm_user_top_artists", "listener")
    builder._lastfm("lastfm_user_top_albums", "listener")
    assert builder.builders[-1] == ("lastfm_user_top_albums", {"username": "listener", "period": "overall", "limit": 50})
    assert "lastfm_user_top_albums" in builder_module.custom_sort_builders
    assert "lastfm_user_top_albums" in builder_module.parts_collection_valid
    builder.builder_level = "track"
    builder._lastfm("lastfm_user_top_tracks", "listener")
    assert builder.builders[-1] == ("lastfm_user_top_tracks", {"username": "listener", "period": "overall", "limit": 50})
    assert "lastfm_user_top_tracks" in builder_module.custom_sort_builders
    assert "lastfm_user_top_tracks" in builder_module.parts_collection_valid
    for method in ("lastfm_user_loved_tracks", "lastfm_user_recent_tracks"):
        builder._lastfm(method, "listener")
        assert builder.builders[-1] == (method, {"username": "listener", "limit": 50})
        assert method in builder_module.custom_sort_builders
        assert method in builder_module.parts_collection_valid
    builder._lastfm("lastfm_user_recent_tracks", {"username": "listener", "from": 100, "to": 200})
    assert builder.builders[-1] == ("lastfm_user_recent_tracks", {"username": "listener", "limit": 50, "from": 100, "to": 200})
    with pytest.raises(BuilderValidationError, match="from must be before to"):
        builder._lastfm("lastfm_user_recent_tracks", {"username": "listener", "from": 200, "to": 100})
    with pytest.raises(BuilderValidationError, match="unsupported options"):
        builder._lastfm("lastfm_user_loved_tracks", {"username": "listener", "period": "overall"})
    builder.builder_level = "artist"
    builder._lastfm("lastfm_user_tags", {"username": "listener", "tag": "pop", "limit": 25})
    assert builder.builders[-1] == ("lastfm_user_tags", {"username": "listener", "tag": "pop", "level": "artist", "limit": 25})
    builder.builder_level = "album"
    builder._lastfm("lastfm_tag_charts", "pop")
    assert builder.builders[-1] == ("lastfm_tag_charts", {"tag": "pop", "level": "album", "limit": 50})
    builder.builder_level = "track"
    builder._lastfm("lastfm_tag_charts", {"tag": "dance", "limit": 10})
    assert builder.builders[-1] == ("lastfm_tag_charts", {"tag": "dance", "level": "track", "limit": 10})
    for method in ("lastfm_user_tags", "lastfm_tag_charts"):
        assert method in builder_module.custom_sort_builders
        assert method in builder_module.parts_collection_valid
    with pytest.raises((BuilderValidationError, Failed)):
        builder._lastfm("lastfm_user_tags", {"tag": "pop"})
    builder.builder_level = "artist"
    builder._lastfm("lastfm_chart_top_artists", {"limit": 25})
    assert builder.builders[-1] == ("lastfm_chart_top_artists", {"limit": 25})
    builder.builder_level = "track"
    builder._lastfm("lastfm_chart_top_tracks", 10)
    assert builder.builders[-1] == ("lastfm_chart_top_tracks", {"limit": 10})
    assert "lastfm_chart_top_tracks" in builder_module.parts_collection_valid
    for method in ("lastfm_chart_top_artists", "lastfm_chart_top_tracks"):
        assert method in builder_module.custom_sort_builders
    with pytest.raises(BuilderValidationError, match="only supports the limit"):
        builder._lastfm("lastfm_chart_top_tracks", {"tag": "pop"})
    with pytest.raises(Failed):
        builder._lastfm("lastfm_chart_top_tracks", 0)


def test_lastfm_config_and_builder_schema():
    root = Path(__file__).resolve().parents[1] / "json-schema"
    config_schema = json.loads((root / "config-schema.json").read_text(encoding="utf-8"))
    collection_schema = json.loads((root / "collection-schema.json").read_text(encoding="utf-8"))
    Draft7Validator.check_schema(config_schema)
    Draft7Validator.check_schema(collection_schema)
    Draft7Validator(config_schema).validate({"plex": {"url": "https://plex.example", "token": "token"}, "tmdb": {"apikey": "key"}, "lastfm": {"apikey": "key"}})
    collection = {"collections": {"My artists": {"lastfm_user_top_artists": {"username": "listener", "period": "1month", "limit": 50}}}}
    Draft7Validator(collection_schema).validate(collection)
    collection["collections"]["My artists"]["lastfm_user_top_artists"]["period"] = "yesterday"
    with pytest.raises(ValidationError):
        Draft7Validator(collection_schema).validate(collection)
    Draft7Validator(collection_schema).validate({"collections": {"My albums": {"lastfm_user_top_albums": {"username": "listener", "period": "overall", "limit": 50}, "collection_order": "custom"}}})
    Draft7Validator(collection_schema).validate({"collections": {"My tracks": {"lastfm_user_top_tracks": {"username": "listener", "period": "overall", "limit": 50}, "collection_order": "custom"}}})
    Draft7Validator(collection_schema).validate({"collections": {"Loved": {"lastfm_user_loved_tracks": {"username": "listener", "limit": 50}}, "Recent": {"lastfm_user_recent_tracks": {"username": "listener", "limit": 50, "from": 100, "to": 200}}}})
    Draft7Validator(collection_schema).validate({"collections": {"Personal tag": {"lastfm_user_tags": {"username": "listener", "tag": "pop", "limit": 50}, "builder_level": "album"}, "Tag chart": {"lastfm_tag_charts": "pop", "builder_level": "track"}}})
    Draft7Validator(collection_schema).validate({"collections": {"Global artists": {"lastfm_chart_top_artists": 50}, "Global tracks": {"lastfm_chart_top_tracks": {"limit": 20}, "collection_order": "custom"}}})
    with pytest.raises(ValidationError):
        Draft7Validator(collection_schema).validate({"collections": {"Invalid global chart": {"lastfm_chart_top_tracks": {"limit": 0}}}})


def test_missing_artists_follow_show_missing_and_save_report(monkeypatch):
    logger = Mock()
    monkeypatch.setattr(builder_module, "logger", logger)
    builder = CollectionBuilder.__new__(CollectionBuilder)
    builder.library = SimpleNamespace(name="Music", is_movie=False, is_show=False, is_music=True, add_missing=Mock())
    builder.name = "Top Artists"
    builder.Type = "Collection"
    builder.details = {"show_missing": True}
    builder.do_report = True
    builder.missing_movies = []
    builder.missing_shows = []
    builder.missing_parts = []
    builder.missing_artists = [{"name": "Bananarama", "mbid": "84d06499-0643-46b8-9e1f-45f743a53f5e", "reason": "not found"}, {"name": "Bebe Rexha & Snoop Dogg", "mbid": "", "reason": "not found"}]

    assert builder.run_missing() == (0, 0)
    logger.separator.assert_called_once_with("Missing Artists from Library: Music", space=False, border=False)
    assert "1/2 Top Artists Collection | ? | Bananarama" in [args.args[0] for args in logger.info.call_args_list]
    assert not any("MBID:" in str(args.args[0]) for args in logger.info.call_args_list)
    builder.library.add_missing.assert_called_once_with("Top Artists", [("Bananarama", "84d06499-0643-46b8-9e1f-45f743a53f5e"), ("Bebe Rexha & Snoop Dogg", None)], False, is_music=True)


def test_missing_artist_report_uses_musicbrainz_ids_as_strings():
    report = Mock()
    library = SimpleNamespace(report_data={}, config=SimpleNamespace(Requests=SimpleNamespace(file_yaml=Mock(return_value=report))), report_path="report.yml")
    Library._add_to_file(library, "Missing", "Top Artists", [("Bananarama", "84d06499-0643-46b8-9e1f-45f743a53f5e"), ("Bebe Rexha & Snoop Dogg", None)], False, is_music=True)
    assert library.report_data == {
        "Top Artists": {
            "Artists Missing (MusicBrainz IDs)": {"84d06499-0643-46b8-9e1f-45f743a53f5e": "Bananarama"},
            "Artists Missing": ["Bebe Rexha & Snoop Dogg"],
        }
    }
    report.save.assert_called_once_with()


def test_missing_music_levels_share_log_and_report_behavior(monkeypatch):
    logger = Mock()
    monkeypatch.setattr(builder_module, "logger", logger)
    builder = CollectionBuilder.__new__(CollectionBuilder)
    builder.library = SimpleNamespace(name="Music", is_movie=False, is_show=False, is_music=True, add_missing=Mock())
    builder.name = "Music Chart"
    builder.Type = "Collection"
    builder.details = {"show_missing": True}
    builder.do_report = True
    builder.missing_movies = []
    builder.missing_shows = []
    builder.missing_parts = []
    builder.missing_artists = []
    builder.missing_albums = []
    builder.missing_tracks = []
    builder._record_missing_music("artist", {"name": "Artist", "mbid": "", "reason": "not found"})
    builder._record_missing_music("album", {"artist": "Artist", "name": "Album", "mbid": "album-id", "reason": "ambiguous"})
    builder._record_missing_music("track", {"artist": "Artist", "album": "Album", "name": "Track", "mbid": "track-id", "reason": "not found"})

    assert builder.run_missing() == (0, 0)
    assert [args.args[0] for args in logger.separator.call_args_list] == [
        "Missing Artists from Library: Music",
        "Missing Albums from Library: Music",
        "Missing Tracks from Library: Music",
    ]
    log_lines = [str(args.args[0]) for args in logger.info.call_args_list]
    assert not any("MBID:" in line for line in log_lines)
    assert "1/1 Music Chart Collection | ? | Artist - Album [Ambiguous Plex match]" in log_lines
    assert "1/1 Music Chart Collection | ? | Artist - Track" in log_lines
    assert builder.library.add_missing.call_args_list == [
        call("Music Chart", [("Artist", None)], False, is_music=True),
        call("Music Chart", [("Artist - Album", "album-id")], False, is_music="album"),
        call("Music Chart", [("Artist - Album - Track", "track-id")], False, is_music="track"),
    ]


def test_music_report_has_distinct_artist_album_and_track_sections():
    report = Mock()
    library = SimpleNamespace(report_data={}, config=SimpleNamespace(Requests=SimpleNamespace(file_yaml=Mock(return_value=report))), report_path="report.yml")
    Library._add_to_file(library, "Missing", "Music Chart", [("Artist", None)], False, is_music="artist")
    Library._add_to_file(library, "Missing", "Music Chart", [("Artist - Album", "album-id")], False, is_music="album")
    Library._add_to_file(library, "Missing", "Music Chart", [("Artist - Album - Track", None)], False, is_music="track")

    assert library.report_data["Music Chart"] == {
        "Artists Missing (MusicBrainz IDs)": {},
        "Artists Missing": ["Artist"],
        "Albums Missing (MusicBrainz IDs)": {"album-id": "Artist - Album"},
        "Tracks Missing (MusicBrainz IDs)": {},
        "Tracks Missing": ["Artist - Album - Track"],
    }
