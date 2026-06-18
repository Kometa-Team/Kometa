"""Tests for modules/imdb.py -- focused on parental_guide edge cases."""
import pytest
from unittest.mock import MagicMock

from modules.imdb import IMDb
from modules.util import Failed


def make_imdb(graph_response):
    """Return a minimal IMDb instance with _graph_request mocked to return graph_response."""
    imdb = IMDb(requests=MagicMock(), cache=None, default_dir="/tmp")
    imdb._graph_request = MagicMock(return_value=graph_response)
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
    assert not isinstance(exc_info.value, AttributeError), (
        "AttributeError escaped -- the None guard is missing"
    )


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
    assert not isinstance(exc_info.value, AttributeError), (
        "AttributeError escaped -- the null title guard is missing"
    )


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
    assert not isinstance(exc_info.value, AttributeError), (
        "AttributeError escaped -- the null parentsGuide guard is missing"
    )


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
    graph_response = {
        "data": {
            "title": {
                "parentsGuide": {
                    "categories": []
                }
            }
        }
    }
    imdb = make_imdb(graph_response=graph_response)
    with pytest.raises(Failed, match="No Parental Guide Found"):
        imdb.parental_guide("tt0000000")


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
