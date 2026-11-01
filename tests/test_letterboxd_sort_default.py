from unittest.mock import MagicMock

import pytest

from modules import letterboxd, util
from tests.conftest import FakeLogger


@pytest.mark.parametrize("page_type", ["films", "reviews", "watchlist"])
@pytest.mark.parametrize(
    ("options", "expected", "warns"),
    [({}, "release_date_newest", False), ({"sort_by": "release_date_newest"}, "release_date_newest", False), ({"Sort_By": "release_date_newest"}, "release_date_newest", False), ({"sort_by": "invalid"}, "release_date_newest", True)],
)
def test_user_page_sort_default_only_warns_for_invalid_value(monkeypatch, page_type, options, expected, warns):
    logger = FakeLogger()
    monkeypatch.setattr(letterboxd, "logger", logger)
    monkeypatch.setattr(util, "logger", logger)
    adapter = letterboxd.Letterboxd.__new__(letterboxd.Letterboxd)
    adapter._get_user_entries = MagicMock(return_value=[])
    result = adapter._validate_single_user_page("Collection", {"username": "criterion", "incremental": False, **options}, page_type, "en")
    assert result["sort_by"] == expected
    assert bool(logger.warning_messages) is warns
    adapter._get_user_entries.assert_called_once_with("criterion", page_type, "en")
