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


def test_primary_release_year_below_minimum(collection_schema):
    doc = _collection_with_discover({"primary_release_year": 1799})
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_first_air_date_year_below_minimum(collection_schema):
    doc = _collection_with_discover({"first_air_date_year": 1799})
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


# ── Cross-dependency rules ─────────────────────────────────────────────────────


def test_certification_country_without_certification_rejected(collection_schema):
    doc = _collection_with_discover(
        {
            "certification_country": "US",
            # missing: certification / certification.lte / certification.gte
        }
    )
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_certification_without_certification_country_rejected(collection_schema):
    doc = _collection_with_discover(
        {
            "certification": "PG-13",
            # missing: certification_country
        }
    )
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_certification_lte_without_certification_country_rejected(collection_schema):
    doc = _collection_with_discover(
        {
            "certification.lte": "PG-13",
        }
    )
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_certification_gte_without_certification_country_rejected(collection_schema):
    doc = _collection_with_discover(
        {
            "certification.gte": "PG-13",
        }
    )
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_certification_pair_valid(collection_schema):
    doc = _collection_with_discover(
        {
            "certification_country": "US",
            "certification": "PG-13",
        }
    )
    validate(doc, collection_schema)  # must not raise


def test_certification_country_with_lte_valid(collection_schema):
    doc = _collection_with_discover(
        {
            "certification_country": "US",
            "certification.lte": "R",
        }
    )
    validate(doc, collection_schema)  # must not raise


def test_watch_region_without_providers_rejected(collection_schema):
    doc = _collection_with_discover(
        {
            "watch_region": "US",
            # missing: with_watch_providers / without_watch_providers / with_watch_monetization_types
        }
    )
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_monetization_types_without_watch_region_rejected(collection_schema):
    doc = _collection_with_discover(
        {
            "with_watch_monetization_types": "flatrate",
        }
    )
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_without_watch_providers_without_watch_region_rejected(collection_schema):
    doc = _collection_with_discover(
        {
            "without_watch_providers": "8",
        }
    )
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_watch_region_with_providers_valid(collection_schema):
    doc = _collection_with_discover(
        {
            "watch_region": "US",
            "with_watch_providers": "8",
        }
    )
    validate(doc, collection_schema)  # must not raise


def test_watch_region_with_monetization_valid(collection_schema):
    doc = _collection_with_discover(
        {
            "watch_region": "GB",
            "with_watch_monetization_types": "flatrate",
        }
    )
    validate(doc, collection_schema)  # must not raise
