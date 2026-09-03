"""Tests for modules/imdb.py -- focused on parental_guide edge cases."""

from unittest.mock import MagicMock

import pytest
from requests.exceptions import JSONDecodeError

from modules.imdb import IMDb, graphql_url
from modules.util import Failed


def make_imdb(graph_response, service_response=None):
    """Return a minimal IMDb instance with _graph_request mocked to return graph_response.

    By default the service response is empty so existing tests exercise the GraphQL fallback.
    """
    imdb = IMDb(requests=MagicMock(), cache=None, default_dir="/tmp")
    imdb._graph_request = MagicMock(return_value=graph_response)
    imdb._service_request = MagicMock(return_value=service_response)
    return imdb


# ---------------------------------------------------------------------------
# IMDb GraphQL request handling
# ---------------------------------------------------------------------------


class TestGraphRequest:

    def test_sends_imdb_web_client_header(self):
        requests = MagicMock()
        response = MagicMock(status_code=200)
        response.json.return_value = {"data": {"result": "ok"}}
        requests.post.return_value = response
        imdb = IMDb(requests=requests, cache=None, default_dir="/tmp")
        payload = {"query": "{ result }"}

        assert imdb._graph_request(payload) == {"data": {"result": "ok"}}
        requests.post.assert_called_once_with(
            graphql_url,
            headers={
                "content-type": "application/json",
                "x-imdb-client-name": "imdb-web-next",
            },
            json=payload,
        )

    def test_http_error_raises_contextual_imdb_error(self):
        requests = MagicMock()
        response = MagicMock(status_code=403)
        requests.post.return_value = response
        imdb = IMDb(requests=requests, cache=None, default_dir="/tmp")

        with pytest.raises(Failed, match="IMDb Error: GraphQL request failed with HTTP 403"):
            imdb._graph_request({"query": "{ result }"})

        response.json.assert_not_called()

    def test_non_json_response_raises_contextual_imdb_error(self):
        requests = MagicMock()
        response = MagicMock(status_code=200)
        response.json.side_effect = JSONDecodeError("Expecting value", "<html>", 0)
        requests.post.return_value = response
        imdb = IMDb(requests=requests, cache=None, default_dir="/tmp")

        with pytest.raises(Failed, match="IMDb Error: GraphQL request returned a non-JSON response"):
            imdb._graph_request({"query": "{ result }"})


# ---------------------------------------------------------------------------
# Regression: demonstrate the bugs that existed before the fix
# ---------------------------------------------------------------------------


def test_parental_guide_none_response_pre_fix_raises_attribute_error():
    """Phase 1 regression: .get() on None raised AttributeError before the fix.

    The original broken line was:
        (self._graph_request(...).get("data") or {})...
    which explodes when _graph_request returns None.
    """
    result = None
    with pytest.raises(AttributeError):
        (result.get("data") or {}).get("title", {})


def test_parental_guide_null_title_pre_fix_raises_attribute_error():
    """Phase 2 regression: .get("title", {}) returns None when title key exists
    but its value is null -- causing AttributeError on the next .get() call.

    IMDb returns {"data": {"title": null}} for IDs that do not exist in their DB
    (e.g. an item whose only Plex GUIDs are tmdb:// or tvdb://).
    """
    response = {"data": {"title": None}}
    with pytest.raises(AttributeError):
        (response.get("data") or {}).get("title", {}).get("parentsGuide", {})


# ---------------------------------------------------------------------------
# Fix: _graph_request returns None (network/auth failure or empty response)
# ---------------------------------------------------------------------------


def test_parental_guide_none_response_raises_failed():
    """When _graph_request returns None, parental_guide raises Failed (not AttributeError)
    so operations.py can catch it and skip the item gracefully."""
    imdb = make_imdb(graph_response=None)
    with pytest.raises(Failed, match="No Parental Guide Found"):
        imdb.parental_guide("tt9999999")


def test_parental_guide_none_response_does_not_raise_attribute_error():
    """The fix must not let AttributeError escape when _graph_request returns None."""
    imdb = make_imdb(graph_response=None)
    with pytest.raises(Exception) as exc_info:
        imdb.parental_guide("tt9999999")
    assert not isinstance(exc_info.value, AttributeError), "AttributeError escaped -- the None guard is missing"


# ---------------------------------------------------------------------------
# Fix: IMDb returns {"data": {"title": null}} for unknown IDs
# ---------------------------------------------------------------------------


def test_parental_guide_null_title_raises_failed():
    """When IMDb returns null for the title (ID not in their DB), parental_guide
    raises Failed so operations.py skips the item gracefully."""
    imdb = make_imdb(graph_response={"data": {"title": None}})
    with pytest.raises(Failed, match="No Parental Guide Found"):
        imdb.parental_guide("tt9999999")


def test_parental_guide_null_title_does_not_raise_attribute_error():
    """The fix must not let AttributeError escape for a null title response."""
    imdb = make_imdb(graph_response={"data": {"title": None}})
    with pytest.raises(Exception) as exc_info:
        imdb.parental_guide("tt9999999")
    assert not isinstance(exc_info.value, AttributeError), "AttributeError escaped -- the null title guard is missing"


# ---------------------------------------------------------------------------
# Fix: IMDb returns {"data": {"title": {"parentsGuide": null}}}
# ---------------------------------------------------------------------------


def test_parental_guide_null_parents_guide_raises_failed():
    """When the title exists but parentsGuide is null, parental_guide raises Failed."""
    imdb = make_imdb(graph_response={"data": {"title": {"parentsGuide": None}}})
    with pytest.raises(Failed, match="No Parental Guide Found"):
        imdb.parental_guide("tt9999999")


def test_parental_guide_null_parents_guide_does_not_raise_attribute_error():
    """The fix must not let AttributeError escape for a null parentsGuide response."""
    imdb = make_imdb(graph_response={"data": {"title": {"parentsGuide": None}}})
    with pytest.raises(Exception) as exc_info:
        imdb.parental_guide("tt9999999")
    assert not isinstance(exc_info.value, AttributeError), "AttributeError escaped -- the null parentsGuide guard is missing"


# ---------------------------------------------------------------------------
# Happy path: valid response with parental guide data
# ---------------------------------------------------------------------------


def test_parental_guide_valid_response():
    """A well-formed GraphQL response returns the expected parental dict."""
    graph_response = {
        "data": {
            "title": {
                "parentsGuide": {
                    "categories": [
                        {"category": {"text": "Violence & Gore"}, "severity": {"text": "Moderate"}},
                        {"category": {"text": "Profanity"}, "severity": {"text": "Mild"}},
                    ]
                }
            }
        }
    }
    imdb = make_imdb(graph_response=graph_response)
    result = imdb.parental_guide("tt1234567")
    assert result.get("Violence") == "Moderate"
    assert result.get("Profanity") == "Mild"


# ---------------------------------------------------------------------------
# Edge case: empty categories list
# ---------------------------------------------------------------------------


def test_parental_guide_empty_categories_raises_failed():
    """An empty categories list (title exists but no guide data) raises Failed."""
    graph_response = {"data": {"title": {"parentsGuide": {"categories": []}}}}
    imdb = make_imdb(graph_response=graph_response)
    with pytest.raises(Failed, match="No Parental Guide Found"):
        imdb.parental_guide("tt0000000")


# ---------------------------------------------------------------------------
# Service-backed parental guide
# ---------------------------------------------------------------------------


def test_parental_guide_prefers_service():
    """When the Kometa IMDb Service returns parental guide data, use it."""
    service_response = {
        "imdb_id": "tt1234567",
        "parental_guide": {
            "Nudity": "Mild",
            "Violence": "Moderate",
            "Profanity": "Severe",
            "Alcohol": "Mild",
            "Frightening": "Moderate",
        },
    }
    imdb = make_imdb(graph_response={"data": {"title": {"parentsGuide": {"categories": []}}}}, service_response=service_response)
    result = imdb.parental_guide("tt1234567")
    assert result.get("Nudity") == "Mild"
    assert result.get("Violence") == "Moderate"
    assert result.get("Profanity") == "Severe"
    assert result.get("Alcohol") == "Mild"
    assert result.get("Frightening") == "Moderate"
    imdb._graph_request.assert_not_called()


def test_parental_guide_fills_missing_service_categories_with_none():
    """The service only returns categories that have values; missing ones are filled with None."""
    service_response = {"imdb_id": "tt1234567", "parental_guide": {"Violence": "Severe"}}
    imdb = make_imdb(graph_response=None, service_response=service_response)
    result = imdb.parental_guide("tt1234567")
    assert result.get("Violence") == "Severe"
    assert result.get("Nudity") is None
    assert result.get("Profanity") is None
    assert result.get("Alcohol") is None
    assert result.get("Frightening") is None


def test_parental_guide_falls_back_to_graphql_when_service_empty():
    """When the service returns no parental guide data, fall back to GraphQL."""
    graph_response = {"data": {"title": {"parentsGuide": {"categories": [{"category": {"text": "Violence & Gore"}, "severity": {"text": "Moderate"}}]}}}}
    imdb = make_imdb(graph_response=graph_response, service_response={"imdb_id": "tt1234567", "parental_guide": {}})
    result = imdb.parental_guide("tt1234567")
    assert result.get("Violence") == "Moderate"
    imdb._graph_request.assert_called_once()


def test_parental_guide_falls_back_to_graphql_when_service_unavailable():
    """When the service raises Failed, fall back to GraphQL."""
    graph_response = {"data": {"title": {"parentsGuide": {"categories": [{"category": {"text": "Profanity"}, "severity": {"text": "Mild"}}]}}}}
    imdb = make_imdb(graph_response=graph_response)
    imdb._service_request = MagicMock(side_effect=Failed("IMDb Service Error: 503"))
    result = imdb.parental_guide("tt1234567")
    assert result.get("Profanity") == "Mild"
    assert imdb._service_available is False


# ---------------------------------------------------------------------------
# validate_imdb: imdb_watchlist user ID format support (#3091)
#
# IMDb stopped showing ur######## IDs in their UI. Users now see p.xxxxxxx
# in watchlist URLs. These tests cover both formats as bare IDs and full URLs.
# ---------------------------------------------------------------------------


class TestValidateImdbWatchlist:

    def _imdb(self):
        return make_imdb(graph_response={})

    # --- ur######## (classic numeric format) ---

    def test_ur_bare_id_accepted(self):
        """Classic ur######## bare ID is still valid."""
        result = self._imdb().validate_imdb("Test", "imdb_watchlist", "ur64054558")
        assert result[0]["user_id"] == "ur64054558"

    def test_ur_full_url_extracted(self):
        """Full watchlist URL containing a ur######## ID is parsed correctly."""
        result = self._imdb().validate_imdb("Test", "imdb_watchlist", "https://www.imdb.com/user/ur64054558/watchlist")
        assert result[0]["user_id"] == "ur64054558"

    # --- p.xxxxxxx (new format) ---

    def test_p_hashed_bare_id_accepted(self):
        """Hashed p.xxxxxxx ID (most accounts) is accepted."""
        result = self._imdb().validate_imdb("Test", "imdb_watchlist", "p.fl6ssgsolkgcctcuxapgh6chsa")
        assert result[0]["user_id"] == "p.fl6ssgsolkgcctcuxapgh6chsa"

    def test_p_readable_bare_id_accepted(self):
        """Human-readable p.<name> ID (older accounts) is accepted."""
        result = self._imdb().validate_imdb("Test", "imdb_watchlist", "p.colneedham")
        assert result[0]["user_id"] == "p.colneedham"

    def test_p_hashed_full_url_extracted(self):
        """Full watchlist URL with hashed p.xxxxxxx ID is parsed correctly."""
        result = self._imdb().validate_imdb("Test", "imdb_watchlist", "https://www.imdb.com/user/p.fl6ssgsolkgcctcuxapgh6chsa/watchlist")
        assert result[0]["user_id"] == "p.fl6ssgsolkgcctcuxapgh6chsa"

    def test_p_readable_full_url_extracted(self):
        """Full watchlist URL with readable p.<name> ID is parsed correctly."""
        result = self._imdb().validate_imdb("Test", "imdb_watchlist", "https://www.imdb.com/user/p.colneedham/watchlist")
        assert result[0]["user_id"] == "p.colneedham"

    # --- invalid input ---

    def test_invalid_format_raises_failed(self):
        """Unrecognised format raises Failed mentioning both valid formats."""
        with pytest.raises(Failed, match="ur########"):
            self._imdb().validate_imdb("Test", "imdb_watchlist", "abc12345")

    def test_ur_non_numeric_suffix_raises_failed(self):
        """ur prefix without a numeric suffix is rejected."""
        with pytest.raises(Failed, match="ur########"):
            self._imdb().validate_imdb("Test", "imdb_watchlist", "urnothex")

    # --- non-string inputs (regression: str-coercion on .strip()) ---

    def test_numeric_user_id_in_dict_doesnt_crash_with_attribute_error(self):
        """YAML can deserialize a bare numeric id as int. The validator used to crash with
        `AttributeError: 'int' object has no attribute 'strip'` before main_data was
        wrapped in `str(...)`. The numeric id is invalid (no ur/p. prefix) so a clean
        Failed is the expected outcome — the point is that we don't `AttributeError`.
        """
        with pytest.raises(Failed, match="ur########"):
            self._imdb().validate_imdb("Test", "imdb_watchlist", [{"user_id": 64054558}])

    def test_numeric_id_wrapped_in_ur_string_via_stringification(self):
        """When the user provides a dict with a string ur######## id, the str() coercion
        is a no-op and the value passes through unchanged.
        """
        result = self._imdb().validate_imdb("Test", "imdb_watchlist", [{"user_id": "ur64054558"}])
        assert result[0]["user_id"] == "ur64054558"


# ---------------------------------------------------------------------------
# Service-backed rating / genre / episode-rating lookups
# ---------------------------------------------------------------------------


def make_imdb_service(service_responses, raise_failed=None, graph_response=None):
    """Return an IMDb instance with _service_request mocked to return responses
    looked up by endpoint path (e.g. 'title/tt0111161').

    Args:
        service_responses: dict mapping endpoint path to JSON response.
        raise_failed: optional endpoint path that will raise Failed when requested.
        graph_response: optional response for _graph_request.
    """
    imdb = IMDb(requests=MagicMock(), cache=None, default_dir="/tmp")

    def _fake_service_request(endpoint, not_found_ok=False):
        if raise_failed and endpoint == raise_failed:
            raise Failed("IMDb Service Error: 503")
        return service_responses.get(endpoint, {})

    imdb._service_request = MagicMock(side_effect=_fake_service_request)
    imdb._graph_request = MagicMock(return_value=graph_response)
    return imdb


def test_get_rating_returns_average_rating():
    imdb = make_imdb_service({"title/tt0111161": {"averageRating": 9.3, "genres": "Drama"}})
    assert imdb.get_rating("tt0111161") == 9.3


def test_get_rating_blank_id_returns_none():
    imdb = make_imdb_service({})
    assert imdb.get_rating("") is None
    assert imdb.get_rating(None) is None


def test_get_rating_falls_back_to_tsv_on_service_failure():
    imdb = make_imdb_service({}, raise_failed="title/tt0111161")
    imdb._ratings = {"tt0111161": "8.7"}
    assert imdb.get_rating("tt0111161") == "8.7"
    assert imdb._service_available is False


def test_get_rating_service_failure_uses_tsv_for_later_calls():
    imdb = make_imdb_service({}, raise_failed="title/tt0111161")
    imdb._ratings = {"tt0111161": "8.7", "tt0068646": "9.2"}
    imdb.get_rating("tt0111161")
    # After first failure, service flag is False; second call should skip service entirely.
    assert imdb.get_rating("tt0068646") == "9.2"
    assert imdb._service_request.call_count == 1


def test_get_genres_splits_comma_string():
    imdb = make_imdb_service({"title/tt0111161": {"averageRating": 9.3, "genres": "Drama,Crime"}})
    assert imdb.get_genres("tt0111161") == ["Drama", "Crime"]


def test_get_genres_blank_id_returns_empty_list():
    imdb = make_imdb_service({})
    assert imdb.get_genres("") == []
    assert imdb.get_genres(None) == []


def test_get_genres_missing_genres_returns_empty_list():
    imdb = make_imdb_service({"title/tt0111161": {"averageRating": 9.3}})
    assert imdb.get_genres("tt0111161") == []


def test_get_genres_falls_back_to_tsv_on_service_failure():
    imdb = make_imdb_service({}, raise_failed="title/tt0111161")
    imdb._genres = {"tt0111161": ["Drama", "Crime"]}
    assert imdb.get_genres("tt0111161") == ["Drama", "Crime"]
    assert imdb._service_available is False


def test_get_episode_rating_returns_rating():
    imdb = make_imdb_service(
        {
            "episode-ratings/tt0096697": {
                "parentTconst": "tt0096697",
                "total_episodes": 760,
                "seasons": {"5": {"12": {"tconst": "tt0701055", "averageRating": 8.1, "numVotes": 3826}}},
            }
        }
    )
    assert imdb.get_episode_rating("tt0096697", 5, 12) == 8.1


def test_get_episode_rating_caches_batch_result():
    imdb = make_imdb_service(
        {
            "episode-ratings/tt0096697": {
                "parentTconst": "tt0096697",
                "total_episodes": 760,
                "seasons": {
                    "5": {
                        "12": {"tconst": "tt0701055", "averageRating": 8.1, "numVotes": 3826},
                        "13": {"tconst": "tt0701173", "averageRating": 9.1, "numVotes": 6598},
                    }
                },
            }
        }
    )
    imdb.get_episode_rating("tt0096697", 5, 12)
    imdb.get_episode_rating("tt0096697", 5, 13)
    imdb._service_request.assert_called_once_with("episode-ratings/tt0096697", not_found_ok=True)


def test_get_episode_rating_missing_show_returns_none():
    imdb = make_imdb_service({"episode-ratings/tt0000000": None})
    assert imdb.get_episode_rating("tt0000000", 1, 1) is None


def test_get_episode_rating_missing_episode_returns_none():
    imdb = make_imdb_service(
        {
            "episode-ratings/tt0096697": {
                "parentTconst": "tt0096697",
                "total_episodes": 760,
                "seasons": {"5": {"12": {"tconst": "tt0701055", "averageRating": 8.1, "numVotes": 3826}}},
            }
        }
    )
    assert imdb.get_episode_rating("tt0096697", 99, 99) is None


def test_get_episode_rating_blank_id_returns_none():
    imdb = make_imdb_service({})
    assert imdb.get_episode_rating("", 1, 1) is None
    assert imdb.get_episode_rating(None, 1, 1) is None


def test_get_episode_rating_falls_back_to_tsv_on_service_failure():
    imdb = make_imdb_service({}, raise_failed="episode-ratings/tt0096697")
    imdb._episode_ratings = {"tt0096697": {"5": {"12": "8.1"}}}
    assert imdb.get_episode_rating("tt0096697", 5, 12) == "8.1"
    assert imdb._service_available is False


def test_get_rating_falls_back_on_non_http_failure():
    """Non-HTTP failures (connection errors, timeouts) should also trigger TSV fallback."""
    imdb = IMDb(requests=MagicMock(), cache=None, default_dir="/tmp")
    imdb.requests.get.side_effect = ConnectionError("Connection refused")
    imdb._ratings = {"tt0111161": "8.7"}
    assert imdb.get_rating("tt0111161") == "8.7"
    assert imdb._service_available is False


def test_get_genres_falls_back_on_invalid_json():
    """An invalid JSON response should be treated as a service outage and fall back."""
    imdb = IMDb(requests=MagicMock(), cache=None, default_dir="/tmp")
    response = MagicMock()
    response.status_code = 200
    response.content = b"not json"
    response.json.side_effect = ValueError("No JSON")
    imdb.requests.get.return_value = response
    imdb._genres = {"tt0111161": ["Drama"]}
    assert imdb.get_genres("tt0111161") == ["Drama"]
    assert imdb._service_available is False


# ---------------------------------------------------------------------------
# Service-backed chart lookups
# ---------------------------------------------------------------------------


def test_ids_from_chart_prefers_service():
    """When the service returns chart data, use it and skip GraphQL/scraping."""
    imdb = make_imdb_service(
        {
            "chart/top_movies": {
                "chart": "top_movies",
                "results": [
                    {"tconst": "tt0111161", "rank": 1},
                    {"tconst": "tt0068646", "rank": 2},
                ],
            }
        }
    )
    ids = imdb._ids_from_chart("top_movies", "en")
    assert ids == ["tt0111161", "tt0068646"]
    imdb._graph_request.assert_not_called()


def test_ids_from_chart_falls_back_to_graphql_on_service_failure():
    """When the service fails, fall back to the GraphQL chart query."""
    graph_response = {
        "data": {
            "chartTitles": {
                "edges": [
                    {"node": {"id": "tt0111161"}},
                    {"node": {"id": "tt0068646"}},
                ]
            }
        }
    }
    imdb = make_imdb_service({}, raise_failed="chart/top_movies", graph_response=graph_response)
    ids = imdb._ids_from_chart("top_movies", "en")
    assert ids == ["tt0111161", "tt0068646"]
    assert imdb._service_available is False


def test_ids_from_chart_falls_back_to_scraping_when_service_and_graphql_fail():
    """When both service and GraphQL fail, fall back to HTML scraping."""
    imdb = make_imdb_service({}, raise_failed="chart/top_movies")
    html_response = MagicMock()
    html_response.xpath.return_value = ['{"props":{"pageProps":{"chartModel":{"chartItems":[{"titleItemId":"tt0111161"},{"titleItemId":"tt0068646"}]}}}}']
    imdb.requests.get_cloudscrape_html.return_value = html_response
    ids = imdb._ids_from_chart("top_movies", "en")
    assert "tt0111161" in ids
    assert "tt0068646" in ids


# ---------------------------------------------------------------------------
# Service-backed keyword lookups
# ---------------------------------------------------------------------------


def test_keywords_prefers_service():
    """When the service returns keywords, use them and skip scraping."""
    imdb = make_imdb_service(
        {
            "keywords/tt0111161": {
                "imdb_id": "tt0111161",
                "keywords": {
                    "prison": [31, 32],
                    "escape from prison": [22, 23],
                },
            }
        }
    )
    imdb._scrape_keywords = MagicMock(return_value={"should": (0, 0), "not": (0, 0), "call": (0, 0)})
    result = imdb.keywords("tt0111161", "en")
    assert result.get("prison") == (31, 32)
    assert result.get("escape from prison") == (22, 23)
    imdb._scrape_keywords.assert_not_called()


def test_keywords_falls_back_to_scraping_when_service_empty():
    """When the service returns no keywords, fall back to scraping."""
    imdb = make_imdb_service({"keywords/tt0111161": {"imdb_id": "tt0111161", "keywords": {}}})
    imdb._scrape_keywords = MagicMock(return_value={"scraped": (5, 10)})
    result = imdb.keywords("tt0111161", "en")
    assert result.get("scraped") == (5, 10)
    imdb._scrape_keywords.assert_called_once_with("tt0111161", "en")


def test_keywords_falls_back_to_scraping_when_service_fails():
    """When the service fails, fall back to scraping and mark service unavailable."""
    imdb = make_imdb_service({}, raise_failed="keywords/tt0111161")
    imdb._scrape_keywords = MagicMock(return_value={"scraped": (3, 7)})
    result = imdb.keywords("tt0111161", "en")
    assert result.get("scraped") == (3, 7)
    assert imdb._service_available is False
    imdb._scrape_keywords.assert_called_once_with("tt0111161", "en")


class TestIdsFromChart:

    @pytest.fixture(autouse=True)
    def _mock_logger(self, monkeypatch):
        monkeypatch.setattr("modules.imdb.logger", MagicMock())

    def _imdb(self):
        return IMDb(requests=MagicMock(), cache=None, default_dir="/tmp")

    def test_graphql_success_does_not_use_html_fallback(self):
        imdb = self._imdb()
        imdb._chart_graphql = MagicMock(return_value=["tt0111161", "tt0068646"])
        imdb._request = MagicMock()

        assert imdb._ids_from_chart("top_movies", "en") == ["tt0111161", "tt0068646"]
        imdb._request.assert_not_called()

    def test_html_fallback_returns_ids_after_graphql_failure(self):
        imdb = self._imdb()
        imdb._chart_graphql = MagicMock(side_effect=Failed("GraphQL unavailable"))
        imdb._request = MagicMock(return_value=['{"id":"tt0111161"},{"id":"tt0068646"}'])

        assert imdb._ids_from_chart("top_movies", "en") == ["tt0111161", "tt0068646"]

    def test_empty_html_fallback_preserves_graphql_failure(self):
        imdb = self._imdb()
        imdb._chart_graphql = MagicMock(side_effect=Failed("GraphQL unavailable"))
        imdb._request = MagicMock(return_value=[])

        with pytest.raises(Failed) as exc_info:
            imdb._ids_from_chart("top_movies", "en")

        error = str(exc_info.value)
        assert "HTML fallback returned no chart data for Top 250 Movies" in error
        assert "GraphQL request failed: GraphQL unavailable" in error

    def test_html_fallback_without_ids_raises_failed(self):
        imdb = self._imdb()
        imdb._chart_graphql = MagicMock(return_value=[])
        imdb._request = MagicMock(return_value=['{"props":{"pageProps":{}}}'])

        with pytest.raises(Failed, match="No IMDb IDs found in HTML fallback for Top 250 Movies"):
            imdb._ids_from_chart("top_movies", "en")


# interest_options: runtime fetch with static-map fallback
# ---------------------------------------------------------------------------


def test_interest_options_uses_fetched_catalog():
    """When the remote catalog fetches cleanly, interest_options uses it (not the fallback)."""
    imdb = IMDb(requests=MagicMock(), cache=None, default_dir="/tmp")
    imdb.requests.get_json = MagicMock(return_value={"hindi": "in0000222", "dc": "in0000244"})
    options = imdb.interest_options
    assert options["hindi"] == "in0000222"
    assert options["dc"] == "in0000244"
    imdb.requests.get_json.assert_called_once()


def test_interest_options_is_cached_after_first_fetch():
    """The catalog is fetched once and memoized on the instance."""
    imdb = IMDb(requests=MagicMock(), cache=None, default_dir="/tmp")
    imdb.requests.get_json = MagicMock(return_value={"action": "in0000001"})
    imdb.interest_options  # noqa: B018 - trigger fetch
    imdb.interest_options  # noqa: B018 - should hit the cache
    imdb.requests.get_json.assert_called_once()


def test_interest_options_falls_back_on_fetch_failure():
    """A network/HTTP failure falls back to the bundled snapshot instead of raising."""
    from modules.imdb import interest_options_fallback

    imdb = IMDb(requests=MagicMock(), cache=None, default_dir="/tmp")
    imdb.requests.get_json = MagicMock(side_effect=ConnectionError("boom"))
    options = imdb.interest_options
    assert options == interest_options_fallback
    assert options["action"] == "in0000001"


def test_interest_options_falls_back_on_empty_response():
    """An empty or malformed response also triggers the fallback."""
    from modules.imdb import interest_options_fallback

    imdb = IMDb(requests=MagicMock(), cache=None, default_dir="/tmp")
    imdb.requests.get_json = MagicMock(return_value={})
    assert imdb.interest_options == interest_options_fallback


# ---------------------------------------------------------------------------
# Service-backed advanced search (imdb_search)
# ---------------------------------------------------------------------------


def make_imdb_search(post_response=None, post_side_effect=None):
    """Return an IMDb instance with _service_post mocked for advanced search."""
    imdb = IMDb(requests=MagicMock(), cache=None, default_dir="/tmp")
    if post_side_effect is not None:
        imdb._service_post = MagicMock(side_effect=post_side_effect)
    else:
        imdb._service_post = MagicMock(return_value=post_response)
    imdb._graph_request = MagicMock()
    return imdb


@pytest.fixture(autouse=True)
def _silence_logger(monkeypatch):
    """Provide a logger for existing unguarded constraint-building traces."""
    monkeypatch.setattr("modules.imdb.logger", MagicMock())


def test_search_posts_constraints_sort_and_limit():
    """The search path splits _graphql_variables into constraints/sort and posts them."""
    imdb = make_imdb_search(post_response={"results": ["tt0111161", "tt0068646"], "total": 2, "cached": True})
    data = {"limit": 10, "type": ["movie"], "genre": ["drama"], "sort_by": "rating.desc"}
    result = imdb._pagination(data, "search")
    assert result == ["tt0111161", "tt0068646"]

    endpoint, body = imdb._service_post.call_args[0]
    assert endpoint == "search/advanced"
    # locale/first/sortBy/sortOrder must NOT be inside constraints
    for key in ("locale", "first", "sortBy", "sortOrder"):
        assert key not in body["constraints"]
    # constraint keys are present
    assert "titleTypeConstraint" in body["constraints"]
    assert "genreConstraint" in body["constraints"]
    # sort is split out correctly
    assert body["sort"] == {"sortBy": "USER_RATING", "sortOrder": "DESC"}
    # limit passed through
    assert body["limit"] == 10


def test_search_allows_missing_logger(monkeypatch):
    """The service request's progress logging is optional."""
    monkeypatch.setattr("modules.imdb.logger", None)
    imdb = make_imdb_search(post_response={"results": ["tt0111161"], "total": 1, "cached": False})
    imdb._graphql_variables = MagicMock(return_value={"locale": "en-US", "first": 250, "sortBy": "POPULARITY", "sortOrder": "ASC"})

    assert imdb._pagination({"limit": 1}, "search") == ["tt0111161"]


def test_search_omits_limit_when_zero():
    """A limit of 0 (Kometa's 'no limit') is omitted so the service uses its default."""
    imdb = make_imdb_search(post_response={"results": ["tt0111161"], "total": 1, "cached": False})
    data = {"limit": 0, "type": ["movie"]}
    imdb._pagination(data, "search")
    _, body = imdb._service_post.call_args[0]
    assert "limit" not in body


def test_search_returns_results_list():
    imdb = make_imdb_search(post_response={"results": ["tt0111161", "tt0068646", "tt0071562"], "total": 3, "cached": True})
    result = imdb._pagination({"limit": 250}, "search")
    assert result == ["tt0111161", "tt0068646", "tt0071562"]


def test_search_empty_results_raises_failed():
    imdb = make_imdb_search(post_response={"results": [], "total": 0, "cached": False})
    with pytest.raises(Failed, match="No IMDb IDs Found"):
        imdb._pagination({"limit": 250}, "search")


def test_search_none_response_raises_failed():
    """A None from _service_post (e.g. 404) is coalesced to {} and raises No IMDb IDs Found."""
    imdb = make_imdb_search(post_response=None)
    with pytest.raises(Failed, match="No IMDb IDs Found"):
        imdb._pagination({"limit": 250}, "search")


def test_search_propagates_service_failure():
    """A service Failed on the search path propagates (no fallback dataset exists)."""
    imdb = make_imdb_search(post_side_effect=Failed("IMDb Service Error: 502 - Bad Gateway"))
    with pytest.raises(Failed, match="502"):
        imdb._pagination({"limit": 250}, "search")


# ---------------------------------------------------------------------------
# _service_post error handling (mirrors _service_request)
# ---------------------------------------------------------------------------


def _post_imdb(status_code=200, json_return=None, json_side_effect=None, content=b"", raise_exc=None):
    imdb = IMDb(requests=MagicMock(), cache=None, default_dir="/tmp")
    if raise_exc is not None:
        imdb.requests.post.side_effect = raise_exc
        return imdb
    response = MagicMock()
    response.status_code = status_code
    response.content = content
    response.text = content.decode() if isinstance(content, bytes) else str(content)
    if json_side_effect is not None:
        response.json.side_effect = json_side_effect
    else:
        response.json.return_value = json_return
    imdb.requests.post.return_value = response
    return imdb


def test_service_post_returns_json_on_success():
    imdb = _post_imdb(status_code=200, json_return={"results": ["tt0111161"]})
    assert imdb._service_post("search/advanced", {"constraints": {}}) == {"results": ["tt0111161"]}
    imdb.requests.post.assert_called_once()


def test_service_post_404_not_found_ok_returns_none():
    imdb = _post_imdb(status_code=404)
    assert imdb._service_post("search/advanced", {}, not_found_ok=True) is None


def test_service_post_error_status_raises_failed():
    imdb = _post_imdb(status_code=502, content=b"Bad Gateway")
    with pytest.raises(Failed, match="502"):
        imdb._service_post("search/advanced", {})


def test_service_post_invalid_json_raises_failed():
    imdb = _post_imdb(status_code=200, json_side_effect=ValueError("no json"), content=b"not json")
    with pytest.raises(Failed, match="invalid JSON"):
        imdb._service_post("search/advanced", {})


def test_service_post_connection_error_raises_failed():
    imdb = _post_imdb(raise_exc=ConnectionError("Connection refused"))
    with pytest.raises(Failed, match="IMDb Service Error"):
        imdb._service_post("search/advanced", {})
