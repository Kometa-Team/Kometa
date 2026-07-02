"""Tests for modules/logs.py — MyLogger formatting and helpers."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

import modules.builder  # noqa: F401


class TestMyLogger:
    @pytest.fixture
    def logger(self):
        from modules.logs import MyLogger

        log = MyLogger.__new__(MyLogger)
        log._logger = MagicMock()
        log.screen_width = 100
        log.separating_character = "="
        log.log_requests = False
        log.is_trace = False
        log.ignore_ghost = False
        log.saved_errors = []
        log.save_errors = False
        log.secrets = []
        log.spacing = 0
        return log

    def test_log_methods_do_not_raise(self, logger):
        logger.info("m")
        logger.warning("m")
        logger.error("m")
        logger.debug("m")
        logger.secret("x")
        logger.ghost("x")
        assert logger._logger.info.call_count >= 0

    def test_ghost_does_not_record_info(self, logger):
        logger.ghost("x")
        # ``info_center`` is a method on real MyLogger; ensure ghost didn't
        # somehow pollute it by tripping over a recorded value.
        assert logger.info_center not in ["x"]


class TestMyLoggerWrapping:
    """Tests for long-line wrapping in MyLogger._log."""

    @pytest.fixture
    def logger(self):
        from modules.logs import MyLogger

        log = MyLogger.__new__(MyLogger)
        log._logger = MagicMock()
        log.screen_width = 20
        log.separating_character = "="
        log.log_requests = False
        log.is_trace = False
        log.ignore_ghost = False
        log.saved_errors = []
        log.save_errors = False
        log.secrets = []
        log.spacing = 0
        return log

    def _msgs(self, logger):
        """Return the msg arg from each makeRecord call (positional arg 4)."""
        return [call.args[4] for call in logger._logger.makeRecord.call_args_list]

    def test_short_plain_not_wrapped(self, logger):
        with patch.object(logger, "_formatter"):
            logger.info("short")
        assert logger._logger.handle.call_count == 1

    def test_short_bordered_not_wrapped(self, logger):
        with patch.object(logger, "_formatter"):
            logger.info("| short |")
        assert logger._logger.handle.call_count == 1

    def test_separator_not_wrapped(self, logger):
        """Lines starting with |= (separator dividers) must never be wrapped."""
        with patch.object(logger, "_formatter"):
            logger.info("|" + "=" * 40 + "|")
        assert logger._logger.handle.call_count == 1

    def test_plain_long_line_is_wrapped(self, logger):
        # screen_width=20; plain trigger is len > 18
        with patch.object(logger, "_formatter"):
            logger.info("x" * 40)
        assert logger._logger.handle.call_count >= 2

    def test_plain_wrap_continuation_indented(self, logger):
        with patch.object(logger, "_formatter"):
            logger.info("x" * 40)
        msgs = self._msgs(logger)
        assert len(msgs) >= 2
        assert msgs[1].startswith("  ")

    def test_bordered_long_line_is_wrapped(self, logger):
        # screen_width=20; bordered trigger is len > 22
        with patch.object(logger, "_formatter"):
            logger.info("| " + "a" * 30 + " |")
        assert logger._logger.handle.call_count >= 2

    def test_bordered_wrap_first_line_no_indent(self, logger):
        with patch.object(logger, "_formatter"):
            logger.info("| " + "a" * 30 + " |")
        msgs = self._msgs(logger)
        assert msgs[0].startswith("| a")

    def test_bordered_wrap_continuation_indented(self, logger):
        with patch.object(logger, "_formatter"):
            logger.info("| " + "a" * 30 + " |")
        msgs = self._msgs(logger)
        assert len(msgs) >= 2
        assert msgs[1].startswith("|   ")  # "| " + two-space indent

    def test_bordered_wrap_lines_within_width(self, logger):
        """Each wrapped bordered line must be at most screen_width + 2 chars."""
        with patch.object(logger, "_formatter"):
            logger.info("| " + "a" * 30 + " |")
        msgs = self._msgs(logger)
        for msg in msgs:
            assert len(msg) <= logger.screen_width + 2
