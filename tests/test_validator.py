import os
from collections import Counter

import modules.validator as validator_module
from modules.validator import ConfigValidator, FileSetValidator, collect_yaml_files, detect_schema_type  # noqa: F401


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


# ── Full-level tests ──────────────────────────────────────────────────────────


def test_full_passes_when_config_file_init_succeeds(tmp_path, monkeypatch):
    import modules.validator as vm

    monkeypatch.setattr(vm, "logger", FakeLogger())

    class FakeConfigFile:
        def __init__(self, *args, **kwargs):
            pass

    monkeypatch.setattr(vm, "_ConfigFile", FakeConfigFile)

    v = make_validator(tmp_path, "libraries: {}\n", level="full")
    passed, errors, warnings = v.validate()
    assert passed
    assert errors == []


def test_full_reports_error_when_config_file_init_raises(tmp_path, monkeypatch):
    import modules.validator as vm

    monkeypatch.setattr(vm, "logger", FakeLogger())

    class BadConfigFile:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("Plex connection refused")

    monkeypatch.setattr(vm, "_ConfigFile", BadConfigFile)

    v = make_validator(tmp_path, "libraries: {}\n", level="full")
    passed, errors, warnings = v.validate()
    assert not passed
    assert any("Plex connection refused" in e for e in errors)


# ── Schema validation tests ───────────────────────────────────────────────────

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
SCHEMA_DIR = os.path.join(REPO_ROOT, "json-schema")

# Minimal valid config.yml stub that satisfies config-schema.json required fields
_VALID_CONFIG_STUB = "plex:\n" "  url: http://localhost:32400\n" "  token: fake-token\n" "tmdb:\n" "  apikey: fake-apikey\n"


def test_schema_valid_collection_file_passes(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    config = _VALID_CONFIG_STUB + "libraries:\n" "  Movies:\n" "    collection_files:\n" "      - file: collections/good.yml\n"
    collection_content = "collections:\n  My Collection:\n    tmdb_popular: 5\n"
    v = make_validator(
        tmp_path,
        config,
        level="syntax",
        validate_schema=True,
        schema_path=SCHEMA_DIR,
        extra_files={"collections/good.yml": collection_content},
    )
    passed, errors, warnings = v.validate()
    assert errors == [], f"Unexpected errors: {errors}"


def test_schema_missing_schema_dir_warns_and_does_not_error(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    v = make_validator(
        tmp_path,
        "libraries: {}\n",
        level="syntax",
        validate_schema=True,
        schema_path="/nonexistent/schema/dir",
    )
    passed, errors, warnings = v.validate()
    assert passed
    assert any("not found" in w or "Schema" in w for w in warnings)


def test_schema_additionalproperties_violation_goes_to_gap_not_error(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    config = _VALID_CONFIG_STUB + "libraries:\n" "  Movies:\n" "    collection_files:\n" "      - file: collections/extra.yml\n"
    # unknown_key_xyz is not in collection-schema.json
    collection_content = "collections:\n  Test:\n    tmdb_popular: 5\nunknown_key_xyz: true\n"
    v = make_validator(
        tmp_path,
        config,
        level="syntax",
        validate_schema=True,
        schema_path=SCHEMA_DIR,
        extra_files={"collections/extra.yml": collection_content},
    )
    passed, errors, warnings = v.validate()
    # additionalProperties violations are warnings/gaps, not errors
    assert errors == [], f"additionalProperties should not be in errors: {errors}"
    assert "collection-schema.json" in v._schema_gaps
    assert any("unknown_key_xyz" in k for k in v._schema_gaps["collection-schema.json"])


def test_schema_type_error_is_an_error(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    config = _VALID_CONFIG_STUB + "libraries:\n" "  Movies:\n" "    collection_files:\n" "      - file: collections/typed.yml\n"
    # visible_home is a bool/string in the schema; passing a list makes it a type error
    collection_content = "collections:\n  Test:\n    tmdb_popular: 5\n    visible_home: [not, a, bool]\n"
    v = make_validator(
        tmp_path,
        config,
        level="syntax",
        validate_schema=True,
        schema_path=SCHEMA_DIR,
        extra_files={"collections/typed.yml": collection_content},
    )
    passed, errors, warnings = v.validate()
    assert not passed
    assert any("visible_home" in e or "typed.yml" in e for e in errors)


def test_schema_gap_report_deduplicates_across_files(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    config = _VALID_CONFIG_STUB + "libraries:\n" "  Movies:\n" "    collection_files:\n" "      - file: collections/a.yml\n" "      - file: collections/b.yml\n"
    content = "collections:\n  Test:\n    tmdb_popular: 5\nunknown_key_xyz: true\n"
    v = make_validator(
        tmp_path,
        config,
        level="syntax",
        validate_schema=True,
        schema_path=SCHEMA_DIR,
        extra_files={"collections/a.yml": content, "collections/b.yml": content},
    )
    v.validate()
    gaps = v._schema_gaps.get("collection-schema.json", Counter())
    assert any("unknown_key_xyz" in k for k in gaps)
    # seen in both files → count is 2
    gap_key = next(k for k in gaps if "unknown_key_xyz" in k)
    assert gaps[gap_key] == 2


# ── detect_schema_type tests ──────────────────────────────────────────────────


def test_detect_schema_type_collection():
    assert detect_schema_type({"collections": {}}) == "collection_files"


def test_detect_schema_type_dynamic_collections():
    assert detect_schema_type({"dynamic_collections": {}}) == "collection_files"


def test_detect_schema_type_overlay():
    assert detect_schema_type({"overlays": {}}) == "overlay_files"


def test_detect_schema_type_playlist():
    assert detect_schema_type({"playlists": {}}) == "playlist_files"


def test_detect_schema_type_metadata():
    assert detect_schema_type({"metadata": {}}) == "metadata_files"


def test_detect_schema_type_config():
    assert detect_schema_type({"libraries": {}, "plex": {}}) == "config"


def test_detect_schema_type_templates_only():
    assert detect_schema_type({"templates": {}}) is None


def test_detect_schema_type_templates_with_collections():
    assert detect_schema_type({"templates": {}, "collections": {}}) == "collection_files"


# ── collect_yaml_files tests ──────────────────────────────────────────────────


def test_collect_yaml_files_single_file(tmp_path):
    f = tmp_path / "test.yml"
    f.write_text("key: value", encoding="utf-8")
    assert collect_yaml_files(str(f)) == [str(f)]


def test_collect_yaml_files_directory(tmp_path):
    (tmp_path / "a.yml").write_text("key: a", encoding="utf-8")
    (tmp_path / "b.yaml").write_text("key: b", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "c.yml").write_text("key: c", encoding="utf-8")
    (tmp_path / "not_yaml.txt").write_text("ignore me", encoding="utf-8")
    result = collect_yaml_files(str(tmp_path))
    assert sorted(result) == sorted(
        [
            str(tmp_path / "a.yml"),
            str(tmp_path / "b.yaml"),
            str(tmp_path / "sub" / "c.yml"),
        ]
    )


# ── FileSetValidator tests ────────────────────────────────────────────────────


def test_fileset_validator_clean_file_passes(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    f = tmp_path / "collections.yml"
    f.write_text("collections:\n  My Collection:\n    tmdb_popular: 5\n", encoding="utf-8")
    v = FileSetValidator([str(f)], SCHEMA_DIR)
    passed, per_file_errors, aggregate_gaps = v.validate()
    assert passed
    assert per_file_errors == {}


def test_fileset_validator_parse_error(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    f = tmp_path / "bad.yml"
    f.write_text("key: [\n  unclosed\n", encoding="utf-8")
    v = FileSetValidator([str(f)], SCHEMA_DIR)
    passed, per_file_errors, aggregate_gaps = v.validate()
    assert not passed
    assert str(f) in per_file_errors
    assert any("YAML" in e for e in per_file_errors[str(f)])
    assert aggregate_gaps == {}


def test_fileset_validator_unknown_type(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    f = tmp_path / "templates_only.yml"
    f.write_text("templates:\n  MyTemplate:\n    test: true\n", encoding="utf-8")
    v = FileSetValidator([str(f)], SCHEMA_DIR)
    passed, per_file_errors, aggregate_gaps = v.validate()
    assert passed
    assert per_file_errors == {}


def test_fileset_validator_aggregate_gaps(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    content = "collections:\n  Test:\n    tmdb_popular: 5\nunknown_key_xyz: true\n"
    f1 = tmp_path / "a.yml"
    f2 = tmp_path / "b.yml"
    f1.write_text(content, encoding="utf-8")
    f2.write_text(content, encoding="utf-8")
    v = FileSetValidator([str(f1), str(f2)], SCHEMA_DIR)
    passed, per_file_errors, aggregate_gaps = v.validate()
    assert passed
    assert "collection-schema.json" in aggregate_gaps
    gap_key = next(k for k in aggregate_gaps["collection-schema.json"] if "unknown_key_xyz" in k)
    assert aggregate_gaps["collection-schema.json"][gap_key] == 2
