from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from modules import util
from modules.util import Failed


def test_parse_run_item_ids_accepts_supported_typed_identifiers():
    assert util.parse_run_item_ids("TMDb:00550|tvdb:1399|imdb:tt0137523|plex:42") == {
        ("tmdb", "550"),
        ("tvdb", "1399"),
        ("imdb", "tt0137523"),
        ("plex", "42"),
    }


@pytest.mark.parametrize(
    "value",
    [
        "550",
        "tmdb:",
        "unknown:550",
        "tmdb:not-a-number",
        "imdb:12345",
        "plex:abc",
    ],
)
def test_parse_run_item_ids_rejects_invalid_identifiers(value):
    with pytest.raises(Failed, match="Argument Error"):
        util.parse_run_item_ids(value)


def test_resolve_run_item_ids_translates_show_tmdb_ids_to_tvdb():
    library = MagicMock()
    library.is_show = True
    library.config.Convert.tmdb_to_tvdb.return_value = 1399

    resolved = util.resolve_run_item_ids(library, {("tmdb", "1396")})

    assert resolved == {("tmdb", "1396"), ("tvdb", "1399")}
    library.config.Convert.tmdb_to_tvdb.assert_called_once_with(1396)


def test_filter_items_by_ids_matches_any_supported_id():
    first = SimpleNamespace(ratingKey=1)
    second = SimpleNamespace(ratingKey=2)
    third = SimpleNamespace(ratingKey=3)
    library = MagicMock()
    library.get_ids.side_effect = [
        (550, None, None),
        (None, 1399, "tt0944947"),
        (None, None, None),
    ]

    selected = util.filter_items_by_ids(
        library,
        [first, second, third],
        {("tmdb", "550"), ("imdb", "tt0944947"), ("plex", "3")},
    )

    assert selected == [first, second, third]


def test_filter_items_by_ids_keeps_only_requested_items():
    selected_item = SimpleNamespace(ratingKey=1)
    other_item = SimpleNamespace(ratingKey=2)
    library = MagicMock()
    library.get_ids.side_effect = [
        (550, None, None),
        (603, None, None),
    ]

    selected = util.filter_items_by_ids(library, [selected_item, other_item], {("tmdb", "550")})

    assert selected == [selected_item]


@pytest.mark.parametrize(
    ("item_attrs", "item_id"),
    [
        ({"grandparentRatingKey": 8}, ("tvdb", "1399")),
        ({"parentRatingKey": 8}, ("imdb", "tt0944947")),
    ],
)
def test_filter_items_by_ids_matches_show_id_for_episode_and_season(item_attrs, item_id):
    from plexapi.video import Episode, Season

    item_type = Episode if "grandparentRatingKey" in item_attrs else Season
    item = MagicMock(spec=item_type)
    item.ratingKey = 99
    for name, value in item_attrs.items():
        setattr(item, name, value)
    library = MagicMock()
    library.show_rating_key_map = {8: 1399}
    library.imdb_rating_key_map = {8: "tt0944947"}

    assert util.filter_items_by_ids(library, [item], {item_id}) == [item]
    library.get_ids.assert_not_called()
