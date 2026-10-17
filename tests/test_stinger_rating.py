"""Stinger filters must validate before reaching their existing comparison logic."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from plexapi.video import Movie

from modules.util import Failed
from tests.test_builder import make_builder
from tests.test_plex import make_plex

MODIFIERS = ["", ".not", ".gt", ".gte", ".lt", ".lte"]


@pytest.fixture
def stinger_builder():
    library = make_plex(config=SimpleNamespace(mediastingers={101: -3, 102: 0, 103: 5}), movie_rating_key_map={1: 101, 2: 102, 3: 103, 4: 104})
    library.reload = MagicMock(side_effect=lambda item, **kwargs: item)
    return make_builder(library=library, builder_level="movie", filters=[])


@pytest.mark.parametrize("definition_type", ["Collection", "Overlay"])
@pytest.mark.parametrize("modifier", MODIFIERS)
@pytest.mark.parametrize("threshold", [-3, 0, 5, "-3", "0", "5"])
def test_all_stinger_modifiers_accept_signed_integer_thresholds(stinger_builder, definition_type, modifier, threshold):
    builder = stinger_builder
    builder.Type = definition_type
    builder._filters("filters", {f"stinger_rating{modifier}": threshold})
    assert builder.filters == [[(f"stinger_rating{modifier}", int(threshold))]]


@pytest.mark.parametrize("definition_type", ["Collection", "Overlay"])
@pytest.mark.parametrize(
    "modifier, threshold, expected",
    [
        ("", 0, [2]),
        (".not", 0, [1, 3]),
        (".gt", 0, [3]),
        (".gte", 0, [2, 3]),
        (".lt", 0, [1]),
        (".lte", 0, [1, 2]),
        ("", -1, []),
        (".not", -1, [1, 2, 3]),
        (".gt", -1, [2, 3]),
        (".gte", -1, [2, 3]),
        (".lt", -1, [1]),
        (".lte", -1, [1]),
        ("", -3, [1]),
    ],
)
def test_validated_filters_match_actual_ratings_and_exclude_missing_ratings(stinger_builder, definition_type, modifier, threshold, expected):
    builder = stinger_builder
    builder.Type = definition_type
    builder._filters("filters", {f"stinger_rating{modifier}": threshold})
    matches = []
    # 4 has a TMDb ID without a stinger rating; 5 has no mapped TMDb ID.
    for rating_key in range(1, 6):
        item = MagicMock(spec=Movie)
        item.ratingKey = rating_key
        if builder.library.check_filters(item, builder.filters[0], None):
            matches.append(rating_key)
    assert matches == expected


@pytest.mark.parametrize("value", [1.5, "1.5", "invalid", True, None, [1, 2], {"value": 1}])
def test_stinger_thresholds_still_require_one_integer(stinger_builder, value):
    with pytest.raises(Failed):
        stinger_builder._filters("filters", {"stinger_rating.gt": value})


@pytest.mark.parametrize("attribute", ["channels", "height", "width", "tmdb_vote_count", "plays"])
def test_other_integer_attributes_still_reject_negative_thresholds(stinger_builder, attribute):
    with pytest.raises(Failed):
        stinger_builder.validate_attribute(attribute, ".gt", f"{attribute}.gt", -1, True)
    assert stinger_builder.validate_attribute(attribute, ".gt", f"{attribute}.gt", 0, True) == 0


def test_stinger_filter_remains_movie_only(stinger_builder):
    stinger_builder.builder_level = "show"
    with pytest.raises(Failed, match="not a valid show filter attribute"):
        stinger_builder._filters("filters", {"stinger_rating.gt": 0})


def test_has_stinger_keeps_its_existing_presence_semantics(stinger_builder):
    builder = stinger_builder
    builder._filters("filters", {"has_stinger": True})
    matches = []
    for rating_key in range(1, 6):
        item = MagicMock(spec=Movie)
        item.ratingKey = rating_key
        if builder.library.check_filters(item, builder.filters[0], None):
            matches.append(rating_key)
    assert matches == [1, 2, 3]
