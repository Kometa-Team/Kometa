"""Regression coverage for ordered, linear-time builder item deduplication."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import modules.builder as builder_module
from tests.conftest import FakeLogger
from tests.factories import make_builder


class KeyedEpisode:
    key_reads = 0

    def __init__(self, rating_key):
        self.ratingKey = rating_key
        self.title = f"Episode {rating_key}"

    @property
    def key(self):
        type(self).key_reads += 1
        return f"/library/metadata/{self.ratingKey}"

    def __eq__(self, other):
        raise AssertionError("Deduplication must not scan Plex objects with equality comparisons")


@pytest.fixture
def episode_builder(monkeypatch):
    monkeypatch.setattr(builder_module, "logger", FakeLogger())
    monkeypatch.setattr(builder_module, "Episode", KeyedEpisode)
    monkeypatch.setattr(builder_module.util, "item_title", lambda item: item.title)
    KeyedEpisode.key_reads = 0
    library = SimpleNamespace(fetch_item=MagicMock())
    builder = make_builder(builder_level="episode", library=library)
    builder.check_filters = MagicMock(return_value=True)
    builder.check_value_filter = MagicMock(return_value=True)
    return builder


def collect(builder, items):
    builder.library.fetch_item.side_effect = items
    builder.filter_and_save_items([(index + 1, "ratingKey") for index in range(len(items))])


def test_distinct_instances_with_the_same_plex_key_keep_first_seen_order(episode_builder):
    builder = episode_builder
    first = KeyedEpisode(3)
    second = KeyedEpisode(1)
    third = KeyedEpisode(2)

    collect(builder, [first, second, KeyedEpisode("3"), third, KeyedEpisode(1)])

    assert [item.ratingKey for item in builder.found_items] == [3, 1, 2]
    assert builder.found_items[0] is first
    assert builder.found_items[1] is second
    assert builder.found_items[2] is third
    assert builder.check_filters.call_count == 3
    assert builder.check_value_filter.call_count == 3


def test_later_builders_skip_existing_items_and_retain_order(episode_builder):
    builder = episode_builder
    collect(builder, [KeyedEpisode(2), KeyedEpisode(1)])
    builder.check_filters.reset_mock()
    builder.check_value_filter.reset_mock()

    collect(builder, [KeyedEpisode(1), KeyedEpisode(3), KeyedEpisode(2)])

    assert [item.ratingKey for item in builder.found_items] == [2, 1, 3]
    assert builder.check_filters.call_count == 1
    assert builder.check_value_filter.call_count == 1


def test_index_is_synced_when_collection_limit_truncates_items(episode_builder):
    builder = episode_builder
    collect(builder, [KeyedEpisode(1), KeyedEpisode(2)])
    builder.limit = 1
    builder.beginning_count = 0
    builder.remove_item_map = {}
    builder.details["changes_webhooks"] = False
    builder.library.get_collection_name_and_items = lambda *args: (builder.name, [])
    builder.library.alter_collection = MagicMock()

    assert builder.add_to_collection() == (1, 0)
    assert [item.ratingKey for item in builder.found_items] == [1]
    assert builder.found_item_keys == {"/library/metadata/1"}

    collect(builder, [KeyedEpisode(2), KeyedEpisode(3)])

    assert [item.ratingKey for item in builder.found_items] == [1, 2, 3]


@pytest.mark.parametrize("mdb_value_filters", [False, True])
def test_filtered_items_stay_excluded_and_are_reported_once(episode_builder, mdb_value_filters):
    builder = episode_builder
    builder.do_report = True
    builder.library.add_filtered = MagicMock()
    builder.library.get_id_from_maps = lambda rating_key: rating_key
    builder.library.is_movie = False
    builder.check_filters.side_effect = lambda item, display: item.ratingKey != 1
    builder.check_value_filter.side_effect = lambda item: item.ratingKey != 2
    if mdb_value_filters:
        builder.value_filters = [("mdb_tomatoes_rating", "gte", 6.0)]
        builder._prefetch_mdblist_value_filters = MagicMock()

    collect(builder, [KeyedEpisode(1), KeyedEpisode(2), KeyedEpisode(3), KeyedEpisode(1)])
    collect(builder, [KeyedEpisode(2), KeyedEpisode(3)])

    assert [item.ratingKey for item in builder.found_items] == [3]
    assert builder.filtered_keys == {1: "Episode 1", 2: "Episode 2"}
    assert builder.check_value_filter.call_count == 2
    builder.library.add_filtered.assert_called_once_with(builder.name, [("Episode 1", 1), ("Episode 2", 2)], False)


def test_mdblist_prefetch_skips_previously_accepted_and_filtered_items(episode_builder):
    builder = episode_builder
    collect(builder, [KeyedEpisode(1)])
    builder.check_filters.reset_mock()
    builder.check_value_filter.reset_mock()
    builder.filtered_keys = {2: "Episode 2"}
    builder.value_filters = [("mdb_tomatoes_rating", "gte", 6.0)]
    builder._prefetch_mdblist_value_filters = MagicMock()
    new_item = KeyedEpisode(3)

    collect(builder, [KeyedEpisode(1), KeyedEpisode(2), new_item])

    prefetched = builder._prefetch_mdblist_value_filters.call_args.args[0]
    assert len(prefetched) == 1
    assert prefetched[0] is new_item
    builder.check_filters.assert_called_once_with(new_item, "3/3")
    builder.check_value_filter.assert_called_once_with(new_item)
    assert [item.ratingKey for item in builder.found_items] == [1, 3]


@pytest.mark.parametrize("mdb_value_filters", [False, True])
def test_large_episode_batch_uses_linear_key_work_without_object_comparisons(episode_builder, mdb_value_filters):
    builder = episode_builder
    count = 80_000
    items = [KeyedEpisode(index) for index in range(count)]
    # Keep the regression focused on the algorithm rather than mock call storage.
    builder.check_filters = lambda item, display: True
    builder.check_value_filter = lambda item: True
    if mdb_value_filters:
        builder.value_filters = [("mdb_tomatoes_rating", "gte", 6.0)]
        builder._prefetch_mdblist_value_filters = lambda items: None

    collect(builder, items)

    assert len(builder.found_items) == count
    assert all(saved is original for saved, original in zip(builder.found_items, items))
    assert KeyedEpisode.key_reads <= 4 * count


@pytest.mark.parametrize("mdb_value_filters", [False, True])
def test_many_builder_entries_do_not_reindex_previous_results(episode_builder, mdb_value_filters):
    builder = episode_builder
    builder.check_filters = lambda item, display: True
    builder.check_value_filter = lambda item: True
    if mdb_value_filters:
        builder.value_filters = [("mdb_tomatoes_rating", "gte", 6.0)]
        builder._prefetch_mdblist_value_filters = lambda items: None
    count = 2_000
    for index in range(count):
        collect(builder, [KeyedEpisode(index)])

    assert [item.ratingKey for item in builder.found_items] == list(range(count))
    assert KeyedEpisode.key_reads <= 4 * count
