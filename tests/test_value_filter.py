from types import SimpleNamespace

import pytest

import modules.builder as builder_module
from modules.builder import CollectionBuilder
from modules.util import BuilderValidationError, Failed


def _parser_builder():
    builder = CollectionBuilder.__new__(CollectionBuilder)
    builder.Type = "Overlay"
    builder.value_filters = []
    return builder


def test_value_filter_parses_valid_conditions():
    builder = _parser_builder()
    builder._value_filter("value_filter", {"mdb_tomatoes_rating.gte": 6.0, "tmdb_rating.lt": 8})
    assert ("mdb_tomatoes_rating", "gte", 6.0) in builder.value_filters
    assert ("tmdb_rating", "lt", 8.0) in builder.value_filters


def test_value_filter_rejects_bad_comparator():
    with pytest.raises(BuilderValidationError):
        _parser_builder()._value_filter("value_filter", {"tmdb_rating.between": 6.0})


def test_value_filter_rejects_non_numeric_threshold():
    with pytest.raises(BuilderValidationError):
        _parser_builder()._value_filter("value_filter", {"tmdb_rating.gte": "high"})


def test_value_filter_rejects_unknown_variable():
    with pytest.raises(BuilderValidationError):
        _parser_builder()._value_filter("value_filter", {"made_up_rating.gte": 6.0})


def test_value_filter_rejects_missing_variable_name():
    with pytest.raises(BuilderValidationError):
        _parser_builder()._value_filter("value_filter", {"gte": 6.0})


def test_value_filter_rejects_non_dict():
    with pytest.raises(BuilderValidationError):
        _parser_builder()._value_filter("value_filter", ["not", "a", "dict"])


def _check_builder(value_filters, fetch):
    builder = CollectionBuilder.__new__(CollectionBuilder)
    builder.Type = "Overlay"
    builder.value_filters = value_filters
    builder.library = SimpleNamespace(fetch_overlay_value=fetch)
    return builder


def test_check_value_filter_empty_passes():
    builder = _check_builder([], lambda item, variable: None)
    assert builder.check_value_filter(SimpleNamespace(title="X")) is True


def test_check_value_filter_passes_and_fails():
    fetch = lambda item, variable: 7.0
    assert _check_builder([("tmdb_rating", "gte", 6.0)], fetch).check_value_filter(SimpleNamespace(title="X")) is True
    assert _check_builder([("tmdb_rating", "gte", 8.0)], fetch).check_value_filter(SimpleNamespace(title="X")) is False


def test_check_value_filter_and_logic_requires_all():
    fetch = lambda item, variable: 7.0
    both_pass = _check_builder([("tmdb_rating", "gte", 6.0), ("tmdb_rating", "lte", 10.0)], fetch)
    assert both_pass.check_value_filter(SimpleNamespace(title="X")) is True
    one_fails = _check_builder([("tmdb_rating", "gte", 6.0), ("tmdb_rating", "lt", 7.0)], fetch)
    assert one_fails.check_value_filter(SimpleNamespace(title="X")) is False


def test_check_value_filter_excludes_on_none(monkeypatch):
    monkeypatch.setattr(builder_module, "logger", SimpleNamespace(warning=lambda *a, **k: None))
    builder = _check_builder([("tmdb_rating", "gte", 6.0)], lambda item, variable: None)
    assert builder.check_value_filter(SimpleNamespace(title="X")) is False


def test_check_value_filter_excludes_on_fetch_failure(monkeypatch):
    monkeypatch.setattr(builder_module, "logger", SimpleNamespace(warning=lambda *a, **k: None))

    def fetch(item, variable):
        raise Failed("no id")

    builder = _check_builder([("tmdb_rating", "gte", 6.0)], fetch)
    assert builder.check_value_filter(SimpleNamespace(title="X")) is False
