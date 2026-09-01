"""
Tests for Plex.fetch_overlay_value() — cache-first logic, float normalization,
source dispatch for plex_* ratings, and None/error handling.

fetch_overlay_value lives in modules/plex.py. It:
  1. Returns a cached float immediately if overlay_value_cache is warm.
  2. Falls through to a source fetch on cache miss or expiry.
  3. Casts the result to float (sources like IMDb can return strings).
  4. Writes the result to cache; does NOT write on None or non-numeric.
  5. Returns None when no rating is available.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import modules.builder  # noqa: F401 -- pre-import to break plex<->builder circular import
import modules.plex as plex_module
from modules.overlay import vars_by_type
from modules.plex import Plex
from modules.util import Failed


def _make_plex(cache=None, get_ids=None, get_ratings=None):
    """Minimal Plex stub — bypasses __init__, wires only what fetch_overlay_value needs."""
    plx = Plex.__new__(Plex)
    plx.config = SimpleNamespace(Cache=cache)
    plx.is_movie = True
    plx.is_show = False
    plx._trakt_user_ratings = None
    plx.get_ids = get_ids or MagicMock(return_value=(None, None, None))
    plx.get_ratings = get_ratings or MagicMock(return_value={})
    return plx


def _item(rating_key=5173):
    return SimpleNamespace(ratingKey=rating_key, title="Test Movie", guid="plex://movie/abc")


def _episode(guids=None, season=2, episode=8):
    return SimpleNamespace(guids=guids or [], seasonNumber=season, episodeNumber=episode)


def test_serializd_rating_is_limited_to_shows_and_episodes():
    assert "serializd_rating" in vars_by_type["show"]
    assert "serializd_rating" in vars_by_type["episode"]
    assert "serializd_rating" not in vars_by_type["movie"]
    assert "serializd_rating" not in vars_by_type["season"]


def test_tmdb_episode_guid_is_used_before_plex_position():
    plx = Plex.__new__(Plex)
    direct_episode = SimpleNamespace(vote_average=9.5)
    tmdb_client = MagicMock()
    tmdb_client.get_episode_by_id.return_value = direct_episode
    plx.config = SimpleNamespace(TMDb=tmdb_client)
    episode = _episode([SimpleNamespace(id="tmdb://6855841")])

    assert plx.get_tmdb_episode(episode, 209867) is direct_episode
    tmdb_client.get_episode_by_id.assert_called_once_with(209867, 6855841)
    tmdb_client.get_episode.assert_not_called()


def test_tmdb_episode_stale_guid_falls_back_to_plex_position(monkeypatch):
    monkeypatch.setattr(plex_module, "logger", MagicMock())
    plx = Plex.__new__(Plex)
    positional_episode = SimpleNamespace(vote_average=8.0)
    tmdb_client = MagicMock()
    tmdb_client.get_episode_by_id.side_effect = Failed("not found")
    tmdb_client.get_episode.return_value = positional_episode
    plx.config = SimpleNamespace(TMDb=tmdb_client)
    episode = _episode([SimpleNamespace(id="tmdb://999999")])

    assert plx.get_tmdb_episode(episode, 209867) is positional_episode
    tmdb_client.get_episode.assert_called_once_with(209867, 2, 8)


def test_tmdb_episode_without_guid_uses_plex_position():
    plx = Plex.__new__(Plex)
    positional_episode = SimpleNamespace(vote_average=8.0)
    tmdb_client = MagicMock()
    tmdb_client.get_episode.return_value = positional_episode
    plx.config = SimpleNamespace(TMDb=tmdb_client)

    assert plx.get_tmdb_episode(_episode(), 209867) is positional_episode
    tmdb_client.get_episode_by_id.assert_not_called()
    tmdb_client.get_episode.assert_called_once_with(209867, 2, 8)


def test_tmdb_episode_malformed_guid_does_not_hide_later_valid_guid():
    plx = Plex.__new__(Plex)
    direct_episode = SimpleNamespace(vote_average=9.5)
    tmdb_client = MagicMock()
    tmdb_client.get_episode_by_id.return_value = direct_episode
    plx.config = SimpleNamespace(TMDb=tmdb_client)
    episode = _episode([SimpleNamespace(id="tmdb://not-a-number"), SimpleNamespace(id="tmdb://6855841")])

    assert plx.get_tmdb_episode(episode, 209867) is direct_episode
    tmdb_client.get_episode_by_id.assert_called_once_with(209867, 6855841)
    tmdb_client.get_episode.assert_not_called()


def test_tmdb_episode_only_malformed_guid_uses_plex_position():
    plx = Plex.__new__(Plex)
    positional_episode = SimpleNamespace(vote_average=8.0)
    tmdb_client = MagicMock()
    tmdb_client.get_episode.return_value = positional_episode
    plx.config = SimpleNamespace(TMDb=tmdb_client)
    episode = _episode([SimpleNamespace(id="tmdb://not-a-number")])

    assert plx.get_tmdb_episode(episode, 209867) is positional_episode
    tmdb_client.get_episode_by_id.assert_not_called()
    tmdb_client.get_episode.assert_called_once_with(209867, 2, 8)


# ── Cache-first logic ──────────────────────────────────────────────────────────


def test_returns_cached_float_when_fresh():
    # Warm cache hit — source must never be called.
    cache = MagicMock()
    cache.query_overlay_value_cache.return_value = ("7.3", False)
    fetch_spy = MagicMock(return_value={})
    plx = _make_plex(cache=cache, get_ratings=fetch_spy)

    result = plx.fetch_overlay_value(_item(), "plex_imdb_rating")

    assert result == 7.3
    assert isinstance(result, float)
    cache.query_overlay_value_cache.assert_called_once_with(5173, "plex_imdb_rating")
    cache.update_overlay_value_cache.assert_not_called()
    fetch_spy.assert_not_called()


def test_expired_cache_re_fetches():
    # Expired entry — falls through to source, returns fresh value, writes to cache.
    cache = MagicMock()
    cache.query_overlay_value_cache.return_value = ("6.0", True)  # expired
    plx = _make_plex(cache=cache, get_ratings=MagicMock(return_value={"plex_imdb": 7.5}))

    result = plx.fetch_overlay_value(_item(), "plex_imdb_rating")

    assert result == 7.5
    cache.update_overlay_value_cache.assert_called_once()


def test_cache_miss_fetches_and_writes():
    # No cached entry — fetches, writes result, returns float.
    cache = MagicMock()
    cache.query_overlay_value_cache.return_value = (None, None)
    plx = _make_plex(cache=cache, get_ratings=MagicMock(return_value={"plex_audience": 8.2}))

    result = plx.fetch_overlay_value(_item(), "plex_audience_rating")

    assert result == 8.2
    cache.update_overlay_value_cache.assert_called_once_with(False, 5173, "plex_audience_rating", 8.2)


def test_no_cache_always_fetches():
    # config.Cache is None — no cache read/write, source always consulted.
    plx = _make_plex(cache=None, get_ratings=MagicMock(return_value={"plex_imdb": 6.0}))

    result = plx.fetch_overlay_value(_item(), "plex_imdb_rating")

    assert result == 6.0


def test_floppy_rating_fetches_direct_decimal_value():
    plx = _make_plex(cache=None, get_ids=MagicMock(return_value=(550, None, "tt0137523")))
    floppy = MagicMock()
    floppy.get_overlay_rating.return_value = 9.9
    plx.config.Floppy = floppy

    assert plx.fetch_overlay_value(_item(), "floppy_rating") == 9.9
    floppy.get_overlay_rating.assert_called_once_with("movie", tmdb_id=550, tvdb_id=None, imdb_id="tt0137523", season=None, episode=None)


# ── Float normalization ────────────────────────────────────────────────────────


def test_string_from_source_normalized_to_float():
    # Some sources (e.g. IMDb) return a string; must be cast to float before returning/writing.
    plx = _make_plex(cache=None, get_ratings=MagicMock(return_value={"plex_imdb": "7.3"}))

    result = plx.fetch_overlay_value(_item(), "plex_imdb_rating")

    assert result == 7.3
    assert isinstance(result, float)


def test_non_numeric_string_returns_none():
    # float("N/A") raises ValueError → returns None, no cache write.
    cache = MagicMock()
    cache.query_overlay_value_cache.return_value = (None, None)
    plx = _make_plex(cache=cache, get_ratings=MagicMock(return_value={"plex_imdb": "N/A"}))

    result = plx.fetch_overlay_value(_item(), "plex_imdb_rating")

    assert result is None
    cache.update_overlay_value_cache.assert_not_called()


def test_out_of_range_cached_rating_is_rejected_and_reported(monkeypatch):
    logger = MagicMock()
    monkeypatch.setattr(plex_module, "logger", logger)
    cache = MagicMock()
    cache.query_overlay_value_cache.return_value = (10.2, False)
    plx = _make_plex(cache=cache, get_ratings=MagicMock(return_value={}))

    result = plx.fetch_overlay_value(_item(), "plex_imdb_rating")

    assert result is None
    assert any("value 10.2 is invalid" in call.args[0] for call in logger.warning.call_args_list)
    cache.update_overlay_value_cache.assert_not_called()


def test_out_of_range_letterboxd_rating_is_not_rendered_or_cached(monkeypatch):
    logger = MagicMock()
    monkeypatch.setattr(plex_module, "logger", logger)
    cache = MagicMock()
    cache.query_overlay_value_cache.return_value = (None, None)
    plx = _make_plex(cache=cache, get_ids=MagicMock(return_value=(550, None, None)))
    plx.config.MDBList = MagicMock(limit=False)
    plx.config.MDBList.get_movie.return_value = SimpleNamespace(letterboxd_rating=5.1, ratings_valid=False)

    result = plx.fetch_overlay_value(_item(), "mdb_letterboxd_rating")

    assert result is None
    assert any("provider's 0 to 5 scale" in call.args[0] for call in logger.warning.call_args_list)
    cache.update_overlay_value_cache.assert_not_called()


def test_valid_rating_from_tainted_provider_response_is_not_overlay_cached():
    cache = MagicMock()
    cache.query_overlay_value_cache.return_value = (None, None)
    plx = _make_plex(cache=cache, get_ids=MagicMock(return_value=(550, None, None)))
    plx.config.MDBList = MagicMock(limit=False)
    plx.config.MDBList.get_movie.return_value = SimpleNamespace(imdb_rating=8.2, ratings_valid=False)

    result = plx.fetch_overlay_value(_item(), "mdb_imdb_rating")

    assert result == 8.2
    cache.update_overlay_value_cache.assert_not_called()


# ── None handling ──────────────────────────────────────────────────────────────


def test_none_from_source_returns_none_and_no_cache_write():
    # Source returns nothing for this item — must NOT poison the cache with a None entry.
    cache = MagicMock()
    cache.query_overlay_value_cache.return_value = (None, None)
    plx = _make_plex(cache=cache, get_ratings=MagicMock(return_value={}))  # KeyError → None

    result = plx.fetch_overlay_value(_item(), "plex_imdb_rating")

    assert result is None
    cache.update_overlay_value_cache.assert_not_called()


# ── plex_* variable dispatch ───────────────────────────────────────────────────


def test_plex_rating_key_stripped_correctly():
    # "plex_imdb_rating" → strip "_rating" → look up "plex_imdb" in get_ratings result.
    plx = _make_plex(cache=None, get_ratings=MagicMock(return_value={"plex_imdb": 9.1, "plex_audience": 8.0}))

    assert plx.fetch_overlay_value(_item(), "plex_imdb_rating") == 9.1
    assert plx.fetch_overlay_value(_item(), "plex_audience_rating") == 8.0


def test_plex_rating_key_not_found_returns_none():
    # Item has no entry for this plex rating type → KeyError → returns None.
    plx = _make_plex(cache=None, get_ratings=MagicMock(return_value={}))

    result = plx.fetch_overlay_value(_item(), "plex_imdb_rating")

    assert result is None


def test_serializd_show_rating_is_fetched_directly():
    plx = _make_plex(get_ids=MagicMock(return_value=(1429, None, None)))
    plx.is_movie = False
    plx.is_show = True
    plx.config.Serializd = MagicMock()
    plx.config.Serializd.get_show_rating.return_value = 9.07

    assert plx.fetch_overlay_value(_item(), "serializd_rating") == 9.07
    plx.config.Serializd.get_show_rating.assert_called_once_with(1429)


def test_serializd_episode_rating_is_fetched_directly(monkeypatch):
    monkeypatch.setattr(plex_module, "Episode", SimpleNamespace)
    show = _item()
    episode = SimpleNamespace(ratingKey=2, title="Episode", guid="plex://episode/abc", seasonNumber=1, episodeNumber=3, show=MagicMock(return_value=show))
    plx = _make_plex(get_ids=MagicMock(return_value=(1429, None, None)))
    plx.is_movie = False
    plx.is_show = True
    plx.config.Serializd = MagicMock()
    plx.config.Serializd.get_episode_rating.return_value = 8.79

    assert plx.fetch_overlay_value(episode, "serializd_rating") == 8.79
    plx.config.Serializd.get_episode_rating.assert_called_once_with(1429, 1, 3)


def test_serializd_rating_resolves_tvdb_show_id_to_tmdb():
    plx = _make_plex(get_ids=MagicMock(return_value=(None, 121361, None)))
    plx.is_movie = False
    plx.is_show = True
    plx.config.Serializd = MagicMock()
    plx.config.Serializd.get_show_rating.return_value = 9.07
    plx.config.Convert = MagicMock()
    plx.config.Convert.tvdb_to_tmdb.return_value = 1429

    assert plx.fetch_overlay_value(_item(), "serializd_rating") == 9.07
    plx.config.Serializd.get_show_rating.assert_called_once_with(1429)
