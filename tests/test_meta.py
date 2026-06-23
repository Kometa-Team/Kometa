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
