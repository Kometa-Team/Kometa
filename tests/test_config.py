from datetime import datetime

import pytest

import modules.builder  # noqa: F401
import modules.config as config_module
from modules.config import ConfigFile
from modules.request import YAML
from modules.util import Failed


class FakeLogger:
    def __init__(self):
        self.secrets = []
        self.saved_errors = []
        self.save_errors = False
        self.warnings = []

    def secret(self, text):
        if text and str(text) not in self.secrets:
            self.secrets.append(str(text))

    def warning(self, message=""):
        self.warnings.append(str(message))

    def clear_errors(self):
        self.saved_errors = []

    def __getattr__(self, name):
        return lambda *args, **kwargs: None


class FakeRequests:
    def file_yaml(self, path, **kwargs):
        return YAML(path=path, **kwargs)

    def has_new_version(self):
        return False


def test_missing_minimum_items_default_is_not_registered_as_secret(tmp_path, monkeypatch):
    config_path = tmp_path / "config.yml"
    config_path.write_text("settings:\n  cache: false\nlibraries: {}\ntmdb: {}\n", encoding="utf-8")

    fake_logger = FakeLogger()
    monkeypatch.setattr(config_module, "logger", fake_logger)

    attrs = {
        "config_file": str(config_path),
        "time_obj": datetime(2026, 6, 14, 18, 53),
        "time": "18:53",
    }

    with pytest.raises(Failed):
        ConfigFile(FakeRequests(), str(tmp_path), attrs, secrets={})

    assert any("settings sub-attribute minimum_items not found using 1 as default" in warning for warning in fake_logger.warnings)
    assert "1" not in fake_logger.secrets
