"""Tests for util.py — exception hierarchy and helpers."""

from __future__ import annotations

import os

import pytest

import modules.builder  # noqa: F401


class TestExceptionHierarchy:
    def test_failed_is_base(self):
        from modules.util import BuilderValidationError, Failed, FilterFailed, MappingConvertError, NoValueFound, OverlayError, ServiceError

        assert issubclass(FilterFailed, Failed)
        assert issubclass(BuilderValidationError, Failed)
        assert issubclass(OverlayError, Failed)
        assert issubclass(NoValueFound, Failed)
        assert issubclass(MappingConvertError, Failed)
        assert issubclass(ServiceError, Failed)

    def test_not_scheduled_is_exception(self):
        from modules.util import NotScheduled, NotScheduledRange

        assert issubclass(NotScheduledRange, NotScheduled)
        assert issubclass(NotScheduled, Exception)

    def test_continue_is_exception(self):
        from modules.util import Continue, Deleted, NonExisting

        assert issubclass(Continue, Exception)
        assert issubclass(Deleted, Exception)
        assert issubclass(NonExisting, Exception)

    def test_exceptions_can_be_raised(self):
        from modules.util import Failed, FilterFailed

        with pytest.raises(Failed):
            raise Failed("test")
        with pytest.raises(Failed):
            raise FilterFailed("test")


# ═══════════════════════════════════════════════════════════════════════
# Helper functions
# ═══════════════════════════════════════════════════════════════════════


class TestCheckNum:
    def test_int_string(self):
        from modules.util import check_num

        assert check_num("42", is_int=True) == 42

    def test_int_value(self):
        from modules.util import check_num

        assert check_num(42, is_int=True) == 42

    def test_float_string(self):
        from modules.util import check_num

        assert check_num("7.5", is_int=False) == 7.5

    def test_none_returns_none(self):
        from modules.util import check_num

        assert check_num(None) is None

    def test_empty_string_returns_none(self):
        from modules.util import check_num

        assert check_num("") is None


class TestGetIdFromImdbUrl:
    def test_full_url(self):
        from modules.util import get_id_from_imdb_url

        assert get_id_from_imdb_url("https://www.imdb.com/title/tt1234567/") == "tt1234567"

    def test_bare_id(self):
        from modules.util import get_id_from_imdb_url

        assert get_id_from_imdb_url("tt1234567") == "tt1234567"

    def test_url_with_ref(self):
        from modules.util import get_id_from_imdb_url

        assert get_id_from_imdb_url("https://www.imdb.com/title/tt9999999/?ref_=fn_al_tt_1") == "tt9999999"


class TestValidateFilename:
    def test_removes_invalid_chars(self):
        from modules.util import validate_filename

        result = validate_filename("My:File/Name*")
        assert ":" not in result
        assert "/" not in result
        assert "*" not in result


class TestIsLocked:
    def test_returns_none_for_nonexistent(self):
        from modules.util import is_locked

        assert is_locked("/nonexistent/file.txt") is None


class TestCheckInt:
    def test_valid_int(self):
        from modules.util import check_int

        assert check_int(5, "test") == 5

    def test_non_numeric_raises(self):
        from modules.util import Failed, check_int

        with pytest.raises(Failed, match="must be"):
            check_int("not-a-number", "test", throw=True)


# ═══════════════════════════════════════════════════════════════════════
# load_files — relative path resolution (issue #3092)
# ═══════════════════════════════════════════════════════════════════════


class TestLoadFiles:
    """Verify that relative paths in load_files() resolve against config_dir,
    not the current working directory."""

    # ── plain string form ──────────────────────────────────────────────

    def test_plain_relative_path_resolves_with_config_dir(self, tmp_path):
        """A bare relative path in the files list resolves to an absolute path
        anchored at config_dir, not CWD."""
        from modules.util import load_files

        yml = tmp_path / "my_collections.yml"
        yml.write_text("# placeholder\n")

        files, had_scheduled = load_files("my_collections.yml", "collection_files", config_dir=str(tmp_path))

        assert not had_scheduled
        assert len(files) == 1
        file_type, file_path, _, _ = files[0]
        assert file_type == "File"
        assert os.path.isabs(file_path), "stored path must be absolute"
        assert os.path.normpath(file_path) == os.path.normpath(str(yml))

    def test_plain_absolute_path_unchanged(self, tmp_path):
        """An already-absolute path is not modified when config_dir is provided."""
        from modules.util import load_files

        yml = tmp_path / "abs.yml"
        yml.write_text("# placeholder\n")

        files, _ = load_files(str(yml), "collection_files", config_dir="/some/other/dir")

        assert len(files) == 1
        assert os.path.normpath(files[0][1]) == os.path.normpath(str(yml))

    def test_plain_missing_file_returns_empty(self, tmp_path):
        """A relative path that does not exist returns an empty list (no exception)."""
        from modules.util import load_files

        files, _ = load_files("nonexistent.yml", "collection_files", config_dir=str(tmp_path))

        assert files == []

    def test_no_config_dir_falls_back_to_cwd(self, tmp_path, monkeypatch):
        """When config_dir is omitted, behaviour is unchanged: relative paths resolve to CWD."""
        from modules.util import load_files

        yml = tmp_path / "cwd_file.yml"
        yml.write_text("# placeholder\n")
        monkeypatch.chdir(tmp_path)

        files, _ = load_files("cwd_file.yml", "collection_files")

        assert len(files) == 1

    # ── dict form: file: key ───────────────────────────────────────────

    def test_dict_file_relative_resolves_with_config_dir(self, tmp_path):
        """The dict form ``- file: relative.yml`` is stored as an absolute path."""
        from modules.util import load_files

        yml = tmp_path / "relative.yml"
        yml.write_text("# placeholder\n")

        files, _ = load_files([{"file": "relative.yml"}], "collection_files", config_dir=str(tmp_path))

        assert len(files) == 1
        file_type, file_path, _, _ = files[0]
        assert file_type == "File"
        assert os.path.isabs(file_path)
        assert os.path.normpath(file_path) == os.path.normpath(str(yml))

    # ── dict form: folder: key ─────────────────────────────────────────

    def test_dict_folder_relative_resolves_with_config_dir(self, tmp_path):
        """The ``folder:`` key resolves relative to config_dir and discovers YAML files."""
        from modules.util import load_files

        sub = tmp_path / "myfolder"
        sub.mkdir()
        (sub / "a.yml").write_text("# a\n")
        (sub / "b.yml").write_text("# b\n")

        files, _ = load_files([{"folder": "myfolder"}], "collection_files", config_dir=str(tmp_path))

        assert len(files) == 2
        for _, fp, _, _ in files:
            assert os.path.isabs(fp)

    def test_dict_folder_missing_returns_empty(self, tmp_path):
        """A relative folder that doesn't exist returns no files (no exception)."""
        from modules.util import load_files

        files, _ = load_files([{"folder": "no_such_folder"}], "collection_files", config_dir=str(tmp_path))

        assert files == []

    # ── dict form: asset_directory: key ───────────────────────────────

    def test_dict_asset_directory_relative_resolves_with_config_dir(self, tmp_path):
        """Relative ``asset_directory`` paths resolve to absolute paths under config_dir."""
        from modules.util import load_files

        assets = tmp_path / "assets"
        assets.mkdir()
        yml = tmp_path / "col.yml"
        yml.write_text("# placeholder\n")

        files, _ = load_files(
            [{"file": "col.yml", "asset_directory": "assets"}],
            "collection_files",
            config_dir=str(tmp_path),
        )

        assert len(files) == 1
        _, _, _, asset_dirs = files[0]
        assert len(asset_dirs) == 1
        assert os.path.isabs(asset_dirs[0])
        assert os.path.normpath(asset_dirs[0]) == os.path.normpath(str(assets))
