from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

import httpx
import pytest
from tenacity import wait_none

from modules.serializd import Serializd
from modules.util import Failed


@patch("modules.serializd.SerializdClient")
def test_authenticates_with_configured_credentials(client_class):
    client = client_class.return_value

    Serializd("user@example.com", "secret")

    client.login.assert_called_once_with(email="user@example.com", password="secret")


@patch("modules.serializd.SerializdClient")
def test_cache_key_is_account_specific_without_exposing_email(client_class):
    first = Serializd("User@Example.com", "secret")
    same = Serializd(" user@example.com ", "secret")
    other = Serializd("other@example.com", "secret")

    assert first.cache_key == same.cache_key
    assert first.cache_key != other.cache_key
    assert "user@example.com" not in first.cache_key


@patch("modules.serializd.SerializdClient")
def test_returns_show_genre_names(client_class):
    client_class.return_value.get_show.return_value = SimpleNamespace(genres=[SimpleNamespace(name="Drama"), SimpleNamespace(name="Mystery")])
    serializd = Serializd("user@example.com", "secret")

    assert serializd.get_show_genres(1396) == ["Drama", "Mystery"]
    client_class.return_value.get_show.assert_called_once_with(1396)


@patch("modules.serializd.SerializdClient")
def test_authentication_failure_becomes_kometa_error(client_class):
    client_class.return_value.login.side_effect = RuntimeError("bad credentials")

    with pytest.raises(Failed, match="Failed to authenticate: bad credentials"):
        Serializd("user@example.com", "wrong")


@patch("modules.serializd.SerializdClient")
def test_retries_transient_authentication_timeout(client_class):
    client = client_class.return_value
    client.login.side_effect = [httpx.ReadTimeout("slow response"), None]

    Serializd("user@example.com", "secret", timeout=90)

    assert client.login.call_count == 2
    assert client.session.timeout == 90


@patch("modules.serializd.SerializdClient")
def test_returns_all_nanogenres_without_leading_emoji(client_class):
    response = client_class.return_value.session.get.return_value
    response.json.return_value = {
        "nanogenres": [
            {"name": "🌸 Anime", "count": 129},
            {"name": "👹 Monsters", "count": 123},
            {"name": "☢️ Post-Apocalyptic", "count": 86},
        ]
    }
    serializd = Serializd("user@example.com", "secret")

    assert serializd.get_show_nanogenres(1429) == ["Anime", "Monsters", "Post-Apocalyptic"]
    client_class.return_value.session.get.assert_called_once_with("/show/1429/nanogenres")
    response.raise_for_status.assert_called_once()


@patch("modules.serializd.SerializdClient")
def test_nanogenre_without_emoji_keeps_full_multiword_name(client_class):
    client_class.return_value.session.get.return_value.json.return_value = {
        "nanogenres": [
            {"name": "Science Fiction", "count": 10},
            {"name": "🌸Anime", "count": 9},
        ]
    }
    serializd = Serializd("user@example.com", "secret")

    assert serializd.get_show_nanogenres(1668) == ["Science Fiction", "Anime"]


@patch("modules.serializd.SerializdClient")
def test_returns_show_community_rating(client_class):
    response = client_class.return_value.session.get.return_value
    response.json.return_value = {"averageRating": 9.07}
    serializd = Serializd("user@example.com", "secret")

    assert serializd.get_show_rating(1429) == 9.07
    response.raise_for_status.assert_called_once()
    client_class.return_value.session.get.assert_called_once_with("https://serializd.onrender.com/mobile/page/show_v2_part_1/1429")


@patch("modules.serializd.SerializdClient")
def test_retries_show_rating_after_rate_limit(client_class, monkeypatch):
    request = httpx.Request("GET", "https://serializd.onrender.com/mobile/page/show_v2_part_1/1429")
    limited = httpx.Response(429, headers={"Retry-After": "30"}, request=request)
    success = MagicMock()
    success.json.return_value = {"averageRating": 9.07}
    client_class.return_value.session.get.side_effect = [limited, success]
    monkeypatch.setattr(Serializd._get_json.retry, "wait", wait_none())
    serializd = Serializd("user@example.com", "secret")

    assert serializd.get_show_rating(1429) == 9.07
    assert client_class.return_value.session.get.call_count == 2


@patch("modules.serializd.SerializdClient")
def test_rate_limit_exhaustion_becomes_kometa_error(client_class, monkeypatch):
    request = httpx.Request("GET", "https://serializd.onrender.com/mobile/page/show_v2_part_1/1429")
    limited = httpx.Response(429, headers={"Retry-After": "invalid"}, request=request)
    client_class.return_value.session.get.return_value = limited
    monkeypatch.setattr(Serializd._get_json.retry, "wait", wait_none())
    serializd = Serializd("user@example.com", "secret")

    with pytest.raises(Failed, match="Failed to fetch TMDb Show ID 1429"):
        serializd.get_show_rating(1429)
    assert client_class.return_value.session.get.call_count == 6


@patch("modules.serializd.SerializdClient")
def test_returns_episode_community_rating(client_class):
    response = client_class.return_value.session.get.return_value
    response.json.return_value = {"averageRating": 8.79}
    serializd = Serializd("user@example.com", "secret")

    assert serializd.get_episode_rating(1429, 1, 1) == 8.79
    client_class.return_value.session.get.assert_called_once_with("https://serializd.onrender.com/mobile/page/show/1429/season/1/episode_part_1/1")


@patch("modules.serializd.SerializdClient")
def test_returns_authenticated_users_episode_rating(client_class):
    response = client_class.return_value.session.get.return_value
    response.json.return_value = {"episodeReviewsForLoggedInUser": [{"rating": 9}]}
    serializd = Serializd("user@example.com", "secret")

    assert serializd.get_episode_user_rating(1429, 1, 1) == 9.0
    client_class.return_value.session.get.assert_called_once_with("https://serializd.onrender.com/mobile/page/show/1429/season/1/episode_part_2/1")


@patch("modules.serializd.SerializdClient")
def test_missing_authenticated_user_episode_rating_is_a_normal_source_failure(client_class):
    client_class.return_value.session.get.return_value.json.return_value = {"episodeReviewsForLoggedInUser": []}
    serializd = Serializd("user@example.com", "secret")

    with pytest.raises(Failed, match="No user rating found"):
        serializd.get_episode_user_rating(1429, 1, 1)


@patch("modules.serializd.SerializdClient")
def test_missing_community_rating_is_a_normal_source_failure(client_class):
    client_class.return_value.session.get.return_value.json.return_value = {"averageRating": 0}
    serializd = Serializd("user@example.com", "secret")

    with pytest.raises(Failed, match="No rating found"):
        serializd.get_episode_rating(1429, 1, 1)


@patch("modules.serializd.SerializdClient")
def test_logs_unique_watched_episode_numbers_for_season(client_class):
    client = client_class.return_value
    client.get_season.return_value = SimpleNamespace(seasonId=12345)
    client.log_episodes.return_value = True
    serializd = Serializd("user@example.com", "secret")

    assert serializd.log_watched_episodes(1429, 1, [3, 1, 3]) is True
    client.get_season.assert_called_once_with(1429, 1)
    client.log_episodes.assert_called_once_with(1429, 12345, [1, 3])


@patch("modules.serializd.SerializdClient")
def test_watched_episode_failure_becomes_kometa_error(client_class):
    client = client_class.return_value
    client.get_season.return_value = SimpleNamespace(seasonId=12345)
    client.log_episodes.return_value = False
    serializd = Serializd("user@example.com", "secret")

    with pytest.raises(Failed, match="Failed to mark watched episodes"):
        serializd.log_watched_episodes(1429, 1, [1])


def _json_response(data):
    response = MagicMock()
    response.json.return_value = data
    return response


@patch("modules.serializd.SerializdClient")
def test_validates_serializd_list_url_and_watchlist_values(client_class):
    serializd = Serializd("user@example.com", "secret")

    assert serializd.validate_builder("serializd_list", "https://www.serializd.com/list/live-action-ranked-662885") == [662885]
    assert serializd.validate_builder("serializd_watchlist", ["me", "noahhershey", "https://www.serializd.com/user/test-user/watchlist"]) == [
        "me",
        "noahhershey",
        "test-user",
    ]


@patch("modules.serializd.SerializdClient")
def test_rejects_non_serializd_list_url(client_class):
    serializd = Serializd("user@example.com", "secret")

    with pytest.raises(Failed, match="Invalid list URL"):
        serializd.validate_builder("serializd_list", "https://example.com/list/live-action-ranked-662885")


@patch("modules.serializd.SerializdClient")
def test_fetches_all_serializd_list_pages_and_deduplicates_shows(client_class):
    client = client_class.return_value
    client.session.get.side_effect = [
        _json_response({"listItems": [{"showId": 1399}, {"showId": 1396}, {"showId": 1399}]}),
        _json_response({"listItems": [{"showId": 60059}]}),
        _json_response({"listItems": []}),
    ]
    serializd = Serializd("user@example.com", "secret")

    assert serializd.get_builder_ids("serializd_list", 662885) == [(1399, "tmdb_show"), (1396, "tmdb_show"), (60059, "tmdb_show")]
    assert client.session.get.call_count == 3
    assert all(request.args[0].endswith("/list/list_items/662885") for request in client.session.get.call_args_list)


@patch("modules.serializd.SerializdClient")
def test_fetches_arbitrary_user_watchlist_through_api(client_class):
    client = client_class.return_value
    client.session.get.side_effect = [
        _json_response({"items": [{"showId": 1396}], "totalPages": 2}),
        _json_response({"items": [{"showId": 60059}], "totalPages": 2}),
    ]
    serializd = Serializd("user@example.com", "secret")

    assert serializd.get_builder_ids("serializd_watchlist", "noahhershey") == [(1396, "tmdb_show"), (60059, "tmdb_show")]
    assert client.session.get.call_args_list == [
        call("/user/noahhershey/watchlistpage_v2/1", params={"sort_by": "date_added_desc", "filters": "{}"}),
        call("/user/noahhershey/watchlistpage_v2/2", params={"sort_by": "date_added_desc", "filters": "{}"}),
    ]


@patch("modules.serializd.SerializdClient")
def test_me_watchlist_resolves_authenticated_username_through_api(client_class):
    client = client_class.return_value
    client.session.get.side_effect = [
        _json_response({"username": "yozoraxcii"}),
        _json_response({"items": [{"showId": 1429}], "totalPages": 1}),
    ]
    serializd = Serializd("user@example.com", "secret")

    assert serializd.get_builder_ids("serializd_watchlist", "me") == [(1429, "tmdb_show")]
    assert client.session.get.call_args_list[0] == call("/user_information")
    assert client.session.get.call_args_list[1] == call("/user/yozoraxcii/watchlistpage_v2/1", params={"sort_by": "date_added_desc", "filters": "{}"})


@patch("modules.serializd.SerializdClient")
def test_validates_serializd_chart_limits(client_class):
    serializd = Serializd("user@example.com", "secret")

    for method in ["serializd_trending", "serializd_popular", "serializd_featured"]:
        assert serializd.validate_builder(method, 10) == [10]
        with pytest.raises(Failed, match="integer greater than 0"):
            serializd.validate_builder(method, 0)


@patch("modules.serializd.SerializdClient")
@pytest.mark.parametrize(
    ("method", "endpoint", "result"),
    [
        ("serializd_trending", "trending_shows", {"id": 1396}),
        ("serializd_popular", "popular_shows", {"id": 1399}),
        ("serializd_featured", "featured", {"showDetails": {"id": 94997}}),
    ],
)
def test_fetches_serializd_homepage_charts(client_class, method, endpoint, result):
    client = client_class.return_value
    client.session.get.return_value = _json_response({"results": [result], "totalPages": 1})
    serializd = Serializd("user@example.com", "secret")

    expected_id = result.get("id") or result["showDetails"]["id"]
    assert serializd.get_builder_ids(method, 10) == [(expected_id, "tmdb_show")]
    client.session.get.assert_called_once_with(f"https://serializd.onrender.com/mobile/page/{endpoint}", params={"page": 1})


@patch("modules.serializd.SerializdClient")
def test_serializd_chart_honors_limit_across_pages(client_class):
    client = client_class.return_value
    client.session.get.side_effect = [
        _json_response({"results": [{"id": 1}, {"id": 2}], "totalPages": 2}),
        _json_response({"results": [{"id": 2}, {"id": 3}, {"id": 4}], "totalPages": 2}),
    ]
    serializd = Serializd("user@example.com", "secret")

    assert serializd.get_builder_ids("serializd_trending", 3) == [(1, "tmdb_show"), (2, "tmdb_show"), (3, "tmdb_show")]
    assert client.session.get.call_count == 2
