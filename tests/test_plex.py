"""Tests for modules/plex.py — the Plex class.

Focuses on methods that can be tested in isolation without a real Plex
server connection.  Test instances are created via ``Plex.__new__`` with
manually-set attributes.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401 — pre-import to break circular deps
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
