"""Tests for modules/meta.py — DataFile / MetadataFile / PlaylistFile.

Focuses on file-path parsing, template validation, and config-file
loading logic that can be tested without real Plex/GitHub connections.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from ruamel.yaml import YAML

import modules.builder  # noqa: F401 — pre-import to break circular deps
from modules.meta import DataFile
from tests.conftest import FakeLogger, FakeRequests

# ═══════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════


def make_datafile(**attrs) -> DataFile:
    """Create a minimal DataFile via ``DataFile.__new__``.

    Also patches ``modules.meta.logger`` to a ``FakeLogger`` - meta.py captures
    ``logger = util.logger`` at import time, so the autouse ``patch_util_logger``
    fixture (which only patches ``modules.util.logger``) doesn't reach it.
    """
    import modules.meta as meta_module

    meta_module.logger = FakeLogger()
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
# apply_template — nested <<var>> resolution (check_for_var early-exit fix)
#
# check_for_var resolves nested "<<var>>" chains over a handful of passes,
# now stopping early once a pass makes no changes instead of always running
# a fixed 8. These tests exercise multi-level chains to confirm the early
# exit doesn't cut resolution off before it's actually done - correctness
# here matters more than measuring the iteration count directly, since
# check_for_var/scan_text are closures with no seam to hook a counter into.
# Iteration-count behavior itself is covered separately by a standalone
# before/after harness (see perf-results-log.md 2026-07-10 entry).
# ═══════════════════════════════════════════════════════════════════════


class TestApplyTemplateNestedVarResolution:
    def test_two_level_chain_fully_resolves(self):
        """var1 references var2, which is a plain value - needs 2 passes to fully resolve."""
        df = make_datafile(templates={"tpl": ({"summary": "<<var1>>"}, {})})
        template_call = [{"name": "tpl", "var1": "<<var2>>-suffix", "var2": "final"}]

        result = df.apply_template("Test Name", "test_mapping", {}, template_call, {})

        assert result["summary"] == "final-suffix"

    def test_three_level_chain_fully_resolves(self):
        """var1 -> var2 -> var3 -> literal, needs 3 passes - well within the early-exit budget."""
        df = make_datafile(templates={"tpl": ({"summary": "<<var1>>"}, {})})
        template_call = [{"name": "tpl", "var1": "<<var2>>", "var2": "<<var3>>", "var3": "literal"}]

        result = df.apply_template("Test Name", "test_mapping", {}, template_call, {})

        assert result["summary"] == "literal"

    def test_single_pass_value_unaffected(self):
        """A plain value with no nested vars must still resolve correctly in one pass."""
        df = make_datafile(templates={"tpl": ({"summary": "<<var1>>"}, {})})
        template_call = [{"name": "tpl", "var1": "plain value"}]

        result = df.apply_template("Test Name", "test_mapping", {}, template_call, {})

        assert result["summary"] == "plain value"

    def test_unresolvable_var_left_as_literal_placeholder(self):
        """A variable that never resolves must stop (not error) and keep the literal placeholder,
        same as the old always-8-passes behavior - proves early exit doesn't mistake 'no progress'
        for a crash or an infinite loop."""
        df = make_datafile(templates={"tpl": ({"summary": "<<never_defined>>"}, {})})
        template_call = [{"name": "tpl", "var1": "irrelevant"}]

        result = df.apply_template("Test Name", "test_mapping", {}, template_call, {})

        assert result["summary"] == "<<never_defined>>"

    def test_arithmetic_suffix_var_plus_n_still_resolves(self):
        """<<var+N>> arithmetic relies on the loop's second=True pass - must still work post-fix."""
        df = make_datafile(templates={"tpl": ({"summary": "<<var1+3>>"}, {})})
        template_call = [{"name": "tpl", "var1": "5"}]

        result = df.apply_template("Test Name", "test_mapping", {}, template_call, {})

        assert result["summary"] == "8"


class TestResolutionEditionDovetailTemplate:
    @staticmethod
    def _apply_edition_template(*, overlay_type, use_resolution=None):
        resolution_path = Path(__file__).resolve().parents[1] / "defaults" / "overlays" / "resolution.yml"
        with resolution_path.open(encoding="utf-8") as handle:
            edition_template = YAML(typ="safe").load(handle)["templates"]["edition"]

        df = make_datafile(
            data_type="Overlay",
            library=SimpleNamespace(type="Movie", name="Movies"),
            templates={"edition": (edition_template, {})},
        )
        variables = {
            "name": "edition",
            "key": "imax",
            "search": "IMAX",
            "type": overlay_type,
            "allowed_libraries": "movie",
        }
        if use_resolution is not None:
            variables["use_resolution"] = use_resolution

        return df.apply_template("IMAX", "IMAX", {}, [variables], {})

    @pytest.mark.parametrize(
        ("use_resolution", "expected"),
        [(None, ["movie"]), (True, ["movie", True]), (False, ["movie", False])],
    )
    def test_dovetail_follows_use_resolution(self, use_resolution, expected):
        result = self._apply_edition_template(overlay_type="edition_dovetail", use_resolution=use_resolution)

        assert result["run_definition"] == expected

    def test_plain_edition_is_not_disabled_with_resolution(self):
        result = self._apply_edition_template(overlay_type="edition", use_resolution=False)

        assert result["run_definition"] == ["movie"]


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
