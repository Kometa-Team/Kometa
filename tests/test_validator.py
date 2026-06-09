import modules.validator as validator_module
from modules.validator import ConfigValidator


class FakeLogger:
    def __init__(self):
        self.info_msgs = []
        self.warning_msgs = []
        self.error_msgs = []

    def info(self, msg=""):
        self.info_msgs.append(str(msg))

    def warning(self, msg=""):
        self.warning_msgs.append(str(msg))

    def error(self, msg=""):
        self.error_msgs.append(str(msg))

    def separator(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        return lambda *args, **kwargs: None


def make_validator(tmp_path, config_content, level="syntax", validate_schema=False, schema_path=None, extra_files=None):
    """Write config.yml to tmp_path and return a ConfigValidator."""
    config_file = tmp_path / "config.yml"
    config_file.write_text(config_content, encoding="utf-8")
    if extra_files:
        for rel_path, content in extra_files.items():
            p = tmp_path / rel_path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
    attrs = {"config_file": str(config_file)}
    return ConfigValidator(
        requests=None,
        default_dir=str(tmp_path),
        attrs=attrs,
        secret_args={},
        level=level,
        validate_schema=validate_schema,
        schema_path=schema_path,
    )


# ── Syntax tests ──────────────────────────────────────────────────────────────


def test_syntax_valid_config_passes(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    v = make_validator(tmp_path, "libraries:\n  Movies:\n    collection_files: []\n")
    passed, errors, warnings = v.validate()
    assert passed
    assert errors == []


def test_syntax_invalid_yaml_in_config_reports_error(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    v = make_validator(tmp_path, "libraries:\n  bad:\n\tinvalid_tab: true\n")
    passed, errors, warnings = v.validate()
    assert not passed
    assert any("YAML Error" in e for e in errors)


def test_syntax_invalid_yaml_in_linked_file_reports_error(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    config = "libraries:\n" "  Movies:\n" "    collection_files:\n" "      - file: collections/bad.yml\n"
    v = make_validator(tmp_path, config, extra_files={"collections/bad.yml": "key: [\n  unclosed\n"})
    passed, errors, warnings = v.validate()
    assert not passed
    assert any("bad.yml" in e for e in errors)


def test_syntax_missing_linked_file_is_not_an_error_at_syntax_level(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    config = "libraries:\n" "  Movies:\n" "    collection_files:\n" "      - file: collections/missing.yml\n"
    v = make_validator(tmp_path, config)
    passed, errors, warnings = v.validate()
    assert passed
    assert errors == []


def test_syntax_url_references_are_skipped(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    config = "libraries:\n" "  Movies:\n" "    collection_files:\n" "      - url: https://example.com/collections.yml\n"
    v = make_validator(tmp_path, config)
    passed, errors, warnings = v.validate()
    assert passed


def test_syntax_git_references_are_skipped(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    config = "libraries:\n" "  Movies:\n" "    collection_files:\n" "      - git: some/path\n"
    v = make_validator(tmp_path, config)
    passed, errors, warnings = v.validate()
    assert passed


def test_syntax_playlist_files_are_checked(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    config = "playlist_files:\n  - file: playlists/bad.yml\n"
    v = make_validator(tmp_path, config, extra_files={"playlists/bad.yml": "key: [\n  unclosed\n"})
    passed, errors, warnings = v.validate()
    assert not passed
    assert any("bad.yml" in e for e in errors)


# ── Structure tests ───────────────────────────────────────────────────────────


def test_structure_missing_libraries_warns(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    v = make_validator(tmp_path, "tmdb:\n  apikey: abc\n", level="structure")
    passed, errors, warnings = v.validate()
    assert passed
    assert any("libraries" in w for w in warnings)


def test_structure_missing_tmdb_warns(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    v = make_validator(tmp_path, "libraries:\n  Movies:\n    collection_files: []\n", level="structure")
    passed, errors, warnings = v.validate()
    assert passed
    assert any("tmdb" in w for w in warnings)


def test_structure_deprecated_metadata_path_warns(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    config = "libraries:\n" "  Movies:\n" "    metadata_path:\n" "      - file: collections/test.yml\n"
    v = make_validator(tmp_path, config, level="structure")
    passed, errors, warnings = v.validate()
    assert any("metadata_path" in w and "deprecated" in w for w in warnings)


def test_structure_deprecated_overlay_path_warns(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    config = "libraries:\n" "  Movies:\n" "    overlay_path:\n" "      - file: overlays/test.yml\n"
    v = make_validator(tmp_path, config, level="structure")
    passed, errors, warnings = v.validate()
    assert any("overlay_path" in w and "deprecated" in w for w in warnings)


def test_structure_missing_file_path_is_error(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    config = "libraries:\n" "  Movies:\n" "    collection_files:\n" "      - file: collections/missing.yml\n" "tmdb:\n" "  apikey: abc\n"
    v = make_validator(tmp_path, config, level="structure")
    passed, errors, warnings = v.validate()
    assert not passed
    assert any("missing.yml" in e and "not found" in e for e in errors)


def test_structure_existing_file_path_passes(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    config = "libraries:\n" "  Movies:\n" "    collection_files:\n" "      - file: collections/good.yml\n" "tmdb:\n" "  apikey: abc\n"
    v = make_validator(tmp_path, config, level="structure", extra_files={"collections/good.yml": "collections:\n  My Collection:\n    tmdb_popular: true\n"})
    passed, errors, warnings = v.validate()
    assert errors == []


def test_structure_library_with_no_content_warns(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    config = "libraries:\n  Movies:\n    plex:\n      url: http://localhost\n"
    v = make_validator(tmp_path, config, level="structure")
    passed, errors, warnings = v.validate()
    assert any("Movies" in w and "no" in w.lower() for w in warnings)


def test_structure_yaml_error_in_config_is_error(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    v = make_validator(tmp_path, "bad:\n\ttabs: not allowed\n", level="structure")
    passed, errors, warnings = v.validate()
    assert not passed
    assert any("YAML Error" in e for e in errors)
