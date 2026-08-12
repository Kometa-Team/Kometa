"""Tests for modules/builder.py — the CollectionBuilder class.

The builder module is 277 KB with ~60 public methods.  These tests
focus on the most critical and bug-prone areas: key resolution, item
filtering, deletion, and method dispatching.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from plexapi.exceptions import NotFound

import modules.builder as builder_module
from modules.builder import CollectionBuilder, custom_sort_builders, parts_collection_valid
from modules.util import Failed
from tests.conftest import FakeLogger

# ═══════════════════════════════════════════════════════════════════════
# Shared fakes
# ═══════════════════════════════════════════════════════════════════════


class FakeShowLibrary:
    def __init__(self):
        self.plex_map = {}
        self.is_show = True
        self.ensure_calls = []

    def ensure_plex_map(self, builder_level):
        self.ensure_calls.append(builder_level)
        if builder_level == "show":
            self.plex_map["plex://show/63e3eedd166819851638a316"] = [101]
        elif builder_level == "episode":
            self.plex_map["plex://episode/63e3eedd166819851638a317"] = [201]


class FakeEpisode:
    def __init__(self, rating_key, title):
        self.ratingKey = rating_key
        self.title = title


class FakeSeason:
    def __init__(self, episodes):
        self._episodes = episodes

    def episodes(self):
        return self._episodes


class FakeShow:
    def __init__(self, title, seasons=None, episodes=None):
        self.title = title
        self._seasons = seasons or {}
        self._episodes = episodes or {}

    def season(self, season):
        if season not in self._seasons:
            raise NotFound(f"Season {season} not found")
        return self._seasons[season]

    def episode(self, season, episode):
        if (season, episode) not in self._episodes:
            raise NotFound(f"Episode {season}/{episode} not found")
        return self._episodes[(season, episode)]


class FakeTVDbLibrary:
    def __init__(self, show_item, tvdb_id=383275, rating_key=101):
        self.show_map = {tvdb_id: [rating_key]}
        self._show_item = show_item

    def fetch_item(self, rating_key):
        if rating_key != 101:
            raise AssertionError(f"Unexpected rating key: {rating_key}")
        return self._show_item

    def cached_item_subitems(self, item, method_name):
        # Mirrors the real Plex.cached_item_subitems() contract (modules/plex.py) without the memoization - these tests don't depend on cache identity, just the same seasons()/episodes() results.
        return list(getattr(item, method_name)())


# ═══════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════


def make_builder(**attrs) -> CollectionBuilder:
    """Create a minimal CollectionBuilder with ``__new__``."""
    builder = CollectionBuilder.__new__(CollectionBuilder)
    defaults = {
        "Type": "Collection",
        "builder_level": "movie",
        "playlist": False,
        "libraries": [],
        "ignore_imdb_ids": [],
        "ignore_ids": [],
        "missing_movies": [],
        "missing_parts": [],
        "missing_shows": [],
        "do_missing": True,
        "filters": [],
        "details": {"show_filtered": False, "show_unfiltered": False, "only_filter_missing": False},
        "filtered_keys": {},
        "found_items": [],
        "do_report": False,
        "obj": None,
        "name": "Test Collection",
        "builders": [],
        "items": [],
        "mdb_list_arr_ids": None,
        "item_details": {},
        "asset_directory": None,
        "radarr_details": {"add_existing": False, "upgrade_existing": False, "monitor_existing": False},
        "sonarr_details": {"add_existing": False, "upgrade_existing": False, "monitor_existing": False},
        "run_again_movies": [],
        "run_again_shows": [],
        "notification_additions": [],
        "notification_removals": [],
        "added_to_radarr": [],
        "added_to_sonarr": [],
        "collection_poster": None,
        "collection_background": None,
        "deleted": False,
        "created": True,
        "smart_label_collection": False,
        "check_filters": lambda item, display: True,
        "value_filters": [],
    }
    defaults.update(attrs)
    for key, value in defaults.items():
        setattr(builder, key, value)
    return builder


def _episode_builder(library) -> CollectionBuilder:
    return make_builder(
        builder_level="episode",
        libraries=[library],
        details={"show_filtered": False, "show_unfiltered": False, "only_filter_missing": False},
    )


def test_load_collection_items_rejects_empty_standard_mdblist_sync(monkeypatch):
    monkeypatch.setattr(builder_module, "logger", FakeLogger())
    builder = make_builder(build_collection=False, sync_to_mdb_list={"name": "List", "mode": "sync"})

    with pytest.raises(Failed, match="No Collection items found"):
        builder.load_collection_items()


def test_load_collection_items_allows_empty_arr_mdblist_sync(monkeypatch):
    monkeypatch.setattr(builder_module, "logger", FakeLogger())
    builder = make_builder(build_collection=False, sync_to_mdb_list={"name": "List", "mode": "sync"}, mdb_list_arr_ids=[])

    builder.load_collection_items()


# ═══════════════════════════════════════════════════════════════════════
# custom_sort_builders
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.parametrize("method", builder_module.letterboxd.semantic_builders)
def test_letterboxd_discovery_builders_support_custom_sort(method):
    assert method in custom_sort_builders


@pytest.mark.parametrize("method", ["tracearr_binged", "tracearr_transcoded", "tracearr_watch_time", "tracearr_in_progress"])
def test_tracearr_activity_builders_support_custom_sort(method):
    assert method in builder_module.tracearr.builders
    assert method in custom_sort_builders
    assert method in builder_module.playlist_attributes


def test_tracearr_parser_supports_user_and_quality_filters():
    builder = make_builder()

    builder._tracearr(
        "tracearr_watch_time",
        {
            "user": "Anthony",
            "watched": True,
            "minimum_progress": 25,
            "maximum_progress": 90,
            "transcode": True,
            "video_decision": "transcode",
            "platform": "Apple TV",
        },
    )

    _, data = builder.builders[0]
    assert data["list_type"] == "watch_time"
    assert data["user"] == "Anthony"
    assert data["minimum_progress"] == 25
    assert data["maximum_progress"] == 90
    assert data["transcode"] is True


def test_tracearr_in_progress_requires_user():
    builder = make_builder(playlist=True)

    with pytest.raises(Failed, match="requires user"):
        builder._tracearr("tracearr_in_progress", {"list_days": 30})


def test_tracearr_in_progress_sets_progress_defaults():
    builder = make_builder(playlist=True)

    builder._tracearr("tracearr_in_progress", {"user": "Anthony"})

    _, data = builder.builders[0]
    assert data["watched"] is False
    assert data["minimum_progress"] == 1
    assert data["maximum_progress"] == 84


# ═══════════════════════════════════════════════════════════════════════
# _find_plex_keys
# ═══════════════════════════════════════════════════════════════════════


class TestFindPlexKeys:
    def test_show_guid(self):
        library = FakeShowLibrary()
        builder = make_builder(libraries=[library], builder_level="show")
        assert builder._find_plex_keys("plex://show/63e3eedd166819851638a316") == [101]
        assert library.ensure_calls == ["show"]

    def test_episode_guid(self):
        library = FakeShowLibrary()
        builder = make_builder(libraries=[library], builder_level="episode")
        assert builder._find_plex_keys("plex://episode/63e3eedd166819851638a317") == [201]
        assert library.ensure_calls == ["episode"]

    def test_returns_none_for_unmapped_movie_guid(self):
        library = MagicMock()
        library.plex_map = {}
        library.is_show = False
        builder = make_builder(libraries=[library], builder_level="movie")
        assert builder._find_plex_keys("plex://movie/5d7768244de0ee001fcc7ff0") is None

    def test_unknown_prefix_returns_none(self):
        library = MagicMock()
        library.plex_map = {}
        builder = make_builder(libraries=[library], builder_level="movie")
        assert builder._find_plex_keys("unknown://id") is None


# ═══════════════════════════════════════════════════════════════════════
# validate_attribute — audio_language / subtitle_language
# ═══════════════════════════════════════════════════════════════════════


class FakeLangLibrary:
    """Stands in for the Plex library used by validate_attribute's language handling."""

    def __init__(self, language_map, search_choices=None, names=None):
        # language_map: {"audio_language": {"es": ["es-419", "spa"]}, ...}
        self.language_map = language_map
        self.search_choices = search_choices or {}
        self.names = names or {}
        self.get_tags_calls = []
        self.get_search_choices_calls = []

    def get_search_choices(self, attribute, title=True, name_pairs=False, libtype=None):
        self.get_search_choices_calls.append(attribute)
        return self.search_choices.get(attribute, {}), self.names.get(attribute, [])

    def get_language_search_values(self, attribute, code):
        self.get_tags_calls.append((attribute, code))
        return self.language_map.get(attribute, {}).get(code, [])


def make_lang_builder(library, **attrs) -> CollectionBuilder:
    defaults = {"details": {"show_options": False}, "ignore_blank_results": False}
    defaults.update(attrs)
    return make_builder(library=library, **defaults)


class TestValidateAttributeLanguage:
    def test_expands_base_code_to_every_library_variant_for_plex_search(self):
        library = FakeLangLibrary({"audio_language": {"es": ["es-419", "es-MX", "spa"]}})
        builder = make_lang_builder(library)
        result = builder.validate_attribute("audio_language", "", "audio_language", "es", True, plex_search=True)
        assert result == [("es", "es-419"), ("es", "es-MX"), ("es", "spa")]

    def test_does_not_call_the_uncached_get_search_choices_for_plex_search_language(self):
        """The generic (uncached) listFilterChoices lookup must be skipped entirely for
        audio_language/subtitle_language under plex_search — get_language_search_values (cached)
        is the only choices lookup that should fire."""
        library = FakeLangLibrary({"audio_language": {"es": ["es-419"], "en": ["en-US"]}})
        builder = make_lang_builder(library)
        builder.validate_attribute("audio_language", "", "audio_language", ["es", "en"], True, plex_search=True)
        assert library.get_search_choices_calls == []

    def test_subtitle_language_uses_its_own_cache_key(self):
        library = FakeLangLibrary({"subtitle_language": {"fr": ["fr-CA", "fre"]}})
        builder = make_lang_builder(library)
        result = builder.validate_attribute("subtitle_language", "", "subtitle_language", "fr", True, plex_search=True)
        assert result == [("fr", "fr-CA"), ("fr", "fre")]
        assert library.get_tags_calls == [("subtitle_language", "fr")]

    def test_is_case_insensitive(self):
        library = FakeLangLibrary({"audio_language": {"es": ["es-419"]}})
        builder = make_lang_builder(library)
        result = builder.validate_attribute("audio_language", "", "audio_language", "ES", True, plex_search=True)
        assert result == [("ES", "es-419")]

    def test_exact_locale_value_passes_through_as_a_single_variant(self):
        """When the library resolves a code to a single exact variant (e.g. the user configured
        the specific locale "es-419" rather than the base "es"), only that variant is used."""
        library = FakeLangLibrary({"audio_language": {"es-419": ["es-419"]}})
        builder = make_lang_builder(library)
        result = builder.validate_attribute("audio_language", "", "audio_language", "es-419", True, plex_search=True)
        assert result == [("es-419", "es-419")]

    def test_multiple_configured_languages_each_expand_independently(self):
        library = FakeLangLibrary({"audio_language": {"es": ["es-419", "spa"], "en": ["en-US"]}})
        builder = make_lang_builder(library)
        result = builder.validate_attribute("audio_language", "", "audio_language", ["es", "en"], True, plex_search=True)
        assert result == [("es", "es-419"), ("es", "spa"), ("en", "en-US")]

    def test_raises_filter_failed_when_language_not_present_in_library(self):
        library = FakeLangLibrary({"audio_language": {}})
        builder = make_lang_builder(library)
        with pytest.raises(builder_module.FilterFailed):
            builder.validate_attribute("audio_language", "", "audio_language", "zh", True, plex_search=True)

    def test_logs_instead_of_raising_when_validate_is_false_and_ignoring_blank_results(self, monkeypatch):
        monkeypatch.setattr(builder_module, "logger", FakeLogger())
        library = FakeLangLibrary({"audio_language": {}})
        builder = make_lang_builder(library, ignore_blank_results=True)
        result = builder.validate_attribute("audio_language", "", "audio_language", "zh", False, plex_search=True)
        assert result == []

    def test_non_plex_search_path_is_unaffected_and_uses_exact_choices_only(self):
        """The filters: (client-side) path doesn't go through get_language_search_values."""
        library = FakeLangLibrary({"audio_language": {"es": ["es-419"]}}, search_choices={"audio_language": {"es-419": "es-419"}})
        builder = make_lang_builder(library)
        result = builder.validate_attribute("audio_language", "", "audio_language", "es-419", True, plex_search=False)
        assert result == ["es-419"]
        assert library.get_tags_calls == []

    def test_regex_on_plex_search_language_matches_against_the_raw_locale_tagged_key(self):
        """The .regex branch only ever reads names (title, key) pairs, never a stripped value,
        so a locale-tagged key like "es-ES" is returned as-is rather than normalized to "es"."""
        library = FakeLangLibrary({}, names={"audio_language": [("Spanish", "es-ES")]})
        builder = make_lang_builder(library)
        result = builder.validate_attribute("audio_language", ".regex", "audio_language", "Span", True, plex_search=True)
        assert result == [("Spanish", "es-ES")]


# ═══════════════════════════════════════════════════════════════════════
# _rating_key_is_ignored
# ═══════════════════════════════════════════════════════════════════════


class TestRatingKeyIsIgnored:
    def test_ignored_key(self):
        library = MagicMock()
        library.movie_map = {101: [500]}
        builder = make_builder(libraries=[library], ignore_ids=[101])
        assert builder._rating_key_is_ignored(500) is True

    def test_non_ignored_key(self):
        library = MagicMock()
        library.movie_map = {101: [500]}
        builder = make_builder(libraries=[library], ignore_ids=[101])
        assert builder._rating_key_is_ignored(999) is False

    def test_empty_ignore_ids(self):
        library = MagicMock()
        library.movie_map = {}
        builder = make_builder(libraries=[library], ignore_ids=[])
        assert builder._rating_key_is_ignored(101) is False


# ═══════════════════════════════════════════════════════════════════════
# filter_and_save_items
# ═══════════════════════════════════════════════════════════════════════


class TestFilterAndSaveItems:
    def test_ratingkey_items_respect_shared_ignore_ids(self, monkeypatch):
        monkeypatch.setattr(builder_module, "logger", FakeLogger())

        class FakeLibrary:
            def __init__(self):
                self.movie_map = {353546: [101]}
                self.show_map = {}
                self.imdb_map = {}
                self.fetch_calls = []

            def fetch_item(self, rating_key):
                self.fetch_calls.append(rating_key)
                raise AssertionError("fetch_item should not be called for ignored rating keys")

        builder = make_builder(
            library=FakeLibrary(),
            libraries=[FakeLibrary()],
            ignore_ids=[353546],
        )
        assert builder.filter_and_save_items([(101, "ratingKey")]) is None
        assert builder.found_items == []
        assert builder.library.fetch_calls == []

    def test_empty_ids_returns_none(self, monkeypatch):
        monkeypatch.setattr(builder_module, "logger", FakeLogger())
        builder = make_builder()
        assert builder.filter_and_save_items([]) is None

    def test_logs_missing_tvdb_season(self, monkeypatch):
        logger = FakeLogger()
        monkeypatch.setattr(builder_module, "logger", logger)
        builder = _episode_builder(FakeTVDbLibrary(FakeShow("Example Show")))
        assert builder.filter_and_save_items([("383275_2", "tvdb_season")]) is None
        assert builder.missing_parts == ["Example Show Season: 2 Missing"]
        assert any("tvdb_season:383275_2" in m for m in logger.warning_messages)
        assert "0 Episodes Expanded from 1 ID" in logger.info_messages
        assert "0 Unique Episodes Kept" in logger.info_messages

    def test_logs_missing_tvdb_episode(self, monkeypatch):
        logger = FakeLogger()
        monkeypatch.setattr(builder_module, "logger", logger)
        builder = _episode_builder(FakeTVDbLibrary(FakeShow("Example Show")))
        assert builder.filter_and_save_items([("383275_2_1", "tvdb_episode")]) is None
        assert builder.missing_parts == ["Example Show Season: 2 Episode: 1 Missing"]

    def test_expands_tvdb_season_into_episodes(self, monkeypatch):
        monkeypatch.setattr(builder_module, "logger", FakeLogger())
        monkeypatch.setattr(builder_module, "Episode", FakeEpisode)
        monkeypatch.setattr(builder_module.util, "item_title", lambda item: item.title)
        episodes = [FakeEpisode(201, "Episode 1"), FakeEpisode(202, "Episode 2")]
        builder = _episode_builder(FakeTVDbLibrary(FakeShow("Example Show", seasons={2: FakeSeason(episodes)})))
        builder.filter_and_save_items([("383275_2", "tvdb_season")])
        assert builder.found_items == episodes

    def test_deduplicates_episodes(self, monkeypatch):
        logger = FakeLogger()
        monkeypatch.setattr(builder_module, "logger", logger)
        monkeypatch.setattr(builder_module, "Episode", FakeEpisode)
        monkeypatch.setattr(builder_module.util, "item_title", lambda item: item.title)
        ep1 = FakeEpisode(201, "Episode 1")
        ep2 = FakeEpisode(202, "Episode 2")
        builder = _episode_builder(
            FakeTVDbLibrary(
                FakeShow("Example Show", seasons={2: FakeSeason([ep1, ep2])}, episodes={(2, 1): ep1}),
            )
        )
        builder.filter_and_save_items([("383275_2", "tvdb_season"), ("383275_2_1", "tvdb_episode")])
        assert "3 Episodes Expanded from 2 IDs" in logger.info_messages
        assert "2 Unique Episodes Kept" in logger.info_messages
        assert builder.found_items == [ep1, ep2]


# ═══════════════════════════════════════════════════════════════════════
# _log_episode_count
# ═══════════════════════════════════════════════════════════════════════


class TestLogEpisodeCount:
    def test_logs_total_only(self, monkeypatch):
        logger = FakeLogger()
        monkeypatch.setattr(builder_module, "logger", logger)
        builder = make_builder(builder_level="episode")
        builder._log_episode_count(5, expanded_total=5)
        assert "5 Episodes Expanded from 5 IDs" in logger.info_messages[0]

    def test_logs_with_expanded_and_unique(self, monkeypatch):
        logger = FakeLogger()
        monkeypatch.setattr(builder_module, "logger", logger)
        builder = make_builder(builder_level="episode")
        builder._log_episode_count(5, expanded_total=15, unique_total=10)
        assert "15 Episodes Expanded from 5 IDs" in logger.info_messages[0]
        assert "10 Unique Episodes Kept" in logger.info_messages[1]

    def test_skips_logging_for_non_episode_builders(self, monkeypatch):
        logger = FakeLogger()
        monkeypatch.setattr(builder_module, "logger", logger)
        builder = make_builder(builder_level="movie")
        builder._log_episode_count(5)
        assert logger.info_messages == []


# ═══════════════════════════════════════════════════════════════════════
# _textfile
# ═══════════════════════════════════════════════════════════════════════


class TestTextfile:
    def test_registers_multiple_files_as_single_builder(self):
        builder = make_builder()
        builder.config = SimpleNamespace(
            TextFile=SimpleNamespace(validate_file=lambda data: ["/tmp/priority.txt", "/tmp/overflow.txt"]),
        )
        builder._textfile("text_file", ["config/lists/priority.txt", "config/lists/overflow.txt"])
        assert builder.builders == [("text_file", ["/tmp/priority.txt", "/tmp/overflow.txt"])]

    def test_is_allowed_for_episode_or_season_collections(self):
        assert "text_file" in parts_collection_valid

    def test_value_filter_is_allowed_for_episode_overlays(self):
        assert "value_filter" in parts_collection_valid


# ═══════════════════════════════════════════════════════════════════════
# Batched item labels
# ═══════════════════════════════════════════════════════════════════════


class BatchLabelLibrary:
    def __init__(self, section_id, batch_size=None):
        self.Plex = SimpleNamespace(key=section_id, batchMultiEdits=MagicMock(), editTags=MagicMock())
        self.plex_bulk_edit_batch_size = batch_size
        self.cached_items = {}
        self._save_multi_edits_with_retry = MagicMock()
        self.edit_tags = MagicMock()
        self.tag_edit = MagicMock()
        self.search = MagicMock(return_value=[])
        self.Radarr = None
        self.Sonarr = None
        self.is_movie = True
        self.is_show = False
        self.movie_rating_key_map = {}
        self.show_rating_key_map = {}

    @staticmethod
    def reload(item):
        return item

    @staticmethod
    def item_labels(item):
        return item.labels


def label_item(rating_key, labels=None, section_id=1, item_type="movie"):
    return SimpleNamespace(
        ratingKey=rating_key,
        title=f"Item {rating_key}",
        labels=[SimpleNamespace(tag=label) for label in labels or []],
        librarySectionID=section_id,
        type=item_type,
        locations=[],
    )


class TestBatchedItemLabels:
    @pytest.fixture(autouse=True)
    def _logger(self, monkeypatch):
        monkeypatch.setattr(builder_module, "logger", FakeLogger())

    def test_adds_labels_in_configured_batches(self):
        library = BatchLabelLibrary(1, batch_size=2)
        items = [label_item(i) for i in range(1, 6)]
        library.cached_items = {item.ratingKey: (item, True) for item in items}
        builder = make_builder(library=library, libraries=[library], items=items, item_details={"item_label": ["Favorite"]})

        builder.update_item_details()

        assert [call.args[0] for call in library.Plex.batchMultiEdits.call_args_list] == [items[:2], items[2:4], items[4:]]
        assert library.Plex.editTags.call_args_list == [
            (("label", "Favorite"), {"remove": False}),
            (("label", "Favorite"), {"remove": False}),
            (("label", "Favorite"), {"remove": False}),
        ]
        assert library._save_multi_edits_with_retry.call_count == 3
        assert library.cached_items == {}
        assert all(call.args[0] == "genre" for call in library.edit_tags.call_args_list)

    def test_removes_only_items_that_have_the_label(self):
        library = BatchLabelLibrary(1)
        first = label_item(1, ["Favorite", "Keep"])
        second = label_item(2, ["Keep"])
        builder = make_builder(library=library, libraries=[library], items=[first, second], item_details={"item_label.remove": ["Favorite"]})

        builder.update_item_details()

        library.Plex.batchMultiEdits.assert_called_once_with([first])
        library.Plex.editTags.assert_called_once_with("label", "Favorite", remove=True)
        library._save_multi_edits_with_retry.assert_called_once()

    def test_sync_groups_each_label_delta(self):
        library = BatchLabelLibrary(1)
        first = label_item(1, ["A", "B"])
        second = label_item(2, ["B", "C"])
        builder = make_builder(library=library, libraries=[library], items=[first, second], item_details={"item_label.sync": ["A", "C"]})

        builder.update_item_details()

        assert [call.args[0] for call in library.Plex.batchMultiEdits.call_args_list] == [[first], [second], [first, second]]
        assert library.Plex.editTags.call_args_list == [
            (("label", "C"), {"remove": False}),
            (("label", "A"), {"remove": False}),
            (("label", "B"), {"remove": True}),
        ]
        assert library._save_multi_edits_with_retry.call_count == 3

    def test_batches_non_item_label_removals_and_excludes_collection_items(self):
        library = BatchLabelLibrary(1)
        collection_item = label_item(1, ["Cleanup"])
        non_item = label_item(2, ["Keep", "Cleanup"])
        library.search.return_value = [collection_item, non_item]
        builder = make_builder(
            library=library,
            libraries=[library],
            items=[collection_item],
            item_details={"non_item_remove_label": ["Cleanup", "Not Present"]},
        )

        builder.update_item_details()

        library.search.assert_called_once_with(label=["Cleanup", "Not Present"], libtype="movie")
        library.Plex.batchMultiEdits.assert_called_once_with([non_item])
        library.Plex.editTags.assert_called_once_with("label", "Cleanup", remove=True)
        library._save_multi_edits_with_retry.assert_called_once()
        assert all(call.args[0] == "genre" for call in library.edit_tags.call_args_list)

    def test_separates_playlist_libraries_and_item_types(self):
        first_library = BatchLabelLibrary(1)
        second_library = BatchLabelLibrary(2)
        movie = label_item(1, section_id=1)
        episode = label_item(2, section_id=1, item_type="episode")
        other_movie = label_item(3, section_id=2)
        builder = make_builder(library=first_library, libraries=[first_library, second_library])

        builder._batch_item_label_edits({"add": {"Shared": [movie, episode, other_movie]}, "remove": {}})

        assert [call.args[0] for call in first_library.Plex.batchMultiEdits.call_args_list] == [[movie], [episode]]
        second_library.Plex.batchMultiEdits.assert_called_once_with([other_movie])
        assert first_library._save_multi_edits_with_retry.call_count == 2
        second_library._save_multi_edits_with_retry.assert_called_once()


# ═══════════════════════════════════════════════════════════════════════
# TMDb lookup resilience
# ═══════════════════════════════════════════════════════════════════════


class TestTmdbLookupResilience:
    def test_item_tmdb_season_titles_skips_tmdb_exception(self, monkeypatch):
        logger = FakeLogger()
        monkeypatch.setattr(builder_module, "logger", logger)
        season = SimpleNamespace(index=1, title="Old Title", editTitle=MagicMock())
        item = SimpleNamespace(ratingKey=1, title="Example Show", seasons=[season], locations=[])
        library = SimpleNamespace(
            reload=lambda value: value,
            item_labels=lambda value: [],
            edit_tags=lambda *args, **kwargs: None,
            query=lambda value: value,
            show_rating_key_map={1: 383275},
            movie_rating_key_map={},
            is_movie=False,
            is_show=True,
            Radarr=None,
            Sonarr=None,
        )
        builder = make_builder(
            library=library,
            libraries=[library],
            items=[item],
            item_details={"item_tmdb_season_titles": True},
            config=SimpleNamespace(
                Convert=SimpleNamespace(tvdb_to_tmdb=lambda tvdb_id: 987),
                TMDb=SimpleNamespace(get_show=MagicMock(side_effect=builder_module.TMDbException("boom"))),
            ),
        )

        builder.update_item_details()

        assert any("unable to load show TMDb ID 987" in message for message in logger.warning_messages)
        assert not season.editTitle.called

    def test_run_collections_again_skips_tmdb_exception_for_missing_movie(self, monkeypatch):
        logger = FakeLogger()
        monkeypatch.setattr(builder_module, "logger", logger)
        library = SimpleNamespace(
            movie_map={},
            show_map={},
            is_movie=False,
            is_show=False,
            get_collection=lambda name, force_search=True: SimpleNamespace(title=name),
            get_collection_name_and_items=lambda obj, smart_label_collection: (obj.title, []),
            alter_collection=lambda *args, **kwargs: None,
        )
        builder = make_builder(
            library=library,
            libraries=[library],
            name="Test Collection",
            Type="Collection",
            run_again_movies=[123],
            details={"show_missing": True},
            config=SimpleNamespace(TMDb=SimpleNamespace(get_movie=MagicMock(side_effect=builder_module.TMDbException("boom")))),
        )
        builder.send_notifications = MagicMock()

        builder.run_collections_again()

        assert any("unable to load movie TMDb ID 123" in message for message in logger.warning_messages)


# ═══════════════════════════════════════════════════════════════════════
# TVDb outage resilience
# ═══════════════════════════════════════════════════════════════════════


class TestTvdbOutageResilience:
    def test_run_missing_stops_after_tvdb_circuit_opens(self, monkeypatch):
        logger = FakeLogger()
        monkeypatch.setattr(builder_module, "logger", logger)
        get_tvdb_obj = MagicMock(side_effect=builder_module.tvdb.CircuitOpen("TVDb circuit open"))
        library = SimpleNamespace(is_movie=False, is_show=True, Sonarr=None)
        builder = make_builder(
            library=library,
            config=SimpleNamespace(TVDb=SimpleNamespace(get_tvdb_obj=get_tvdb_obj)),
            is_playlist=False,
            missing_shows=[1, 2, 3],
            details={"show_missing": False, "show_filtered": False, "missing_only_released": False},
            run_again=False,
        )

        builder.run_missing()

        get_tvdb_obj.assert_called_once_with(1)
        assert logger.warning_messages == []


# ═══════════════════════════════════════════════════════════════════════
# update_item_details — rating batching
# ═══════════════════════════════════════════════════════════════════════


class TestRatingBatching:
    # Rating batching goes through the same per-library/per-type grouping as label batching (see TestBatchedItemLabels
    # / BatchLabelLibrary), so mixed-library playlists route through the right library's Plex connection.
    @staticmethod
    def _library(section_id=1):
        return SimpleNamespace(
            name="Test Library",
            Plex=SimpleNamespace(key=section_id, batchMultiEdits=MagicMock(), editField=MagicMock()),
            plex_bulk_edit_batch_size=None,
            cached_items={},
            _save_multi_edits_with_retry=MagicMock(),
            reload=lambda item: item,
            item_labels=lambda item: [],
            show_rating_key_map={},
            movie_rating_key_map={},
            is_movie=True,
            is_show=False,
            Radarr=None,
            Sonarr=None,
        )

    def test_only_items_needing_change_are_batched(self, monkeypatch):
        monkeypatch.setattr(builder_module, "logger", FakeLogger())
        library = self._library()
        needs_change = SimpleNamespace(ratingKey=1, title="Needs Change", rating=None, librarySectionID=1, type="movie")
        already_set = SimpleNamespace(ratingKey=2, title="Already Set", rating=5.5, librarySectionID=1, type="movie")
        builder = make_builder(
            library=library,
            libraries=[library],
            items=[needs_change, already_set],
            item_details={"item_critic_rating": 5.5},
        )

        builder.update_item_details()

        library.Plex.batchMultiEdits.assert_called_once_with([needs_change])
        library.Plex.editField.assert_called_once_with("rating", 5.5)
        library._save_multi_edits_with_retry.assert_called_once()

    def test_multiple_rating_attrs_batched_separately(self, monkeypatch):
        monkeypatch.setattr(builder_module, "logger", FakeLogger())
        library = self._library()
        item = SimpleNamespace(ratingKey=1, title="Example", rating=None, userRating=None, librarySectionID=1, type="movie")
        builder = make_builder(
            library=library,
            libraries=[library],
            items=[item],
            item_details={"item_critic_rating": 5.5, "item_user_rating": 7.0},
        )

        builder.update_item_details()

        assert library.Plex.editField.call_args_list == [
            (("rating", 5.5),),
            (("userRating", 7.0),),
        ]
        assert library._save_multi_edits_with_retry.call_count == 2

    def test_no_items_need_change_skips_batch_call(self, monkeypatch):
        monkeypatch.setattr(builder_module, "logger", FakeLogger())
        library = self._library()
        item = SimpleNamespace(ratingKey=1, title="Already Set", rating=5.5, librarySectionID=1, type="movie")
        builder = make_builder(
            library=library,
            libraries=[library],
            items=[item],
            item_details={"item_critic_rating": 5.5},
        )

        builder.update_item_details()

        library.Plex.batchMultiEdits.assert_not_called()
        library.Plex.editField.assert_not_called()

    def test_separates_playlist_libraries_for_ratings(self, monkeypatch):
        monkeypatch.setattr(builder_module, "logger", FakeLogger())
        first_library = self._library(section_id=1)
        second_library = self._library(section_id=2)
        first_item = SimpleNamespace(ratingKey=1, title="First", rating=None, librarySectionID=1, type="movie")
        second_item = SimpleNamespace(ratingKey=2, title="Second", rating=None, librarySectionID=2, type="movie")
        builder = make_builder(
            library=first_library,
            libraries=[first_library, second_library],
            items=[first_item, second_item],
            item_details={"item_critic_rating": 5.5},
        )

        builder.update_item_details()

        first_library.Plex.batchMultiEdits.assert_called_once_with([first_item])
        second_library.Plex.batchMultiEdits.assert_called_once_with([second_item])


# ═══════════════════════════════════════════════════════════════════════
# delete
# ═══════════════════════════════════════════════════════════════════════


class TestDelete:
    def test_deletes_and_skips_notifications(self):
        class FakeLibrary:
            def __init__(self):
                self.deleted_items = []
                self.reloaded_items = []
                self.webhook_calls = 0

                class _Webhooks:
                    def __init__(self, outer):
                        self.outer = outer

                    def collection_hooks(self, *args, **kwargs):
                        self.outer.webhook_calls += 1

                self.Webhooks = _Webhooks(self)

            def delete(self, item):
                self.deleted_items.append(item)

            def item_reload(self, item):
                self.reloaded_items.append(item)

        builder = make_builder(
            library=FakeLibrary(),
            obj=SimpleNamespace(title="Test Collection"),
            details={"changes_webhooks": True},
        )
        assert builder.delete() == "Collection Test Collection deleted"
        builder.send_notifications()
        assert builder.deleted is True
        assert builder.library.deleted_items == [builder.obj]
        assert builder.library.webhook_calls == 0

    def test_smart_label_collection_removes_labels_before_delete(self):
        items = [SimpleNamespace(title="First"), SimpleNamespace(title="Second")]
        library = MagicMock()
        library.search.return_value = items
        builder = make_builder(
            library=library,
            name="Smart",
            smart_label_collection=True,
            obj=SimpleNamespace(title="Smart"),
        )

        assert builder.delete() == "Collection Smart deleted"

        library.search.assert_called_once_with(label="Smart", libtype="movie")
        assert library.edit_tags.call_args_list == [
            (("label", items[0]), {"remove_tags": "Smart"}),
            (("label", items[1]), {"remove_tags": "Smart"}),
        ]
        library.delete.assert_called_once_with(builder.obj)
        assert builder.deleted is True

    def test_no_obj_returns_empty_string(self):
        builder = make_builder(obj=None)
        assert builder.delete() == ""


# ═══════════════════════════════════════════════════════════════════════
# gather_ids
# ═══════════════════════════════════════════════════════════════════════


class TestGatherIds:
    def test_dispatches_tracearr_builder(self):
        tracearr = MagicMock()
        tracearr.get_rating_keys.return_value = [(101, "ratingKey")]
        library = SimpleNamespace(Tracearr=tracearr)
        builder = make_builder(
            config=SimpleNamespace(Cache=None),
            library=library,
            libraries=[library],
            playlist=False,
            details={"cache_builders": 0},
        )
        value = {"list_type": "history", "list_days": 30, "list_size": 10, "list_minimum": 0}

        assert builder.gather_ids("tracearr_history", value) == [(101, "ratingKey")]
        tracearr.get_rating_keys.assert_called_once_with(value)

    def test_playlist_queries_tracearr_server_once_for_movie_and_show_libraries(self):
        first_connector = MagicMock(api="http://tracearr/api/v1/public", server_id="tracearr-server-1")
        first_connector.get_rating_keys.return_value = [(101, "tmdb")]
        first_server = SimpleNamespace(machineIdentifier="plex-server-1")
        first_connector.library = SimpleNamespace(PlexServer=first_server)

        movie_library = SimpleNamespace(Tracearr=first_connector, PlexServer=first_server)
        show_library = SimpleNamespace(Tracearr=first_connector, PlexServer=first_server)
        libraries = [movie_library, show_library]
        builder = make_builder(
            config=SimpleNamespace(Cache=None),
            library=movie_library,
            libraries=libraries,
            playlist=True,
            details={"cache_builders": 0},
        )
        value = {"list_type": "history", "list_days": 30, "list_size": 10, "list_minimum": 0}

        assert builder.gather_ids("tracearr_history", value) == [(101, "tmdb")]
        first_connector.get_rating_keys.assert_called_once_with(value, is_playlist=True, libraries=[movie_library, show_library])

    def test_playlist_rejects_multiple_tracearr_servers(self):
        first_server = SimpleNamespace(machineIdentifier="plex-server-1")
        first_connector = MagicMock(api="http://tracearr/api/v1/public", server_id="tracearr-server-1")
        first_connector.library = SimpleNamespace(PlexServer=first_server)
        second_server = SimpleNamespace(machineIdentifier="plex-server-2")
        second_connector = MagicMock(api="http://tracearr/api/v1/public", server_id="tracearr-server-2")
        second_connector.library = SimpleNamespace(PlexServer=second_server)
        libraries = [
            SimpleNamespace(Tracearr=first_connector, PlexServer=first_server),
            SimpleNamespace(Tracearr=second_connector, PlexServer=second_server),
        ]
        builder = make_builder(
            config=SimpleNamespace(Cache=None),
            library=libraries[0],
            libraries=libraries,
            playlist=True,
            details={"cache_builders": 0},
        )

        with pytest.raises(Failed, match="only combine libraries from one Plex server"):
            builder.gather_ids(
                "tracearr_history",
                {"list_type": "history", "list_days": 30, "list_size": 10, "list_minimum": 0},
            )


class TestBuildFilter:
    def test_raises_on_none_filter(self):
        builder = make_builder()
        import modules.util as util

        with pytest.raises(util.BuilderValidationError, match="is blank"):
            builder.build_filter("tmdb", None)

    def test_raises_on_non_dict_filter(self):
        builder = make_builder()
        import modules.util as util

        with pytest.raises(util.BuilderValidationError, match="must be a dictionary"):
            builder.build_filter("tmdb", "not_a_dict")

    @pytest.mark.parametrize(
        ("attribute", "expected_filter"),
        [
            ("folder_location", "source=7"),
            ("folder_location.not", "source!=7"),
        ],
    )
    def test_builds_folder_location_smart_filter(self, attribute, expected_filter):
        import modules.plex as plex_module

        library = plex_module.Plex.__new__(plex_module.Plex)
        library.is_movie = True
        library.is_show = False
        library.is_music = False
        library.Plex = SimpleNamespace(
            TYPE="movie",
            listFilters=lambda libtype: [SimpleNamespace(filter="source", title="Folder Location")],
        )
        library.get_search_choices = MagicMock(return_value=({"/media/movies": 7}, ["/media/movies"]))
        builder = make_builder(
            library=library,
            details={"show_options": False},
        )

        _, details, url = builder.build_filter(
            "smart_filter",
            {"all": {attribute: "/media/movies"}},
            default_sort="random",
        )

        assert expected_filter in url
        assert "Folder Location" in details
        library.get_search_choices.assert_called_once_with("folder_location", title=False, libtype="movie")

    def test_builds_track_folder_location_smart_filter(self):
        import modules.plex as plex_module

        list_filters = MagicMock(return_value=[SimpleNamespace(filter="source", title="Folder Location")])
        library = plex_module.Plex.__new__(plex_module.Plex)
        library.is_movie = False
        library.is_show = False
        library.is_music = True
        library.Plex = SimpleNamespace(TYPE="artist", listFilters=list_filters)
        library.get_tags = MagicMock(return_value=[SimpleNamespace(title="/media/music", key="12")])
        builder = make_builder(
            library=library,
            builder_level="track",
            details={"show_options": False},
        )

        _, details, url = builder.build_filter(
            "smart_filter",
            {"all": {"folder_location": "/media/music"}},
            default_sort="random",
        )

        assert "source=12" in url
        assert "Folder Location" in details
        assert list_filters.call_count == 2
        list_filters.assert_called_with("track")
        library.get_tags.assert_called_once_with("source")

    def test_rejects_folder_location_above_track_level_in_music_library(self):
        library = SimpleNamespace(
            is_movie=False,
            is_show=False,
            is_music=True,
            split=lambda value: (value.removesuffix(".not"), ".not" if value.endswith(".not") else "", value),
        )
        builder = make_builder(
            library=library,
            builder_level="artist",
            details={"show_options": False},
        )

        with pytest.raises(builder_module.BuilderValidationError, match="does not work for music libraries"):
            builder.build_filter(
                "smart_filter",
                {"all": {"folder_location": "/media/music"}},
                default_sort="random",
            )


# ═══════════════════════════════════════════════════════════════════════
# Dispatch table sanity tests
# ═══════════════════════════════════════════════════════════════════════
#
# CollectionBuilder dispatches based on membership in module-level lists.
# A typo or duplicate in any of these lists is a silent routing bug:
# the builder will either ignore an attribute or double-process it.
#
# These tests are *only* about the data, no fixtures needed.
# ═══════════════════════════════════════════════════════════════════════


class TestDispatchTables:
    """Sanity checks on builder.py's module-level dispatch tables.

    Catches:
      - Typos that create duplicate entries (silent double-dispatch).
      - Cross-list contamination where a name belongs to mutually
        exclusive categories (e.g. movie_only AND show_only).
      - Non-string entries that would never match dictionary lookups.
    """

    @pytest.mark.parametrize(
        "table_name",
        [
            "advance_new_agent",
            "advance_show",
            "show_only_builders",
            "movie_only_builders",
            "music_only_builders",
            "summary_details",
            "poster_details",
            "background_details",
            "square_art_details",
            "boolean_details",
            "scheduled_boolean",
            "string_details",
            "ignored_details",
            "item_false_details",
            "item_bool_details",
            "none_details",
            "none_builders",
            "radarr_details",
            "sonarr_details",
        ],
    )
    def test_table_has_no_duplicates(self, table_name):
        """Duplicate entries cause silent double-processing in dispatch."""
        table = getattr(builder_module, table_name)
        dupes = [x for x in table if table.count(x) > 1]
        assert len(table) == len(set(table)), f"{table_name} has duplicate entries: {sorted(set(dupes))}"

    @pytest.mark.parametrize(
        "table_name",
        [
            "advance_new_agent",
            "advance_show",
            "show_only_builders",
            "movie_only_builders",
            "music_only_builders",
            "summary_details",
            "poster_details",
            "background_details",
            "square_art_details",
            "boolean_details",
            "scheduled_boolean",
            "string_details",
            "ignored_details",
            "item_false_details",
            "item_bool_details",
            "none_details",
            "none_builders",
            "radarr_details",
            "sonarr_details",
        ],
    )
    def test_table_entries_are_non_empty_strings(self, table_name):
        """A non-string or empty-string entry can never match an attribute name."""
        table = getattr(builder_module, table_name)
        for entry in table:
            assert isinstance(entry, str), f"{table_name} contains non-string: {entry!r}"
            assert entry, f"{table_name} contains empty string"

    def test_movie_only_and_show_only_are_disjoint(self):
        """A builder cannot be both movie-only and show-only at the same time."""
        movies = set(builder_module.movie_only_builders)
        shows = set(builder_module.show_only_builders)
        overlap = movies & shows
        assert not overlap, f"Builders claim to be both movie-only and show-only: {overlap}"

    def test_movie_only_and_music_only_are_disjoint(self):
        movies = set(builder_module.movie_only_builders)
        music = set(builder_module.music_only_builders)
        overlap = movies & music
        assert not overlap, f"Builders are both movie-only and music-only: {overlap}"

    def test_show_only_and_music_only_are_disjoint(self):
        shows = set(builder_module.show_only_builders)
        music = set(builder_module.music_only_builders)
        overlap = shows & music
        assert not overlap, f"Builders are both show-only and music-only: {overlap}"

    def test_poster_details_disjoint_from_background_details(self):
        """A field name is either a poster or a background, never both."""
        posters = set(builder_module.poster_details)
        backgrounds = set(builder_module.background_details)
        overlap = posters & backgrounds
        assert not overlap, f"Fields appear in both poster_details and background_details: {overlap}"

    def test_radarr_and_sonarr_details_disjoint(self):
        """A detail name belongs to radarr OR sonarr, not both."""
        radarr = set(builder_module.radarr_details)
        sonarr = set(builder_module.sonarr_details)
        overlap = radarr & sonarr
        assert not overlap, f"Field names overlap between radarr_details and sonarr_details: {overlap}"

    def test_all_builders_contains_known_data_sources(self):
        """Sanity: the master builder list mentions tmdb, trakt, imdb."""
        all_builders = builder_module.all_builders
        # all_builders is a tuple of strings — at minimum some core sources
        text = " ".join(str(b) for b in all_builders)
        assert "tmdb" in text, "all_builders missing tmdb-related entries"
        assert "trakt" in text, "all_builders missing trakt-related entries"
        assert "imdb" in text, "all_builders missing imdb-related entries"
        assert "serializd_list" in all_builders
        assert "serializd_watchlist" in all_builders
        assert "serializd_trending" in all_builders
        assert "serializd_popular" in all_builders
        assert "serializd_featured" in all_builders
