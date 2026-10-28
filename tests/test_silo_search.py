from types import SimpleNamespace

import pytest

from modules.local_search import compile_selector
from modules.silo_search import FIELD_TYPES
from modules.silo_search import compile_selector as compile_silo_selector
from modules.util import Failed


@pytest.mark.parametrize("rating,expected_overlay", [("G", "g"), ("PG", "pg"), ("PG-13", "pg-13"), ("R", "r"), ("NC-17", "nc-17"), ("NR", "nr"), ("gb/12A", "pg-13"), ("TV-MA", "r"), ("01", "g"), (None, "nr"), ("", "nr")])
def test_shipped_us_rating_overlays_match_csv_alternatives(rating, expected_overlay):
    from pathlib import Path

    from ruamel.yaml import YAML

    with Path("defaults/overlays/content_rating_us_movie.yml").open() as handle:
        default = YAML(typ="safe").load(handle)
    matched = []
    for name, definition in default["overlays"].items():
        call = next(call for call in definition["template"] if call["name"] == "cr_us")
        if compile_silo_selector({"any": {"content_rating": call["rating"]}})(item(content_rating=rating)):
            matched.append(name)
    assert matched == [expected_overlay]


@pytest.mark.parametrize("compile_filter", [compile_selector, compile_silo_selector])
def test_csv_tags_preserve_regex_and_explicit_list_literals(compile_filter):
    assert compile_filter({"content_rating": " G, PG, PG-13 "})(item(content_rating="PG"))
    assert not compile_filter({"content_rating.not": "G, PG, PG-13"})(item(content_rating="PG"))
    assert compile_filter({"studio": ["Example, Inc."]})(item(studios=["Example, Inc."]))
    assert compile_filter({"content_rating.regex": r"^PG(?:-13){0,1}$"})(item(content_rating="PG-13"))
    assert compile_filter({"title.is": "Example, Inc."})(item(title="Example, Inc."))
    assert not compile_filter({"content_rating": "G, PG"})(item())


@pytest.fixture
def silo_detail():
    result = item(
        title="Example",
        original_title="Original",
        sort_title="Sort Example",
        overview="A space adventure",
        tagline="Into space",
        series_title="Series",
        year=1999,
        genres=["Drama", "Science Fiction"],
        studios=["Studio"],
        networks=["Network"],
        countries=["US"],
        keywords=["space"],
        folder_paths=["/movies/Example"],
        original_language="eng",
        content_rating="PG-13",
        type="movie",
        status="matched",
        show_status="Ended",
        runtime=120,
        duration_seconds=7200,
        release_date="1999-01-01",
        added_at="2026-10-01T12:00:00Z",
        first_air_date="1999-01-01",
        last_air_date="2001-12-31",
        rating_imdb=7.5,
        rating_tmdb=7.2,
        rating_rt_critic=80,
        rating_rt_audience=90,
        user_rating=4,
        season_count=3,
        episode_count=12,
        season_number=2,
        episode_number=4,
        advisory_age=13,
        user_state={"played": False, "is_favorite": True, "in_watchlist": False, "not_interested": False},
        user_data={"position_seconds": 60, "is_in_progress": True},
        sort_metrics={"play_count": 2, "progress_ratio": 0.25, "viewed_at": "2026-10-10"},
        subtitles=[{"language": "fr", "title": "External French"}],
        overlay_summary={"release_type": "WEB-DL"},
        versions=[
            {
                "resolution": "4K",
                "edition_raw": "Director's Cut",
                "file_path": "/movies/Example/file.mkv",
                "container": "mkv",
                "bitrate": 12000,
                "file_size": 100000,
                "duration": 7200,
                "hdr": True,
                "codec_video": "hevc",
                "codec_audio": "truehd",
                "audio_tracks": [{"codec": "truehd", "channels": 8, "profile": "Atmos", "title": "English", "embedded_title": "Commentary", "language": "eng", "bit_depth": 24, "sample_rate": 48000, "bitrate": 3000000}],
                "subtitle_tracks": [{"language": "deu", "title": "German"}],
                "video_tracks": [
                    {
                        "codec": "hevc",
                        "width": 1920,
                        "height": 1080,
                        "aspect_ratio": "1.33:1",
                        "profile": "Main 10",
                        "dv_profile": 8,
                        "dv_level": 6,
                        "dv_config_present": True,
                        "hdr10_plus": True,
                        "interlaced": False,
                        "bit_depth": 10,
                        "frame_rate": "24000/1001",
                        "reference_frames": 4,
                        "bitrate": 10000000,
                        "video_range_type": "DOVI",
                    }
                ],
            }
        ],
    )
    for role in ("actors", "directors", "writers", "producers"):
        setattr(result, role, [SimpleNamespace(tag="Person")])
    return result


def test_every_registered_silo_field_has_a_metadata_reader(silo_detail):
    from modules.silo_search import values

    assert all(values(silo_detail, field) for field in FIELD_TYPES)


def test_silo_rating_arrays_fill_missing_direct_rating_fields():
    data = item(ratings=[{"source": "imdb", "score": 75}], rating_sources=[{"source": "rt_critic", "score": 80}, {"source": "rt_audience", "score": 90}])
    assert compile_silo_selector({"rating_imdb": 7.5, "critic_rating": 8, "audience_rating": 9})(data)
    assert not compile_silo_selector({"rating_tmdb.gt": 0})(data)


def test_silo_tag_counts_distinguish_empty_from_unreported():
    assert compile_silo_selector({"genre.count_lt": 1})(item(genres=[]))
    assert not compile_silo_selector({"genre.count_lt": 1})(item())


def test_silo_year_aliases_and_relative_dates_use_supplied_clock():
    from datetime import datetime, timezone

    now = datetime(2026, 10, 28, tzinfo=timezone.utc)
    assert compile_silo_selector({"year": "current_year-1"}, current_time=now)(item(year=2025))
    assert compile_silo_selector({"decade": "1990s"})(item(year=1999))
    assert compile_silo_selector({"added": 30}, current_time=now)(item(added_at="2026-10-01T00:00:00Z"))
    assert not compile_silo_selector({"added.not": 30}, current_time=now)(item())


def test_silo_native_false_flags_and_track_rational_values():
    data = item(versions=[{"hdr": False, "video_tracks": [{"dv_config_present": False, "dv_profile": 0, "interlaced": False, "hdr10_plus": False, "frame_rate": "30000/1001"}]}])
    assert compile_silo_selector({"hdr": False, "has_dolby_vision": False, "hdr10plus": False, "interlaced": False, "frame_rate.gt": 29.9})(data)


@pytest.mark.parametrize(
    "field,expected",
    [
        ("title.is", "Example"),
        ("summary", "space"),
        ("original_title", "Original"),
        ("sort_title", "Sort"),
        ("tagline", "space"),
        ("show_title", "Series"),
        ("genre", "Drama"),
        ("studio", "Studio"),
        ("network", "Network"),
        ("country", "US"),
        ("keyword", "space"),
        ("folder", "Example"),
        ("original_language", "en"),
        ("content_rating", "PG-13"),
        ("type", "movie"),
        ("status", "matched"),
        ("show_status", "Ended"),
        ("year.gte", 1999),
        ("decade", 1990),
        ("duration", 120),
        ("runtime", 120),
        ("duration_seconds", 7200),
        ("versions", 1),
        ("width", 1920),
        ("height", 1080),
        ("aspect.gt", 1.32),
        ("aspect.lt", 1.34),
        ("channels.gte", 8),
        ("dovi_profile", 8),
        ("dovi_level", 6),
        ("video_bit_depth", 10),
        ("audio_bit_depth", 24),
        ("audio_sample_rate", 48000),
        ("frame_rate.gt", 23.9),
        ("reference_frames", 4),
        ("bitrate", 12000),
        ("video_bitrate", 10000000),
        ("audio_bitrate", 3000000),
        ("file_size", 100000),
        ("critic_rating", 8),
        ("audience_rating", 9),
        ("user_rating", 8),
        ("rating_imdb", 7.5),
        ("rating_tmdb", 7.2),
        ("rating_rt_critic", 80),
        ("rating_rt_audience", 90),
        ("seasons", 3),
        ("episodes", 12),
        ("season_number", 2),
        ("episode_number", 4),
        ("advisory_age", 13),
        ("plays", 2),
        ("progress", 0.25),
        ("position_seconds", 60),
        ("audio_codec", "truehd"),
        ("video_codec", "hevc"),
        ("audio_profile", "Atmos"),
        ("video_profile", "Main 10"),
        ("video_range", "DOVI"),
        ("audio_track_title", "Commentary"),
        ("subtitle_track_title", "External French"),
        ("audio_language", "en"),
        ("subtitle_language", "de"),
        ("subtitle_language", "fr"),
        ("container", "mkv"),
        ("edition", "Director"),
        ("resolution", "4k"),
        ("resolution", 2160),
        ("hdr", True),
        ("has_dolby_vision", True),
        ("hdr10plus", True),
        ("atmos", True),
        ("interlaced", False),
        ("has_edition", True),
        ("unmatched", False),
        ("watched", False),
        ("is_favorite", True),
        ("in_watchlist", False),
        ("not_interested", False),
        ("is_in_progress", True),
        ("release.before", "2000-01-01"),
        ("release.after", "1998-12-31"),
        ("added.after", "2026-09-30"),
        ("first_episode_aired.before", "2000-01-01"),
        ("last_episode_aired.after", "2001-01-01"),
        ("last_played.after", "2026-10-01"),
        ("genre.count_gte", 2),
        ("genre.count_lt", 3),
    ],
)
def test_silo_contract_fields_and_modifiers(silo_detail, field, expected):
    assert compile_silo_selector({field: expected})(silo_detail)


def test_silo_aspect_uses_maximum_of_known_versions_and_rounds_dimensions():
    assert compile_silo_selector({"aspect.gt": 1.32, "aspect.lt": 1.34})(item(versions=[{"video_tracks": [{"width": 1440, "height": 1080}]}]))
    assert not compile_silo_selector({"aspect.lt": 1.34})(item(versions=[{"video_tracks": [{"aspect_ratio": "4:3"}, {"aspect_ratio": "16:9"}]}]))
    assert compile_silo_selector({"aspect": 1.78})(item(overlay_summary={"aspect_ratio": "16:9"}))


@pytest.mark.parametrize("field", ["aspect", "width", "channels", "dovi_profile", "critic_rating", "plays", "duration"])
@pytest.mark.parametrize("modifier", ["gt", "not"])
def test_silo_unknown_numbers_do_not_match(field, modifier):
    assert not compile_silo_selector({f"{field}.{modifier}": 1})(item())


@pytest.mark.parametrize("definition", [{"aspect.gt": "nan"}, {"aspect.lt": float("inf")}, {"channels": True}, {"aspect.gt": "widescreen"}, {"title.gte": 2}, {"label": "Overlay"}, {"has_collection": True}, {"release.before": "not a date"}])
def test_silo_unsupported_or_invalid_filters_fail_explicitly(definition):
    with pytest.raises(Failed):
        compile_silo_selector(definition)


def test_silo_nested_numeric_and_boolean_filters_do_not_capture_last_field_type(silo_detail):
    assert compile_silo_selector({"all": [{"aspect.gt": 1.3}, {"any": {"hdr10plus": True, "channels.lt": 2}}, {"genre": "Drama"}]})(silo_detail)
    assert not compile_silo_selector({"all": {"channels.lt": 2, "hdr": True}})(silo_detail)


def test_silo_country_aliases_and_counts(silo_detail):
    names = {"US": "United States of America"}
    assert compile_silo_selector({"country": "United States", "country.count_lt": 2}, country_names=names)(silo_detail)
    assert not compile_silo_selector({"country.count_lt": 1}, country_names=names)(silo_detail)


def item(**data):
    return SimpleNamespace(data=data)


def test_nested_resolution_regex_matches_any_available_version():
    predicate = compile_selector({"all": {"any": {"resolution.regex": "(?i)2160|4k", "title.is": "Fallback"}, "hdr": True}})
    assert predicate(item(title="Example", versions=[{"resolution": "1080p", "hdr": False}, {"resolution": "2160p", "hdr": True}]))
    assert not predicate(item(title="Example", versions=[{"resolution": "1080p", "hdr": True}]))
    assert not predicate(item(title="Fallback", versions=[{"resolution": "1080p", "hdr": False}]))


def test_filename_edition_and_summary_metadata():
    data = item(versions=[{"file_path": "/Movies/Example.2024.DV.HDR10+.mkv", "edition_raw": "Director's Cut"}], overlay_summary={"resolution": "4K", "hdr": "Dolby Vision"})
    assert compile_selector({"resolution.regex": "(?i)2160|4k", "filepath.regex": ["never", r"(?i)\bdv.HDR10(\+|P(lus)?\b)"], "edition": "Director", "has_dolby_vision": True})(data)


def test_missing_metadata_does_not_match_positive_or_negative_searches():
    assert not compile_selector({"resolution.regex": "4K"})(item())
    assert not compile_selector({"filepath.not": "Director"})(item(versions=[{"file_name": "Director.mkv"}]))


@pytest.mark.parametrize("definition", [{}, {"all": {}}, {"resolution.regex": "["}, {"label": "Kometa"}, {"title.gte": "x"}, {"hdr": "false"}])
def test_invalid_search_is_rejected_before_execution(definition):
    with pytest.raises(Failed, match="Silo Error"):
        compile_selector(definition)
