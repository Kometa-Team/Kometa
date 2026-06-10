# tests/test_collection_schema.py
import json
import os

import pytest
from jsonschema import ValidationError, validate

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "json-schema", "collection-schema.json")


@pytest.fixture(scope="module")
def collection_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def _collection_with_discover(discover_block):
    """Wrap a tmdb_discover block in a minimal valid collection document."""
    return {"collections": {"Test": {"tmdb_discover": discover_block}}}


# ── Property validation ────────────────────────────────────────────────────────


def test_valid_shared_keys_pass(collection_schema):
    doc = _collection_with_discover(
        {
            "limit": 50,
            "sort_by": "popularity.asc",
            "with_genres": "28",
            "vote_average.gte": 7.0,
            "include_adult": False,
        }
    )
    validate(doc, collection_schema)  # must not raise


def test_unknown_key_rejected(collection_schema):
    doc = _collection_with_discover({"limit": 50, "nonexistent_key": "value"})
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_limit_must_be_integer(collection_schema):
    doc = _collection_with_discover({"limit": "fifty"})
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_vote_average_must_be_number(collection_schema):
    doc = _collection_with_discover({"vote_average.gte": "high"})
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_include_adult_must_be_boolean(collection_schema):
    doc = _collection_with_discover({"include_adult": "yes"})
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_with_status_out_of_range(collection_schema):
    doc = _collection_with_discover({"with_status": 6})  # max is 5
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_with_type_out_of_range(collection_schema):
    doc = _collection_with_discover({"with_type": 7})  # max is 6
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_year_below_minimum(collection_schema):
    doc = _collection_with_discover({"year": 1799})
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_with_status_at_maximum_valid(collection_schema):
    doc = _collection_with_discover({"with_status": 5})  # max is 5
    validate(doc, collection_schema)  # must not raise


def test_with_type_at_maximum_valid(collection_schema):
    doc = _collection_with_discover({"with_type": 6})  # max is 6
    validate(doc, collection_schema)  # must not raise


def test_array_of_blocks_valid(collection_schema):
    doc = _collection_with_discover(
        [
            {"limit": 20, "with_genres": "28"},
            {"limit": 30, "with_genres": "35"},
        ]
    )
    validate(doc, collection_schema)  # must not raise
