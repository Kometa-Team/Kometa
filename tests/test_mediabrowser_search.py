"""Search contracts shared by Jellyfin and Emby, using native DTO fixtures."""

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

import modules.builder  # noqa: F401 -- break circular imports
from modules.mediabrowser import MediaBrowser, MediaBrowserItem
from modules.mediabrowser_search import FIELD_TYPES, compile_selector, requires_media, values
from modules.util import Failed


def item(**raw):
    library = SimpleNamespace(server=SimpleNamespace(type_name="jellyfin"), find_poster_url=lambda item: None)
    return MediaBrowser._search_metadata(MediaBrowserItem({"_kometa_collections": ["Example collection"], "Id": "1", "Name": "Example", "Type": "Movie", **raw}, library))


@pytest.fixture
def detail():
    return item(
        Name="Example",
        Type="Series",
        ProductionYear=2020,
        OfficialRating="PG-13",
        Overview="Space adventure",
        OriginalTitle="Original",
        SortName="Sort",
        Taglines=["In space"],
        SeriesName="Series",
        Album="Album",
        Status="Ended",
        Tags=["Favorite"],
        Artists=["Artist"],
        AlbumArtists=[{"Name": "Artist"}],
        Genres=["Drama"],
        Studios=[{"Name": "Studio"}],
        ProductionLocations=["United States"],
        People=[{"Name": role, "Type": role} for role in ("Actor", "Director", "Writer", "Producer")],
        PremiereDate="2020-01-01",
        DateCreated="2024-01-01",
        DateLastSaved="2024-02-01",
        EndDate="2023-01-01",
        RunTimeTicks=72000000000,
        CommunityRating=7.5,
        CriticRating=80,
        SeasonCount=3,
        EpisodeCount=30,
        ChildCount=3,
        RecursiveItemCount=30,
        ParentIndexNumber=1,
        IndexNumber=2,
        EditionName="Extended",
        ProviderIds={"Tmdb": "123"},
        IsMissing=False,
        LockData=True,
        UserData={"Rating": 9, "PlayCount": 0, "PlaybackPositionTicks": 1200000000, "PlayedPercentage": 25, "Played": False, "IsFavorite": True, "LastPlayedDate": "2024-01-01"},
        MediaSources=[
            {
                "Path": "/Movies/Example.mkv",
                "Bitrate": 18000000,
                "Size": 1000000000,
                "Container": "mkv",
                "Video3DFormat": None,
                "MediaStreams": [
                    {
                        "Type": "Video",
                        "Width": 3840,
                        "Height": 2160,
                        "AspectRatio": "16:9",
                        "Codec": "hevc",
                        "Profile": "Main 10",
                        "VideoRangeType": "DOVIWithHDR10",
                        "BitRate": 16000000,
                        "BitDepth": 10,
                        "AverageFrameRate": 23.976,
                        "RefFrames": 4,
                        "DvProfile": 8,
                        "DvLevel": 6,
                        "Hdr10PlusPresentFlag": False,
                        "IsInterlaced": False,
                    },
                    {"Type": "Audio", "Codec": "eac3", "Profile": "Atmos", "Title": "English Atmos", "Channels": 6, "BitRate": 640000, "BitDepth": 24, "SampleRate": 48000, "Language": "eng", "IsOriginal": True},
                    {"Type": "Subtitle", "Title": "English subtitles", "Language": "eng", "IsExternal": True},
                ],
            },
            {"Path": "/Movies/Example.1080p.mkv", "MediaStreams": []},
        ],
    )


def test_every_registered_field_has_a_reader(detail):
    for field in FIELD_TYPES:
        assert values(detail, field), field


@pytest.mark.parametrize(
    "field,expected",
    [
        ("aspect.gt", 1.7),
        ("width", 3840),
        ("height", 2160),
        ("channels", 6),
        ("audio_codec", "eac3"),
        ("video_profile", "Main 10"),
        ("audio_track_title", "Atmos"),
        ("subtitle_language", "en"),
        ("label", "Favorite"),
        ("label.count_gt", 0),
        ("duration", 120),
        ("duration_seconds", 7200),
        ("bitrate", 18000),
        ("video_bitrate", 16000000),
        ("audio_bitrate", 640000),
        ("file_size", 1000000000),
        ("audience_rating", 7.5),
        ("critic_rating", 8),
        ("user_rating", 9),
        ("plays", 0),
        ("progress_ratio", 0.25),
        ("position_seconds", 120),
        ("duplicate", True),
        ("watched", False),
        ("unwatched", True),
        ("is_favorite", True),
        ("is_in_progress", True),
        ("is_locked", True),
        ("is_missing", False),
        ("hdr10plus", False),
        ("interlaced", False),
        ("has_dolby_vision", True),
        ("atmos", True),
        ("has_subtitles", True),
        ("has_edition", True),
        ("unmatched", False),
        ("seasons", 3),
        ("episodes", 30),
        ("season_number", 1),
        ("episode_number", 2),
        ("last_played.before", "2025-01-01"),
        ("updated.after", "2024-01-01"),
    ],
)
def test_native_metadata_selectors(detail, field, expected):
    assert compile_selector({field: expected})(detail)


@pytest.mark.parametrize("field", ["duration.not", "aspect.lt", "plays", "progress", "user_rating", "last_played", "watched", "is_favorite", "unmatched", "hdr10plus"])
def test_missing_metadata_does_not_match_negative_or_zero_filters(field):
    expected = False if FIELD_TYPES[field.split(".")[0]] == "boolean" else 30 if field == "last_played" else 0
    assert not compile_selector({field: expected})(item())


def test_validate_is_a_control_option_and_definitions_are_not_mutated(detail):
    definition = {"validate": False, "any": {"content_rating": "R, PG-13"}}
    assert compile_selector(definition)(detail)
    assert definition["validate"] is False
    with pytest.raises(Failed, match="validate must be a boolean"):
        compile_selector({"validate": "false", "any": {"title": "Example"}})
    with pytest.raises(Failed, match="Unsupported local search"):
        compile_selector({"validate": False, "any": {"nonexistent": True}})


def test_year_aliases_date_filters_and_nested_groups(detail):
    now = datetime(2024, 6, 1, tzinfo=timezone.utc)
    assert compile_selector({"all": [{"year": "current_year-4"}, {"any": {"decade": "2020s", "title": "Other"}}]}, current_time=now)(detail)
    assert compile_selector({"updated": 180}, current_time=now)(detail)


def test_media_requirements_include_nested_fields_and_sorting():
    assert requires_media({"all": [{"any": {"audio_codec": "aac"}}]})
    assert requires_media({"sort_by": "channels.desc", "any": {"title": "Example"}})
    assert not requires_media({"any": {"actor": "Example"}})


def test_progress_and_unplayed_use_playback_state_not_favorites():
    data = item(UserData={"PlaybackPositionTicks": 10000000, "Played": False, "IsFavorite": False})
    assert compile_selector({"progress": True, "unplayed": True})(data)
    assert not compile_selector({"progress": False})(data)


def test_and_tags_and_aliases(detail):
    detail.data["native"]["Tags"] = ["One", "Two"]
    assert compile_selector({"label.and": "One, Two"})(detail)
    assert not compile_selector({"label.and": ["One", "Missing"]})(detail)
    assert compile_selector({"folder_location": "/Movies", "dovi": True})(detail)
    assert compile_selector({"original_language": "en"})(detail)


def test_sort_title_uses_explicit_server_override():
    assert compile_selector({"sort_title.is": "001 Example"})(item(ForcedSortName="001 Example", SortName="Example"))
