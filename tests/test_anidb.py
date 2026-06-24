"""Tests for modules/anidb.py — AniDB anime database client."""

from __future__ import annotations

import pytest

import modules.builder  # noqa: F401


class TestAniDB:
    @pytest.fixture
    def adapter(self):
        from modules.anidb import AniDB

        a = AniDB.__new__(AniDB)
        a._is_authorized = False
        return a

    def test_is_authorized_false_initially(self, adapter):
        assert adapter.is_authorized is False
