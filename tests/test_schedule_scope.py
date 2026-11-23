from types import SimpleNamespace

import modules.builder  # noqa: F401 - pre-import breaks the plex/meta circular import
from modules.library import Library
from modules.plex import Plex


def test_schedule_scope_includes_seasons_and_episodes_of_selected_show():
    library = SimpleNamespace(scheduled_item_keys={10})

    assert Library.is_scheduled_item(library, SimpleNamespace(ratingKey=10))
    assert Library.is_scheduled_item(library, SimpleNamespace(ratingKey=11, parentRatingKey=10))
    assert Library.is_scheduled_item(library, SimpleNamespace(ratingKey=12, parentRatingKey=11, grandparentRatingKey=10))
    assert not Library.is_scheduled_item(library, SimpleNamespace(ratingKey=20, parentRatingKey=21, grandparentRatingKey=22))


def test_scoped_plex_all_episodes_loads_only_selected_show_episodes(monkeypatch):
    monkeypatch.setitem(Plex.get_rating_keys.__globals__, "logger", SimpleNamespace(info=lambda *_: None))
    selected_show = type("Show", (), {"ratingKey": 10})()
    monkeypatch.setitem(Plex.get_rating_keys.__globals__, "Show", type(selected_show))
    episodes = [SimpleNamespace(ratingKey=101), SimpleNamespace(ratingKey=102)]
    library = SimpleNamespace(
        has_schedule_scope=True,
        is_show=True,
        get_all=lambda target_keys=None: [selected_show],
        cached_item_subitems=lambda item, method_name: episodes if item is selected_show and method_name == "episodes" else [],
    )

    assert Plex.get_rating_keys(library, "plex_all", "episode") == [(101, "ratingKey"), (102, "ratingKey")]


def test_index_schedule_uses_sort_title():
    library = SimpleNamespace(schedule_mode="index(b)")
    items = [
        SimpleNamespace(ratingKey=1, title="The Boys", titleSort="Boys"),
        SimpleNamespace(ratingKey=2, title="Better Call Saul"),
        SimpleNamespace(ratingKey=3, title="The Last of Us", titleSort="Last of Us"),
    ]

    assert Library._schedule_item_keys(library, items) == {1, 2}


def test_refresh_maps_all_items_but_returns_only_current_scope():
    items = [SimpleNamespace(ratingKey=10), SimpleNamespace(ratingKey=20)]
    calls = []
    library = SimpleNamespace(
        has_schedule_scope=True,
        scheduled_item_keys={10},
        is_music=False,
        get_all=lambda **kwargs: calls.append(kwargs) or items,
        map_guids=lambda mapped: calls.append(mapped),
    )

    assert Library.refresh_item_cache_and_mappings(library) == [items[0]]
    assert calls == [{"load": True, "ignore_schedule_scope": True}, items]
    assert set(library.cached_items) == {10, 20}


def _diff_library(**overrides):
    attrs = {"schedule_mode": "diff", "is_show": False, "is_music": False, "remove_overlays": False, "cached_item_subitems": lambda item, method_name: []}
    attrs.update(overrides)
    return SimpleNamespace(**attrs)


def test_diff_target_keys_lists_new_movies():
    items = [SimpleNamespace(ratingKey=1), SimpleNamespace(ratingKey=2)]

    assert Library.diff_target_keys(_diff_library(), items) == {1, 2}


def test_diff_target_keys_is_empty_when_nothing_is_new():
    assert Library.diff_target_keys(_diff_library(), []) == set()


def test_diff_target_keys_expands_shows_to_seasons_and_episodes():
    show = SimpleNamespace(ratingKey=10)
    subitems = {"seasons": [SimpleNamespace(ratingKey=11)], "episodes": [SimpleNamespace(ratingKey=111), SimpleNamespace(ratingKey=112)]}
    library = _diff_library(is_show=True, cached_item_subitems=lambda item, method_name: subitems[method_name] if item is show else [])

    assert Library.diff_target_keys(library, [show]) == {10, 11, 111, 112}


def test_diff_target_keys_gathers_library_wide_outside_diff_or_when_too_large(monkeypatch):
    items = [SimpleNamespace(ratingKey=1), SimpleNamespace(ratingKey=2)]

    assert Library.diff_target_keys(_diff_library(schedule_mode="full"), items) is None
    assert Library.diff_target_keys(_diff_library(schedule_mode="added(7d)"), items) is None
    assert Library.diff_target_keys(_diff_library(is_music=True), items) is None
    assert Library.diff_target_keys(_diff_library(remove_overlays=True), items) is None
    monkeypatch.setitem(Library.diff_target_keys.__globals__, "DIFF_TARGET_KEY_LIMIT", 1)
    assert Library.diff_target_keys(_diff_library(), items) is None
