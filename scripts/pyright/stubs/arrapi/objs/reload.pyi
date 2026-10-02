"""Stubs for arrapi reload objects.

Key typed attributes match what modules/radarr.py and modules/sonarr.py
access.  Everything else falls through __getattr__ -> Any.
"""

from __future__ import annotations

from typing import Any

from arrapi.objs.base import BaseObj

class ReloadObj(BaseObj):
    def __getattr__(self, name: str) -> Any: ...

class QualityProfile(ReloadObj):
    id: int
    name: Any
    def __getattr__(self, name: str) -> Any: ...

class LanguageProfile(ReloadObj):
    id: int
    name: Any
    def __getattr__(self, name: str) -> Any: ...

class SystemStatus(ReloadObj):
    def __getattr__(self, name: str) -> Any: ...

# Tag is declared before Movie/Series because they reference it in the
# tags: list[Tag] attribute.
class Tag(ReloadObj):
    id: int
    label: str
    def __getattr__(self, name: str) -> Any: ...

class Command(ReloadObj):
    def __getattr__(self, name: str) -> Any: ...

class Movie(ReloadObj):
    id: int
    tmdbId: int
    imdbId: Any
    title: Any
    path: Any
    monitored: Any
    qualityProfileId: Any
    tags: list[Tag]
    def __getattr__(self, name: str) -> Any: ...

class Series(ReloadObj):
    id: int
    tvdbId: int
    title: Any
    path: Any
    monitored: Any
    qualityProfileId: Any
    languageProfileId: Any
    seriesType: Any
    tags: list[Tag]
    def __getattr__(self, name: str) -> Any: ...
