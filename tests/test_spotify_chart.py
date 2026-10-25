import json
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from jsonschema import Draft7Validator

from modules import builder as _builder  # noqa: F401  # Initialize the existing builder/Plex import cycle first.
from modules.spotify_chart import SpotifyChart, normalize_country, parse_chart_page
from modules.util import Failed


def plex_track(artist, album, title, rating_key, release_date):
    return SimpleNamespace(
        grandparentTitle=artist,
        parentTitle=album,
        title=title,
        ratingKey=rating_key,
        parentRatingKey={"Old Album": 11, "New Album": 12}[album],
        parentYear=release_date.year if release_date else None,
        guids=[],
    )


def test_country_names_and_codes():
    assert normalize_country("UK") == "gb"
    assert normalize_country("United Kingdom") == "gb"
    assert normalize_country("GB") == "gb"
    with pytest.raises(Failed):
        normalize_country("Atlantis")


def test_validation_defaults_nothing_and_rejects_bad_type():
    assert SpotifyChart.validate({"country": "UK", "chart": "DAILY"}) == {"country": "gb", "chart": "daily"}
    with pytest.raises(Failed, match="chart must be daily or weekly"):
        SpotifyChart.validate({"country": "UK", "chart": "monthly"})


def test_parse_chart_table_splits_on_first_separator():
    content = b"""
    <table><tr><th>Pos</th><th>Move</th><th>Artist and Title</th><th>Streams</th></tr>
    <tr><td>2</td><td>=</td><td><div><a>sombr</a> - <a>undressed</a></div></td><td>20</td></tr>
    <tr><td>1</td><td>+1</td><td><div><a>Artist</a> - <a>Song - Remix</a> (w/ <a>Guest</a>)</div></td><td>30</td></tr></table>
    """
    assert parse_chart_page(content, "https://kworb.net/chart") == [
        {"position": 1, "artist": "Artist", "title": "Song - Remix"},
        {"position": 2, "artist": "sombr", "title": "undressed"},
    ]


def test_builder_requests_expected_url_and_matches_earliest_album():
    old_track = plex_track("sombr", "Old Album", "undressed", 1, datetime(2023, 1, 1))
    new_track = plex_track("sombr", "New Album", "undressed", 2, datetime(2024, 1, 1))
    old_album = SimpleNamespace(ratingKey=11, originallyAvailableAt=datetime(2023, 1, 1), year=2023)
    new_album = SimpleNamespace(ratingKey=12, originallyAvailableAt=datetime(2024, 1, 1), year=2024)
    library = SimpleNamespace(is_music=True, get_all=Mock(side_effect=lambda builder_level=None, load=False: [new_track, old_track] if builder_level == "track" else [new_album, old_album]))
    response = Mock(content=b"<table><tr><td>1</td><td>=</td><td><div><a>sombr</a> - <a>undressed</a></div></td></tr></table>")
    client = Mock()
    client.get.return_value = response
    builder = SpotifyChart(session=client)

    result = builder.get_rating_keys({"country": "gb", "chart": "daily"}, library)

    assert result == [(1, "ratingKey")]
    assert builder.chart_order == {1: 1}
    client.get.assert_called_once_with("https://kworb.net/spotify/country/gb_daily.html", timeout=30, headers={"User-Agent": "Kometa/SpotifyChart"})


def test_schema_accepts_chart_builder_and_custom_order():
    schema_path = Path(__file__).resolve().parents[1] / "json-schema" / "collection-schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft7Validator.check_schema(schema)
    Draft7Validator(schema).validate({"collections": {"Spotify UK Daily": {"spotify_chart": {"country": "UK", "chart": "daily"}, "collection_order": "custom"}}})
