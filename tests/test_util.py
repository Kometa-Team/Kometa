"""Tests for util.py — exception hierarchy and helpers."""

from __future__ import annotations

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
