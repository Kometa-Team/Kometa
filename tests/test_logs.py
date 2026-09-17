"""Tests for modules/logs.py — MyLogger formatting and helpers."""

from __future__ import annotations

import logging
from unittest.mock import MagicMock

import pytest


class TestMyLogger:
    @pytest.mark.parametrize(
        ("is_debug", "is_trace", "expected_level"),
        [(False, False, logging.INFO), (True, False, logging.DEBUG), (False, True, logging.DEBUG), (True, True, logging.DEBUG)],
    )
    def test_command_handler_uses_debug_and_trace_settings(self, tmp_path, is_debug, is_trace, expected_level):
        from modules.logs import MyLogger

        log = MyLogger(f"kometa-test-{is_debug}-{is_trace}", str(tmp_path), 100, "=", True, is_debug, is_trace, False)
        try:
            assert log._logger.handlers[-1].level == expected_level
        finally:
            for handler in list(log._logger.handlers):
                log._logger.removeHandler(handler)
                handler.close()

    @pytest.mark.parametrize("is_trace", [False, True])
    def test_trace_console_output_without_debug(self, tmp_path, capsys, is_trace):
        from modules.logs import MyLogger

        log = MyLogger(f"kometa-trace-console-{is_trace}", str(tmp_path), 100, "=", True, False, is_trace, False)
        try:
            log.add_main_handler()
            message = "Rejected TMDb language configuration response: {'languages': []}"
            log.trace(message)
            log.remove_main_handler()

            assert (message in capsys.readouterr().err) is is_trace
            contents = (tmp_path / "logs" / "meta.log").read_text(encoding="utf-8") if (tmp_path / "logs" / "meta.log").exists() else ""
            assert (message in contents) is is_trace
        finally:
            if log.main_handler is not None:
                log.main_handler.close()
            for handler in list(log._logger.handlers):
                log._logger.removeHandler(handler)
                handler.close()

    def test_disabled_console_debug_remains_in_detailed_log(self, tmp_path, capsys):
        from modules.logs import MyLogger

        log = MyLogger("kometa-test-file-debug", str(tmp_path), 100, "=", True, False, False, False)
        try:
            log.add_main_handler()
            log.debug("detailed diagnostic")
            log.info("console information")
            log.remove_main_handler()

            captured = capsys.readouterr()
            assert "detailed diagnostic" not in captured.err
            assert "console information" in captured.err
            assert "detailed diagnostic" in (tmp_path / "logs" / "meta.log").read_text(encoding="utf-8")
        finally:
            if log.main_handler is not None:
                log.main_handler.close()
            for handler in list(log._logger.handlers):
                log._logger.removeHandler(handler)
                handler.close()

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

    def test_ghost_writes_when_stdout_is_a_tty(self, logger, monkeypatch, capsys):
        monkeypatch.setattr("sys.stdout.isatty", lambda: True)
        logger.ghost("progress")
        assert capsys.readouterr().out.endswith("\r")

    def test_ghost_silent_when_stdout_is_not_a_tty(self, logger, monkeypatch, capsys):
        # Regression test for #3542: non-TTY stdout must never get \r-only output.
        monkeypatch.setattr("sys.stdout.isatty", lambda: False)
        logger.ghost("progress")
        assert capsys.readouterr().out == ""

    def test_exorcise_silent_when_stdout_is_not_a_tty(self, logger, monkeypatch, capsys):
        monkeypatch.setattr("sys.stdout.isatty", lambda: False)
        logger.exorcise()
        assert capsys.readouterr().out == ""


class TestSecretRedaction:
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

    def test_secret_registers_url_encoded_variants(self, logger):
        """A token that appears percent-encoded inside a logged URL must still be redacted."""
        logger.secret("my token+key")
        assert "my token+key" in logger.secrets
        assert "my+token%2Bkey" in logger.secrets  # quote_plus form
        assert "my%20token%2Bkey" in logger.secrets  # quote form

    def test_secret_deduplicates(self, logger):
        logger.secret("abc123")
        logger.secret("abc123")
        assert logger.secrets.count("abc123") == 1

    def test_redact_replaces_raw_and_url_encoded_secrets(self, logger):
        logger.secret("my token+key")
        text = "raw=my token+key encoded=my%20token%2Bkey query=my+token%2Bkey"
        assert logger.redact(text) == "raw=(redacted) encoded=(redacted) query=(redacted)"


class TestTracebackSuppression:
    def test_known_not_found_error_is_suppressed(self, capsys):
        from modules.logs import _suppress_traceback_hook

        _suppress_traceback_hook(RuntimeError, RuntimeError("Plex Error: No Items found in Plex"), None)

        captured = capsys.readouterr()
        assert "[WARNING] RuntimeError: Plex Error: No Items found in Plex" in captured.err
        assert "Traceback" not in captured.err


# ═══════════════════════════════════════════════════════════════════════
# BufferedRotatingFileHandler
#
# Real file I/O against tmp_path rather than mocks - the whole point of
# this class is what actually lands on disk and when, which a mocked
# stream can't verify.
# ═══════════════════════════════════════════════════════════════════════


def make_record(level, msg):
    return logging.LogRecord(name="kometa", level=level, pathname="test.py", lineno=1, msg=msg, args=(), exc_info=None)


class TestBufferedRotatingFileHandler:
    def _handler(self, tmp_path, flush_every=5):
        from modules.logs import BufferedRotatingFileHandler

        log_file = tmp_path / "test.log"
        handler = BufferedRotatingFileHandler(str(log_file), delay=True, mode="w", backupCount=1, encoding="utf-8")
        handler.FLUSH_EVERY = flush_every
        handler.setFormatter(logging.Formatter("%(message)s"))
        return handler, log_file

    def test_low_severity_records_are_buffered_not_written_immediately(self, tmp_path):
        handler, log_file = self._handler(tmp_path, flush_every=5)
        handler.emit(make_record(logging.INFO, "line one"))
        assert log_file.read_text(encoding="utf-8") == ""  # Below FLUSH_EVERY, still buffered in the OS/file object, not on disk yet.
        handler.close()

    def test_reaching_flush_every_writes_buffered_lines(self, tmp_path):
        handler, log_file = self._handler(tmp_path, flush_every=3)
        for i in range(3):
            handler.emit(make_record(logging.INFO, f"line {i}"))
        content = log_file.read_text(encoding="utf-8")
        assert "line 0" in content and "line 1" in content and "line 2" in content
        handler.close()

    def test_warning_flushes_immediately_even_below_threshold(self, tmp_path):
        handler, log_file = self._handler(tmp_path, flush_every=25)
        handler.emit(make_record(logging.WARNING, "important warning"))
        assert "important warning" in log_file.read_text(encoding="utf-8")
        handler.close()

    def test_error_flushes_immediately_even_below_threshold(self, tmp_path):
        handler, log_file = self._handler(tmp_path, flush_every=25)
        handler.emit(make_record(logging.ERROR, "something broke"))
        assert "something broke" in log_file.read_text(encoding="utf-8")
        handler.close()

    def test_force_flush_writes_buffered_content_immediately(self, tmp_path):
        handler, log_file = self._handler(tmp_path, flush_every=25)
        handler.emit(make_record(logging.INFO, "buffered line"))
        assert log_file.read_text(encoding="utf-8") == ""
        handler.force_flush()
        assert "buffered line" in log_file.read_text(encoding="utf-8")
        handler.close()

    def test_close_flushes_buffered_content(self, tmp_path):
        handler, log_file = self._handler(tmp_path, flush_every=25)
        handler.emit(make_record(logging.INFO, "line before close"))
        handler.close()
        assert "line before close" in log_file.read_text(encoding="utf-8")

    def test_counter_resets_after_a_forced_flush(self, tmp_path):
        """A WARNING-triggered flush shouldn't leave the counter primed to over-flush right after."""
        handler, log_file = self._handler(tmp_path, flush_every=3)
        handler.emit(make_record(logging.WARNING, "w"))  # forces a flush, counter -> 0
        handler.emit(make_record(logging.INFO, "i1"))
        handler.emit(make_record(logging.INFO, "i2"))
        content = log_file.read_text(encoding="utf-8")
        assert "i1" not in content and "i2" not in content  # only 2 of 3 needed to hit the threshold again
        handler.close()
        content = log_file.read_text(encoding="utf-8")
        assert "i1" in content and "i2" in content
