from unittest.mock import patch

import pytest

from modules.flicklist import FlickList
from modules.util import Failed


class FakeResponse:
    def __init__(self, status_code=200, json_data=None, headers=None, content=b"{}", text=None, reason="OK", raise_on_json=False):
        self.status_code = status_code
        self._json_data = json_data
        self.headers = headers or {}
        self.content = content
        self.text = text if text is not None else ("" if content == b"" else content.decode("utf-8", errors="ignore"))
        self.reason = reason
        self._raise_on_json = raise_on_json

    def json(self):
        if self._raise_on_json:
            raise ValueError("not JSON")
        return self._json_data


class FakeRequests:
    def __init__(self, responses):
        self.local = "2.4.8-build5"
        self._responses = list(responses)
        self.gets = []
        self.posts = []

    def get(self, url, headers=None, params=None):
        self.gets.append((url, headers, params))
        return self._responses.pop(0)

    def post(self, url, json=None, headers=None):
        self.posts.append((url, json, headers))
        return self._responses.pop(0)


def make_flicklist(responses, read_only=False):
    return FlickList(FakeRequests(responses), read_only, {"api_key": "fs_live_test"})


def test_user_agent_includes_local_version():
    flicklist = make_flicklist([])
    assert flicklist.user_agent == "Kometa/2.4.8-build5 (+https://kometa.wiki)"


def test_test_connection_success_logs_username():
    flicklist = make_flicklist([FakeResponse(json_data={"username": "chris"})])
    flicklist.test_connection()
    assert flicklist._me == {"username": "chris"}


def test_test_connection_failure_raises_failed():
    flicklist = make_flicklist([FakeResponse(status_code=401, json_data={"error": "unauthorized"})])
    with pytest.raises(Failed, match="API key was rejected"):
        flicklist.test_connection()


def test_401_raises_revoked_message_without_retry():
    flicklist = make_flicklist([FakeResponse(status_code=401, json_data={"error": "unauthorized"})])
    with pytest.raises(Failed, match="revoked"):
        flicklist._request("/me")
    assert len(flicklist.requests.gets) == 1


def test_403_names_missing_scope():
    flicklist = make_flicklist([FakeResponse(status_code=403, json_data={"error": "forbidden"})])
    with pytest.raises(Failed, match=r"missing a required scope for /sync/watchlist"):
        flicklist._request("/sync/watchlist")


def test_non_json_error_body_on_500_raises_failed_not_valueerror():
    flicklist = make_flicklist([FakeResponse(status_code=500, content=b"internal server error", text="internal server error", raise_on_json=True, reason="Internal Server Error")])
    with pytest.raises(Failed, match="internal server error"):
        flicklist._request("/me")


@patch("time.sleep", return_value=None)
def test_429_with_retry_after_honors_header_value(mock_sleep):
    flicklist = make_flicklist(
        [
            FakeResponse(status_code=429, headers={"Retry-After": "5"}, json_data={"error": "rate_limited"}),
            FakeResponse(json_data={"username": "chris"}),
        ]
    )
    flicklist._request("/me")
    mock_sleep.assert_called_once_with(5.0)


@patch("time.sleep", return_value=None)
def test_429_without_header_and_html_body_still_backs_off(mock_sleep):
    flicklist = make_flicklist(
        [
            FakeResponse(status_code=429, headers={}, content=b"<html>rate limited</html>", text="<html>rate limited</html>", raise_on_json=True, reason="Too Many Requests"),
            FakeResponse(json_data={"username": "chris"}),
        ]
    )
    flicklist._request("/me")
    mock_sleep.assert_called_once_with(60.0)


@patch("time.sleep", return_value=None)
def test_429_gives_up_after_three_attempts(mock_sleep):
    responses = [FakeResponse(status_code=429, headers={}, json_data={"error": "rate_limited"}) for _ in range(3)]
    flicklist = make_flicklist(responses)
    with pytest.raises(Failed, match="Rate limited"):
        flicklist._request("/me")
    assert len(flicklist.requests.gets) == 3


def test_paginated_read_follows_page_count_header():
    flicklist = make_flicklist(
        [
            FakeResponse(json_data=[{"id": 1}], headers={"X-FlickList-Page-Count": "2", "X-FlickList-Limit": "500"}),
            FakeResponse(json_data=[{"id": 2}]),
        ]
    )
    results = flicklist._request_paginated("/lists/1/items")
    assert results == [{"id": 1}, {"id": 2}]
    assert len(flicklist.requests.gets) == 2


def test_paginated_read_without_page_count_header_is_single_page():
    flicklist = make_flicklist([FakeResponse(json_data=[{"id": 1}], headers={})])
    results = flicklist._request_paginated("/lists/1/items")
    assert results == [{"id": 1}]
    assert len(flicklist.requests.gets) == 1


def test_no_limit_param_is_ever_sent_on_paginated_reads():
    flicklist = make_flicklist([FakeResponse(json_data=[{"id": 1}], headers={"X-FlickList-Page-Count": "2"}), FakeResponse(json_data=[{"id": 2}])])
    flicklist._request_paginated("/lists/1/items")
    for _, _, params in flicklist.requests.gets:
        assert not params or "limit" not in params


@pytest.mark.parametrize(
    "value,expected",
    [
        (4821, 4821),
        ("4821", 4821),
        ("https://flicklist.tv/list/4821", 4821),
        ("https://flicklist.tv/list/4821/", 4821),
    ],
)
def test_parse_list_id_accepts_bare_id_and_url(value, expected):
    assert FlickList._parse_list_id(value) == expected


def test_parse_list_id_rejects_garbage():
    with pytest.raises(Failed, match="Could not parse a list id"):
        FlickList._parse_list_id("not-a-list")


def test_validate_lists_returns_ids_for_multiple_values():
    flicklist = make_flicklist([])
    assert flicklist.validate_lists("Collection", ["4821", "https://flicklist.tv/list/9310"]) == [4821, 9310]


def test_validate_lists_rejects_dict_entries():
    flicklist = make_flicklist([])
    with pytest.raises(Failed, match="cannot be a dictionary"):
        flicklist.validate_lists("Collection", [{"bad": True}])


def _movie(tmdb=None, tvdb=None, imdb=None, fldb=None, title="Movie", media_type="movie"):
    ids = {}
    if tmdb is not None:
        ids["tmdb"] = tmdb
    if tvdb is not None:
        ids["tvdb"] = tvdb
    if imdb is not None:
        ids["imdb"] = imdb
    if fldb is not None:
        ids["fldb"] = fldb
    return {"ids": ids, "media_type": media_type, "title": title}


def test_parse_ids_movie_with_tmdb():
    flicklist = make_flicklist([])
    assert flicklist._parse_ids([_movie(tmdb=550)]) == [(550, "tmdb")]


def test_parse_ids_show_with_tmdb():
    flicklist = make_flicklist([])
    assert flicklist._parse_ids([_movie(tmdb=1396, media_type="show")]) == [(1396, "tmdb_show")]


def test_parse_ids_show_with_tvdb_only():
    flicklist = make_flicklist([])
    assert flicklist._parse_ids([_movie(tvdb=81189, media_type="show")]) == [(81189, "tvdb")]


def test_parse_ids_imdb_only():
    flicklist = make_flicklist([])
    assert flicklist._parse_ids([_movie(imdb="tt0903747", media_type="show")]) == [("tt0903747", "imdb")]


def test_parse_ids_media_type_tv_and_show_both_resolve_to_show():
    flicklist = make_flicklist([])
    tv_item = _movie(tmdb=1396, media_type="tv")
    show_item = _movie(tmdb=1397, media_type="show")
    assert flicklist._parse_ids([tv_item, show_item]) == [(1396, "tmdb_show"), (1397, "tmdb_show")]


def test_parse_ids_no_usable_id_warns_and_skips():
    flicklist = make_flicklist([])
    assert flicklist._parse_ids([{"ids": {}, "media_type": "movie", "title": "Mystery Movie"}]) == []


def test_parse_ids_unknown_key_in_ids_block_is_ignored():
    flicklist = make_flicklist([])
    item = {"ids": {"tmdb": 550, "anilist": None, "some_future_key": "xyz"}, "media_type": "movie", "title": "Fight Club"}
    assert flicklist._parse_ids([item]) == [(550, "tmdb")]


def test_parse_ids_is_movie_true_filters_to_movies_only():
    flicklist = make_flicklist([])
    items = [_movie(tmdb=550, media_type="movie"), _movie(tmdb=1396, media_type="show")]
    assert flicklist._parse_ids(items, is_movie=True) == [(550, "tmdb")]


def test_parse_ids_is_movie_false_filters_to_shows_only():
    flicklist = make_flicklist([])
    items = [_movie(tmdb=550, media_type="movie"), _movie(tmdb=1396, media_type="show")]
    assert flicklist._parse_ids(items, is_movie=False) == [(1396, "tmdb_show")]


def test_parse_ids_is_movie_none_returns_both_movie_and_show_playlist_mode():
    flicklist = make_flicklist([])
    items = [_movie(tmdb=550, media_type="movie"), _movie(tmdb=1396, media_type="show")]
    assert flicklist._parse_ids(items, is_movie=None) == [(550, "tmdb"), (1396, "tmdb_show")]


def test_parse_ids_dedupes_on_fldb():
    flicklist = make_flicklist([])
    items = [_movie(tmdb=550, fldb="flt_abc"), _movie(tmdb=550, fldb="flt_abc")]
    assert flicklist._parse_ids(items) == [(550, "tmdb")]


def test_validate_flag_accepts_blank_as_true():
    flicklist = make_flicklist([])
    assert flicklist.validate_flag("Collection", "flicklist_watchlist", None) is True


def test_validate_flag_explicit_false_returns_false_without_raising():
    # false just means "don't add this builder" - same as omitting the attribute - not a config error.
    flicklist = make_flicklist([])
    assert flicklist.validate_flag("Collection", "flicklist_watchlist", False) is False


def test_validate_up_next_accepts_blank_true_and_int():
    assert FlickList.validate_up_next("Collection", None) is None
    assert FlickList.validate_up_next("Collection", True) is None
    assert FlickList.validate_up_next("Collection", 20) == 20


def test_validate_up_next_rejects_non_integer():
    with pytest.raises(Failed, match="blank, true, or an integer limit"):
        FlickList.validate_up_next("Collection", "soon")


def test_validate_ratings_accepts_blank_number_and_dict():
    assert FlickList.validate_ratings("Collection", None) == {"minimum": None, "maximum": None}
    assert FlickList.validate_ratings("Collection", 7) == {"minimum": 7.0, "maximum": None}
    assert FlickList.validate_ratings("Collection", {"minimum": 7, "maximum": 9}) == {"minimum": 7.0, "maximum": 9.0}


# --- flicklist_watched: WatchedMovie/WatchedShow carry no top-level media_type (WatchedShow also
# nests its `ids` under a `show` object), unlike every other personal endpoint this integration
# reads. _parse_ids classifies purely off `media_type`, so without normalizing these two shapes
# first, every watched item is silently dropped regardless of real watch history - these fixtures
# use the real nested/flat shapes from the live OpenAPI spec, not a flattened stand-in that would
# pass against both the buggy and fixed code. ---


def _watched_movie_payload(tmdb=550, title="Fight Club", plays=3):
    # Real WatchedMovie shape: top-level `ids`, no `media_type` key at all.
    return {"title": title, "year": 1999, "plays": plays, "last_watched_at": "2026-05-14T02:10:33.000Z", "ids": {"tmdb": tmdb}}


def _watched_show_payload(tmdb=1396, title="Breaking Bad", plays=62):
    # Real WatchedShow shape: no top-level `media_type` OR `ids` - both live under `show`.
    return {
        "show": {"title": title, "ids": {"tmdb": tmdb}},
        "plays": plays,
        "last_watched_at": "2026-05-14T02:10:33.000Z",
        "reset_at": None,
        "seasons": [],
    }


def test_normalize_watched_movie_tags_media_type_without_losing_ids():
    flicklist = make_flicklist([])
    normalized = flicklist._normalize_watched_movie(_watched_movie_payload(tmdb=550))
    assert normalized["media_type"] == "movie"
    assert normalized["ids"] == {"tmdb": 550}


def test_normalize_watched_show_unwraps_show_object_and_tags_media_type():
    flicklist = make_flicklist([])
    normalized = flicklist._normalize_watched_show(_watched_show_payload(tmdb=1396))
    assert normalized["media_type"] == "tv"
    assert normalized["ids"] == {"tmdb": 1396}


def test_normalize_watched_show_missing_show_key_does_not_raise():
    flicklist = make_flicklist([])
    normalized = flicklist._normalize_watched_show({"plays": 1, "seasons": []})
    assert normalized["media_type"] == "tv"
    assert normalized.get("ids") is None


def test_flicklist_watched_movie_library_returns_real_watched_movies():
    flicklist = make_flicklist([FakeResponse(json_data=[_watched_movie_payload(tmdb=550)])])
    assert flicklist.get_flicklist_ids("flicklist_watched", None, is_movie=True) == [(550, "tmdb")]


def test_flicklist_watched_show_library_returns_real_watched_shows():
    flicklist = make_flicklist([FakeResponse(json_data=[_watched_show_payload(tmdb=1396)])])
    assert flicklist.get_flicklist_ids("flicklist_watched", None, is_movie=False) == [(1396, "tmdb_show")]


def test_flicklist_watched_playlist_mode_returns_both_movies_and_shows():
    flicklist = make_flicklist(
        [
            FakeResponse(json_data=[_watched_movie_payload(tmdb=550)]),
            FakeResponse(json_data=[_watched_show_payload(tmdb=1396)]),
        ]
    )
    assert flicklist.get_flicklist_ids("flicklist_watched", None, is_movie=None) == [(550, "tmdb"), (1396, "tmdb_show")]
