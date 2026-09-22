from typing import Any

from arrapi.objs.base import BaseObj

class SimpleObj(BaseObj):
    def __getattr__(self, name: str) -> Any: ...

class Collection(SimpleObj):
    id: int
    name: Any
    def __getattr__(self, name: str) -> Any: ...

class Image(SimpleObj):
    def __getattr__(self, name: str) -> Any: ...

class MetadataProfile(SimpleObj):
    id: int
    name: Any
    def __getattr__(self, name: str) -> Any: ...

class RemotePathMapping(SimpleObj):
    def __getattr__(self, name: str) -> Any: ...

class RootFolder(SimpleObj):
    id: int
    path: Any
    def __getattr__(self, name: str) -> Any: ...

class Season(SimpleObj):
    seasonNumber: int
    monitored: Any
    def __getattr__(self, name: str) -> Any: ...

class UnmappedFolder(SimpleObj):
    def __getattr__(self, name: str) -> Any: ...

class RadarrExclusion(SimpleObj):
    def __getattr__(self, name: str) -> Any: ...

class SonarrExclusion(SimpleObj):
    def __getattr__(self, name: str) -> Any: ...
