from unittest.mock import MagicMock, patch

import pytest

from modules.listrr import Listrr
from modules.util import Failed

MOVIE_ID = "671527158e1c7df162d0fe69"
SHOW_ID = "67fb123c6f5a448f92e7ee03"
MOVIE_URL = f"https://listrr.pro/Lists/ShowMovieList/{MOVIE_ID}"
SHOW_URL = f"https://listrr.pro/Lists/ShowShowList/{SHOW_ID}"


class FakeResponse:
    def __init__(self, status_code=200, json_data=None, headers=None, text="", raise_on_json=False):
        self.status_code = status_code
        self._json_data = json_data if json_data is not None else {}
        self.headers = headers or {}
        self.text = text
        self.content = text.encode("utf-8") if text else b"{}"
        self.reason = "Error"
        self._raise_on_json = raise_on_json

    def json(self):
        if self._raise_on_json:
            raise ValueError("not JSON")
        return self._json_data


class FakeRequests:
    def __init__(self, responses):
        self._responses = list(responses)
        self.gets = []

    def get(self, url, headers=None):
        self.gets.append((url, headers))
        if not self._responses:
            raise AssertionError(f"unexpected GET {url}")
        return self._responses.pop(0)


def make_listrr(responses, api_key="test-key"):
    return Listrr(FakeRequests(responses), api_key)


def meta(list_type="Movie", state="Scheduled", description="A list", last_processed="2024-01-02T00:00:00Z", list_id=MOVIE_ID):
    return FakeResponse(
        json_data={
            "id": list_id,
            "name": "List",
            "description": description,
            "items": 2,
            "type": list_type,
            "state": state,
            "lastProcessed": last_processed,
        }
    )


def page(items, pages=1, count=None):
    return FakeResponse(json_data={"items": items, "pages": pages, "count": len(items) if count is None else count})


def movie(tmdb=0, imdb=None, name="Film", row_id="row"):
    return {"tmDbId": tmdb, "imDbId": imdb, "name": name, "id": row_id, "releaseDate": "2020-01-01"}


def show(tvdb=0, tmdb=0, imdb=None, name="Show", row_id="row"):
    return {"tvDbId": tvdb, "tmDbId": tmdb, "imDbId": imdb, "name": name, "id": row_id, "firstAirDate": "2020-01-01"}


def normalized(list_id=MOVIE_ID, sort_by="name.asc", limit=0):
    return {"list_id": list_id, "sort_by": sort_by, "limit": limit}


@pytest.mark.parametrize(
    "value,expected",
    [
        (MOVIE_ID, MOVIE_ID),
        (MOVIE_ID.upper(), MOVIE_ID),
        (MOVIE_URL, MOVIE_ID),
        (f"{MOVIE_URL}?page=4", MOVIE_ID),
        (f"{MOVIE_URL}/?page=2", MOVIE_ID),
        (SHOW_URL, SHOW_ID),
        (f"http://listrr.pro/Lists/ShowShowList/{SHOW_ID}?page=9", SHOW_ID),
    ],
)
def test_parse_list_id_accepts_bare_id_and_url_and_ignores_page(value, expected):
    assert Listrr._parse_list_id(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "not-a-list",
        "671527158e1c7df162d0fe6",
        "671527158e1c7df162d0fe6g",
        f"https://example.com/Lists/ShowMovieList/{MOVIE_ID}",
        f"https://listrr.pro/lists/{MOVIE_ID}",
        f"https://www.listrr.pro/Lists/ShowMovieList/{MOVIE_ID}",
    ],
)
def test_parse_list_id_rejects_bad_id_and_non_listrr_host(value):
    with pytest.raises(Failed, match="not a Listrr list id or URL|not a listrr.pro list URL"):
        Listrr._parse_list_id(value)


def test_validate_lists_defaults_and_aliases():
    client = make_listrr([])
    assert client.validate_lists("Collection", MOVIE_ID) == [normalized()]
    assert client.validate_lists("Collection", {"list_id": SHOW_URL}) == [normalized(SHOW_ID)]
    assert client.validate_lists("Collection", {"url": MOVIE_URL, "sort_by": "release.desc", "limit": 100}) == [normalized(sort_by="release.desc", limit=100)]
    assert client.validate_lists("Collection", [MOVIE_ID, SHOW_ID]) == [normalized(), normalized(SHOW_ID)]


def test_validate_lists_rejects_invalid_sort_and_limit():
    client = make_listrr([])
    with pytest.raises(Failed, match="sort_by must be one of"):
        client.validate_lists("Collection", {"url": MOVIE_ID, "sort_by": "rank.asc"})
    for limit in (-1, "10", True, 1.5):
        with pytest.raises(Failed, match="limit must be an integer 0 or greater"):
            client.validate_lists("Collection", {"url": MOVIE_ID, "limit": limit})


def test_validate_lists_does_not_comma_split_a_string():
    client = make_listrr([])
    with pytest.raises(Failed, match="not a Listrr list id or URL"):
        client.validate_lists("Collection", f"{MOVIE_ID},{SHOW_ID}")


def test_constructor_sends_apikey_authorization_header(patch_util_logger):
    client = make_listrr([FakeResponse(json_data={"items": [], "count": 0, "pages": 0})], api_key="super-secret")
    client.test_connection()
    url, headers = client.requests.gets[0]
    assert url == "https://listrr.pro/api/List/My/1"
    assert headers["Authorization"] == "APIKEY super-secret"
    assert "super-secret" in patch_util_logger.secrets


def test_ids_prefer_tmdb_for_movies_and_tvdb_for_shows(patch_util_logger):
    movie_row = movie(tmdb=550, imdb="tt0137523", name="Fight Club", row_id="m1")
    show_row = show(tvdb=81189, tmdb=1396, imdb="tt0903747", name="Breaking Bad", row_id="s1")
    movies = make_listrr([meta(), page([movie_row])])
    assert movies.get_listrr_ids("listrr_list", normalized(), True) == [(550, "tmdb")]
    shows = make_listrr([meta(list_type="Show", list_id=SHOW_ID), page([show_row])])
    assert shows.get_listrr_ids("listrr_list", normalized(SHOW_ID), False) == [(81189, "tvdb")]


def test_zero_ids_are_skipped_and_imdb_digits_gain_tt_prefix(patch_util_logger):
    rows = [
        movie(tmdb=0, imdb="1375666", name="Inception", row_id="m1"),
        movie(tmdb=0, imdb="tt0109830", name="Forrest Gump", row_id="m2"),
        movie(tmdb=0, imdb=None, name="No Ids", row_id="m3"),
        movie(tmdb=0, imdb="not-an-id", name="Bad Imdb", row_id="m4"),
    ]
    client = make_listrr([meta(), page(rows, count=4)])
    assert client.get_listrr_ids("listrr_list", normalized(), True) == [("tt1375666", "imdb"), ("tt0109830", "imdb")]
    warnings = " ".join(patch_util_logger.warning_messages)
    assert "No Ids" in warnings
    assert "Bad Imdb" in warnings
    assert "not-an-id" in warnings


def test_show_id_fallback_order(patch_util_logger):
    rows = [
        show(tvdb=0, tmdb=1399, name="TMDb Show", row_id="s1"),
        show(tvdb=0, tmdb=0, imdb="0944947", name="IMDb Show", row_id="s2"),
    ]
    client = make_listrr([meta(list_type="Show", list_id=SHOW_ID), page(rows)])
    assert client.get_listrr_ids("listrr_list", normalized(SHOW_ID), False) == [(1399, "tmdb_show"), ("tt0944947", "imdb")]


def test_paging_stops_at_pages_on_empty_page_and_at_limit(patch_util_logger):
    two_pages = make_listrr(
        [
            meta(),
            page([movie(tmdb=1, row_id="a")], pages=2, count=2),
            page([movie(tmdb=2, row_id="b")], pages=2, count=2),
        ]
    )
    assert two_pages.get_listrr_ids("listrr_list", normalized(), True) == [(1, "tmdb"), (2, "tmdb")]
    assert [url.rsplit("/", 1)[-1] for url, _ in two_pages.requests.gets[1:]] == ["1", "2"]
    assert any("2/2" in message for message in patch_util_logger.info_messages)

    empty_page = make_listrr(
        [
            meta(),
            page([movie(tmdb=1, row_id="a")], pages=5, count=5),
            page([], pages=5, count=5),
        ]
    )
    assert empty_page.get_listrr_ids("listrr_list", normalized(), True) == [(1, "tmdb")]
    assert len(empty_page.requests.gets) == 3

    limited = make_listrr(
        [
            meta(),
            page([movie(tmdb=1, row_id="a"), movie(tmdb=2, row_id="b")], pages=3, count=6),
            page([movie(tmdb=3, row_id="c")], pages=3, count=6),
        ]
    )
    assert limited.get_listrr_ids("listrr_list", normalized(limit=1), True) == [(1, "tmdb")]
    assert len(limited.requests.gets) == 2


def test_missing_pages_after_first_page_stops(patch_util_logger):
    client = make_listrr([meta(), FakeResponse(json_data={"items": [movie(tmdb=1, row_id="a")], "count": 1})])
    assert client.get_listrr_ids("listrr_list", normalized(), True) == [(1, "tmdb")]
    assert len(client.requests.gets) == 2


def test_limit_counts_emitted_ids_not_skipped_rows(patch_util_logger):
    rows = [movie(tmdb=0, imdb=None, name="Skip", row_id="a"), movie(tmdb=8, name="Keep", row_id="b"), movie(tmdb=9, name="Extra", row_id="c")]
    client = make_listrr([meta(), page(rows, count=3)])
    assert client.get_listrr_ids("listrr_list", normalized(limit=1), True) == [(8, "tmdb")]


def test_duplicate_listrr_id_is_emitted_once(patch_util_logger):
    rows = [movie(tmdb=1, row_id="same"), movie(tmdb=2, row_id="same")]
    client = make_listrr([meta(), page(rows)])
    assert client.get_listrr_ids("listrr_list", normalized(), True) == [(1, "tmdb")]


def test_sort_by_is_placed_in_the_items_path(patch_util_logger):
    client = make_listrr([meta(), page([movie(tmdb=1)])])
    client.get_listrr_ids("listrr_list", normalized(sort_by="release.desc"), True)
    assert client.requests.gets[1][0] == f"https://listrr.pro/api/List/Movies/{MOVIE_ID}/ReleaseDate/Descending/1"


def test_movie_list_on_a_show_library_does_not_call_the_items_route(patch_util_logger):
    client = make_listrr([meta(list_type="Movie")])
    with pytest.raises(Failed, match="Movie list"):
        client.get_listrr_ids("listrr_list", normalized(), False)
    assert len(client.requests.gets) == 1
    assert "/Movies/" not in client.requests.gets[0][0]
    assert "/Shows/" not in client.requests.gets[0][0]


def test_playlist_accepts_either_list_type(patch_util_logger):
    movies = make_listrr([meta(list_type="Movie"), page([movie(tmdb=5, imdb="tt1", row_id="m")])])
    assert movies.get_listrr_ids("listrr_list", normalized(), None) == [(5, "tmdb")]
    shows = make_listrr([meta(list_type="Show", list_id=SHOW_ID), page([show(tvdb=9, row_id="s")])])
    assert shows.get_listrr_ids("listrr_list", normalized(SHOW_ID), None) == [(9, "tvdb")]


def test_error_state_warns_with_last_processed_and_still_returns_items(patch_util_logger):
    client = make_listrr([meta(state="SchduledForDeletion", last_processed="2024-05-01T00:00:00Z"), page([movie(tmdb=5)])])
    assert client.get_listrr_ids("listrr_list", normalized(), True) == [(5, "tmdb")]
    warning = " ".join(patch_util_logger.warning_messages)
    assert "SchduledForDeletion" in warning
    assert "2024-05-01T00:00:00Z" in warning


def test_updating_state_logs_info_and_returns_items(patch_util_logger):
    client = make_listrr([meta(state="Updating"), page([movie(tmdb=5)])])
    assert client.get_listrr_ids("listrr_list", normalized(), True) == [(5, "tmdb")]
    assert any("Updating" in message for message in patch_util_logger.info_messages)


@pytest.mark.parametrize(
    "response,match",
    [
        (FakeResponse(status_code=404, text="missing"), "could not be found"),
        (FakeResponse(status_code=400, text="wrong type"), "type does not match"),
        (FakeResponse(status_code=302, headers={"Location": "https://listrr.pro/Identity/Account/Login"}, text="login"), "API key was rejected"),
        (FakeResponse(status_code=401, text="nope"), "API key was rejected"),
        (FakeResponse(status_code=500, text="boom " * 80, raise_on_json=True), r"\(500\)"),
    ],
)
def test_status_codes_become_failed(response, match):
    client = make_listrr([response])
    with pytest.raises(Failed, match=match):
        client._request("https://listrr.pro/api/List/My/1")


def test_list_description_uses_metadata_and_blank_is_empty():
    described = make_listrr([FakeResponse(json_data={"description": "From Listrr"})])
    assert described.list_description(MOVIE_ID) == "From Listrr"
    blank = make_listrr([FakeResponse(json_data={"description": ""})])
    assert blank.list_description(MOVIE_ID) == ""
    missing = make_listrr([FakeResponse(json_data={})])
    assert missing.list_description(MOVIE_ID) == ""


@patch("modules.listrr.time.sleep", return_value=None)
def test_429_honors_retry_after(mock_sleep):
    client = make_listrr(
        [
            FakeResponse(status_code=429, headers={"Retry-After": "5"}, text="slow"),
            FakeResponse(json_data={"items": [], "count": 0, "pages": 0}),
        ]
    )
    client.test_connection()
    mock_sleep.assert_called_once_with(5.0)


@patch("modules.listrr.time.sleep", return_value=None)
def test_429_gives_up_after_three_attempts(mock_sleep):
    client = make_listrr([FakeResponse(status_code=429, headers={"Retry-After": "1"}, text="slow") for _ in range(3)])
    with pytest.raises(Failed, match="after 3 attempts"):
        client.test_connection()
    assert len(client.requests.gets) == 3
    assert mock_sleep.call_count == 2


@patch("modules.listrr.time.sleep", return_value=None)
def test_429_over_cap_does_not_sleep(mock_sleep):
    client = make_listrr([FakeResponse(status_code=429, headers={"Retry-After": "121"}, text="slow")])
    with pytest.raises(Failed, match="120"):
        client.test_connection()
    mock_sleep.assert_not_called()


@patch("modules.listrr.time.sleep", return_value=None)
def test_successful_pages_do_not_sleep(mock_sleep, patch_util_logger):
    client = make_listrr([meta(), page([movie(tmdb=1)], pages=2), page([movie(tmdb=2)], pages=2)])
    client.get_listrr_ids("listrr_list", normalized(), True)
    mock_sleep.assert_not_called()


SECOND_ID = "aaaaaaaaaaaaaaaaaaaaaaaa"


def test_multiple_lists_keep_each_sort_and_drop_ids_already_emitted(patch_util_logger):
    client = make_listrr(
        [
            meta(),
            page([movie(tmdb=1, row_id="a"), movie(tmdb=2, row_id="b")]),
            meta(list_id=SECOND_ID),
            page([movie(tmdb=2, row_id="other"), movie(tmdb=3, row_id="c")]),
        ]
    )
    lists = [normalized(), normalized(SECOND_ID, sort_by="release.desc")]
    assert client.get_listrr_ids("listrr_list", lists, True) == [(1, "tmdb"), (2, "tmdb"), (3, "tmdb")]
    urls = [url for url, _headers in client.requests.gets]
    assert urls[1] == f"https://listrr.pro/api/List/Movies/{MOVIE_ID}/Name/Ascending/1"
    assert urls[3] == f"https://listrr.pro/api/List/Movies/{SECOND_ID}/ReleaseDate/Descending/1"


def test_limit_applies_to_each_list(patch_util_logger):
    client = make_listrr(
        [
            meta(),
            page([movie(tmdb=1, row_id="a"), movie(tmdb=2, row_id="b")], count=2),
            meta(list_id=SECOND_ID),
            page([movie(tmdb=3, row_id="c")]),
        ]
    )
    lists = [normalized(limit=1), normalized(SECOND_ID)]
    assert client.get_listrr_ids("listrr_list", lists, True) == [(1, "tmdb"), (3, "tmdb")]


def test_playlist_concatenates_movie_and_show_lists(patch_util_logger):
    client = make_listrr(
        [
            meta(),
            page([movie(tmdb=5, row_id="m")]),
            meta(list_type="Show", list_id=SHOW_ID),
            page([show(tvdb=9, row_id="s")]),
        ]
    )
    assert client.get_listrr_ids("listrr_list", [normalized(), normalized(SHOW_ID)], None) == [(5, "tmdb"), (9, "tvdb")]


def test_show_list_on_a_movie_library_still_fails_when_lists_are_combined(patch_util_logger):
    client = make_listrr([meta(), page([movie(tmdb=5, row_id="m")]), meta(list_type="Show", list_id=SHOW_ID)])
    with pytest.raises(Failed, match="Show list"):
        client.get_listrr_ids("listrr_list", [normalized(), normalized(SHOW_ID)], True)
    assert "/Shows/" not in client.requests.gets[-1][0]


def test_retry_error_and_connection_error_become_failed():
    from concurrent.futures import Future

    from requests.exceptions import ConnectionError
    from tenacity import RetryError

    future = Future()
    future.set_exception(ConnectionError("timed out"))

    class PlainGet:
        def get(self, url, headers=None):
            raise RetryError(future)

    retry_client = Listrr(PlainGet(), "test-key")
    with pytest.raises(Failed, match="Request failed") as retry_exc:
        retry_client.test_connection()
    assert not str(retry_exc.value).endswith("is blank")

    class Disconnect:
        def get(self, url, headers=None):
            raise ConnectionError("timed out")

    with pytest.raises(Failed, match="Request failed") as connection_exc:
        Listrr(Disconnect(), "test-key").test_connection()
    assert not str(connection_exc.value).endswith("is blank")


@patch("modules.listrr.time.sleep", return_value=None)
def test_shared_requests_returns_oversized_retry_after_without_retrying(mock_sleep, monkeypatch):
    from tenacity import wait_none

    from modules.request import DEFAULT_TIMEOUT, Requests

    req = Requests.__new__(Requests)
    limited = MagicMock(status_code=429, reason="Too Many Requests", headers={"Retry-After": "121"}, text="slow", content=b"slow")
    req.session = MagicMock()
    req.session.get.return_value = limited
    monkeypatch.setattr(Requests.get.retry, "wait", wait_none())

    with pytest.raises(Failed, match="120"):
        Listrr(req, "test-key").test_connection()
    req.session.get.assert_called_once()
    assert req.session.get.call_args.kwargs["timeout"] == DEFAULT_TIMEOUT
    assert req.session.get.call_args.kwargs["headers"]["Authorization"] == "APIKEY test-key"
    mock_sleep.assert_not_called()


@patch("modules.listrr.time.sleep", return_value=None)
def test_shared_requests_429_then_success_uses_the_local_loop(mock_sleep, monkeypatch):
    from tenacity import wait_none

    from modules.request import Requests

    req = Requests.__new__(Requests)
    limited = MagicMock(status_code=429, headers={"Retry-After": "2"}, text="slow", content=b"slow")
    success = MagicMock(status_code=200, headers={})
    success.json.return_value = {"items": [], "count": 0, "pages": 0}
    req.session = MagicMock()
    req.session.get.side_effect = [limited, success]
    monkeypatch.setattr(Requests.get.retry, "wait", wait_none())

    Listrr(req, "test-key").test_connection()
    assert req.session.get.call_count == 2
    mock_sleep.assert_called_once_with(2.0)
