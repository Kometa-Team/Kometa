"""Native rating target validation, source fallback and Silo score conversions."""

from types import SimpleNamespace
from unittest.mock import MagicMock, call

import pytest

from modules.rating_operations import configure_rating_updates, rating_value, update_silo_ratings
from modules.util import Failed


@pytest.mark.parametrize("server", ["plex", "jellyfin", "emby"])
def test_native_targets_are_rejected_on_other_servers(server):
    params = {"mass_silo_imdb_rating_update": ["imdb"], "mass_user_rating_update": ["imdb"]}
    logger = MagicMock()
    configure_rating_updates(params, server, logger)
    assert params["mass_silo_imdb_rating_update"] is None
    assert params["mass_user_rating_update"] == ["imdb"]
    assert "unsupported" in logger.error.call_args.args[0]


@pytest.mark.parametrize("server,source", [("silo", "plex_imdb"), ("emby", "silo_imdb"), ("jellyfin", "silo_tmdb"), ("plex", "silo_user")])
def test_incompatible_sources_are_reported_and_fallbacks_retained(server, source):
    params = {"mass_user_rating_update": [source, "imdb"]}
    logger = MagicMock()
    configure_rating_updates(params, server, logger)
    assert params.get("mass_silo_user_rating_update" if server == "silo" else "mass_user_rating_update") == ["imdb"]
    logger.error.assert_called_once()


def test_silo_generic_slots_are_not_guessed_and_explicit_user_wins():
    params = {"mass_user_rating_update": ["imdb"], "mass_silo_user_rating_update": ["tmdb"], "mass_critic_rating_update": ["imdb"], "mass_audience_rating_update": ["tmdb"], "mass_episode_user_rating_update": ["imdb"]}
    logger = MagicMock()
    configure_rating_updates(params, "silo", logger)
    assert params["mass_silo_user_rating_update"] == ["tmdb"]
    assert all(params[key] is None for key in params if key != "mass_silo_user_rating_update")
    assert logger.error.call_count == 4


@pytest.mark.parametrize("target,score,expected", [("silo_user", 0, 1), ("silo_user", 7, 4), ("silo_user", 9.9, 5), ("silo_tomatoes", 7.45, 75), ("silo_tomatoesaudience", 0, 0), ("silo_imdb", 7.4, 7.4), ("silo_tmdb", 0, 0), ("silo_user", None, None)])
def test_score_conversions(target, score, expected):
    assert rating_value(target, score) == expected


@pytest.mark.parametrize("score", [-1, 11, float("nan"), float("inf"), True, "bad"])
def test_invalid_scores_never_reach_api(score):
    with pytest.raises(Failed):
        rating_value("silo_imdb", score)


def test_provider_values_use_fallbacks_and_combine_writes():
    library = MagicMock()
    library.fetch_overlay_value.side_effect = [None, 7.45, 8.2]
    item = SimpleNamespace(title="Example", data={})
    update_silo_ratings(library, item, {"silo_tomatoes": ["mdb_tomatoes", "imdb"], "silo_imdb": ["imdb"], "silo_user": [7]}, MagicMock())
    assert library.update_native_ratings.call_args_list == [call(item, {"rating_rt_critic": 75, "rating_imdb": 8.2}), call(item, {"user_rating": 4})]


def test_unchanged_zero_and_clear_are_distinct():
    library = MagicMock()
    item = SimpleNamespace(title="Example", data={"rating_imdb": 0})
    update_silo_ratings(library, item, {"silo_imdb": [0], "silo_tmdb": ["clear"]}, MagicMock())
    library.update_native_ratings.assert_called_once_with(item, {"rating_tmdb": None})


def test_missing_and_invalid_sources_never_clear_existing_ratings():
    library = MagicMock()
    library.fetch_overlay_value.side_effect = [None, 20]
    update_silo_ratings(library, SimpleNamespace(title="Example", data={"rating_imdb": 8}), {"silo_imdb": ["imdb", "tmdb"]}, MagicMock())
    library.update_native_ratings.assert_not_called()


@pytest.mark.parametrize("option", ["lock", "unlock", "remove", "reset", "random"])
def test_unsupported_silo_actions_are_reported_before_scanning(option):
    logger = MagicMock()
    params = {"mass_silo_imdb_rating_update": [option]}
    configure_rating_updates(params, "silo", logger)
    assert params["mass_silo_imdb_rating_update"] is None
    assert "unsupported" in logger.error.call_args.args[0]


def test_native_clear_source_is_reported_on_plex():
    params = {"mass_user_rating_update": ["clear"]}
    logger = MagicMock()
    configure_rating_updates(params, "plex", logger)
    assert params["mass_user_rating_update"] is None
    logger.error.assert_called_once()


def test_clear_skips_a_known_unrated_profile():
    library = MagicMock()
    update_silo_ratings(library, SimpleNamespace(title="Example", data={"user_rating": 0}), {"silo_user": ["clear"]}, MagicMock())
    library.update_native_ratings.assert_not_called()


def test_failed_provider_write_does_not_block_profile_write():
    library = MagicMock()
    library.update_native_ratings.side_effect = [Failed("connection reset"), None]
    logger = MagicMock()
    item = SimpleNamespace(title="Example", data={})
    update_silo_ratings(library, item, {"silo_imdb": [8], "silo_user": [7]}, logger)
    assert library.update_native_ratings.call_args_list == [call(item, {"rating_imdb": 8}), call(item, {"user_rating": 4})]
    logger.error.assert_called_once()
    logger.info.assert_called_once_with("silo_user Updated | 4")
