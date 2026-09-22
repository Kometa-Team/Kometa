"""Stub for tmdbapis.objs.base.

The critical fix: _parse() is declared as returning Any.  Without this stub,
pyright reads the actual source and infers a ~49-member union from all the
elif branches, which then explodes across every attribute assignment in every
TMDb object class (resulting in 670 errors in modules/tmdb.py alone).

The __getattr__ fallback ensures that any attribute not explicitly typed in a
subclass stub returns Any rather than causing an AttributeError at type-check time.
"""

from abc import ABC
from typing import Any, Optional, Union

class TMDbObj(ABC):
    id: Any
    def __init__(self, tmdb: Any, data: Any) -> None: ...
    def _parse(
        self,
        data: Any = ...,
        attrs: Optional[Union[str, list[Any]]] = ...,
        value_type: str = ...,
        default_is_none: bool = ...,
        is_list: bool = ...,
        is_dict: bool = ...,
        extend: bool = ...,
        key: Any = ...,
    ) -> Any: ...
    def _image_url(self, image_path: Any) -> str | None: ...
    def _finish(self, name: Any) -> None: ...
    def __getattr__(self, name: str) -> Any: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
