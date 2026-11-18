from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from modules.tmdb import TMDb
from tests.factories import make_builder, make_plex


@pytest.mark.parametrize("is_movie", [True, False])
@pytest.mark.parametrize("modifier", [".gt", ".gte", ".lt", ".lte"])
@pytest.mark.parametrize("year", [None, 2019, 2020, 2021])
def test_tmdb_year_filter_handles_missing_and_present_dates(is_movie, modifier, year):
    date = datetime(year, 1, 1) if year else None
    item = SimpleNamespace(release_date=date, first_air_date=date)
    comparisons = {".gt": lambda y: y > 2020, ".gte": lambda y: y >= 2020, ".lt": lambda y: y < 2020, ".lte": lambda y: y <= 2020}
    expected = year is not None and comparisons[modifier](year)
    assert TMDb.__new__(TMDb).item_filter(item, "tmdb_year", modifier, f"tmdb_year{modifier}", 2020, is_movie, datetime.now()) is expected


@pytest.mark.parametrize("is_movie", [True, False])
def test_missing_year_filter_continues_after_item_without_date(is_movie):
    api = TMDb.__new__(TMDb)
    builder = make_builder(
        config=SimpleNamespace(TMDb=api),
        library=make_plex(),
        has_tmdb_filters=True,
        has_imdb_filters=False,
        filters=[[("tmdb_year.gte", 2020)]],
        current_time=datetime(2026, 1, 1),
    )
    items = [SimpleNamespace(release_date=None, first_air_date=None), SimpleNamespace(release_date=datetime(2021, 1, 1), first_air_date=datetime(2021, 1, 1))]
    api.get_movie = MagicMock(side_effect=items)
    api.get_show = MagicMock(side_effect=items)
    builder.config.Convert = SimpleNamespace(tvdb_to_tmdb=lambda item_id, fail: item_id)
    assert [builder.check_missing_filters(item_id, is_movie) for item_id in [1, 2]] == [False, True]
