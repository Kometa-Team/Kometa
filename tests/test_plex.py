"""Tests for modules/plex.py — the Plex class.

Focuses on methods that can be tested in isolation without a real Plex
server connection.  Test instances are created via ``Plex.__new__`` with
manually-set attributes.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import cast
from unittest.mock import MagicMock

import pytest
from plexapi.exceptions import BadRequest, NotFound
from requests.exceptions import ConnectionError, ReadTimeout
from tenacity import wait_none

import modules.builder  # noqa: F401 — pre-import to break circular deps
from modules.plex import Plex
from modules.util import Failed
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
    plex.filter_attr_cache = attrs.pop("filter_attr_cache", {})
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
# image_update
# ═══════════════════════════════════════════════════════════════════════


class TestImageUpdate:
    def test_tmdb_reset_returns_structured_result_and_logs_success(self):
        import modules.plex as plex_module

        plex = make_plex(mass_poster_update={"source": "tmdb", "language": None})
        plex.upload_poster = MagicMock()
        plex.item_labels = MagicMock(return_value=[])

        result = plex.image_update(make_plex_item(), None, tmdb=("tmdb", "https://image.tmdb.org/poster.jpg"), title="S01E01")

        assert result == ("Reset", "TMDb", "Updated")
        plex.upload_poster.assert_called_once()
        assert "S01E01 Poster | Reset from TMDb" in plex_module.logger.info_messages

    def test_missing_tmdb_reset_returns_missing_result_and_keeps_warning(self):
        import modules.plex as plex_module

        plex = make_plex(mass_poster_update={"source": "tmdb", "language": None})

        result = plex.image_update(make_plex_item(), None, tmdb=("tmdb", None), title="S01E01")

        assert result == ("Reset", "TMDb", "Missing")
        assert "S01E01 Poster | No Reset Image Found" in plex_module.logger.warning_messages

    def test_asset_reset_is_counted_under_actual_source(self):
        plex = make_plex(mass_poster_update={"source": "tmdb", "language": None})
        plex.upload_poster = MagicMock()
        plex.item_labels = MagicMock(return_value=[])

        result = plex.image_update(make_plex_item(), SimpleNamespace(location="/assets/poster.jpg"), tmdb=("tmdb", "https://image.tmdb.org/poster.jpg"))

        assert result == ("Reset", "Assets", "Updated")


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
        assert kwargs.get("library") == "Test Library"

    def test_notify_playlist_delete_omits_library(self):
        mock_config = MagicMock()
        plex = make_plex(config=mock_config, PlexServer=SimpleNamespace(friendlyName="MyServer"))
        plex.notify_delete("Playlist removed", playlist=True)
        mock_config.notify_delete.assert_called_once_with("Playlist removed", server="MyServer", library=None)


# ═══════════════════════════════════════════════════════════════════════
# search keys
# ═══════════════════════════════════════════════════════════════════════


class TestSearchKeys:
    def test_folder_location_uses_plex_source_filter(self):
        list_filters = MagicMock(
            return_value=[
                SimpleNamespace(filter="genre", title="Genre"),
                SimpleNamespace(filter="source", title="Folder Location"),
            ]
        )
        section = SimpleNamespace(
            TYPE="movie",
            listFilters=list_filters,
        )
        plex = make_plex(Plex=section)

        assert plex.get_search_key("folder_location") == "source"
        list_filters.assert_called_once_with("movie")

    def test_folder_location_uses_requested_track_filter_type(self):
        list_filters = MagicMock(return_value=[SimpleNamespace(filter="source", title="Folder Location")])
        section = SimpleNamespace(TYPE="artist", listFilters=list_filters)
        plex = make_plex(Plex=section, is_movie=False, type="Music")

        assert plex.get_search_key("folder_location", libtype="track") == "source"
        list_filters.assert_called_once_with("track")

    def test_folder_location_falls_back_to_filter_title(self):
        section = SimpleNamespace(
            TYPE="movie",
            listFilters=lambda libtype: [SimpleNamespace(filter="location", title="Folder Location")],
        )
        plex = make_plex(Plex=section)

        assert plex.get_search_key("folder_location") == "location"

    def test_folder_location_choices_map_paths_to_plex_location_ids(self):
        list_filters = MagicMock(return_value=[SimpleNamespace(filter="source", title="Folder Location")])
        section = SimpleNamespace(
            TYPE="movie",
            listFilters=list_filters,
        )
        plex = make_plex(Plex=section)
        plex.get_tags = MagicMock(
            return_value=[
                SimpleNamespace(title="/media/movies", key="7"),
                SimpleNamespace(title="/media/movies-4k", key="8"),
            ]
        )

        choices, names = plex.get_search_choices("folder_location", title=False, libtype="track")

        assert choices["/media/movies"] == "7"
        assert choices["/media/movies-4k"] == "8"
        assert names == ["/media/movies", "/media/movies-4k"]
        list_filters.assert_called_once_with("track")
        plex.get_tags.assert_called_once_with("source")

    def test_folder_location_raises_when_plex_does_not_expose_filter(self):
        section = SimpleNamespace(
            TYPE="movie",
            listFilters=lambda libtype: [SimpleNamespace(filter="genre", title="Genre")],
        )
        plex = make_plex(Plex=section)

        with pytest.raises(NotFound, match="folder_location"):
            plex.get_search_key("folder_location")

        with pytest.raises(Failed, match="folder_location not supported"):
            plex.get_search_choices("folder_location")


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
    def test_delete_calls_server_delete_and_notifies_collection(self):
        item = make_plex_item(type="collection")
        mock_config = MagicMock()
        plex = make_plex(config=mock_config, PlexServer=SimpleNamespace(friendlyName="MyServer"))
        plex.delete(item)
        item.delete.assert_called_once()
        mock_config.notify_delete.assert_called_once_with("Collection Test Item deleted", server="MyServer", library="Test Library")

    def test_delete_notifies_playlist_without_library(self):
        item = make_plex_item(title="My Playlist", type="playlist")
        mock_config = MagicMock()
        plex = make_plex(config=mock_config, PlexServer=SimpleNamespace(friendlyName="MyServer"))

        plex.delete(item)

        mock_config.notify_delete.assert_called_once_with("Playlist My Playlist deleted", server="MyServer", library=None)

    def test_delete_can_suppress_notification(self):
        item = make_plex_item(type="playlist")
        mock_config = MagicMock()
        plex = make_plex(config=mock_config)

        plex.delete(item, notify=False)

        item.delete.assert_called_once()
        mock_config.notify_delete.assert_not_called()

    def test_failed_delete_does_not_notify(self):
        item = make_plex_item(type="collection")
        mock_config = MagicMock()
        plex = make_plex(config=mock_config)
        plex.query = MagicMock(side_effect=RuntimeError("delete failed"))

        with pytest.raises(Failed, match="Plex Error: Failed to delete Test Item"):
            plex.delete(item)

        mock_config.notify_delete.assert_not_called()

    def test_delete_user_playlist_includes_user(self):
        item = make_plex_item(title="My Playlist", type="playlist")
        mock_config = MagicMock()
        server = MagicMock()
        server.friendlyName = "MyServer"
        server.switchUser.return_value.playlist.return_value = item
        plex = make_plex(config=mock_config, PlexServer=server)

        plex.delete_user_playlist("My Playlist", "Friend")

        mock_config.notify_delete.assert_called_once_with("Playlist My Playlist deleted on User Friend", server="MyServer", library=None)

    def test_delete_user_playlist_can_suppress_notification(self):
        item = make_plex_item(title="My Playlist", type="playlist")
        mock_config = MagicMock()
        server = MagicMock()
        server.switchUser.return_value.playlist.return_value = item
        plex = make_plex(config=mock_config, PlexServer=server)

        plex.delete_user_playlist("My Playlist", "Friend", notify=False)

        item.delete.assert_called_once()
        mock_config.notify_delete.assert_not_called()


# ═══════════════════════════════════════════════════════════════════════
# moveItem retry behavior
# ═════════════════════════════════════════════════════════════════════


class TestMoveItemRetry:
    def test_bad_request_raises_failed_without_retry_error(self):
        import modules.util as util

        plex = make_plex()
        collection = MagicMock()
        collection.moveItem.side_effect = BadRequest("400 Bad Request")
        item = make_plex_item(title="Test Movie")

        with pytest.raises(util.Failed, match="Plex Error: Failed to move Test Movie: 400 Bad Request"):
            plex.moveItem(collection, item, None)

        collection.moveItem.assert_called_once_with(item, after=None)


class TestPlexRetryPolicy:
    def test_failed_is_terminal_for_generic_query(self):
        plex = make_plex()
        method = MagicMock(side_effect=Failed("terminal failure"))

        with pytest.raises(Failed, match="terminal failure"):
            plex.query(method)

        method.assert_called_once_with()

    def test_reload_wrapped_failed_is_terminal(self):
        plex = make_plex()
        plex.item_reload = MagicMock(side_effect=BadRequest("400 Bad Request"))
        item = make_plex_item(title="Test Movie")

        with pytest.raises(Failed, match="Item Failed to Load: 400 Bad Request"):
            plex.reload(item)

        plex.item_reload.assert_called_once_with(item)

    def test_query_collection_wraps_bad_request_without_retrying(self, monkeypatch):
        plex = make_plex()
        item = make_plex_item(title="Test Movie")
        item.addCollection.side_effect = BadRequest("400 Bad Request")
        monkeypatch.setattr(Plex.query_collection.retry, "wait", wait_none())

        with pytest.raises(Failed, match="Plex Error: Failed to add collection 'Favorites' to Test Movie: 400 Bad Request"):
            plex.query_collection(item, "Favorites")

        item.addCollection.assert_called_once_with("Favorites", locked=True)

    def test_get_actor_id_wraps_bad_request_without_retrying(self, monkeypatch):
        plex = make_plex()
        plex.Plex.hubSearch.side_effect = BadRequest("400 Bad Request")
        monkeypatch.setattr(Plex.get_actor_id.retry, "wait", wait_none())

        with pytest.raises(Failed, match="Plex Error: Failed to find person ID for 'Example Person': 400 Bad Request"):
            plex.get_actor_id("Example Person")

        plex.Plex.hubSearch.assert_called_once_with("Example Person")

    def test_exhausted_transient_error_reraises_underlying_exception(self, monkeypatch):
        plex = make_plex()
        plex.Plex.search.side_effect = ConnectionError("connection lost")
        monkeypatch.setattr(Plex.search.retry, "wait", wait_none())

        with pytest.raises(ConnectionError, match="connection lost"):
            plex.search(title="Test")

        assert plex.Plex.search.call_count == 6


# ════════════════════════════════════════════════════════════════════
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

    def test_real_reload_clears_filter_attr_cache_for_that_item(self):
        item = make_plex_item(rating_key=101)
        plex = make_plex(filter_attr_cache={(101, "genres"): ["stale"], (202, "genres"): ["untouched"]})
        plex.item_reload = MagicMock()
        plex.reload(item, force=True)
        assert (101, "genres") not in plex.filter_attr_cache
        assert (202, "genres") in plex.filter_attr_cache, "a different item's cached entries must not be touched"

    def test_cache_hit_reload_does_not_clear_filter_attr_cache(self):
        item = make_plex_item(rating_key=101)
        plex = make_plex(cached_items={101: (item, True)}, filter_attr_cache={(101, "genres"): ["Action"]})
        plex.item_reload = MagicMock()
        plex.reload(item)
        plex.item_reload.assert_not_called()
        assert plex.filter_attr_cache[(101, "genres")] == ["Action"]


# ═══════════════════════════════════════════════════════════════════════
# check_filters / check_filter reload dedup
# ═══════════════════════════════════════════════════════════════════════


class TestCheckFiltersReloadDedup:
    def test_first_tag_filter_forces_reload_second_does_not(self):
        plex = make_plex()
        plex.check_filter = MagicMock(return_value=True)
        item = make_plex_item()
        filters_in = [("genre", ["Action"]), ("label", ["Test"])]

        plex.check_filters(item, filters_in, None)

        first_call, second_call = plex.check_filter.call_args_list
        assert first_call.kwargs["force_reload"] is True
        assert second_call.kwargs["force_reload"] is False

    def test_non_tag_filter_never_forces_reload(self):
        plex = make_plex()
        plex.check_filter = MagicMock(return_value=True)
        item = make_plex_item()
        filters_in = [("title", ["Something"])]

        plex.check_filters(item, filters_in, None)

        assert plex.check_filter.call_args_list[0].kwargs["force_reload"] is False

    def test_mixed_filters_only_first_tag_filter_forces(self):
        plex = make_plex()
        plex.check_filter = MagicMock(return_value=True)
        item = make_plex_item()
        filters_in = [("title", ["Something"]), ("genre", ["Action"]), ("collection", ["Marvel"])]

        plex.check_filters(item, filters_in, None)

        calls = plex.check_filter.call_args_list
        assert calls[0].kwargs["force_reload"] is False  # title - never a tag filter
        assert calls[1].kwargs["force_reload"] is True  # genre - first tag filter this call
        assert calls[2].kwargs["force_reload"] is False  # collection - already reloaded this call

    def test_dedup_state_does_not_leak_across_separate_calls(self):
        """Each check_filters call is for a distinct item, so a fresh call must force again."""
        plex = make_plex()
        plex.check_filter = MagicMock(return_value=True)
        item_a = make_plex_item(rating_key=1)
        item_b = make_plex_item(rating_key=2)
        filters_in = [("genre", ["Action"])]

        plex.check_filters(item_a, filters_in, None)
        plex.check_filters(item_b, filters_in, None)

        assert plex.check_filter.call_args_list[0].kwargs["force_reload"] is True
        assert plex.check_filter.call_args_list[1].kwargs["force_reload"] is True

    def test_short_circuits_on_first_failing_filter(self):
        """A failing filter still short-circuits check_filters (dedup change must not affect this)."""
        plex = make_plex()
        plex.check_filter = MagicMock(side_effect=[False, True])
        item = make_plex_item()
        filters_in = [("genre", ["Action"]), ("label", ["Test"])]

        result = plex.check_filters(item, filters_in, None)

        assert result is False
        assert plex.check_filter.call_count == 1


class TestCheckFilterForceReloadParam:
    def _movie_item(self, genres=None, labels=None):
        from plexapi.video import Movie

        item = MagicMock(spec=Movie)
        item.ratingKey = 1
        item.genres = genres if genres is not None else [MagicMock(tag="Action")]
        item.labels = labels if labels is not None else [MagicMock(tag="Test")]
        return item

    def test_force_reload_true_passed_through_to_reload(self):
        plex = make_plex()
        item = self._movie_item()
        plex.reload = MagicMock(return_value=item)

        plex.check_filter(item, "genre", "", "genre", ["Action"], None, force_reload=True)

        plex.reload.assert_called_once_with(item, force=True)

    def test_force_reload_false_passed_through_to_reload(self):
        plex = make_plex()
        item = self._movie_item()
        plex.reload = MagicMock(return_value=item)

        plex.check_filter(item, "genre", "", "genre", ["Action"], None, force_reload=False)

        plex.reload.assert_called_once_with(item, force=False)

    def test_force_reload_none_falls_back_to_old_always_force_behavior(self):
        """Only a direct caller that bypasses check_filters would hit this - kept for safety."""
        plex = make_plex()
        item = self._movie_item()
        plex.reload = MagicMock(return_value=item)

        plex.check_filter(item, "genre", "", "genre", ["Action"], None, force_reload=None)

        plex.reload.assert_called_once_with(item, force=True)

    def test_force_reload_none_for_non_tag_filter_does_not_force(self):
        plex = make_plex()
        item = self._movie_item()
        item.title = "Something"
        plex.reload = MagicMock(return_value=item)

        plex.check_filter(item, "title", "", "title", ["Something"], None, force_reload=None)

        plex.reload.assert_called_once_with(item, force=False)


# ═══════════════════════════════════════════════════════════════════════
# cached_item_attr - the per-run memo for check_filter's plain attribute reads
# ═══════════════════════════════════════════════════════════════════════


class TestCachedItemAttr:
    def test_first_read_hits_the_real_attribute(self):
        plex = make_plex()
        item = make_plex_item(rating_key=1, genres=["Action"])
        assert plex.cached_item_attr(item, "genres") == ["Action"]

    def test_repeat_read_returns_memoized_value_without_touching_the_item_again(self):
        plex = make_plex()
        item = MagicMock()
        item.ratingKey = 1
        item.genres = ["Action"]
        plex.cached_item_attr(item, "genres")
        item.genres = ["Changed"]  # if the memo weren't working, the second read would see this
        assert plex.cached_item_attr(item, "genres") == ["Action"]

    def test_different_items_get_independent_cache_entries(self):
        plex = make_plex()
        item_a = make_plex_item(rating_key=1, genres=["Action"])
        item_b = make_plex_item(rating_key=2, genres=["Comedy"])
        assert plex.cached_item_attr(item_a, "genres") == ["Action"]
        assert plex.cached_item_attr(item_b, "genres") == ["Comedy"]

    def test_different_attributes_on_the_same_item_get_independent_cache_entries(self):
        plex = make_plex()
        item = make_plex_item(rating_key=1, genres=["Action"], labels=["Test"])
        assert plex.cached_item_attr(item, "genres") == ["Action"]
        assert plex.cached_item_attr(item, "labels") == ["Test"]


# ═══════════════════════════════════════════════════════════════════════
# check_filter - which attribute reads are cached vs. always read live
#
# genre/label/collection are protected by check_filters' own force-reload dedup above; every other
# cached attribute here is never written by Kometa anywhere, so a per-run memo changes nothing about
# the value ever returned. summary/editionTitle are the one pair confirmed writable by update_details
# with no cache eviction anywhere - these must stay live, not cached, and this must not silently
# regress if someone "helpfully" converts them later.
# ═══════════════════════════════════════════════════════════════════════


class TestCheckFilterCachingScope:
    def _movie_item(self, **extras):
        from plexapi.video import Movie

        item = MagicMock(spec=Movie)
        item.ratingKey = 1
        for key, value in extras.items():
            setattr(item, key, value)
        return item

    def test_has_collection_is_cached(self):
        plex = make_plex()
        item = self._movie_item(collections=[MagicMock(tag="Marvel")])
        plex.reload = MagicMock(return_value=item)
        plex.check_filter(item, "has_collection", "", "has_collection", True, None, force_reload=False)
        item.collections = []  # if cached correctly, this change must not be seen on the next call
        result = plex.check_filter(item, "has_collection", "", "has_collection", True, None, force_reload=False)
        assert result is True, "second call must still see the cached (pre-change) collections list"

    def test_has_edition_is_never_cached(self):
        # editionTitle is writable by update_details with no cache eviction - must always read live.
        plex = make_plex()
        item = self._movie_item(editionTitle="Director's Cut")
        plex.reload = MagicMock(return_value=item)
        plex.check_filter(item, "has_edition", "", "has_edition", True, None, force_reload=False)
        item.editionTitle = None
        result = plex.check_filter(item, "has_edition", "", "has_edition", True, None, force_reload=False)
        assert result is False, "has_edition must see the live value, not a stale cached one"
        assert (1, "editionTitle") not in plex.filter_attr_cache

    def test_summary_string_filter_is_never_cached(self):
        plex = make_plex()
        item = self._movie_item(summary="Original summary")
        plex.reload = MagicMock(return_value=item)
        plex.check_filter(item, "summary", "", "summary", ["Original summary"], None, force_reload=False)
        item.summary = "Changed summary"
        plex.check_filter(item, "summary", "", "summary", ["Changed summary"], None, force_reload=False)
        assert (1, "summary") not in plex.filter_attr_cache

    def test_title_string_filter_is_cached(self):
        # title is written only via operations.py's mass-edit path, which explicitly evicts cached_items - safe to cache here.
        plex = make_plex()
        item = self._movie_item(title="Original Title")
        plex.reload = MagicMock(return_value=item)
        plex.check_filter(item, "title", "", "title", ["Original Title"], None, force_reload=False)
        assert (1, "title") in plex.filter_attr_cache


# ═══════════════════════════════════════════════════════════════════════
# tag_diff / batch_edit_tags
# ═══════════════════════════════════════════════════════════════════════


class TestTagDiff:
    def test_add_only(self):
        add, remove = Plex.tag_diff(["Action"], add_tags=["Drama"])
        assert add == ["Drama"]
        assert remove == []

    def test_add_skips_already_present(self):
        add, remove = Plex.tag_diff(["Action", "Drama"], add_tags=["Drama"])
        assert add == []
        assert remove == []

    def test_remove_only(self):
        add, remove = Plex.tag_diff(["Action", "Drama"], remove_tags=["Drama"])
        assert add == []
        assert remove == ["Drama"]

    def test_remove_absent_tag_is_noop(self):
        add, remove = Plex.tag_diff(["Action"], remove_tags=["Drama"])
        assert add == []
        assert remove == []

    def test_sync_removes_extraneous_and_adds_missing(self):
        add, remove = Plex.tag_diff(["Action", "Horror"], sync_tags=["Action", "Drama"])
        assert add == ["Drama"]
        assert remove == ["Horror"]

    def test_sync_with_nothing_to_change(self):
        add, remove = Plex.tag_diff(["Action", "Drama"], sync_tags=["Action", "Drama"])
        assert add == []
        assert remove == []

    def test_no_args_is_noop(self):
        add, remove = Plex.tag_diff(["Action"])
        assert add == []
        assert remove == []


class TestBatchEditTags:
    def test_noop_when_no_items(self):
        plex = make_plex()
        mock_section = cast(MagicMock, plex.Plex)
        plex.batch_edit_tags([], "label", add_tags=["Overlay"])
        mock_section.batchMultiEdits.assert_not_called()

    def test_noop_when_no_tags(self):
        plex = make_plex()
        mock_section = cast(MagicMock, plex.Plex)
        item = make_plex_item()
        plex.batch_edit_tags([item], "label")
        mock_section.batchMultiEdits.assert_not_called()

    def test_rejects_unsupported_attr(self):
        plex = make_plex()
        item = make_plex_item()
        with pytest.raises(NotImplementedError):
            plex.batch_edit_tags([item], "director", add_tags=["Someone"])

    def test_add_and_remove_labels_batched_once(self):
        plex = make_plex()
        mock_section = cast(MagicMock, plex.Plex)
        plex._save_multi_edits_with_retry = MagicMock()
        items = [make_plex_item(rating_key=i) for i in range(3)]

        plex.batch_edit_tags(items, "label", add_tags={"Overlay"}, remove_tags={"Stale"})

        mock_section.batchMultiEdits.assert_called_once_with(items)
        mock_section.addLabel.assert_called_once_with(["Overlay"], locked=True)
        mock_section.removeLabel.assert_called_once_with(["Stale"], locked=True)
        plex._save_multi_edits_with_retry.assert_called_once()

    def test_add_only_does_not_call_remove_method(self):
        plex = make_plex()
        mock_section = cast(MagicMock, plex.Plex)
        plex._save_multi_edits_with_retry = MagicMock()
        items = [make_plex_item()]

        plex.batch_edit_tags(items, "genre", add_tags={"Drama"})

        mock_section.addGenre.assert_called_once_with(["Drama"], locked=True)
        mock_section.removeGenre.assert_not_called()

    def test_chunks_large_batches(self):
        plex = make_plex()
        mock_section = cast(MagicMock, plex.Plex)
        plex._save_multi_edits_with_retry = MagicMock()
        items = [make_plex_item(rating_key=i) for i in range(150)]

        plex.batch_edit_tags(items, "label", add_tags={"Overlay"})

        assert mock_section.batchMultiEdits.call_count == 2
        assert plex._save_multi_edits_with_retry.call_count == 2

    def test_mixed_item_types_batched_separately(self):
        # Regression: batchMultiEdits() raises BadRequest("Cannot mix items of different type") if a chunk isn't homogeneous.
        plex = make_plex()
        mock_section = cast(MagicMock, plex.Plex)
        plex._save_multi_edits_with_retry = MagicMock()
        shows = [make_plex_item(rating_key=i, type="show") for i in range(2)]
        seasons = [make_plex_item(rating_key=i + 10, type="season") for i in range(2)]

        plex.batch_edit_tags(shows + seasons, "label", add_tags={"Overlay"})

        assert mock_section.batchMultiEdits.call_count == 2
        called_chunks = [call.args[0] for call in mock_section.batchMultiEdits.call_args_list]
        assert called_chunks == [shows, seasons]


class TestBatchAddLabel:
    def test_noop_when_no_items(self):
        plex = make_plex()
        mock_section = cast(MagicMock, plex.Plex)
        plex.batch_add_label([], "Overlay")
        mock_section.batchMultiEdits.assert_not_called()

    def test_adds_label_to_all_items_in_one_batch(self):
        plex = make_plex()
        mock_section = cast(MagicMock, plex.Plex)
        plex._save_multi_edits_with_retry = MagicMock()
        items = [make_plex_item(rating_key=i) for i in range(3)]

        plex.batch_add_label(items, "Overlay")

        mock_section.batchMultiEdits.assert_called_once_with(items)
        mock_section.addLabel.assert_called_once_with("Overlay")
        plex._save_multi_edits_with_retry.assert_called_once()

    def test_chunks_large_batches(self):
        plex = make_plex()
        mock_section = cast(MagicMock, plex.Plex)
        plex._save_multi_edits_with_retry = MagicMock()
        items = [make_plex_item(rating_key=i) for i in range(150)]

        plex.batch_add_label(items, "Overlay")

        assert mock_section.batchMultiEdits.call_count == 2
        assert plex._save_multi_edits_with_retry.call_count == 2

    def test_mixed_item_types_batched_separately(self):
        # Regression: overlays.py accumulates overlay_label_items across a whole library run, which can span shows and seasons.
        plex = make_plex()
        mock_section = cast(MagicMock, plex.Plex)
        plex._save_multi_edits_with_retry = MagicMock()
        shows = [make_plex_item(rating_key=i, type="show") for i in range(2)]
        seasons = [make_plex_item(rating_key=i + 10, type="season") for i in range(2)]

        plex.batch_add_label(shows + seasons, "Overlay")

        assert mock_section.batchMultiEdits.call_count == 2
        called_chunks = [call.args[0] for call in mock_section.batchMultiEdits.call_args_list]
        assert called_chunks == [shows, seasons]


class TestBatchAddLabel:
    def test_noop_when_no_items(self):
        plex = make_plex()
        mock_section = cast(MagicMock, plex.Plex)
        plex.batch_add_label([], "Overlay")
        mock_section.batchMultiEdits.assert_not_called()

    def test_adds_label_to_all_items_in_one_batch(self):
        plex = make_plex()
        mock_section = cast(MagicMock, plex.Plex)
        plex._save_multi_edits_with_retry = MagicMock()
        items = [make_plex_item(rating_key=i) for i in range(3)]

        plex.batch_add_label(items, "Overlay")

        mock_section.batchMultiEdits.assert_called_once_with(items)
        mock_section.addLabel.assert_called_once_with("Overlay")
        plex._save_multi_edits_with_retry.assert_called_once()

    def test_chunks_large_batches(self):
        plex = make_plex()
        mock_section = cast(MagicMock, plex.Plex)
        plex._save_multi_edits_with_retry = MagicMock()
        items = [make_plex_item(rating_key=i) for i in range(150)]

        plex.batch_add_label(items, "Overlay")

        assert mock_section.batchMultiEdits.call_count == 2
        assert plex._save_multi_edits_with_retry.call_count == 2


class TestBatchEditField:
    def test_noop_when_no_items(self):
        plex = make_plex()
        mock_section = cast(MagicMock, plex.Plex)
        plex.batch_edit_field([], "rating", 5.5)
        mock_section.batchMultiEdits.assert_not_called()

    def test_sets_same_value_for_whole_batch(self):
        plex = make_plex()
        mock_section = cast(MagicMock, plex.Plex)
        plex._save_multi_edits_with_retry = MagicMock()
        items = [make_plex_item(rating_key=i) for i in range(3)]

        plex.batch_edit_field(items, "rating", 5.5)

        mock_section.batchMultiEdits.assert_called_once_with(items)
        mock_section.editField.assert_called_once_with("rating", 5.5, locked=True)
        plex._save_multi_edits_with_retry.assert_called_once()

    def test_chunks_large_batches(self):
        plex = make_plex()
        mock_section = cast(MagicMock, plex.Plex)
        plex._save_multi_edits_with_retry = MagicMock()
        items = [make_plex_item(rating_key=i) for i in range(150)]

        plex.batch_edit_field(items, "rating", 5.5)

        assert mock_section.batchMultiEdits.call_count == 2
        assert plex._save_multi_edits_with_retry.call_count == 2

    def test_mixed_item_types_batched_separately(self):
        # Regression: item_critic/audience/user_rating batches can span shows and seasons in the same library run.
        plex = make_plex()
        mock_section = cast(MagicMock, plex.Plex)
        plex._save_multi_edits_with_retry = MagicMock()
        shows = [make_plex_item(rating_key=i, type="show") for i in range(2)]
        seasons = [make_plex_item(rating_key=i + 10, type="season") for i in range(2)]

        plex.batch_edit_field(shows + seasons, "rating", 5.5)

        assert mock_section.batchMultiEdits.call_count == 2
        called_chunks = [call.args[0] for call in mock_section.batchMultiEdits.call_args_list]
        assert called_chunks == [shows, seasons]


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
