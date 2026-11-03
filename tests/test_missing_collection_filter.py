from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from plexapi.video import Movie, Show

import modules.builder as builder_module
from modules.plex import Plex
from modules.util import Failed, FilterFailed
from tests.conftest import FakeLogger
from tests.factories import make_builder

MISSING = "Speciale Halloween 🎃"
EXISTING = "Existing Collection"


@pytest.fixture
def builder(monkeypatch):
    logger = FakeLogger()
    monkeypatch.setattr(builder_module, "logger", logger)
    plex = Plex.__new__(Plex)
    plex.get_search_choices = MagicMock(return_value=({EXISTING.lower(): EXISTING}, [EXISTING]))
    plex.reload = MagicMock(side_effect=lambda item, **kwargs: item)
    plex.cached_item_attr = lambda item, attribute: getattr(item, attribute)
    result = make_builder(
        Type="Overlay",
        overlay=True,
        builder_level="movie",
        library=plex,
        details={"show_options": False, "only_filter_missing": False},
        current_time=datetime(2026, 11, 3),
    )
    del result.check_filters  # Exercise the real filter pipeline rather than the factory default.
    result.test_logger = logger
    return result


def item_with_collections(item_class, rating_key, *collections):
    item = MagicMock(spec=item_class)
    item.ratingKey = rating_key
    item.title = f"Item {rating_key}"
    item.collections = [SimpleNamespace(tag=name) for name in collections]
    return item


@pytest.mark.parametrize("item_class", [Movie, Show])
@pytest.mark.parametrize("available", [False, True])
def test_missing_collection_exclusion_keeps_builder_candidates(builder, item_class, available):
    builder.builder_level = "movie" if item_class is Movie else "show"
    if available:
        builder.library.get_search_choices.return_value = ({MISSING: MISSING}, [MISSING])
    builder._filters("filters", {"collection.not": MISSING})
    candidates = [item_with_collections(item_class, 1), item_with_collections(item_class, 2, MISSING), item_with_collections(item_class, 3, EXISTING)]

    selected = [item.ratingKey for item in candidates if builder.check_filters(item, "Test")]

    assert selected == ([1, 3] if available else [1, 2, 3])
    assert builder.filters == [[("collection.not", [MISSING] if available else [])]]
    assert builder.test_logger.error_messages == []
    if not available:
        assert len(builder.test_logger.warning_messages) == 1
        assert builder.test_logger.warning_messages[0] == f"Plex Warning: collection: {MISSING} not found; ignoring this collection exclusion"


def test_mixed_collection_exclusions_keep_existing_names(builder):
    builder._filters("filters", {"collection.not": [MISSING, EXISTING.lower()]})
    candidates = [item_with_collections(Movie, 1), item_with_collections(Movie, 2, EXISTING)]

    assert [item.ratingKey for item in candidates if builder.check_filters(item, "Test")] == [1]
    assert builder.filters == [[("collection.not", [EXISTING])]]
    assert len(builder.test_logger.warning_messages) == 1


def test_missing_collection_exclusion_keeps_other_filters_active(builder):
    builder._filters("filters", {"collection.not": MISSING, "year.gte": 2020})
    old_item = item_with_collections(Movie, 1)
    old_item.year = 2019
    new_item = item_with_collections(Movie, 2)
    new_item.year = 2021

    assert not builder.check_filters(old_item, "Test")
    assert builder.check_filters(new_item, "Test")


@pytest.mark.parametrize("definition_type", ["Collection", "Playlist", "Overlay"])
def test_missing_exclusion_behavior_is_shared_by_definition_types(builder, definition_type):
    builder.Type = definition_type
    builder._filters("filters", {"collection.not": MISSING})
    assert builder.check_filters(item_with_collections(Movie, 1), "Test")


def test_missing_positive_collection_still_fails_validation(builder):
    with pytest.raises(Failed, match="not found"):
        builder._filters("filters", {"collection": MISSING})


@pytest.mark.parametrize("attribute", ["genre", "label"])
def test_other_missing_negative_tags_still_fail_validation(builder, attribute):
    with pytest.raises(Failed, match="not found"):
        builder._filters("filters", {f"{attribute}.not": MISSING})


@pytest.mark.parametrize("modifier", ["", ".not"])
def test_plex_search_missing_collection_still_fails_validation(builder, modifier):
    with pytest.raises(FilterFailed, match="not found"):
        builder.validate_attribute("collection", modifier, f"collection{modifier}", MISSING, True, plex_search=True)
