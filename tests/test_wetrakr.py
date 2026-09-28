from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest

from modules.util import Failed
from modules.wetrakr import WeTrakr
from tests.tracker_fakes import FakeConvert, FakeRequests, FakeResponse


def _iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _future(days=5):
    return _iso(datetime.now(UTC) + timedelta(days=days))


def _past(days=1):
    return _iso(datetime.now(UTC) - timedelta(days=days))


def auth(access="tok1", refresh="ref1", expires_at=None):
    return {"access_token": access, "refresh_token": refresh, "expires_at": expires_at}


def make_wetrakr(responses, expires_at=None, read_only=False, client_id="cid", config_data=None):
    requests = FakeRequests(responses, config_data=config_data)
    wetrakr = WeTrakr(requests, read_only, {"client_id": client_id, "config_path": "/cfg.yml", "authorization": auth(expires_at=expires_at)})
    return wetrakr, requests


# --- construction / client id ---


def test_user_agent_includes_local_version():
    wetrakr, _ = make_wetrakr([], expires_at=_future())
    assert wetrakr.user_agent == "Kometa/2.4.8-build5 (+https://kometa.wiki)"


def test_missing_authorization_raises_failed():
    requests = FakeRequests([])
    with pytest.raises(Failed, match="authorization is blank"):
        WeTrakr(requests, False, {"client_id": "cid", "config_path": "/cfg.yml", "authorization": None})


def test_missing_refresh_token_alone_also_raises_failed():
    requests = FakeRequests([])
    with pytest.raises(Failed, match="authorization is blank"):
        WeTrakr(requests, False, {"client_id": "cid", "config_path": "/cfg.yml", "authorization": {"access_token": "tok1"}})


def test_explicit_client_id_skips_public_lookup():
    wetrakr, requests = make_wetrakr([], expires_at=_future(), client_id="my-own-id")
    assert wetrakr.client_id == "my-own-id"
    assert len(requests.gets) == 0


def test_blank_client_id_fetches_public_id():
    requests = FakeRequests([FakeResponse(text="# comment\nWETRAKR_CLIENT_ID=shared-public-id\n")])
    wetrakr = WeTrakr(requests, False, {"client_id": None, "config_path": "/cfg.yml", "authorization": auth(expires_at=_future())})
    assert wetrakr.client_id == "shared-public-id"
    assert len(requests.gets) == 1


def test_public_client_id_fetch_failure_raises_failed():
    requests = FakeRequests([FakeResponse(status_code=500, reason="Internal Server Error")])
    with pytest.raises(Failed, match="Unable to fetch public Client IDs"):
        WeTrakr(requests, False, {"client_id": None, "config_path": "/cfg.yml", "authorization": auth(expires_at=_future())})


def test_public_client_id_missing_key_raises_failed():
    requests = FakeRequests([FakeResponse(text="SOME_OTHER_KEY=value\n")])
    with pytest.raises(Failed, match="Unable to find WETRAKR_CLIENT_ID"):
        WeTrakr(requests, False, {"client_id": None, "config_path": "/cfg.yml", "authorization": auth(expires_at=_future())})


# --- auth lifecycle ---


def test_no_refresh_when_expiry_is_far_in_the_future():
    wetrakr, requests = make_wetrakr([FakeResponse(json_data={"id": 1, "info": {"username": "chris"}, "plan": "free"})], expires_at=_future())
    wetrakr.test_connection()
    assert len(requests.posts) == 0
    assert len(requests.gets) == 1


def test_refreshes_when_expires_at_missing():
    wetrakr, requests = make_wetrakr(
        [
            FakeResponse(json_data={"access_token": "tok2", "new_refresh_token": "ref2", "expires_in": 604800}),
            FakeResponse(json_data={"id": 1, "info": {"username": "chris"}, "plan": "free"}),
        ],
        expires_at=None,
    )
    wetrakr.test_connection()
    assert len(requests.posts) == 1
    assert wetrakr.access_token == "tok2"
    assert wetrakr.refresh_token == "ref2"


def test_refreshes_when_within_margin_even_though_not_yet_expired():
    # refresh_margin_seconds is 86400 (24h); an access token expiring in 1 hour should still trigger a proactive refresh.
    soon = _iso(datetime.now(UTC) + timedelta(hours=1))
    wetrakr, requests = make_wetrakr(
        [
            FakeResponse(json_data={"access_token": "tok2", "new_refresh_token": "ref2", "expires_in": 604800}),
            FakeResponse(json_data={"id": 1, "info": {"username": "chris"}, "plan": "free"}),
        ],
        expires_at=soon,
    )
    wetrakr.test_connection()
    assert len(requests.posts) == 1


def test_refresh_falls_back_to_refresh_token_key_when_new_refresh_token_absent():
    wetrakr, _requests = make_wetrakr(
        [FakeResponse(json_data={"access_token": "tok2", "refresh_token": "ref2-fallback", "expires_in": 604800})],
        expires_at=None,
    )
    wetrakr._refresh_token()
    assert wetrakr.refresh_token == "ref2-fallback"


def test_refresh_writes_new_authorization_back_to_config():
    wetrakr, requests = make_wetrakr(
        [FakeResponse(json_data={"access_token": "tok2", "new_refresh_token": "ref2", "expires_in": 604800})],
        expires_at=None,
        config_data={"wetrakr": {"authorization": {"access_token": "tok1"}}},
    )
    wetrakr._refresh_token()
    assert requests._yaml.saved is True
    saved = requests._yaml.data["wetrakr"]["authorization"]
    assert saved["access_token"] == "tok2"
    assert saved["refresh_token"] == "ref2"
    assert saved["expires_at"] is not None


def test_refresh_preserves_other_config_keys():
    wetrakr, requests = make_wetrakr(
        [FakeResponse(json_data={"access_token": "tok2", "new_refresh_token": "ref2", "expires_in": 604800})],
        expires_at=None,
        config_data={"libraries": {"Movies": {}}, "wetrakr": {"client_id": "cid"}},
    )
    wetrakr._refresh_token()
    assert requests._yaml.data["libraries"] == {"Movies": {}}
    assert requests._yaml.data["wetrakr"]["client_id"] == "cid"


def test_refresh_failure_raises_reauth_message():
    wetrakr, _requests = make_wetrakr([FakeResponse(status_code=400, json_data={"error": "invalid_grant"})], expires_at=None)
    with pytest.raises(Failed, match="re-run the Kometa Utilities"):
        wetrakr._refresh_token()


def test_read_only_never_refreshes_even_when_expired():
    wetrakr, requests = make_wetrakr([], expires_at=_past(), read_only=True)
    with pytest.raises(Failed, match="read_only"):
        wetrakr.test_connection()
    assert len(requests.posts) == 0


def test_read_only_with_valid_token_succeeds_without_refresh():
    wetrakr, requests = make_wetrakr([FakeResponse(json_data={"id": 1, "info": {"username": "chris"}, "plan": "free"})], expires_at=_future(), read_only=True)
    wetrakr.test_connection()
    assert len(requests.posts) == 0


def test_mid_run_401_refreshes_once_and_retries_the_call():
    wetrakr, requests = make_wetrakr(
        [
            FakeResponse(status_code=401, json_data={"message": "expired"}),
            FakeResponse(json_data={"access_token": "tok2", "new_refresh_token": "ref2", "expires_in": 604800}),
            FakeResponse(json_data=[{"type": "movie", "id": 1, "ids": {"tmdb": 550}}]),
        ],
        expires_at=_future(),
    )
    items = wetrakr._request_paginated("/sync/lists")
    assert items == [{"type": "movie", "id": 1, "ids": {"tmdb": 550}}]
    assert len(requests.posts) == 1


def test_mid_run_401_retry_uses_the_refreshed_bearer_token():
    wetrakr, requests = make_wetrakr(
        [
            FakeResponse(status_code=401, json_data={"message": "expired"}),
            FakeResponse(json_data={"access_token": "tok2", "new_refresh_token": "ref2", "expires_in": 604800}),
            FakeResponse(json_data=[]),
        ],
        expires_at=_future(),
    )
    wetrakr._request_paginated("/sync/lists")
    retry_headers = requests.gets[-1][1]
    assert retry_headers["Authorization"] == "Bearer tok2"


def test_second_401_after_refresh_fails_without_looping():
    wetrakr, requests = make_wetrakr(
        [
            FakeResponse(status_code=401, json_data={"message": "expired"}),
            FakeResponse(json_data={"access_token": "tok2", "new_refresh_token": "ref2", "expires_in": 604800}),
            FakeResponse(status_code=401, json_data={"message": "still bad"}),
        ],
        expires_at=_future(),
    )
    with pytest.raises(Failed, match="re-run the Kometa Utilities"):
        wetrakr._request_paginated("/sync/lists")
    assert len(requests.posts) == 1


def test_401_on_the_refresh_call_itself_does_not_recurse():
    wetrakr, requests = make_wetrakr([FakeResponse(status_code=401, json_data={"message": "bad refresh token"})], expires_at=None)
    with pytest.raises(Failed, match="re-run the Kometa Utilities"):
        wetrakr._refresh_token()
    assert len(requests.posts) == 1


def test_read_only_does_not_auto_refresh_on_a_mid_run_401():
    wetrakr, requests = make_wetrakr([FakeResponse(status_code=401, json_data={"message": "expired"})], expires_at=_future(), read_only=True)
    with pytest.raises(Failed, match="authorization was rejected"):
        wetrakr._request_paginated("/sync/lists")
    assert len(requests.posts) == 0


# --- headers ---


def test_headers_include_api_key_version_and_bearer_token():
    wetrakr, _ = make_wetrakr([], expires_at=_future(), client_id="my-key")
    headers = wetrakr._headers()
    assert headers["wetrakr-api-key"] == "my-key"
    assert headers["wetrakr-api-version"] == "1"
    assert headers["Authorization"] == "Bearer tok1"


def test_anonymous_headers_omit_authorization():
    wetrakr, _ = make_wetrakr([], expires_at=_future())
    headers = wetrakr._headers(anonymous=True)
    assert "Authorization" not in headers
    assert headers["wetrakr-api-key"] == "cid"


# --- rate limiting / quota ---


def test_quota_exceeded_fails_fast_without_sleeping():
    with patch("time.sleep") as mock_sleep:
        wetrakr, _requests = make_wetrakr([FakeResponse(status_code=429, json_data={"error": "QUOTA_EXCEEDED", "message": "daily limit hit"})], expires_at=_future())
        with pytest.raises(Failed, match="daily quota exceeded"):
            wetrakr._request("/account/settings")
        mock_sleep.assert_not_called()


def test_per_minute_429_sleeps_the_rate_limit_reset_value_then_succeeds():
    with patch("time.sleep") as mock_sleep:
        wetrakr, _requests = make_wetrakr(
            [
                FakeResponse(status_code=429, json_data={"message": "Too many requests. Please slow down."}, headers={"RateLimit-Reset": "5"}),
                FakeResponse(json_data={"id": 1, "info": {"username": "chris"}, "plan": "free"}),
            ],
            expires_at=_future(),
        )
        wetrakr._request("/account/settings")
        mock_sleep.assert_called_once_with(5.0)


def test_429_without_rate_limit_reset_header_falls_back_to_default_wait():
    with patch("time.sleep") as mock_sleep:
        wetrakr, _requests = make_wetrakr(
            [
                FakeResponse(status_code=429, json_data={"message": "slow down"}, headers={}),
                FakeResponse(json_data={"id": 1, "info": {"username": "chris"}, "plan": "free"}),
            ],
            expires_at=_future(),
        )
        wetrakr._request("/account/settings")
        mock_sleep.assert_called_once_with(wetrakr.default_retry_wait)


# --- status code mapping (_raise_for_status) ---


def test_401_raises_authorization_rejected_when_already_read_only():
    wetrakr, _requests = make_wetrakr([FakeResponse(status_code=401, json_data={"message": "bad token"})], expires_at=_future(), read_only=True)
    with pytest.raises(Failed, match="authorization was rejected"):
        wetrakr._request("/account/settings")


def test_400_on_lists_path_reports_private_or_friends_only():
    wetrakr, _requests = make_wetrakr([FakeResponse(status_code=400, json_data={"message": "forbidden"})], expires_at=_future())
    with pytest.raises(Failed, match="is private or friends-only"):
        wetrakr._request("/lists/13255")


def test_400_off_the_lists_path_falls_back_to_generic_handling():
    wetrakr, _requests = make_wetrakr([FakeResponse(status_code=400, json_data={"message": "bad request"})], expires_at=_future())
    with pytest.raises(Failed, match=r"\(400\) bad request"):
        wetrakr._request("/account/settings")


def test_403_names_app_key_rejection():
    wetrakr, _requests = make_wetrakr([FakeResponse(status_code=403, json_data={"message": "blocked"})], expires_at=_future())
    with pytest.raises(Failed, match="app key rejected or blocked at the edge"):
        wetrakr._request("/account/settings")


def test_420_includes_upgrade_url_when_present():
    wetrakr, _requests = make_wetrakr([FakeResponse(status_code=420, json_data={"message": "needs VIP", "upgrade": {"url": "https://wetrakr.com/upgrade"}})], expires_at=_future())
    with pytest.raises(Failed, match=r"needs VIP \(https://wetrakr.com/upgrade\)"):
        wetrakr._request("/account/settings")


def test_420_without_upgrade_url_has_no_parenthetical_suffix():
    wetrakr, _requests = make_wetrakr([FakeResponse(status_code=420, json_data={"message": "needs VIP"})], expires_at=_future())
    with pytest.raises(Failed) as excinfo:
        wetrakr._request("/account/settings")
    assert str(excinfo.value).endswith("needs VIP")


def test_423_names_suspended_app_key():
    wetrakr, _requests = make_wetrakr([FakeResponse(status_code=423, json_data={"message": "suspended"})], expires_at=_future())
    with pytest.raises(Failed, match="Kometa's WeTrakr app key is suspended"):
        wetrakr._request("/account/settings")


def test_426_names_vip_requirement():
    wetrakr, _requests = make_wetrakr([FakeResponse(status_code=426, json_data={"message": "VIP only endpoint"})], expires_at=_future())
    with pytest.raises(Failed, match="needs WeTrakr VIP"):
        wetrakr._request("/account/settings")


def test_unmapped_5xx_falls_through_to_generic_tracker_handling():
    wetrakr, _requests = make_wetrakr([FakeResponse(status_code=500, json_data={"message": "server error"}, reason="Internal Server Error")], expires_at=_future())
    with pytest.raises(Failed, match=r"\(500\) server error"):
        wetrakr._request("/account/settings")


# --- cursor pagination (_request_cursor) ---


def test_cursor_pagination_follows_next_header_and_stops_when_absent():
    wetrakr, requests = make_wetrakr(
        [
            FakeResponse(json_data=[{"type": "movie", "id": 1}], headers={"X-Pagination-Next": "cursor2"}),
            FakeResponse(json_data=[{"type": "movie", "id": 2}], headers={}),
        ],
        expires_at=_future(),
    )
    items = wetrakr._request_cursor("/sync/favorites/movies")
    assert items == [{"type": "movie", "id": 1}, {"type": "movie", "id": 2}]
    assert len(requests.gets) == 2


def test_cursor_pagination_sends_compact_and_limit_defaults():
    wetrakr, requests = make_wetrakr([FakeResponse(json_data=[], headers={})], expires_at=_future())
    wetrakr._request_cursor("/sync/favorites/movies")
    _, _, params = requests.gets[0]
    assert params == {"compact": "true", "limit": 1000}


def test_cursor_pagination_second_page_includes_after_param():
    wetrakr, requests = make_wetrakr(
        [
            FakeResponse(json_data=[{"type": "movie", "id": 1}], headers={"X-Pagination-Next": "cursor2"}),
            FakeResponse(json_data=[], headers={}),
        ],
        expires_at=_future(),
    )
    wetrakr._request_cursor("/sync/favorites/movies")
    _, _, second_page_params = requests.gets[1]
    assert second_page_params["after"] == "cursor2"


def test_cursor_pagination_stops_on_204():
    wetrakr, _requests = make_wetrakr([FakeResponse(status_code=204, content=b"", headers={})], expires_at=_future())
    items = wetrakr._request_cursor("/sync/favorites/movies")
    assert items == []


def test_cursor_pagination_non_json_body_raises_failed():
    wetrakr, _requests = make_wetrakr([FakeResponse(content=b"not json", text="not json", raise_on_json=True)], expires_at=_future())
    with pytest.raises(Failed, match="non-JSON response body"):
        wetrakr._request_cursor("/sync/favorites/movies")


# --- _parse_media ---


def test_parse_media_skips_season_episode_and_person_rows():
    wetrakr, _ = make_wetrakr([], expires_at=_future())
    items = [
        {"type": "movie", "id": 1, "ids": {"tmdb": 550}},
        {"type": "episode", "id": 2, "ids": {}},
        {"type": "season", "id": 3, "ids": {}},
        {"type": "person", "id": 4, "ids": {}},
    ]
    assert wetrakr._parse_media(items, None) == [(550, "tmdb")]


def test_parse_media_falls_back_to_native_id_when_no_tmdb_tvdb_imdb():
    wetrakr, _ = make_wetrakr([], expires_at=_future())
    items = [{"type": "movie", "id": 1, "ids": {}, "title": "Untitled"}]
    assert wetrakr._parse_media(items, None) == []


# --- _parse_list_id / validate_lists ---


@pytest.mark.parametrize(
    "value,expected",
    [
        (13255, 13255),
        ("13255", 13255),
        ("https://wetrakr.com/lists/13255", 13255),
        ("https://wetrakr.com/lists/13255/", 13255),
    ],
)
def test_parse_list_id_accepts_bare_id_and_url(value, expected):
    assert WeTrakr._parse_list_id(value) == expected


def test_parse_list_id_rejects_garbage():
    with pytest.raises(Failed, match="Could not parse a list id"):
        WeTrakr._parse_list_id("not-a-list")


def test_parse_list_id_rejects_bool():
    with pytest.raises(Failed, match="Could not parse a list id"):
        WeTrakr._parse_list_id(True)


def test_validate_lists_returns_ids_for_multiple_values():
    wetrakr, _ = make_wetrakr([], expires_at=_future())
    assert wetrakr.validate_lists("Collection", ["13255", "https://wetrakr.com/lists/1033032976"]) == [13255, 1033032976]


def test_validate_lists_rejects_dict_entries():
    wetrakr, _ = make_wetrakr([], expires_at=_future())
    with pytest.raises(Failed, match="cannot be a dictionary"):
        wetrakr.validate_lists("Collection", [{"bad": True}])


def test_validate_lists_rejects_empty():
    wetrakr, _ = make_wetrakr([], expires_at=_future())
    with pytest.raises(Failed, match="No valid WeTrakr Lists"):
        wetrakr.validate_lists("Collection", [])


# --- _parse_user_id / validate_user_id ---


def test_parse_user_id_accepts_numeric_int_and_string():
    wetrakr, _requests = make_wetrakr([], expires_at=_future())
    assert wetrakr._parse_user_id(275) == 275
    assert wetrakr._parse_user_id("275") == 275


def test_parse_user_id_resolves_a_bare_username():
    results = [
        {"id": 44, "type": "user", "username": "elvis"},
        {"id": 6777, "type": "user", "username": "elvin210"},
    ]
    wetrakr, requests = make_wetrakr([FakeResponse(json_data=results, headers={})], expires_at=_future())
    assert wetrakr._parse_user_id("elvis") == 44
    assert requests.gets[0][0].endswith("/search")


def test_parse_user_id_resolves_a_username_from_a_profile_url():
    results = [{"id": 44, "type": "user", "username": "elvis"}]
    wetrakr, _requests = make_wetrakr([FakeResponse(json_data=results, headers={})], expires_at=_future())
    assert wetrakr._parse_user_id("https://wetrakr.com/user/elvis") == 44


def test_resolve_user_id_matches_case_insensitively():
    results = [{"id": 1976, "type": "user", "username": "Elishaya13"}]
    wetrakr, _requests = make_wetrakr([FakeResponse(json_data=results, headers={})], expires_at=_future())
    assert wetrakr._parse_user_id("elishaya13") == 1976


def test_resolve_user_id_raises_when_no_exact_username_match():
    results = [{"id": 6777, "type": "user", "username": "elvin210"}]
    wetrakr, _requests = make_wetrakr([FakeResponse(json_data=results, headers={})], expires_at=_future())
    with pytest.raises(Failed, match="user elvis not found"):
        wetrakr._parse_user_id("elvis")


def test_resolve_user_id_memoizes_the_search():
    results = [{"id": 44, "type": "user", "username": "elvis"}]
    wetrakr, requests = make_wetrakr([FakeResponse(json_data=results, headers={})], expires_at=_future())
    wetrakr._parse_user_id("elvis")
    wetrakr._parse_user_id("elvis")
    assert len(requests.gets) == 1


def test_validate_user_id_delegates_to_parse_user_id():
    wetrakr, _requests = make_wetrakr([], expires_at=_future())
    assert wetrakr.validate_user_id("Collection", "275") == 275


# --- validate_flag / validate_ratings (thin delegation to the shared Layer 0 functions) ---


def test_validate_flag_delegates_to_shared_tracker_function():
    assert WeTrakr.validate_flag("Collection", "wetrakr_favorites", None) is True
    assert WeTrakr.validate_flag("Collection", "wetrakr_favorites", False) is False


def test_validate_ratings_delegates_to_shared_tracker_function():
    assert WeTrakr.validate_ratings("Collection", None) == {"minimum": None, "maximum": None}
    assert WeTrakr.validate_ratings("Collection", 7) == {"minimum": 7.0, "maximum": None}
    assert WeTrakr.validate_ratings("Collection", {"minimum": 7, "maximum": 9}) == {"minimum": 7.0, "maximum": 9.0}


# --- validate_tracking ---


def test_validate_tracking_blank_or_true_enables_every_status():
    expected = {status: True for status in ["planning", "watching", "waiting", "watched", "paused", "dropped"]}
    assert WeTrakr.validate_tracking("Collection", None) == expected
    assert WeTrakr.validate_tracking("Collection", True) == expected


def test_validate_tracking_false_disables_every_status():
    expected = {status: False for status in ["planning", "watching", "waiting", "watched", "paused", "dropped"]}
    assert WeTrakr.validate_tracking("Collection", False) == expected


def test_validate_tracking_dict_is_case_insensitive():
    result = WeTrakr.validate_tracking("Collection", {"Watching": True, "DROPPED": False})
    assert result["watching"] is True
    assert result["dropped"] is False


def test_validate_tracking_dict_defaults_unlisted_statuses_to_true():
    # A partial dict only overrides the statuses it names; every other status still defaults to enabled.
    result = WeTrakr.validate_tracking("Collection", {"watching": True})
    assert result["planning"] is True
    assert result["watched"] is True


def test_validate_tracking_all_false_dict_raises_no_enabled_statuses():
    with pytest.raises(Failed, match="has no enabled statuses"):
        WeTrakr.validate_tracking("Collection", {status: False for status in ["planning", "watching", "waiting", "watched", "paused", "dropped"]})


def test_validate_tracking_rejects_non_bool_non_dict():
    with pytest.raises(Failed, match="must be blank, true, false, or a dictionary"):
        WeTrakr.validate_tracking("Collection", "watching")


# --- list_description / _list_ids ---


def test_list_description_appends_wetrakr_credit_line():
    wetrakr, _ = make_wetrakr([FakeResponse(json_data={"description": "My favorite movies"})], expires_at=_future())
    assert wetrakr.list_description(13255) == "My favorite movies\n\nList from WeTrakr: https://wetrakr.com"


def test_list_description_links_to_the_list_page_when_public():
    wetrakr, _ = make_wetrakr([FakeResponse(json_data={"description": "My favorite movies", "privacy": "public"})], expires_at=_future())
    assert wetrakr.list_description(13255) == "My favorite movies\n\nList from WeTrakr: https://wetrakr.com/lists/13255"


def test_list_description_blank_when_missing():
    wetrakr, _ = make_wetrakr([FakeResponse(json_data={})], expires_at=_future())
    assert wetrakr.list_description(13255) == ""


def test_list_ids_uses_movies_target_for_movie_libraries():
    wetrakr, requests = make_wetrakr([FakeResponse(json_data=[{"type": "movie", "id": 1, "ids": {"tmdb": 550}}], headers={})], expires_at=_future())
    ids = wetrakr._list_ids(13255, True)
    assert ids == [(550, "tmdb")]
    url = requests.gets[0][0]
    assert url.endswith("/lists/13255/items/movies")


def test_list_ids_uses_all_target_for_playlist_mode():
    wetrakr, requests = make_wetrakr([FakeResponse(json_data=[], headers={})], expires_at=_future())
    wetrakr._list_ids(13255, None)
    url = requests.gets[0][0]
    assert url.endswith("/lists/13255/items/all")


def test_list_ids_is_memoized_per_list_and_target():
    wetrakr, requests = make_wetrakr([FakeResponse(json_data=[{"type": "movie", "id": 1, "ids": {"tmdb": 550}}], headers={})], expires_at=_future())
    ids1 = wetrakr._list_ids(13255, True)
    ids2 = wetrakr._list_ids(13255, True)
    assert ids1 == ids2
    assert len(requests.gets) == 1


# --- _user_lists_ids ---


def test_user_lists_ids_raises_when_user_not_found():
    wetrakr, _requests = make_wetrakr([FakeResponse(status_code=404, json_data={"message": "not found"})], expires_at=_future())
    with pytest.raises(Failed, match="user 275 not found"):
        wetrakr._user_lists_ids(275, None)


def test_user_lists_ids_raises_when_no_public_lists():
    wetrakr, _requests = make_wetrakr([FakeResponse(json_data=[], headers={})], expires_at=_future())
    with pytest.raises(Failed, match="has no public lists"):
        wetrakr._user_lists_ids(275, None)


def test_user_lists_ids_skips_non_public_and_locked_lists():
    wetrakr, requests = make_wetrakr(
        [
            FakeResponse(json_data=[{"id": 1, "privacy": "public", "locked": False}, {"id": 2, "privacy": "friends", "locked": False}, {"id": 3, "privacy": "public", "locked": True}], headers={}),
            FakeResponse(json_data=[{"type": "movie", "id": 10, "ids": {"tmdb": 550}}], headers={}),
        ],
        expires_at=_future(),
    )
    ids = wetrakr._user_lists_ids(275, None)
    assert ids == [(550, "tmdb")]
    # only list 1's items were ever fetched - lists 2 and 3 were skipped before any items request.
    assert len(requests.gets) == 2


def test_user_lists_ids_dedupes_items_shared_across_lists():
    wetrakr, _requests = make_wetrakr(
        [
            FakeResponse(json_data=[{"id": 1, "privacy": "public", "locked": False}, {"id": 2, "privacy": "public", "locked": False}], headers={}),
            FakeResponse(json_data=[{"type": "movie", "id": 10, "ids": {"tmdb": 550}}], headers={}),
            FakeResponse(json_data=[{"type": "movie", "id": 11, "ids": {"tmdb": 550}}], headers={}),
        ],
        expires_at=_future(),
    )
    ids = wetrakr._user_lists_ids(275, None)
    assert ids == [(550, "tmdb")]


# --- _tracking_ids ---


def test_tracking_ids_movie_library_only_requests_valid_statuses():
    wetrakr, requests = make_wetrakr(
        [FakeResponse(json_data=[{"type": "movie", "id": 1, "ids": {"tmdb": 550}}], headers={}), FakeResponse(json_data=[], headers={}), FakeResponse(json_data=[], headers={})],
        expires_at=_future(),
    )
    statuses = WeTrakr.validate_tracking("Collection", None)
    ids = wetrakr._tracking_ids(statuses, True)
    assert ids == [(550, "tmdb")]
    called_paths = [g[0] for g in requests.gets]
    assert len(called_paths) == 3
    for path in called_paths:
        assert any(status in path for status in ["planning", "watched", "dropped"])
        assert not any(status in path for status in ["watching", "waiting", "paused"])


def test_tracking_ids_show_library_requests_all_six_statuses():
    responses = [FakeResponse(json_data=[], headers={}) for _ in range(6)]
    wetrakr, requests = make_wetrakr(responses, expires_at=_future())
    statuses = WeTrakr.validate_tracking("Collection", None)
    wetrakr._tracking_ids(statuses, False)
    assert len(requests.gets) == 6


def test_tracking_ids_raises_when_no_statuses_valid_for_library():
    wetrakr, _requests = make_wetrakr([], expires_at=_future())
    statuses = {"watching": True, "waiting": True, "paused": True, "planning": False, "watched": False, "dropped": False}
    with pytest.raises(Failed, match="no statuses valid for a movie library"):
        wetrakr._tracking_ids(statuses, True)


def test_tracking_ids_memoizes_per_status():
    wetrakr, requests = make_wetrakr([FakeResponse(json_data=[], headers={})], expires_at=_future())
    statuses = {"planning": True, "watching": False, "waiting": False, "watched": False, "paused": False, "dropped": False}
    ids1 = wetrakr._tracking_ids(statuses, None)
    ids2 = wetrakr._tracking_ids(statuses, None)
    assert ids1 == ids2 == []
    assert len(requests.gets) == 1


# --- _favorites_ids ---


def test_favorites_ids_fetches_and_parses():
    wetrakr, requests = make_wetrakr([FakeResponse(json_data=[{"type": "show", "id": 1, "ids": {"tmdb": 1396}}], headers={})], expires_at=_future())
    ids = wetrakr._favorites_ids(False)
    assert ids == [(1396, "tmdb_show")]
    assert requests.gets[0][0].endswith("/sync/favorites/shows")


# --- _ratings_ids ---


def test_ratings_ids_filters_by_minimum_and_maximum():
    items = [
        {"type": "movie", "id": 1, "ids": {"tmdb": 1}, "rating": 3.0},
        {"type": "movie", "id": 2, "ids": {"tmdb": 2}, "rating": 7.5},
        {"type": "movie", "id": 3, "ids": {"tmdb": 3}, "rating": 9.5},
    ]
    wetrakr, _requests = make_wetrakr([FakeResponse(json_data=items, headers={})], expires_at=_future())
    ids = wetrakr._ratings_ids({"minimum": 5, "maximum": 9}, None)
    assert ids == [(2, "tmdb")]


def test_ratings_ids_skips_items_with_no_rating():
    items = [{"type": "movie", "id": 1, "ids": {"tmdb": 1}, "rating": None}]
    wetrakr, _requests = make_wetrakr([FakeResponse(json_data=items, headers={})], expires_at=_future())
    assert wetrakr._ratings_ids({"minimum": None, "maximum": None}, None) == []


def test_ratings_ids_memoizes_the_underlying_fetch_across_filter_calls():
    items = [{"type": "movie", "id": 1, "ids": {"tmdb": 550}, "rating": 8.0}]
    wetrakr, requests = make_wetrakr([FakeResponse(json_data=items, headers={})], expires_at=_future())
    ids1 = wetrakr._ratings_ids({"minimum": 5}, None)
    ids2 = wetrakr._ratings_ids({"minimum": 7}, None)
    assert ids1 == ids2 == [(550, "tmdb")]
    assert len(requests.gets) == 1


# --- get_wetrakr_ids dispatch ---


def test_get_wetrakr_ids_dispatches_list_and_list_details_the_same_way():
    wetrakr, _requests = make_wetrakr([FakeResponse(json_data=[{"type": "movie", "id": 1, "ids": {"tmdb": 550}}], headers={})], expires_at=_future())
    assert wetrakr.get_wetrakr_ids("wetrakr_list", 13255, None) == [(550, "tmdb")]


def test_get_wetrakr_ids_dispatches_list_details():
    wetrakr, _requests = make_wetrakr([FakeResponse(json_data=[{"type": "movie", "id": 1, "ids": {"tmdb": 550}}], headers={})], expires_at=_future())
    assert wetrakr.get_wetrakr_ids("wetrakr_list_details", 13255, None) == [(550, "tmdb")]


def test_get_wetrakr_ids_dispatches_user_lists():
    wetrakr, _requests = make_wetrakr(
        [FakeResponse(json_data=[{"id": 1, "privacy": "public", "locked": False}], headers={}), FakeResponse(json_data=[{"type": "movie", "id": 1, "ids": {"tmdb": 550}}], headers={})],
        expires_at=_future(),
    )
    assert wetrakr.get_wetrakr_ids("wetrakr_user_lists", 275, None) == [(550, "tmdb")]


def test_get_wetrakr_ids_dispatches_tracking():
    responses = [FakeResponse(json_data=[], headers={}) for _ in range(6)]
    wetrakr, _requests = make_wetrakr(responses, expires_at=_future())
    statuses = WeTrakr.validate_tracking("Collection", None)
    assert wetrakr.get_wetrakr_ids("wetrakr_tracking", statuses, False) == []


def test_get_wetrakr_ids_dispatches_favorites():
    wetrakr, _requests = make_wetrakr([FakeResponse(json_data=[], headers={})], expires_at=_future())
    assert wetrakr.get_wetrakr_ids("wetrakr_favorites", True, None) == []


def test_get_wetrakr_ids_dispatches_ratings():
    wetrakr, _requests = make_wetrakr([FakeResponse(json_data=[], headers={})], expires_at=_future())
    assert wetrakr.get_wetrakr_ids("wetrakr_ratings", {"minimum": None, "maximum": None}, None) == []


def test_get_wetrakr_ids_unsupported_method_raises_failed():
    wetrakr, _requests = make_wetrakr([], expires_at=_future())
    with pytest.raises(Failed, match="Method wetrakr_bogus not supported"):
        wetrakr.get_wetrakr_ids("wetrakr_bogus", None, None)


# --- test_connection ---


def test_connection_logs_username_and_plan():
    wetrakr, requests = make_wetrakr([FakeResponse(json_data={"id": 1, "info": {"username": "chris"}, "plan": "vip"})], expires_at=_future())
    wetrakr.test_connection()
    assert len(requests.gets) == 1


def test_connection_succeeds_without_a_username_in_the_response():
    wetrakr, requests = make_wetrakr([FakeResponse(json_data={"id": 1})], expires_at=_future())
    wetrakr.test_connection()
    assert len(requests.gets) == 1


# --- _resolve_list ---


def test_resolve_list_matches_by_numeric_id():
    wetrakr, requests = make_wetrakr([FakeResponse(json_data=[{"id": 1003620444, "name": "Watchlist"}], headers={})], expires_at=_future())
    list_id, created = wetrakr._resolve_list(1003620444)
    assert (list_id, created) == (1003620444, False)


def test_resolve_list_matches_by_exact_name():
    wetrakr, requests = make_wetrakr([FakeResponse(json_data=[{"id": 1003620444, "name": "Recently Added"}], headers={})], expires_at=_future())
    list_id, created = wetrakr._resolve_list("Recently Added")
    assert (list_id, created) == (1003620444, False)


def test_resolve_list_creates_when_no_name_match_with_explicit_private_privacy():
    wetrakr, requests = make_wetrakr(
        [
            FakeResponse(json_data=[], headers={}),
            FakeResponse(json_data={"id": 9310, "name": "New List"}),
        ],
        expires_at=_future(),
    )
    list_id, created = wetrakr._resolve_list("New List")
    assert (list_id, created) == (9310, True)
    create_call = requests.posts[0]
    assert create_call[1] == {"name": "New List", "privacy": "private"}


def test_resolve_list_unknown_id_raises_failed():
    wetrakr, requests = make_wetrakr([FakeResponse(json_data=[{"id": 1, "name": "Other"}], headers={})], expires_at=_future())
    with pytest.raises(Failed, match="not found among your own lists"):
        wetrakr._resolve_list(1003620444)


def test_resolve_list_does_not_page_the_lists_call():
    # WETRAKR-INTEGRATION-PLAN.md #8: "GET /sync/lists (not paged)" - a single call regardless of a page-count header.
    wetrakr, requests = make_wetrakr([FakeResponse(json_data=[{"id": 1003620444, "name": "Watchlist"}], headers={"X-Pagination-Page-Count": "3"})], expires_at=_future())
    wetrakr._resolve_list(1003620444)
    assert len(requests.gets) == 1


# --- sync_list / _sync_batch ---


def test_sync_list_adds_new_items_and_removes_stale_ones():
    wetrakr, requests = make_wetrakr(
        [
            FakeResponse(json_data=[{"id": 1003620444, "name": "My List"}], headers={}),  # _resolve_list
            FakeResponse(json_data=[{"type": "movie", "ids": {"tmdb": 999}}], headers={}),  # current items
            FakeResponse(json_data={"added": {"total": 1, "movies": 1}}),  # add batch
            FakeResponse(json_data={"removed": {"total": 1, "movies": 1}}),  # remove batch
        ],
        expires_at=_future(),
    )
    ids = [({"tmdb": 550}, "movie")]
    wetrakr.sync_list(FakeConvert(), 1003620444, ids)
    add_call = requests.posts[-2]
    assert add_call[0].endswith("/sync/lists/1003620444/items")
    assert add_call[1] == {"movies": [{"ids": {"tmdb": 550}}], "shows": []}
    remove_call = requests.posts[-1]
    assert remove_call[0].endswith("/sync/lists/1003620444/items/remove")
    assert remove_call[1] == {"movies": [{"ids": {"tmdb": 999}}], "shows": []}
    # WeTrakr removes via POST .../items/remove, never DELETE (unlike FlickList).
    assert requests.deletes == []


def test_sync_list_leaves_unmatched_current_items_alone():
    wetrakr, requests = make_wetrakr(
        [
            FakeResponse(json_data=[{"id": 1003620444, "name": "My List"}], headers={}),  # _resolve_list
            FakeResponse(json_data=[{"type": "movie", "ids": {}}], headers={}),  # current items, no usable id
            FakeResponse(json_data={"added": {"total": 1}}),  # add batch
        ],
        expires_at=_future(),
    )
    ids = [({"tmdb": 550}, "movie")]
    wetrakr.sync_list(FakeConvert(), 1003620444, ids)
    assert len(requests.posts) == 1  # just the add batch; no remove batch call at all since nothing was removable
    assert requests.deletes == []


def test_sync_list_chunks_batches_at_5000_items_and_keeps_body_under_1mb():
    current_page = FakeResponse(json_data=[], headers={})
    add_batches = [FakeResponse(json_data={"added": {"total": 5000}}), FakeResponse(json_data={"added": {"total": 1500}})]
    wetrakr, requests = make_wetrakr([FakeResponse(json_data=[{"id": 1003620444, "name": "Big List"}], headers={}), current_page] + add_batches, expires_at=_future())
    ids = [({"tmdb": i}, "movie") for i in range(6500)]
    wetrakr.sync_list(FakeConvert(), 1003620444, ids)
    assert len(requests.posts) == 2
    first_chunk = requests.posts[0][1]["movies"]
    second_chunk = requests.posts[1][1]["movies"]
    assert len(first_chunk) == 5000
    assert len(second_chunk) == 1500
    # Plan's own estimate: ~200KB at 5000 single-id items - comfortably under WeTrakr's 1MB body cap.
    import json

    assert len(json.dumps(requests.posts[0][1]).encode("utf-8")) < 1_000_000


def test_sync_list_unresolved_tvdb_conversion_does_not_delete_the_matching_tmdb_item():
    # Same D9 guarantee as FlickList's own test: a desired show that only carries tvdb this run
    # (Convert missed) must not cause deletion of a current item that shares that tvdb id.
    wetrakr, requests = make_wetrakr(
        [
            FakeResponse(json_data=[{"id": 1003620444, "name": "My List"}], headers={}),  # _resolve_list
            FakeResponse(json_data=[{"type": "show", "ids": {"tmdb": 1396, "tvdb": 81189}}], headers={}),  # current items
        ],
        expires_at=_future(),
    )
    ids = [({"tvdb": 81189}, "show")]  # Convert unavailable/misses -> FakeConvert() has no tvdb_to_tmdb_map entry
    wetrakr.sync_list(FakeConvert(), 1003620444, ids)
    # Nothing to add (already matched) and nothing to remove (still matched) - _sync_batch skips the call entirely for an empty payload.
    assert requests.posts == []


def test_sync_list_current_item_with_only_imdb_matches_desired_tmdb_via_convert():
    # WeTrakr's ids block has no native id (unlike FlickList's fldb) - imdb->tmdb via Convert is the
    # only bridge available when a current item carries only imdb.
    wetrakr, requests = make_wetrakr(
        [
            FakeResponse(json_data=[{"id": 1003620444, "name": "My List"}], headers={}),  # _resolve_list
            FakeResponse(json_data=[{"type": "movie", "ids": {"imdb": "tt0903747"}}], headers={}),  # current items
        ],
        expires_at=_future(),
    )
    convert = FakeConvert(imdb_to_tmdb_map={"tt0903747": (550, "movie")})
    ids = [({"tmdb": 550}, "movie")]
    wetrakr.sync_list(convert, 1003620444, ids)
    # Nothing to add (already matched via the imdb->tmdb bridge) and nothing to remove - no POST at all.
    assert requests.posts == []


def test_sync_list_logs_not_found_but_does_not_raise():
    wetrakr, requests = make_wetrakr(
        [
            FakeResponse(json_data=[{"id": 1003620444, "name": "My List"}], headers={}),
            FakeResponse(json_data=[], headers={}),
            FakeResponse(json_data={"added": {"total": 0}, "notFound": {"movies": [{"ids": {"imdb": "tt0000000"}}]}}),
        ],
        expires_at=_future(),
    )
    ids = [({"tmdb": 550}, "movie")]
    wetrakr.sync_list(FakeConvert(), 1003620444, ids)  # should not raise


def test_sync_list_already_added_error_is_logged_at_debug_not_as_a_failure():
    # WeTrakr reports a dupe as an `errored` entry with "error": "Already added!" (not a separate
    # `existing` array like FlickList) - this must not be treated as a real error.
    wetrakr, requests = make_wetrakr(
        [
            FakeResponse(json_data=[{"id": 1003620444, "name": "My List"}], headers={}),
            FakeResponse(json_data=[], headers={}),
            FakeResponse(json_data={"added": {"total": 0}, "errored": {"movies": [{"ids": {"tmdb": 603}, "error": "Already added!"}]}}),
        ],
        expires_at=_future(),
    )
    ids = [({"tmdb": 603}, "movie")]
    wetrakr.sync_list(FakeConvert(), 1003620444, ids)  # should not raise


def test_sync_list_real_error_is_logged_but_does_not_raise():
    wetrakr, requests = make_wetrakr(
        [
            FakeResponse(json_data=[{"id": 1003620444, "name": "My List"}], headers={}),
            FakeResponse(json_data=[], headers={}),
            FakeResponse(json_data={"added": {"total": 0}, "errored": {"movies": [{"ids": {"tmdb": 603}, "error": "Some other failure"}]}}),
        ],
        expires_at=_future(),
    )
    ids = [({"tmdb": 603}, "movie")]
    wetrakr.sync_list(FakeConvert(), 1003620444, ids)  # should not raise


def test_sync_batch_420_on_add_raises_failed():
    wetrakr, requests = make_wetrakr(
        [
            FakeResponse(json_data=[{"id": 1003620444, "name": "My List"}], headers={}),
            FakeResponse(json_data=[], headers={}),
            FakeResponse(status_code=420, json_data={"message": "list item limit reached", "upgrade": {"url": "https://wetrakr.com/upgrade"}}),
        ],
        expires_at=_future(),
    )
    ids = [({"tmdb": 550}, "movie")]
    with pytest.raises(Failed, match="list item limit reached"):
        wetrakr.sync_list(FakeConvert(), 1003620444, ids)


def test_sync_batch_skips_the_call_entirely_when_there_is_nothing_to_send():
    wetrakr, requests = make_wetrakr(
        [
            FakeResponse(json_data=[{"id": 1003620444, "name": "My List"}], headers={}),
            FakeResponse(json_data=[], headers={}),  # current items - nothing to remove, nothing desired to add
        ],
        expires_at=_future(),
    )
    wetrakr.sync_list(FakeConvert(), 1003620444, [])
    assert requests.posts == []  # resolve-list and current-items are both GETs; nothing to add or remove means no POST at all
    assert len(requests.gets) == 2
