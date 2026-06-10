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


def test_with_watch_providers_without_watch_region_rejected(collection_schema):
    doc = _collection_with_discover(
        {
            "with_watch_providers": "8",
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


def test_watch_region_with_without_providers_valid(collection_schema):
    doc = _collection_with_discover(
        {
            "watch_region": "US",
            "without_watch_providers": "9",
        }
    )
    validate(doc, collection_schema)  # must not raise


# ── Mutual exclusion ──────────────────────────────────────────────────────────


def test_movie_only_keys_pass(collection_schema):
    doc = _collection_with_discover(
        {
            "limit": 100,
            "with_cast": "500",
            "primary_release_year": 2023,
            "sort_by": "popularity.desc",
        }
    )
    validate(doc, collection_schema)  # must not raise


def test_tv_only_keys_pass(collection_schema):
    doc = _collection_with_discover(
        {
            "limit": 100,
            "with_networks": "213",
            "first_air_date_year": 2023,
            "sort_by": "popularity.desc",
        }
    )
    validate(doc, collection_schema)  # must not raise


def test_mixed_movie_and_tv_keys_rejected(collection_schema):
    doc = _collection_with_discover(
        {
            "primary_release_year": 2023,  # movie-only
            "with_networks": "213",  # TV-only
        }
    )
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_tv_signal_disallows_movie_key(collection_schema):
    doc = _collection_with_discover(
        {
            "first_air_date_year": 2022,  # TV signal
            "with_cast": "500",  # movie-only — must be rejected
        }
    )
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_movie_signal_disallows_tv_key(collection_schema):
    doc = _collection_with_discover(
        {
            "with_cast": "500",  # movie signal
            "include_null_first_air_dates": True,  # TV-only — must be rejected
        }
    )
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_shared_only_allows_all_sort_options(collection_schema):
    """No movie/TV signal — sort_by is unconstrained."""
    doc = _collection_with_discover({"sort_by": "name.asc"})  # TV-only sort option
    validate(doc, collection_schema)  # must not raise (no signal present)


def test_movie_signal_restricts_sort_by(collection_schema):
    doc = _collection_with_discover(
        {
            "with_cast": "500",  # movie signal
            "sort_by": "name.asc",  # TV-only sort option — must be rejected
        }
    )
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_movie_signal_allows_movie_sort(collection_schema):
    doc = _collection_with_discover(
        {
            "with_cast": "500",
            "sort_by": "revenue.desc",  # movie sort option
        }
    )
    validate(doc, collection_schema)  # must not raise


def test_movie_signal_without_sort_by_valid(collection_schema):
    doc = _collection_with_discover(
        {
            "with_cast": "500",  # movie signal, no sort_by specified
        }
    )
    validate(doc, collection_schema)  # must not raise — sort_by constraint only applies when present


def test_tv_signal_without_sort_by_valid(collection_schema):
    doc = _collection_with_discover(
        {
            "with_networks": "213",  # TV signal, no sort_by specified
        }
    )
    validate(doc, collection_schema)  # must not raise — sort_by constraint only applies when present


def test_tv_signal_restricts_sort_by(collection_schema):
    doc = _collection_with_discover(
        {
            "with_networks": "213",  # TV signal
            "sort_by": "revenue.desc",  # movie-only sort option — must be rejected
        }
    )
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_tv_signal_allows_tv_sort(collection_schema):
    doc = _collection_with_discover(
        {
            "with_networks": "213",
            "sort_by": "name.asc",  # TV sort option
        }
    )
    validate(doc, collection_schema)  # must not raise
