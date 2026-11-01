from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from modules.imdb import IMDb
from tests.factories import make_builder, make_plex


@pytest.mark.parametrize("is_movie", [True, False])
@pytest.mark.parametrize(
    ("keywords", "modifier", "expected"),
    [
        ({"stand up comedy special": (1, 1)}, "", True),
        ({"unrelated keyword": (1, 1)}, "", False),
        ({"stand up comedy special": (1, 1)}, ".not", False),
        ({"unrelated keyword": (1, 1)}, ".not", True),
        ({"stand up comedy special": (0, 1)}, "", False),
        ({}, "", False),
        (None, "", False),
        (None, ".not", False),
    ],
)
def test_missing_items_apply_imdb_keyword_filters(is_movie, keywords, modifier, expected):
    api = IMDb.__new__(IMDb)
    api.keywords = MagicMock(return_value=keywords)
    builder = make_builder(
        config=SimpleNamespace(IMDb=api),
        library=make_plex(),
        has_tmdb_filters=False,
        has_imdb_filters=True,
        language="en",
        filters=[[(f"imdb_keyword{modifier}", {"keywords": ["stand up comedy special"], "minimum_relevant": 1, "minimum_votes": 1, "minimum_percentage": 0})]],
    )
    item = SimpleNamespace(imdb_id="tt1234567")
    assert builder.check_missing_filters(1, is_movie, tmdb_item=item) is expected
    api.keywords.assert_called_once_with(item.imdb_id, "en")


def test_missing_imdb_id_fails_keyword_filter_without_calling_imdb():
    api = SimpleNamespace(keywords=MagicMock())
    builder = make_builder(config=SimpleNamespace(IMDb=api), has_tmdb_filters=False, has_imdb_filters=True, filters=[[("imdb_keyword", {})]])
    assert builder.check_missing_filters(1, True, tmdb_item=SimpleNamespace(imdb_id=None)) is False
    api.keywords.assert_not_called()


def test_missing_keyword_filter_preserves_alternative_filter_groups():
    builder = make_builder(
        config=SimpleNamespace(IMDb=SimpleNamespace(keywords=MagicMock(return_value={"unrelated": (1, 1)}))),
        has_tmdb_filters=False,
        has_imdb_filters=True,
        language="en",
        filters=[[("imdb_keyword", {})], [("year.gte", 2020)]],
        check_imdb_filters=MagicMock(return_value=False),
    )
    assert builder.check_missing_filters(1, True, tmdb_item=SimpleNamespace(imdb_id="tt1234567")) is True
    builder.check_imdb_filters.assert_called_once()
