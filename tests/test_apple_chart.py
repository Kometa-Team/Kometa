from types import SimpleNamespace

import pytest

from modules import apple_chart
from modules import builder as _builder  # noqa: F401  # Initialize the existing builder/Plex import cycle first.
from modules.util import Failed


@pytest.mark.parametrize(
    ("method", "country", "chart_type", "url"),
    [
        ("apple_chart", "US", "track", "https://kworb.net/apple_songs/"),
        ("apple_chart", "FR", "album", "https://kworb.net/apple_albums_eu/"),
        ("itunes_chart", "IT", "track", "https://kworb.net/eu/"),
        ("itunes_chart", "DE", "album", "https://kworb.net/aww/"),
        ("itunes_chart", "RU", "album", "https://kworb.net/eua/"),
    ],
)
def test_chart_url(method, country, chart_type, url):
    assert apple_chart.chart_url(method, country, chart_type) == url


def test_validate_defaults_to_track_and_accepts_album():
    assert apple_chart.validate("apple_chart", {"country": "uk"}) == {"country": "UK", "type": "track"}
    assert apple_chart.validate("itunes_chart", {"country": "FR", "type": "album"}) == {"country": "FR", "type": "album"}


def test_validate_rejects_unsupported_country():
    with pytest.raises(Failed, match="country must be one of"):
        apple_chart.validate("apple_chart", {"country": "CA"})


def test_parse_chart_filters_and_sorts_by_country_rank():
    content = b"""
    <table><tr><th>Pos</th><th>Artist and Title</th><th>Days</th><th>US</th><th>UK</th></tr>
    <tr><td>1</td><td><div><a>A</a> - <a>First</a></div></td><td>1</td><td>5</td><td>2</td></tr>
    <tr><td>2</td><td><div><a>B</a> - <a>Second</a></div></td><td>1</td><td>1</td><td></td></tr>
    <tr><td>3</td><td><div><a>C</a> - <a>Third</a></div></td><td>1</td><td>3</td><td>1</td></tr>
    </table>
    """
    entries = apple_chart.parse_chart_page(content, "UK", "https://kworb.net/test/")
    assert [(entry["rank"], entry["artist"], entry["title"]) for entry in entries] == [(1, "C", "Third"), (2, "A", "First")]


def test_get_rating_keys_uses_country_rank_for_chart_order(monkeypatch):
    class Matcher:
        def __init__(self, libraries, level, load_dates=False):
            assert level == "track"
            assert load_dates is True

        def match_earliest_track(self, artist, title):
            return SimpleNamespace(ratingKey={"A": 1, "B": 2}[artist]), None

    monkeypatch.setattr("modules.plex.MusicMatcher", Matcher)
    chart = apple_chart.MusicChart("apple_chart")
    chart.get_chart = lambda value: [
        {"rank": 4, "artist": "A", "title": "First"},
        {"rank": 2, "artist": "B", "title": "Second"},
    ]
    assert chart.get_rating_keys({"type": "track"}, object()) == [(1, "ratingKey"), (2, "ratingKey")]
    assert chart.chart_order == {1: 4, 2: 2}
