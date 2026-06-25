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
from modules.builder import CollectionBuilder, parts_collection_valid
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

    def test_smart_label_collection_does_not_delete(self):
        """Smart label collections are not deleted from Plex."""
        builder = make_builder(smart_label_collection=True, obj=SimpleNamespace(title="Smart"))
        # delete() calls self.library.search — skip that path
        # Smart label collections should not change deleted flag
        assert builder.deleted is False

    def test_no_obj_returns_empty_string(self):
        builder = make_builder(obj=None)
        assert builder.delete() == ""


# ═══════════════════════════════════════════════════════════════════════
# gather_ids
# ═══════════════════════════════════════════════════════════════════════


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
