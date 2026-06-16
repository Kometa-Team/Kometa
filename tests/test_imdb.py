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
# Regression test: the original bug
# ---------------------------------------------------------------------------

def test_parental_guide_none_response_pre_fix_raises_attribute_error():
    """Demonstrate the original bug: calling .get() on None raises AttributeError.

    This documents the regression -- the line BEFORE the fix looked like:
        (self._graph_request(...).get("data") or {})...
    which explodes when _graph_request returns None.
    """
    result = None  # simulate _graph_request returning None
    with pytest.raises(AttributeError):
        (result.get("data") or {}).get("title", {})


# ---------------------------------------------------------------------------
# Fix tests: _graph_request returns None (item has no IMDb record)
# ---------------------------------------------------------------------------

def test_parental_guide_none_response_raises_failed():
    """When _graph_request returns None (no IMDb record), parental_guide should
    raise Failed -- not AttributeError -- so operations.py can catch it cleanly."""
    imdb = make_imdb(graph_response=None)
    with pytest.raises(Failed, match="No Parental Guide Found"):
        imdb.parental_guide("tt9999999")


def test_parental_guide_none_response_does_not_raise_attribute_error():
    """The fix must not let AttributeError escape."""
    imdb = make_imdb(graph_response=None)
    with pytest.raises(Exception) as exc_info:
        imdb.parental_guide("tt9999999")
    assert not isinstance(exc_info.value, AttributeError), (
        "AttributeError escaped -- the None guard is missing"
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
