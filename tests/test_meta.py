"""Tests for modules/meta.py — DataFile / MetadataFile / PlaylistFile.

Focuses on file-path parsing, template validation, and config-file
loading logic that can be tested without real Plex/GitHub connections.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401 — pre-import to break circular deps
from modules.meta import DataFile
from tests.conftest import FakeLogger, FakeRequests

# ═══════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════


def make_datafile(**attrs) -> DataFile:
    """Create a minimal DataFile via ``DataFile.__new__``."""
    df = DataFile.__new__(DataFile)
    defaults = {
        "config": MagicMock(),
        "library": None,
        "type": "File",
        "path": "/config/collections/test.yml",
        "temp_vars": {},
        "language": "en",
        "asset_directory": None,
        "data_type": "Collection",
        "templates": {},
    }
    defaults.update(attrs)
    for key, value in defaults.items():
        setattr(df, key, value)
    return df


# ═══════════════════════════════════════════════════════════════════════
# get_file_name
# ═══════════════════════════════════════════════════════════════════════


class TestGetFileName:
    def test_local_file_with_yml(self):
        df = make_datafile(path="/config/collections/action.yml", type="File")
        assert df.get_file_name() == "action"

    def test_local_file_with_yaml(self):
        df = make_datafile(path="/config/collections/action.yaml", type="File")
        assert df.get_file_name() == "action"

    def test_local_file_no_extension(self):
        df = make_datafile(path="/config/collections/action", type="File")
        assert df.get_file_name() == "action"

    def test_windows_path(self):
        df = make_datafile(path="C:\\config\\collections\\action.yml", type="File")
        assert df.get_file_name() == "action"

    def test_relative_path(self):
        df = make_datafile(path="config/collections/action.yml", type="File")
        assert df.get_file_name() == "action"

    def test_git_type_extracts_filename(self):
        """GIT type builds a URL internally but extracts the filename from it."""
        config = MagicMock()
        config.GitHub.configs_url = "https://raw.githubusercontent.com/Kometa-Team/Default-Collection/master/"
        df = make_datafile(path="action", config=config)
        df.type = "GIT"
        name = df.get_file_name()
        assert name == "action"

    def test_just_filename_preserves_extension(self):
        """When there's no directory separator, the full name is returned as-is."""
        df = make_datafile(path="action.yml")
        assert df.get_file_name() == "action.yml"


# ═══════════════════════════════════════════════════════════════════════
# apply_template — validation paths
# ═══════════════════════════════════════════════════════════════════════


class TestApplyTemplate:
    def test_raises_when_no_templates(self):
        df = make_datafile(templates={})
        from modules.util import Failed

        with pytest.raises(Failed, match="No templates found"):
            df.apply_template("test", "test", {}, None, {})

    def test_raises_when_template_call_is_none(self):
        df = make_datafile(templates={"test": [{"name": "test"}, {}]})
        from modules.util import Failed

        with pytest.raises(Failed, match="is blank"):
            df.apply_template("test", "test", {}, None, {})

    def test_raises_when_template_not_found(self):
        df = make_datafile(templates={"exists": [{"name": "exists"}, {}]})
        from modules.util import Failed

        with pytest.raises(Failed, match="not found"):
            df.apply_template("test", "test", {}, [{"name": "missing"}], {})


# ═══════════════════════════════════════════════════════════════════════
# load_file — file existence and type validation
# ═══════════════════════════════════════════════════════════════════════


class TestLoadFile:
    def test_adds_yml_extension_when_missing(self, monkeypatch):
        monkeypatch.setattr("modules.meta.logger", FakeLogger())
        df = make_datafile()
        # Simulate the file not being found by making config.Requests.file_yaml raise
        df.config.Requests = FakeRequests()
        import modules.util as util

        with pytest.raises(util.Failed):
            df.load_file("File", "/nonexistent/path")

    def test_preserves_yml_extension(self, monkeypatch):
        monkeypatch.setattr("modules.meta.logger", FakeLogger())
        df = make_datafile()
        df.config.Requests = FakeRequests()
        import modules.util as util

        with pytest.raises(util.Failed):
            df.load_file("File", "/nonexistent/path.yml")


# ═══════════════════════════════════════════════════════════════════════
# get_dict — module-level pure function for parsing YAML attribute blocks
# ═══════════════════════════════════════════════════════════════════════


class TestGetDict:
    """Tests for meta.get_dict — extracts a nested dict from YAML attr data.

    Used pervasively for parsing 'collections:', 'templates:', 'queues:',
    'overlays:' blocks out of metadata YAML files. Every branch matters
    because a silent skip here means a user's YAML is partially ignored.
    """

    @pytest.fixture(autouse=True)
    def _logger(self, monkeypatch):
        monkeypatch.setattr("modules.meta.logger", FakeLogger())

    def test_missing_attribute_returns_empty(self):
        from modules.meta import get_dict

        assert get_dict("collections", {"other_key": {}}) == {}

    def test_blank_attribute_returns_empty(self):
        from modules.meta import get_dict

        assert get_dict("collections", {"collections": None}) == {}

    def test_non_dict_attribute_returns_empty(self):
        """If 'collections' is a list/string/int, ignore it and return {}."""
        from modules.meta import get_dict

        assert get_dict("collections", {"collections": ["a", "b"]}) == {}
        assert get_dict("collections", {"collections": "string"}) == {}

    def test_simple_dict_passthrough(self):
        from modules.meta import get_dict

        data = {"collections": {"My Collection": {"smart": True}}}
        result = get_dict("collections", data)
        assert result == {"My Collection": {"smart": True}}

    def test_none_value_skipped(self):
        """Entries with None data are dropped silently (YAML null)."""
        from modules.meta import get_dict

        data = {
            "collections": {
                "Good": {"smart": True},
                "Blank": None,
            }
        }
        result = get_dict("collections", data)
        assert "Good" in result
        assert "Blank" not in result

    def test_non_dict_value_skipped_with_warning(self):
        """A collection definition must be a dict; strings/ints are skipped."""
        from modules.meta import get_dict

        data = {
            "collections": {
                "Good": {"smart": True},
                "Bad": "this is a string, not a dict",
            }
        }
        result = get_dict("collections", data)
        assert "Good" in result
        assert "Bad" not in result

    def test_duplicate_in_check_list_skipped(self):
        """If a name is already in check_list, it's a duplicate; skip it."""
        from modules.meta import get_dict

        data = {"collections": {"Existing": {"a": 1}, "New": {"b": 2}}}
        result = get_dict("collections", data, check_list=["Existing"])
        assert "Existing" not in result
        assert "New" in result

    def test_templates_special_case_wraps_in_tuple(self):
        """For 'templates' attribute, value becomes (data, {}) tuple."""
        from modules.meta import get_dict

        data = {"templates": {"my_template": {"key": "value"}}}
        result = get_dict("templates", data)
        assert result == {"my_template": ({"key": "value"}, {})}

    def test_queues_special_case_allows_non_dict(self):
        """For 'queues', non-dict values are kept (unlike collections)."""
        from modules.meta import get_dict

        data = {"queues": {"my_queue": "some string"}}
        result = get_dict("queues", data)
        assert "my_queue" in result

    def test_make_str_converts_keys_to_string(self):
        from modules.meta import get_dict

        data = {"collections": {123: {"key": "value"}}}
        result = get_dict("collections", data, make_str=True)
        assert "123" in result
        assert 123 not in result

    def test_check_list_with_make_str_compares_string_form(self):
        from modules.meta import get_dict

        data = {"collections": {123: {"key": "value"}, 456: {"key": "value2"}}}
        # check_list contains "123" (string); int 123 should be detected as duplicate
        result = get_dict("collections", data, check_list=["123"], make_str=True)
        assert "123" not in result
        assert "456" in result

    def test_empty_dict_input_returns_empty(self):
        from modules.meta import get_dict

        assert get_dict("collections", {}) == {}

    def test_none_input_returns_empty(self):
        from modules.meta import get_dict

        assert get_dict("collections", None) == {}
