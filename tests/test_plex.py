"""Tests for modules/plex.py — the Plex class.

Focuses on methods that can be tested in isolation without a real Plex
server connection.  Test instances are created via ``Plex.__new__`` with
manually-set attributes.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from plexapi.exceptions import BadRequest
from plexapi.video import Movie
from requests.exceptions import ReadTimeout

import modules.builder  # noqa: F401 — pre-import to break circular deps
import modules.plex as plex_module
from modules.plex import Plex
from tests.conftest import FakeLogger

# ═══════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════


def make_plex(**attrs) -> Plex:
    """Create a minimal Plex instance with ``Plex.__new__``.

    Defaults provide enough for basic method calls.  Override any
    attribute via keyword arguments.

    Sets ``Plex.logger`` and ``plex_module.logger`` to FakeLogger.
    """
    import modules.plex as plex_module

    plex = Plex.__new__(Plex)

    # Required by Library base class
    plex.name = attrs.pop("name", "Test Library")
    plex.is_movie = attrs.pop("is_movie", True)
    plex.is_show = attrs.pop("is_show", False)
    plex.type = attrs.pop("type", "Movie")
    plex.cached_items = attrs.pop("cached_items", {})
    plex.collection_names = attrs.pop("collection_names", [])
    plex.collection_files = attrs.pop("collection_files", [])
    plex.config = attrs.pop("config", SimpleNamespace(notify=MagicMock(), notify_delete=MagicMock()))

    # Required by Plex class
    plex.plex = attrs.pop("plex", None)
    plex.url = attrs.pop("url", "http://localhost:32400")
    plex.token = attrs.pop("token", "fake-token")
    plex.PlexServer = attrs.pop("PlexServer", MagicMock())
    plex.Plex = attrs.pop("Plex", MagicMock())
    plex.session = attrs.pop("session", MagicMock())
    plex.timeout = attrs.pop("timeout", 30)

    # Apply any remaining overrides
    for key, value in attrs.items():
        setattr(plex, key, value)

    plex_module.logger = FakeLogger()
    return plex


def make_plex_item(
    rating_key: int = 1,
    title: str = "Test Item",
    year: int = 2023,
    **extras,
) -> MagicMock:
    """Return a MagicMock that looks like a Plex video object."""
    item = MagicMock()
    item.ratingKey = rating_key
    item.title = title
    item.year = year
    item.type = extras.pop("type", "movie")
    for key, value in extras.items():
        setattr(item, key, value)
    return item


# ═══════════════════════════════════════════════════════════════════════
# validate_image_size
# ═══════════════════════════════════════════════════════════════════════


class TestValidateImageSize:
    def test_returns_true_when_under_limit(self, tmp_path):
        plex = make_plex()
        path = tmp_path / "small.jpg"
        path.write_bytes(b"a" * 100)
        assert plex.validate_image_size(SimpleNamespace(location=str(path), compare="abc")) is True

    def test_returns_false_when_over_limit(self, tmp_path, monkeypatch):
        import modules.plex as plex_module

        monkeypatch.setattr(plex_module, "MAX_IMAGE_SIZE", 50)
        plex = make_plex()
        path = tmp_path / "large.jpg"
        path.write_bytes(b"a" * 100)
        assert plex.validate_image_size(SimpleNamespace(location=str(path), compare="abc")) is False

    def test_zero_byte_file_under_limit(self, tmp_path):
        plex = make_plex()
        path = tmp_path / "empty.jpg"
        path.write_bytes(b"")
        assert plex.validate_image_size(SimpleNamespace(location=str(path), compare="abc")) is True

    def test_exactly_at_limit(self, tmp_path, monkeypatch):
        import modules.plex as plex_module

        monkeypatch.setattr(plex_module, "MAX_IMAGE_SIZE", 10)
        plex = make_plex()
        path = tmp_path / "exact.jpg"
        path.write_bytes(b"1234567890")  # 10 bytes
        assert plex.validate_image_size(SimpleNamespace(location=str(path), compare="abc")) is False


# ═══════════════════════════════════════════════════════════════════════
# notify / notify_delete
# ═══════════════════════════════════════════════════════════════════════


class TestNotify:
    def test_notify_delegates_to_config(self):
        mock_config = MagicMock()
        plex = make_plex(config=mock_config, PlexServer=SimpleNamespace(friendlyName="MyServer"))
        plex.notify("Something happened", collection="Test Collection")
        mock_config.notify.assert_called_once()
        args, kwargs = mock_config.notify.call_args
        assert kwargs.get("server") == "MyServer"
        assert kwargs.get("collection") == "Test Collection"

    def test_notify_delete_delegates_to_config(self):
        mock_config = MagicMock()
        plex = make_plex(config=mock_config, PlexServer=SimpleNamespace(friendlyName="MyServer"))
        plex.notify_delete("Collection removed")
        mock_config.notify_delete.assert_called_once()
        args, kwargs = mock_config.notify_delete.call_args
        assert kwargs.get("server") == "MyServer"


# ═══════════════════════════════════════════════════════════════════════
# item_labels
# ═══════════════════════════════════════════════════════════════════════


class TestItemLabels:
    def test_returns_labels_from_item(self):
        labels = [SimpleNamespace(tag="Kometa"), SimpleNamespace(tag="PMM")]
        item = make_plex_item(labels=labels)
        plex = make_plex()
        assert plex.item_labels(item) == labels

    def test_returns_empty_list_when_no_labels(self):
        item = make_plex_item(labels=[])
        plex = make_plex()
        assert plex.item_labels(item) == []


# ═══════════════════════════════════════════════════════════════════════
# find_poster_url
# ═══════════════════════════════════════════════════════════════════════


class TestFindPosterUrl:
    def test_returns_none_for_unknown_item(self):
        """Without TMDb mapping, find_poster_url returns None."""
        from plexapi.video import Movie

        item = MagicMock(spec=Movie)
        item.ratingKey = 1
        plex = make_plex(movie_rating_key_map={})
        url = plex.find_poster_url(item)
        assert url is None


# ═══════════════════════════════════════════════════════════════════════
# load_from_cache / load_list_from_cache
# ═══════════════════════════════════════════════════════════════════════


class TestLoadFromCache:
    def test_cache_hit(self):
        item = make_plex_item(rating_key=101)
        plex = make_plex(cached_items={101: (item, True)})
        assert plex.load_from_cache(101) is item

    def test_cache_miss(self):
        plex = make_plex()
        assert plex.load_from_cache(999) is None


class TestLoadListFromCache:
    def test_all_hit(self):
        items = {1: make_plex_item(rating_key=1), 2: make_plex_item(rating_key=2)}
        plex = make_plex(cached_items={k: (v, True) for k, v in items.items()})
        result = plex.load_list_from_cache([1, 2])
        assert len(result) == 2
        assert result[0] is items[1]

    def test_partial_miss(self):
        items = {1: make_plex_item(rating_key=1)}
        plex = make_plex(cached_items={1: (items[1], True)})
        result = plex.load_list_from_cache([1, 999])
        assert len(result) == 1
        assert result[0] is items[1]

    def test_all_miss(self):
        plex = make_plex()
        assert plex.load_list_from_cache([999, 888]) == []


# ═══════════════════════════════════════════════════════════════════════
# search / exact_search
# ═══════════════════════════════════════════════════════════════════════


class TestSearch:
    def test_search_calls_plex_library(self):
        mock_lib = MagicMock()
        mock_lib.search.return_value = [make_plex_item()]
        plex = make_plex(Plex=mock_lib)
        results = plex.search(title="Test", libtype="movie")
        mock_lib.search.assert_called_once_with(title="Test", sort=None, maxresults=None, libtype="movie")
        assert len(results) == 1

    def test_exact_search_with_year(self):
        mock_lib = MagicMock()
        mock_lib.search.return_value = [make_plex_item()]
        plex = make_plex(Plex=mock_lib)
        plex.exact_search(title="Test Movie", year=2023)
        mock_lib.search.assert_called_once_with(libtype=None, **{"title=": "Test Movie", "year": 2023})


# ═══════════════════════════════════════════════════════════════════════
# fetch_item
# ═══════════════════════════════════════════════════════════════════════


class TestFetchItem:
    def test_returns_cached_item(self):
        item = make_plex_item(rating_key=101)
        plex = make_plex(cached_items={101: (item, True)})
        plex.reload = MagicMock(return_value=item)
        result = plex.fetch_item(101)
        assert result is item

    def test_raises_failed_for_missing(self):
        from plexapi.exceptions import NotFound as PlexNotFound

        plex = make_plex()
        plex.fetchItem = MagicMock(side_effect=PlexNotFound("not found"))
        plex.item_reload = MagicMock()
        import modules.util as util

        with pytest.raises(util.Failed, match="not found"):
            plex.fetch_item(999)


# ═══════════════════════════════════════════════════════════════════════
# delete
# ═══════════════════════════════════════════════════════════════════════


class TestDelete:
    def test_delete_calls_server_delete(self):
        item = make_plex_item()
        plex = make_plex()
        plex.delete(item)
        item.delete.assert_called_once()


# ═══════════════════════════════════════════════════════════════════════
# saveMultiEdits retry behavior
# ═══════════════════════════════════════════════════════════════════════


class TestSaveMultiEditsRetry:
    def test_retries_twice_then_succeeds(self, monkeypatch):
        import modules.plex as plex_module

        plex = make_plex()
        plex.Plex.saveMultiEdits.side_effect = [ReadTimeout("timeout-1"), ReadTimeout("timeout-2"), None]
        sleep_mock = MagicMock()
        monkeypatch.setattr(plex_module.time, "sleep", sleep_mock)

        plex._save_multi_edits_with_retry()

        assert plex.Plex.saveMultiEdits.call_count == 3
        sleep_mock.assert_any_call(2)
        sleep_mock.assert_any_call(5)
        assert any("attempt 1 timed out" in message for message in plex_module.logger.info_messages)
        assert any("attempt 2 timed out" in message for message in plex_module.logger.info_messages)

    def test_restores_batch_state_between_timeouts(self, monkeypatch):
        import modules.plex as plex_module

        plex = make_plex()
        plex.Plex._edits = {"items": [MagicMock()], "title.value": "New Title"}
        call_count = 0

        def save_multi_edits():
            nonlocal call_count
            call_count += 1
            if plex.Plex._edits is None:
                raise BadRequest("Batch multi-editing mode not enabled. Must call `batchMultiEdits()` first.")
            plex.Plex._edits = None
            if call_count == 1:
                raise ReadTimeout("timeout-1")

        plex.Plex.saveMultiEdits.side_effect = save_multi_edits
        sleep_mock = MagicMock()
        monkeypatch.setattr(plex_module.time, "sleep", sleep_mock)

        plex._save_multi_edits_with_retry()

        assert call_count == 2
        assert plex.Plex._edits is None

    def test_raises_after_third_timeout(self, monkeypatch):
        import modules.plex as plex_module
        import modules.util as util

        plex = make_plex()
        plex.Plex.saveMultiEdits.side_effect = [ReadTimeout("timeout-1"), ReadTimeout("timeout-2"), ReadTimeout("timeout-3")]
        sleep_mock = MagicMock()
        monkeypatch.setattr(plex_module.time, "sleep", sleep_mock)

        with pytest.raises(util.Failed, match="Plex Error: saveMultiEdits did not respond within the 30-second timeout"):
            plex._save_multi_edits_with_retry()

        assert plex.Plex.saveMultiEdits.call_count == 3
        sleep_mock.assert_any_call(2)
        sleep_mock.assert_any_call(5)
        assert any("attempt 2 timed out" in message for message in plex_module.logger.info_messages)


# ═══════════════════════════════════════════════════════════════════════
# reload
# ═══════════════════════════════════════════════════════════════════════


class TestReload:
    def test_reload_cached_item_does_not_refetch(self):
        item = make_plex_item(rating_key=101)
        plex = make_plex(cached_items={101: (item, True)})
        plex.item_reload = MagicMock()
        result = plex.reload(item)
        assert result is item
        plex.item_reload.assert_not_called()

    def test_reload_uncached_item_fetches(self):
        item = make_plex_item(rating_key=101)
        plex = make_plex()
        plex.item_reload = MagicMock()
        result = plex.reload(item)
        assert result is item
        plex.item_reload.assert_called_once_with(item)


# ═══════════════════════════════════════════════════════════════════════
# Edge cases
# ═══════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    def test_collection_mode_query_calls_mode_update(self):
        """collection_mode_query calls modeUpdate on the collection."""
        plex = make_plex()
        collection = MagicMock()
        plex.collection_mode_query(collection, "default")
        collection.modeUpdate.assert_called_once_with(mode="default")

    def test_collection_order_query_calls_sort_update(self):
        plex = make_plex()
        collection = MagicMock()
        plex.collection_order_query(collection, "release")
        collection.sortUpdate.assert_called_once_with(sort="release")


# ═══════════════════════════════════════════════════════════════════════
# base_language_code
# ═══════════════════════════════════════════════════════════════════════


class TestBaseLanguageCode:
    @pytest.mark.parametrize(
        "value,expected",
        [
            # BCP-47/POSIX locale tags -> base language, via langcodes
            ("es-419", "es"),
            ("en-US", "en"),
            ("es-ES", "es"),
            ("es-MX", "es"),
            ("en_US", "en"),
            ("zh-Hans-CN", "zh"),
            ("sr-Latn-RS", "sr"),
            ("pt-BR", "pt"),
            # 3-letter ISO 639-2/3 codes -> ISO 639-1, including bibliographic vs
            # terminological pairs that differ from the 2-letter code (langcodes only)
            ("ita", "it"),
            ("deu", "de"),
            ("ger", "de"),
            ("chi", "zh"),
            ("fre", "fr"),
            ("spa", "es"),
            ("may", "ms"),
            ("bur", "my"),
            ("cze", "cs"),
            # langcodes normalizes casing
            ("EN", "en"),
            # already a bare 2-letter code
            ("es", "es"),
            # no 2-letter ISO 639-1 equivalent exists, so it passes through unchanged
            ("fil", "fil"),
            # separators langcodes can't parse fall back to the leading letter run
            ("en/USA", "en"),
            # not a language tag at all (langcodes rejects it) -> leading letter run
            ("PG-13", "PG"),
        ],
    )
    def test_normalizes_to_base_language_code(self, value, expected):
        assert plex_module.base_language_code(value) == expected

    def test_none_is_unchanged(self):
        assert plex_module.base_language_code(None) is None

    def test_empty_string_is_unchanged(self):
        assert plex_module.base_language_code("") == ""


# ═══════════════════════════════════════════════════════════════════════
# get_search_choices — audio/subtitle language region-tag normalization
# ═══════════════════════════════════════════════════════════════════════


def make_choice(title, key):
    """A minimal stand-in for plexapi's FilterChoice (only .title/.key are read)."""
    return SimpleNamespace(title=title, key=key)


class TestGetSearchChoicesLanguage:
    """Streams tagged with a full locale (e.g. "es-419", "en-US") must still be
    matchable by their base ISO 639-1 code (e.g. "es", "en"), for both movie and
    show libraries, since Plex may only expose the region-specific tag."""

    def test_movie_audio_language_resolves_bare_code_from_region_variant(self):
        plex = make_plex(is_show=False)
        plex.get_tags = MagicMock(return_value=[make_choice("Spanish (Latin America)", "es-419")])
        choices, _ = plex.get_search_choices("audio_language", title=False)
        assert choices["es"] == "es-419"
        assert choices["es-419"] == "es-419"

    def test_movie_subtitle_language_resolves_bare_code_from_region_variant(self):
        plex = make_plex(is_show=False)
        plex.get_tags = MagicMock(return_value=[make_choice("English (US)", "en-US")])
        choices, _ = plex.get_search_choices("subtitle_language", title=False)
        assert choices["en"] == "en-US"

    def test_show_episode_audio_language_resolves_bare_code(self):
        """TV show libraries route audio_language through episode.audioLanguage."""
        plex = make_plex(is_show=True)
        plex.get_tags = MagicMock(return_value=[make_choice("Spanish (Spain)", "es-ES")])
        choices, _ = plex.get_search_choices("audio_language", title=False)
        assert choices["es"] == "es-ES"

    def test_show_episode_subtitle_language_resolves_bare_code(self):
        plex = make_plex(is_show=True)
        plex.get_tags = MagicMock(return_value=[make_choice("Spanish (Mexico)", "es-MX")])
        choices, _ = plex.get_search_choices("subtitle_language", title=False)
        assert choices["es"] == "es-MX"

    def test_exact_bare_code_choice_wins_over_region_variant(self):
        """When Plex reports both a bare "es" tag and a region-specific "es-419" tag,
        an "es" query must resolve to the exact match, not the regional fallback."""
        plex = make_plex(is_show=False)
        plex.get_tags = MagicMock(return_value=[make_choice("Spanish (Latin America)", "es-419"), make_choice("Spanish", "es")])
        choices, _ = plex.get_search_choices("audio_language", title=False)
        assert choices["es"] == "es"

    def test_exact_bare_code_choice_wins_regardless_of_order(self):
        plex = make_plex(is_show=False)
        plex.get_tags = MagicMock(return_value=[make_choice("Spanish", "es"), make_choice("Spanish (Latin America)", "es-419")])
        choices, _ = plex.get_search_choices("audio_language", title=False)
        assert choices["es"] == "es"

    def test_plain_code_untouched_when_no_region_variant(self):
        plex = make_plex(is_show=False)
        plex.get_tags = MagicMock(return_value=[make_choice("English", "en")])
        choices, _ = plex.get_search_choices("audio_language", title=False)
        assert choices["en"] == "en"

    def test_non_language_field_is_not_stripped(self):
        """Hyphenated values in unrelated tag fields (e.g. content_rating) must be left alone."""
        plex = make_plex(is_show=False)
        plex.get_tags = MagicMock(return_value=[make_choice("PG-13", "PG-13")])
        choices, _ = plex.get_search_choices("content_rating", title=False)
        assert choices["pg-13"] == "PG-13"
        assert "pg" not in choices


# ═══════════════════════════════════════════════════════════════════════
# check_filter — audio/subtitle language region-tag normalization
# (the manual "filters:" attribute path, separate from plex_search)
# ═══════════════════════════════════════════════════════════════════════


def make_audio_stream(language=None, languageCode=None, languageTag=None):
    return SimpleNamespace(language=language, languageCode=languageCode, languageTag=languageTag, extendedDisplayTitle=None)


def make_movie_with_streams(audio_streams=None, subtitle_streams=None):
    part = SimpleNamespace(audioStreams=lambda: audio_streams or [], subtitleStreams=lambda: subtitle_streams or [])
    media = SimpleNamespace(parts=[part])
    item = MagicMock(spec=Movie)
    item.media = [media]
    return item


class TestCheckFilterLanguage:
    def make_plex_for_filter(self):
        plex = make_plex(is_show=False)
        plex.reload = MagicMock(side_effect=lambda item, force=False: item)
        return plex

    def test_matches_region_tagged_audio_stream_on_base_code(self):
        """A stream tagged "es-419" (no plain "es" anywhere) must still satisfy an
        audio_language: es filter."""
        plex = self.make_plex_for_filter()
        item = make_movie_with_streams(audio_streams=[make_audio_stream(language="Spanish (Latin America)", languageCode="es-419", languageTag="es-419")])
        assert plex.check_filter(item, "audio_language", "", "audio_language", ["es"], None) is True

    def test_matches_underscore_tagged_subtitle_stream_on_base_code(self):
        plex = self.make_plex_for_filter()
        item = make_movie_with_streams(subtitle_streams=[make_audio_stream(language="English (US)", languageCode="en_US", languageTag="en_US")])
        assert plex.check_filter(item, "subtitle_language", "", "subtitle_language", ["en"], None) is True

    def test_does_not_match_unrelated_language(self):
        plex = self.make_plex_for_filter()
        item = make_movie_with_streams(audio_streams=[make_audio_stream(language="French", languageCode="fre", languageTag="fr")])
        assert plex.check_filter(item, "audio_language", "", "audio_language", ["es"], None) is False

    def test_plain_code_still_matches_without_region(self):
        plex = self.make_plex_for_filter()
        item = make_movie_with_streams(audio_streams=[make_audio_stream(language="English", languageCode="eng", languageTag="en")])
        assert plex.check_filter(item, "audio_language", "", "audio_language", ["en"], None) is True

    def test_matches_bibliographic_three_letter_code_with_no_language_tag(self):
        """Plex/ffprobe commonly tag streams with a plain ISO 639-2 code and nothing else.
        "ita"/"deu"/"chi" have no separator for a regex to split on, and some (like the
        bibliographic "chi" for Chinese) aren't even a prefix of their ISO 639-1 code ("zh"),
        so this only works via a real language-tag lookup (langcodes), not string splitting."""
        plex = self.make_plex_for_filter()
        item = make_movie_with_streams(audio_streams=[make_audio_stream(language="Italian", languageCode="ita", languageTag=None)])
        assert plex.check_filter(item, "audio_language", "", "audio_language", ["it"], None) is True

    def test_matches_chinese_bibliographic_code_despite_no_shared_prefix(self):
        plex = self.make_plex_for_filter()
        item = make_movie_with_streams(audio_streams=[make_audio_stream(language="Chinese", languageCode="chi", languageTag=None)])
        assert plex.check_filter(item, "audio_language", "", "audio_language", ["zh"], None) is True

    def test_different_locale_variants_all_match_the_same_single_filter(self):
        """This is the scenario plex_search can't handle: Plex only exact-matches one locale key
        per query, so a library mixing "es-419" and "es-MX" titles needs two separate plex_search
        queries. Routed through plex_all + filters/check_filter instead, one ["es"] filter_data
        list must match items carrying either variant."""
        plex = self.make_plex_for_filter()
        item_419 = make_movie_with_streams(audio_streams=[make_audio_stream(language="Spanish (Latin America)", languageCode="es-419", languageTag="es-419")])
        item_mx = make_movie_with_streams(audio_streams=[make_audio_stream(language="Spanish (Mexico)", languageCode="es-MX", languageTag="es-MX")])
        assert plex.check_filter(item_419, "audio_language", "", "audio_language", ["es"], None) is True
        assert plex.check_filter(item_mx, "audio_language", "", "audio_language", ["es"], None) is True
