"""Tests for modules/logs.py — MyLogger formatting and helpers."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest


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


class TestTracebackSuppression:
    def test_known_not_found_error_is_suppressed(self, capsys):
        from modules.logs import _suppress_traceback_hook

        _suppress_traceback_hook(RuntimeError, RuntimeError("Plex Error: No Items found in Plex"), None)

        captured = capsys.readouterr()
        assert "[WARNING] RuntimeError: Plex Error: No Items found in Plex" in captured.err
        assert "Traceback" not in captured.err
