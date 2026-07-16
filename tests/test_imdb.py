"""Tests for modules/imdb.py -- focused on parental_guide edge cases."""

from unittest.mock import MagicMock

import pytest

from modules.imdb import IMDb
from modules.util import Failed

_UNSET = object()


def make_imdb(graph_response, service_response=_UNSET):
    """Return a minimal IMDb instance with _graph_request mocked to return graph_response.

    By default the service request returns a valid parental guide response so tests exercise
    the service-only path. Pass service_response to override the service payload.
    """
    imdb = IMDb(requests=MagicMock(), cache=None, default_dir="/tmp")
    imdb._graph_request = MagicMock(return_value=graph_response)
    if service_response is _UNSET:
        service_response = {
            "imdb_id": "tt1234567",
            "parental_guide": {
                "Nudity": "Mild",
                "Violence": "Moderate",
                "Profanity": "None",
                "Alcohol": "None",
                "Frightening": "None",
            },
        }
    imdb._service_request = MagicMock(return_value=service_response)
    return imdb


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
# Service-only parental guide lookups
# ---------------------------------------------------------------------------


def test_parental_guide_valid_service_response():
    """A well-formed service response returns the expected parental dict."""
    service_response = {
        "imdb_id": "tt1234567",
        "parental_guide": {
            "Violence": "Moderate",
            "Profanity": "Mild",
        },
    }
    imdb = make_imdb(graph_response={}, service_response=service_response)
    result = imdb.parental_guide("tt1234567")
    assert result.get("Violence") == "Moderate"
    assert result.get("Profanity") == "Mild"
    imdb._graph_request.assert_not_called()


def test_parental_guide_fills_missing_service_categories_with_none():
    """The service only returns categories that have values; missing ones are filled with None."""
    service_response = {"imdb_id": "tt1234567", "parental_guide": {"Violence": "Severe"}}
    imdb = make_imdb(graph_response={}, service_response=service_response)
    result = imdb.parental_guide("tt1234567")
    assert result.get("Violence") == "Severe"
    assert result.get("Nudity") is None
    assert result.get("Profanity") is None
    assert result.get("Alcohol") is None
    assert result.get("Frightening") is None


def test_parental_guide_empty_service_response_raises_failed():
    """When the service returns an empty guide, treat it as no guide data and raise Failed.

    The service fetches uncached IDs from IMDb and caches them, so an empty response means
    IMDb has no parental guide data for this title.
    """
    imdb = make_imdb(graph_response={}, service_response={"imdb_id": "tt1234567", "parental_guide": {}})
    with pytest.raises(Failed, match="No Parental Guide Found"):
        imdb.parental_guide("tt1234567")
    imdb._graph_request.assert_not_called()


def test_parental_guide_service_returns_none_raises_failed():
    """When the service returns None (e.g. 404), raise Failed instead of AttributeError."""
    imdb = make_imdb(graph_response={}, service_response=None)
    with pytest.raises(Failed, match="No Parental Guide Found"):
        imdb.parental_guide("tt9999999")


def test_parental_guide_service_unavailable_flag_raises_failed():
    """When the service has been marked unavailable, fail fast without calling it."""
    imdb = make_imdb(graph_response={})
    imdb._service_available = False
    with pytest.raises(Failed, match="Kometa IMDb Service is unavailable"):
        imdb.parental_guide("tt1234567")
    imdb._service_request.assert_not_called()


def test_parental_guide_service_failure_raises_failed():
    """When the service raises Failed, propagate the error instead of falling back to GraphQL."""
    imdb = make_imdb(graph_response={"data": {"title": {"parentsGuide": {"categories": [{"category": {"text": "Profanity"}, "severity": {"text": "Mild"}}]}}}})
    imdb._service_request = MagicMock(side_effect=Failed("IMDb Service Error: 503"))
    with pytest.raises(Failed, match="IMDb Service Error: 503"):
        imdb.parental_guide("tt1234567")
    imdb._graph_request.assert_not_called()


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


def make_imdb_service(service_responses, raise_failed=None):
    """Return an IMDb instance with _service_request mocked to return responses
    looked up by endpoint path (e.g. 'title/tt0111161').

    Args:
        service_responses: dict mapping endpoint path to JSON response.
        raise_failed: optional endpoint path that will raise Failed when requested.
    """
    imdb = IMDb(requests=MagicMock(), cache=None, default_dir="/tmp")

    def _fake_service_request(endpoint, not_found_ok=False):
        if raise_failed and endpoint == raise_failed:
            raise Failed("IMDb Service Error: 503")
        return service_responses.get(endpoint, {})

    imdb._service_request = MagicMock(side_effect=_fake_service_request)
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
